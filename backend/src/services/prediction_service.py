import requests
from typing import Dict
from src.utils.auth import get_bigquery_client
from src.config import Config


class PredictionService:
    def __init__(self):
        self.client = get_bigquery_client()
        self.feature_extraction_url = Config.FEATURE_EXTRACTION_URL
    
    def extract_features(self, audio_url: str) -> Dict:
        """Extract audio features using Cloud Run service"""
        response = requests.post(
            self.feature_extraction_url,
            json={"audio_url": audio_url},
            timeout=Config.UPLOAD_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result["features"]
        
        raise Exception("Feature extraction failed")
    
    def predict_cringe(self, features: Dict) -> Dict:
        """Predict cringe level using BigQuery ML model"""
        query = f"""
        SELECT 
            predicted_is_cringe,
            predicted_is_cringe_probs
        FROM ML.PREDICT(
            MODEL `{Config.PROJECT_ID}.{Config.BIGQUERY_DATASET}.{Config.BIGQUERY_MODEL}`,
            (SELECT 
                {features['duration']} as duration,
                {features['pause_count']} as pause_count,
                {features['longest_pause']} as longest_pause,
                {features['pitch_mean']} as pitch_mean,
                {features['pitch_variance']} as pitch_variance,
                {features['voice_cracks']} as voice_cracks,
                {features['energy_mean']} as energy_mean,
                {features['energy_drops']} as energy_drops,
                {features['speaking_rate']} as speaking_rate
            )
        )
        """
        
        query_job = self.client.query(query)
        results = query_job.result()
        
        for row in results:
            is_cringe = bool(row.predicted_is_cringe)
            
            # Extract confidence from probability array
            probs = row.predicted_is_cringe_probs
            confidence = 0.5
            
            for prob_item in probs:
                if prob_item['label'] == is_cringe:
                    confidence = float(prob_item['prob'])
                    break
            
            return {
                'is_cringe': is_cringe,
                'confidence': confidence,
                'cringe_score': confidence if is_cringe else 1 - confidence,
                'features': features
            }
        
        raise Exception("No prediction results from BigQuery ML model")