#!/usr/bin/env python3
"""
Aetherial Image Transmuter — DUAL image generation pipeline.

Generates images using BOTH:
1. Grok Imagine (via XAI_API_KEY) — The Sovereign Flame's vision
2. Abacus/Deep Agent — The Alchemist's celestial interpretation

Images are saved to assets/aetherial_images/[date]/grok/ and /abacus/
for comparison during the testing phase.
"""

import asyncio
import base64
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp

# --- Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "aetherial_images"

logger = logging.getLogger("aetherial-image-transmuter")


def get_xai_api_key() -> Optional[str]:
    """Get XAI API key from environment."""
    return os.getenv("XAI_API_KEY")


def get_abacus_api_key() -> Optional[str]:
    """Get Abacus API key from environment."""
    return os.getenv("ABACUS_PRIMARY_KEY") or os.getenv("ABACUS_API_KEY")


def parse_prompts_file(prompts_path: str) -> list[dict]:
    """Parse the image_prompts.md file into structured prompts."""
    prompts = []
    
    with open(prompts_path, "r") as f:
        content = f.read()
    
    # Split by ## headers
    sections = re.split(r"^## ", content, flags=re.MULTILINE)
    
    for section in sections[1:]:  # Skip the title section
        lines = section.strip().split("\n")
        if not lines:
            continue
        
        name = lines[0].strip()
        prompt = ""
        filename = ""
        usage = ""
        
        for line in lines[1:]:
            if line.startswith("**Prompt:**"):
                prompt = line.replace("**Prompt:**", "").strip()
            elif line.startswith("**File Name:**"):
                filename = line.replace("**File Name:**", "").strip().strip("`")
            elif line.startswith("**Usage:**"):
                usage = line.replace("**Usage:**", "").strip()
        
        if prompt:
            prompts.append({
                "name": name,
                "prompt": prompt,
                "filename": filename,
                "usage": usage,
            })
    
    return prompts


async def generate_grok_image(
    prompt: str,
    output_path: Path,
    dry_run: bool = False,
) -> Optional[str]:
    """Generate an image using Grok Imagine (XAI API)."""
    api_key = get_xai_api_key()
    
    if not api_key:
        logger.warning("XAI_API_KEY not set — skipping Grok image generation")
        return None
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would generate Grok image: {output_path.name}")
        # Create placeholder
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"[DRY-RUN PLACEHOLDER]\nPrompt: {prompt[:100]}...")
        return str(output_path)
    
    url = "https://api.x.ai/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "grok-2-image",
        "prompt": prompt,
        "n": 1,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Grok API error: {response.status} - {error_text}")
                    return None
                
                data = await response.json()
                
                # Extract image data
                if "data" in data and len(data["data"]) > 0:
                    image_data = data["data"][0]
                    
                    # Handle URL or base64 response
                    if "url" in image_data:
                        # Download from URL
                        async with session.get(image_data["url"]) as img_response:
                            img_bytes = await img_response.read()
                    elif "b64_json" in image_data:
                        img_bytes = base64.b64decode(image_data["b64_json"])
                    else:
                        logger.error("Unexpected Grok response format")
                        return None
                    
                    # Save image
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(img_bytes)
                    logger.info(f"Grok image saved: {output_path}")
                    return str(output_path)
                
    except Exception as e:
        logger.error(f"Grok image generation failed: {e}")
    
    return None


