#!/usr/bin/env python3
"""Meeting-Code-Deployer CLI - Process meeting transcripts into tasks and code.

Usage:
    python scripts/meeting-code-deployer.py <transcript_path> [options]

Examples:
    # Dry run (preview what would be created)
    python scripts/meeting-code-deployer.py meetings/logs/sample-meeting.md --dry-run
    
    # Process and auto-commit
    python scripts/meeting-code-deployer.py meetings/logs/sample-meeting.md --auto-commit
    
    # Process and create PR
    python scripts/meeting-code-deployer.py meetings/logs/sample-meeting.md --create-pr
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from _agents.meeting_code_deployer.deployer import MeetingCodeDeployer


def main():
    parser = argparse.ArgumentParser(
        description="Meeting-Code-Deployer: Transform meeting transcripts into actionable tasks and code.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s meetings/logs/sample-meeting.md --dry-run
      Preview what would be created without making changes
  
  %(prog)s meetings/logs/sample-meeting.md --auto-commit
      Process transcript and commit changes
  
  %(prog)s meetings/logs/sample-meeting.md --create-pr
      Process transcript and create a PR

For more information, see:
  docs/v2-architecture/meeting-code-deployer.md
"""
    )
    
    parser.add_argument(
        'transcript',
        help='Path to meeting transcript file (markdown)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without creating files'
    )
    
    parser.add_argument(
        '--auto-commit',
        action='store_true',
        help='Automatically commit changes after processing'
    )
    
    parser.add_argument(
        '--create-pr',
        action='store_true',
        help='Create a PR with the changes (requires --auto-commit)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to custom config file (default: _agents/meeting-code-deployer/config.yaml)'
    )
    
    parser.add_argument(
        '--output',
        help='Path for deployment report output'
    )
    
    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Report output format (default: markdown)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Meeting-Code-Deployer v2.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate transcript path
    transcript_path = Path(args.transcript)
    if not transcript_path.exists():
        print(f"❌ Error: Transcript not found: {args.transcript}")
        sys.exit(1)
    
    # Validate PR requires commit
    if args.create_pr and not args.auto_commit:
        print("❌ Error: --create-pr requires --auto-commit")
        sys.exit(1)
    
    # Initialize deployer
    try:
        deployer = MeetingCodeDeployer(
            config_path=args.config,
            repo_root=str(project_root)
        )
    except Exception as e:
        print(f"❌ Error initializing deployer: {e}")
        sys.exit(1)
    
    # Print banner
    if not args.quiet:
        print("\n" + "="*60)
        print("  🚀 Meeting-Code-Deployer v2.0.0")
        print("="*60)
        print(f"\n  Transcript: {args.transcript}")
        print(f"  Mode: {'DRY RUN' if args.dry_run else 'DEPLOY'}")
        if args.auto_commit:
            print("  Auto-commit: Enabled")
        if args.create_pr:
            print("  Create PR: Enabled")
        print("\n" + "-"*60 + "\n")
    
    # Process transcript
    try:
        report = deployer.process(
            transcript_path=str(transcript_path),
            dry_run=args.dry_run,
            auto_commit=args.auto_commit,
            create_pr=args.create_pr,
            verbose=not args.quiet
        )
    except Exception as e:
        print(f"❌ Error processing transcript: {e}")
        sys.exit(1)
    
    # Save report
    if args.output:
        report_path = deployer.save_report(report, args.output, args.format)
        if not args.quiet:
            print(f"\n📄 Report saved to: {report_path}")
    
    # Print summary
    if not args.quiet:
        print("\n" + "-"*60)
        print("\n📊 SUMMARY")
        print(f"   Meeting ID: {report.meeting_id}")
        print(f"   Action Items: {report.action_items_found}")
        print(f"   Decisions: {report.decisions_found}")
        print(f"   Tasks Created: {len(report.tasks_created)}")
        print(f"   Files Generated: {len(report.files_generated)}")
        print(f"   Skill Links: {report.skills_linked}")
        print(f"   Skill Gaps: {report.skill_gaps}")
        
        if report.warnings:
            print(f"\n⚠️  Warnings: {len(report.warnings)}")
            for w in report.warnings[:3]:
                print(f"    - {w}")
        
        if report.errors:
            print(f"\n❌ Errors: {len(report.errors)}")
            for e in report.errors:
                print(f"    - {e}")
        
        print("\n" + "="*60 + "\n")
    
    # Print the report
    if not args.quiet:
        print(deployer.generate_report(report, args.format))
    
    # Exit with error code if errors
    sys.exit(1 if report.errors else 0)


if __name__ == '__main__':
    main()
