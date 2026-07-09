# Context Briefs

This directory holds **external context briefs** for long-running tasks.

## Why?

OpenCode's auto-compaction summarizer copies the entire initial prompt
verbatim into each compaction cycle. When you paste a 4000-word brief
inline, it gets duplicated 5+ times, wasting context window.

Auto-compaction is disabled via `compaction.auto: false` in `opencode.json`.

## How to use

1. Create a brief file here: e.g. `issue-15-audit-logging.md`
2. Start your opencode session with a short reference:

   ```
   Read .opencode/context/issue-15-audit-logging.md for full requirements.
   Then implement the audit logging endpoints per the acceptance criteria.
   ```

3. The compaction summary will only carry the short reference, not the
   full 4000-word brief. The agent can re-read the file when needed.

## Naming convention

```
<issue-or-topic>-<short-description>.md
```

Examples:
- `issue-15-audit-logging.md`
- `issue-42-dashboard-redesign.md`
- `pellet-heating-analysis.md`

## Template

See `_TEMPLATE.md` in this directory for a starting structure.
