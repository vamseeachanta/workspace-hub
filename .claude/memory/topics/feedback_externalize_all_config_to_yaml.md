> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-14
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_externalize_all_config_to_yaml.md

---
name: feedback-externalize-all-config-to-yaml
description: "All work config (members, repos, data locations, material/code constants, thresholds) must live in reviewable/editable/trackable .yml — never hardcoded — because deliverables are industry-grade (many companies, not 1-2)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 71a79ff0-329a-44b2-9bb9-df290e7e5916
---

For the GTM parametric work (and deliverables generally), **all configuration must be externalized to `.yml`** — reviewable, editable, git-trackable — and **never embedded in code**. Stated 2026-06-01: "building for an industry not just 1-2 companies." Config explicitly includes: members/assignees, repos, **data locations / catalog paths**, material properties (SMYS/SMTS/grade), safety classes, code thresholds, find_min bounds — not just the sweep axes.

**Why:** an industry client/operator must reconfigure the deliverable for their own site/material/codes by editing yaml, with zero code edits. Hardcoded constants make the tool a 1-2-company artifact.

**How to apply:**
- Externalize sweep axes AND the "locked" engineering constants + data-location/catalog paths into yaml. This **elevates the deferred "Phase-2 constant migration" (ADR-0002) from optional to required** and generalizes it.
- The demo_02 §A "loud-refuse if you edit a constant" guard was a Phase-1 stopgap — the end state is those constants are *wired from yaml*, not refused.
- Consider whether a per-demo yaml suffices or a shared site/material/codes config library is needed (Codex review of the delegation plan to advise).
- Pairs with [[feedback_delegate_heavy_work_to_codex_for_tokens]] — also 2026-06-01 the user said "delegate to Codex as much as possible": route implementation/review to Codex, Claude orchestrates + verifies on disk. Open question the review must answer: who adversarially reviews Codex's output (Claude, or a second Codex)?
