#!/usr/bin/env python3
"""
BPR&D V2 Migration Cleanup Script

Purpose:
- Remove duplicate files from research/epstein-daily/processed/
- Consolidate handoffs to _handoffs/ directory
- Generate migration report

Usage:
    python cleanup.py [--dry-run] [--report-only]
"""

import os
import sys
import hashlib
import shutil
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import argparse
import re

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
HANDOFF_CANONICAL = REPO_ROOT / "_handoffs"
HANDOFF_ACTIVE = HANDOFF_CANONICAL / "active"
HANDOFF_ARCHIVED = HANDOFF_CANONICAL / "archived"
REPORTS_DIR = REPO_ROOT / "reports" / "v2-migration"

# Patterns
HANDOFF_PATTERN = re.compile(r'handoff-.*\.md$', re.IGNORECASE)
TASK_ID_PATTERN = re.compile(r'BPRD-\d{4}-\d{4}')

# Directories that should NOT contain handoffs
INVALID_HANDOFF_LOCATIONS = [
    "research/epstein-daily/processed",
    "_agents/*/_handoffs",
    "_agents/*/context",
]


def compute_file_hash(filepath):
    """Compute MD5 hash of file contents."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_all_handoffs(root):
    """Find all handoff files in the repository."""
    handoffs = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip .git directory
        if '.git' in dirpath:
            continue
        for filename in filenames:
            if HANDOFF_PATTERN.match(filename):
                filepath = Path(dirpath) / filename
                handoffs.append({
                    'path': filepath,
                    'relative': filepath.relative_to(root),
                    'hash': compute_file_hash(filepath),
                    'size': filepath.stat().st_size,
                    'mtime': filepath.stat().st_mtime,
                })
    return handoffs


def find_duplicates(files):
    """Group files by content hash to find duplicates."""
    by_hash = defaultdict(list)
    for f in files:
        by_hash[f['hash']].append(f)
    
    duplicates = {h: files for h, files in by_hash.items() if len(files) > 1}
    return duplicates


def is_invalid_location(filepath, root):
    """Check if file is in an invalid location."""
    rel_path = str(filepath.relative_to(root))
    
    for pattern in INVALID_HANDOFF_LOCATIONS:
        if '*' in pattern:
            # Simple glob pattern
            parts = pattern.split('*')
            if len(parts) == 2:
                if rel_path.startswith(parts[0]) and parts[1] in rel_path:
                    return True
        else:
            if rel_path.startswith(pattern):
                return True
    return False


def find_files_to_clean(root):
    """Find files in research/epstein-daily/processed that don't belong."""
    processed_dir = root / "research" / "epstein-daily" / "processed"
    if not processed_dir.exists():
        return []
    
    files_to_clean = []
    for dirpath, dirnames, filenames in os.walk(processed_dir):
        for filename in filenames:
            filepath = Path(dirpath) / filename
            # Check if it's a handoff file (shouldn't be here)
            if HANDOFF_PATTERN.match(filename):
                files_to_clean.append({
                    'path': filepath,
                    'relative': filepath.relative_to(root),
                    'reason': 'handoff_in_wrong_location',
                })
            # Check for timestamp suffixes (e.g., file_063331.md)
            elif re.search(r'_\d{6}\.md$', filename):
                files_to_clean.append({
                    'path': filepath,
                    'relative': filepath.relative_to(root),
                    'reason': 'timestamp_duplicate',
                })
    return files_to_clean


def consolidate_handoffs(handoffs, root, dry_run=True):
    """Move handoffs to canonical location."""
    actions = []
    
    for handoff in handoffs:
        if is_invalid_location(handoff['path'], root):
            # Determine destination
            filename = handoff['path'].name
            dest = HANDOFF_ACTIVE / filename
            
            # Check if already exists at destination
            if dest.exists():
                existing_hash = compute_file_hash(dest)
                if existing_hash == handoff['hash']:
                    actions.append({
                        'action': 'delete_duplicate',
                        'source': str(handoff['relative']),
                        'reason': 'identical copy exists in canonical location',
                    })
                else:
                    # Different content - keep newer
                    existing_mtime = dest.stat().st_mtime
                    if handoff['mtime'] > existing_mtime:
                        actions.append({
                            'action': 'replace',
                            'source': str(handoff['relative']),
                            'dest': str(dest.relative_to(root)),
                            'reason': 'source is newer',
                        })
                    else:
                        actions.append({
                            'action': 'delete_duplicate',
                            'source': str(handoff['relative']),
                            'reason': 'canonical version is newer',
                        })
            else:
                actions.append({
                    'action': 'move',
                    'source': str(handoff['relative']),
                    'dest': str(dest.relative_to(root)),
                })
    
    return actions


def execute_cleanup(actions, root, dry_run=True):
    """Execute the cleanup actions."""
    results = []
    
    for action in actions:
        if dry_run:
            results.append({
                'action': action,
                'status': 'dry_run',
            })
            continue
        
        try:
            source = root / action.get('source', '')
            
            if action['action'] == 'delete_duplicate':
                source.unlink()
                results.append({'action': action, 'status': 'deleted'})
            
            elif action['action'] == 'move':
                dest = root / action['dest']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(dest))
                results.append({'action': action, 'status': 'moved'})
            
            elif action['action'] == 'replace':
                dest = root / action['dest']
                shutil.copy2(str(source), str(dest))
                source.unlink()
                results.append({'action': action, 'status': 'replaced'})
        
        except Exception as e:
            results.append({'action': action, 'status': 'error', 'error': str(e)})
    
    return results


