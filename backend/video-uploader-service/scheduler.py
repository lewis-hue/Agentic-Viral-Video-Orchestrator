"""
APScheduler Integration for Scheduled Video Publishing

This module provides scheduling functionality for publishing videos at specific times
using APScheduler with async support.

Features:
- Schedule video publishing for future dates
- Background job execution
- Job persistence and recovery
- Integration with main FastAPI app
- Proper error handling and logging
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import JobEvent, JobSubmissionEvent, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# Import from our modules
from uploader import upload_to_platform, PlatformResult
from models import PublishRequest

# Configure logging
logger = logging.getLogger(__name__)

# Job data structure
@dataclass
class ScheduledJob:
    job_id: str
    video_path: str
    request_data: Dict[str, Any]
    scheduled_time: datetime
    created_at: datetime
    status: str  # "pending", "running", "completed", "failed"
    platform_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# Global scheduler instance
scheduler = None
scheduled_jobs_store: Dict[str, ScheduledJob] = {}

def init_scheduler(use_async: bool = True, database_url: Optional[str] = None) -> None:
    """
    Initialize the APScheduler with appropriate configuration

    Args:
        use_async: Whether to use AsyncIOScheduler for async job execution
        database_url: Optional database URL for job persistence
    """
    global scheduler

    # Configure job stores
    jobstores = {
        'default': MemoryJobStore()
    }

    if database_url:
        try:
            jobstores['persistent'] = SQLAlchemyJobStore(url=database_url)
            logger.info(f"Using persistent job store with database: {database_url}")
        except Exception as e:
            logger.warning(f"Failed to initialize persistent job store: {e}")

    # Configure executors
    executors = {
        'default': AsyncIOExecutor()
    }

    # Job defaults
    job_defaults = {
        'coalesce': True,
        'max_instances': 3,
        'misfire_grace_time': 30
    }

    if use_async:
        scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
    else:
        scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )

    # Add event listeners
    scheduler.add_listener(job_event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()
    logger.info(f"Scheduler initialized and started (async={use_async})")

def job_event_listener(event: JobEvent) -> None:
    """Listen to job events and update job status"""
    if isinstance(event, JobEvent):
        job_id = event.job_id
        if job_id in scheduled_jobs_store:
            job = scheduled_jobs_store[job_id]

            if event.exception:
                job.status = "failed"
                job.error_message = str(event.exception)
                logger.error(f"Job {job_id} failed: {event.exception}")
            else:
                job.status = "completed"
                logger.info(f"Job {job_id} completed successfully")

def schedule_publish(
    video_path: str,
    request: PublishRequest,
    publish_id: str,
    run_at: Optional[datetime] = None
) -> str:
    """
    Schedule a video for publishing at a specific time

    Args:
        video_path: Path to the video file
        request: PublishRequest containing platform and metadata info
        publish_id: Unique identifier for this publish request
        run_at: When to run the job (defaults to request.publish_at)

    Returns:
        job_id: The APScheduler job ID
    """
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized")

    # Use provided run_at time or parse from request
    if run_at is None and request.publish_at:
        try:
            run_at = datetime.fromisoformat(request.publish_at.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"Invalid publish_at format: {e}")

    if run_at is None:
        raise ValueError("No scheduling time provided")

    # Create job data
    job_data = ScheduledJob(
        job_id=publish_id,
        video_path=video_path,
        request_data=request.dict(),
        scheduled_time=run_at,
        created_at=datetime.utcnow(),
        status="pending"
    )

    # Store job data
    scheduled_jobs_store[publish_id] = job_data

    # Schedule the job
    if isinstance(scheduler, AsyncIOScheduler):
        job = scheduler.add_job(
            func=execute_scheduled_publish,
            trigger='date',
            run_date=run_at,
            args=[publish_id],
            id=publish_id,
            replace_existing=True
        )
    else:
        # For BackgroundScheduler, we need to run the async function in a new event loop
        job = scheduler.add_job(
            func=run_async_job,
            trigger='date',
            run_date=run_at,
            args=[execute_scheduled_publish, publish_id],
            id=publish_id,
            replace_existing=True
        )

    logger.info(f"Scheduled publish job {publish_id} for {run_at}")
    return publish_id

async def execute_scheduled_publish(job_id: str) -> None:
    """
    Execute the scheduled video publishing

    This is the main async function that handles the actual publishing
    """
    if job_id not in scheduled_jobs_store:
        logger.error(f"Job {job_id} not found in store")
        return

    job = scheduled_jobs_store[job_id]
    job.status = "running"

    logger.info(f"Executing scheduled publish for job {job_id}")

    try:
        # Reconstruct the PublishRequest
        request = PublishRequest(**job.request_data)

        # Publish to each platform
        results = {}
        for platform in request.platforms:
            try:
                logger.info(f"Publishing to {platform} for job {job_id}")

                # Use the upload_to_platform function from uploader.py
                result = await upload_to_platform(platform, job.video_path, request)

                results[platform] = asdict(result)

                if result.status == "success":
                    logger.info(f"Successfully published to {platform}: {result.media_id}")
                else:
                    logger.error(f"Failed to publish to {platform}: {result.error_message}")

            except Exception as e:
                logger.error(f"Exception publishing to {platform}: {e}")
                results[platform] = {
                    "platform": platform,
                    "status": "error",
                    "error_message": str(e)
                }

        # Update job with results
        job.platform_results = results
        job.status = "completed"

        # Calculate success rate
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        total_count = len(results)

        logger.info(f"Scheduled publish completed for job {job_id}: {success_count}/{total_count} successful")

        # Here you would typically:
        # 1. Save results to database
        # 2. Send notifications
        # 3. Trigger analytics ingestion
        # 4. Clean up temporary files

        # Clean up video file after processing
        await cleanup_video_file(job.video_path)

    except Exception as e:
        logger.error(f"Critical error in scheduled publish {job_id}: {e}")
        job.status = "failed"
        job.error_message = str(e)

def run_async_job(async_func: Callable, *args) -> None:
    """
    Helper function to run async functions in BackgroundScheduler
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_func(*args))
        loop.close()
    except Exception as e:
        logger.error(f"Error running async job: {e}")

