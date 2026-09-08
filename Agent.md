# Agent.md — AVVO Agent Architecture Reference

> This document is the authoritative reference for all AI agents in the AVVO system. Read this before modifying any agent code.

---

## Agent Pipeline Overview

AVVO runs a **7-stage sequential pipeline** coordinated by the `EnhancedOrchestrator` in `backend/app/orchestrator.py`. Each stage maps to a dedicated agent module.

```
[Input: Topic / Platform]
         │
         ▼
┌─────────────────────┐
│  1. Trend Discovery  │  Scans TikTok, YouTube, Instagram, X for viral signals
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  2. Story Ideation   │  Generates structured JSON scripts from trend data
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  3. Brand Safety     │  Validates content for ethical compliance pre-production
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  4. Video Generation │  Storyboards and synthesizes the video shot-by-shot
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  5. Predictive Intel │  Forecasts performance; detects cross-platform arbitrage
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  6. Optimization     │  Applies RL-driven creative parameter adjustments
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  7. Publisher        │  Schedules and publishes to TikTok, YouTube, Instagram
└─────────────────────┘
```

---

## Agent 1: Trend Discovery Agent

**File:** `backend/agents/trend_discovery/trend_discovery_agent.py`
**Primary Model:** Google Gemini 2.5-flash

### Responsibility
Discovers trending content signals across social media platforms and scores them for viral potential.

### Key Methods
| Method | Input | Output |
|--------|-------|--------|
| `discover_trends(topic, platform)` | Topic string, platform name | List of `TrendResult` dicts |
| `analyze_links(urls)` | List of video URLs | Trend analysis per URL |
| `analyze_voice_input(audio_bytes)` | Raw audio bytes | Transcribed + analyzed trends |
| `analyze_files(file_paths)` | File paths (images, docs) | Extracted trend signals |

### Output Schema
```json
{
  "trend_id": "string",
  "platform": "tiktok | youtube | instagram | x",
  "summary": "string",
  "virality_score": 0.0,
  "keywords": ["string"],
  "engagement_metrics": {},
  "timestamp": "ISO8601"
}
```

### Virality Score
- Scale: 1–100
- Factors: engagement velocity, cross-platform presence, keyword frequency, recency

---

## Agent 2: Story Ideation Agent

**File:** `backend/agents/story_ideation/story_ideation_agent.py`
**Primary Model:** Google Gemini 2.5-flash

### Responsibility
Converts trend data into production-ready video scripts with hooks, scenes, voiceovers, and CTAs.

### Key Methods
| Method | Input | Output |
|--------|-------|--------|
| `generate_script(trend_data, platform)` | Trend result dict | Structured script JSON |
| `rank_scripts(scripts)` | List of scripts | Ranked list by predicted performance |
| `analyze_voice_input(audio_bytes)` | Audio | Script from voice brief |

### Output Schema
```json
{
  "script_id": "string",
  "title": "string",
  "hook": "string (first 3 seconds)",
  "scenes": [
    {
      "scene_number": 1,
      "duration_seconds": 5,
      "visual_description": "string",
      "voiceover": "string",
      "on_screen_text": "string"
    }
  ],
  "cta": "string",
  "total_duration_seconds": 60,
  "target_platform": "tiktok | youtube_shorts | instagram_reels",
  "predicted_score": 0.0
}
```

### Platform Duration Targets
| Platform | Max Duration |
|----------|-------------|
| TikTok | 180 seconds |
| YouTube Shorts | 60 seconds |
| Instagram Reels | 90 seconds |

---

## Agent 3: Brand Safety Agent (Ethical Guardian)

**File:** `backend/agents/brand_safety/ethical_guardian_agent.py`
**Primary Model:** Google Gemini 2.5-flash + regex classifiers

### Responsibility
Validates scripts and generated content for brand safety, ethical compliance, and platform policy adherence **before** video production begins.

### Safety Checks Performed
| Check | Method |
|-------|--------|
| Hate speech | Regex pattern matching |
| NSFW content | Keyword classifier |
| Violence | Pattern matching |
| Misinformation | LLM-based review |
| Brand alignment | Keyword scoring |
| Adversarial probing | Injection test suite |

### Key Methods
| Method | Input | Output |
|--------|-------|--------|
| `evaluate_content(script)` | Script JSON | Safety report |
| `score_brand_alignment(content, brand_guidelines)` | Content + guidelines | Alignment score 0–1 |
| `recommend_review(report)` | Safety report | `requires_human_review: bool` |

