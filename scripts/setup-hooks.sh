#!/bin/bash
# BPR&D Pre-commit Hook Setup
# Run this script after cloning the repository to enable v2 validation hooks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installing BPR&D v2 pre-commit hooks..."

# Copy pre-commit hook
cp "$SCRIPT_DIR/v2-migration/pre-commit-check.sh" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"

echo "✓ Pre-commit hook installed successfully"
echo ""
echo "The hook will enforce:"
echo "  - Task ID format (BPRD-YYYY-NNNN)"
echo "  - No duplicate file content"
echo "  - Handoffs in _handoffs/ directory"
echo "  - Required fields in task files"
