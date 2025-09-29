FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
COPY main.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD exec functions-framework --target=extract_audio_features --port=${PORT:-8080}