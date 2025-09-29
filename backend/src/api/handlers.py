from fastapi import UploadFile, HTTPException
from src.services.storage_service import StorageService
from src.services.prediction_service import PredictionService
from src.models.responses import PredictionResponse, AudioFeatures
from src.models.requests import PredictionRequest
from src.utils.exceptions import UncringerException
import uuid


class AudioAnalysisHandler:
    def __init__(self):
        self.storage_service = StorageService()
        self.prediction_service = PredictionService()
    
    async def analyze_audio(self, file: UploadFile) -> PredictionResponse:
        """Handle complete audio analysis workflow"""
        blob_name = None
        
        try:
            # Read file data
            file_data = await file.read()
            
            # Upload to temporary storage
            blob_name, audio_url = self.storage_service.upload_temp_audio(file_data)
            
            # Extract features
            features = self.prediction_service.extract_features(audio_url)
            
            # Get prediction
            prediction = self.prediction_service.predict_cringe(features)
            
            # Create response
            analysis_id = blob_name.split('/')[-1].replace('.mp3', '')
            
            return PredictionResponse(
                is_cringe=prediction['is_cringe'],
                confidence=prediction['confidence'],
                cringe_score=prediction['cringe_score'],
                features=AudioFeatures(**prediction['features']),
                analysis_id=analysis_id
            )
            
        except UncringerException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        finally:
            # Cleanup temporary file
            if blob_name:
                try:
                    self.storage_service.delete_temp_audio(blob_name)
                except Exception:
                    pass  # Log this in production
    
    async def predict_from_url(self, request: PredictionRequest) -> PredictionResponse:
        """Handle prediction from existing audio URL"""
        try:
            # Extract features
            features = self.prediction_service.extract_features(request.audio_url)
            
            # Get prediction
            prediction = self.prediction_service.predict_cringe(features)
            
            # Create response
            analysis_id = str(uuid.uuid4())
            
            return PredictionResponse(
                is_cringe=prediction['is_cringe'],
                confidence=prediction['confidence'],
                cringe_score=prediction['cringe_score'],
                features=AudioFeatures(**prediction['features']),
                analysis_id=analysis_id
            )
            
        except UncringerException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")