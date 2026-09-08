from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import json
from app.services.zapier_service import schedule_post_via_zapier
from app.services.video_uploader import upload_to_cloudinary
from app.tasks import publisher_task
from database.db import SessionLocal
from database.models import Job

router = APIRouter()

class PublisherRequest(BaseModel):
    videos: Optional[List[str]] = None  # Assuming file paths
    platforms: Optional[List[str]] = None  # Platforms to publish to
    caption: Optional[str] = ""  # Caption for the video
    jsonPayload: Optional[dict] = None  # The JSON payload for Zapier

class PublisherResponse(BaseModel):
    status: str  # 'success' | 'failed'
    publishedUrls: Optional[List[str]] = None
    message: str
    job_id: Optional[str] = None

@router.post("/publish")
async def publish_content(request: PublisherRequest):
    # Handle different request formats
    videos = request.videos or []
    platforms = request.platforms or []
    caption = request.caption or ""
    json_payload = request.jsonPayload or {}

    # If videos are not provided, try to get from json_payload
    if not videos and json_payload.get("video"):
        videos = [json_payload["video"]]

    # If platforms are not provided, try to get from json_payload
    if not platforms and json_payload.get("platforms"):
        platforms = list(json_payload["platforms"].keys())

    if not videos:
        raise HTTPException(status_code=400, detail="No videos provided")

    # Validate video paths
    for video_path in videos:
        if not os.path.exists(video_path):
            raise HTTPException(status_code=400, detail=f"Video not found: {video_path}")

    job_id = str(uuid.uuid4())
    
    # Create a Job entry
    db = SessionLocal()
    job = Job(id=job_id, status='processing', progress=0)
    db.add(job)
    db.commit()
    db.close()
    
    # Queue the Celery task
    publisher_task.delay(videos, platforms, caption, json_payload, job_id)
    
    return PublisherResponse(
        status="processing",
        message=f"Publishing {len(request.videos)} videos queued",
        job_id=job_id
    )

@router.get("/status/{job_id}")
async def get_publish_status(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == 'completed':
        result = json.loads(job.result) if job.result else {}
        return {"status": "completed", "results": result}
    elif job.status == 'failed':
        return {"status": "failed", "error": job.result}
    else:
        return {"status": "processing", "progress": job.progress}