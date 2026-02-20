# DDAS Video & Audio Production Pipeline

Complete guide for setting up automated video and audio content production for YouTube, Substack, and podcasts.

## Project Overview

**Goal**: Distribute daily written content across video (YouTube) and audio (Podcasts) platforms to maximize reach and Hive rewards.

**Target Output**:
- **YouTube**: 1 video per day (game footage + narration)
- **Podcast**: 2-3 episodes per week (audio articles)
- **Substack**: Cross-post written content with video embeds
- **Hive**: 5+ articles daily (written content)

## Tech Stack

### Video Production
- **Video Editor**: DaVinci Resolve (free version) or OpenShot
- **Screen Recording**: OBS Studio (free, open-source)
- **Video Processing**: FFmpeg (free, open-source)
- **Thumbnail Generator**: Stable Diffusion or custom Python script
- **Upload Automation**: YouTube Data API v3

### Audio Production
- **Audio Editor**: Audacity (free, open-source)
- **Text-to-Speech**: ElevenLabs API or Google Cloud TTS (free tier)
- **Podcast Hosting**: Anchor/Spotify for Podcasters (free)
- **Podcast Publishing**: RSS feed generation

### Content Management
- **Game Recording**: Godot's built-in recording + OBS
- **Asset Management**: Organized folder structure
- **Workflow Coordination**: Python orchestration scripts

## Video Production Pipeline

### Step 1: Capture Game Footage

#### Option A: OBS Studio (Recommended for live recording)

1. **Install OBS Studio**: https://obsproject.com/
2. **Configure Sources**:
   - Game window: Add "Window Capture" or "Game Capture"
   - Microphone: Add audio input
   - Desktop audio: Capture game sounds

3. **Recording Settings**:
   ```
   Resolution: 1920x1080 (1080p)
   Framerate: 60 FPS
   Encoder: NVIDIA/AMD/CPU (based on system)
   Bitrate: 5000-8000 kbps
   Format: MP4
   ```

4. **Start Recording**: Press "Start Recording" button

#### Option B: Godot's Built-in Recording

```gdscript
# In your game scene
extends Node

func _ready():
    # Record gameplay directly
    get_tree().root.debug_draw_fps = true

func start_video_capture():
    # Use ffmpeg to capture Godot window
    OS.execute("ffmpeg", [
        "-f", "gdigrab",
        "-framerate", "60",
        "-i", "desktop",
        "-c:v", "libx264",
        "-crf", "23",
        f"gameplay_{OS.get_ticks_msec()}.mp4"
    ])
```

### Step 2: Script & Narrate

#### Create Video Script

```markdown
# Video: "Splinterlands Civilization - Devlog Update"

## Hook (0-10 seconds)
"Welcome back to DDAS! This week we made major progress on the
civilization system. Let's see what's new..."

## Body (10-60 seconds)
- Show game footage of new features
- Explain mechanics
- Highlight challenges and solutions
- Show community reactions

## Call-to-Action (50-60 seconds)
"If you enjoy game development content, don't forget to:
- Subscribe for weekly updates
- Check out our articles on Hive
- Join our Discord community"

## Outro (60-70 seconds)
"Thanks for watching! See you next time!"
```

#### Generate Narration Audio

**Option A: Text-to-Speech (Fastest)**

```python
from google.cloud import texttospeech

def generate_narration(script_text: str, output_file: str):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=script_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-A"  # High-quality voice
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)
```

**Option B: AI Voice (Better Quality)**

- ElevenLabs: https://elevenlabs.io/ (20,000 characters free/month)
- Google Cloud TTS: Free tier available
- Azure TTS: Enterprise solution

**Option C: Human Narration (Best Quality)**

- Record yourself: Use good microphone, quiet room
- Hire voice actor: Fiverr, Upwork (~$50-200 per video)

### Step 3: Edit Video

#### Using DaVinci Resolve (Free)

1. **Create New Project**: File → New Project
2. **Import Assets**:
   - Game footage (MP4)
   - Narration audio (MP3)
   - Background music (MP3)
   - Thumbnail image

3. **Timeline Editing**:
   ```
   Video Track 1: Game footage
   Video Track 2: Transitions, overlays
   Audio Track 1: Narration
   Audio Track 2: Background music/SFX
   ```

4. **Add Cuts & Transitions**:
   - Cut between game scenes on key story beats
   - Add fade transitions (0.3-0.5 seconds)
   - Sync narration to gameplay

