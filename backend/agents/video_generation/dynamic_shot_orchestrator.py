import asyncio
import json
import logging
import os
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import tempfile
import base64
from google import genai
from google.genai import types
from google.cloud import texttospeech
from app.services.veo_service import veo_service, VeoGenerationRequest

@dataclass
class ShotComposition:
    """Data class for individual shot composition"""
    scene_id: int
    shot_type: str  # wide_shot, medium_shot, close_up, extreme_close_up
    camera_angle: str  # eye_level, high_angle, low_angle, dutch_angle
    lighting: str  # natural, dramatic, soft, harsh, golden_hour
    color_palette: str  # vibrant, muted, monochromatic, complementary
    action_description: str
    duration_seconds: float
    voiceover_text: str
    visual_effects: List[str] = field(default_factory=list)
    transition_in: str = "fade"
    transition_out: str = "fade"

@dataclass
class VideoSequence:
    """Data class for complete video sequence"""
    sequence_id: str
    shots: List[ShotComposition]
    total_duration: float
    music_style: str
    voiceover_style: str
    overall_theme: str
    target_platform: str
    aspect_ratio: str = "9:16"  # Default for mobile/social

@dataclass
class StyleFrame:
    """Data class for style reference frames"""
    frame_id: str
    prompt: str
    style_keywords: List[str]
    color_palette: Dict[str, str]
    composition_guidelines: Dict[str, Any]
    reference_image: Optional[str] = None

