---
name: learn
aliases: [extract-learnings, capture]
description: "Extract learnings from the current session and convert them to actionable repo content. Phase 4 of #1760."
model: sonnet
effort: medium
---

Run the learning extraction pipeline on recent sessions:

```bash
cd $(git rev-parse --show-toplevel 2>/dev/null || echo /mnt/local-analysis/workspace-hub)
bash scripts/learnings/extract-learnings.sh HEAD
```

Then present results to the user:
1. Show any patterns detected (repeated bugs, TDD gaps, skill updates)
2. Show any auto-generated issue recommendations
3. Ask: "Create these issues? [y/n] or edit first?"
