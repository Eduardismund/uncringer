from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.config import Config
from src.api.handlers import AudioAnalysisHandler
from src.models.requests import PredictionRequest
from src.models.responses import PredictionResponse, HealthResponse

# Initialize FastAPI app
app = FastAPI(
    title="Uncringer API",
    description="AI-powered audio cringe detection using BigQuery ML",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
audio_handler = AudioAnalysisHandler()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(status="ok", message="Uncringer API is running!")

@app.post("/api/analyze", response_model=PredictionResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """Analyze uploaded audio file for cringe detection"""
    return await audio_handler.analyze_audio(file)

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_audio(request: PredictionRequest):
    """Predict cringe level from audio URL"""
    return await audio_handler.predict_from_url(request)

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy")