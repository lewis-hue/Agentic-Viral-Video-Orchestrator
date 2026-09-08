from app.celery_app import celery_app
import google.generativeai as genai
import os
import json
import tempfile
import requests
import cloudinary
import cloudinary.uploader
import datetime
from database.db import SessionLocal
from database.models import Job
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from urllib.parse import urlparse, parse_qs
import sys
import asyncio

# Add the backend directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import uploader module using importlib
import importlib.util
import os
spec = importlib.util.spec_from_file_location("uploader", os.path.abspath("video-uploader-service/uploader.py"))
uploader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uploader)
upload_to_platform = uploader.upload_to_platform

load_dotenv()  # loads .env from current working directory (backend/)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# API keys
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
X_API_KEY = os.environ.get("X_API_KEY")
INSTAGRAM_API_KEY = os.environ.get("INSTAGRAM_API_KEY")
TIKTOK_API_KEY = os.environ.get("TIKTOK_API_KEY")

def detect_platform(url):
    """Detect the platform from the URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if 'youtube.com' in domain or 'youtu.be' in domain:
        return 'youtube'
    elif 'x.com' in domain or 'twitter.com' in domain:
        return 'x'
    elif 'instagram.com' in domain:
        return 'instagram'
    elif 'tiktok.com' in domain:
        return 'tiktok'
    else:
        return 'unknown'

def extract_youtube_video_id(url):
    """Extract video ID from YouTube URL."""
    parsed = urlparse(url)
    if 'youtube.com' in parsed.netloc:
        if '/shorts/' in parsed.path:
            return parsed.path.split('/shorts/')[1].split('?')[0]
        elif 'watch' in parsed.path:
            return parse_qs(parsed.query).get('v', [None])[0]
    elif 'youtu.be' in parsed.netloc:
        return parsed.path.lstrip('/')
    return None

def fetch_youtube_video_data(video_id):
    """Fetch video data from YouTube API."""
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key not set. Please set YOUTUBE_API_KEY in .env")
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    try:
        response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()
        if response['items']:
            return response['items'][0]
        else:
            return None
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

def fetch_trending_youtube_shorts():
    """Fetch trending YouTube Shorts."""
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key not set. Please set YOUTUBE_API_KEY in .env")
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    try:
        response = youtube.search().list(
            part='snippet',
            q='shorts',
            type='video',
            order='relevance',
            maxResults=10
        ).execute()
        return response['items']
    except HttpError as e:
        print(f"An error occurred: {e}")
        return []

# Similar functions for other platforms can be added here

# @celery_app.task
# def discover_trends_task(links, voice_input, files, job_id):
#     import asyncio
#     from agents.trend_discovery.trend_discovery_agent import TrendDiscoveryAgent
#
#     # Update progress
#     db = SessionLocal()
#     job = db.query(Job).filter(Job.id == job_id).first()
#     job.progress = 10
#     db.commit()
#     db.close()
#
#     agent = TrendDiscoveryAgent(gemini_api_key=os.environ["GEMINI_API_KEY"])
#
#     # Analyze inputs
#     job.progress = 30
#     db.commit()
#     db.close()
#
#     trends = asyncio.run(agent.discover_trends(links, voice_input, files))
#
#     # Ensure we have exactly 5 trends
#     job.progress = 70
#     db.commit()
#     db.close()
#
#     while len(trends) < 5:
#         trends.append({
#             "theme": "General Trend",
#             "description": "Emerging trend based on analysis.",
#             "key_elements": ["general"],
#             "virality_score": 50,
#             "reasoning": "Fallback trend.",
#             "additional_instructions": "Start with a hook, keep it engaging."
#         })
#
#     # Save to DB
#     db = SessionLocal()
#     job = db.query(Job).filter(Job.id == job_id).first()
#     job.result = json.dumps(trends)
#     job.status = 'completed'
#     job.progress = 100
#     db.commit()
#     db.close()
#     return trends

# @celery_app.task
# def generate_script_task(topic, instructions, voice_input, files, job_id):
#     import asyncio
#     from agents.story_ideation.story_ideation_agent import StoryIdeationAgent
#
#     # Update progress
#     db = SessionLocal()
#     job = db.query(Job).filter(Job.id == job_id).first()
#     job.progress = 10
#     db.commit()
#     db.close()
#
#     agent = StoryIdeationAgent(gemini_api_key=os.environ["GEMINI_API_KEY"])
#     script = asyncio.run(agent.generate_script(topic, instructions, voice_input, files))
#
#     # Save to DB
#     db = SessionLocal()
#     job = db.query(Job).filter(Job.id == job_id).first()
#     job.result = json.dumps(script)
#     job.status = 'completed'
#     job.progress = 100
#     db.commit()
#     db.close()
#     return script

# @celery_app.task
# def optimize_feedback_task(script, viral_video_link, job_id):
#     from app.services.knowledge_base_service import KnowledgeBaseService
#
#     # Update progress
#     db = SessionLocal()
#     job = db.query(Job).filter(Job.id == job_id).first()
#     job.progress = 20
#     db.commit()
#     db.close()
#
#     kb_service = KnowledgeBaseService()
#     tips = kb_service.get_all_tips()
#
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     prompt = f"""
# Act as an expert viral video consultant.
# Analyze the provided script against a knowledge base of viral patterns.
#
# Script: {script}
# Viral Video Link: {viral_video_link}
# Knowledge Base Tips: {json.dumps([tip.dict() for tip in tips])}
#
# Provide detailed feedback in the following JSON format:
# {{
#   "overall_score": "Score out of 100.",
#   "strengths": ["List of strengths."],
#   "areas_for_improvement": ["List of improvements."],
#   "actionable_recommendations": ["List of recommendations."],
#   "viral_patterns_matched": ["List of matched patterns."],
#   "refined_prompt": "Suggested prompt for regeneration.",
#   "analytics": {{
#     "hook_effectiveness": "Score 1-10",
#     "storytelling_quality": "Score 1-10",
#     "visual_appeal": "Score 1-10",
#     "cta_strength": "Score 1-10",
#     "length_optimization": "Score 1-10"
#   }},
#   "comparison": "Comparison with viral video if link provided."
# }}
# """
#     response = model.generate_content(prompt)
#     feedback = json.loads(response.text)
#
#     job.progress = 70
#     db.commit()
#     db.close()
#
#     db = SessionLocal()
#     job = db.query(Job).filter(Job.id == job_id).first()
#     job.result = json.dumps(feedback)
#     job.status = 'completed'
#     job.progress = 100
#     db.commit()
#     db.close()
#     return feedback

@celery_app.task
def generate_video_task(script, json_plan, job_id, prompt=None, publish_request=None):
    import asyncio
    import logging
    from agents.video_generation.dynamic_shot_orchestrator import DynamicShotOrchestrator

    logger = logging.getLogger(__name__)

    try:
        # Update progress
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.progress = 10
        db.commit()
        db.close()

        orchestrator = DynamicShotOrchestrator()

        # Parse script and json_plan
        script_data = {"script": script} if script else {}
        try:
            json_plan_data = json.loads(json_plan) if json_plan else {}
        except json.JSONDecodeError:
            json_plan_data = {}

        # Combine script and json_plan
        if json_plan_data:
            script_data.update(json_plan_data)

        # Update progress to 30%
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.progress = 30
        db.commit()
        db.close()

        logger.info(f"Starting video orchestration for job {job_id} using Vertex AI Veo with prompt: {prompt}")
        video_package = asyncio.run(orchestrator.orchestrate_video_creation(script_data, prompt=prompt))

        # Update progress to 70%
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.progress = 70
        db.commit()
        db.close()

        # Save video path or result
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.result = json.dumps(video_package)
        job.status = 'completed'
        job.progress = 100
        db.commit()
        db.close()
        logger.info(f"Vertex AI video generation completed for job {job_id}")

        # If publish_request is provided, queue the publisher task
        if publish_request:
            video_path = video_package.get('video_path')
            if video_path:
                publish_job_id = str(uuid.uuid4())
                platforms = publish_request.get('platforms', [])
                caption = publish_request.get('title', '') or publish_request.get('description', '')
                json_plan = publish_request
                publisher_task.delay([video_path], platforms, caption, json_plan, publish_job_id)
                logger.info(f"Queued publisher task for job {publish_job_id} after video generation")

        return video_package

    except Exception as e:
        logger.error(f"Error in generate_video_task for job {job_id}: {str(e)}")
        logger.error("Vertex AI video generation failed - this is a critical error requiring immediate attention")
        # Update job status to failed
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = 'failed'
            job.result = json.dumps({"error": f"Vertex AI video generation failed: {str(e)}"})
            db.commit()
        db.close()
        raise  # Re-raise to mark task as failed in Celery

