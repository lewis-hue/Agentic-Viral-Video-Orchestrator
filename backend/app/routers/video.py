from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
import uuid
from datetime import datetime
import json
import requests
import logging
from app.services.knowledge_base_service import KnowledgeBaseService
# Removed OpenAI import, using Gemini instead
import google.generativeai as genai
from google.genai import types
import os

logger = logging.getLogger(__name__)

# Configure Gemini with API key
from google import genai
from google.genai import types

api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
if api_key:
    genai_client = genai.Client(
        api_key=api_key,
    )
else:
    genai_client = None
    logger.warning("No Google API key configured. Set GOOGLE_CLOUD_API_KEY.")
from app.services.video_uploader import upload_to_platform, PlatformResult
from app.services.video_scheduler import schedule_publish, scheduler, get_scheduler_status, get_job_status
from app.services.video_analytics import ingest_analytics
from app.services.veo_service import veo_service, VeoGenerationRequest
from agents.video_generation.dynamic_shot_orchestrator import DynamicShotOrchestrator
from app.tasks import generate_video_task
from database.db import SessionLocal
from database.models import Job

router = APIRouter()

# Directory to store uploaded videos
UPLOAD_DIR = "uploads/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Directory for general attachments
ATTACH_DIR = "uploads/attachments"
os.makedirs(ATTACH_DIR, exist_ok=True)

# Directory for audio files
AUDIO_DIR = "uploads/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

class VideoUploadResponse(BaseModel):
    filename: str
    file_path: str
    upload_time: str
    size: int

class VideoAnalysisRequest(BaseModel):
    user_video_path: str
    reference_video: str  # Link or path to reference video
    voice_input: str = None  # Optional voice transcription
    attached_files: list[str] = []  # Optional list of attached file paths

class VideoAnalysisResponse(BaseModel):
    virality_analysis: str
    comparison: str
    criticism: str
    suggestions: list[str]
    json_plan: dict
    workbench_link: str

class AttachResponse(BaseModel):
    filename: str
    file_path: str
    upload_time: str
    size: int

class VoiceTranscriptionRequest(BaseModel):
    audio_path: str

class VoiceTranscriptionResponse(BaseModel):
    transcription: str

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    # Validate file type (e.g., only video files)
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: mp4, avi, mov, mkv, webm")

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return VideoUploadResponse(
        filename=unique_filename,
        file_path=file_path,
        upload_time=datetime.now().isoformat(),
        size=len(content)
    )

@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(request: VideoAnalysisRequest):
    kb_service = KnowledgeBaseService()
    tips = kb_service.get_all_tips()

    # Incorporate voice input and attached files into analysis
    additional_context = ""
    if request.voice_input:
        additional_context += f" User voice input: {request.voice_input}"
    if request.attached_files:
        additional_context += f" Attached files: {', '.join(request.attached_files)}"

    # Use Gemini for AI analysis
    if not genai_client:
        analysis_text = "Gemini client not configured"
    else:
        prompt = f"Analyze the following video for virality: {request.reference_video}. {additional_context}. Provide virality analysis, comparison, criticism, and suggestions."
        try:
            response = genai_client.models.generate_content(
                model="gemini-1.5-pro",
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
            )
            analysis_text = response.text
        except Exception as e:
            logger.error(f"Gemini API error in analysis: {e}")
            analysis_text = f"Analysis failed due to API error: {str(e)}"

    # Parse the response (assuming Gemini provides structured output)
    virality_analysis = f"Gemini analysis: {analysis_text}"
    comparison = f"Comparison based on Gemini: {analysis_text}"
    criticism = " ".join([f"Based on '{tip.tip}': {tip.description}" for tip in tips[:3]])
    suggestions = [tip.tip for tip in tips[:5]]

    # Generate JSON plan using Gemini
    if not genai_client:
        json_plan = {
            "title": "Viral Video Improvement Plan",
            "steps": [
                {"step": "Improve Hook", "description": "Start with a question or surprising fact."},
                {"step": "Enhance Storytelling", "description": "Use Hero's Journey structure."},
                {"step": "Optimize Visuals", "description": "Use high-contrast colors and dynamic movements."}
            ],
            "tips": [tip.dict() for tip in tips],
            "additional_context": additional_context
        }
    else:
        plan_prompt = f"Create a JSON plan for improving the video based on: {analysis_text}"
        try:
            plan_response = genai_client.models.generate_content(
                model="gemini-1.5-pro",
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=plan_prompt)])]
            )
            json_plan = json.loads(plan_response.text) if plan_response.text else {
                "title": "Viral Video Improvement Plan",
                "steps": [
                    {"step": "Improve Hook", "description": "Start with a question or surprising fact."},
                    {"step": "Enhance Storytelling", "description": "Use Hero's Journey structure."},
                    {"step": "Optimize Visuals", "description": "Use high-contrast colors and dynamic movements."}
                ],
                "tips": [tip.dict() for tip in tips],
                "additional_context": additional_context
            }
        except Exception as e:
            logger.error(f"Gemini API error in plan generation: {e}")
            json_plan = {
                "title": "Viral Video Improvement Plan",
                "steps": [
                    {"step": "Improve Hook", "description": "Start with a question or surprising fact."},
                    {"step": "Enhance Storytelling", "description": "Use Hero's Journey structure."},
                    {"step": "Optimize Visuals", "description": "Use high-contrast colors and dynamic movements."}
                ],
                "tips": [tip.dict() for tip in tips],
                "additional_context": additional_context
            }

    workbench_link = f"https://agentic-plan-workbench.com/import?plan={json.dumps(json_plan)}"  # Placeholder link

    return VideoAnalysisResponse(
        virality_analysis=virality_analysis,
        comparison=comparison,
        criticism=criticism,
        suggestions=suggestions,
        json_plan=json_plan,
        workbench_link=workbench_link
    )

