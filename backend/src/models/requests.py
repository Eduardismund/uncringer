from pydantic import BaseModel


class PredictionRequest(BaseModel):
    audio_url: str