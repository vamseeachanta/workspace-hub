# Archived Skill: `github-issue-closeout-race-safe`

Original path: `/home/vamsee/.hermes/skills/github/github-issue-closeout-race-safe`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-issue-closeout-race-safe`
Consolidation date: 2026-04-29

---

---
name: github-issue-closeout-race-safe
description: Close GitHub issues without losing the evidence comment when multiple agents or races may close the issue concurrently.
version: 1.0.0
author: Hermes Agent
category: github
tags: [github, issues, closeout, race-condition, reliability]
---

# GitHub issue closeout race-safe pattern

Use when:
- closing issues after verification or implementation
- multiple agents/terminals may act on the same issue
- the closeout comment is important evidence and must not be lost

## Problem

`gh issue close --comment "..."` is convenient, but in live multi-agent use the comment can be lost if the issue becomes closed before the command lands cleanly.

## Safe pattern

1. Post the evidence comment first.
2. Close the issue as a separate command.

```bash
gh issue comment <issue> --body-file /tmp/closeout.md
gh issue close <issue>
```

## Why this works

- The closeout evidence becomes durable even if a separate process closes the issue moments later.
- It avoids silent loss of the most important verification/implementation summary.

## Recommended closeout block

Include:
- Result: landed / already done / blocked
- Evidence checked
- Validation commands/results
- Commit hashes or artifact paths
- Residual risks or blockers

## Extra verification

After commenting/closing, verify:

```bash
gh issue view <issue> --json state,comments,url
```

Confirm:
- issue state is `CLOSED` when intended
- the closeout comment is present in recent comments

## When not necessary

If you intentionally want a single quick close with no meaningful evidence, `gh issue close` alone is fine. But when evidence matters, always comment first, then close.
