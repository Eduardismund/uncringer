from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Uncringer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Uncringer API is running!"}

@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "size": file.size,
        "status": "received"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}