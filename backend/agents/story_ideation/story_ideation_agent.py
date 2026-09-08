import asyncio
from typing import List, Dict
import os
import json
from google.cloud import speech
import io
from google import genai
from google.genai import types
import logging

class StoryIdeationAgent:
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
        self.script_prompt_template = "Create a short-form video script based on topic: {topic}, with instructions: {instructions}. Include hook, style, tone. Output as JSON with title, hook, scenes (scene_number, visual_description, voiceover_script, duration_seconds), cta. Content: {content}"
        logging.basicConfig(level=logging.INFO)

    async def generate_script(self, topic: str, instructions: str = "", voice_input: str = "", files: List[str] = []) -> Dict:
        content = f"Topic: {topic}\nInstructions: {instructions}\n"
        if voice_input:
            transcribed = await self.analyze_voice_input(voice_input)
            content += transcribed
        if files:
            file_content = await self.analyze_files(files)
            content += file_content

        if not self.client:
            logging.warning("Gemini client not initialized. Using mock data.")
            return {"title": "Mock Script", "hook": "Mock hook", "scenes": [{"scene_number": 1, "visual_description": "Mock visual", "voiceover_script": "Mock voiceover", "duration_seconds": 10}], "cta": "Mock CTA"}
        full_prompt = self.script_prompt_template.format(topic=topic, instructions=instructions, content=content)
        logging.info(f"Sending prompt to Gemini: {full_prompt[:100]}...")
        try:
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
            response_text = ""
            for chunk in self.client.models.generate_content_stream(
                model=model,
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])],
                config=generate_content_config,
            ):
                response_text += chunk.text
            logging.info("Gemini response received successfully.")
            logging.info(f"Response text: {response_text}")
            # Remove markdown code block if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            script = json.loads(response_text)
            logging.info(f"Generated script with {len(script.get('scenes', []))} scenes.")
            return script
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            return {"title": "Error Script", "hook": "Error in API call", "scenes": [{"scene_number": 1, "visual_description": "Error visual", "voiceover_script": "Error voiceover", "duration_seconds": 10}], "cta": "Error CTA"}

    async def analyze_voice_input(self, voice_input: str) -> str:
        if os.path.isfile(voice_input):
            transcribed_text = await self.transcribe_audio(voice_input)
            return f" Transcribed voice: {transcribed_text}\n"
        else:
            return f" Voice input: {voice_input}\n"

    async def transcribe_audio(self, audio_file_path: str) -> str:
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