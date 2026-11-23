# Archived Skill: `github-issue-automation-evidence-fields`

Original path: `/home/vamsee/.hermes/skills/github/github-issue-automation-evidence-fields`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-issue-automation-evidence-fields`
Consolidation date: 2026-04-29

---

---
name: github-issue-automation-evidence-fields
description: Use when building GitHub issue classifiers, dashboards, closeout verifiers, or queue/report automation that depends on comments, approval evidence, or linked PR handoff state.
version: 1.0.0
author: Hermes Agent
category: github
tags: [github, gh-cli, issues, automation, evidence, dashboards, closeout]
related_skills:
  - github-issues
  - gh-work-execution
---

# GitHub Issue Automation Evidence Fields

## When to use

Use this skill for the class of tasks where you are building or validating automation over GitHub issues and the automation must classify issues based on evidence beyond labels/title/body, such as:
- issue comments
- approval request / approval marker evidence
- linked or closing PR evidence
- handoff comments
- closeout verification state
- queue dashboards or lane classifiers

Do not use this for simple one-off label changes or issue comments; `github-issues` is enough for those.

## Core pattern: list broad, then enrich

`gh issue list` is good for the broad candidate sweep, but it does not provide enough evidence-bearing detail for robust automation. If your classifier/validator depends on comments or PR linkage, enrich each candidate with `gh issue view`.

```bash
# 1) Broad sweep for candidate numbers and cheap metadata
gh issue list --state open --limit 200 --json number,title,labels,state,updatedAt

# 2) Per-issue enrichment for evidence-bearing fields
gh issue view <number> --json number,title,state,labels,comments,closedByPullRequestsReferences,url
```

## Important gh field gotcha

For linked/closing PR evidence, use:

```bash
gh issue view <number> --json closedByPullRequestsReferences
```

Do not use `closedByPullRequests`; it is not a valid `gh issue view --json` field and will fail.

Quick verification:

```bash
gh issue view <number> --json comments,closedByPullRequestsReferences --jq 'keys'
# expected includes: ["closedByPullRequestsReferences", "comments"]
```

## Classifier design rules

1. Treat missing evidence channels as observability degradation, not proof of absence.
   - Example: a missing dispatch ledger means global degraded visibility; it does not prove every issue has no active dispatch.
2. Separate global warnings from per-issue blockers.
   - Global warnings belong in top-level report metadata.
   - Per-issue warnings should only describe evidence specific to that issue.
3. Do not classify implementation-output / QA-handoff solely from labels.
   - Enrich with comments and PR references so unlabeled but real handoff evidence is not missed.
4. For generated queue/report artifacts, include both:
   - machine-readable JSON for downstream automation
   - human-readable Markdown for morning/overnight operator review
5. For overnight implementation suggestions, cap new dispatch recommendations separately from QA/handoff saturation.
   - This avoids over-dispatching while still surfacing review-ready work.

## Minimal Python subprocess helper

```python
import json
import subprocess


def gh_json(args):
    proc = subprocess.run(
        ["gh", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return json.loads(proc.stdout or "null")


issues = gh_json([
    "issue", "list",
    "--state", "open",
    "--limit", "200",
    "--json", "number,title,labels,state,updatedAt",
])

for issue in issues:
    detail = gh_json([
        "issue", "view", str(issue["number"]),
        "--json", "number,title,state,labels,comments,closedByPullRequestsReferences,url",
    ])
    # classify using detail, not the shallow list row alone
```

## Verification checklist

Before trusting an issue-automation report:
- [ ] The broad issue list command succeeded.
- [ ] Evidence-bearing candidates were enriched with `gh issue view`.
- [ ] The code uses `closedByPullRequestsReferences`, not `closedByPullRequests`.
- [ ] Missing external ledgers or optional evidence stores appear as global warnings.
- [ ] Per-issue warnings are only issue-specific.
- [ ] Generated JSON and Markdown reports are deterministic enough for review/diffing.
- [ ] Tests cover unlabeled issues that still have PR/handoff evidence.