@router.post("/attach", response_model=AttachResponse)
async def attach_file(file: UploadFile = File(...)):
    # Validate file type (allow common types)
    allowed_extensions = {".txt", ".pdf", ".docx", ".jpg", ".png", ".mp3", ".wav"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: txt, pdf, docx, jpg, png, mp3, wav")

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(ATTACH_DIR, unique_filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return AttachResponse(
        filename=unique_filename,
        file_path=file_path,
        upload_time=datetime.now().isoformat(),
        size=len(content)
    )

@router.post("/upload-audio", response_model=VideoUploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    # Validate file type (audio files)
    allowed_extensions = {".mp3", ".wav", ".m4a", ".ogg"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: mp3, wav, m4a, ogg")

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(AUDIO_DIR, unique_filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return VideoUploadResponse(
        filename=unique_filename,
        file_path=file_path,
        upload_time=datetime.now().isoformat(),
        size=len(content)
    )

@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(request: VoiceTranscriptionRequest):
    # Use Gemini for transcription
    try:
        if not genai_client:
            raise HTTPException(status_code=500, detail="Gemini client not configured")

        with open(request.audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part(
                            inline_data=types.Blob(data=audio_bytes, mime_type='audio/mp3')
                        ),
                        types.Part(text='Transcribe the audio.')
                    ]
                )
            ]
        )
        transcription = response.text
        return VoiceTranscriptionResponse(transcription=transcription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


# New models for multi-platform upload
class PublishRequest(BaseModel):
    platforms: List[str] = Field(..., description="List of platforms to publish to", examples=[["instagram", "tiktok", "youtube"]])
    title: str = Field("", description="Video title")
    description: str = Field("", description="Video description")
    publish_at: Optional[str] = Field(None, description="ISO datetime for scheduled publishing")
    captions: Dict[str, str] = Field(default_factory=dict, description="Platform-specific captions/hashtags")
    voice_to_text: Optional[bool] = Field(False, description="Enable voice-to-text for text inputs")
    tags: List[str] = Field(default_factory=list, description="Video tags/hashtags")

class VideoGenerationRequest(BaseModel):
    script: str
    json_plan: Optional[str] = None
    publish_request: Optional[PublishRequest] = None
    prompt: Optional[str] = None  # Prompt for Veo video generation
    aspect_ratio: str = "16:9"
    duration_seconds: str = "4"
    sample_count: int = 1
    person_generation: str = "allow_all"
    add_watermark: bool = True
    include_rai_reason: bool = True
    generate_audio: bool = True
    resolution: str = "720p"

class VideoGenerationResponse(BaseModel):
    video_path: str
    status: str
    job_id: Optional[str] = None
    publish_id: Optional[str] = None

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    job_id = str(uuid.uuid4())
    
    # Create a Job entry
    db = SessionLocal()
    job = Job(id=job_id, status='processing', progress=0)
    db.add(job)
    db.commit()
    db.close()
    
    # Queue the Celery task with the prompt and publish_request
    generate_video_task.delay(request.script, request.json_plan, job_id, request.prompt, request.publish_request.dict() if request.publish_request else None)
    
    return VideoGenerationResponse(video_path="", status="processing", job_id=job_id)

class PublishStatus(BaseModel):
    status: str
    message: str
    publish_id: Optional[str] = None
    scheduled_at: Optional[str] = None
    results: Optional[Dict[str, Any]] = None

class PlatformConfig(BaseModel):
    platform: str
    enabled: bool
    credentials_configured: bool

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    scheduler_running: bool
    available_platforms: List[str]

# Global configuration
SUPPORTED_PLATFORMS = ["zapier"]  # Using Zapier for all platforms
TEMP_DIR = "/tmp/video_uploads"

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# Dependency to check if scheduler is running
def check_scheduler():
    if not scheduler.running:
        raise HTTPException(status_code=503, detail="Scheduler is not running")
    return True

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        scheduler_running=scheduler.running,
        available_platforms=SUPPORTED_PLATFORMS
    )

@router.get("/platforms", response_model=List[PlatformConfig])
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
        "youtube": ["YOUTUBE_API_KEY"],
        "zapier": ["ZAPIER_WEBHOOK_URL", "YOUTUBE_PROFILE_ID", "INSTAGRAM_PROFILE_ID", "TIKTOK_PROFILE_ID"]
    }
    required_vars = env_vars.get(platform, [])
    return all(os.getenv(var) for var in required_vars)

@router.post("/upload-and-publish", response_model=PublishStatus)
async def upload_and_publish(
    request: PublishRequest,
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

        # Handle voice-to-text if enabled
        if request.voice_to_text:
            # This would integrate with a voice-to-text service
            # For now, we'll just log it
            pass

        # Schedule or publish immediately
        if request.publish_at:
            try:
                # Validate datetime format
                scheduled_time = datetime.fromisoformat(request.publish_at.replace('Z', '+00:00'))
                if scheduled_time <= datetime.utcnow():
                    raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

                # Schedule the publish
                schedule_publish(temp_path, request, publish_id)

                return PublishStatus(
                    status="scheduled",
                    message=f"Video scheduled for publishing to {len(request.platforms)} platforms",
                    publish_id=publish_id,
                    scheduled_at=request.publish_at
                )

            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")

        else:
            # Schedule immediate publishing using the scheduler
            schedule_publish(temp_path, request, publish_id, run_at=datetime.utcnow())

            return PublishStatus(
                status="publishing",
                message=f"Video publishing started to {len(request.platforms)} platforms",
                publish_id=publish_id
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def publish_to_platforms(path: str, request: PublishRequest, publish_id: str):
    """Background task to publish video via Zapier"""
    results = {}
    errors = []

    try:
        # Use Zapier for all platforms
        result = await upload_to_platform("zapier", path, request)
        results["zapier"] = result

        # Ingest analytics for successful uploads
        if result.status == "success":
            await ingest_analytics("zapier", result.__dict__, publish_id)

        if result.status == "error":
            errors.append(result.error_message)

        # Here you would typically save results to a database
        if errors:
            pass

    except Exception as e:
        pass
    finally:
        # Clean up temp file
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            pass

@router.get("/publish-status/{publish_id}")
async def get_publish_status(publish_id: str):
    """Get the status of a publish request"""
    # In a real implementation, this would query a database
    # For now, return a placeholder response
    return {
        "publish_id": publish_id,
        "status": "unknown",
        "message": "Status tracking not implemented in this demo"
    }

@router.get("/scheduler-status")
async def get_scheduler_status_endpoint():
    """Get scheduler status"""
    return get_scheduler_status()

@router.get("/generate/status/{job_id}")
async def get_video_generation_status(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == 'completed':
        result = json.loads(job.result) if job.result else {}
        video_path = result.get('video_path', '')
        return {"status": "completed", "video_path": video_path}
    elif job.status == 'failed':
        return {"status": "failed", "error": job.result}
    else:
        return {"status": "processing", "progress": job.progress}

@router.get("/uploads/videos/{filename}")
async def get_generated_video(filename: str):
    """Serve generated video files"""
    video_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video_path, media_type='video/mp4')

@router.post("/trim")
async def trim_video(request: dict):
    """Trim video based on start and end times"""
    try:
        video_path = request.get("video_path", "").replace("http://localhost:8000", "")
        start_time = request.get("start_time", 0)
        end_time = request.get("end_time", 0)
        video_id = request.get("video_id", "")

        # Extract filename from path
        filename = os.path.basename(video_path)
        input_path = os.path.join(UPLOAD_DIR, filename)

        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="Original video not found")

        # Generate output filename
        trimmed_filename = f"trimmed_{video_id}_{int(start_time)}_{int(end_time)}_{filename}"
        output_path = os.path.join(UPLOAD_DIR, trimmed_filename)

        # Use FFmpeg to trim the video
        import subprocess
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-ss', str(start_time),
            '-t', str(end_time - start_time),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-preset', 'fast',
            '-crf', '23',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"FFmpeg error: {result.stderr}")

        return {
            "success": True,
            "trimmed_video_path": f"/videos/{trimmed_filename}",
            "message": "Video trimmed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trim failed: {str(e)}")