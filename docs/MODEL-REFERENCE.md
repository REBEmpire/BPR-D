# BPR&D Model Reference - Quick Guide

**Last Updated:** 2026-02-14

---

## Quick Model Selection

### By Agent Role

| Agent | Platform | Primary Model | Use For |
|-------|----------|---------------|---------|
| **Grok** | xAI | `grok-4-1-fast-reasoning` | Executive decisions, strategic planning, agentic workflows |
| **Claude** | Anthropic | `claude-opus-4-6` | Complex reasoning, architecture, long documents |
| **Gemini** | Google AI | `gemini-3-pro-preview` | Coding, multimodal tasks, compliance automation |
| **Abacus** | Abacus.AI | `abacus-deep-agent` | Adaptive routing, innovation, accessing all models |

---

## Quick Access: Model IDs for API Calls

### xAI (Grok)
```python
# Recommended for BPR&D
"grok-4-1-fast-reasoning"  # Best for agentic work, 2M context
"grok-code-fast-1"         # Best for coding, 256K context

# Alternatives
"grok-3"                   # Current stable
"grok-3-fast"              # Faster variant
"grok-3-mini"              # Efficient
```

### Anthropic (Claude)
```python
# Recommended for BPR&D
"claude-opus-4-6"          # Most capable
"claude-sonnet-4-5-20250929"  # Fast general-purpose

# Alternatives
"claude-haiku-4-5-20251001"   # High-volume, cost-effective
```

### Google AI (Gemini)
```python
# Recommended for BPR&D
"gemini-3-pro-preview"     # Best for coding + reasoning, 1M context
"gemini-3-flash-preview"   # Fast multimodal

# Alternatives (stable/production)
"gemini-2.5-pro-preview-05-06"   # Code improvements
"gemini-2.5-flash-preview-04-17" # Price-performance
"gemini-2.5-flash-lite"          # High-volume
```

### Abacus.AI (Unified Access)
```python
# Recommended - Auto-routing
"abacus-deep-agent"        # Routes to best model automatically

# Direct access to all major models
"claude-opus-4.6"
"gpt-5.2"
"gpt-5.2-codex"            # Best for coding
"gpt-5.2-thinking"         # Extended reasoning
"o3"                       # OpenAI reasoning
"gemini-3.0-pro"
"grok-4.1"
"qwen-3-coder"             # Alibaba coding model
"llama-4"

# Image/Video Generation
"sora-2"                   # OpenAI video
"veo-3"                    # Google video
"grok-imagine"             # xAI image
"flux-ultra-pro"           # Image generation
```

---

## By Use Case

### Coding & Development
1. **`grok-code-fast-1`** (xAI) - 256K context, coding optimized
2. **`gemini-3-pro-preview`** (Google) - 1M context, strong coding
3. **`qwen-3-coder`** (Abacus) - Specialized coding model
4. **`gpt-5.2-codex`** (Abacus) - OpenAI coding

### Executive & Strategic Decisions
1. **`grok-4-1-fast-reasoning`** (xAI) - Agentic tool calling, 2M context
2. **`claude-opus-4-6`** (Anthropic) - Complex reasoning
3. **`abacus-deep-agent`** (Abacus) - Adaptive routing

### Long Documents & Analysis
1. **`grok-4-1-fast-reasoning`** (xAI) - 2M context
2. **`gemini-3-pro-preview`** (Google) - 1M context
3. **`claude-opus-4-6`** (Anthropic) - Deep analysis

### Fast Responses
1. **`grok-4-1-fast-non-reasoning`** (xAI) - Instant, no reasoning
2. **`claude-sonnet-4.5`** (Anthropic) - Fast general-purpose
3. **`gemini-3-flash-preview`** (Google) - Fast multimodal

### High-Volume / Cost-Sensitive
1. **`claude-haiku-4.5`** (Anthropic) - Most cost-effective
2. **`grok-3-mini-fast`** (xAI) - Fastest mini variant
3. **`gemini-2.5-flash-lite`** (Google) - High-volume

### Multimodal (Text + Image + Audio)
1. **`gemini-3-pro-preview`** (Google) - Best multimodal
2. **`gemini-3-flash-preview`** (Google) - Fast multimodal

### Image Generation
1. **`grok-imagine`** (xAI)
2. **`flux-ultra-pro`** (Abacus)
3. **`gpt-image`** (Abacus)

### Video Generation
1. **`sora-2`** (Abacus - OpenAI)
2. **`veo-3`** (Abacus - Google)
3. **`kling-2.6`** (Abacus)

---

## Context Window Sizes

| Model | Context | Best For |
|-------|---------|----------|
| `grok-4-1-fast-reasoning` | 2M tokens | Massive documents, full codebases |
| `grok-4-1-fast-non-reasoning` | 2M tokens | Fast retrieval from huge context |
| `gemini-3-pro-preview` | 1M tokens | Large documents, multimodal |
| `gemini-3-flash-preview` | 1M tokens | Fast processing of large inputs |
| `grok-code-fast-1` | 256K tokens | Full coding files |
| `claude-opus-4-6` | Standard | Complex reasoning (exact limit TBD) |

