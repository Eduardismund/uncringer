from pydantic import BaseModel
from typing import Dict, Optional


class AudioFeatures(BaseModel):
    duration: float
    pause_count: int
    longest_pause: float
    pitch_mean: float
    pitch_variance: float
    voice_cracks: int
    energy_mean: float
    energy_drops: int
    speaking_rate: int


class PredictionResponse(BaseModel):
    is_cringe: bool
    confidence: float
    cringe_score: float
    features: AudioFeatures
    analysis_id: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: Optional[str] = None