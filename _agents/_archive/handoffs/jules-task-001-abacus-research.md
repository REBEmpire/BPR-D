# Task 001: Research Abacus.AI SDK

**To:** Jules | **Priority:** High | **Est:** 1-2 hrs

## Goal
Get Deep Agent and ChatLLM APIs working.

## Problem
Direct REST calls to Abacus return 404. The `s2_` prefix keys suggest SDK access.

## Keys
- Deep Agent: `s2_31d1f22c7c69422ba5da165fb98532bb`
- ChatLLM: `s2_1e30fa4a3d834bffb1b465d67eb1809e`

## Tasks
1. `pip install abacusai`
2. Find the correct method to send chat messages
3. Test both keys
4. Document working code in `docs/api-configuration.md`

## Resources
- https://abacusai.github.io/api-python/
- https://abacus.ai/help/api/ref/ai_agents

## Done When
```python
# This works:
from abacusai import ApiClient
client = ApiClient(api_key='s2_...')
response = client.???("Hello")  # Find the right method
print(response)
```
