import os
import sys
from pathlib import Path
import google.generativeai as genai

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

print("Listing available Gemini models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