async def cleanup_video_file(video_path: str) -> None:
    """Clean up temporary video file after processing"""
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
            logger.info(f"Cleaned up video file: {video_path}")
        else:
            logger.warning(f"Video file not found for cleanup: {video_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup video file {video_path}: {e}")

def get_scheduled_jobs() -> List[Dict[str, Any]]:
    """Get list of all scheduled jobs"""
    jobs = []
    for job_id, job_data in scheduled_jobs_store.items():
        jobs.append(asdict(job_data))
    return jobs

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a specific job"""
    if job_id in scheduled_jobs_store:
        return asdict(scheduled_jobs_store[job_id])
    return None

def cancel_scheduled_job(job_id: str) -> bool:
    """
    Cancel a scheduled job

    Returns:
        True if job was cancelled, False if not found
    """
    if scheduler is None:
        return False

    try:
        scheduler.remove_job(job_id)

        if job_id in scheduled_jobs_store:
            scheduled_jobs_store[job_id].status = "cancelled"

        logger.info(f"Cancelled scheduled job {job_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        return False

def reschedule_job(job_id: str, new_time: datetime) -> bool:
    """
    Reschedule an existing job to a new time

    Returns:
        True if job was rescheduled, False if not found or failed
    """
    if scheduler is None or job_id not in scheduled_jobs_store:
        return False

    try:
        # Remove existing job
        scheduler.remove_job(job_id)

        # Update job data
        job = scheduled_jobs_store[job_id]
        job.scheduled_time = new_time

        # Reschedule
        if isinstance(scheduler, AsyncIOScheduler):
            scheduler.add_job(
                func=execute_scheduled_publish,
                trigger='date',
                run_date=new_time,
                args=[job_id],
                id=job_id,
                replace_existing=True
            )
        else:
            scheduler.add_job(
                func=run_async_job,
                trigger='date',
                run_date=new_time,
                args=[execute_scheduled_publish, job_id],
                id=job_id,
                replace_existing=True
            )

        logger.info(f"Rescheduled job {job_id} to {new_time}")
        return True

    except Exception as e:
        logger.error(f"Failed to reschedule job {job_id}: {e}")
        return False

def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status and statistics"""
    if scheduler is None:
        return {"status": "not_initialized"}

    return {
        "status": "running" if scheduler.running else "stopped",
        "jobs_total": len(scheduled_jobs_store),
        "jobs_pending": len([j for j in scheduled_jobs_store.values() if j.status == "pending"]),
        "jobs_running": len([j for j in scheduled_jobs_store.values() if j.status == "running"]),
        "jobs_completed": len([j for j in scheduled_jobs_store.values() if j.status == "completed"]),
        "jobs_failed": len([j for j in scheduled_jobs_store.values() if j.status == "failed"]),
        "next_run_time": str(scheduler.get_jobs()[0].next_run_time) if scheduler.get_jobs() else None
    }

# Initialize scheduler when module is imported
try:
    init_scheduler(use_async=True)
except Exception as e:
    logger.error(f"Failed to initialize scheduler: {e}")