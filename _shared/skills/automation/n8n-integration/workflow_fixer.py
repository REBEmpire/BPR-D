"""
Workflow Fixer for BPR&D n8n Workflows

This script fixes common issues in BPR&D workflows:
1. Adds missing Abacus agent to Team Meetings workflow
2. Updates deprecated Gemini model references
3. Connects tools to agents in General workflow
4. Adds missing storage and notification nodes

Usage:
    python workflow_fixer.py --workflow team-meetings --fix abacus
    python workflow_fixer.py --workflow team-meetings --fix gemini-model
    python workflow_fixer.py --workflow general --fix data-flow
    python workflow_fixer.py --list
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from n8n_client import N8NClient, BPRDWorkflows


class WorkflowFixer:
    """Fix common issues in BPR&D workflows"""

    TEAM_MEETING_ID = 'pDh6gPBEULb5kSx9'

    def __init__(self, client: Optional[N8NClient] = None):
        """Initialize workflow fixer"""
        self.client = client or N8NClient()

    def backup_workflow(self, workflow_id: str, backup_dir: str = './backups') -> str:
        """
        Backup workflow before modifications

        Args:
            workflow_id: Workflow ID to backup
            backup_dir: Directory to store backups

        Returns:
            Path to backup file
        """
        os.makedirs(backup_dir, exist_ok=True)

        workflow = self.client.get_workflow(workflow_id)
        backup_file = Path(backup_dir) / f"{workflow['name'].replace(' ', '_')}_{workflow_id}_backup.json"

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)

        print(f"✅ Backed up workflow to: {backup_file}")
        return str(backup_file)

    def fix_team_meetings_add_abacus(self, workflow_id: str = None) -> Dict:
        """
        Add Abacus agent to Team Meetings workflow

        Args:
            workflow_id: Workflow ID (defaults to known Team Meeting ID)

        Returns:
            Updated workflow
        """
        workflow_id = workflow_id or self.TEAM_MEETING_ID

        print(f"\n📝 Adding Abacus agent to workflow {workflow_id}...")

        # Backup first
        self.backup_workflow(workflow_id)

        # Get current workflow
        workflow = self.client.get_workflow(workflow_id)

        # Create Abacus agent node
        abacus_node = {
            "parameters": {
                "agent": "conversationalAgent",
                "text": "={{ $json.prompt }}",
                "options": {
                    "systemMessage": "You are Abacus, the Co-Second and Innovator of BPR&D. You bring unconventional approaches, question assumptions, and stress-test ideas from first principles. You're part of the Truth-Seekers faction with Gemini."
                }
            },
            "id": "abacus-agent-node",
            "name": "Abacus Agent",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 1.8,
            "position": [1400, 500],
            "credentials": {},
            "webhookId": ""
        }

        # Add HTTP Request sub-node for Abacus API call
        abacus_http_node = {
            "parameters": {
                "method": "POST",
                "url": "https://api.abacus.ai/chat/deployments/latest/predict",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "Authorization",
                            "value": f"Bearer {{{{$credentials.ABACUS_PRIMARY_KEY}}}}"
                        }
                    ]
                },
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "model", "value": "abacus-deep-agent"},
                        {"name": "messages", "value": "={{ $json.messages }}"}
                    ]
                },
                "options": {}
            },
            "id": "abacus-http-request",
            "name": "Abacus API Call",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1400, 600],
            "credentials": {
                "httpHeaderAuth": {
                    "id": "abacus-api-key",
                    "name": "Abacus API Key"
                }
            }
        }

        # Add nodes to workflow
        workflow['nodes'].append(abacus_node)
        workflow['nodes'].append(abacus_http_node)

        # Update connections (this is simplified - you may need to adjust based on actual flow)
        # The actual connection logic depends on your workflow structure

        print("✅ Abacus agent node created")
        print("⚠️  Note: You may need to manually connect the node in the n8n UI")
        print("   or update the connections dictionary in the workflow JSON")

        # Update workflow
        updated = self.client.update_workflow(workflow_id, workflow)
        print("✅ Workflow updated successfully")

        return updated

    def fix_team_meetings_update_gemini(self, workflow_id: str = None) -> Dict:
        """
        Update deprecated Gemini model in Team Meetings workflow

        Args:
            workflow_id: Workflow ID (defaults to known Team Meeting ID)

        Returns:
            Updated workflow
        """
        workflow_id = workflow_id or self.TEAM_MEETING_ID

        print(f"\n📝 Updating Gemini model in workflow {workflow_id}...")

        # Backup first
        self.backup_workflow(workflow_id)

        # Get current workflow
        workflow = self.client.get_workflow(workflow_id)

        # Find and update Gemini nodes
        updated_count = 0
        for node in workflow['nodes']:
            if node.get('name', '').lower().startswith('gemini'):
                # Update model parameter
                if 'parameters' in node and 'model' in node['parameters']:
                    old_model = node['parameters']['model']
                    if 'gemini-pro-latest' in str(old_model) or 'gemini-pro' in str(old_model):
                        node['parameters']['model'] = 'gemini-3-pro-preview'
                        print(f"  ✅ Updated {node['name']}: {old_model} → gemini-3-pro-preview")
                        updated_count += 1

        if updated_count == 0:
            print("  ℹ️  No Gemini model references found to update")
            return workflow

        # Update workflow
        updated = self.client.update_workflow(workflow_id, workflow)
        print(f"✅ Updated {updated_count} Gemini model reference(s)")

        return updated

    def fix_general_workflow_data_flow(self, workflow_id: str) -> Dict:
        """
        Add missing data flow components to General BPR&D workflow

        Args:
            workflow_id: Workflow ID

        Returns:
            Updated workflow
        """
        print(f"\n📝 Adding data flow components to workflow {workflow_id}...")

        # Backup first
        self.backup_workflow(workflow_id)

        # Get current workflow
        workflow = self.client.get_workflow(workflow_id)

        # Add merge node
        merge_node = {
            "parameters": {
                "mode": "combine",
                "combineBy": "combineAll"
            },
            "id": "merge-agent-responses",
            "name": "Merge Agent Responses",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 3,
            "position": [2000, 400]
        }

        # Add GitHub storage node
        github_node = {
            "parameters": {
                "operation": "create",
                "owner": "REBEmpire",
                "repository": "BPR-D",
                "filePath": "={{ 'results/' + $now.toFormat('yyyy-MM-dd') + '/' + $json.task_id + '.md' }}",
                "fileContent": "={{ $json.merged_results }}",
                "commitMessage": "={{ 'BPR&D Task Results: ' + $json.task_title }}"
            },
            "id": "store-to-github",
            "name": "Store Results to GitHub",
            "type": "n8n-nodes-base.github",
            "typeVersion": 1,
            "position": [2200, 400],
            "credentials": {
                "githubApi": {
                    "id": "github-bprd",
                    "name": "GitHub BPR&D"
                }
            }
        }

        # Add Telegram notification node
        telegram_node = {
            "parameters": {
                "chatId": "={{ $env.TELEGRAM_CHAT_ID }}",
                "text": "=Task Completed: {{ $json.task_title }}\\n\\nResults stored: {{ $json.github_url }}",
                "additionalFields": {
                    "parse_mode": "Markdown"
                }
            },
            "id": "notify-telegram",
            "name": "Notify Team via Telegram",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [2400, 400],
            "credentials": {
                "telegramApi": {
                    "id": "telegram-bprd",
                    "name": "Telegram BPR&D Bot"
                }
            }
        }

        # Add nodes to workflow
        workflow['nodes'].extend([merge_node, github_node, telegram_node])

        print("✅ Added merge, GitHub storage, and Telegram notification nodes")
        print("⚠️  Note: You need to manually connect these nodes in the n8n UI")

        # Update workflow
        updated = self.client.update_workflow(workflow_id, workflow)
        print("✅ Workflow updated successfully")

        return updated

    def list_workflows(self) -> None:
        """List all available workflows"""
        print("\n📋 Available Workflows:\n")
        workflows = self.client.list_workflows()

        for wf in workflows:
            status = "🟢 Active" if wf.get('active') else "⚪ Inactive"
            print(f"{status} - {wf['name']}")
            print(f"   ID: {wf['id']}")
            print(f"   Nodes: {len(wf.get('nodes', []))}")
            print(f"   Updated: {wf.get('updatedAt', 'Unknown')}")
            print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Fix common issues in BPR&D n8n workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all workflows
  python workflow_fixer.py --list

  # Add Abacus agent to Team Meetings workflow
  python workflow_fixer.py --workflow team-meetings --fix add-abacus

  # Update Gemini model in Team Meetings workflow
  python workflow_fixer.py --workflow team-meetings --fix update-gemini

  # Add data flow to General workflow
  python workflow_fixer.py --workflow WORKFLOW_ID --fix add-data-flow

  # Apply all fixes to Team Meetings
  python workflow_fixer.py --workflow team-meetings --fix all
        """
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available workflows'
    )

    parser.add_argument(
        '--workflow',
        type=str,
        help='Workflow ID or "team-meetings" for the known Team Meetings workflow'
    )

    parser.add_argument(
        '--fix',
        type=str,
        choices=['add-abacus', 'update-gemini', 'add-data-flow', 'all'],
        help='Which fix to apply'
    )

    parser.add_argument(
        '--backup-dir',
        type=str,
        default='./backups',
        help='Directory for workflow backups (default: ./backups)'
    )

    args = parser.parse_args()

    try:
        fixer = WorkflowFixer()

        if args.list:
            fixer.list_workflows()
            return

        if not args.workflow:
            parser.error("--workflow is required when not using --list")

        if not args.fix:
            parser.error("--fix is required when --workflow is specified")

        # Resolve workflow ID
        workflow_id = args.workflow
        if args.workflow.lower() == 'team-meetings':
            workflow_id = WorkflowFixer.TEAM_MEETING_ID

        # Apply fixes
        if args.fix == 'add-abacus' or args.fix == 'all':
            fixer.fix_team_meetings_add_abacus(workflow_id)

        if args.fix == 'update-gemini' or args.fix == 'all':
            fixer.fix_team_meetings_update_gemini(workflow_id)

        if args.fix == 'add-data-flow':
            fixer.fix_general_workflow_data_flow(workflow_id)

        print("\n✅ All fixes applied successfully!")
        print(f"   Backups saved to: {args.backup_dir}")
        print("\n📝 Next steps:")
        print("   1. Review the updated workflow in n8n UI")
        print("   2. Manually connect any new nodes")
        print("   3. Test the workflow with a sample execution")
        print("   4. Activate the workflow when ready")

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
