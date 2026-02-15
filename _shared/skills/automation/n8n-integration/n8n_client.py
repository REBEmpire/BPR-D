"""
n8n Workflow API Client for BPR&D

Provides programmatic access to n8n workflows for automation and integration.
"""

import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class N8NClient:
    """Client for interacting with n8n REST API"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize n8n API client

        Args:
            api_key: n8n API key (defaults to N8N_API_KEY env var)
            base_url: n8n instance URL (defaults to N8N_BASE_URL env var)
        """
        self.api_key = api_key or os.getenv('N8N_API_KEY')
        self.base_url = (base_url or os.getenv('N8N_BASE_URL', 'https://n8n.bprd.io')).rstrip('/')

        if not self.api_key:
            raise ValueError("N8N_API_KEY must be set in environment or passed to constructor")

        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Make HTTP request to n8n API

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response data

        Raises:
            requests.HTTPError: If request fails
        """
        url = f'{self.base_url}{endpoint}'
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    # Workflow Management

    def list_workflows(self, active: Optional[bool] = None, tags: Optional[List[str]] = None) -> List[Dict]:
        """
        List all workflows

        Args:
            active: Filter by active status (True/False/None for all)
            tags: Filter by tags

        Returns:
            List of workflow objects
        """
        params = {}
        if active is not None:
            params['active'] = str(active).lower()
        if tags:
            params['tags'] = ','.join(tags)

        return self._request('GET', '/api/v1/workflows', params=params)

    def get_workflow(self, workflow_id: str) -> Dict:
        """
        Get workflow by ID

        Args:
            workflow_id: Workflow ID or name

        Returns:
            Workflow object
        """
        return self._request('GET', f'/api/v1/workflows/{workflow_id}')

    def create_workflow(self, workflow_json: Dict) -> Dict:
        """
        Create new workflow

        Args:
            workflow_json: Workflow definition

        Returns:
            Created workflow object
        """
        return self._request('POST', '/api/v1/workflows', json=workflow_json)

    def update_workflow(self, workflow_id: str, workflow_json: Dict) -> Dict:
        """
        Update existing workflow

        Args:
            workflow_id: Workflow ID
            workflow_json: Updated workflow definition

        Returns:
            Updated workflow object
        """
        return self._request('PATCH', f'/api/v1/workflows/{workflow_id}', json=workflow_json)

    def delete_workflow(self, workflow_id: str) -> None:
        """
        Delete workflow

        Args:
            workflow_id: Workflow ID
        """
        self._request('DELETE', f'/api/v1/workflows/{workflow_id}')

    def activate_workflow(self, workflow_id: str, active: bool = True) -> Dict:
        """
        Activate or deactivate workflow

        Args:
            workflow_id: Workflow ID
            active: True to activate, False to deactivate

        Returns:
            Updated workflow object
        """
        return self._request(
            'PATCH',
            f'/api/v1/workflows/{workflow_id}',
            json={'active': active}
        )

    # Workflow Execution

    def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Dict:
        """
        Execute workflow

        Args:
            workflow_id: Workflow ID
            data: Input data for workflow execution

        Returns:
            Execution result
        """
        payload = {'data': data} if data else {}
        return self._request('POST', f'/api/v1/workflows/{workflow_id}/execute', json=payload)

    def list_executions(self, workflow_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        List workflow executions

        Args:
            workflow_id: Filter by workflow ID (optional)
            limit: Maximum number of results

        Returns:
            List of execution objects
        """
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id

        return self._request('GET', '/api/v1/executions', params=params)

    def get_execution(self, execution_id: str) -> Dict:
        """
        Get execution details

        Args:
            execution_id: Execution ID

        Returns:
            Execution object with detailed results
        """
        return self._request('GET', f'/api/v1/executions/{execution_id}')

    def delete_execution(self, execution_id: str) -> None:
        """
        Delete execution

        Args:
            execution_id: Execution ID
        """
        self._request('DELETE', f'/api/v1/executions/{execution_id}')

    # Credentials Management

    def list_credentials(self) -> List[Dict]:
        """
        List all credentials

        Returns:
            List of credential objects (without sensitive data)
        """
        return self._request('GET', '/api/v1/credentials')

    def get_credential(self, credential_id: str) -> Dict:
        """
        Get credential by ID

        Args:
            credential_id: Credential ID

        Returns:
            Credential object (without sensitive data)
        """
        return self._request('GET', f'/api/v1/credentials/{credential_id}')

    def create_credential(self, credential_json: Dict) -> Dict:
        """
        Create new credential

        Args:
            credential_json: Credential definition

        Returns:
            Created credential object
        """
        return self._request('POST', '/api/v1/credentials', json=credential_json)

    def update_credential(self, credential_id: str, credential_json: Dict) -> Dict:
        """
        Update existing credential

        Args:
            credential_id: Credential ID
            credential_json: Updated credential definition

        Returns:
            Updated credential object
        """
        return self._request('PATCH', f'/api/v1/credentials/{credential_id}', json=credential_json)

    def delete_credential(self, credential_id: str) -> None:
        """
        Delete credential

        Args:
            credential_id: Credential ID
        """
        self._request('DELETE', f'/api/v1/credentials/{credential_id}')


