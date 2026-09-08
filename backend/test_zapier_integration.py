"""
Test script for Zapier integration

This script tests the Zapier webhook POST request with sample data.
Ensure .env file is configured with actual values before running.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.zapier_service import schedule_post_via_zapier

def test_zapier_integration():
    """Test the Zapier integration with sample JSON payload"""

    # Sample JSON payload matching the schema
    payload = {
        "video": {
            "url": "https://res.cloudinary.com/dp33x3kna/video/upload/v1761437364/gk6wkm9erc1wa9gvuwfp.mp4",
            "title": "Amazing AI Video",
            "description": "Check out this amazing new video created by my AI-powered application! #AI #Automation",
            "hashtags": ["AI", "Automation", "Video"],
            "duration": 45,
            "platforms": {
                "tiktok": {
                    "enabled": True,
                    "content_type": "post",
                    "caption": "Amazing AI video! #AI #Automation",
                    "hashtags": ["AI", "Automation"],
                    "schedule": {
                        "type": "scheduled",
                        "datetime": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
                    }
                },
                "instagram": {
                    "enabled": True,
                    "content_type": "reel",
                    "caption": "Check out this video! #AI #Automation",
                    "hashtags": ["AI", "Automation"],
                    "share_to_feed": True,
                    "schedule": {
                        "type": "scheduled",
                        "datetime": (datetime.now(timezone.utc) + timedelta(hours=2, minutes=5)).isoformat()
                    }
                },
                "youtube": {
                    "enabled": True,
                    "content_type": "short",
                    "title": "Amazing AI Video",
                    "description": "Check out this amazing new video!",
                    "tags": ["AI", "Automation", "Video"],
                    "visibility": "public",
                    "category": "24",
                    "made_for_kids": False,
                    "schedule": {
                        "type": "scheduled",
                        "datetime": (datetime.now(timezone.utc) + timedelta(hours=2, minutes=10)).isoformat()
                    }
                }
            },
            "global_settings": {
                "default_schedule_offset": {
                    "tiktok_offset_minutes": 0,
                    "instagram_offset_minutes": 5,
                    "youtube_offset_minutes": 10
                }
            }
        },
        "metadata": {
            "source": "video_editor_app",
            "user_id": "test_user",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }

    print("Testing Zapier Integration...")
    print(f"ZAPIER_WEBHOOK_URL: {os.getenv('ZAPIER_WEBHOOK_URL')}")
    print(f"Payload: {payload}")

    # Call the function
    result = schedule_post_via_zapier(payload)

    print("\nResult:")
    print(result)

    if result["status"] == "success":
        print("✅ Test successful! Check your Zapier webhook for the scheduled post.")
    else:
        print("❌ Test failed. Check the error message and ensure .env is configured correctly.")

if __name__ == "__main__":
    # Note: Ensure .env file is configured with actual values
    # If using dotenv, uncomment the lines below
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")

    test_zapier_integration()