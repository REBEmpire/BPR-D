# n8n Workflow Integration Skill

**Version:** 1.0
**Created:** 2026-02-14
**Category:** Automation

---

## Overview

This skill enables BPR&D agents to work directly with n8n workflows via the n8n REST API. Agents can inspect, create, modify, execute, and manage workflows programmatically.

---

## Capabilities

### 1. Workflow Management
- List all workflows
- Get workflow details by ID
- Create new workflows
- Update existing workflows
- Delete workflows
- Activate/deactivate workflows

### 2. Workflow Execution
- Trigger workflow executions
- Pass data to workflows
- Monitor execution status
- Get execution results

### 3. Workflow Analysis
- Inspect workflow structure
- Understand triggers and nodes
- Analyze data flow
- Identify optimization opportunities

### 4. Credentials Management
- List available credentials
- Create new credentials (if permissions allow)
- Update credentials

---

## Prerequisites

### Environment Variables
Add to your `.env` file:
```bash
N8N_API_KEY=your_n8n_api_key_here
N8N_BASE_URL=https://n8n.bprd.io  # Your n8n instance URL
```

### API Authentication
n8n API uses API key authentication via the `X-N8N-API-KEY` header.

---

## Usage Examples

### List All Workflows
```bash
curl -X GET "${N8N_BASE_URL}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Accept: application/json"
```

### Get Workflow by ID
```bash
curl -X GET "${N8N_BASE_URL}/api/v1/workflows/{workflowId}" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Accept: application/json"
```

### Execute Workflow
```bash
curl -X POST "${N8N_BASE_URL}/api/v1/workflows/{workflowId}/execute" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "your": "input data here"
    }
  }'
```

### Create New Workflow
```bash
curl -X POST "${N8N_BASE_URL}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

### Update Existing Workflow
```bash
curl -X PATCH "${N8N_BASE_URL}/api/v1/workflows/{workflowId}" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @updated_workflow.json
```

### Activate/Deactivate Workflow
```bash
curl -X PATCH "${N8N_BASE_URL}/api/v1/workflows/{workflowId}" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"active": true}'
```

---

## Common Workflow Patterns

### 1. BPR&D Team Meeting Automation
**Workflow ID:** `pDh6gPBEULb5kSx9`
**URL:** https://n8n.bprd.io/workflow/pDh6gPBEULb5kSx9

Purpose: Automates BPR&D team meetings with 4-agent coordination.

**Usage:**
```bash
# Trigger a team meeting
curl -X POST "${N8N_BASE_URL}/api/v1/workflows/pDh6gPBEULb5kSx9/execute" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_type": "strategic_planning",
    "participants": ["grok", "claude", "abacus", "gemini"],
    "agenda": "Q1 2026 Planning"
  }'
```

### 2. Agent Coordination Workflows
Use n8n to coordinate multi-agent workflows:
- Trigger workflows when one agent completes a task
- Route tasks to appropriate agents based on expertise
- Aggregate results from multiple agents

### 3. API Integration Workflows
Connect BPR&D to external services:
- Slack notifications for completed tasks
- GitHub issue creation/updates
- Database synchronization
- Email notifications

---

## API Endpoints Reference

### Workflows
- `GET /api/v1/workflows` - List all workflows
- `GET /api/v1/workflows/{id}` - Get workflow by ID
- `POST /api/v1/workflows` - Create new workflow
- `PATCH /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow
- `POST /api/v1/workflows/{id}/execute` - Execute workflow

### Executions
- `GET /api/v1/executions` - List executions
- `GET /api/v1/executions/{id}` - Get execution details
- `DELETE /api/v1/executions/{id}` - Delete execution

### Credentials
- `GET /api/v1/credentials` - List credentials
- `GET /api/v1/credentials/{id}` - Get credential
- `POST /api/v1/credentials` - Create credential
- `PATCH /api/v1/credentials/{id}` - Update credential
- `DELETE /api/v1/credentials/{id}` - Delete credential

---

## Workflow JSON Structure

### Basic Workflow Template
```json
{
  "name": "My Workflow",
  "nodes": [
    {
      "parameters": {},
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "httpMethod": "GET",
        "url": "https://api.example.com/data"
      },
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [450, 300]
    }
  ],
  "connections": {
    "Start": {
      "main": [
        [
          {
            "node": "HTTP Request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": false,
  "settings": {},
  "tags": []
}
```

---

## Integration with BPR&D Agents

### Grok (Chief/Executive)
**Use Case:** High-level workflow orchestration and decision-making
```bash
# Example: Grok initiates strategic planning workflow
curl -X POST "${N8N_BASE_URL}/api/v1/workflows/strategic-planning/execute" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -d '{"initiated_by": "grok", "priority": "high"}'
```

