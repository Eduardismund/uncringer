"""
Simple Google Cloud Storage service for audio files
"""

from google.cloud import storage
import os
from datetime import datetime
import uuid

class StorageService:
    def __init__(self):
        creds_path = os.path.join(os.path.dirname(__file__), "../../../credentials.json")
        if os.path.exists(creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        
        self.client = storage.Client()
        self.bucket_name = "uncringer-audio-472412"
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            self.bucket = self.client.bucket(self.bucket_name)
            if self.bucket.exists():
                print(f"Using existing bucket {self.bucket_name}")
            else:
                self.bucket = self.client.create_bucket(
                    self.bucket_name,
                    location="europe-west1"
                )
                print(f"Created new bucket {self.bucket_name}")
        except Exception as e:
            print(f"Creating bucket: {e}")
            try:
                bucket = storage.Bucket(self.bucket_name)
                bucket.location = "europe-west1"
                self.bucket = self.client.create_bucket(bucket)
                print(f"Created bucket {self.bucket_name}")
            except Exception as e2:
                print(f"Failed to create bucket: {e2}")
                self.bucket = self.client.bucket(self.bucket_name)
    
    async def upload_audio(self, file_data: bytes, filename: str) -> dict:
        """Upload audio file to Cloud Storage"""
        
        file_id = str(uuid.uuid4())
        ext = filename.split('.')[-1]
        blob_name = f"audio/{file_id}.{ext}"
        
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(file_data)
        
        url = f"gs://{self.bucket_name}/{blob_name}"
        
        return {
            "file_id": file_id,
            "filename": filename,
            "gcs_url": url,
            "uploaded_at": datetime.utcnow().isoformat()
        }