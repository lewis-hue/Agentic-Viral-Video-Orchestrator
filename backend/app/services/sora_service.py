import os
import asyncio
import logging
import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SoraGenerationRequest:
    image: str  # URL
    prompt: str
    length: int
    aspect_ratio: str = "16:9"
    webhook_url: Optional[str] = None

@dataclass
class SoraGenerationResponse:
    task_id: str
    status: str

class SoraService:
    def __init__(self):
        self.api_key = os.getenv("SORA_API_KEY")
        self.base_url = "https://pollo.ai/api/platform/generation/sora/sora-2"
        # If no API key, use mock mode
        self.mock_mode = not self.api_key
        logger.info(f"SoraService initialized. Mock mode: {self.mock_mode}, API key present: {bool(self.api_key)}")

    def generate_video(self, request: SoraGenerationRequest) -> SoraGenerationResponse:
        """
        Initiate video generation using Sora 2 API
        """
        if self.mock_mode:
            # Mock response for testing
            return SoraGenerationResponse(
                task_id="mock_task_id_12345",
                status="completed"
            )

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }

        payload = {
            "input": {
                "image": request.image,
                "prompt": request.prompt,
                "length": request.length,
                "aspectRatio": request.aspect_ratio
            }
        }

        if request.webhook_url:
            payload["webhookUrl"] = request.webhook_url

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            return SoraGenerationResponse(
                task_id=data.get("taskId"),
                status=data.get("status")
            )
        except requests.RequestException as e:
            logger.error(f"Error initiating Sora 2 generation: {e}")
            raise

    async def poll_for_completion(self, task_id: str, max_polls: int = 30, poll_interval: int = 10) -> Dict[str, Any]:
        """
        Poll for the completion of the video generation task
        Note: This is a placeholder. In production, use webhooks for real-time updates.
        """
        # Since the API doesn't specify a status endpoint, we'll simulate polling
        # In a real implementation, you'd need to check the API documentation for status checking
        for _ in range(max_polls):
            await asyncio.sleep(poll_interval)
            # Placeholder: Assume completion after some time
            # Replace with actual status API call if available
            logger.info(f"Polling for task {task_id}...")

        # For now, return a mock completed status
        return {
            "task_id": task_id,
            "status": "completed",
            "video_url": f"https://example.com/generated_video_{task_id}.mp4"  # Placeholder
        }

# Global instance
sora_service = SoraService()