from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import agents, dashboard, optimization, review, simulation, knowledge_base, criticism, prompts, video, comments, chat, auth, publisher, collaboration, notifications
# from app.orchestrator import Orchestrator  # Commented out due to missing agents module

# Import services to initialize scheduler
from app.services import video_scheduler

# Load environment variables
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize database
from database.db import create_tables
create_tables()

app = FastAPI(
    title="AVVO - Agentic Viral Video Orchestrator",
    description="A self-optimizing multi-agent system for viral video creation.",
    version="1.0.0",
)

# Mount static files for serving uploaded/generated videos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/videos", StaticFiles(directory="uploads/videos"), name="videos")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth, prefix="/api/auth", tags=["Authentication"])
app.include_router(agents, prefix="/api/agents", tags=["Agents"])
app.include_router(dashboard, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(optimization, prefix="/api/optimization", tags=["Optimization"])
app.include_router(review, prefix="/api/review", tags=["Review"])
app.include_router(simulation, prefix="/api/simulation", tags=["Simulation"])
app.include_router(knowledge_base, prefix="/api/knowledge", tags=["Knowledge Base"])
app.include_router(criticism, prefix="/api/criticism", tags=["Criticism"])
app.include_router(prompts, prefix="/api/prompts", tags=["Prompts"])
app.include_router(video, prefix="/api/video", tags=["Video"])
app.include_router(comments, prefix="/api/comments", tags=["Comments"])
app.include_router(chat, prefix="/api/chat", tags=["Chat"])
app.include_router(publisher, prefix="/api/publisher", tags=["Publisher"])
app.include_router(collaboration, tags=["Collaboration"])
app.include_router(notifications, prefix="/api/notifications", tags=["Notifications"])

# orchestrator = Orchestrator()  # Commented out

# @app.post("/api/orchestrate")
# async def orchestrate():
#     result = await orchestrator.run_pipeline()
#     return result

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to AVVO Backend"}