### Output Schema
```json
{
  "safe": true,
  "brand_safety_score": 0.95,
  "flags": [],
  "requires_human_review": false,
  "risk_level": "LOW | MEDIUM | HIGH | CRITICAL",
  "recommendations": ["string"]
}
```

> **Rule:** If `risk_level` is `HIGH` or `CRITICAL`, the pipeline halts and a human review task is created. Never bypass this check.

---

## Agent 4: Video Generation Agent (Dynamic Shot Orchestrator)

**File:** `backend/agents/video_generation/dynamic_shot_orchestrator.py`
**Primary Model:** Google Vertex AI Veo + Google Text-to-Speech

### Responsibility
Produces the final video from a script by generating a storyboard, synthesizing individual scenes, adding voiceover and music, then stitching everything with FFmpeg.

### Internal Components

#### `StoryboardGenerator`
- Input: Script JSON
- Output: `VideoSequence` — ordered list of `ShotComposition` objects

#### `StyleConsistencyManager`
- Maintains visual coherence (color palette, lighting, camera language) across scenes
- Prevents style drift between shots

#### `SceneBySceneGenerator`
- Calls Veo API per scene using the storyboard spec
- Returns video clip paths

#### `DynamicShotOrchestrator` (main class)
- Coordinates the above components
- Synthesizes voiceover via Google TTS
- Calls music generation API (Suno)
- Runs FFmpeg to stitch clips, add audio tracks

### Key Data Structures

```python
@dataclass
class ShotComposition:
    shot_type: str           # wide, medium, close-up, extreme-close-up
    camera_angle: str        # eye-level, low-angle, high-angle, dutch
    lighting: str            # natural, studio, dramatic, soft
    color_palette: list[str] # hex codes
    vfx: list[str]           # transitions, overlays
    duration_seconds: float
    prompt: str              # text prompt for Veo

@dataclass
class VideoSequence:
    shots: list[ShotComposition]
    platform: str
    aspect_ratio: str        # "9:16" for TikTok/Reels, "16:9" for YouTube
    total_duration: float
    style_profile: dict
```

### Key Methods
| Method | Input | Output |
|--------|-------|--------|
| `generate_video(script)` | Script JSON | `{"video_path": str, "job_id": str}` |
| `generate_storyboard(script)` | Script JSON | `VideoSequence` |
| `synthesize_voiceover(script)` | Script JSON | Audio file path |

### Platform Aspect Ratios
| Platform | Ratio | Resolution |
|----------|-------|-----------|
| TikTok | 9:16 | 1080×1920 |
| YouTube Shorts | 9:16 | 1080×1920 |
| Instagram Reels | 9:16 | 1080×1920 |
| YouTube (standard) | 16:9 | 1920×1080 |

---

## Agent 5: Predictive Intelligence Agent

**File:** `backend/agents/predictive_intelligence/predictive_intelligence_agent.py`
**Primary Models:** Facebook Prophet (forecasting), scikit-learn IsolationForest (anomaly detection)

### Responsibility
Forecasts trend trajectory, detects anomalous engagement patterns, and identifies cross-platform content arbitrage opportunities.

### Key Methods
| Method | Input | Output |
|--------|-------|--------|
| `forecast_trend_trajectory(trend_id, horizon_days)` | Trend ID, forecast window | Time-series forecast |
| `detect_anomalies(engagement_data)` | Engagement metrics array | Anomaly flags |
| `identify_cross_platform_opportunities(trends)` | Trend list | Arbitrage opportunities |
| `score_breakout_potential(trend)` | Single trend | Breakout score 0–1 |

### Output Schema (forecast)
```json
{
  "trend_id": "string",
  "forecast_horizon_days": 7,
  "predicted_peak_day": "ISO8601",
  "predicted_peak_engagement": 0.0,
  "confidence_interval": {"lower": 0.0, "upper": 0.0},
  "breakout_potential": 0.85,
  "recommended_publish_window": "string"
}
```

---

## Agent 6: Optimization & Feedback Agent (Reinforcement Strategy Engine)

**File:** `backend/agents/optimization_feedback/reinforcement_strategy_engine.py`

### Responsibility
Continuously improves creative strategy through reinforcement learning. Uses a **contextual bandit** (Upper Confidence Bound algorithm) to select creative parameters and updates its policy based on real engagement rewards.

