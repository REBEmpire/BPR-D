#!/usr/bin/env python3
"""
Extract key frames from agent MP4 videos and save as PNG avatars.
"""

import cv2
import os

# Agent video mappings
VIDEOS = {
    'grok': "_agents/grok/Grok Boss Babe.mp4",
    'claude': "_agents/claude/Professor Claude.mp4",
    'abacus': "_agents/abacus/Deep Agent.mp4",
    'gemini': "_agents/gemini/Gemini Chick.mp4"
}

OUTPUT_DIR = "web/public/avatars"

def extract_frame(video_path, output_path, time_sec=1.0):
    """Extract a frame at the specified time from video."""
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return False

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Could not open video: {video_path}")
        return False

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(time_sec * fps)

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(output_path, frame)
        print(f"Extracted frame to: {output_path}")
        cap.release()
        return True
    else:
        print(f"Could not read frame at {time_sec}s from {video_path}")
        cap.release()
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for agent, video_path in VIDEOS.items():
        output_path = os.path.join(OUTPUT_DIR, f"{agent}.png")
        print(f"Processing {agent}...")
        success = extract_frame(video_path, output_path)
        if not success:
            print(f"Failed to extract frame for {agent}")

if __name__ == "__main__":
    main()