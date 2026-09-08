"""
AVVO Multi-Platform Video Uploader Service

A FastAPI service for uploading and publishing videos to multiple social media platforms
including Instagram, Facebook, TikTok, Twitter/X, and YouTube.

Features:
- Async video upload and publishing
- Scheduled publishing with APScheduler
- Modular platform-specific uploaders
- Analytics ingestion hooks
- Voice-to-text integration for text inputs
- Comprehensive error handling and logging
"""

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
import uuid
import logging
from datetime import datetime
import json
import cloudinary
import cloudinary.uploader
import requests
from dotenv import load_dotenv

# Import our custom modules
from uploader import (
    upload_instagram_reel,
    upload_facebook_video,
    upload_tiktok_video,
    upload_twitter_video,
    upload_youtube_video,
    upload_to_platform,
    PlatformResult
)
from scheduler import schedule_publish, scheduler
from analytics import ingest_analytics

# Import Zapier service
from zapier_service import schedule_post_via_zapier

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AVVO Multi-Platform Video Uploader",
    description="Upload and publish videos to Instagram, Facebook, TikTok, Twitter/X, and YouTube",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import models from separate file
from models import PublishRequest, PublishStatus, PlatformConfig, HealthResponse

# Global configuration
SUPPORTED_PLATFORMS = ["instagram", "facebook", "tiktok", "twitter", "youtube"]
TEMP_DIR = "/tmp/video_uploads"

# Configure Cloudinary
cloudinary_url = os.getenv('CLOUDINARY_URL')
if cloudinary_url:
    from urllib.parse import urlparse
    parsed = urlparse(cloudinary_url)
    cloudinary.config(
        cloud_name=parsed.hostname,
        api_key=parsed.username,
        api_secret=parsed.password
    )
else:
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# Dependency to check if scheduler is running
def check_scheduler():
    if not scheduler.running:
        raise HTTPException(status_code=503, detail="Scheduler is not running")
    return True

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        scheduler_running=scheduler.running,
        available_platforms=SUPPORTED_PLATFORMS
    )

@app.get("/platforms", response_model=List[PlatformConfig])
async def get_available_platforms():
    """Get list of available platforms and their status"""
    platforms = []
    for platform in SUPPORTED_PLATFORMS:
        # Check if credentials are configured (simplified check)
        credentials_configured = check_platform_credentials(platform)
        platforms.append(PlatformConfig(
            platform=platform,
            enabled=True,
            credentials_configured=credentials_configured
        ))
    return platforms

def check_platform_credentials(platform: str) -> bool:
    """Check if platform credentials are configured"""
    # This is a simplified check - in production, you'd verify actual credentials
    env_vars = {
        "instagram": ["INSTAGRAM_ACCESS_TOKEN", "IG_USER_ID"],
        "facebook": ["FACEBOOK_PAGE_ID", "FACEBOOK_PAGE_TOKEN"],
        "tiktok": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"],
        "twitter": ["TWITTER_BEARER"],
        "youtube": ["YOUTUBE_API_KEY"]
    }
    required_vars = env_vars.get(platform, [])
    return all(os.getenv(var) for var in required_vars)

