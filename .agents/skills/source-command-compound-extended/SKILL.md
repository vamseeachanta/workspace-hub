---
name: "source-command-compound-extended"
description: "Run cross-agent memory bridge. Sync learnings between machine agents, update shared knowledge. Phase 5 of #1760."
---

# source-command-compound-extended

Use this skill when the user asks to run the migrated source command `compound-extended`.

## Command Template

Run the cross-agent bridge:

```bash
cd $(git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)
bash scripts/learnings/cross-agent-bridge.sh bridge
```

Then:
1. Summarize what was bridged
2. Report any compliance warnings
3. Show skill sync status across repos
