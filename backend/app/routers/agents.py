from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from app.services.knowledge_base_service import KnowledgeBaseService
from app.tasks import publisher_task, generate_video_task  # Note: discover_trends_task, generate_script_task, optimize_feedback_task removed
from database.db import SessionLocal
from database.models import Job
import json
import google.generativeai as genai
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()

class TrendDiscoveryRequest(BaseModel):
    links: list[str] = []
    voiceInput: str = ""  # Can be text or file path
    files: list[str] = []

class ScriptGenerationRequest(BaseModel):
    topic: str
    instructions: str = ""
    voiceInput: str = ""
    files: list[str] = []

class ScriptGenerationResponse(BaseModel):
    script: str
    confidence: float
    suggestions: list[str] = []

class OptimizationRequest(BaseModel):
    script: str
    viral_video: str  # URL or path

class VideoGenerationRequest(BaseModel):
    script: str
    json_plan: str = ""  # Optional JSON plan

class PublisherRequest(BaseModel):
    videos: list[str]
    platforms: list[str]
    caption: str
    jsonPlan: str = ""

@router.post("/trend-discovery")
async def discover_trends(request: TrendDiscoveryRequest):
    logger.info(f"Trend discovery requested with links: {request.links}, voice: {request.voiceInput}, files: {request.files}")
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id)
    db.add(job)
    db.commit()
    db.close()

    # Call the agent directly
    from agents.trend_discovery.trend_discovery_agent import TrendDiscoveryAgent
    agent = TrendDiscoveryAgent(gemini_api_key=os.environ.get("GEMINI_API_KEY"))
    trends = await agent.discover_trends(request.links, request.voiceInput, request.files)

    # Update job with result
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    job.result = json.dumps(trends)
    job.status = 'completed'
    job.progress = 100
    db.commit()
    db.close()

    logger.info(f"Trend discovery completed for job {job_id}")
    return {"job_id": job_id, "status": "completed", "result": trends}

@router.get("/trend-discovery/status/{job_id}")
async def get_trend_status(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == 'completed':
        return {"status": "completed", "result": json.loads(job.result), "progress": 100}
    return {"status": "processing", "progress": job.progress}

@router.post("/story-ideation")
async def generate_script(request: ScriptGenerationRequest):
    logger.info(f"Story ideation requested for topic: {request.topic}, instructions: {request.instructions}")
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id)
    db.add(job)
    db.commit()
    db.close()

    # Call the agent directly
    from agents.story_ideation.story_ideation_agent import StoryIdeationAgent
    agent = StoryIdeationAgent(gemini_api_key=os.environ.get("GEMINI_API_KEY"))
    script = await agent.generate_script(request.topic, request.instructions, request.voiceInput, request.files)

    # Update job with result
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    job.result = json.dumps(script)
    job.status = 'completed'
    job.progress = 100
    db.commit()
    db.close()

    logger.info(f"Story ideation completed for job {job_id}")
    return {"job_id": job_id, "status": "completed", "result": script}

@router.get("/story-ideation/status/{job_id}")
async def get_script_status(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == 'completed':
        return {"status": "completed", "result": json.loads(job.result), "progress": 100}
    return {"status": "processing", "progress": job.progress}

@router.post("/story-ideation/refine")
async def refine_script(request: ScriptGenerationRequest):
    # Similar to generate_script, but for refining
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id)
    db.add(job)
    db.commit()
    db.close()

    # Call the agent directly
    from agents.story_ideation.story_ideation_agent import StoryIdeationAgent
    agent = StoryIdeationAgent(gemini_api_key=os.environ.get("GEMINI_API_KEY"))
    script = await agent.generate_script(request.topic, request.instructions, request.voiceInput, request.files)

    # Update job with result
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    job.result = json.dumps(script)
    job.status = 'completed'
    job.progress = 100
    db.commit()
    db.close()

    logger.info(f"Story ideation refine completed for job {job_id}")
    return {"job_id": job_id, "status": "completed", "result": script}

@router.post("/optimization")
async def optimize_feedback(request: OptimizationRequest):
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id)
    db.add(job)
    db.commit()
    db.close()

    # Call the optimization logic directly
    kb_service = KnowledgeBaseService()
    tips = kb_service.get_all_tips()

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
Act as an expert viral video consultant.
Analyze the provided script against a knowledge base of viral patterns.