### Internal Components

#### `ContextualBandit`
- Algorithm: UCB (Upper Confidence Bound)
- Context features: platform, time-of-day, audience segment, content category
- Arms: combinations of creative parameters

#### `ABTestManager`
- Creates and manages automated A/B experiments
- Tracks variants, splits traffic, determines statistical significance

#### `RewardModel`
- Computes multi-component reward signals from engagement metrics
- Reward components: views, watch-time, shares, saves, comments, follower gain

#### `ReinforcementStrategyEngine` (main class)
- Wires all components together
- Exposes `select_strategy()` and `update_from_feedback()` methods

### Creative Variables Optimized

```python
class CreativeVariable(Enum):
    VOICEOVER_STYLE   = "voiceover_style"    # energetic, calm, narrative, ASMR
    MUSIC_GENRE       = "music_genre"         # pop, trap, lo-fi, cinematic
    VIDEO_PACING      = "video_pacing"        # fast-cut, slow-burn, rhythmic
    NARRATIVE_STRUCTURE = "narrative_structure" # problem-solution, listicle, story-arc
    OPENING_HOOK      = "opening_hook"        # question, shock, statement, visual
    CTA_STYLE         = "cta_style"           # explicit, implicit, challenge
    VISUAL_STYLE      = "visual_style"        # raw, polished, animated, cinematic
    CONTENT_LENGTH    = "content_length"      # short (<30s), medium (30-60s), long (>60s)
```

### Key Methods
| Method | Input | Output |
|--------|-------|--------|
| `select_strategy(context)` | Platform + audience context | `CreativeParams` dict |
| `update_from_feedback(params, reward)` | Params used + engagement metrics | Updated bandit weights |
| `run_ab_test(variants, traffic_split)` | Variant list + split % | Experiment ID |
| `get_performance_report()` | — | Strategy performance summary |

---

## Agent 7: Publisher Agent

**File:** `backend/agents/publisher/index.js` (Node.js service)
**Integration:** Zapier webhooks → Buffer → platform APIs

### Responsibility
Schedules and publishes the final video to TikTok, YouTube, and Instagram. Handles platform-specific metadata (captions, hashtags, thumbnails).

### Supported Platforms
| Platform | Method | Profile ID Env Var |
|----------|--------|-------------------|
| TikTok | Zapier → TikTok API | `TIKTOK_PROFILE_ID` |
| YouTube | Zapier → YouTube API | `YOUTUBE_PROFILE_ID` |
| Instagram | Zapier → Instagram Graph API | `INSTAGRAM_PROFILE_ID` |

### Key Methods
| Method | Input | Output |
|--------|-------|--------|
| `publishVideo(videoPath, metadata, platforms)` | Video file + meta | Publish job ID |
| `schedulePost(videoPath, metadata, publishAt)` | Video + datetime | Schedule confirmation |
| `getPublishStatus(jobId)` | Job ID | Status + platform URLs |

### Metadata Schema
```json
{
  "title": "string",
  "description": "string",
  "hashtags": ["string"],
  "thumbnail_path": "string (optional)",
  "publish_at": "ISO8601 (optional, null = publish immediately)",
  "platforms": ["tiktok", "youtube", "instagram"]
}
```

---

## Supporting Agents

### Documentation Agent
**File:** `backend/agents/documentation/documentation_agent.py`
- Auto-generates documentation for pipeline runs
- Maintains versioned activity logs
- Updates knowledge base with successful pipeline patterns

### Simulation Agent
**File:** `backend/agents/simulation/simulation_agent.py`
- Runs the full pipeline in dry-run mode without publishing
- Returns predicted metrics and content previews
- Used for QA before production runs

---

## Orchestrator (`EnhancedOrchestrator`)

**File:** `backend/app/orchestrator.py`

### Pipeline Execution
```python
async def run_pipeline(topic: str, platform: str, options: dict) -> PipelineResult:
    # Stage 1
    trends = await trend_agent.discover_trends(topic, platform)
    # Stage 2
    scripts = await story_agent.generate_script(trends[0])
    # Stage 3 — halts on HIGH/CRITICAL risk
    safety = await brand_safety_agent.evaluate_content(scripts)
    if safety["risk_level"] in ("HIGH", "CRITICAL"):
        raise HumanReviewRequired(safety)
    # Stage 4
    video = await video_agent.generate_video(scripts)
    # Stage 5
    forecast = await predictive_agent.forecast_trend_trajectory(trends[0]["trend_id"])
    # Stage 6
    strategy = await optimization_agent.select_strategy(context)
    # Stage 7
    result = await publisher_agent.publishVideo(video["video_path"], metadata, platforms)
    return result
```