5. **Color Correction**:
   - Color tab → Lift, Gamma, Gain adjustments
   - Match game colors to branding

6. **Export Settings**:
   ```
   Format: MP4 (H.264)
   Resolution: 1920x1080
   Framerate: 60 FPS
   Bitrate: 8000-12000 kbps
   ```

#### Python Automation with FFmpeg

```python
import subprocess
import json

def create_video_with_ffmpeg(
    game_footage: str,
    narration_audio: str,
    background_music: str,
    output_file: str
):
    """Combine game footage, narration, and music"""

    # Create audio mix (narration + background music)
    subprocess.run([
        "ffmpeg",
        "-i", narration_audio,
        "-i", background_music,
        "-filter_complex", "[0:a]volume=1.0[a1];[1:a]volume=0.3[a2];[a1][a2]amix=inputs=2:duration=longest",
        "-c:a", "aac",
        f"audio_mix.aac"
    ])

    # Combine video and mixed audio
    subprocess.run([
        "ffmpeg",
        "-i", game_footage,
        "-i", "audio_mix.aac",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-crf", "23",
        output_file
    ])

    print(f"Video created: {output_file}")
```

### Step 4: Create Thumbnail

#### Stable Diffusion Image Generation

```python
def generate_thumbnail(prompt: str, output_file: str = "thumbnail.png"):
    """Generate thumbnail using Stable Diffusion"""

    from stability_sdk.client import StabilityClient

    client = StabilityClient(
        key="YOUR_STABILITY_KEY",
        engine_id="stable-diffusion-v1-6",
        verbose=True
    )

    resp = client.generate(
        prompt=prompt,
        steps=30,
        cfg_scale=12.0,
        width=1280,
        height=720,
        samples=1,
        sampler="k_dpmpp_2m"
    )

    for resp_data in resp:
        for img in resp_data.artifacts:
            img.save(output_file)
```

#### Custom Python Thumbnail Creator

```python
from PIL import Image, ImageDraw, ImageFont

def create_thumbnail(title: str, subtitle: str, output_file: str):
    """Create YouTube thumbnail (1280x720)"""

    # Create base image with gradient
    img = Image.new('RGB', (1280, 720), color='#1a1a1a')
    draw = ImageDraw.Draw(img)

    # Add title text
    title_font = ImageFont.truetype("arial.ttf", 80)
    draw.text((50, 100), title, fill='#FFFFFF', font=title_font)

    # Add subtitle
    subtitle_font = ImageFont.truetype("arial.ttf", 50)
    draw.text((50, 350), subtitle, fill='#FFD700', font=subtitle_font)

    # Add decorative box
    draw.rectangle([50, 600, 1230, 720], outline='#FFD700', width=5)

    img.save(output_file)
    print(f"Thumbnail created: {output_file}")

# Example usage
create_thumbnail(
    title="Splinterlands RPG",
    subtitle="New Dungeon System!",
    output_file="thumbnail.png"
)
```

### Step 5: Upload to YouTube

#### YouTube Data API Setup

1. **Enable YouTube API**:
   - Go to: https://console.cloud.google.com/
   - Create new project
   - Search for "YouTube Data API v3"
   - Click "Enable"
   - Create OAuth 2.0 credentials (Desktop app)
   - Download JSON file

2. **Install YouTube API Client**:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

#### Upload Script

