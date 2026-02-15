"""
Test script for n8n API integration

This script demonstrates how to interact with n8n workflows programmatically.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from n8n_client import N8NClient, BPRDWorkflows


def main():
    """Test n8n API integration"""

    print("=" * 60)
    print("BPR&D n8n API Integration Test")
    print("=" * 60)

    # Check environment variables
    print("\n1. Checking environment variables...")
    api_key = os.getenv('N8N_API_KEY')
    base_url = os.getenv('N8N_BASE_URL')

    if not api_key:
        print("❌ N8N_API_KEY not set in environment")
        print("   Please add it to your .env file")
        return

    if not base_url:
        print("⚠️  N8N_BASE_URL not set, using default: https://n8n.bprd.io")

    print("✅ Environment configured")

    # Initialize client
    print("\n2. Initializing n8n client...")
    try:
        client = N8NClient()
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    # List workflows
    print("\n3. Listing workflows...")
    try:
        workflows = client.list_workflows()
        print(f"✅ Found {len(workflows)} workflows:")
        for wf in workflows[:5]:  # Show first 5
            status = "🟢 Active" if wf.get('active') else "⚪ Inactive"
            print(f"   {status} - {wf['name']} (ID: {wf['id']})")
        if len(workflows) > 5:
            print(f"   ... and {len(workflows) - 5} more")
    except Exception as e:
        print(f"❌ Failed to list workflows: {e}")
        return

    # Get team meeting workflow
    print("\n4. Checking BPR&D Team Meeting workflow...")
    try:
        workflow = client.get_workflow('pDh6gPBEULb5kSx9')
        print(f"✅ Team Meeting Workflow: {workflow['name']}")
        print(f"   Status: {'🟢 Active' if workflow.get('active') else '⚪ Inactive'}")
        print(f"   Nodes: {len(workflow.get('nodes', []))}")
    except Exception as e:
        print(f"⚠️  Could not retrieve team meeting workflow: {e}")

    # Test BPR&D helper
    print("\n5. Testing BPR&D workflow helper...")
    try:
        bprd = BPRDWorkflows(client)
        print("✅ BPR&D helper initialized")

        # Get agent workflows (without executing)
        print("\n   Checking for agent-specific workflows...")
        for agent in ['grok', 'claude', 'gemini', 'abacus']:
            try:
                agent_wfs = bprd.get_agent_workflows(agent)
                print(f"   - {agent.title()}: {len(agent_wfs)} workflows")
            except:
                print(f"   - {agent.title()}: Unable to retrieve")

    except Exception as e:
        print(f"❌ Failed to test BPR&D helper: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nYou can now use the n8n API integration in your workflows.")
    print("\nNext steps:")
    print("1. Review _shared/skills/automation/n8n-integration/SKILL.md")
    print("2. Import and use N8NClient or BPRDWorkflows in your code")
    print("3. Trigger workflows programmatically!")
    print("\nExample:")
    print("  from n8n_client import BPRDWorkflows")
    print("  bprd = BPRDWorkflows()")
    print("  bprd.trigger_team_meeting(agenda='Your meeting topic')")


if __name__ == '__main__':
    main()
