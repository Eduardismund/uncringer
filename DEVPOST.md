# Uncringer - AI-Powered Discord Audio Reaction Analyzer

## Submission for Google Chrome Built-in AI Challenge 2025

### Project Overview
**Uncringer** is an innovative web application that leverages Chrome's built-in AI APIs and Google Cloud's Vertex AI to analyze Discord audio messages and their emoji reactions, determining "cringe" levels and training custom models based on community feedback patterns.

### Problem Statement
Discord communities generate thousands of audio messages daily, with emoji reactions serving as implicit feedback. Currently, there's no automated way to:
- Analyze audio content sentiment at scale
- Correlate emoji reactions with audio content quality
- Train models based on community reaction patterns
- Filter or moderate audio content based on community standards

### Solution
Uncringer creates a comprehensive pipeline that:
1. **Extracts** audio files from Discord channels via custom data source integration
2. **Stores** audio content in Google Cloud Storage buckets
3. **Analyzes** audio using Gemini 2.0's multimodal capabilities
4. **Processes** emoji reactions as training labels
5. **Trains** custom classification models on Vertex AI
6. **Provides** real-time analysis through a React-based web interface

### Technical Architecture

#### Frontend (Web Application)
- **React UI** for audio upload testing and analysis visualization
- **Chrome Built-in AI APIs Integration**:
  - **Prompt API**: Generate dynamic analysis prompts for audio content
  - **Summarizer API**: Create concise summaries of audio transcriptions
  - **Translator API**: Support multilingual Discord communities
  - **Writer API**: Generate analysis reports and insights

#### Backend Infrastructure
- **FastAPI** server handling API requests
- **Google Cloud Platform**:
  - Cloud Storage for audio file persistence
  - Vertex AI for model training and inference
  - Gemini 2.0 for multimodal audio analysis
- **Elasticsearch** for indexing and searching analyzed content
- **Fivetran** for data pipeline orchestration

#### Custom Discord Data Source
- Webhook integration for real-time audio message capture
- Reaction tracking system mapping emojis to audio messages
- Batch processing for historical data extraction

### Key Features

#### 1. Multimodal Audio Analysis
- Leverages Gemini 2.0's audio understanding capabilities
- Analyzes tone, content, and context
- Provides cringe scoring (0-100 scale)

#### 2. Reaction-Based Learning
- Maps emoji reactions to audio quality metrics
- Builds training datasets from community feedback
- Continuously improves classification accuracy

#### 3. Privacy-First Design
- Client-side processing using Chrome's built-in AI
- Audio analysis without server uploads (for preview features)
- User consent management for data collection

#### 4. Real-Time Dashboard
- Live analysis of incoming audio messages
- Trend visualization for cringe patterns
- Community moderation tools

### APIs Used
- **Prompt API**: Dynamic prompt generation for audio analysis context
- **Summarizer API**: Audio transcription summarization
- **Translator API**: Multi-language support for global Discord communities
- **Writer API**: Automated report generation
- **Hybrid Strategy**: Firebase AI Logic for scalable backend processing

### Use Cases
1. **Community Moderation**: Automatically flag potentially problematic audio content
2. **Content Quality**: Help users understand reception before posting
3. **Trend Analysis**: Identify patterns in community reactions
4. **Training Data Generation**: Create labeled datasets for custom ML models

### Demo Video
[YouTube Link - Coming Soon]

### GitHub Repository
[GitHub Link - Coming Soon]

### Live Demo
[Demo URL - Coming Soon]

### Development Process

#### Phase 1: Infrastructure Setup ✅
- FastAPI backend configuration
- GCP integration (Storage, Vertex AI)
- Elasticsearch setup
- Basic React frontend

#### Phase 2: Discord Integration (Current)
- Custom data source development
- Audio extraction pipeline
- Reaction mapping system

#### Phase 3: AI Integration (Next)
- Chrome Built-in AI API implementation
- Gemini 2.0 audio analysis
- Model training pipeline on Vertex AI

#### Phase 4: Polish & Deploy
- UI/UX improvements
- Performance optimization
- Production deployment

### Technical Challenges & Solutions

**Challenge**: Real-time processing of audio streams
**Solution**: Implemented queue-based processing with GCS as intermediate storage

**Challenge**: Correlating reactions with specific audio segments
**Solution**: Timestamp-based mapping with Discord message IDs as keys

**Challenge**: Privacy concerns with audio content
**Solution**: Hybrid approach using client-side Chrome AI for preview, server-side for training

### Future Enhancements
- Support for video content analysis
- Integration with other communication platforms (Slack, Teams)
- Advanced sentiment analysis beyond "cringe" classification
- Community-specific model fine-tuning

### Team
- Solo Developer: [Your Name]

### Acknowledgments
- Google Chrome team for the Built-in AI APIs
- Discord developer community for API support
- Vertex AI team for ML infrastructure

---

*Built for the Google Chrome Built-in AI Challenge 2025*
*🤖 Powered by Gemini Nano and Chrome AI*