```python
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
from datetime import datetime

class YouTubeUploader:
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = credentials_file
        self.youtube = self._authenticate()

    def _authenticate(self):
        """Authenticate with YouTube API"""
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)

        return build('youtube', 'v3', credentials=creds)

    def upload_video(
        self,
        file_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: str = "20",  # 20 = Gaming
        is_public: bool = False,  # Start as unlisted
        thumbnail_file: str = None,
        publish_at: datetime = None
    ) -> str:
        """Upload video to YouTube"""

        body = {
            'snippet': {
                'categoryId': category_id,
                'title': title,
                'description': description,
                'tags': tags,
                'defaultLanguage': 'en',
                'localized': {
                    'title': title,
                    'description': description
                }
            },
            'status': {
                'privacyStatus': 'public' if is_public else 'unlisted',
                'selfDeclaredMadeForKids': False
            }
        }

        if publish_at:
            # Schedule for future publish
            body['status']['publishAt'] = publish_at.isoformat() + 'Z'
            body['status']['privacyStatus'] = 'private'

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

        request = self.youtube.videos().insert(
            part='snippet,status,localizations',
            body=body,
            media_body=media
        )

        response = self._execute_with_exponential_backoff(request)
        video_id = response['id']

        # Upload thumbnail if provided
        if thumbnail_file:
            self._upload_thumbnail(video_id, thumbnail_file)

        return video_id

    def _upload_thumbnail(self, video_id: str, thumbnail_file: str):
        """Upload custom thumbnail"""
        request = self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_file)
        )
        request.execute()

    def _execute_with_exponential_backoff(self, request):
        """Execute request with retry logic"""
        import time
        import random

        for attempt in range(5):
            try:
                return request.execute()
            except Exception as e:
                if attempt < 4:
                    sleep_seconds = 2 ** attempt + random.random()
                    print(f"Retry in {sleep_seconds:.1f} seconds...")
                    time.sleep(sleep_seconds)
                else:
                    raise

# Usage
uploader = YouTubeUploader()
video_id = uploader.upload_video(
    file_path="final_video.mp4",
    title="Splinterlands Civ - Weekly Dev Update",
    description="""Weekly development update for DDAS games.

Watch our progress on:
- Splinterlands Civilization
- Slingerlands RPG

Support us on Hive: https://hive.blog/@ddas-news
Join our Discord: [link]
Subscribe for more updates!""",
    tags=["gamedev", "splinterlands", "game development", "civilization"],
    thumbnail_file="thumbnail.png"
)

print(f"Uploaded video: https://www.youtube.com/watch?v={video_id}")
```

## Audio/Podcast Production Pipeline

### Step 1: Generate Audio from Text

#### Using ElevenLabs (Best Quality)

```python
import requests
import json

def generate_podcast_audio(
    script: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
    output_file: str = "podcast.mp3"
):
    """Generate podcast audio using ElevenLabs API"""

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": "YOUR_ELEVENLABS_API_KEY"
    }

    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=data, headers=headers)

    with open(output_file, 'wb') as f:
        f.write(response.content)

    return output_file

# Example
podcast_audio = generate_podcast_audio("""
Welcome to the DDAS Weekly Podcast. This week we're discussing
the new combat system in Splinterlands Civilization...
""")
```

#### Using Google Cloud TTS (Free Tier)

```python
from google.cloud import texttospeech
import os

def generate_podcast_with_google(
    script: str,
    output_file: str = "podcast.mp3",
    voice_name: str = "en-US-Neural2-A",
    speaking_rate: float = 0.9
):
    """Generate podcast using Google Cloud TTS (free tier)"""

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=script)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate,
        pitch=0.0
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)

    return output_file

# Example
generate_podcast_with_google("""
Welcome to DDAS Weekly Podcast. Today we're discussing...
""")
```

### Step 2: Add Background Music & Effects

```python
import subprocess

def add_music_to_podcast(
    narration_file: str,
    music_file: str,
    output_file: str,
    music_volume: float = 0.2
):
    """Mix narration with background music"""

    subprocess.run([
        "ffmpeg",
        "-i", narration_file,
        "-i", music_file,
        "-filter_complex", f"[1:a]volume={music_volume}[a2];[0:a][a2]amix=inputs=2:duration=longest",
        "-c:a", "libmp3lame",
        "-q:a", "4",
        output_file
    ])

    print(f"Podcast with music created: {output_file}")

# Example
add_music_to_podcast(
    narration_file="podcast_narration.mp3",
    music_file="background_music.mp3",
    output_file="podcast_final.mp3",
    music_volume=0.15
)
```

### Step 3: Create Podcast RSS Feed

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>DDAS - Game Development Podcast</title>
    <link>https://ddas.example.com/podcast</link>
    <description>Weekly podcast covering game development, Hive blockchain,
    and the Splinterlands and Slingerlands universes.</description>
    <language>en-us</language>
    <itunes:category text="Technology"/>
    <itunes:category text="Games &amp; Hobbies"/>
    <itunes:author>DDAS</itunes:author>
    <itunes:explicit>false</itunes:explicit>

    <item>
      <title>Episode 1: Welcome to DDAS</title>
      <link>https://ddas.example.com/podcast/episode-1</link>
      <description>Introduction to the DDAS project and what's coming.</description>
      <pubDate>Mon, 12 Feb 2026 12:00:00 GMT</pubDate>
      <enclosure url="https://ddas.example.com/episodes/episode-1.mp3"
                  length="45823" type="audio/mpeg"/>
      <guid>https://ddas.example.com/podcast/episode-1</guid>
      <itunes:duration>25:30</itunes:duration>
    </item>
  </channel>
