# n8n Workflow Fixes for BPR&D

Based on the comprehensive workflow analysis, this guide helps you apply recommended fixes to your n8n workflows.

---

## Quick Start

### Prerequisites

1. **Install dependencies:**
   ```bash
   cd _shared/skills/automation/n8n-integration
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   # In your .env file or shell
   export N8N_API_KEY="your-api-key-here"
   export N8N_BASE_URL="https://n8n.bprd.io"
   ```

3. **Test connection:**
   ```bash
   python test_integration.py
   ```

---

## Team Meetings Workflow Fixes

### Fix 1: Add Missing Abacus Agent

**Issue:** Workflow only has 3 agents (Grok, Claude, Gemini) - missing Abacus
**Impact:** Faction imbalance, Truth-Seekers faction incomplete
**Priority:** High

**Apply Fix:**
```bash
python workflow_fixer.py --workflow team-meetings --fix add-abacus
```

**What it does:**
- Creates Abacus agent node with HTTP Request to Abacus.AI API
- Uses `abacus-deep-agent` model for adaptive routing
- Adds proper system message for Abacus personality
- Creates backup before making changes

**Manual steps after:**
1. Open workflow in n8n UI
2. Connect Abacus agent node to the orchestration flow
3. Add Abacus to the meeting participants list
4. Test with a sample meeting execution

---

### Fix 2: Update Deprecated Gemini Model

**Issue:** Using `gemini-pro-latest` (deprecated)
**Should be:** `gemini-3-pro-preview`
**Impact:** May cause API errors or degraded performance
**Priority:** Medium

**Apply Fix:**
```bash
python workflow_fixer.py --workflow team-meetings --fix update-gemini
```

**What it does:**
- Finds all Gemini agent nodes
- Updates model parameter from `gemini-pro-latest` to `gemini-3-pro-preview`
- Creates backup before making changes

**Manual steps after:**
1. Verify model update in n8n UI
2. Test Gemini agent responses
3. Monitor for any API errors

---

### Fix 3: Apply All Team Meetings Fixes

**Recommended:** Apply both fixes at once

```bash
python workflow_fixer.py --workflow team-meetings --fix all
```

---

## General BPR&D Workflow Fixes

### Fix: Complete Data Flow

**Issue:** Workflow has incomplete data flow - no storage, synthesis, or notifications
**Impact:** Critical - workflow cannot complete end-to-end
**Priority:** Critical

**Apply Fix:**
```bash
# Get your General workflow ID first
python workflow_fixer.py --list

# Then apply fix (replace WORKFLOW_ID with actual ID)
python workflow_fixer.py --workflow WORKFLOW_ID --fix add-data-flow
```

**What it does:**
- Adds "Merge Agent Responses" node to combine outputs
- Adds "Store Results to GitHub" node for persistence
- Adds "Notify Team via Telegram" node for alerts
- Creates backup before making changes

**Manual steps after:**
1. Open workflow in n8n UI
2. Connect merge node after all agent nodes
3. Connect GitHub storage after merge
4. Connect Telegram notification after storage
5. Configure GitHub repository and file path
6. Configure Telegram bot and chat ID
7. Test full end-to-end flow

---

## Manual Fixes Required

Some fixes require manual intervention in the n8n UI:

### Team Meetings: Connect Agent Personas

**Issue:** "Get Agent Personas from GitHub" node is disconnected
**Manual Fix:**
1. Open Team Meetings workflow in n8n UI
2. Find "Get Agent Personas from GitHub" node
3. Connect its output to each agent's system prompt input
4. Map persona content to system message parameter

### General Workflow: Connect Tools to Agents

**Issue:** Calculator and Code Interpreter tools are present but not connected
**Manual Fix:**
1. Open General workflow in n8n UI
2. For each agent node (Grok, Claude, Gemini, Abacus):
   - Open node configuration
   - Find "Tools" parameter
   - Add Calculator tool
   - Add Code Interpreter tool (especially for Gemini and Abacus)
3. Test tool invocation with sample tasks

---

## Workflow Management Commands

### List All Workflows
```bash
python workflow_fixer.py --list
```

### Backup a Workflow Manually
```python
from workflow_fixer import WorkflowFixer

fixer = WorkflowFixer()
backup_path = fixer.backup_workflow('WORKFLOW_ID')
print(f"Backed up to: {backup_path}")
```

### Get Workflow Details
```python
from n8n_client import N8NClient

client = N8NClient()
workflow = client.get_workflow('WORKFLOW_ID')

print(f"Name: {workflow['name']}")
print(f"Active: {workflow['active']}")
print(f"Nodes: {len(workflow['nodes'])}")
```

---

## Testing Workflows

### Test Team Meetings Workflow
```python
from n8n_client import BPRDWorkflows

bprd = BPRDWorkflows()

# Trigger test meeting with all 4 agents
result = bprd.trigger_team_meeting(
    meeting_type='strategic_planning',
    participants=['grok', 'claude', 'gemini', 'abacus'],
    agenda='Test Meeting - Verify All Agents Present'
)

print("Meeting Result:", result)
```