def generate_report(handoffs, duplicates, cleanup_files, actions, results):
    """Generate migration report."""
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_handoffs_found': len(handoffs),
            'duplicate_groups': len(duplicates),
            'total_duplicates': sum(len(files) - 1 for files in duplicates.values()),
            'files_in_wrong_location': len(cleanup_files),
            'actions_planned': len(actions),
        },
        'duplicates': {
            hash_val: [
                {
                    'path': str(f['relative']),
                    'size': f['size'],
                    'modified': datetime.fromtimestamp(f['mtime']).isoformat(),
                }
                for f in files
            ]
            for hash_val, files in duplicates.items()
        },
        'files_in_wrong_location': [
            {'path': str(f['relative']), 'reason': f['reason']}
            for f in cleanup_files
        ],
        'planned_actions': actions,
        'execution_results': results,
    }
    return report


def print_report(report):
    """Print human-readable report."""
    print("\n" + "="*70)
    print("BPR&D V2 MIGRATION CLEANUP REPORT")
    print("="*70)
    print(f"Generated: {report['generated_at']}")
    print()
    
    summary = report['summary']
    print("SUMMARY")
    print("-"*40)
    print(f"  Total handoff files found: {summary['total_handoffs_found']}")
    print(f"  Duplicate groups: {summary['duplicate_groups']}")
    print(f"  Total duplicate files: {summary['total_duplicates']}")
    print(f"  Files in wrong locations: {summary['files_in_wrong_location']}")
    print(f"  Actions planned: {summary['actions_planned']}")
    print()
    
    if report['duplicates']:
        print("DUPLICATES")
        print("-"*40)
        for hash_val, files in report['duplicates'].items():
            print(f"  Hash: {hash_val[:8]}...")
            for f in files:
                print(f"    - {f['path']}")
        print()
    
    if report['files_in_wrong_location']:
        print("FILES IN WRONG LOCATIONS")
        print("-"*40)
        for f in report['files_in_wrong_location']:
            print(f"  - {f['path']} ({f['reason']})")
        print()
    
    if report['planned_actions']:
        print("PLANNED ACTIONS")
        print("-"*40)
        for action in report['planned_actions']:
            print(f"  [{action['action'].upper()}] {action.get('source', 'N/A')}")
            if 'dest' in action:
                print(f"    -> {action['dest']}")
            if 'reason' in action:
                print(f"    Reason: {action['reason']}")
        print()
    
    if report['execution_results']:
        print("EXECUTION RESULTS")
        print("-"*40)
        for result in report['execution_results']:
            status = result['status']
            action = result['action']
            print(f"  [{status.upper()}] {action.get('action', '')} - {action.get('source', '')}")
        print()
    
    print("="*70)


def ensure_directories():
    """Ensure canonical handoff directories exist."""
    HANDOFF_CANONICAL.mkdir(parents=True, exist_ok=True)
    HANDOFF_ACTIVE.mkdir(parents=True, exist_ok=True)
    HANDOFF_ARCHIVED.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description='BPR&D V2 Migration Cleanup Script'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--report-only', '-r',
        action='store_true',
        help='Generate report without executing cleanup'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output report to file'
    )
    
    args = parser.parse_args()
    
    print("BPR&D V2 Migration Cleanup")
    print(f"Repository root: {REPO_ROOT}")
    print()
    
    # Ensure directories exist
    ensure_directories()
    
    # Find all handoffs
    print("Scanning for handoff files...")
    handoffs = find_all_handoffs(REPO_ROOT)
    print(f"  Found {len(handoffs)} handoff files")
    
    # Find duplicates
    print("Analyzing duplicates...")
    duplicates = find_duplicates(handoffs)
    print(f"  Found {len(duplicates)} duplicate groups")
    
    # Find files to clean
    print("Finding files in wrong locations...")
    cleanup_files = find_files_to_clean(REPO_ROOT)
    print(f"  Found {len(cleanup_files)} files to clean")
    
    # Plan consolidation
    print("Planning consolidation...")
    actions = consolidate_handoffs(handoffs, REPO_ROOT, dry_run=True)
    print(f"  Planned {len(actions)} actions")
    
    # Execute if not report-only
    results = []
    if not args.report_only:
        dry_run = args.dry_run
        if dry_run:
            print("\nDRY RUN MODE - No changes will be made")
        else:
            print("\nExecuting cleanup...")
        results = execute_cleanup(actions, REPO_ROOT, dry_run=dry_run)
    
    # Generate report
    report = generate_report(handoffs, duplicates, cleanup_files, actions, results)
    
    # Output report
    print_report(report)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {output_path}")
    else:
        # Save to default location
        report_file = REPORTS_DIR / f"cleanup-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {report_file}")
    
    return 0 if not results or all(r['status'] != 'error' for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
