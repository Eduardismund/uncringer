import json
from google.oauth2 import service_account
from google.cloud import storage, bigquery
from src.config import Config


def get_credentials():
    """Get Google Cloud credentials"""
    creds_path = Config.get_credentials_path()
    
    if not creds_path:
        return None
    
    with open(creds_path, 'r') as f:
        key_info = json.load(f)
        return service_account.Credentials.from_service_account_info(key_info)


def get_storage_client():
    """Get authenticated Google Cloud Storage client"""
    credentials = get_credentials()
    if credentials:
        return storage.Client(project=Config.PROJECT_ID, credentials=credentials)
    return storage.Client(project=Config.PROJECT_ID)


def get_bigquery_client():
    """Get authenticated BigQuery client"""
    credentials = get_credentials()
    if credentials:
        return bigquery.Client(project=Config.PROJECT_ID, credentials=credentials)
    return bigquery.Client(project=Config.PROJECT_ID)