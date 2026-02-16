import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from crewai import LLM
from config import settings

def test_llm(name, llm_instance):
    print(f"\nTesting {name}...")
    try:
        response = llm_instance.call("Say 'Hello' and nothing else.")
        print(f"✅ {name} Success: {response}")
        return True
    except Exception as e:
        print(f"❌ {name} Failed: {e}")
        return False

def verify_all():
    print("Verifying LLM Connections...")

    results = {}

    # 1. Grok
    try:
        grok = LLM(
            model="grok-4-1-fast-reasoning",
            api_key=settings.XAI_API_KEY,
            base_url="https://api.x.ai/v1"
        )
        if not test_llm("Grok", grok):
             print("⚠️  Trying Grok fallback (grok-2)...")
             grok_fb = LLM(
                model="grok-2",
                api_key=settings.XAI_API_KEY,
                base_url="https://api.x.ai/v1"
             )
             results["grok"] = test_llm("Grok (Fallback)", grok_fb)
        else:
            results["grok"] = True
    except Exception as e:
        print(f"❌ Grok Setup Failed: {e}")
        results["grok"] = False

    # 2. Claude
    try:
        claude = LLM(
            model="anthropic/claude-sonnet-4-5-20250929",
            api_key=settings.ANTHROPIC_API_KEY
        )
        if not test_llm("Claude", claude):
             print("⚠️  Trying Claude fallback (claude-3-5-sonnet-20240620)...")
             claude_fb = LLM(
                model="anthropic/claude-3-5-sonnet-20240620",
                api_key=settings.ANTHROPIC_API_KEY
             )
             results["claude"] = test_llm("Claude (Fallback)", claude_fb)
        else:
            results["claude"] = True
    except Exception as e:
        print(f"❌ Claude Setup Failed: {e}")
        results["claude"] = False

    # 3. Gemini
    try:
        gemini = LLM(
            model="gemini/gemini-3-pro-preview", # Updated model ID
            api_key=settings.GEMINI_API_KEY
        )
        if not test_llm("Gemini (3 Pro Preview)", gemini):
             print("⚠️  Trying Gemini fallback (gemini/gemini-3-flash-preview)...")
             gemini_fb = LLM(
                model="gemini/gemini-3-flash-preview",
                api_key=settings.GEMINI_API_KEY
             )
             results["gemini"] = test_llm("Gemini (3 Flash Preview)", gemini_fb)
        else:
            results["gemini"] = True
    except Exception as e:
        print(f"❌ Gemini Setup Failed: {e}")
        results["gemini"] = False

    # 4. Abacus
    if settings.ABACUS_PRIMARY_KEY:
        try:
            abacus = LLM(
                model="qwen3-max",
                api_key=settings.ABACUS_PRIMARY_KEY,
                base_url="https://routellm.abacus.ai/v1",
                max_tokens=4000
            )
            results["abacus"] = test_llm("Abacus", abacus)
        except Exception as e:
            print(f"❌ Abacus Setup Failed: {e}")
            results["abacus"] = False
    else:
        print("\nSkipping Abacus (No Key)")
        results["abacus"] = None

    print("\n--- Summary ---")
    for k, v in results.items():
        status = "✅ PASS" if v else "❌ FAIL" if v is not None else "⚪ SKIP"
        print(f"{k.capitalize()}: {status}")

if __name__ == "__main__":
    verify_all()
