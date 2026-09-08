# CLAUDE.md — AVVO Project Guide

> **AVVO** (Agentic Viral Video Orchestrator) is a multi-agent AI platform that autonomously discovers trends, generates video scripts, produces videos, and publishes content across social media platforms.

---

## Project Overview

AVVO orchestrates 7+ specialized AI agents through a pipeline that goes from raw trend signals to published viral video content. The system uses Google Gemini 2.5-flash as the primary LLM, Vertex AI Veo for video generation, and a reinforcement learning engine to continuously optimize creative strategy.

---

## Repository Structure

```
AVVO/
├── backend/                        # FastAPI Python backend
│   ├── app/
│   │   ├── main.py                 # App entry point, CORS, router registration
│   │   ├── orchestrator.py         # EnhancedOrchestrator — 7-stage pipeline
│   │   ├── celery_app.py           # Celery config (Redis broker)
│   │   ├── tasks.py                # Async Celery task definitions
│   │   ├── session_store.py        # In-memory session management
│   │   ├── websocket_manager.py    # WebSocket connection manager
│   │   └── routers/                # API route handlers
│   │       ├── agents.py           # Core agent pipeline endpoints
│   │       ├── video.py            # Video upload/generate/publish
│   │       ├── dashboard.py        # Analytics & monitoring
│   │       ├── chat.py             # WebSocket chat
│   │       ├── notifications.py    # Notification system
│   │       ├── auth.py             # Authentication
│   │       ├── publisher.py        # Publishing controls
│   │       ├── review.py           # Human review workflow
│   │       ├── simulation.py       # Pipeline simulation
│   │       ├── optimization.py     # Strategy optimization
│   │       ├── knowledge_base.py   # RAG knowledge base
│   │       ├── collaboration.py    # Team collaboration
│   │       ├── criticism.py        # Content critique
│   │       ├── comments.py         # Comment management
│   │       └── prompts.py          # Prompt management
│   ├── agents/                     # Specialized AI agents
│   │   ├── trend_discovery/
│   │   ├── story_ideation/
│   │   ├── video_generation/
│   │   ├── optimization_feedback/
│   │   ├── brand_safety/
│   │   ├── predictive_intelligence/
│   │   └── documentation/
│   ├── services/                   # External service integrations
│   │   ├── gemini_service.py       # Google Gemini LLM
│   │   ├── veo_service.py          # Vertex AI Veo video generation
│   │   ├── sora_service.py         # OpenAI Sora
│   │   ├── zapier_service.py       # Social media webhooks
│   │   ├── video_analytics.py      # Platform metrics
│   │   ├── video_scheduler.py      # Scheduled posting
│   │   ├── video_uploader.py       # File upload & CDN
│   │   └── knowledge_base_service.py
│   ├── database/
│   │   ├── db.py                   # SQLAlchemy + PostgreSQL setup
│   │   ├── models.py               # Trend, Script, Video, Job models
│   │   ├── mongodb.py              # MongoDB connection
│   │   ├── mongodb_models.py       # Comment, ChatMessage, Notification
│   │   └── vector_db.py            # FAISS vector store
│   ├── models/
│   │   └── knowledge_base.py
│   ├── data/                       # FAISS index and persistent data
│   ├── uploads/                    # User-uploaded files
│   ├── video-uploader-service/     # Standalone upload microservice (port 8002)
│   ├── Dockerfile
│   └── requirements.txt
├── AVVO_fronted/                   # React 19 + TypeScript frontend
│   ├── pages/                      # Route-level page components
│   ├── components/                 # Shared UI components
│   ├── services/apiService.ts      # Backend API client
│   ├── contexts/                   # React Context providers
│   ├── App.tsx
│   ├── vite.config.ts
│   └── tailwind.config.js
├── deployment/
│   └── docker/
│       ├── docker-compose.yml      # Full-stack service orchestration
│       ├── Dockerfile.backend
│       └── Dockerfile.frontend
├── .env.example                    # Required env vars template
├── test_expert_features.py         # Agent unit + integration tests
└── test_workflow_integration.py    # End-to-end workflow tests
```

---

## Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.104+ with Uvicorn |
| Validation | Pydantic v2 |
| Primary DB | PostgreSQL via SQLAlchemy 2.0 |
| Document DB | MongoDB 7 (comments, chat, notifications) |
| Vector DB | FAISS (semantic search / RAG) |
| Cache/Queue | Redis (port 6380) |
| Task Queue | Celery 5.3 with gevent workers |
| Primary LLM | Google Gemini 2.5-flash |
| Video Gen | Google Vertex AI Veo |
| Alt LLMs | Claude (Anthropic), OpenAI GPT |
| ML | scikit-learn, Prophet, NumPy, Pandas |
| NLP | spaCy 3.7 |
| Audio | librosa, pydub, FFmpeg |
| Monitoring | Prometheus, LangSmith, Datadog |
| Media CDN | Cloudinary |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React 19 + TypeScript 5.8 |
| Build | Vite 6 |
| Routing | React Router DOM 7 |
| Styling | Tailwind CSS 4 |
| State | React Context API |
| Real-time | WebSocket (native) |

### Infrastructure (Docker)
| Service | Port | Role |
|---------|------|------|
| api_gateway | 8000 | FastAPI backend |
| frontend | 3001 | React via Nginx |
| chat_service | 8001 | WebSocket server |
| video_uploader | 8002 | File upload service |
| redis | 6380 | Cache + Celery broker |
| mongo | 27017 | Document database |
| worker | — | Celery async worker |

