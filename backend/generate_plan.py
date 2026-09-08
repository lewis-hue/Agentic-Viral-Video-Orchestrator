from google import genai
from google.genai import types
import base64
import os

def generate():
  client = genai.Client(
      vertexai=True,
      api_key=os.environ.get("GOOGLE_CLOUD_API_KEY"),
  )

  msg1_text1 = types.Part.from_text(text="""This is how my application works \"Video Generation: Your app generates videos as before
Public Upload: Videos are uploaded to a public URL (Cloudinary/S3)
Scheduling: Instead of direct API calls, the app sends a single POST to your Zapier webhook with:
Caption/description
Public video URL
Target platform profile IDs
Scheduled time (ISO 8601 format)
Zapier Processing: Zapier catches the data and uses Buffer's API to upload and schedule the post
Multi-Platform: One request handles YouTube, Instagram, and TikTok simultaneously
📋 Next Steps for You
Set Up Zapier:

Follow the plan to create your Zapier webhook
Connect it to Buffer's \"Create Schedule Update\" action
Map the fields as described in the plan
\" Here are my details \"# Zapier and Buffer Integration
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/25100574/ur02hls/
YOUTUBE_PROFILE_ID=68fa3ea1669affb4c9823ad9
INSTAGRAM_PROFILE_ID=68fa3d94669affb4c982391f
TIKTOK_PROFILE_ID=68fa5447669affb4c9826de0

# Media Upload for Public URLs
MEDIA_UPLOAD_SERVICE=cloudinary  # Options: cloudinary, s3, etc.
CLOUDINARY_URL=cloudinary://478181443685777:0cEIbeHBk7Hw5SVn_hY_U5GLp4g@dp33x3kna
\" Can you create in JSON format, a plan to publish and schedule posts on Instagram, TikTok, and YouTube from my application?""")

  model = "gemini-2.5-flash-image"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_text1
      ]
    ),
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    seed = 0,
    max_output_tokens = 32768,
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
  )

  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    print(chunk.text, end="")

generate()