---
name: interoperability-setup-new-machine-or-after-fresh-clone
description: 'Sub-skill of interoperability: Setup (new machine or after fresh clone).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Setup (new machine or after fresh clone)

## Setup (new machine or after fresh clone)


```bash
# 1. Install uv (once per machine)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install hooks (once per clone)
bash scripts/operations/setup-hooks.sh

# 3. Verify
git config core.hooksPath          # → .claude/hooks
ls -la .claude/hooks/pre-commit    # → executable
command -v uv                      # → found
```