---

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL (local) or use Docker
- Redis (local) or use Docker

### Backend (Local)
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and fill environment variables
cp ../.env.example ../.env

# Run FastAPI dev server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker (separate terminal)
celery -A app.celery_app worker --loglevel=info --pool=gevent
```

### Frontend (Local)
```bash
cd AVVO_fronted
npm install
npm run dev       # Vite dev server on http://localhost:5173
```

### Video Upload Service
```bash
cd backend/video-uploader-service
python app.py     # Runs on port 8002
```

### Full Stack (Docker)
```bash
docker-compose -f deployment/docker/docker-compose.yml up --build
```

---

## Environment Variables

All secrets live in `.env` (never commit). See `.env.example` for required keys:

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Google Gemini (primary LLM) |
| `GOOGLE_CLOUD_API_KEY` | Vertex AI Veo, Speech APIs |
| `OPENAI_API_KEY` | GPT models + Sora |
| `ANTHROPIC_API_KEY` | Claude models |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis broker URL |
| `MONGODB_URI` | MongoDB connection |
| `CLOUDINARY_URL` | Media CDN |
| `ZAPIER_WEBHOOK_URL` | Social media publishing |
| `TIKTOK_API_KEY` | TikTok platform API |
| `YOUTUBE_API_KEY` | YouTube Data API |
| `INSTAGRAM_API_KEY` | Instagram Graph API |
| `LANGCHAIN_API_KEY` | LangSmith tracing |
| `DATADOG_API_KEY` | APM monitoring |
| `FAISS_INDEX_PATH` | Vector store path |

Platform Profile IDs (used for Zapier publishing targets):
- `YOUTUBE_PROFILE_ID`
- `INSTAGRAM_PROFILE_ID`
- `TIKTOK_PROFILE_ID`

---

## Core API Endpoints

### Agent Pipeline
```
POST   /api/agents/trend-discovery          # Run trend discovery
GET    /api/agents/trend-discovery/status/{job_id}
POST   /api/agents/story-ideation           # Generate video script
GET    /api/agents/story-ideation/status/{job_id}
POST   /api/agents/video-generation         # Generate video
GET    /api/agents/video-generation/status/{job_id}
POST   /api/agents/publisher                # Publish to platforms
GET    /api/agents/publisher/status/{job_id}
POST   /api/agents/optimization             # Run optimization
```

### Video Operations
```
POST   /api/video/upload
POST   /api/video/analyze
POST   /api/video/generate
GET    /api/video/generate/status/{job_id}
POST   /api/video/upload-and-publish
GET    /api/video/publish-status/{publish_id}
POST   /api/video/transcribe
POST   /api/video/trim
```

### Real-time
```
WS     /api/chat/ws                         # WebSocket chat
GET    /api/notifications/
GET    /api/notifications/online-users
```

---

## Database Schema

### PostgreSQL (SQLAlchemy)
- **Trend** — `id, platform, summary, timestamp`
- **Script** — `id, trend_id (FK), script, critique, score`
- **Video** — `id, script_id (FK), path, engagement_score, timestamp`
- **Job** — `id (str), status, result, progress (0-100), created_at`

### MongoDB
- **Comment** — user tickets with status workflow (OPEN → IN_PROGRESS → RESOLVED → CLOSED)
- **ChatMessage** — real-time chat with soft delete
- **Notification** — typed events (NEW_COMMENT, NEW_CHAT, FAILED_TASK, etc.)

---

## Async Job Pattern

Long-running agent tasks follow this pattern:
1. Request hits router → creates a `Job` record with `status=processing`
2. Router dispatches Celery task → returns `job_id` immediately
3. Client polls `GET /status/{job_id}` for progress (0–100%)
4. On completion, `Job.result` contains the full response JSON

---

## Testing

```bash
# Expert feature tests (unit + agent integration)
python test_expert_features.py

# End-to-end workflow tests
python test_workflow_integration.py
```

Test reports are written as timestamped JSON files in the project root.

---

## Code Conventions

- **Python:** Follow PEP 8. Use `async/await` for all I/O. Use Pydantic models for request/response validation.
- **TypeScript:** Strict mode. Functional components with hooks. No `any` types.
- **API:** All responses include a `status` field. Errors return `{"status": "error", "message": "..."}`.
- **Agents:** Each agent is a self-contained module with a primary async method as its entry point.
- **Environment:** Never hardcode credentials. Always read from `os.environ` or `.env`.
- **Commits:** Descriptive imperative messages. Group related changes in a single commit.

---

## Key Architectural Decisions

1. **Celery over asyncio for heavy jobs** — Video generation and publishing can take minutes; Celery + Redis provides reliable queuing, retries, and worker scaling.
2. **Dual database strategy** — PostgreSQL for structured relational data (jobs, trends, scripts, videos); MongoDB for high-write document data (chat, notifications, comments).
3. **FAISS for RAG** — Lightweight, file-based vector search avoids a dedicated vector database service.
4. **Agent isolation** — Each agent is independently importable and testable. The orchestrator wires them together but does not bleed state between agents.
5. **Reinforcement learning feedback loop** — The ReinforcementStrategyEngine uses a contextual bandit (UCB algorithm) to continuously improve creative parameter selection based on real engagement metrics.
