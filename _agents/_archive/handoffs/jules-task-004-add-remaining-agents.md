# Task 004: Add Remaining Agents

**To:** Jules | **Priority:** Medium | **Depends:** Tasks 001, 002, 003

## Goal
Once APIs are researched and MVP works, add the other 4 agents.

## Agents to Add

| Agent | Platform | Status |
|-------|----------|--------|
| Deep Agent | Abacus SDK | After Task 001 |
| ChatLLM | Abacus SDK | After Task 001 |
| Jules | TBD | After Task 002 |
| Gemini | Google AI | Wait for quota reset or upgrade |

## Gemini (when quota resets)
```python
httpx.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
    json={"systemInstruction": {"parts": [{"text": "..."}]},
          "contents": [{"parts": [{"text": "..."}]}],
          "generationConfig": {"temperature": 0.8}})
```

## Tasks
1. Create `agents/deep_agent.py` using Abacus SDK
2. Create `agents/chatllm.py` using Abacus SDK
3. Create `agents/jules.py` once platform identified
4. Create `agents/gemini.py` when quota available
5. Update `config.yaml` to enable each as ready

## Done When
All 6 agents can participate in meetings via API.
