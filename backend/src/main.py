from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import os
from src.services.ai_reaction_analyzer import AIReactionAnalyzer
from src.services.storage import StorageService

app = FastAPI(title="Uncringer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_analyzer = AIReactionAnalyzer()
storage_service = StorageService()

class ReactionAnalysisRequest(BaseModel):
    reactions: Dict[str, int]
    context: str = ""

@app.get("/")
async def root():
    return {"message": "Uncringer API is running!"}

@app.post("/api/analyze-reactions")
async def analyze_reactions(request: ReactionAnalysisRequest):
    """Test endpoint for AI reaction analysis"""
    analysis = await ai_analyzer.analyze_reactions(request.reactions, request.context)
    return analysis

@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    """Upload audio file to Cloud Storage"""
    
    file_data = await file.read()
    
    result = await storage_service.upload_audio(file_data, file.filename)
    
    return {
        "message": "Audio uploaded successfully",
        "file_id": result["file_id"],
        "gcs_url": result["gcs_url"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}