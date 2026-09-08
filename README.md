# Agentic Viral Video Orchestrator (AVVO)

A Self-Optimizing, Multi-Agent System for AI Video Trend Discovery, Generation, and Publishing.

## Overview

AVVO is an autonomous, end-to-end AI video creation ecosystem designed to continuously discover trending topics, generate short-form videos using advanced AI tools, evaluate their performance, and optimize future generations based on real-time feedback.

## Architecture

The system comprises 7 AI agents working collaboratively in a sophisticated multi-agent orchestration framework:

### AI Agents

#### 1. Trend Discovery Agent
**Location**: `backend/agents/trend_discovery/trend_discovery_agent.py`

**Core Features**:
- **Social Platform Scanning**: Analyzes TikTok, YouTube, Instagram, and X (Twitter) for viral trends
- **Content Analysis**: Processes video URLs, voice inputs, and attached files
- **Gemini AI Integration**: Uses Google's Gemini 2.5-flash model for trend analysis
- **Multi-modal Input**: Supports YouTube Shorts, regular videos, and direct content analysis
- **Speech-to-Text**: Integrated Google Speech-to-Text for voice input processing
- **Trend Scoring**: Provides virality scores (1-100) and additional instructions for content creation

**Key Methods**:
- `discover_trends()`: Main orchestration method for trend discovery
- `analyze_links()`: Processes video URLs from different platforms
- `analyze_voice_input()`: Transcribes and analyzes voice inputs
- `analyze_files()`: Processes attached documents and files

#### 2. Story Ideation Agent
**Location**: `backend/agents/story_ideation/story_ideation_agent.py`

**Core Features**:
- **Script Generation**: Creates structured video scripts with hooks, scenes, and CTAs
- **Multi-modal Processing**: Handles topics, instructions, voice inputs, and files
- **Gemini AI Integration**: Uses advanced prompting for creative script writing
- **Structured Output**: Generates JSON-formatted scripts with scenes, voiceover, and timing
- **Voice Transcription**: Integrated speech-to-text for voice-based ideation

**Key Methods**:
- `generate_script()`: Creates complete video scripts from inputs
- `analyze_voice_input()`: Processes voice-based creative inputs
- `analyze_files()`: Incorporates file-based content into scripts

#### 3. Video Generation Agent
**Location**: `backend/agents/video_generation/dynamic_shot_orchestrator.py`

**Core Features**:
- **Dynamic Shot Orchestration**: Creates complex video sequences with multiple shots
- **Storyboard Generation**: Automated storyboard creation with shot composition
- **Style Consistency**: Maintains visual consistency across video sequences
- **Scene-by-Scene Generation**: Individual scene processing with FFmpeg stitching
- **Vertex AI Veo Integration**: Uses Google's Vertex AI for video generation
- **Multi-platform Optimization**: Adapts content for TikTok, YouTube Shorts, Instagram Reels
- **Voiceover Synthesis**: Google Text-to-Speech integration
- **Music Generation**: AI-powered background music creation

**Key Components**:
- `StoryboardGenerator`: Creates structured video plans
- `StyleConsistencyManager`: Ensures visual coherence
- `SceneBySceneGenerator`: Handles individual scene creation and stitching
- `DynamicShotOrchestrator`: Main orchestration engine

#### 4. Optimization & Feedback Agent
**Location**: `backend/agents/optimization_feedback/reinforcement_strategy_engine.py`

**Core Features**:
- **Contextual Bandit Learning**: Multi-armed bandit algorithm for strategy optimization
- **A/B Testing Framework**: Automated testing of creative variables
- **Reinforcement Learning**: Sophisticated reward modeling for content performance
- **Performance Analytics**: Tracks engagement, virality, and retention metrics
- **Strategy Adaptation**: Dynamic adjustment of content creation parameters

**Key Components**:
- `ContextualBandit`: Optimizes creative decisions
- `ABTestManager`: Manages automated experiments
- `RewardModel`: Calculates performance-based rewards
- `ReinforcementStrategyEngine`: Main optimization engine

**Creative Variables Optimized**:
- Voiceover style, music genre, video pacing
- Narrative structure, opening hooks, calls-to-action
- Visual style, content length

#### 5. Publisher Agent
**Location**: `backend/agents/publisher/index.js`

**Core Features**:
- **Multi-platform Publishing**: Automated posting to TikTok, YouTube, Instagram
- **API Integration**: Direct platform API connections
- **Scheduling**: Automated publishing at optimal times
- **Performance Tracking**: Post-publish analytics collection
- **Node.js Implementation**: JavaScript-based agent for web automation

**Supported Platforms**:
- TikTok (API integration)
- YouTube (API integration)
- Instagram (Selenium automation)

#### 6. Brand Safety Agent
**Location**: `backend/agents/brand_safety/ethical_guardian_agent.py`

