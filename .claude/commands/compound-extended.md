---
name: compound
aliases: [bridge, sync-memory]
description: "Run cross-agent memory bridge. Sync learnings between machine agents, update shared knowledge. Phase 5 of #1760."
model: haiku
effort: low
---

Run the cross-agent bridge:

```bash
cd $(git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)
bash scripts/learnings/cross-agent-bridge.sh bridge
```

Then:
1. Summarize what was bridged
2. Report any compliance warnings
3. Show skill sync status across repos