### Test General Workflow
```python
from n8n_client import N8NClient

client = N8NClient()

# Execute general workflow with test data
result = client.execute_workflow(
    workflow_id='YOUR_GENERAL_WORKFLOW_ID',
    data={
        'task_type': 'research',
        'task_description': 'Test task to verify data flow',
        'priority': 'high'
    }
)

print("Task Result:", result)
```

---

## Troubleshooting

### API Connection Issues

**Problem:** `Could not resolve host: n8n.bprd.io`

**Solutions:**
1. Check DNS settings
2. Verify n8n instance is accessible
3. Try accessing https://n8n.bprd.io in browser
4. Check firewall/network settings
5. For n8n Cloud, use full cloud URL (e.g., `https://yourname.app.n8n.cloud`)

### Authentication Errors

**Problem:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**
1. Verify API key is correct: `echo $N8N_API_KEY`
2. Check API key hasn't expired (Settings > n8n API in n8n UI)
3. For enterprise: Verify API key has required scopes
4. Generate new API key if needed

### Workflow Update Failures

**Problem:** Workflow update fails with validation errors

**Solutions:**
1. Check backup file in `./backups/` directory
2. Restore from backup if needed:
   ```python
   with open('backups/workflow_backup.json') as f:
       workflow_data = json.load(f)
   client.update_workflow(workflow_id, workflow_data)
   ```
3. Manually fix validation errors in n8n UI
4. Report issue with error details

---

## Advanced Usage

### Custom Node Creation

Create custom nodes programmatically:

```python
from n8n_client import N8NClient

client = N8NClient()

# Create a custom webhook node
custom_node = {
    "parameters": {
        "path": "custom-webhook",
        "responseMode": "responseNode",
        "options": {}
    },
    "id": "webhook-trigger",
    "name": "Custom Webhook",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 1.1,
    "position": [250, 300],
    "webhookId": "custom-webhook-id"
}

# Add to workflow
workflow = client.get_workflow('WORKFLOW_ID')
workflow['nodes'].append(custom_node)
client.update_workflow('WORKFLOW_ID', workflow)
```

### Batch Workflow Updates

Update multiple workflows:

```python
from workflow_fixer import WorkflowFixer

fixer = WorkflowFixer()

# Get all workflows
workflows = fixer.client.list_workflows()

# Update Gemini model in all workflows
for wf in workflows:
    if 'gemini' in wf['name'].lower():
        print(f"Updating {wf['name']}...")
        fixer.fix_team_meetings_update_gemini(wf['id'])
```

---

## Production Deployment Checklist

Before activating workflows in production:

### Team Meetings Workflow
- [ ] Abacus agent added and connected
- [ ] Gemini model updated to `gemini-3-pro-preview`
- [ ] Agent personas connected to system prompts
- [ ] All 6 schedule triggers tested
- [ ] GitHub storage validated
- [ ] Telegram notifications working
- [ ] Test meeting executed successfully with all 4 agents
- [ ] Backup created and stored safely

### General BPR&D Workflow
- [ ] Merge node added and connected
- [ ] GitHub storage configured and tested
- [ ] Telegram notifications configured
- [ ] Tools connected to agents (Calculator, Code)
- [ ] Error handling added
- [ ] Test task executed end-to-end successfully
- [ ] Performance validated (< 2 min per task)
- [ ] Backup created and stored safely

---

## Monitoring and Maintenance

### Check Workflow Health
```python
from n8n_client import N8NClient

client = N8NClient()

# Get recent executions
executions = client.list_executions(workflow_id='WORKFLOW_ID', limit=50)

# Calculate success rate
total = len(executions)
successful = sum(1 for e in executions if e.get('finished') and not e.get('stoppedAt'))
success_rate = (successful / total * 100) if total > 0 else 0

print(f"Success Rate: {success_rate:.1f}% ({successful}/{total})")
```

### Monitor Execution Times
```python
from datetime import datetime

for execution in executions:
    if execution.get('finished'):
        start = datetime.fromisoformat(execution['startedAt'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(execution['finishedAt'].replace('Z', '+00:00'))
        duration = (end - start).total_seconds()
        print(f"Execution {execution['id']}: {duration:.1f}s")
```

---

## Resources

- **Workflow Analysis:** See `docs/n8n-workflow-analysis.md` for detailed technical assessment
- **API Documentation:** See `SKILL.md` for complete n8n API reference
- **Team Meetings Guide:** See `docs/n8n-meeting-automation.md` for usage guide
- **Model Reference:** See `docs/MODEL-REFERENCE.md` for AI model selection

---

## Support

For issues or questions:

1. **Check documentation:** Review `docs/` directory
2. **Test integration:** Run `python test_integration.py`
3. **Review backups:** Check `./backups/` for workflow snapshots
4. **Check n8n docs:** https://docs.n8n.io/api/
5. **Community:** https://community.n8n.io/

---

*Workflow fixes by Claude Sonnet 4.5 for BPR&D*
*Last updated: 2026-02-14*