### Error Handling
- Each stage is wrapped in a try/except; failures update the `Job` record with `status=failed`
- Partial results are preserved — a video generation failure does not lose the script
- Human review flags are surfaced as notifications, not exceptions to the caller

---

## Inter-Agent Communication

Agents do **not** communicate directly with each other. All data flows through the orchestrator, which:
1. Holds the pipeline state in memory during execution
2. Persists each stage's output to the `Job` record in PostgreSQL
3. Returns the full accumulated result on completion

### Shared Data Format
All agents accept and return plain Python `dict` or Pydantic models. No agent imports another agent module.

---

## Adding a New Agent

1. Create a directory: `backend/agents/<agent_name>/`
2. Add `__init__.py` and `<agent_name>_agent.py`
3. Implement the agent class with an async primary method
4. Add the agent to `EnhancedOrchestrator` in `backend/app/orchestrator.py`
5. Create a router in `backend/app/routers/` if direct API access is needed
6. Register the router in `backend/app/main.py`
7. Add tests in `test_expert_features.py`

### Agent Template
```python
import os
import google.generativeai as genai

class MyNewAgent:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def primary_action(self, input_data: dict) -> dict:
        prompt = self._build_prompt(input_data)
        response = await self.model.generate_content_async(prompt)
        return self._parse_response(response.text)

    def _build_prompt(self, data: dict) -> str:
        raise NotImplementedError

    def _parse_response(self, text: str) -> dict:
        raise NotImplementedError
```

---

## External Service Dependencies

| Service | Agent(s) | Env Var | Fallback |
|---------|----------|---------|---------|
| Google Gemini 2.5-flash | All LLM agents | `GEMINI_API_KEY` | OpenAI GPT-4 |
| Vertex AI Veo | Video Generation | `GOOGLE_CLOUD_API_KEY` | Sora (OpenAI) |
| Google TTS | Video Generation | `GOOGLE_CLOUD_API_KEY` | ElevenLabs |
| Google STT | Trend Discovery, Story | `GOOGLE_CLOUD_API_KEY` | None |
| Suno | Video Generation | `SUNO_API_KEY` | None (no music) |
| ElevenLabs | Video Generation (alt TTS) | `ELEVENLABS_API_KEY` | Google TTS |
| Zapier | Publisher | `ZAPIER_WEBHOOK_URL` | None |
| Cloudinary | Video Uploader | `CLOUDINARY_URL` | Local storage |

---

## Testing Agents

Each agent should be testable in isolation. The test suite covers:

```bash
# Run all agent tests
python test_expert_features.py

# Tests included:
# - test_predictive_intelligence_agent()
# - test_reinforcement_strategy_engine()
# - test_brand_safety_guardian()
# - test_dynamic_shot_orchestrator()
# - test_enhanced_orchestrator_integration()
# - test_end_to_end_pipeline()
```

Test reports are JSON files written to the project root with timestamps:
```
avvo_expert_features_test_report_<YYYYMMDD_HHMMSS>.json
```

### Writing Agent Tests
- Mock external API calls (Gemini, Veo, TTS) using `unittest.mock`
- Test both happy path and error/safety-rejection cases
- Validate output schema matches documented JSON structure above
- Assert virality scores, safety scores, and forecasts are within expected ranges

---

## Performance & Scaling Notes

- **Trend Discovery** — I/O-bound, runs fast (~5–15s). Safe to run synchronously.
- **Story Ideation** — LLM inference (~10–30s). Run as Celery task for long scripts.
- **Video Generation** — Slow (~2–10 minutes per video). Always async via Celery. Poll `/status/{job_id}`.
- **Brand Safety** — Fast (~2–5s). Blocking check; must complete before video generation starts.
- **Predictive Intelligence** — CPU-bound (Prophet fitting). Run as Celery task.
- **Optimization** — In-memory (bandit weights). Near-instant. Run synchronously.
- **Publisher** — Network I/O (~10–60s depending on platform). Run as Celery task.