**Core Features**:
- **Content Moderation**: Ensures brand-safe content generation
- **Ethical Guidelines**: Enforces content standards and policies
- **Risk Assessment**: Evaluates content for potential issues
- **Compliance Monitoring**: Maintains brand alignment

#### 7. Documentation & Versioning Agent
**Location**: `backend/agents/documentation/documentation_agent.py`

**Core Features**:
- **Automated Documentation**: Creates and maintains project documentation
- **Version Control**: Tracks changes and versions
- **Knowledge Base**: Maintains institutional knowledge
- **Process Logging**: Records agent activities and decisions

## Backend Services

### Main API Gateway (FastAPI)
**Location**: `backend/app/main.py`
**Port**: 8000

**Core Services**:
- **Authentication**: JWT-based user authentication
- **Agent Orchestration**: Routes requests to appropriate AI agents
- **WebSocket Support**: Real-time communication for chat and notifications
- **File Management**: Handles uploads and static file serving
- **CORS Configuration**: Frontend integration support

**Routers**:
- `/api/auth`: Authentication endpoints
- `/api/agents`: AI agent orchestration
- `/api/dashboard`: Analytics and monitoring
- `/api/optimization`: Performance optimization
- `/api/review`: Content review workflows
- `/api/simulation`: Content simulation
- `/api/knowledge`: Knowledge base access
- `/api/criticism`: Content criticism and feedback
- `/api/prompts`: Prompt management
- `/api/video`: Video processing and generation
- `/api/comments`: Comment management
- `/api/chat`: Real-time chat functionality
- `/api/publisher`: Content publishing
- `/api/collaboration`: Team collaboration features
- `/api/notifications`: Notification system

### Video Uploader Service
**Location**: `backend/video-uploader-service/`
**Port**: 8002

**Features**:
- **File Upload**: Handles video file uploads with validation
- **Cloud Storage**: Integrates with cloud storage providers
- **Analytics**: Upload performance tracking
- **Zapier Integration**: Workflow automation

### Asynchronous Worker Service (Celery)
**Location**: `backend/app/celery_app.py`

**Features**:
- **Task Queue**: Asynchronous processing of video generation
- **Background Jobs**: Long-running AI tasks
- **Redis Backend**: Task state management
- **Scalability**: Horizontal scaling support

## Frontend

### Tech Stack
- **Framework**: React 19.2.0 with TypeScript
- **Build Tool**: Vite 6.2.0
- **Routing**: React Router DOM 7.9.4
- **Styling**: Tailwind CSS 4.1.15 with PostCSS
- **AI Integration**: Google Generative AI SDK
- **State Management**: React Context API

### Components
- **BackButton**: Navigation component
- **Button**: Reusable button component
- **Card**: Content container component
- **Header**: Application header
- **NotificationCenter**: Notification management
- **Sidebar**: Navigation sidebar
- **TeamPresence**: Team collaboration indicator
- **VideoPlayer**: Video playback component
- **VoiceToText**: Speech-to-text interface

### Pages
- **Home**: Dashboard and overview
- **Login**: User authentication
- **TrendDiscovery**: Trend analysis interface
- **StoryIdeation**: Script creation tools
- **VideoGeneration**: Video creation workflow
- **Publisher**: Content publishing interface
- **OptimizationFeedback**: Performance analytics
- **Chat**: Real-time collaboration
- **Comments**: Comment management
- **Documentation**: System documentation

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL + FAISS Vector Database
- **Cache/Message Queue**: Redis
- **Document Database**: MongoDB
- **Task Queue**: Celery
- **AI/ML**: Google Gemini 2.5-flash, Vertex AI Veo
- **Speech Services**: Google Speech-to-Text, Text-to-Speech
- **Video Processing**: FFmpeg, OpenCV
- **Cloud Storage**: Google Cloud Storage, Cloudinary

### Frontend
- **Framework**: React 19.2.0 + TypeScript
- **Build System**: Vite 6.2.0
- **Styling**: Tailwind CSS 4.1.15
- **State Management**: React Context API
- **Routing**: React Router DOM 7.9.4

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (planned)
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana (planned)
- **Logging**: ELK Stack (planned)

### AI/ML Services
- **Language Models**: Google Gemini 2.5-flash
- **Video Generation**: Google Vertex AI Veo
- **Speech Processing**: Google Cloud Speech-to-Text/TTS
- **Computer Vision**: OpenCV, MediaPipe
- **Vector Search**: FAISS
- **Reinforcement Learning**: Custom contextual bandits

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - User logout

