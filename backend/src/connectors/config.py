import os
from typing import Optional


class ConnectorConfig:
    
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_SERVER_ID = os.getenv('DISCORD_SERVER_ID')
    
    MIN_REACTIONS = int(os.getenv('MIN_REACTIONS', '1'))
    LOOKBACK_HOURS = int(os.getenv('LOOKBACK_HOURS', '24'))
    TRAINING_INTERVAL = int(os.getenv('TRAINING_INTERVAL', '2'))
    
    PROJECT_ID = "uncringer-472412"
    DATASET_ID = "uncringer_discord"
    MODEL_ID = "cringe_model"
    FEATURE_EXTRACTION_URL = os.getenv('FEATURE_EXTRACTION_URL')
    
    @classmethod
    def get_google_credentials(cls) -> Optional[str]:
        return os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')