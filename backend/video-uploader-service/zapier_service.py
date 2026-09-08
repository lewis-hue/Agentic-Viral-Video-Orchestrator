"""
Zapier Integration Service for Buffer API

This module handles sending scheduled posts to Buffer via Zapier webhook.
It abstracts the complexity of OAuth and API calls by using Zapier as a gateway.
"""

import requests
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")
YOUTUBE_PROFILE_ID = os.getenv("YOUTUBE_PROFILE_ID")
INSTAGRAM_PROFILE_ID = os.getenv("INSTAGRAM_PROFILE_ID")
TIKTOK_PROFILE_ID = os.getenv("TIKTOK_PROFILE_ID")

# Platform to Profile ID mapping
PLATFORM_PROFILE_MAP = {
    "youtube": YOUTUBE_PROFILE_ID,
    "instagram": INSTAGRAM_PROFILE_ID,
    "tiktok": TIKTOK_PROFILE_ID
}

def validate_credentials() -> bool:
    """Validate that required credentials are available"""
    if not ZAPIER_WEBHOOK_URL:
        logger.error("ZAPIER_WEBHOOK_URL not configured")
        return False
    return True

def get_profile_ids(platforms: List[str]) -> List[str]:
    """Get profile IDs for the given platforms"""
    profile_ids = []
    for platform in platforms:
        platform_lower = platform.lower()
        if "instagram" in platform_lower:
            profile_id = PLATFORM_PROFILE_MAP.get("instagram")
        elif "youtube" in platform_lower:
            profile_id = PLATFORM_PROFILE_MAP.get("youtube")
        elif "tiktok" in platform_lower:
            profile_id = PLATFORM_PROFILE_MAP.get("tiktok")
        else:
            profile_id = None
        if profile_id:
            profile_ids.append(profile_id)
        else:
            logger.warning(f"No profile ID configured for platform: {platform}")
    return profile_ids

def schedule_post_via_zapier(payload: dict) -> dict:
    """
    Schedule a post via Zapier webhook

    Args:
        payload: The JSON payload containing video details, platforms, etc.

    Returns:
        dict: Response from Zapier or error details
    """
    if not validate_credentials():
        logger.warning("Zapier webhook URL not configured, skipping post")
        return {"status": "success", "response": "Skipped due to missing Zapier configuration"}

    # Extract values from payload
    video = payload.get("video", {})
    media_url = video.get("url")
    if not media_url:
        return {"status": "error", "response": "No media URL provided"}

    # Extract text_content (use description or title)
    text_content = video.get("description", video.get("title", ""))

    # Extract platforms
    platforms_dict = video.get("platforms", {})
    platforms = [p for p in platforms_dict if platforms_dict[p].get("enabled", False)]

    # Extract schedule_at
    schedule_at_str = None
    for p in platforms:
        schedule = platforms_dict[p].get("schedule", {}).get("datetime")
        if schedule:
            schedule_at_str = schedule
            break
    if not schedule_at_str:
        schedule_at_str = (datetime.now() + timedelta(hours=1)).isoformat()  # Default to 1 hour from now

    schedule_at = datetime.fromisoformat(schedule_at_str.replace('Z', '+00:00'))

    # Construct the payload for Zapier
    zapier_payload = {
        "text_content": text_content,
        "media_url": media_url,
        "platforms": platforms,
        "schedule_at": schedule_at.isoformat()
    }

    try:
        logger.info(f"Sending data to Zapier: {json.dumps(zapier_payload)}")
        response = requests.post(
            ZAPIER_WEBHOOK_URL,
            data=json.dumps(zapier_payload),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info("Successfully sent data to Zapier")
        return {"status": "success", "response": response.json()}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Zapier webhook: {e}")
        return {"status": "error", "response": str(e)}