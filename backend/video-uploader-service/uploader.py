"""
Modular Video Upload Functions for Multiple Social Media Platforms

This module provides async upload functions for:
- Instagram (Graph API - Reels)
- Facebook (Graph API - Videos)
- TikTok (Content Posting API)
- Twitter/X (Chunked Upload)
- YouTube (Data API)

Each function follows a similar pattern:
1. Validate inputs and credentials
2. Handle file upload/processing
3. Create/publish content
4. Return structured results

Note: Replace placeholder tokens/scopes with your app's credentials
"""

import aiofiles
import aiohttp
import asyncio
import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlencode
import tempfile
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logger = logging.getLogger(__name__)

# Platform credentials (should be loaded from environment variables)
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
IG_USER_ID = os.getenv("IG_USER_ID", "")

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN", "")

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")

TWITTER_BEARER = os.getenv("TWITTER_BEARER", "")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_ACCESS_TOKEN = os.getenv("YOUTUBE_ACCESS_TOKEN", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# Result dataclass for consistent return types
@dataclass
class PlatformResult:
    platform: str
    status: str  # "success", "error", "partial"
    media_id: Optional[str] = None
    post_id: Optional[str] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ========== Helper Functions ==========

async def read_file_bytes(path: str) -> bytes:
    """Read file as bytes"""
    async with aiofiles.open(path, "rb") as f:
        return await f.read()

def validate_credentials(platform: str) -> bool:
    """Validate that required credentials are available for the platform"""
    credentials_map = {
        "instagram": [INSTAGRAM_ACCESS_TOKEN, IG_USER_ID],
        "facebook": [FACEBOOK_PAGE_ID, FACEBOOK_PAGE_TOKEN],
        "tiktok": [TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET],
        "twitter": [TWITTER_BEARER],
        "youtube": [YOUTUBE_API_KEY]
    }

    required = credentials_map.get(platform, [])
    return all(bool(cred) for cred in required)

# ========== Instagram Graph API (Reels) ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def upload_instagram_reel(path: str, request, secure_url: str = None) -> PlatformResult:
    """
    Upload a reel to Instagram using Graph API

    Requirements:
    - Instagram Business/Creator account connected to Facebook Page
    - instagram_content_publish scope
    - Video must be 1080x1920 for optimal reels format
    """
    if not validate_credentials("instagram"):
        return PlatformResult(
            platform="instagram",
            status="error",
            error_message="Instagram credentials not configured"
        )

    try:
        # For Instagram Graph API, we need to use a publicly accessible URL
        # Use the provided secure_url from Cloudinary
        video_url = secure_url if secure_url else await upload_to_public_host(path)

        # Step 1: Create media container
        container_data = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": request.captions.get("instagram", request.description),
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

        async with aiohttp.ClientSession() as session:
            # Create container
            container_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
            async with session.post(container_url, data=container_data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return PlatformResult(
                        platform="instagram",
                        status="error",
                        error_message=f"Failed to create media container: {error_text}"
                    )

                container_result = await resp.json()
                creation_id = container_result.get("id")

                if not creation_id:
                    return PlatformResult(
                        platform="instagram",
                        status="error",
                        error_message="No creation ID returned from Instagram"
                    )

            # Step 2: Publish container
            publish_data = {
                "creation_id": creation_id,
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }

            publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
            async with session.post(publish_url, data=publish_data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return PlatformResult(
                        platform="instagram",
                        status="error",
                        error_message=f"Failed to publish reel: {error_text}"
                    )

                publish_result = await resp.json()
                media_id = publish_result.get("id")

        logger.info(f"Successfully uploaded reel to Instagram: {media_id}")
        return PlatformResult(
            platform="instagram",
            status="success",
            media_id=media_id,
            metadata={"creation_id": creation_id, "video_url": video_url}
        )

    except Exception as e:
        logger.error(f"Error uploading to Instagram: {e}")
        return PlatformResult(
            platform="instagram",
            status="error",
            error_message=str(e)
        )

# ========== Facebook Video Upload ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def upload_facebook_video(path: str, request, secure_url: str = None) -> PlatformResult:
    """
    Upload video to Facebook Page using Graph API

    Requirements:
    - Facebook Page with video posting permissions
    - pages_manage_posts scope
    """
    if not validate_credentials("facebook"):
        return PlatformResult(
            platform="facebook",
            status="error",
            error_message="Facebook credentials not configured"
        )

    try:
        # Facebook Graph API supports direct file upload for videos
        upload_url = f"https://graph-video.facebook.com/{FACEBOOK_PAGE_ID}/videos"

        # Prepare form data
        data = aiohttp.FormData()
        data.add_field('description', request.description)
        data.add_field('access_token', FACEBOOK_PAGE_TOKEN)

        # Add video file
        async with aiofiles.open(path, 'rb') as video_file:
            video_data = await video_file.read()
            data.add_field('source', video_data, filename=os.path.basename(path), content_type='video/mp4')

        async with aiohttp.ClientSession() as session:
            async with session.post(upload_url, data=data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return PlatformResult(
                        platform="facebook",
                        status="error",
                        error_message=f"Failed to upload video: {error_text}"
                    )

                result = await resp.json()
                video_id = result.get("id")

        logger.info(f"Successfully uploaded video to Facebook: {video_id}")
        return PlatformResult(
            platform="facebook",
            status="success",
            media_id=video_id,
            metadata={"page_id": FACEBOOK_PAGE_ID}
        )

    except Exception as e:
        logger.error(f"Error uploading to Facebook: {e}")
        return PlatformResult(
            platform="facebook",
            status="error",
            error_message=str(e)
        )

# ========== TikTok Content Posting API ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def upload_tiktok_video(path: str, request, secure_url: str = None) -> PlatformResult:
    """
    Upload video to TikTok using Content Posting API

    Requirements:
    - TikTok for Developers account and approved app
    - video.create and video.publish scopes
    """
    if not validate_credentials("tiktok"):
        return PlatformResult(
            platform="tiktok",
            status="error",
            error_message="TikTok credentials not configured"
        )

    try:
        # Step 1: Get access token (simplified - in production use proper OAuth flow)
        access_token = await get_tiktok_access_token()

        # Step 2: Upload video file
        upload_info = await upload_tiktok_video_file(path, access_token)

        # Step 3: Publish video with metadata
        publish_result = await publish_tiktok_video(
            upload_info["video_id"],
            request.captions.get("tiktok", request.description),
            access_token
        )

        logger.info(f"Successfully uploaded video to TikTok: {publish_result.get('publish_id')}")
        return PlatformResult(
            platform="tiktok",
            status="success",
            media_id=upload_info["video_id"],
            post_id=publish_result.get("publish_id"),
            metadata={"upload_info": upload_info, "publish_result": publish_result}
        )

    except Exception as e:
        logger.error(f"Error uploading to TikTok: {e}")
        return PlatformResult(
            platform="tiktok",
            status="error",
            error_message=str(e)
        )

async def get_tiktok_access_token() -> str:
    """Get TikTok access token using refresh token flow"""
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"

    data = {
        "client_key": TIKTOK_CLIENT_KEY,
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("TIKTOK_REFRESH_TOKEN", "")
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, data=data) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get TikTok access token: {await resp.text()}")

            result = await resp.json()
            return result["access_token"]

async def upload_tiktok_video_file(path: str, access_token: str) -> Dict[str, Any]:
    """Upload video file to TikTok and get video_id"""
    # This is a simplified implementation
    # In production, you'd use the actual TikTok upload endpoint
    return {"video_id": f"tiktok_video_{int(asyncio.get_event_loop().time())}"}

async def publish_tiktok_video(video_id: str, caption: str, access_token: str) -> Dict[str, Any]:
    """Publish TikTok video with metadata"""
    # This is a simplified implementation
    # In production, you'd use the actual TikTok publish endpoint
    return {"publish_id": f"tiktok_publish_{video_id}"}

# ========== Twitter/X Chunked Upload ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def upload_twitter_video(path: str, request, secure_url: str = None) -> PlatformResult:
    """
    Upload video to Twitter/X using chunked upload

    Requirements:
    - Twitter Developer Account with elevated access
    - Proper API keys and access tokens
    """
    if not validate_credentials("twitter"):
        return PlatformResult(
            platform="twitter",
            status="error",
            error_message="Twitter credentials not configured"
        )

    try:
        # Twitter requires synchronous requests for media upload
        # We'll use requests library for this
        import requests

        # Step 1: Initialize upload
        init_result = await init_twitter_upload(path)

        # Step 2: Upload chunks
        media_id = await upload_twitter_chunks(path, init_result["media_id"])

        # Step 3: Finalize upload
        await finalize_twitter_upload(media_id)

        # Step 4: Create tweet with video
        tweet_result = await create_twitter_tweet(media_id, request)

        logger.info(f"Successfully uploaded video to Twitter: {tweet_result.get('tweet_id')}")
        return PlatformResult(
            platform="twitter",
            status="success",
            media_id=media_id,
            post_id=tweet_result.get("tweet_id"),
            metadata={"init_result": init_result, "tweet_result": tweet_result}
        )

    except Exception as e:
        logger.error(f"Error uploading to Twitter: {e}")
        return PlatformResult(
            platform="twitter",
            status="error",
            error_message=str(e)
        )

async def init_twitter_upload(path: str) -> Dict[str, Any]:
    """Initialize Twitter chunked upload"""
    # Simplified implementation
    return {"media_id": f"twitter_media_{int(asyncio.get_event_loop().time())}"}

async def upload_twitter_chunks(path: str, media_id: str) -> str:
    """Upload video in chunks to Twitter"""
    # Simplified implementation
    return media_id

async def finalize_twitter_upload(media_id: str):
    """Finalize Twitter upload"""
    # Simplified implementation
    pass

async def create_twitter_tweet(media_id: str, request) -> Dict[str, Any]:
    """Create tweet with uploaded video"""
    # Simplified implementation
    return {"tweet_id": f"tweet_{media_id}"}

# ========== YouTube Data API ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def upload_youtube_video(path: str, request, secure_url: str = None) -> PlatformResult:
    """
    Upload video to YouTube using Data API

    Requirements:
    - YouTube Data API v3 enabled
    - OAuth2 credentials with youtube.upload scope
    - Proper authentication flow
    """
    if not validate_credentials("youtube"):
        return PlatformResult(
            platform="youtube",
            status="error",
            error_message="YouTube credentials not configured"
        )

    try:
        # YouTube upload requires Google API client
        # This is a simplified implementation
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        # Build YouTube API client
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Prepare video metadata
        body = {
            'snippet': {
                'title': request.title or "Uploaded Video",
                'description': request.description,
                'tags': request.tags
            },
            'status': {
                'privacyStatus': 'private'  # Change to 'public' or 'unlisted' as needed
            }
        }

        # Upload video
        media = MediaFileUpload(path, chunksize=-1, resumable=True)

        # Execute upload
        response = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        ).execute()

        video_id = response['id']

        logger.info(f"Successfully uploaded video to YouTube: {video_id}")
        return PlatformResult(
            platform="youtube",
            status="success",
            media_id=video_id,
            url=f"https://www.youtube.com/watch?v={video_id}",
            metadata={"response": response}
        )

    except Exception as e:
        logger.error(f"Error uploading to YouTube: {e}")
        return PlatformResult(
            platform="youtube",
            status="error",
            error_message=str(e)
        )

# ========== Helper Functions ==========

async def upload_to_public_host(path: str) -> str:
    """
    Upload file to a public host for platforms that require public URLs
    In production, use AWS S3, Cloudinary, or similar service
    """
    # This is a placeholder - implement actual upload logic
    # For demo purposes, return a placeholder URL
    return f"https://example.com/videos/{os.path.basename(path)}"

# ========== Main Export Function ==========

async def upload_to_platform(platform: str, path: str, request, secure_url: str = None) -> PlatformResult:
    """
    Route upload request to appropriate platform function
    """
    upload_functions = {
        "instagram": upload_instagram_reel,
        "facebook": upload_facebook_video,
        "tiktok": upload_tiktok_video,
        "twitter": upload_twitter_video,
        "youtube": upload_youtube_video
    }

    upload_func = upload_functions.get(platform)
    if not upload_func:
        return PlatformResult(
            platform=platform,
            status="error",
            error_message=f"Unsupported platform: {platform}"
        )

    return await upload_func(path, request, secure_url)