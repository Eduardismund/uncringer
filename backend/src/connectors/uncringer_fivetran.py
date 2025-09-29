from fivetran_connector_sdk import Operations as op
from fivetran_connector_sdk import Logging as log
from datetime import datetime, timezone
import json
import asyncio
import requests
from google.cloud import bigquery
from discord_connector import DiscordConnector
from gemini_classifier import GeminiClassifier
from config import ConnectorConfig


class UncringerFivetranConnector:
    
    def __init__(self):
        self.feature_extraction_url = ConnectorConfig.FEATURE_EXTRACTION_URL
    
    def configure(self, configuration: dict) -> dict:
        self.discord_token = configuration["discord_token"]
        self.server_id = configuration["discord_server_id"]
        self.min_reactions = int(configuration.get("min_reactions", ConnectorConfig.MIN_REACTIONS))
        self.lookback_hours = int(configuration.get("lookback_hours", ConnectorConfig.LOOKBACK_HOURS))
        
        self.discord = DiscordConnector(self.discord_token, self.server_id)
        
        service_account_key = configuration.get("google_service_account_key")
        self.service_account_key = service_account_key
        self.classifier = GeminiClassifier(credentials_json=service_account_key)
        
        return {"status": "SUCCESS"}
    
    def schema(self, configuration: dict) -> list:
        return [
            {
                "table": "discord_audios",
                "primary_key": ["message_id"],
                "columns": {
                    "message_id": "STRING",
                    "author": "STRING",
                    "channel_id": "STRING",
                    "channel_name": "STRING",
                    "filename": "STRING",
                    "audio_url": "STRING",
                    "reactions": "JSON",
                    "total_reactions": "INT",
                    "is_cringe": "BOOLEAN",
                    "ai_confidence": "FLOAT",
                    "ai_reasoning": "STRING",
                    "posted_at": "UTC_DATETIME",
                    "processed_at": "UTC_DATETIME"
                }
            },
            {
                "table": "audio_features",
                "primary_key": ["message_id"],
                "columns": {
                    "message_id": "STRING",
                    "duration": "FLOAT",
                    "pause_count": "INT",
                    "longest_pause": "FLOAT",
                    "pitch_mean": "FLOAT",
                    "pitch_variance": "FLOAT",
                    "voice_cracks": "INT",
                    "energy_mean": "FLOAT",
                    "energy_drops": "INT",
                    "speaking_rate": "INT",
                    "is_cringe": "BOOLEAN",
                    "feature_extracted_at": "UTC_DATETIME"
                }
            }
        ]
    
    def update(self, configuration: dict, state: dict) -> None:
        if not hasattr(self, 'discord'):
            self.configure(configuration)
        
        cursor = state.get("cursor", {})
        last_message_id = cursor.get("last_message_id", "0")
        
        log.info(f"Starting sync - looking for messages after ID: {last_message_id}")
        audio_messages = asyncio.run(
            self.discord.fetch_audio_messages(last_message_id, self.lookback_hours)
        )
        
        log.info(f"Found {len(audio_messages)} audio messages to process")
        processed_count = 0
        latest_message_id = last_message_id
        
        for audio in audio_messages:
            try:
                if audio["total_reactions"] < self.min_reactions:
                    log.info(f"Skipping message {audio['message_id']} - insufficient reactions ({audio['total_reactions']} < {self.min_reactions})")
                    continue
                
                log.info(f"Processing message {audio['message_id']} by {audio['author']} with {audio['total_reactions']} reactions")
                
                log.info(f"Classifying reactions for message {audio['message_id']}: {audio['reactions']}")
                classification = self.classifier.classify_reactions(audio["reactions"])
                log.info(f"Classification result: is_cringe={classification['is_cringe']}, confidence={classification['confidence']}")
                
                discord_record = {
                    "message_id": audio["message_id"],
                    "author": audio["author"],
                    "channel_id": audio["channel_id"],
                    "channel_name": audio["channel_name"],
                    "filename": audio["filename"],
                    "audio_url": audio["audio_url"],
                    "reactions": json.dumps(audio["reactions"]),
                    "total_reactions": audio["total_reactions"],
                    "is_cringe": classification["is_cringe"],
                    "ai_confidence": classification["confidence"],
                    "ai_reasoning": classification["reason"],
                    "posted_at": audio["posted_at"].isoformat(),
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
                
                log.info(f"Saving discord audio record for message {audio['message_id']}")
                op.upsert(table="discord_audios", data=discord_record)
                
                log.info(f"Starting feature extraction for message {audio['message_id']} from URL: {audio['audio_url']}")
                try:
                    features = self._extract_audio_features(audio["audio_url"])
                    if features:
                        log.info(f"Feature extraction successful for message {audio['message_id']}")
                        feature_record = {
                            "message_id": audio["message_id"],
                            **features,
                            "is_cringe": classification["is_cringe"],
                            "feature_extracted_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        log.info(f"Saving feature record for message {audio['message_id']}")
                        op.upsert(table="audio_features", data=feature_record)
                        log.info(f"Feature record saved successfully for message {audio['message_id']}")
                    else:
                        log.warning(f"Feature extraction returned empty result for message {audio['message_id']}")
                        
                except Exception as e:
                    log.severe(f"Audio feature extraction failed for message {audio['message_id']}: {str(e)}")
                
                processed_count += 1
                latest_message_id = audio["message_id"]
                log.info(f"Successfully processed message {audio['message_id']} ({processed_count} total)")
                
            except Exception as e:
                log.severe(f"Error processing audio {audio.get('message_id', 'unknown')}: {str(e)}")
                continue
        
        previous_count = state.get("cursor", {}).get("total_processed_count", 0)
        new_total_count = previous_count + processed_count
        
        new_state = {
            "cursor": {
                "last_message_id": latest_message_id,
                "last_sync_time": datetime.now(timezone.utc).isoformat(),
                "processed_count": processed_count,
                "total_processed_count": new_total_count
            }
        }
        
        op.checkpoint(state=new_state)
        
        self._train_model_if_ready(new_total_count)
    
    def _extract_audio_features(self, audio_url: str) -> dict:
        log.info(f"Calling Cloud Run feature extraction service: {self.feature_extraction_url}")
        log.info(f"Audio URL for feature extraction: {audio_url}")
        
        try:
            response = requests.post(
                self.feature_extraction_url,
                json={"audio_url": audio_url},
                timeout=600
            )
            
            log.info(f"Cloud Run response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                log.info(f"Cloud Run response: {result}")
                
                if result.get("success"):
                    log.info("Feature extraction successful - returning features")
                    return result["features"]
                else:
                    log.warning(f"Cloud Run returned success=false: {result.get('error', 'Unknown error')}")
            else:
                log.warning(f"Cloud Run returned non-200 status: {response.status_code}, Response: {response.text}")
        
        except requests.exceptions.Timeout:
            log.severe("Cloud Run request timed out after 300 seconds")
        except requests.exceptions.RequestException as e:
            log.severe(f"Cloud Run request failed: {str(e)}")
        except Exception as e:
            log.severe(f"Unexpected error during feature extraction: {str(e)}")
        
        return None
    
    def _train_model_if_ready(self, total_count: int) -> None:
        if total_count % ConnectorConfig.TRAINING_INTERVAL == 0 and total_count >= 2:
            try:
                from google.oauth2 import service_account
                
                if self.service_account_key:
                    key_info = json.loads(self.service_account_key)
                    credentials = service_account.Credentials.from_service_account_info(key_info)
                    client = bigquery.Client(project=ConnectorConfig.PROJECT_ID, credentials=credentials)
                else:
                    client = bigquery.Client(project=ConnectorConfig.PROJECT_ID)
                
                query = f"""
                CREATE OR REPLACE MODEL `{ConnectorConfig.PROJECT_ID}.{ConnectorConfig.DATASET_ID}.{ConnectorConfig.MODEL_ID}`
                OPTIONS(
                    model_type='LOGISTIC_REG',
                    input_label_cols=['is_cringe'],
                    auto_class_weights=TRUE
                ) AS
                SELECT 
                    duration, pause_count, longest_pause, pitch_mean,
                    pitch_variance, voice_cracks, energy_mean, 
                    energy_drops, speaking_rate, is_cringe
                FROM `{ConnectorConfig.PROJECT_ID}.{ConnectorConfig.DATASET_ID}.audio_features`
                WHERE duration > 0
                """
                
                client.query(query).result()
                log.info(f"Model retrained with {total_count} total samples")
                
            except Exception as e:
                log.severe(f"Model training failed: {str(e)}")


connector = UncringerFivetranConnector()