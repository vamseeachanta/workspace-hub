# Archived Skill: `plan-review-handoff-verification`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/plan-review-handoff-verification`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/plan-review-handoff-verification`
Consolidation date: 2026-04-29

---

---
name: plan-review-handoff-verification
description: Verify a parked GitHub issue plan-review handoff across live labels, local markers, README rows, canonical review artifacts, and stale plan-body evidence before reporting next action.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [github, planning, handoff, governance, verification]
related_skills:
  - issue-planning-mode
  - plan-exit-governance-drift-handoff
  - plan-review-artifact-authority-and-approval-drift
---

# Plan-review handoff verification

Use this when a user provides or references an exit handoff for a GitHub issue parked in `status:plan-review`, especially after iterative adversarial review and approval-state drift cleanup.

## Workflow

1. Load the canonical planning skill (`issue-planning-mode`) first.
2. Read the handoff file and extract the asserted state surfaces:
   - GitHub issue state and `status:*` labels
   - `.planning/plan-approved/<issue>.md` marker state
   - `docs/plans/README.md` row status
   - canonical provider review artifact paths and verdicts
   - stated clean next action / do-not-do guidance
3. Verify the live GitHub state with `gh issue view <issue> --json state,labels,title,url`.
4. Verify the local approval marker presence/absence.
5. Search `docs/plans/README.md` for the issue row and confirm the row status and note match the intended parked state.
6. Read or scan the canonical `scripts/review/results/*plan-<issue>-<provider>.md` artifacts and extract each verdict.
7. Read the local plan header and scan the plan body for stale older rerun evidence (for example a review-artifacts line still saying `r11 MAJOR` while canonical artifacts now say `r16 MINOR`).
8. Report the operational state and next valid action. Do not implement, approve, recreate approval markers, or rewrite broad plan content unless the user explicitly asks.

## Classification rules

- Operational surfaces are, in order: live GitHub status labels, local approval marker, `docs/plans/README.md` row, canonical review artifacts.
- If those surfaces align to `status:plan-review` with no approval marker and no fresh MAJOR verdicts, classify the issue as parked/exit-clean for user review.
- If the local plan header/body contains stale historical evidence while the operational surfaces are aligned, report it as non-blocking polish/drift. Do not treat it as approval or implementation authority.
- If a stale approval marker or `status:plan-approved` label remains after fresh review evidence says the issue is back in review, perform the governance cleanup from `issue-planning-mode` instead of merely noting it.

## Minimal verification command pattern

Use one script to reduce missed surfaces:

```python
from hermes_tools import terminal, search_files, read_file
import os, json, re

issue = 2460
state = terminal(f"gh issue view {issue} --json state,labels,title,url", timeout=60)
marker_exists = os.path.exists(f".planning/plan-approved/{issue}.md")
readme = search_files(str(issue), target="content", path="docs/plans/README.md", output_mode="content")

for provider in ["claude", "codex", "gemini"]:
    path = f"scripts/review/results/2026-04-23-plan-{issue}-{provider}.md"
    # read_file(path) and extract Verdict: APPROVE|MINOR|MAJOR
```

Then separately scan the plan file for stale older strings such as `MAJOR`, `UNAVAILABLE`, or older rerun IDs when the latest artifacts have advanced.

## Output pattern

State the result as:

1. GitHub issue state and live status labels
2. Local approval marker state
3. README row state
4. Provider artifact verdicts
5. Local plan file/header state
6. Conclusion: exit-clean vs drift found
7. Next valid action and prohibited action

Keep the response short and explicit: if parked for user approval, say no implementation should start yet.
