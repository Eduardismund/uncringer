import os
from typing import Optional


class Config:
    PROJECT_ID = "uncringer-472412"
    BIGQUERY_DATASET = "uncringer_discord"
    BIGQUERY_MODEL = "cringe_model"
    STORAGE_BUCKET = "uncringer-app-audio"
    
    FEATURE_EXTRACTION_URL = "https://extract-audio-features-480404075714.us-central1.run.app"
    
    CREDENTIALS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'credentials.json'
    )
    
    CORS_ORIGINS = ["*"]
    UPLOAD_TIMEOUT = 30
    
    @classmethod
    def get_credentials_path(cls) -> Optional[str]:
        """Get the path to Google Cloud credentials"""
        env_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if env_path:
            return env_path
        
        if os.path.exists(cls.CREDENTIALS_PATH):
            return cls.CREDENTIALS_PATH
        
        return None