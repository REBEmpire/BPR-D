# Avatar Frame Extraction Guide

**Purpose**: Extract the most visually appealing, intriguing, aesthetically striking frames from each agent's video for use as GitHub avatars.

**Videos to Process**:
- `_agents/grok/Grok Boss Babe.mp4`
- `_agents/claude/Professor Claude.mp4`
- `_agents/abacus/Deep Agent.mp4`
- `_agents/gemini/Gemini Chick.mp4`

---

## Option 1: Using FFmpeg (Recommended if you have it installed)

### Installation
```bash
# Mac
brew install ffmpeg

# Windows (via chocolatey)
choco install ffmpeg

# Windows (via scoop)
scoop install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

### Extract Multiple Frames from Each Video

```bash
# For Grok
ffmpeg -i "_agents/grok/Grok Boss Babe.mp4" -vf fps=1/5 "_agents/grok/frames/grok-frame_%03d.png"

# For Claude
ffmpeg -i "_agents/claude/Professor Claude.mp4" -vf fps=1/5 "_agents/claude/frames/claude-frame_%03d.png"

# For Abacus
ffmpeg -i "_agents/abacus/Deep Agent.mp4" -vf fps=1/5 "_agents/abacus/frames/abacus-frame_%03d.png"

# For Gemini
ffmpeg -i "_agents/gemini/Gemini Chick.mp4" -vf fps=1/5 "_agents/gemini/frames/gemini-frame_%03d.png"
```

This extracts 1 frame every 5 seconds, creating a series of images you can review.

### Extract Just the Best Frame (if you know the timestamp)

Once you've reviewed and selected a frame, extract just that one:

```bash
# Extract frame at 00:01:23 (1 minute 23 seconds)
ffmpeg -i "input.mp4" -ss 00:01:23 -vf scale=256:256 -vframes 1 "output.png"

# Or extract at frame number (if you know it)
ffmpeg -i "input.mp4" -vf select='eq(n\,50)' -vframes 1 output.png
```

---

## Option 2: Using Python with moviepy (If you prefer)

### Installation
```bash
pip install moviepy Pillow
```

### Python Script to Extract Frames

```python
#!/usr/bin/env python3
"""Extract frames from agent videos for avatar selection."""

from moviepy.editor import VideoFileClip
from pathlib import Path
import os

# Configuration
VIDEOS = {
    'grok': '_agents/grok/Grok Boss Babe.mp4',
    'claude': '_agents/claude/Professor Claude.mp4',
    'abacus': '_agents/abacus/Deep Agent.mp4',
    'gemini': '_agents/gemini/Gemini Chick.mp4'
}

# Extract every N seconds (adjust to get 10-15 frames per video)
FRAME_INTERVAL = 5  # seconds

