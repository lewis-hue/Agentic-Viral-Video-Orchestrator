import os
import json
import logging
import requests
import asyncio
import base64
import tempfile
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VeoGenerationRequest:
    prompt: str
    aspect_ratio: str = "16:9"
    sample_count: int = 1
    duration_seconds: str = "4"
    person_generation: str = "allow_all"
    add_watermark: bool = True
    include_rai_reason: bool = True
    generate_audio: bool = True
    resolution: str = "720p"

@dataclass
class VeoGenerationResponse:
    operation_id: str
    status: str

class VeoService:
    def __init__(self):
        self.project_id = "datascrapex-470817"
        self.location_id = "us-central1"
        self.model_id = "veo-3.1-generate-preview"  # Updated to use the new model as per user request
        self.api_endpoint = "us-central1-aiplatform.googleapis.com"
        self.api_key = os.environ.get("GEMINI_API_KEY", "")  # Set the provided API key
        if self.api_key:
            self.mock_mode = False
            logger.info("Using Google Cloud API key for authentication - Vertex AI Veo enabled")
        else:
            self.mock_mode = True
            logger.error("CRITICAL: No Google API key configured. Set GOOGLE_CLOUD_API_KEY to enable Vertex AI video generation. Falling back to mock mode.")

        logger.info(f"VeoService initialized. Mock mode: {self.mock_mode}, API key present: {bool(self.api_key)}")

    def generate_video(self, request: VeoGenerationRequest) -> VeoGenerationResponse:
        """
        Initiate video generation using Veo API
        """
        if self.mock_mode:
            logger.info("Mock mode: Simulating Veo video generation")
            return VeoGenerationResponse(
                operation_id="mock_operation_id_12345",
                status="completed"
            )

        # Prepare the request payload
        payload = {
            "endpoint": f"projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}",
            "instances": [
                {
                    "prompt": request.prompt,
                }
            ],
            "parameters": {
                "aspectRatio": request.aspect_ratio,
                "sampleCount": request.sample_count,
                "durationSeconds": request.duration_seconds,
                "personGeneration": request.person_generation,
                "addWatermark": request.add_watermark,
                "includeRaiReason": request.include_rai_reason,
                "generateAudio": request.generate_audio,
                "resolution": request.resolution,
            }
        }

        if not self.api_key:
            raise ValueError("No API key available for authentication")

        headers = {
            'Content-Type': 'application/json'
        }
        url = f"https://{self.api_endpoint}/v1/projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}:predictLongRunning?key={self.api_key}"

        try:
            logger.info(f"Sending request to Veo API: {url}")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            operation_name = data.get('name')
            if not operation_name:
                raise ValueError("No operation name in response")

            logger.info(f"Veo API initiated operation: {operation_name}")
            return VeoGenerationResponse(
                operation_id=operation_name,
                status="running"
            )
        except requests.RequestException as e:
            logger.error(f"Error initiating Veo generation: {e}")
            raise

    async def poll_for_completion(self, operation_id: str, max_polls: int = 30, poll_interval: int = 10) -> Dict[str, Any]:
        """
        Poll for the completion of the video generation task
        """
        if self.mock_mode:
            logger.info("Mock mode: Simulating polling for completion")
            await asyncio.sleep(2)  # Simulate delay
            return {
                "operation_id": operation_id,
                "status": "completed",
                "video_path": self._create_mock_video()
            }

        url = f"https://{self.api_endpoint}/v1/projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}:fetchPredictOperation?key={self.api_key}"

        headers = {
            'Content-Type': 'application/json'
        }

        for attempt in range(max_polls):
            try:
                logger.info(f"Polling Veo operation {operation_id}, attempt {attempt + 1}")
                payload = {"operationName": operation_id}
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Check the operation status
                done = data.get('done', False)
                if done:
                    logger.info(f"Operation {operation_id} completed. Full response: {data}")
                    if 'response' in data:
                        # Operation completed successfully
                        videos = data['response'].get('videos', [])
                        logger.info(f"Videos: {videos}")
                        if videos:
                            video_data = videos[0].get('bytesBase64Encoded')
                            if video_data:
                                # Decode base64 and save to file
                                video_bytes = base64.b64decode(video_data)
                                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                                    tmp_file.write(video_bytes)
                                    return {
                                        "operation_id": operation_id,
                                        "status": "completed",
                                        "video_path": tmp_file.name
                                    }
                            else:
                                logger.error("Video data is empty")
                        else:
                            logger.error("No videos in response")
                            raise ValueError("No video data in completed operation")
                    elif 'error' in data:
                        # Operation failed
                        error = data['error']
                        logger.error(f"Operation failed: {error}")
                        raise ValueError(f"Operation failed: {error.get('message', 'Unknown error')}")
                    else:
                        logger.error("Operation completed but no response or error found")
                        raise ValueError("Operation completed but no response or error found")
                else:
                    # Operation still running
                    logger.info("Operation still running, waiting...")
                    await asyncio.sleep(poll_interval)
            except requests.RequestException as e:
                logger.error(f"Error polling Veo operation: {e}")
                await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Operation {operation_id} did not complete within {max_polls * poll_interval} seconds")

    def _create_mock_video(self) -> str:
        """Create a mock video file for testing"""
        import subprocess
        import tempfile
        import os

        # Create a simple colored video using FFmpeg
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            video_path = tmp_file.name

        # Generate a 3-second blue video
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=c=blue:size=1280x720:duration=3:rate=30',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            video_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Mock video created at {video_path}")
            return video_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create mock video: {e}")
            return ""

# Global instance
veo_service = VeoService()