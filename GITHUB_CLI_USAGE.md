# GitHub CLI Usage with Claude/MCP

## Problem
The `gh` CLI is authenticated but the GITHUB_TOKEN environment variable overrides it with a token that has limited permissions (read-only).

## Solution
Use `env -u GITHUB_TOKEN` to temporarily unset the environment variable and use the keyring authentication instead.

## Examples

### View Issue
```bash
env -u GITHUB_TOKEN gh issue view 44
```

### Add Comment to Issue
```bash
cat > /tmp/comment.txt << 'COMMENT'
This is my comment
COMMENT

env -u GITHUB_TOKEN gh api repos/OWNER/REPO/issues/44/comments -X POST -f body="$(cat /tmp/comment.txt)"
```

### Close Issue
```bash
env -u GITHUB_TOKEN gh issue close 44
```

### List Issues
```bash
env -u GITHUB_TOKEN gh issue list --state open
```

### Create Issue
```bash
env -u GITHUB_TOKEN gh issue create --title "Bug title" --body "Description"
```

### View PR
```bash
env -u GITHUB_TOKEN gh pr view 123
```

### List PRs
```bash
env -u GITHUB_TOKEN gh pr list
```

### Merge PR
```bash
env -u GITHUB_TOKEN gh pr merge 123 --squash
```

## Authentication Scopes

The keyring token has these scopes:
- `gist` - Create and manage gists
- `read:org` - Read organization data
- `repo` - Full control of private repositories (includes issues, PRs, etc.)

## Current Status

✅ **Successfully used to close Issue #44** (2026-02-14)
- Added comprehensive closing comment
- Closed the issue
- All operations completed successfully

## MCP Server Setup (Optional)

For now, we're using `gh` CLI directly with `env -u GITHUB_TOKEN` prefix.
A dedicated GitHub MCP server could be set up in the future if needed.

## Reference

- GitHub CLI docs: https://cli.github.com/manual/
- Issue #44 closed: https://github.com/DonHugo/sun_heat_and_ftx/issues/44
