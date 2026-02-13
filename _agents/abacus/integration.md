# Abacus Integration Options

Abacus (Abacus.AI) requires SDK-based integration rather than a simple REST API key. Two keys are available — a primary and a legacy backup from the ChatLLM merge.

**Primary Key:** Configured in `.env` as `ABACUS_PRIMARY_KEY`
**Backup Key (legacy ChatLLM):** Configured in `.env` as `ABACUS_BACKUP_KEY`

---

## Option 1: Abacus.AI Python SDK (Recommended for Automation)

The `abacusai` Python package provides programmatic access.

### Installation
```bash
pip install abacusai python-dotenv
```

### Authentication
```python
# Import from local helper
from _agents.abacus.client import get_client

# Initialize client using environment variables
client = get_client()

# Work with agents
# agent = client.describe_agent(agent_id='abacus-agent-id')
```

### Key Classes
- `AbacusApi` — Main client
- `Agent` — Agent management (refresh, describe, copy)
- `AgentConversation` — Message history
- `AgentChatMessage` — Individual messages

### Setup Steps
1. `pip install abacusai python-dotenv`
2. Configure `.env` with keys (see `.env.example`)
3. Test connection with `python _agents/abacus/client.py`
4. Identify agent ID from dashboard
5. Test basic conversation flow

---

## Option 2: DeepAgent Desktop + CLI

Abacus provides a desktop app with CLI capabilities.

### Installation
Download from: https://desktop.abacus.ai/

### Features
- Agentic browsing
- Coding CLI and editor
- Local code processing
- Can be scripted for automation

### Use Case
Good for interactive work. Less suited for fully automated pipelines.

---

## Option 3: DeepAgent Cloud + MCP Integration

Abacus supports Model Context Protocol (MCP) for tool integration.

### Setup
1. Access via https://deepagent.abacus.ai
2. Configure MCP servers for external tool access
3. Connect to GitHub, Slack, etc.

### Automation Workflows
- Describe tasks in natural language
- DeepAgent designs the workflow
- Can schedule recurring jobs
- Integrates with GitHub, Jira, etc.

---

## Option 4: GitHub Actions Relay (For Async Work)

For autonomous task processing:

1. Create a GitHub repo or directory for Abacus tasks
2. Drop task files (handoffs) into the repo
3. Abacus monitors via GitHub integration
4. Results posted back to repo or notified via Slack

### Setup Required
- Connect Abacus to GitHub account
- Configure webhook or polling for new tasks
- Set up notification channel for completions

---

## Option 5: Manual Relay (Fallback)

Russell acts as the bridge:

1. Team creates handoff for Abacus
2. Russell takes the handoff to DeepAgent web/desktop
3. Abacus works on it
4. Russell brings response back to team

Works immediately, no setup required. Not truly async.

---

## Recommended Path Forward

1. **Immediate:** Use Manual Relay for first sessions
2. **Short-term:** Install Python SDK, configure `.env`
3. **Medium-term:** Set up GitHub integration for async workflows
4. **Long-term:** Full MCP integration with BPR&D AI Comm Hub

---

## Resources

- [DeepAgent Cloud](https://deepagent.abacus.ai)
- [DeepAgent Desktop](https://desktop.abacus.ai/)
- [API Reference](https://abacus.ai/help/api/ref/ai_agents)
- [Python SDK Docs](https://abacusai.github.io/api-python/)
- [MCP Setup Guide](https://abacus.ai/help/howTo/chatllm/mcp_servers_how_to)
- [GitHub: abacusai/DeepAgent](https://github.com/abacusai/DeepAgent)

---

## Notes for Abacus

- Integration is more complex than Grok/Claude/Gemini (SDK-based, not simple API)
- May need to work async or through relays initially
- The paranoid-inventor persona should appreciate the security of local processing options
- GitHub integration enables autonomous "wake up and work" patterns
- Two keys available — if one fails, try the other
