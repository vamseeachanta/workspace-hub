---
name: flywheel-closeout
description: Use this at the end of substantial repo or agent waves to convert evidence-backed lessons into proposed durable assets: skills, scripts, rules/checks, prompt templates, docs, or issues. Always use it when the user mentions flywheel, wave closeout, repo ecosystem learning, durable asset promotion, or learning-to-tools.
---

# Flywheel Closeout

Use this skill after meaningful agent waves, repeated defects, or cross-provider review cycles.

## Workflow

1. Gather explicit source evidence: issue URLs, PR URLs, commit SHAs, handoff paths, and review artifacts.
2. Run `uv run --no-project python scripts/workflow/flywheel_closeout.py` with `--mode propose`.
3. Inspect `manifest.json`, `report.html`, and `issue-drafts/`.
4. Route local behavior changes to the local repo. Route skills, shared scripts, rules/checks, provider workflow, and review-artifact contracts to `workspace-hub`.
5. Keep all outputs advisory in this first slice. Do not create issues, comments, labels, or approvals from this skill.

## Gates

Preserve the normal repo workflow: issue, plan, adversarial review, user approval, implementation, code/artifact review, legal/security scan, and pre-completion cleanup audit.

Missing flywheel evidence is advisory until a later approved enforcement issue hardens it.
