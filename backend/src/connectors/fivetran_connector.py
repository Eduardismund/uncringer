from fivetran_connector_sdk import Operations as op
from datetime import datetime, timezone
import json
import asyncio
from discord_client import DiscordClient
from ai_classifier import AwkwardnessClassifier


class UncringerConnector:
    
    def __init__(self):
        pass
    
    def configure(self, configuration: dict):
        self.discord_token = configuration["discord_token"]
        self.server_id = configuration["discord_server_id"]
        self.min_reactions = int(configuration.get("min_reactions", "1"))
        self.lookback_hours = int(configuration.get("lookback_hours", "24"))
        
        self.discord = DiscordClient(self.discord_token, self.server_id)
        
        service_account_key = configuration.get("google_service_account_key")
        self.classifier = AwkwardnessClassifier(service_account_key=service_account_key)
        
        return {"status": "SUCCESS"}
    
    def schema(self, configuration: dict):
        return [
            {
                "table": "discord_audios",
                "primary_key": ["message_id"],
                "columns": {
                    "message_id": "STRING",
                    "author": "STRING",
                    "channel_id": "STRING",
                    "filename": "STRING",
                    "audio_url": "STRING",
                    "reactions": "JSON",
                    "total_reactions": "INT",
                    "awkwardness_level": "INT",
                    "awkwardness_label": "STRING",
                    "ai_confidence": "FLOAT",
                    "ai_reasoning": "STRING",
                    "posted_at": "UTC_DATETIME",
                    "processed_at": "UTC_DATETIME"
                }
            }
        ]
    
    def update(self, configuration: dict, state: dict):
        if not hasattr(self, 'discord'):
            self.configure(configuration)
        
        cursor = state.get("cursor", {})
        last_message_id = cursor.get("last_message_id", "0")
        
        audio_messages = asyncio.run(
            self.discord.fetch_audio_messages(last_message_id, self.lookback_hours)
        )
        
        processed_count = 0
        latest_message_id = last_message_id
        
        for audio in audio_messages:
            try:
                if audio["total_reactions"] < self.min_reactions:
                    continue
                
                classification = self.classifier.classify(audio["reactions"])
                
                record = {
                    "message_id": audio["message_id"],
                    "author": audio["author"],
                    "channel_id": audio["channel_id"],
                    "filename": audio["filename"],
                    "audio_url": audio["audio_url"],
                    "reactions": json.dumps(audio["reactions"]),
                    "total_reactions": audio["total_reactions"],
                    "awkwardness_level": classification["level"],
                    "awkwardness_label": classification["label"],
                    "ai_confidence": classification["confidence"],
                    "ai_reasoning": classification["reason"],
                    "posted_at": audio["posted_at"].isoformat(),
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
                
                op.upsert(table="discord_audios", data=record)
                
                processed_count += 1
                latest_message_id = audio["message_id"]
                
            except Exception:
                continue
        
        new_state = {
            "cursor": {
                "last_message_id": latest_message_id,
                "last_sync_time": datetime.now(timezone.utc).isoformat(),
                "processed_count": processed_count
            }
        }
        
        op.checkpoint(state=new_state)


connector = UncringerConnector()