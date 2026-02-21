#!/bin/bash

# BPR&D V2 Pre-commit Hook
# 
# Purpose:
# - Enforce file naming conventions
# - Prevent duplicate file creation
# - Validate task ID format
# - Block handoffs in wrong locations
#
# Installation:
#   cp scripts/v2-migration/pre-commit-check.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Running BPR&D V2 pre-commit checks..."
echo ""

ERRORS=0
WARNINGS=0

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo -e "${GREEN}No files staged for commit${NC}"
    exit 0
fi

# ============================================================================
# CHECK 1: Handoff files in wrong locations
# ============================================================================
echo "[1/5] Checking handoff file locations..."

for file in $STAGED_FILES; do
    if echo "$file" | grep -qE 'handoff-.*\.md$'; then
        # Check if it's in the canonical location
        if ! echo "$file" | grep -qE '^_handoffs/(active|archived)/'; then
            echo -e "${RED}ERROR: Handoff file in wrong location:${NC}"
            echo "       $file"
            echo "       Handoffs must be in _handoffs/active/ or _handoffs/archived/"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# ============================================================================
# CHECK 2: Task ID format validation
# ============================================================================
echo "[2/5] Validating task ID format..."

for file in $STAGED_FILES; do
    if echo "$file" | grep -qE '^tasks/.*\.md$'; then
        filename=$(basename "$file")
        # Extract task ID from filename
        if ! echo "$filename" | grep -qE '^BPRD-[0-9]{4}-[0-9]{4}\.md$'; then
            echo -e "${RED}ERROR: Invalid task file name:${NC}"
            echo "       $file"
            echo "       Task files must be named BPRD-YYYY-NNNN.md"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# ============================================================================
# CHECK 3: Prohibited patterns in filenames
# ============================================================================
echo "[3/5] Checking for prohibited filename patterns..."

for file in $STAGED_FILES; do
    filename=$(basename "$file")
    
    # Check for timestamp suffixes (e.g., file_063331.md)
    if echo "$filename" | grep -qE '_[0-9]{6}\.(md|yaml|json)$'; then
        echo -e "${RED}ERROR: Timestamp suffix in filename:${NC}"
        echo "       $file"
        echo "       Remove timestamp suffix from filename"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for copy indicators
    if echo "$filename" | grep -qE '(\(copy\)|\([0-9]+\)|-copy|_copy)\.(md|yaml|json)$'; then
        echo -e "${RED}ERROR: Copy indicator in filename:${NC}"
        echo "       $file"
        echo "       Remove copy indicator from filename"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for spaces in filenames
    if echo "$filename" | grep -q ' '; then
        echo -e "${YELLOW}WARNING: Space in filename:${NC}"
        echo "         $file"
        echo "         Consider using dashes instead of spaces"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# ============================================================================
# CHECK 4: Duplicate content detection
# ============================================================================
echo "[4/5] Checking for duplicate content..."

# Build list of hashes for staged files
declare -A FILE_HASHES

for file in $STAGED_FILES; do
    if [ -f "$file" ] && echo "$file" | grep -qE '\.(md|yaml|json)$'; then
        hash=$(git show :"$file" 2>/dev/null | md5sum | cut -d' ' -f1)
        
        if [ -n "${FILE_HASHES[$hash]}" ]; then
            echo -e "${RED}ERROR: Duplicate content detected:${NC}"
            echo "       $file"
            echo "       Same content as: ${FILE_HASHES[$hash]}"
            ERRORS=$((ERRORS + 1))
        else
            FILE_HASHES[$hash]=$file
        fi
    fi
done

# ============================================================================
# CHECK 5: Required fields in task files
# ============================================================================
echo "[5/5] Validating task file required fields..."

for file in $STAGED_FILES; do
    if echo "$file" | grep -qE '^tasks/(active|backlog|review|blocked)/.*\.md$'; then
        content=$(git show :"$file" 2>/dev/null)
        
        # Check for required fields
        required_fields=("id:" "source:" "skill_web_node:" "owner:" "status:" "verification_criteria:")
        
        for field in "${required_fields[@]}"; do
            if ! echo "$content" | grep -q "^$field"; then
                echo -e "${RED}ERROR: Missing required field '$field' in:${NC}"
                echo "       $file"
                ERRORS=$((ERRORS + 1))
            fi
        done
        
        # Check if status is valid
        status=$(echo "$content" | grep "^status:" | cut -d':' -f2 | tr -d ' ')
        valid_statuses="Created Assigned In-Progress Review Verified Complete Blocked Failed"
        
        if [ -n "$status" ] && ! echo "$valid_statuses" | grep -qw "$status"; then
            echo -e "${RED}ERROR: Invalid status '$status' in:${NC}"
            echo "       $file"
            echo "       Valid statuses: $valid_statuses"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# ============================================================================
# CHECK 6: Handoff required fields
# ============================================================================
echo "[6/6] Validating handoff required fields..."

for file in $STAGED_FILES; do
    if echo "$file" | grep -qE '^_handoffs/active/handoff-.*\.md$'; then
        content=$(git show :"$file" 2>/dev/null)
        
        # Check for required fields
        required_fields=("handoff_id:" "from_agent:" "to_agent:" "related_task:" "status:" "title:")
        
        for field in "${required_fields[@]}"; do
            if ! echo "$content" | grep -q "^$field"; then
                echo -e "${RED}ERROR: Missing required field '$field' in handoff:${NC}"
                echo "       $file"
                ERRORS=$((ERRORS + 1))
            fi
        done
    fi
done

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "======================================"
echo "Pre-commit Check Summary"
echo "======================================"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}FAILED: $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}Plus $WARNINGS warning(s)${NC}"
    fi
    echo ""
    echo "Commit blocked. Please fix the errors above."
    echo ""
    echo "To bypass this check (not recommended):"
    echo "  git commit --no-verify"
    exit 1
else
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}PASSED with $WARNINGS warning(s)${NC}"
    else
        echo -e "${GREEN}PASSED: All checks successful${NC}"
    fi
    exit 0
fi