</rss>
```

### Step 4: Publish to Podcast Platforms

```python
def publish_to_anchor(
    email: str,
    password: str,
    episode_title: str,
    episode_description: str,
    audio_file: str
):
    """Publish to Spotify for Podcasters (Anchor)"""

    # Anchor now requires manual upload through web interface
    # Alternative: Use Anchor API if available or Transistor.fm

    print(f"""
    To publish to Spotify Podcasters:
    1. Go to podcasters.spotify.com
    2. Login with {email}
    3. Click "Upload Episode"
    4. Title: {episode_title}
    5. Description: {episode_description}
    6. Audio file: {audio_file}
    7. Click Publish

    Episode will be live within 24 hours.
    """)
```

## Automation Orchestrator

### Complete Daily Pipeline

```python
# content/automation/media_orchestrator.py

import subprocess
import os
from datetime import datetime
from content_generator import ContentGenerator
from hive_publisher import HivePublisher

class MediaOrchestrator:
    def __init__(self):
        self.generator = ContentGenerator()
        self.uploader = YouTubeUploader()

    def generate_daily_media(self):
        """Generate article, video, and podcast from single content source"""

        # 1. Generate written article
        article = self.generator.generate_content(today_prompt)
        print(f"✓ Article generated: {article['title']}")

        # 2. Create video
        narration = generate_podcast_audio(article['content'])
        game_footage = self.capture_gameplay()
        video = self.create_video(game_footage, narration)
        self.uploader.upload_video(video, article['title'], article['description'])
        print(f"✓ Video uploaded")

        # 3. Create podcast episode
        podcast = self.add_music_to_podcast(narration, "bg_music.mp3")
        self.publish_to_anchor(podcast, article['title'], article['description'])
        print(f"✓ Podcast published")

        # 4. Publish article to Hive
        self.publisher.publish_post(
            title=article['title'],
            content=article['content'],
            tags=article['tags']
        )
        print(f"✓ Article published to Hive")

    def capture_gameplay(self):
        """Capture game footage for video"""
        # Integration with OBS or direct Godot recording
        pass

    def create_video(self, footage, narration):
        # Uses FFmpeg or DaVinci Resolve
        pass
```

## Scheduling & Automation

### Cron Job for Daily Pipeline

```bash
#!/bin/bash
# daily_media.sh

cd /path/to/DDAS/content/automation

# Run complete media pipeline daily at 10 AM UTC
python media_orchestrator.py --generate-all --publish

# Log output
echo "$(date): Daily media pipeline complete" >> /var/log/ddas.log
```

Add to crontab:
```
0 10 * * * /path/to/daily_media.sh
```

## Budget Breakdown

### Monthly Costs (Realistic)

| Service | Cost | Notes |
|---------|------|-------|
| ElevenLabs TTS | $10-20 | 20K char/month free, then paid |
| YouTube (free) | $0 | Unlimited uploads |
| Spotify Podcasters | $0 | Free hosting |
| Stable Diffusion | $5-10 | Via Replicate or local GPU |
| Domain/Hosting | $5-10 | For RSS/website |
| **Total** | **$20-40** | Lean setup |

### Free Alternative Path

- Use Google Cloud TTS (free tier: 1M chars/month)
- Use open-source Stable Diffusion locally (requires GPU)
- Self-host podcast RSS feed
- Use OBS + FFmpeg for video production
- **Total**: $0-5/month (just infrastructure)

## Quality Tips

### For Better Videos
1. **B-roll**: Capture multiple angles of gameplay
2. **Pacing**: Match cuts to narration beats
3. **Thumbnails**: Test different designs, use A/B testing
4. **Titles**: Research trending keywords on YouTube
5. **Descriptions**: Include timestamps, links to Hive, Discord

### For Better Podcasts
1. **Script Quality**: Use generated content as draft, edit heavily
2. **Voice**: Test different TTS voices, pick most engaging
3. **Audio Levels**: Normalize audio to -3dB peak
4. **Music**: Use royalty-free music (YouTube Audio Library)
5. **Consistency**: Same upload day/time weekly

## Next Steps

1. **Set up YouTube channel**: Create DDAS channel
2. **Create Spotify Podcasters account**: For podcast distribution
3. **Install OBS/DaVinci**: For recording/editing
4. **Generate test video**: End-to-end test
5. **Schedule first episode**: Get pipeline running

---

**Status**: Planning Phase
**Last Updated**: 2026-02-12
**Next Review**: After Phase 1 game development

Ready to launch video and audio? Let's go!
