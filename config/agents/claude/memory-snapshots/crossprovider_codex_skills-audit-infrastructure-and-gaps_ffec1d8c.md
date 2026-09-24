---
name: crossprovider codex skills-audit-infrastructure-and-gaps
description: Skills audit infrastructure and gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [skills-infrastructure, inventory-gap, audit-subsystem]
---

Skill auditing subsystem exists in `scripts/skills/weekly_skills_audit.py` (from #2281/#2486) with test coverage and cron wrapper at `scripts/cron/skills-curation.sh`. Known gap: does not model tracked-vs-filesystem inventory or filesystem-only active skills as first-class findings. As of 2026-04-25, 6 filesystem-only active skills were untracked (72 untracked total).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
