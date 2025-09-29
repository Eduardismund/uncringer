import uuid
from typing import Tuple
from src.utils.auth import get_storage_client
from src.config import Config


class StorageService:
    def __init__(self):
        self.client = get_storage_client()
        self.bucket_name = Config.STORAGE_BUCKET
    
    def upload_temp_audio(self, file_data: bytes) -> Tuple[str, str]:
        """Upload audio file temporarily and return blob name and public URL"""
        analysis_id = str(uuid.uuid4())
        blob_name = f"user_uploads/{analysis_id}.mp3"
        
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(file_data, content_type='audio/mpeg')
        blob.make_public()
        
        return blob_name, blob.public_url
    
    def delete_temp_audio(self, blob_name: str) -> None:
        """Delete temporary audio file"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()