class StoryboardGenerator:
    """
    Generates structured storyboards from script content
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Shot type templates
        self.shot_templates = {
            'introduction': {
                'shot_type': 'wide_shot',
                'camera_angle': 'eye_level',
                'lighting': 'soft',
                'color_palette': 'vibrant'
            },
            'explanation': {
                'shot_type': 'medium_shot',
                'camera_angle': 'eye_level',
                'lighting': 'natural',
                'color_palette': 'neutral'
            },
            'detail': {
                'shot_type': 'close_up',
                'camera_angle': 'eye_level',
                'lighting': 'dramatic',
                'color_palette': 'monochromatic'
            },
            'conclusion': {
                'shot_type': 'wide_shot',
                'camera_angle': 'high_angle',
                'lighting': 'golden_hour',
                'color_palette': 'warm'
            }
        }

        # Platform-specific requirements
        self.platform_specs = {
            'tiktok': {
                'aspect_ratio': '9:16',
                'max_duration': 180,
                'preferred_shot_length': 3.0,
                'emphasis': 'visual_impact'
            },
            'youtube_shorts': {
                'aspect_ratio': '9:16',
                'max_duration': 60,
                'preferred_shot_length': 2.5,
                'emphasis': 'educational_value'
            },
            'instagram_reels': {
                'aspect_ratio': '9:16',
                'max_duration': 90,
                'preferred_shot_length': 3.5,
                'emphasis': 'aesthetic_appeal'
            }
        }

    async def generate_storyboard(self, script_data: Dict, platform: str = 'tiktok') -> VideoSequence:
        """Generate structured storyboard from script"""
        try:
            script_text = script_data.get('script', '')
            topic = script_data.get('topic', 'general')
            tone = script_data.get('tone', 'engaging')

            # Parse script into scenes
            scenes = self._parse_script_into_scenes(script_text)

            # Generate shot compositions for each scene
            shots = []
            for i, scene in enumerate(scenes):
                shot = await self._generate_shot_composition(scene, i, platform, topic, tone)
                shots.append(shot)

            # Calculate total duration
            total_duration = sum(shot.duration_seconds for shot in shots)

            # Generate sequence metadata
            sequence_id = hashlib.md5(f"{script_text}_{platform}_{datetime.now()}".encode()).hexdigest()

            # Determine music and voiceover style based on content
            music_style = self._determine_music_style(topic, tone)
            voiceover_style = self._determine_voiceover_style(tone)

            return VideoSequence(
                sequence_id=sequence_id,
                shots=shots,
                total_duration=total_duration,
                music_style=music_style,
                voiceover_style=voiceover_style,
                overall_theme=topic,
                target_platform=platform
            )

        except Exception as e:
            self.logger.error(f"Error generating storyboard: {e}")
            return self._get_fallback_sequence()

    def _parse_script_into_scenes(self, script_text: str) -> List[Dict]:
        """Parse script text into logical scenes"""
        scenes = []

        # Split by sentences or logical breaks
        sentences = [s.strip() for s in script_text.split('.') if s.strip()]

        # Group sentences into scenes (aim for 3-5 sentences per scene)
        sentences_per_scene = 3
        for i in range(0, len(sentences), sentences_per_scene):
            scene_sentences = sentences[i:i + sentences_per_scene]
            scene_text = '. '.join(scene_sentences)

            scenes.append({
                'scene_number': len(scenes) + 1,
                'text': scene_text,
                'sentence_count': len(scene_sentences)
            })

        return scenes

    async def _generate_shot_composition(self, scene: Dict, scene_index: int,
                                       platform: str, topic: str, tone: str) -> ShotComposition:
        """Generate shot composition for a single scene"""
        # Determine shot characteristics based on scene position and content
        shot_characteristics = self._determine_shot_characteristics(scene, scene_index, platform)

        # Generate action description using content analysis
        action_description = self._generate_action_description(scene['text'], topic, tone)

        # Calculate duration based on text length and platform
        duration = self._calculate_shot_duration(scene['text'], platform)

        # Generate voiceover text (can be same as scene text or modified)
        voiceover_text = self._generate_voiceover_text(scene['text'], tone)

        # Add visual effects based on content
        visual_effects = self._generate_visual_effects(scene['text'], topic)

        return ShotComposition(
            scene_id=scene['scene_number'],
            shot_type=shot_characteristics['shot_type'],
            camera_angle=shot_characteristics['camera_angle'],
            lighting=shot_characteristics['lighting'],
            color_palette=shot_characteristics['color_palette'],
            action_description=action_description,
            duration_seconds=duration,
            voiceover_text=voiceover_text,
            visual_effects=visual_effects
        )

    def _determine_shot_characteristics(self, scene: Dict, scene_index: int, platform: str) -> Dict:
        """Determine shot characteristics based on scene content and position"""
        # Base characteristics from templates
        if scene_index == 0:
            base_template = self.shot_templates['introduction']
        elif scene_index == len([scene]) - 1:  # Last scene
            base_template = self.shot_templates['conclusion']
        else:
            # Analyze content to determine if it's explanation or detail
            text_lower = scene['text'].lower()
            if any(word in text_lower for word in ['explain', 'show', 'demonstrate', 'how']):
                base_template = self.shot_templates['explanation']
            else:
                base_template = self.shot_templates['detail']

        # Platform-specific adjustments
        platform_spec = self.platform_specs.get(platform, self.platform_specs['tiktok'])

        # Modify based on platform emphasis
        if platform_spec['emphasis'] == 'visual_impact':
            if base_template['shot_type'] == 'medium_shot':
                base_template['shot_type'] = 'close_up'
        elif platform_spec['emphasis'] == 'educational_value':
            if base_template['shot_type'] == 'close_up':
                base_template['shot_type'] = 'medium_shot'

        return base_template

    def _generate_action_description(self, scene_text: str, topic: str, tone: str) -> str:
        """Generate detailed action description for AI video generation"""
        # Create vivid, specific descriptions for AI video models

        # Topic-specific visual elements
        topic_visuals = {
            'technology': 'modern digital interfaces, glowing screens, futuristic elements',
            'education': 'books, charts, diagrams, learning environments',
            'entertainment': 'dynamic movements, colorful backgrounds, engaging visuals',
            'business': 'professional settings, data visualizations, corporate environments',
            'lifestyle': 'everyday scenarios, personal spaces, relatable situations'
        }

        base_visuals = topic_visuals.get(topic, 'engaging visual elements')

        # Tone-specific modifiers
        tone_modifiers = {
            'exciting': 'dynamic and energetic',
            'calm': 'smooth and peaceful',
            'professional': 'clean and structured',
            'humorous': 'light-hearted and fun',
            'dramatic': 'intense and compelling'
        }

        tone_modifier = tone_modifiers.get(tone, 'engaging')

        # Combine into comprehensive description
        action_description = f"""
        Create a {tone_modifier} scene featuring {base_visuals}.
        The composition should be visually compelling with {scene_text.lower()}.
        Use appropriate lighting and camera work to maintain viewer engagement.
        """

        return action_description.strip()

    def _calculate_shot_duration(self, scene_text: str, platform: str) -> float:
        """Calculate optimal shot duration based on content and platform"""
        # Base duration on text length
        word_count = len(scene_text.split())
        base_duration = min(word_count * 0.8, 8.0)  # Max 8 seconds per shot

        # Platform-specific adjustments
        platform_spec = self.platform_specs.get(platform, self.platform_specs['tiktok'])
        preferred_length = platform_spec['preferred_shot_length']

        # Adjust duration based on platform preferences
        if platform_spec['emphasis'] == 'visual_impact':
            # Shorter, punchier shots for TikTok-style content
            adjusted_duration = min(base_duration, preferred_length)
        else:
            # Slightly longer for educational content
            adjusted_duration = min(base_duration * 1.2, preferred_length * 1.5)

        return max(1.5, adjusted_duration)  # Minimum 1.5 seconds

    def _generate_voiceover_text(self, scene_text: str, tone: str) -> str:
        """Generate or modify voiceover text"""
        # For now, use the scene text as voiceover
        # In production, this could be enhanced with text simplification,
        # emphasis keywords, or pacing adjustments

        return scene_text

    def _generate_visual_effects(self, scene_text: str, topic: str) -> List[str]:
        """Generate visual effects based on content"""
        effects = []

        # Content-based effects
        text_lower = scene_text.lower()

        if any(word in text_lower for word in ['amazing', 'incredible', 'wow', 'spectacular']):
            effects.append('sparkle_effect')

        if any(word in text_lower for word in ['fast', 'quick', 'rapid', 'speed']):
            effects.append('motion_blur')

        if any(word in text_lower for word in ['technology', 'digital', 'future', 'modern']):
            effects.append('tech_glow')

        if any(word in text_lower for word in ['nature', 'environment', 'green', 'eco']):
            effects.append('natural_lighting')

        # Topic-specific effects
        if topic == 'technology':
            effects.append('digital_interface_overlay')
        elif topic == 'education':
            effects.append('knowledge_graphic')

        return effects[:3]  # Limit to 3 effects per shot

    def _determine_music_style(self, topic: str, tone: str) -> str:
        """Determine appropriate music style"""
        style_matrix = {
            ('technology', 'exciting'): 'electronic_upbeat',
            ('technology', 'professional'): 'electronic_minimal',
            ('education', 'calm'): 'ambient_instrumental',
            ('education', 'engaging'): 'upbeat_educational',
            ('entertainment', 'exciting'): 'pop_energetic',
            ('entertainment', 'humorous'): 'quirky_fun',
            ('business', 'professional'): 'corporate_motivational',
            ('lifestyle', 'calm'): 'acoustic_warm'
        }

        return style_matrix.get((topic, tone), 'electronic_upbeat')

    def _determine_voiceover_style(self, tone: str) -> str:
        """Determine voiceover style based on tone"""
        style_mapping = {
            'exciting': 'energetic_young',
            'calm': 'warm_friendly',
            'professional': 'authoritative_clear',
            'humorous': 'casual_fun',
            'dramatic': 'deep_compelling'
        }

        return style_mapping.get(tone, 'energetic_young')

    def _get_fallback_sequence(self) -> VideoSequence:
        """Get fallback sequence when generation fails"""
        return VideoSequence(
            sequence_id="fallback",
            shots=[
                ShotComposition(
                    scene_id=1,
                    shot_type="medium_shot",
                    camera_angle="eye_level",
                    lighting="natural",
                    color_palette="vibrant",
                    action_description="A person speaking directly to camera",
                    duration_seconds=5.0,
                    voiceover_text="Content generation in progress"
                )
            ],
            total_duration=5.0,
            music_style="electronic_upbeat",
            voiceover_style="energetic_young",
            overall_theme="general",
            target_platform="tiktok"
        )

class StyleConsistencyManager:
    """
    Manages visual style consistency across video sequence
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.style_cache = {}

    async def generate_style_frame(self, sequence: VideoSequence) -> StyleFrame:
        """Generate reference style frame for visual consistency"""
        try:
            # Create style keywords based on sequence characteristics
            style_keywords = self._extract_style_keywords(sequence)

            # Generate color palette
            color_palette = self._generate_color_palette(sequence.overall_theme)

            # Create composition guidelines
            composition_guidelines = self._create_composition_guidelines(sequence)

            # Generate style prompt
            style_prompt = self._generate_style_prompt(style_keywords, color_palette, composition_guidelines)

            style_frame = StyleFrame(
                frame_id=f"style_{sequence.sequence_id}",
                prompt=style_prompt,
                style_keywords=style_keywords,
                color_palette=color_palette,
                composition_guidelines=composition_guidelines
            )

            self.style_cache[sequence.sequence_id] = style_frame
            return style_frame

        except Exception as e:
            self.logger.error(f"Error generating style frame: {e}")
            return self._get_default_style_frame()

    def _extract_style_keywords(self, sequence: VideoSequence) -> List[str]:
        """Extract style keywords from sequence"""
        keywords = []

        # Theme-based keywords
        theme_keywords = {
            'technology': ['modern', 'sleek', 'digital', 'futuristic'],
            'education': ['clear', 'structured', 'informative', 'professional'],
            'entertainment': ['vibrant', 'dynamic', 'engaging', 'colorful'],
            'business': ['professional', 'clean', 'corporate', 'polished'],
            'lifestyle': ['warm', 'relatable', 'authentic', 'natural']
        }

        keywords.extend(theme_keywords.get(sequence.overall_theme, ['modern', 'engaging']))

        # Platform-specific keywords
        platform_keywords = {
            'tiktok': ['trendy', 'youthful', 'energetic'],
            'youtube': ['educational', 'detailed', 'informative'],
            'instagram': ['aesthetic', 'beautiful', 'stylish']
        }

        keywords.extend(platform_keywords.get(sequence.target_platform, []))

        return keywords

    def _generate_color_palette(self, theme: str) -> Dict[str, str]:
        """Generate color palette for theme"""
        palettes = {
            'technology': {
                'primary': '#00D4FF',
                'secondary': '#3A7BD5',
                'accent': '#FF006E',
                'background': '#1a1a1a'
            },
            'education': {
                'primary': '#4ECDC4',
                'secondary': '#44A08D',
                'accent': '#093637',
                'background': '#f8f9fa'
            },
            'entertainment': {
                'primary': '#FF6B6B',
                'secondary': '#FFE66D',
                'accent': '#FF8E53',
                'background': '#2D2D2D'
            },
            'business': {
                'primary': '#2C3E50',
                'secondary': '#3498DB',
                'accent': '#E74C3C',
                'background': '#ECF0F1'
            },
            'lifestyle': {
                'primary': '#A8E6CF',
                'secondary': '#88D8C0',
                'accent': '#F8F8F8',
                'background': '#2D2D2D'
            }
        }

        return palettes.get(theme, palettes['technology'])

    def _create_composition_guidelines(self, sequence: VideoSequence) -> Dict[str, Any]:
        """Create composition guidelines for consistent visuals"""
        return {
            'rule_of_thirds': True,
            'leading_lines': True,
            'color_harmony': 'analogous',
            'contrast_level': 'medium',
            'focus_point': 'center_third',
            'movement_direction': 'dynamic' if sequence.music_style == 'electronic_upbeat' else 'subtle'
        }

    def _generate_style_prompt(self, keywords: List[str], colors: Dict[str, str],
                              guidelines: Dict[str, Any]) -> str:
        """Generate comprehensive style prompt"""
        prompt = f"""
        Create a visually consistent style with {', '.join(keywords[:3])} aesthetic.
        Use a color palette featuring {colors['primary']}, {colors['secondary']}, and {colors['accent']}.
        Follow {guidelines['color_harmony']} color harmony principles.
        Maintain {guidelines['contrast_level']} contrast levels.
        Composition should use {guidelines['focus_point']} focus point with {guidelines['rule_of_thirds']} rule of thirds.
        """

        return prompt.strip()

    def _get_default_style_frame(self) -> StyleFrame:
        """Get default style frame when generation fails"""
        return StyleFrame(
            frame_id="default_style",
            prompt="Modern, clean, engaging visual style",
            style_keywords=['modern', 'clean', 'engaging'],
            color_palette={
                'primary': '#00D4FF',
                'secondary': '#3A7BD5',
                'accent': '#FF006E',
                'background': '#1a1a1a'
            },
            composition_guidelines={
                'rule_of_thirds': True,
                'leading_lines': True,
                'color_harmony': 'analogous',
                'contrast_level': 'medium'
            }
        )