@app.post("/upload-and-publish", response_model=PublishStatus)
async def upload_and_publish(
    platforms: str = Form(...),
    title: str = Form(""),
    description: str = Form(""),
    publish_at: Optional[str] = Form(None),
    captions: str = Form("{}"),
    voice_to_text: bool = Form(False),
    tags: str = Form("[]"),
    file: UploadFile = File(...),
    background: BackgroundTasks = None,
    scheduler_check: bool = Depends(check_scheduler)
):
    """
    Upload and publish video to multiple platforms

    - **file**: Video file to upload (supports common video formats)
    - **platforms**: List of platforms to publish to
    - **title**: Video title
    - **description**: Video description
    - **publish_at**: Optional ISO datetime for scheduled publishing
    - **captions**: Platform-specific captions and hashtags
    - **voice_to_text**: Enable voice-to-text conversion for text inputs
    """

    # Parse request
    import json
    request = PublishRequest(
        platforms=json.loads(platforms),
        title=title,
        description=description,
        publish_at=publish_at,
        captions=json.loads(captions),
        voice_to_text=voice_to_text,
        tags=json.loads(tags)
    )

    # Validate platforms
    invalid_platforms = [p for p in request.platforms if p not in SUPPORTED_PLATFORMS]
    if invalid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platforms: {invalid_platforms}. Supported: {SUPPORTED_PLATFORMS}"
        )

    # Validate file
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Supported: .mp4, .mov, .avi, .mkv, .webm"
        )

    # Generate unique ID for this publish request
    publish_id = str(uuid.uuid4())

    try:
        # Save uploaded file temporarily
        temp_filename = f"{publish_id}_{file.filename}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)

        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"File saved to {temp_path}")

        # Handle voice-to-text if enabled
        if request.voice_to_text:
            # This would integrate with a voice-to-text service
            # For now, we'll just log it
            logger.info("Voice-to-text processing would be applied here")

        # Schedule or publish immediately
        if request.publish_at:
            try:
                # Validate datetime format
                scheduled_time = datetime.fromisoformat(request.publish_at.replace('Z', '+00:00'))
                if scheduled_time <= datetime.utcnow():
                    raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

                # Schedule the publish
                schedule_publish(temp_path, request, publish_id)

                logger.info(f"Video scheduled for publishing at {request.publish_at}")

                return PublishStatus(
                    status="scheduled",
                    message=f"Video scheduled for publishing to {len(request.platforms)} platforms",
                    publish_id=publish_id,
                    scheduled_at=request.publish_at
                )

            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")

        else:
            # Publish immediately and wait for completion
            results = await publish_to_platforms(temp_path, request, publish_id)

            # Check if all steps succeeded
            cloudinary_success = results.get("cloudinary", {}).get("status") == "success"
            zapier_success = results.get("zapier", {}).get("status") == "success"

            if cloudinary_success and zapier_success:
                return PublishStatus(
                    status="completed",
                    message="publishing completed successfully",
                    publish_id=publish_id,
                    scheduled_at=None,
                    results=results
                )
            else:
                error_messages = []
                if not cloudinary_success:
                    error_messages.append(results.get("cloudinary", {}).get("error", "Cloudinary upload failed"))
                if not zapier_success:
                    error_messages.append("Zapier send failed")
                raise HTTPException(
                    status_code=500,
                    detail=f"Publishing failed: {'; '.join(error_messages)}"
                )

    except Exception as e:
        logger.error(f"Error processing upload request: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def publish_to_platforms(path: str, request: PublishRequest, publish_id: str):
    """Background task to publish video via Cloudinary and Zapier"""
    results = {}

    logger.info(f"Starting publish to Zapier for ID: {publish_id}")

    try:
        # Upload video to Cloudinary
        try:
            logger.info(f"Uploading {path} to Cloudinary")
            upload_result = cloudinary.uploader.upload(path, resource_type="video")
            secure_url = upload_result['secure_url']
            logger.info(f"Uploaded to Cloudinary: {secure_url}")
            results["cloudinary"] = {"status": "success", "url": secure_url}
        except Exception as e:
            logger.error(f"Failed to upload {path} to Cloudinary: {str(e)}")
            results["cloudinary"] = {"status": "error", "error": str(e)}
            # Clean up temp file
            if os.path.exists(path):
                os.remove(path)
            return results

        # Send to Zapier for all platforms
        try:
            logger.info(f"Sending {publish_id} to Zapier")
            zapier_payload = {
                "video": {
                    "url": secure_url,
                    "description": request.captions.get("default", request.description),
                    "platforms": {
                        p: {"enabled": True, "schedule": {"datetime": datetime.utcnow().isoformat()}} for p in request.platforms
                    }
                }
            }
            zapier_result = schedule_post_via_zapier(zapier_payload)
            if zapier_result.get("status") == "success":
                logger.info(f"Successfully sent {publish_id} to Zapier")
                results["zapier"] = {"status": "success", "response": zapier_result.get("response")}
            else:
                logger.error(f"Zapier responded with error for {publish_id}: {zapier_result.get('response')}")
                results["zapier"] = {"status": "error", "error": zapier_result.get("response")}
        except Exception as e:
            logger.error(f"Failed to send {publish_id} to Zapier: {str(e)}")
            results["zapier"] = {"status": "error", "error": str(e)}

        # Log final results
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        logger.info(f"Publish completed for ID {publish_id}: {success_count}/{len(results)} successful")

    except Exception as e:
        logger.error(f"Critical error during publishing: {e}")
        results["general"] = {"status": "error", "error": str(e)}
    finally:
        # Clean up temp file
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Cleaned up temp file: {path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {path}: {e}")

    return results

@app.get("/publish-status/{publish_id}")
async def get_publish_status(publish_id: str):
    """Get the status of a publish request"""
    # In a real implementation, this would query a database
    # For now, return a placeholder response
    return {
        "publish_id": publish_id,
        "status": "unknown",
        "message": "Status tracking not implemented in this demo"
    }

@app.post("/api/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    """Simple video upload endpoint that returns the file path"""
    # Validate file
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Supported: .mp4, .mov, .avi, .mkv, .webm"
        )

    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"uploaded_{file_id}{file_extension}"
    save_path = os.path.join("..", "uploads", "videos", new_filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save the file
    with open(save_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    logger.info(f"File uploaded to {save_path}")

    # Return path relative to backend directory for publisher task
    return_path = os.path.join("uploads", "videos", new_filename)
    return {"file_path": return_path}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AVVO Multi-Platform Video Uploader",
        "version": "1.0.0",
        "description": "Upload and publish videos to multiple social media platforms",
        "endpoints": {
            "health": "/health",
            "platforms": "/platforms",
            "upload": "/upload-and-publish",
            "simple_upload": "/api/videos/upload",
            "status": "/publish-status/{publish_id}"
        },
        "supported_platforms": SUPPORTED_PLATFORMS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)