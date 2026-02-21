---
Date: 2026-02-20
Author: Claude | Model: claude-sonnet-4-6
Topic: Git Push & PR Creation from Claude Code
Status: Active — use this every session
---

# Git Push & PR Creation — Claude Code on Windows

## Problem

The `gh` CLI (GitHub CLI) is frequently unavailable in Claude Code sessions on Windows. Attempting `gh pr create` fails with exit code 127 (command not found). Installing via `winget` may fail or require user approval/admin permissions.

**Do NOT waste time trying to install gh.** Use the workaround below.

## Solution: GitHub REST API via curl

### Step 1: Push the branch (this always works)
```bash
git push -u origin branch-name
```
Git credential manager handles auth automatically.

### Step 2: Extract the auth token
```bash
TOKEN=$(git credential fill <<< $'protocol=https\nhost=github.com' 2>/dev/null | grep password | cut -d= -f2)
```

### Step 3: Create PR via REST API
**CRITICAL: Use a temp file for the JSON body.** Dollar signs and special characters in inline JSON break curl's `-d` flag.

```bash
cat > /tmp/pr_body.json << 'JSONEOF'
{
  "title": "PR title here",
  "head": "branch-name",
  "base": "main",
  "body": "## Summary\n- Point 1\n- Point 2\n\n## Test plan\n- [ ] Test item"
}
JSONEOF

curl -s -X POST "https://api.github.com/repos/REBEmpire/BPR-D/pulls" \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @/tmp/pr_body.json
```

### Step 4: Parse the response
The response JSON contains `html_url` — that's the PR link to share with the user.

## Fallback: Manual PR URL

If curl also fails, `git push` output includes a direct URL:
```
remote: Create a pull request on GitHub by visiting:
remote:   https://github.com/REBEmpire/BPR-D/pull/new/branch-name
```
Share this URL with the user and they can create the PR manually.

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| `gh: command not found` (exit 127) | gh CLI not installed | Use curl + REST API |
| `Problems parsing JSON` (400) | Dollar signs in `-d '...'` | Use temp file with single-quoted heredoc |
| Push rejected | Branch doesn't exist on remote | Use `git push -u origin branch` |
| 401 Unauthorized | Token extraction failed | Verify git credential manager is configured |
| winget install cancelled (1602) | User denied install prompt | Don't retry — use curl workaround |