async def generate_abacus_image(
    prompt: str,
    output_path: Path,
    dry_run: bool = False,
) -> Optional[str]:
    """Generate an image using Abacus AI with persona influence."""
    api_key = get_abacus_api_key()
    
    if not api_key:
        logger.warning("ABACUS_PRIMARY_KEY not set — skipping Abacus image generation")
        return None
    
    # Enhance prompt with Alchemist persona
    enhanced_prompt = f"""
[The Weaver of Celestial Calculations interprets:]
{prompt}

Style notes: Infuse with celestial mathematics, sacred geometry undertones,
and the wisdom of transmutation. The image should feel like it emerged
from the Alchemist's workshop — precise yet mystical.
""".strip()
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would generate Abacus image: {output_path.name}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"[DRY-RUN PLACEHOLDER]\nPrompt: {enhanced_prompt[:100]}...")
        return str(output_path)
    
    # Use Abacus AI image generation
    # Note: This uses the RouteLLM endpoint with image generation capability
    url = "https://i.ytimg.com/vi/_0jEH700GLw/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLCReRJP0kxuHo87AIzaarumio8zMA"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "flux-dev",  # Abacus image model
        "prompt": enhanced_prompt,
        "n": 1,
        "size": "1024x1024",
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Abacus API error: {response.status} - {error_text}")
                    return None
                
                data = await response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    image_data = data["data"][0]
                    
                    if "url" in image_data:
                        async with session.get(image_data["url"]) as img_response:
                            img_bytes = await img_response.read()
                    elif "b64_json" in image_data:
                        img_bytes = base64.b64decode(image_data["b64_json"])
                    else:
                        logger.error("Unexpected Abacus response format")
                        return None
                    
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(img_bytes)
                    logger.info(f"Abacus image saved: {output_path}")
                    return str(output_path)
                    
    except Exception as e:
        logger.error(f"Abacus image generation failed: {e}")
    
    return None


async def transmute_images(
    prompts_path: str,
    dry_run: bool = False,
) -> dict:
    """Transmute all image prompts using DUAL generation.
    
    Args:
        prompts_path: Path to image_prompts.md file
        dry_run: If True, create placeholders instead of calling APIs
    
    Returns:
        dict with paths to generated images
    """
    result = {
        "success": False,
        "paths": [],
        "grok_paths": [],
        "abacus_paths": [],
        "errors": [],
    }
    
    # Parse prompts
    try:
        prompts = parse_prompts_file(prompts_path)
    except Exception as e:
        result["errors"].append(f"Failed to parse prompts: {e}")
        return result
    
    if not prompts:
        result["errors"].append("No prompts found in file")
        return result
    
    logger.info(f"Found {len(prompts)} image prompts to transmute")
    
    # Create dated output directories
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    grok_dir = ASSETS_DIR / date_str / "grok"
    abacus_dir = ASSETS_DIR / date_str / "abacus"
    
    grok_dir.mkdir(parents=True, exist_ok=True)
    abacus_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate images for each prompt
    for i, prompt_data in enumerate(prompts):
        name = prompt_data["name"].lower().replace(" ", "-").replace(":", "")
        prompt = prompt_data["prompt"]
        
        # Generate filename
        safe_name = re.sub(r"[^a-z0-9-]", "", name)[:50]
        filename = f"{safe_name}.png"
        
        logger.info(f"Transmuting image {i+1}/{len(prompts)}: {name}")
        
        # Generate with Grok
        grok_path = grok_dir / filename
        grok_result = await generate_grok_image(prompt, grok_path, dry_run=dry_run)
        if grok_result:
            result["grok_paths"].append(grok_result)
            result["paths"].append(grok_result)
        
        # Generate with Abacus
        abacus_path = abacus_dir / filename
        abacus_result = await generate_abacus_image(prompt, abacus_path, dry_run=dry_run)
        if abacus_result:
            result["abacus_paths"].append(abacus_result)
            result["paths"].append(abacus_result)
        
        # Small delay between API calls
        if not dry_run:
            await asyncio.sleep(1)
    
    result["success"] = len(result["paths"]) > 0
    return result


async def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Aetherial Image Transmuter — DUAL image generation"
    )
    parser.add_argument(
        "--prompts",
        type=str,
        default="publishing/hive/drafts/image_prompts.md",
        help="Path to image prompts file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create placeholders instead of calling APIs",
    )
    
    args = parser.parse_args()
    
    prompts_path = PROJECT_ROOT / args.prompts
    if not prompts_path.exists():
        print(f"Prompts file not found: {prompts_path}")
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO)
    
    result = await transmute_images(
        prompts_path=str(prompts_path),
        dry_run=args.dry_run,
    )
    
    print("\n" + "=" * 50)
    print("AETHERIAL IMAGE TRANSMUTER — REPORT")
    print("=" * 50)
    print(f"Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Grok images: {len(result['grok_paths'])}")
    print(f"Abacus images: {len(result['abacus_paths'])}")
    if result["errors"]:
        print(f"Errors: {result['errors']}")
    print("=" * 50)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