### Agents
- `POST /api/agents/trend-discovery` - Discover viral trends
- `GET /api/agents/trend-discovery/status/{job_id}` - Check trend discovery status
- `POST /api/agents/story-ideation` - Generate video scripts
- `GET /api/agents/story-ideation/status/{job_id}` - Check script generation status
- `POST /api/agents/optimization` - Optimize content strategy
- `GET /api/agents/optimization/status/{job_id}` - Check optimization status
- `POST /api/agents/video-generation` - Generate videos
- `GET /api/agents/video-generation/status/{job_id}` - Check video generation status
- `POST /api/agents/publisher` - Publish content
- `GET /api/agents/publisher/status/{job_id}` - Check publishing status

### Video Processing
- `POST /api/video/upload` - Upload video files
- `POST /api/video/analyze` - Analyze video for virality
- `POST /api/video/generate` - Generate AI videos
- `GET /api/video/generate/status/{job_id}` - Check generation status
- `POST /api/video/attach` - Attach files to videos
- `POST /api/video/upload-audio` - Upload audio files
- `POST /api/video/transcribe` - Transcribe audio to text
- `POST /api/video/upload-and-publish` - Upload and publish videos
- `GET /api/video/publish-status/{publish_id}` - Check publish status
- `POST /api/video/trim` - Trim video segments

### Real-time Features
- `WebSocket /api/chat/ws` - Real-time chat
- `GET /api/notifications/` - Get notifications
- `GET /api/notifications/online-users` - Get online users

## Deployment & Infrastructure

### Docker Services
- **api_gateway**: FastAPI application (Port 8000)
- **worker**: Celery worker for async tasks
- **chat_service**: WebSocket service (Port 8001)
- **video_uploader**: Video upload service (Port 8002)
- **frontend**: React application served by Nginx (Port 3001)
- **redis**: Redis cache/message queue (Port 6380)
- **mongo**: MongoDB document database (Port 27017)

### Environment Variables
```bash
# AI Services
GOOGLE_CLOUD_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_project_id

# Database
DATABASE_URL=postgresql://user:password@localhost/avvo
MONGO_URL=mongodb://admin:password@mongo:27017
REDIS_URL=redis://redis:6379/0

# External APIs
YOUTUBE_API_KEY=your_youtube_api_key
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
TIKTOK_CLIENT_KEY=your_tiktok_key
ZAPIER_WEBHOOK_URL=your_zapier_webhook

# Platform Credentials
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

### Scaling Strategy
- **Horizontal Scaling**: Multiple worker instances for video generation
- **Load Balancing**: Nginx for API gateway distribution
- **Database Sharding**: MongoDB sharding for large-scale deployments
- **CDN Integration**: CloudFront/Cloudflare for global content delivery

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Google Cloud Platform account with APIs enabled

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd VIRALISH
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd ../viralish_fronted
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

5. **Database Setup**
   ```bash
   # Start infrastructure services
   docker-compose -f deployment/docker/docker-compose.yml up -d redis mongo
   ```

6. **Run Services**
   ```bash
   # Terminal 1: Backend API
   cd backend
   python -m uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd ../viralish_fronted
   npm run dev

   # Terminal 3: Celery Worker
   cd ../backend
   celery -A app.celery_app worker --loglevel=info

   # Terminal 4: Video Uploader Service
   cd video-uploader-service
   python app.py
   ```

### Docker Deployment

```bash
# Build and run all services
docker-compose -f deployment/docker/docker-compose.yml up --build
```

## Monitoring & Analytics

### Performance Metrics
- **Video Generation Success Rate**: Percentage of successful video generations
- **Average Generation Time**: Time from request to completion
- **Platform Engagement**: Views, likes, shares, comments per platform
- **Trend Accuracy**: How well discovered trends perform
- **Agent Performance**: Success rates and response times per agent

### Logging
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Log Aggregation**: Centralized logging with ELK stack
- **Error Tracking**: Sentry integration for error monitoring
- **Performance Monitoring**: Custom metrics and APM

## Security Considerations

### API Security
- JWT authentication with refresh tokens
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS configuration for frontend domains

### Data Protection
- Encryption at rest for sensitive data
- Secure API key management
- GDPR compliance for user data
- Content moderation for generated videos

### Platform Security
- OAuth 2.0 for social media integrations
- Secure credential storage
- Network segmentation in production
- Regular security audits and updates

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with comprehensive tests
4. Ensure all agents are properly documented
5. Submit a pull request with detailed description

### Code Standards
- **Backend**: PEP 8 compliance, type hints, comprehensive docstrings
- **Frontend**: ESLint, Prettier, TypeScript strict mode
- **Documentation**: All new features must be documented
- **Testing**: Unit tests for all agents and services

### Agent Development Guidelines
- Each agent should be modular and independently testable
- Implement proper error handling and logging
- Use async/await for I/O operations
- Include comprehensive type hints
- Document all public methods and parameters

## License

This project is proprietary software. All rights reserved.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `/docs`

---

**Version**: 1.0.0
**Last Updated**: October 2025
**Architecture**: Multi-Agent AI System
**Primary Use Case**: Automated viral video creation and optimization