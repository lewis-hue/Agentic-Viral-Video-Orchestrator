import asyncio
from typing import List, Dict
import requests
from playwright.async_api import async_playwright
import os
import json
from google.cloud import speech_v1 as speech
import io
from google import genai
from google.genai import types
import logging

class TrendDiscoveryAgent:
    def __init__(self, gemini_api_key: str = None):
        if gemini_api_key:
            os.environ["GOOGLE_CLOUD_API_KEY"] = gemini_api_key
        self.client = genai.Client(
            vertexai=True,
            api_key=os.environ.get("GOOGLE_CLOUD_API_KEY"),
        )
        try:
            self.speech_client = speech.SpeechClient()
        except Exception:
            self.speech_client = None
        self.prompt_template = "Analyze the provided content or scan social platforms to identify 5 top viral trends. For each trend, provide: theme (name), description, key_elements (list), virality_score (1-100), reasoning, and additional_instructions (hook, style, tone). Output as a JSON array of 5 objects."
        logging.basicConfig(level=logging.INFO)

    async def analyze_links(self, links: List[str]) -> List[str]:
        video_uris = []
        for link in links:
            platform = self.detect_platform(link)
            if platform == 'youtube':
                video_id = self.extract_youtube_video_id(link)
                if video_id:
                    if '/shorts/' in link:
                        uri = f"https://www.youtube.com/shorts/{video_id}"
                    else:
                        uri = f"https://www.youtube.com/watch?v={video_id}"
                    video_uris.append(uri)
                else:
                    logging.warning(f"Invalid YouTube link: {link}")
            elif platform == 'tiktok':
                # Placeholder for TikTok scraping
                logging.info(f"TikTok link: {link} (scraping not implemented)")
            elif platform == 'instagram':
                # Placeholder for Instagram scraping
                logging.info(f"Instagram link: {link} (scraping not implemented)")
            else:
                logging.info(f"Unknown link: {link}")
        return video_uris

    def detect_platform(self, url: str) -> str:
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'instagram.com' in url:
            return 'instagram'
        else:
            return 'unknown'

    def extract_youtube_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc:
            if '/shorts/' in parsed.path:
                return parsed.path.split('/shorts/')[1].split('?')[0]
            elif 'watch' in parsed.path:
                return parse_qs(parsed.query).get('v', [None])[0]
        elif 'youtu.be' in parsed.netloc:
            return parsed.path.lstrip('/')
        return None

    def fetch_youtube_video_data(self, video_id: str) -> dict:
        """Fetch video data from YouTube API."""
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        import os
        youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
        if not youtube_api_key:
            return None
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
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

    async def analyze_voice_input(self, voice_input: str) -> str:
        # If voice_input is a file path, transcribe it
        if os.path.isfile(voice_input):
            transcribed_text = await self.transcribe_audio(voice_input)
            return f" Transcribed voice: {transcribed_text}\n"
        else:
            return f" Voice input: {voice_input}\n"

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file using Google Speech-to-Text."""
        if not self.speech_client:
            return "Audio transcription not available (missing credentials)"
        with io.open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )

        response = self.speech_client.recognize(config=config, audio=audio)

        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript

        return transcript

    async def analyze_files(self, files: List[str]) -> str:
        content = ""
        for file in files:
            if os.path.isfile(file):
                try:
                    with open(file, 'r') as f:
                        file_content = f.read()
                    content += f" File content: {file_content}\n"
                except:
                    content += f" File: {file} (could not read)\n"
            else:
                content += f" File: {file} (not found)\n"
        return content

    async def discover_trends(self, links: List[str] = [], voice_input: str = "", files: List[str] = []) -> List[Dict]:
        # Analyze provided inputs
        video_uris = []
        content = ""
        if links:
            video_uris = await self.analyze_links(links)
        if voice_input:
            content += await self.analyze_voice_input(voice_input)
        if files:
            content += await self.analyze_files(files)

        # If no video URIs and no content, scan platforms
        if not video_uris and not content:
            content = await self.scan_platforms()

        # Use Gemini to generate trends
        if not self.client:
            logging.warning("Gemini client not initialized. Using mock data.")
            return [
                {"theme": "Mock Trend 1", "description": "Mock description", "key_elements": ["mock"], "virality_score": 50, "reasoning": "Mock", "additional_instructions": {"hook": "mock", "style": "mock", "tone": "mock"}},
                {"theme": "Mock Trend 2", "description": "Mock description", "key_elements": ["mock"], "virality_score": 60, "reasoning": "Mock", "additional_instructions": {"hook": "mock", "style": "mock", "tone": "mock"}},
                {"theme": "Mock Trend 3", "description": "Mock description", "key_elements": ["mock"], "virality_score": 70, "reasoning": "Mock", "additional_instructions": {"hook": "mock", "style": "mock", "tone": "mock"}},
                {"theme": "Mock Trend 4", "description": "Mock description", "key_elements": ["mock"], "virality_score": 80, "reasoning": "Mock", "additional_instructions": {"hook": "mock", "style": "mock", "tone": "mock"}},
                {"theme": "Mock Trend 5", "description": "Mock description", "key_elements": ["mock"], "virality_score": 90, "reasoning": "Mock", "additional_instructions": {"hook": "mock", "style": "mock", "tone": "mock"}}
            ]

        model = "gemini-2.5-flash"
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            seed=0,
            max_output_tokens=32768,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
            ],
        )

        contents = []
        if video_uris:
            for uri in video_uris:
                msg_video = types.Part.from_uri(file_uri=uri, mime_type="video/mp4")
                contents.append(types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=self.prompt_template),
                        msg_video
                    ]
                ))
        else:
            full_prompt = self.prompt_template.format(content=content)
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=full_prompt)]
            ))

        logging.info(f"Sending request to Gemini with {len(contents)} contents.")
        try:
            response_text = ""
            for content in contents:
                for chunk in self.client.models.generate_content_stream(
                    model=model,
                    contents=[content],
                    config=generate_content_config,
                ):
                    response_text += chunk.text
            logging.info("Gemini response received successfully.")
            logging.info(f"Response text: {response_text}")
            try:
                # Remove markdown code block if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                trends = json.loads(response_text)
                logging.info(f"Generated {len(trends)} trends.")
                return trends
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON response: {response_text}")
                return [
                    {"theme": "Error Trend 1", "description": "Invalid response format", "key_elements": ["error"], "virality_score": 0, "reasoning": "JSON Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                    {"theme": "Error Trend 2", "description": "Invalid response format", "key_elements": ["error"], "virality_score": 0, "reasoning": "JSON Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                    {"theme": "Error Trend 3", "description": "Invalid response format", "key_elements": ["error"], "virality_score": 0, "reasoning": "JSON Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                    {"theme": "Error Trend 4", "description": "Invalid response format", "key_elements": ["error"], "virality_score": 0, "reasoning": "JSON Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                    {"theme": "Error Trend 5", "description": "Invalid response format", "key_elements": ["error"], "virality_score": 0, "reasoning": "JSON Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}}
                ]
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            return [
                {"theme": "Error Trend 1", "description": "Error in API call", "key_elements": ["error"], "virality_score": 0, "reasoning": "API Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                {"theme": "Error Trend 2", "description": "Error in API call", "key_elements": ["error"], "virality_score": 0, "reasoning": "API Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                {"theme": "Error Trend 3", "description": "Error in API call", "key_elements": ["error"], "virality_score": 0, "reasoning": "API Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                {"theme": "Error Trend 4", "description": "Error in API call", "key_elements": ["error"], "virality_score": 0, "reasoning": "API Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}},
                {"theme": "Error Trend 5", "description": "Error in API call", "key_elements": ["error"], "virality_score": 0, "reasoning": "API Error", "additional_instructions": {"hook": "error", "style": "error", "tone": "error"}}
            ]

    async def scan_platforms(self) -> str:
        # Placeholder for scanning platforms if no inputs
        return "No specific inputs provided. Scanning general trends from TikTok, YouTube, X, Instagram."