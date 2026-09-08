from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class PublishRequest(BaseModel):
    platforms: List[str] = Field(..., description="List of platforms to publish to", examples=[["instagram", "tiktok", "youtube"]])
    title: str = Field("", description="Video title")
    description: str = Field("", description="Video description")
    publish_at: Optional[str] = Field(None, description="ISO datetime for scheduled publishing")
    captions: Dict[str, str] = Field(default_factory=dict, description="Platform-specific captions/hashtags")
    voice_to_text: Optional[bool] = Field(False, description="Enable voice-to-text for text inputs")
    tags: List[str] = Field(default_factory=list, description="Video tags/hashtags")

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