def extract_frames(video_path, agent_name, output_dir):
    """Extract frames from video at regular intervals."""
    print(f"\nProcessing {agent_name}...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        print(f"  Duration: {duration:.1f} seconds")

        frame_count = 0
        t = 0
        while t < duration:
            frame = clip.get_frame(t)
            output_path = f"{output_dir}/{agent_name}_frame_{frame_count:03d}_{t:.1f}s.png"

            # Convert numpy array to image and save
            from PIL import Image
            import numpy as np
            img = Image.fromarray((frame * 255).astype(np.uint8))
            img.save(output_path)

            print(f"  Extracted: {output_path}")
            frame_count += 1
            t += FRAME_INTERVAL

        clip.close()
        print(f"  Total frames extracted: {frame_count}")

    except Exception as e:
        print(f"  ERROR: {e}")

# Extract all frames
for agent, video_path in VIDEOS.items():
    output_dir = f"_agents/{agent}/frames"
    if os.path.exists(video_path):
        extract_frames(video_path, agent, output_dir)
    else:
        print(f"Video not found: {video_path}")

print("\n✅ Frame extraction complete!")
print("Review the extracted frames and select the best one for each agent.")
```

---

## Option 3: Manual Video Player Review

1. Open each `.mp4` file in your video player (Windows Media Player, VLC, QuickTime, etc.)
2. Pause on frames that look:
   - **Aesthetically striking** - Good lighting, composition, visual interest
   - **Character-defining** - Shows the agent's personality or iconic pose
   - **Avatar-suitable** - Clear face/figure, good framing for a profile pic
3. Note the timestamp or frame number where the best image occurs
4. Use FFmpeg to extract that specific frame (see examples above)

---

## Selection Criteria for Each Agent

### **Grok** - "Elizabeth Hurley Energy"
Look for:
- Sharp, commanding presence
- Professional/polished appearance
- Confident pose or gaze
- Good lighting on face and attire
- Raven black hair visible
- Executive/boardroom aesthetic

### **Claude** - "Distinguished Professor Wizard"
Look for:
- Warm, thoughtful expression
- Wise or contemplative gaze
- Professor or scholar-like presentation
- Approachable but intelligent demeanor
- Possibly robes or scholarly attire
- Good lighting to show facial features

### **Abacus** - "Mad Scientist / Deep Agent"
Look for:
- Weathered, mysterious appearance
- Contemplative or intense expression
- Inventor/workshop aesthetic
- Possibly goggles or technical gear
- Sharp, analytical look
- Character and intrigue in the face

### **Gemini** - "Hacker Programmer Chick"
Look for:
- Confident, energetic expression
- Tech-casual appearance
- Youthful, smart look
- Possibly with multiple monitors or coding environment
- Confident pose
- Modern, relevant aesthetic

---

## Once You've Selected Your Frames

### Save to Local Folder
```bash
# Copy the selected frame to the agents folder (next to the MP4)
cp "_agents/[agent]/frames/best_frame.png" "_agents/[agent]/[agent]-avatar.png"
```

### Save to GitHub
```bash
# 1. Copy the avatar PNG to GitHub repo
cp "_agents/[agent]/[agent]-avatar.png" "C:\path\to\BPR-D\repo\web\public\avatars\[agent].png"

# 2. Commit to GitHub
cd C:\path\to\BPR-D\repo
git add "web/public/avatars/*.png"
git commit -m "Update agent avatars with video frame extracts"
git push
```

---

## Frame Extraction Commands Reference

### Extract 1 frame every 5 seconds (good overview)
```bash
ffmpeg -i video.mp4 -vf fps=1/5 frame_%03d.png
```

### Extract frame at specific time
```bash
ffmpeg -i video.mp4 -ss 00:00:15 -vframes 1 frame.png
```

### Extract frame at specific frame number
```bash
ffmpeg -i video.mp4 -vf select='eq(n\,100)' -vframes 1 frame.png
```

### Resize to avatar size while extracting
```bash
ffmpeg -i video.mp4 -ss 00:00:15 -vf scale=256:256 -vframes 1 frame.png
```

### Extract multiple sizes
```bash
# Full size
ffmpeg -i video.mp4 -ss 00:00:15 -vframes 1 frame-full.png

# Avatar size (256x256)
ffmpeg -i video.mp4 -ss 00:00:15 -vf scale=256:256 -vframes 1 frame-256.png

# Thumbnail size (128x128)
ffmpeg -i video.mp4 -ss 00:00:15 -vf scale=128:128 -vframes 1 frame-128.png
```

---

## Workflow Summary

1. **Extract frames** from all 4 videos (use Option 1, 2, or 3 above)
2. **Review frames** - Open output folder and view all extracted images
3. **Select best** - Choose the most visually appealing frame for each agent
4. **Verify quality** - Ensure good resolution, lighting, and aesthetic
5. **Rename files**:
   - `grok.png`
   - `claude.png`
   - `abacus.png`
   - `gemini.png`
6. **Save locally** - Place next to corresponding .mp4 files:
   - `_agents/grok/grok.png`
   - `_agents/claude/claude.png`
   - `_agents/abacus/abacus.png`
   - `_agents/gemini/gemini.png`
7. **Save to GitHub** - Add to `web/public/avatars/`:
   - `web/public/avatars/grok.png`
   - `web/public/avatars/claude.png`
   - `web/public/avatars/abacus.png`
   - `web/public/avatars/gemini.png`
8. **Commit** - Push to GitHub with message: "Update agent avatars from video frames"

---

## Tips

- **Don't spend too long** - The first "good" frame is usually fine
- **Lighting matters** - Well-lit frames look better as avatars
- **Face visibility** - Make sure faces are clearly visible and in good focus
- **Consistent styling** - Try to get similar composition/framing for all 4
- **Test in browser** - After uploading to GitHub, verify they display correctly at bpr-d.onrender.com/team

---

## Troubleshooting

**FFmpeg not found**: Install it (see Installation section above)

**Video file corrupt**: Try opening in VLC first to verify it plays

**Frames come out blurry**: The source video may be low quality, or you're extracting at a key moment. Try different timestamps.

**Wrong aspect ratio**: Use `-vf scale=256:256` with `:force_original_aspect_ratio=decrease:pad=256:256` to maintain aspect ratio while filling space

---

**Next Steps**:
1. Extract frames from videos
2. Review and select best frame for each agent
3. Save locally and to GitHub (see paths above)
4. Verify display on website
5. Report back with avatar image links

Let me know if you need help with any step!
