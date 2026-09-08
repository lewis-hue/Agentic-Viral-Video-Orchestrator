# AVVO Multi-Platform Video Uploader

A comprehensive FastAPI service for uploading and publishing videos to multiple social media platforms including Instagram, Facebook, TikTok, Twitter/X, and YouTube. Features async processing, scheduled publishing, analytics ingestion, and modular platform integrations.

## 🚀 Features

- **Multi-Platform Support**: Instagram, Facebook, TikTok, Twitter/X, YouTube
- **Async Processing**: Non-blocking video uploads and publishing
- **Scheduled Publishing**: APScheduler integration for timed posts
- **Analytics Integration**: Engagement metrics collection and feedback loops
- **Voice-to-Text**: Integration for text input areas (excluding links)
- **Modular Design**: Easy integration with agentic orchestration layers
- **Production Ready**: Comprehensive error handling, logging, and monitoring
- **RESTful API**: Clean FastAPI endpoints with automatic documentation

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Platform Setup](#platform-setup)
- [Usage Examples](#usage-examples)
- [Analytics](#analytics)
- [Scheduling](#scheduling)
- [Production Considerations](#production-considerations)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd video-uploader-service
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

3. **Run the service:**
   ```bash
   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Upload your first video:**
   ```bash
   curl -X POST "http://localhost:8000/upload-and-publish" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@video.mp4" \
     -F "platforms=[\"instagram\",\"youtube\"]" \
     -F "title=My Video" \
     -F "description=Check out this awesome video!"
   ```

## 📦 Installation

### Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- Valid API credentials for target platforms

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
IG_USER_ID=your_instagram_user_id

# Facebook Graph API
FACEBOOK_PAGE_ID=your_facebook_page_id
FACEBOOK_PAGE_TOKEN=your_facebook_page_token

# TikTok Content Posting API
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token
TIKTOK_REFRESH_TOKEN=your_tiktok_refresh_token

# Twitter/X API
TWITTER_BEARER=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
YOUTUBE_ACCESS_TOKEN=your_youtube_access_token
YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token

# Analytics and Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO

# Database (Optional)
DATABASE_URL=postgresql://user:password@localhost/analytics_db
```

## 📚 API Documentation

Once the service is running, visit:
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check and service status |
| GET | `/platforms` | Available platforms and configuration status |
| POST | `/upload-and-publish` | Upload and publish video to multiple platforms |
| GET | `/publish-status/{publish_id}` | Check status of a publish request |

### Request/Response Examples

#### Upload and Publish Video

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-and-publish" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_video.mp4" \
  -F 'platforms=["instagram","facebook","youtube"]' \
  -F "title=My Awesome Video" \
  -F "description=This is a great video about technology!" \
  -F "publish_at=2024-01-15T10:30:00Z" \
  -F 'captions={"instagram":"#tech #innovation","youtube":"Technology showcase"}'
```

**Response:**
```json
{
  "status": "scheduled",
  "message": "Video scheduled for publishing to 3 platforms",
  "publish_id": "123e4567-e89b-12d3-a456-426614174000",
  "scheduled_at": "2024-01-15T10:30:00Z"
}
```

## 🔧 Platform Setup

### Instagram Setup

1. **Create a Facebook Developer App**
   - Go to [Facebook Developers](https://developers.facebook.com)
   - Create a new app or use existing one

2. **Add Instagram Basic Display Product**
   - In your app settings, add "Instagram Basic Display"

3. **Configure Instagram Business Account**
   - Connect your Instagram Business or Creator account to a Facebook Page
   - Ensure the account has the necessary permissions

4. **Required Scopes:**
   ```
   instagram_basic
   instagram_content_publish
   pages_read_engagement
   pages_manage_posts
   ```

5. **Get Access Token:**
   ```bash
   # Use Facebook's Graph API Explorer or your app's OAuth flow
   # Token should have the required scopes
   ```

### Facebook Setup

1. **Use the same Facebook App as Instagram**
2. **Required Scopes:**
   ```
   pages_read_engagement
   pages_manage_posts
   pages_read_user_content
   pages_manage_metadata
   ```

3. **Get Page Token:**
   ```bash
   GET /oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={app-id}&
     client_secret={app-secret}&
     fb_exchange_token={short-lived-token}
   ```

### TikTok Setup

1. **Create TikTok Developer App**
   - Go to [TikTok for Developers](https://developers.tiktok.com)
   - Create a new app

2. **Apply for Content Posting API**
   - Request access to Content Posting API
   - Complete the review process

3. **Required Scopes:**
   ```
   video.create
   video.publish
   ```

4. **OAuth Flow:**
   ```bash
   # Implement OAuth 2.0 flow to get access tokens
   # Store refresh tokens securely
   ```

### Twitter/X Setup

1. **Create Twitter Developer Account**
   - Apply for developer access at [Twitter Developer Portal](https://developer.twitter.com)

2. **Create a Project and App**
   - Set up authentication settings
   - Enable OAuth 2.0

3. **Required Permissions:**
   ```
   tweet.read
   tweet.write
   users.read
   offline.access
   ```

4. **Get Bearer Token:**
   - Generate in your app's "Keys and Tokens" section

### YouTube Setup

1. **Enable YouTube Data API**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Enable YouTube Data API v3

2. **Create OAuth 2.0 Credentials**
   - Set up OAuth client ID
   - Configure authorized redirect URIs

3. **Required Scopes:**
   ```
   https://www.googleapis.com/auth/youtube.upload
   https://www.googleapis.com/auth/youtube.readonly
   ```

4. **Get API Key:**
   - Create an API key in Google Cloud Console

## 💡 Usage Examples

### Basic Upload

```python
import requests

url = "http://localhost:8000/upload-and-publish"
files = {"file": open("video.mp4", "rb")}
data = {
    "platforms": '["instagram", "youtube"]',
    "title": "My Video",
    "description": "Check this out!"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Scheduled Publishing

```python
import requests
from datetime import datetime, timezone

url = "http://localhost:8000/upload-and-publish"
files = {"file": open("video.mp4", "rb")}
data = {
    "platforms": '["tiktok", "facebook"]',
    "title": "Scheduled Video",
    "description": "This will be published later!",
    "publish_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

response = requests.post(url, files=files, data=data)
print(f"Scheduled for: {response.json()['scheduled_at']}")
```

### Platform-Specific Captions

```python
import requests

url = "http://localhost:8000/upload-and-publish"
files = {"file": open("video.mp4", "rb")}
data = {
    "platforms": '["instagram", "youtube", "tiktok"]',
    "title": "Multi-Platform Video",
    "description": "Base description",
    "captions": {
        "instagram": "Instagram caption with #hashtags #viral",
        "youtube": "YouTube description with links and details",
        "tiktok": "TikTok trending hashtags #fyp #viral"
    }
}

response = requests.post(url, files=files, data=data)
```

## 📊 Analytics

### Automatic Analytics Collection

The service automatically collects engagement metrics after publishing:

- **Views/Watches**
- **Likes/Reactions**
- **Comments**
- **Shares/Retweets**
- **Saves/Bookmarks**
- **Engagement Rates**

### Analytics Endpoints

```bash
# Get platform status
GET /platforms

# Check publish status
GET /publish-status/{publish_id}
```

### Manual Analytics Fetching

```python
# In your code, you can manually fetch analytics
from analytics import fetch_instagram_metrics, fetch_youtube_metrics

# Fetch Instagram metrics
ig_metrics = await fetch_instagram_metrics("media_id_123")

# Fetch YouTube metrics
yt_metrics = await fetch_youtube_metrics("video_id_456")
```

## ⏰ Scheduling

### Schedule Management

The service uses APScheduler for robust job scheduling:

```python
from scheduler import schedule_publish, get_scheduler_status
from app import PublishRequest

# Schedule a video
request = PublishRequest(
    platforms=["instagram", "youtube"],
    title="Scheduled Video",
    description="This is scheduled!",
    publish_at="2024-01-15T10:30:00Z"
)

job_id = schedule_publish("/path/to/video.mp4", request, "unique_id")

# Check scheduler status
status = get_scheduler_status()
print(f"Jobs pending: {status['jobs_pending']}")
```

### Job Management

```python
from scheduler import cancel_scheduled_job, reschedule_job

# Cancel a job
cancelled = cancel_scheduled_job("job_id_123")

# Reschedule a job
from datetime import datetime
new_time = datetime(2024, 1, 15, 11, 0, 0)
rescheduled = reschedule_job("job_id_123", new_time)
```

## 🏭 Production Considerations

### Token Management

- **Secure Storage**: Use HashiCorp Vault or AWS KMS for tokens
- **Auto-refresh**: Implement automatic token refresh before expiry
- **Rotation**: Regular token rotation for security

### Rate Limits & Retries

- **Exponential Backoff**: Implement retry logic with exponential backoff
- **Rate Limit Handling**: Respect platform rate limits
- **Queue Management**: Use Redis or similar for job queuing

### Media Hosting

For platforms requiring public URLs:

```python
# Example: Upload to S3 first, then use signed URL
import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(file_path):
    s3 = boto3.client('s3')
    bucket_name = 'your-bucket'
    key = f"videos/{os.path.basename(file_path)}"

    s3.upload_file(file_path, bucket_name, key)
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600  # 1 hour
    )
    return url
```

### Quality Checks

```python
from moviepy.editor import VideoFileClip

def validate_video(file_path):
    """Validate video before uploading"""
    try:
        clip = VideoFileClip(file_path)

        # Check duration (e.g., max 60 seconds for reels)
        if clip.duration > 60:
            raise ValueError("Video too long for reels")

        # Check resolution
        if clip.size[0] < 720 or clip.size[1] < 720:
            raise ValueError("Video resolution too low")

        clip.close()
        return True

    except Exception as e:
        raise ValueError(f"Video validation failed: {e}")
```

### Logging & Monitoring

```python
import structlog
import sentry_sdk

# Initialize structured logging
logger = structlog.get_logger()

# Initialize Sentry for error tracking
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

# Log important events
logger.info("Video uploaded successfully", platform="instagram", media_id="123")
```

### Human-in-the-Loop

For initial launches, consider adding approval steps:

```python
# Example: Slack notification before publishing
import requests

def notify_slack(message):
    webhook_url = os.getenv("SLACK_WEBHOOK")
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

# In your upload flow
notify_slack(f"New video ready for approval: {publish_id}")
# Wait for approval before actual publishing
```

## 🔧 Troubleshooting

### Common Issues

#### Authentication Errors

**Problem**: `Invalid access token` or `Authentication failed`

**Solutions**:
1. Verify token scopes match requirements
2. Check token expiration and refresh if needed
3. Ensure correct token type (user vs page token)

#### Upload Failures

**Problem**: `Upload failed` or `Media processing error`

**Solutions**:
1. Check video format and size requirements
2. Verify file path and permissions
3. Check network connectivity and API status

#### Scheduling Issues

**Problem**: Jobs not executing or stuck in pending

**Solutions**:
1. Check scheduler status: `GET /health`
2. Verify APScheduler configuration
3. Check system timezone settings

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m uvicorn app:app --reload --log-level debug
```

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Check platform configurations
curl http://localhost:8000/platforms
```

### Log Locations

- **Application logs**: Check your logging configuration
- **Scheduler logs**: Integrated with main application logs
- **Error logs**: Sent to configured logging service

## 📝 API Reference

### Models

#### PublishRequest
```typescript
{
  platforms: string[],           // Required: ["instagram", "youtube", etc.]
  title: string,                 // Optional: Video title
  description: string,           // Optional: Video description
  publish_at?: string,          // Optional: ISO datetime for scheduling
  captions?: Record<string, string>, // Optional: Platform-specific captions
  voice_to_text?: boolean,       // Optional: Enable voice-to-text
  tags?: string[]               // Optional: Video tags
}
```

#### PlatformResult
```typescript
{
  platform: string,              // Platform name
  status: "success" | "error",   // Upload status
  media_id?: string,             // Platform media ID
  post_id?: string,              // Platform post ID
  url?: string,                  // Direct link to content
  error_message?: string,        // Error details if failed
  metadata?: Record<string, any> // Additional platform data
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review platform-specific documentation

## 🔄 Updates and Changes

This service is designed to handle API changes gracefully:
- Platform APIs change often - monitor for updates
- Use official SDKs when available
- Test on sandbox accounts before production
- Respect platform Terms of Service and rate limits

---

**Note**: Always test thoroughly on sandbox/test accounts before deploying to production. Platform APIs evolve rapidly, so keep dependencies updated and monitor for deprecation notices.