### Claude (Strategist)
**Use Case:** Architecture and planning workflow analysis
```bash
# Example: Claude reviews workflow structure for optimization
curl -X GET "${N8N_BASE_URL}/api/v1/workflows/{id}" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}"
```

### Gemini (Developer)
**Use Case:** Building and deploying new automation workflows
```bash
# Example: Gemini creates a new compliance automation
curl -X POST "${N8N_BASE_URL}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -d @compliance_automation.json
```

### Abacus (Innovator)
**Use Case:** Experimental workflows and unconventional integrations
```bash
# Example: Abacus tests edge cases in workflow execution
curl -X POST "${N8N_BASE_URL}/api/v1/workflows/{id}/execute" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -d '{"test_mode": true, "edge_case": "stress_test"}'
```

---

## Error Handling

### Common Error Responses
```json
{
  "code": 401,
  "message": "Unauthorized - Invalid API key"
}

{
  "code": 404,
  "message": "Workflow not found"
}

{
  "code": 400,
  "message": "Invalid workflow JSON"
}
```

### Best Practices
1. Always check response status codes
2. Log execution IDs for debugging
3. Handle rate limits gracefully
4. Validate workflow JSON before submitting
5. Test workflows in inactive state before activating

---

## Security Best Practices

1. **API Key Protection**
   - Store API key in `.env` file (never commit)
   - Use environment variables in scripts
   - Rotate keys periodically

2. **Workflow Security**
   - Validate webhook inputs
   - Use credential management for external services
   - Implement error handling for sensitive operations

3. **Access Control**
   - Limit API key permissions to necessary operations
   - Monitor workflow executions for anomalies
   - Use separate credentials for dev/prod environments

---

## Helper Functions

### Python Helper Class
```python
import os
import requests
from typing import Dict, List, Optional

class N8NClient:
    def __init__(self):
        self.api_key = os.getenv('N8N_API_KEY')
        self.base_url = os.getenv('N8N_BASE_URL', 'https://n8n.bprd.io')
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def list_workflows(self) -> List[Dict]:
        """List all workflows"""
        response = requests.get(
            f'{self.base_url}/api/v1/workflows',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow by ID"""
        response = requests.get(
            f'{self.base_url}/api/v1/workflows/{workflow_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Dict:
        """Execute workflow with optional input data"""
        response = requests.post(
            f'{self.base_url}/api/v1/workflows/{workflow_id}/execute',
            headers=self.headers,
            json={'data': data} if data else {}
        )
        response.raise_for_status()
        return response.json()

    def create_workflow(self, workflow_json: Dict) -> Dict:
        """Create new workflow"""
        response = requests.post(
            f'{self.base_url}/api/v1/workflows',
            headers=self.headers,
            json=workflow_json
        )
        response.raise_for_status()
        return response.json()

    def update_workflow(self, workflow_id: str, workflow_json: Dict) -> Dict:
        """Update existing workflow"""
        response = requests.patch(
            f'{self.base_url}/api/v1/workflows/{workflow_id}',
            headers=self.headers,
            json=workflow_json
        )
        response.raise_for_status()
        return response.json()

    def activate_workflow(self, workflow_id: str, active: bool = True) -> Dict:
        """Activate or deactivate workflow"""
        response = requests.patch(
            f'{self.base_url}/api/v1/workflows/{workflow_id}',
            headers=self.headers,
            json={'active': active}
        )
        response.raise_for_status()
        return response.json()

# Usage
if __name__ == '__main__':
    client = N8NClient()

    # List all workflows
    workflows = client.list_workflows()
    print(f"Found {len(workflows)} workflows")

    # Execute team meeting workflow
    result = client.execute_workflow(
        'pDh6gPBEULb5kSx9',
        data={'meeting_type': 'strategic_planning'}
    )
    print(f"Meeting workflow executed: {result}")
```

---

## Resources

### Official Documentation
- **n8n API Documentation:** https://docs.n8n.io/api/
- **n8n API Reference:** https://docs.n8n.io/api/api-reference/
- **n8n Workflows:** https://docs.n8n.io/

### BPR&D Resources
- **Meeting Automation Guide:** `docs/n8n-meeting-automation.md`
- **Environment Setup:** `.env.example`
- **Agent Profiles:** `_agents/{agent}/profile.md`

---

## Changelog

**v1.0 - 2026-02-14**
- Initial n8n integration skill
- Full API endpoint documentation
- Python helper class
- BPR&D agent integration examples
- Security best practices

---

*Automated with ❤️ by BPR&D*
