---
name: ecosystem-health-output-format
description: 'Sub-skill of ecosystem-health: Output Format.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Output Format

## Output Format


```
=== Ecosystem Health Check — 2026-02-19 ===

Group 1: Cross-Platform Guard
  [PASS] Hook wired: .claude/hooks
  [PASS] pre-commit: executable
  [FAIL] uv: not found in PATH
         Fix: curl -LsSf https://astral.sh/uv/install.sh | sh

Group 2: Work Queue Integrity
  [PASS] Index generates: exit 0
  [WARN] 2 working/ items missing plan_reviewed: WRK-205, WRK-199

Group 3: Skill Frontmatter
  [PASS] All skills have required frontmatter
  [WARN] 3 asymmetric related_skills links (see WRK-207)

Group 4: Signal Backlog
  [PASS] 12 pending signals (< 50)

Summary: 1 FAIL, 2 WARN, 11 PASS
```