class SceneBySceneGenerator:
    """
    Generates video content scene by scene with FFmpeg stitching
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp()

        # Initialize Gemini client with API key
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        if api_key:
            self.genai_client = genai.Client(
                api_key=api_key,
            )
        else:
            self.genai_client = None
            self.logger.warning("No Google API key configured. Set GOOGLE_CLOUD_API_KEY.")

        # Initialize TTS client with proper error handling
        try:
            self.tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS client: {e}")
            self.tts_client = None

    async def generate_video_sequence(self, sequence: VideoSequence,
                                       style_frame: StyleFrame, prompt: str, job_id: Optional[str] = None) -> str:
        """Generate video by creating individual scenes and stitching them"""
        try:
            # Generate individual scene videos
            scene_videos = []

            for i, shot in enumerate(sequence.shots):
                scene_video = await self._generate_single_scene(shot, style_frame, sequence, prompt, i)
                scene_videos.append(scene_video)

            # Stitch scenes together
            final_video = await self._stitch_scenes(scene_videos, sequence)

            # Save to uploads directory
            upload_dir = "uploads/videos"
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"generated_{job_id}.mp4" if job_id else f"generated_{sequence.sequence_id}.mp4"
            final_video_path = os.path.join(upload_dir, filename)

            # Copy the final video to uploads directory
            import shutil
            if final_video and os.path.exists(final_video):
                shutil.copy2(final_video, final_video_path)
                self.logger.info(f"Video saved to {final_video_path}")
            else:
                self.logger.error("No valid video file to save")
                return ""

            # Cleanup temporary files
            await self._cleanup_temp_files(scene_videos)

            return final_video_path

        except Exception as e:
            self.logger.error(f"Error generating video sequence: {e}")
            return ""

    async def _generate_single_scene(self, shot: ShotComposition, style_frame: StyleFrame,
                                    sequence: VideoSequence, prompt: str, scene_index: int) -> str:
        """Generate a single scene video"""
        try:
            # Create comprehensive prompt for AI video generation
            scene_prompt = self._create_scene_prompt(shot, style_frame, sequence)

            # Generate voiceover audio
            voiceover_audio = await self._generate_voiceover_audio(shot.voiceover_text, sequence.voiceover_style)

            # Generate background music segment
            music_segment = await self._generate_music_segment(shot.duration_seconds, sequence.music_style)

            # Generate visual scene using Veo or fallback
            scene_video = await self._generate_visual_scene(scene_prompt, shot.duration_seconds, prompt)

            # Combine elements
            final_scene = await self._combine_scene_elements(
                scene_video, voiceover_audio, music_segment, shot
            )

            return final_scene

        except Exception as e:
            self.logger.error(f"Error generating scene {shot.scene_id}: {e}")
            return await self._generate_fallback_scene(shot)

    def _create_scene_prompt(self, shot: ShotComposition, style_frame: StyleFrame,
                           sequence: VideoSequence) -> str:
        """Create detailed prompt for AI video generation"""
        prompt = f"""
        {shot.shot_type}, {shot.camera_angle}, {shot.lighting} lighting.
        Color palette: {shot.color_palette}.
        Style reference: {style_frame.prompt}.
        Action: {shot.action_description}.
        Duration: {shot.duration_seconds} seconds.
        Platform: {sequence.target_platform}.
        Visual effects: {', '.join(shot.visual_effects)}.
        """

        return prompt.strip()

    async def _generate_voiceover_audio(self, text: str, style: str) -> str:
        """Generate voiceover audio file using Google TTS"""
        try:
            if not self.tts_client:
                raise Exception("TTS client not available. Please ensure the Text-to-Speech API is enabled in Google Cloud Console.")

            # Use Google TTS
            request = {
                'input': {'text': text},
                'voice': {'language_code': 'en-US', 'ssml_gender': 'NEUTRAL'},
                'audio_config': {'audio_encoding': 'MP3'},
            }

            response = self.tts_client.synthesize_speech(request=request)
            audio_content = response.audio_content

            output_file = os.path.join(self.temp_dir, f"voiceover_{hashlib.md5(text.encode()).hexdigest()}.mp3")
            with open(output_file, 'wb') as f:
                f.write(audio_content)

            return output_file
        except Exception as e:
            self.logger.error(f"TTS failed: {e}. Creating silent audio. Note: Enable Text-to-Speech API in Google Cloud Console if not already done.")
            # Create silent audio using FFmpeg
            output_file = os.path.join(self.temp_dir, f"voiceover_{hashlib.md5(text.encode()).hexdigest()}.mp3")
            duration = max(1, len(text.split()) * 0.5)  # Estimate duration
            cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', f'sine=frequency=0:duration={duration}', '-c:a', 'libmp3lame', output_file]
            subprocess.run(cmd, check=True)
            return output_file

    async def _generate_music_segment(self, duration: float, style: str) -> str:
        """Generate music segment using Gemini"""
        if not self.genai_client:
            music_description = f"Mock music description for {duration}s in {style} style"
        else:
            # Use Gemini to generate a music description
            prompt = f"Generate a description for a {duration}s music segment in {style} style for a viral video."
            try:
                response = self.genai_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
                )
                music_description = response.text
            except Exception as e:
                self.logger.error(f"Gemini API error for music: {e}")
                music_description = f"Mock music description for {duration}s in {style} style"

        # Simulate music generation
        output_file = os.path.join(self.temp_dir, f"music_{duration}_{style}.mp3")
        # Create silent audio
        cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', f'sine=frequency=0:duration={duration}', '-c:a', 'libmp3lame', output_file]
        subprocess.run(cmd, check=True)
        return output_file

    async def _generate_visual_scene(self, prompt: str, duration: float, main_prompt: Optional[str] = None) -> str:
        """Generate visual scene using Vertex AI Veo API with proper authentication"""
        self.logger.info(f"Generating visual scene with prompt: {prompt[:50]}..., duration: {duration}")

        try:
            self.logger.info("Attempting to use Vertex AI Veo API for video generation")
            # Use Veo API with the main prompt
            veo_request = VeoGenerationRequest(
                prompt=main_prompt or prompt,
                aspect_ratio="16:9",  # Default, can be parameterized
                duration_seconds=str(int(duration)),
                sample_count=1,
                person_generation="allow_all",
                add_watermark=True,
                include_rai_reason=True,
                generate_audio=True,
                resolution="720p"
            )
            response = veo_service.generate_video(veo_request)
            self.logger.info(f"Vertex AI Veo API response: operation_id={response.operation_id}, status={response.status}")
            # Since it's async, poll for completion
            completion = await veo_service.poll_for_completion(response.operation_id)
            # Completion returns video_path if successful
            video_path = completion.get('video_path', '')
            if video_path:
                self.logger.info(f"Video generated successfully via Vertex AI Veo at {video_path}")
                return video_path
            else:
                raise ValueError("No video path from Vertex AI Veo")
        except Exception as e:
            self.logger.error(f"Error using Vertex AI Veo API: {e}")
            self.logger.error("CRITICAL: Vertex AI video generation failed. This should not happen in production.")
            raise  # Re-raise to prevent fallback - Vertex AI is required

        # Vertex AI is required - no fallback allowed
        raise Exception("Vertex AI video generation failed - no fallback available. Ensure GOOGLE_CLOUD_API_KEY is properly configured.")

    async def _combine_scene_elements(self, video_file: str, voiceover_file: str,
                                    music_file: str, shot: ShotComposition) -> str:
        """Combine video, voiceover, and music into final scene"""
        try:
            output_file = os.path.join(
                self.temp_dir,
                f"final_scene_{shot.scene_id}_{datetime.now().strftime('%H%M%S')}.mp4"
            )

            # Use FFmpeg to combine elements
            # This is a simplified version - full implementation would need proper FFmpeg command
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', video_file,
                '-i', voiceover_file,
                '-i', music_file,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-map', '2:a:0',
                '-filter_complex', '[1:a][2:a]amix=inputs=2[a]',
                '-map', '0:v',
                '-map', '[a]',
                '-t', str(shot.duration_seconds),
                output_file
            ]

            # Execute FFmpeg command
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return output_file
            else:
                self.logger.error(f"FFmpeg error: {result.stderr}")
                return video_file  # Return original video if combination fails

        except Exception as e:
            self.logger.error(f"Error combining scene elements: {e}")
            return video_file

    async def _stitch_scenes(self, scene_videos: List[str], sequence: VideoSequence) -> str:
        """Stitch multiple scenes together with transitions"""
        try:
            output_file = os.path.join(
                self.temp_dir,
                f"final_video_{sequence.sequence_id}.mp4"
            )

            if len(scene_videos) == 1:
                # Single scene - just copy the file
                import shutil
                shutil.copy2(scene_videos[0], output_file)
                return output_file

            # Filter out empty or invalid video files
            valid_videos = [v for v in scene_videos if v and os.path.exists(v) and os.path.getsize(v) > 0]
            if not valid_videos:
                self.logger.error("No valid video files to stitch")
                return ""

            # Create file list for FFmpeg concat
            concat_file = os.path.join(self.temp_dir, 'concat_list.txt')
            with open(concat_file, 'w') as f:
                for video in valid_videos:
                    f.write(f"file '{video}'\n")

            # FFmpeg concat command with re-encoding to ensure compatibility
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                output_file
            ]

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return output_file
            else:
                self.logger.error(f"FFmpeg concat error: {result.stderr}")
                # Try alternative approach - merge videos sequentially
                return await self._merge_videos_sequentially(valid_videos, output_file)

        except Exception as e:
            self.logger.error(f"Error stitching scenes: {e}")
            return scene_videos[0] if scene_videos else ""

    async def _merge_videos_sequentially(self, video_files: List[str], output_file: str) -> str:
        """Alternative method to merge videos by concatenating them sequentially"""
        try:
            if len(video_files) == 1:
                import shutil
                shutil.copy2(video_files[0], output_file)
                return output_file

            # Build FFmpeg command for sequential merging
            inputs = []
            filter_complex = []
            audio_inputs = []

            for i, video in enumerate(video_files):
                inputs.extend(['-i', video])
                filter_complex.append(f'[{i}:v][{i}:a]')
                audio_inputs.append(f'[{i}:a]')

            # Create concat filter for video and audio
            video_concat = ''.join([f'[{i}:v]' for i in range(len(video_files))])
            audio_concat = ''.join([f'[{i}:a]' for i in range(len(video_files))])

            filter_complex_str = f'{video_concat}concat=n={len(video_files)}:v=1:a=1[v][a]'

            ffmpeg_cmd = [
                'ffmpeg', '-y',
                *inputs,
                '-filter_complex', filter_complex_str,
                '-map', '[v]',
                '-map', '[a]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                output_file
            ]

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return output_file
            else:
                self.logger.error(f"Sequential merge failed: {result.stderr}")
                return video_files[0] if video_files else ""

        except Exception as e:
            self.logger.error(f"Error in sequential merge: {e}")
            return video_files[0] if video_files else ""

    async def _generate_fallback_scene(self, shot: ShotComposition) -> str:
        """Generate fallback scene when normal generation fails"""
        fallback_file = os.path.join(self.temp_dir, f"fallback_scene_{shot.scene_id}.mp4")
        # Create a placeholder video
        cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', f'color=c=red:size=1280x720:duration={shot.duration_seconds}:rate=30', '-c:v', 'libx264', fallback_file]
        subprocess.run(cmd, check=True)
        return fallback_file

    async def _cleanup_temp_files(self, scene_videos: List[str]):
        """Clean up temporary files"""
        try:
            import shutil

            # Remove individual scene files
            for video_file in scene_videos:
                if os.path.exists(video_file):
                    os.remove(video_file)

            # Optionally remove entire temp directory
            # shutil.rmtree(self.temp_dir)

        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")

class DynamicShotOrchestrator:
    """
    Main orchestrator that coordinates storyboard generation and scene-by-scene video creation
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.storyboard_generator = StoryboardGenerator()
        self.style_manager = StyleConsistencyManager()
        self.scene_generator = SceneBySceneGenerator()

    async def orchestrate_video_creation(self, script_data: Dict, platform: str = 'tiktok', prompt: Optional[str] = None, job_id: Optional[str] = None) -> Dict:
        """Main method to orchestrate complete video creation"""
        try:
            # Step 1: Generate structured storyboard
            storyboard = await self.storyboard_generator.generate_storyboard(script_data, platform)

            # Step 2: Create style frame for consistency
            style_frame = await self.style_manager.generate_style_frame(storyboard)

            # Step 3: Generate video scene by scene
            final_video_path = await self.scene_generator.generate_video_sequence(storyboard, style_frame, prompt, job_id)

            # Step 4: Return complete video package
            video_package = {
                'video_path': final_video_path,
                'storyboard': storyboard,
                'style_frame': style_frame,
                'metadata': {
                    'total_duration': storyboard.total_duration,
                    'shot_count': len(storyboard.shots),
                    'platform': platform,
                    'generated_at': datetime.now(),
                    'sequence_id': storyboard.sequence_id
                }
            }

            return video_package

        except Exception as e:
            self.logger.error(f"Error in video orchestration: {e}")
            # Return a mock video path for testing
            mock_video_path = "uploads/videos/generated_mock_video.mp4"
            return {
                'video_path': mock_video_path,
                'error': str(e),
                'metadata': {'generated_at': datetime.now()}
            }

    def get_shot_breakdown(self, storyboard: VideoSequence) -> Dict:
        """Get detailed breakdown of shots in the sequence"""
        breakdown = {
            'total_shots': len(storyboard.shots),
            'total_duration': storyboard.total_duration,
            'shot_types': defaultdict(int),
            'shot_details': []
        }

        for shot in storyboard.shots:
            breakdown['shot_types'][shot.shot_type] += 1
            breakdown['shot_details'].append({
                'scene_id': shot.scene_id,
                'shot_type': shot.shot_type,
                'duration': shot.duration_seconds,
                'has_effects': len(shot.visual_effects) > 0,
                'effects_count': len(shot.visual_effects)
            })

        return breakdown