---

## API Configuration

### Environment Variables

```bash
# xAI (Grok)
XAI_API_KEY=your_xai_key_here
# or
GROK_API_KEY=your_grok_key_here

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google AI (Gemini)
GOOGLE_AI_API_KEY=your_google_key_here
# or
GEMINI_API_KEY=your_gemini_key_here

# Jules/Codebuff (optional)
JULES_LEGACY_KEY=your_jules_key_here

# Abacus.AI
ABACUS_PRIMARY_KEY=your_abacus_primary_key_here
ABACUS_BACKUP_KEY=your_abacus_backup_key_here  # optional
```

### API Endpoints

```python
# xAI (Grok)
endpoint = "https://api.x.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {XAI_API_KEY}"}

# Anthropic (Claude)
endpoint = "https://api.anthropic.com/v1/messages"
headers = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01"
}

# Google AI (Gemini)
# Use Google AI Studio SDK
from google.generativeai import configure, GenerativeModel
configure(api_key=GOOGLE_AI_API_KEY)

# Abacus.AI
# Use Abacus SDK (configured in _agents/abacus/client.py)
from abacusai import ApiClient
client = ApiClient(api_key=ABACUS_PRIMARY_KEY)
```

---

## Decision Matrix

### When to Use Each Platform

| Scenario | Platform | Why |
|----------|----------|-----|
| Need 2M+ token context | xAI | Grok 4 has largest context window |
| Complex reasoning task | Anthropic | Claude Opus excels at deep analysis |
| Coding + multimodal | Google AI | Gemini 3 Pro best for mixed tasks |
| Don't know which model | Abacus.AI | Deep Agent auto-routes |
| Need GPT-5.2 or o3 | Abacus.AI | Only platform with OpenAI access |
| Need video generation | Abacus.AI | Sora 2, Veo-3 access |
| Fast iteration | xAI or Google | Grok 4 fast / Gemini 3 Flash |
| Budget-conscious | Anthropic | Claude Haiku most cost-effective |

---

## Platform Status

| Platform | Status | Models Available | Notes |
|----------|--------|------------------|-------|
| **xAI** | ✅ Operational | ~10 | Grok 4 recommended upgrade |
| **Anthropic** | ✅ Operational | 3 | Opus 4.6 recommended upgrade |
| **Google AI** | ✅ Operational | ~8 | Upgraded 2026-02-14 |
| **Abacus.AI** | ✅ Configured | 50+ | SDK ready, needs testing |

---

## Upgrade Checklist

### Immediate Upgrades Recommended

- [ ] **xAI:** Upgrade from `grok-3` → `grok-4-1-fast-reasoning`
  - Benefit: 2M context, better agentic performance

- [ ] **Anthropic:** Upgrade from `claude-opus-4-5` → `claude-opus-4-6`
  - Benefit: Latest capabilities, improved reasoning

- [ ] **Google AI:** Configure `gemini-3-pro-preview` or `gemini-3-flash-preview`
  - Status: ✅ API access active

- [ ] **Abacus.AI:** Test `abacus-deep-agent` for automatic routing
  - Status: SDK configured, ready to test

---

## Quick Examples

### Python API Call Examples

#### xAI (Grok)
```python
import requests
import os

response = requests.post(
    "https://api.x.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"},
    json={
        "model": "grok-4-1-fast-reasoning",
        "messages": [{"role": "user", "content": "Your prompt here"}],
        "temperature": 0.7
    }
)
```

#### Anthropic (Claude)
```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Your prompt here"}]
)
```

#### Google AI (Gemini)
```python
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
model = genai.GenerativeModel('gemini-3-pro-preview')
response = model.generate_content("Your prompt here")
```

#### Abacus.AI
```python
from abacusai import ApiClient
import os

client = ApiClient(api_key=os.getenv('ABACUS_PRIMARY_KEY'))
# Use configured client from _agents/abacus/client.py
```

---

## Knowledge Cutoffs

| Platform | Latest Model | Knowledge Cutoff |
|----------|--------------|------------------|
| xAI | Grok 4.1 | November 2024 |
| Anthropic | Claude Opus 4.6 | January 2025 |
| Google AI | Gemini 3 | Current (varies) |
| Abacus.AI | Various | Depends on routed model |

---

## Additional Resources

- **Full Documentation:** `docs/api-configuration.md`
- **Agent Profiles:** `_agents/{grok,claude,gemini,abacus}/profile.md`
- **Abacus Client:** `_agents/abacus/client.py`
- **Environment Template:** `.env.example`

---

## Notes

- All 4 platforms are now operational ✅
- Abacus.AI provides access to 50+ models including GPT-5.2, o3, and more
- Recommend testing `abacus-deep-agent` for intelligent model routing
- Keep `.env` file secure - never commit to version control
- See `docs/api-configuration.md` for complete details and use case guide