@celery_app.task
def publisher_task(videos, platforms, caption, jsonPlan, job_id):
    import logging
    import asyncio
    logger = logging.getLogger(__name__)

    # Configure Cloudinary
    cloudinary_url = os.environ['CLOUDINARY_URL']
    from urllib.parse import urlparse
    parsed = urlparse(cloudinary_url)
    cloudinary.config(
        cloud_name=parsed.hostname,
        api_key=parsed.username,
        api_secret=parsed.password
    )

    async def async_publisher():
        results = {}
        logger.info(f"Starting publisher task for job {job_id} with {len(videos)} videos and platforms: {platforms}")

        # Update progress
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.progress = 10
        db.commit()
        db.close()

        for i, video_path in enumerate(videos):
            logger.info(f"Processing video: {video_path}")
            if not video_path or not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                results[video_path] = {"error": "Video file not found"}
                continue

            # Upload to Cloudinary
            try:
                logger.info(f"Uploading {video_path} to Cloudinary")
                upload_result = cloudinary.uploader.upload(video_path, resource_type="video")
                secure_url = upload_result['secure_url']
                logger.info(f"Uploaded to Cloudinary: {secure_url}")
            except Exception as e:
                logger.error(f"Failed to upload {video_path} to Cloudinary: {str(e)}")
                results[video_path] = {"error": str(e)}
                continue

            # Send to Zapier for all platforms
            try:
                logger.info(f"Sending {video_path} to Zapier")
                from app.services.zapier_service import schedule_post_via_zapier
                zapier_payload = {
                    "video": {
                        "url": secure_url,
                        "description": caption,
                        "platforms": {
                            p: {"enabled": True, "schedule": {"datetime": datetime.datetime.utcnow().isoformat()}} for p in platforms
                        }
                    }
                }
                zapier_result = schedule_post_via_zapier(zapier_payload)
                if zapier_result.get("status") == "success":
                    logger.info(f"Successfully sent {video_path} to Zapier")
                    results[video_path] = {"status": "sent to Zapier", "cloudinary_url": secure_url, "response": zapier_result.get("response")}
                else:
                    logger.error(f"Zapier responded with error for {video_path}: {zapier_result.get('response')}")
                    results[video_path] = {"status": "error", "error": zapier_result.get("response")}
            except Exception as e:
                logger.error(f"Failed to send {video_path} to Zapier: {str(e)}")
                results[video_path] = {"status": "error", "error": str(e)}

            # Update progress
            progress = 20 + (i + 1) * (70 / len(videos))
            db = SessionLocal()
            job = db.query(Job).filter(Job.id == job_id).first()
            job.progress = int(progress)
            db.commit()
            db.close()

        # Check if all uploads succeeded
        has_errors = any(result.get("status") == "error" for result in results.values())

        # Save results to DB
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.result = json.dumps(results)
        job.status = 'failed' if has_errors else 'completed'
        job.progress = 100
        db.commit()
        db.close()
        logger.info(f"Publisher task {'failed' if has_errors else 'completed'} for job {job_id}")
        return results

    return asyncio.run(async_publisher())