"""
Analytics and Engagement Metrics Collection

This module provides functionality for:
- Fetching engagement metrics from all supported platforms
- Analytics ingestion and storage
- Performance tracking and feedback loops
- Integration with external analytics services

Features:
- Platform-specific metrics collection
- Async analytics ingestion
- Metrics aggregation and reporting
- Performance optimization recommendations
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Import platform credentials
from uploader import (
    INSTAGRAM_ACCESS_TOKEN, FACEBOOK_PAGE_TOKEN, TIKTOK_ACCESS_TOKEN,
    TWITTER_BEARER, YOUTUBE_API_KEY
)

# Configure logging
logger = logging.getLogger(__name__)

# Analytics data structures
@dataclass
class PlatformMetrics:
    platform: str
    media_id: str
    post_id: Optional[str]
    collected_at: datetime

    # Common metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0

    # Platform-specific metrics
    platform_specific: Dict[str, Any] = None

    # Calculated metrics
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0

@dataclass
class AnalyticsReport:
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_posts: int
    platform_metrics: Dict[str, List[PlatformMetrics]]
    aggregated_metrics: Dict[str, Any]
    recommendations: List[str]

# ========== Instagram Analytics ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_instagram_metrics(media_id: str) -> PlatformMetrics:
    """
    Fetch engagement metrics for Instagram media

    Uses Instagram Graph API to get media insights
    """
    try:
        # Instagram media insights endpoint
        insights_url = f"https://graph.facebook.com/v18.0/{media_id}/insights"

        params = {
            "metric": "impressions,reach,likes,comments,shares,saved",
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(insights_url, params=params) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch Instagram metrics: {resp.status}")
                    return PlatformMetrics(
                        platform="instagram",
                        media_id=media_id,
                        post_id=media_id,
                        collected_at=datetime.utcnow()
                    )

                data = await resp.json()

        # Parse Instagram insights
        metrics = PlatformMetrics(
            platform="instagram",
            media_id=media_id,
            post_id=media_id,
            collected_at=datetime.utcnow()
        )

        if data.get("data"):
            for insight in data["data"]:
                name = insight.get("name")
                values = insight.get("values", [])

                if values and len(values) > 0:
                    value = values[0].get("value", 0)

                    if name == "impressions":
                        metrics.impressions = value
                    elif name == "reach":
                        metrics.reach = value
                    elif name == "likes":
                        metrics.likes = value
                    elif name == "comments":
                        metrics.comments = value
                    elif name == "shares":
                        metrics.shares = value
                    elif name == "saved":
                        metrics.saves = value

        # Calculate engagement rate
        if metrics.reach > 0:
            total_engagements = metrics.likes + metrics.comments + metrics.shares + metrics.saves
            metrics.engagement_rate = (total_engagements / metrics.reach) * 100

        logger.info(f"Fetched Instagram metrics for {media_id}: {metrics.likes} likes, {metrics.views} views")
        return metrics

    except Exception as e:
        logger.error(f"Error fetching Instagram metrics: {e}")
        return PlatformMetrics(
            platform="instagram",
            media_id=media_id,
            post_id=media_id,
            collected_at=datetime.utcnow(),
            platform_specific={"error": str(e)}
        )

# ========== Facebook Analytics ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_facebook_metrics(post_id: str) -> PlatformMetrics:
    """
    Fetch engagement metrics for Facebook post

    Uses Facebook Graph API to get post insights
    """
    try:
        # Facebook post insights endpoint
        insights_url = f"https://graph.facebook.com/v18.0/{post_id}/insights"

        params = {
            "metric": "post_impressions,post_reactions_by_type_total,post_clicks,post_video_views",
            "access_token": FACEBOOK_PAGE_TOKEN
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(insights_url, params=params) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch Facebook metrics: {resp.status}")
                    return PlatformMetrics(
                        platform="facebook",
                        media_id=post_id,
                        post_id=post_id,
                        collected_at=datetime.utcnow()
                    )

                data = await resp.json()

        # Parse Facebook insights
        metrics = PlatformMetrics(
            platform="facebook",
            media_id=post_id,
            post_id=post_id,
            collected_at=datetime.utcnow()
        )

        if data.get("data"):
            for insight in data["data"]:
                name = insight.get("name")
                values = insight.get("values", [])

                if values and len(values) > 0:
                    value = values[0].get("value", 0)

                    if name == "post_impressions":
                        metrics.impressions = value
                    elif name == "post_reactions_by_type_total":
                        metrics.likes = value
                    elif name == "post_clicks":
                        metrics.shares = value  # Using shares as proxy for clicks
                    elif name == "post_video_views":
                        metrics.views = value

        # Get additional post data
        post_url = f"https://graph.facebook.com/v18.0/{post_id}"
        post_params = {
            "fields": "comments.summary(true),shares",
            "access_token": FACEBOOK_PAGE_TOKEN
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(post_url, params=post_params) as resp:
                if resp.status == 200:
                    post_data = await resp.json()
                    metrics.comments = post_data.get("comments", {}).get("summary", {}).get("total_count", 0)
                    metrics.shares = post_data.get("shares", {}).get("count", 0)

        # Calculate engagement rate
        if metrics.impressions > 0:
            total_engagements = metrics.likes + metrics.comments + metrics.shares
            metrics.engagement_rate = (total_engagements / metrics.impressions) * 100

        logger.info(f"Fetched Facebook metrics for {post_id}: {metrics.likes} likes, {metrics.views} views")
        return metrics

    except Exception as e:
        logger.error(f"Error fetching Facebook metrics: {e}")
        return PlatformMetrics(
            platform="facebook",
            media_id=post_id,
            post_id=post_id,
            collected_at=datetime.utcnow(),
            platform_specific={"error": str(e)}
        )

# ========== TikTok Analytics ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_tiktok_metrics(video_id: str) -> PlatformMetrics:
    """
    Fetch engagement metrics for TikTok video

    Uses TikTok Research API or Content Posting API for metrics
    """
    try:
        # TikTok metrics endpoint (simplified - actual endpoint may vary)
        metrics_url = "https://open.tiktokapis.com/v2/research/video/query/"

        headers = {
            "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "query": {
                "and": [
                    {"field_name": "video_id", "operation": "IN", "field_values": [video_id]}
                ]
            },
            "max_count": 10,
            "cursor": 0
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(metrics_url, headers=headers, json=data) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch TikTok metrics: {resp.status}")
                    return PlatformMetrics(
                        platform="tiktok",
                        media_id=video_id,
                        post_id=video_id,
                        collected_at=datetime.utcnow()
                    )

                result = await resp.json()

        # Parse TikTok metrics (simplified structure)
        metrics = PlatformMetrics(
            platform="tiktok",
            media_id=video_id,
            post_id=video_id,
            collected_at=datetime.utcnow()
        )

        # This is a simplified parsing - actual TikTok API response structure may differ
        videos = result.get("data", {}).get("videos", [])
        if videos:
            video_data = videos[0]
            metrics.views = video_data.get("view_count", 0)
            metrics.likes = video_data.get("like_count", 0)
            metrics.comments = video_data.get("comment_count", 0)
            metrics.shares = video_data.get("share_count", 0)

        # Calculate engagement rate
        if metrics.views > 0:
            total_engagements = metrics.likes + metrics.comments + metrics.shares
            metrics.engagement_rate = (total_engagements / metrics.views) * 100

        logger.info(f"Fetched TikTok metrics for {video_id}: {metrics.likes} likes, {metrics.views} views")
        return metrics

    except Exception as e:
        logger.error(f"Error fetching TikTok metrics: {e}")
        return PlatformMetrics(
            platform="tiktok",
            media_id=video_id,
            post_id=video_id,
            collected_at=datetime.utcnow(),
            platform_specific={"error": str(e)}
        )

# ========== Twitter/X Analytics ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_twitter_metrics(tweet_id: str) -> PlatformMetrics:
    """
    Fetch engagement metrics for Twitter/X post

    Uses Twitter API v2 to get tweet metrics
    """
    try:
        # Twitter API v2 tweet lookup endpoint
        tweet_url = f"https://api.twitter.com/2/tweets/{tweet_id}"

        headers = {
            "Authorization": f"Bearer {TWITTER_BEARER}",
            "Content-Type": "application/json"
        }

        params = {
            "tweet.fields": "public_metrics,non_public_metrics,organic_metrics"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(tweet_url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch Twitter metrics: {resp.status}")
                    return PlatformMetrics(
                        platform="twitter",
                        media_id=tweet_id,
                        post_id=tweet_id,
                        collected_at=datetime.utcnow()
                    )

                data = await resp.json()

        # Parse Twitter metrics
        metrics = PlatformMetrics(
            platform="twitter",
            media_id=tweet_id,
            post_id=tweet_id,
            collected_at=datetime.utcnow()
        )

        tweet_data = data.get("data", {})
        public_metrics = tweet_data.get("public_metrics", {})

        metrics.likes = public_metrics.get("like_count", 0)
        metrics.shares = public_metrics.get("retweet_count", 0)
        metrics.comments = public_metrics.get("reply_count", 0)

        # Twitter doesn't provide view count in public metrics
        # but we can estimate based on impressions if available
        if "organic_metrics" in tweet_data:
            metrics.views = tweet_data["organic_metrics"].get("impression_count", 0)

        # Calculate engagement rate (simplified)
        if metrics.views > 0:
            total_engagements = metrics.likes + metrics.comments + metrics.shares
            metrics.engagement_rate = (total_engagements / metrics.views) * 100

        logger.info(f"Fetched Twitter metrics for {tweet_id}: {metrics.likes} likes, {metrics.views} views")
        return metrics

    except Exception as e:
        logger.error(f"Error fetching Twitter metrics: {e}")
        return PlatformMetrics(
            platform="twitter",
            media_id=tweet_id,
            post_id=tweet_id,
            collected_at=datetime.utcnow(),
            platform_specific={"error": str(e)}
        )

# ========== YouTube Analytics ==========

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_youtube_metrics(video_id: str) -> PlatformMetrics:
    """
    Fetch engagement metrics for YouTube video

    Uses YouTube Data API v3 to get video statistics
    """
    try:
        # YouTube API v3 videos endpoint
        video_url = "https://www.googleapis.com/youtube/v3/videos"

        params = {
            "part": "statistics",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(video_url, params=params) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch YouTube metrics: {resp.status}")
                    return PlatformMetrics(
                        platform="youtube",
                        media_id=video_id,
                        post_id=video_id,
                        collected_at=datetime.utcnow()
                    )

                data = await resp.json()

        # Parse YouTube metrics
        metrics = PlatformMetrics(
            platform="youtube",
            media_id=video_id,
            post_id=video_id,
            collected_at=datetime.utcnow()
        )

        items = data.get("items", [])
        if items:
            statistics = items[0].get("statistics", {})

            metrics.views = int(statistics.get("viewCount", 0))
            metrics.likes = int(statistics.get("likeCount", 0))
            metrics.comments = int(statistics.get("commentCount", 0))

        # Calculate engagement rate
        if metrics.views > 0:
            total_engagements = metrics.likes + metrics.comments
            metrics.engagement_rate = (total_engagements / metrics.views) * 100

        logger.info(f"Fetched YouTube metrics for {video_id}: {metrics.likes} likes, {metrics.views} views")
        return metrics

    except Exception as e:
        logger.error(f"Error fetching YouTube metrics: {e}")
        return PlatformMetrics(
            platform="youtube",
            media_id=video_id,
            post_id=video_id,
            collected_at=datetime.utcnow(),
            platform_specific={"error": str(e)}
        )

# ========== Analytics Ingestion and Processing ==========

async def ingest_analytics(platform: str, publish_result: Dict[str, Any], publish_id: str) -> Dict[str, Any]:
    """
    Main function to ingest analytics for a published video

    This function:
    1. Fetches metrics from the platform
    2. Stores metrics in database/cache
    3. Triggers feedback loops
    4. Generates performance insights
    """
    try:
        logger.info(f"Starting analytics ingestion for {platform} publish {publish_id}")

        # Get the appropriate metrics fetcher
        fetch_functions = {
            "instagram": fetch_instagram_metrics,
            "facebook": fetch_facebook_metrics,
            "tiktok": fetch_tiktok_metrics,
            "twitter": fetch_twitter_metrics,
            "youtube": fetch_youtube_metrics
        }

        fetch_func = fetch_functions.get(platform)
        if not fetch_func:
            raise ValueError(f"No metrics fetcher for platform: {platform}")

        # Fetch metrics
        media_id = publish_result.get("media_id") or publish_result.get("id")
        if not media_id:
            logger.warning(f"No media ID found in publish result for {platform}")
            return {"error": "No media ID found"}

        metrics = await fetch_func(media_id)

        # Store metrics (in production, this would be a database)
        await store_analytics_metrics(metrics, publish_id)

        # Generate insights and recommendations
        insights = await generate_performance_insights(metrics)

        # Trigger feedback loops
        await trigger_feedback_loops(platform, metrics, publish_id)

        logger.info(f"Analytics ingestion completed for {platform} - {metrics.likes} likes, {metrics.views} views")

        return {
            "status": "success",
            "metrics": asdict(metrics),
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error in analytics ingestion for {platform}: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

async def store_analytics_metrics(metrics: PlatformMetrics, publish_id: str) -> None:
    """
    Store analytics metrics in database/cache

    In production, this would integrate with:
    - PostgreSQL/MySQL for persistent storage
    - Redis for caching
    - Elasticsearch for search and analytics
    """
    # For demo purposes, we'll just log the metrics
    logger.info(f"Storing metrics for {publish_id}: {asdict(metrics)}")

    # In production implementation:
    # - Insert into analytics table
    # - Update cache with latest metrics
    # - Trigger real-time dashboards

async def generate_performance_insights(metrics: PlatformMetrics) -> List[str]:
    """
    Generate performance insights and recommendations based on metrics
    """
    insights = []

    # Engagement rate analysis
    if metrics.engagement_rate > 5.0:
        insights.append("High engagement rate - content resonates well with audience")
    elif metrics.engagement_rate < 1.0:
        insights.append("Low engagement rate - consider adjusting content strategy")

    # Platform-specific insights
    if metrics.platform == "instagram":
        if metrics.saves > metrics.likes * 0.1:
            insights.append("High save rate indicates valuable content")
    elif metrics.platform == "youtube":
        if metrics.views > 1000 and metrics.likes / metrics.views > 0.02:
            insights.append("Good like-to-view ratio - content quality is high")

    # General recommendations
    if metrics.views == 0:
        insights.append("No views detected - check if content is publicly visible")
    elif metrics.views > 0 and metrics.likes == 0:
        insights.append("Content is being viewed but not liked - consider call-to-action")

    return insights

async def trigger_feedback_loops(platform: str, metrics: PlatformMetrics, publish_id: str) -> None:
    """
    Trigger feedback loops for performance optimization

    This could include:
    - Updating machine learning models
    - Adjusting content strategy
    - Triggering A/B tests
    - Sending performance reports
    """
    # For demo purposes, we'll just log potential actions
    logger.info(f"Feedback loops for {platform} {publish_id}:")

    if metrics.engagement_rate > 3.0:
        logger.info("  - High engagement: Consider creating similar content")

    if metrics.views > 10000:
        logger.info("  - High views: Content is trending, boost similar posts")

    # In production, this would trigger actual workflows

# ========== Analytics Reporting ==========

async def generate_analytics_report(
    start_date: datetime,
    end_date: datetime,
    platforms: Optional[List[str]] = None
) -> AnalyticsReport:
    """
    Generate comprehensive analytics report for a date range
    """
    report_id = f"report_{int(datetime.utcnow().timestamp())}"

    # In production, this would query a database for historical metrics
    # For demo, we'll return a placeholder report

    return AnalyticsReport(
        report_id=report_id,
        generated_at=datetime.utcnow(),
        period_start=start_date,
        period_end=end_date,
        total_posts=0,
        platform_metrics={},
        aggregated_metrics={
            "total_views": 0,
            "total_likes": 0,
            "average_engagement_rate": 0.0
        },
        recommendations=["Connect platform APIs to see real analytics data"]
    )

# ========== Platform-specific metric fetchers by ID ==========

async def fetch_metrics_by_platform_and_id(platform: str, media_id: str) -> PlatformMetrics:
    """
    Fetch metrics for any platform by media ID
    """
    fetch_functions = {
        "instagram": fetch_instagram_metrics,
        "facebook": fetch_facebook_metrics,
        "tiktok": fetch_tiktok_metrics,
        "twitter": fetch_twitter_metrics,
        "youtube": fetch_youtube_metrics
    }

    fetch_func = fetch_functions.get(platform)
    if not fetch_func:
        raise ValueError(f"Unsupported platform: {platform}")

    return await fetch_func(media_id)