Script: {request.script}
Viral Video Link: {request.viral_video}
Knowledge Base Tips: {json.dumps([tip.dict() for tip in tips])}

Provide detailed feedback in the following JSON format:
{{
  "overall_score": "Score out of 100.",
  "strengths": ["List of strengths."],
  "areas_for_improvement": ["List of improvements."],
  "actionable_recommendations": ["List of recommendations."],
  "viral_patterns_matched": ["List of matched patterns."],
  "refined_prompt": "Suggested prompt for regeneration.",
  "analytics": {{
    "hook_effectiveness": "Score 1-10",
    "storytelling_quality": "Score 1-10",
    "visual_appeal": "Score 1-10",
    "cta_strength": "Score 1-10",
    "length_optimization": "Score 1-10"
  }},
  "comparison": "Comparison with viral video if link provided."
}}
"""
    response = model.generate_content(prompt)
    feedback = json.loads(response.text)

    # Update job with result
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    job.result = json.dumps(feedback)
    job.status = 'completed'
    job.progress = 100
    db.commit()
    db.close()

    logger.info(f"Optimization completed for job {job_id}")
    return {"job_id": job_id, "status": "completed", "result": feedback}

@router.get("/optimization/status/{job_id}")
async def get_optimization_status(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == 'completed':
        return {"status": "completed", "result": json.loads(job.result), "progress": 100}
    return {"status": "processing", "progress": job.progress}

@router.post("/video-generation")
async def generate_video(request: VideoGenerationRequest):
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id)
    db.add(job)
    db.commit()
    db.close()
    # Queue the Celery task asynchronously
    generate_video_task.delay(request.script, request.json_plan, job_id)
    logger.info(f"Video generation task queued for job {job_id}")
    return {"job_id": job_id, "status": "processing"}

@router.get("/video-generation/status/{job_id}")
async def get_video_status(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == 'completed':
        return {"status": "completed", "result": json.loads(job.result), "progress": 100}
    return {"status": "processing", "progress": job.progress}

@router.post("/video-generation/refine")
async def refine_video(request: VideoGenerationRequest):
    # Similar to generate_video, but for refining
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id)
    db.add(job)
    db.commit()
    db.close()
    # Queue the Celery task asynchronously
    generate_video_task.delay(request.script, request.json_plan, job_id)
    logger.info(f"Video generation refine task queued for job {job_id}")
    return {"job_id": job_id, "status": "processing"}

@router.get("/video-generation/download/{job_id}")
async def download_video(job_id: str):
    # Return the video file path or URL
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job or job.status != 'completed':
        raise HTTPException(status_code=404, detail="Video not found or not ready")
    result = json.loads(job.result)
    video_path = result.get('video_path')
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return {"download_url": f"/api/videos/{job_id}"}  # Placeholder

@router.post("/publisher")
async def publisher(request: PublisherRequest):
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id)
    db.add(job)
    db.commit()
    db.close()
    # Queue the Celery task asynchronously
    publisher_task.delay(request.videos, request.platforms, request.caption, request.jsonPlan, job_id)
    logger.info(f"Publisher task queued for job {job_id}")
    return {"job_id": job_id, "status": "processing"}

@router.get("/publisher/status/{job_id}")
async def get_publisher_status(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in ['completed', 'failed']:
        return {"status": job.status, "result": json.loads(job.result), "progress": 100}
    return {"status": "processing", "progress": job.progress}

class AIAssistantRequest(BaseModel):
    json_plan: str
    instructions: str = ""

@router.post("/ai-assistant")
async def ai_assistant(request: AIAssistantRequest):
    # Use Gemini to edit the JSON plan based on instructions
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Edit the following JSON plan based on instructions: {request.instructions}. JSON: {request.json_plan}. Return the updated JSON."
    response = model.generate_content(prompt)
    updated_plan = json.loads(response.text)
    return {"updated_plan": updated_plan}

@router.get("/")
async def get_agents():
    return {"agents": ["TrendDiscoveryAgent", "StoryIdeationAgent", "VideoGenerationAgent"]}