class BPRDWorkflows:
    """Helper class for common BPR&D workflow operations"""

    # Known BPR&D workflow IDs
    TEAM_MEETING_WORKFLOW = 'pDh6gPBEULb5kSx9'

    def __init__(self, client: Optional[N8NClient] = None):
        """
        Initialize BPR&D workflows helper

        Args:
            client: N8NClient instance (creates new one if not provided)
        """
        self.client = client or N8NClient()

    def trigger_team_meeting(
        self,
        meeting_type: str = 'strategic_planning',
        participants: Optional[List[str]] = None,
        agenda: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Trigger BPR&D team meeting workflow

        Args:
            meeting_type: Type of meeting (strategic_planning, implementation, full_team)
            participants: List of agent names (defaults to all 4 agents)
            agenda: Meeting agenda/topic
            **kwargs: Additional data to pass to workflow

        Returns:
            Execution result
        """
        if participants is None:
            participants = ['grok', 'claude', 'gemini', 'abacus']

        data = {
            'meeting_type': meeting_type,
            'participants': participants,
            'agenda': agenda or 'General Meeting',
            **kwargs
        }

        return self.client.execute_workflow(self.TEAM_MEETING_WORKFLOW, data=data)

    def get_agent_workflows(self, agent_name: str) -> List[Dict]:
        """
        Get workflows tagged for specific agent

        Args:
            agent_name: Agent name (grok, claude, gemini, abacus)

        Returns:
            List of workflows for that agent
        """
        return self.client.list_workflows(tags=[agent_name, 'bprd'])

    def create_agent_workflow(
        self,
        name: str,
        agent: str,
        workflow_nodes: List[Dict],
        active: bool = False
    ) -> Dict:
        """
        Create new workflow for specific agent

        Args:
            name: Workflow name
            agent: Agent name (grok, claude, gemini, abacus)
            workflow_nodes: List of workflow nodes
            active: Whether to activate immediately

        Returns:
            Created workflow object
        """
        workflow = {
            'name': f'{agent.title()} - {name}',
            'nodes': workflow_nodes,
            'connections': {},
            'active': active,
            'tags': [agent, 'bprd'],
            'settings': {}
        }

        return self.client.create_workflow(workflow)


# Example usage
if __name__ == '__main__':
    # Initialize client
    client = N8NClient()

    # List all workflows
    print("=== All Workflows ===")
    workflows = client.list_workflows()
    for wf in workflows:
        print(f"- {wf['name']} (ID: {wf['id']}, Active: {wf.get('active', False)})")

    print("\n=== BPR&D Helper ===")
    # Use BPR&D helper
    bprd = BPRDWorkflows(client)

    # Trigger team meeting
    print("Triggering team meeting...")
    result = bprd.trigger_team_meeting(
        meeting_type='strategic_planning',
        agenda='Q1 2026 Planning and Model Integration Strategy'
    )
    print(f"Meeting triggered: {result}")

    # Get workflows for specific agent
    print("\n=== Grok Workflows ===")
    grok_workflows = bprd.get_agent_workflows('grok')
    for wf in grok_workflows:
        print(f"- {wf['name']}")
