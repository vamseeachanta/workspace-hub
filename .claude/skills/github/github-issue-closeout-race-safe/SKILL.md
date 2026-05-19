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

## Tool-budget guardrail

When closeout is part of a larger implementation/verification turn, do not leave evidence comments and issue closure until after optional cleanup, extra review polish, or broad worktree hygiene. Once the deliverable is committed/pushed and the closeout evidence is known, post the evidence comment immediately, then close as a separate command. This prevents tool-call or context limits from leaving an otherwise-complete issue open with no durable closeout trail.

If additional verification is still desirable after closeout, state it as residual follow-up in the comment rather than delaying the comment itself.

For the concrete pattern, including how to verify a push that reports a transient GitHub remote `cannot lock ref` race even though `origin/main` advanced to the intended SHA, see `references/tool-budget-and-remote-ref-race-closeout.md`.

## When not necessary

If you intentionally want a single quick close with no meaningful evidence, `gh issue close` alone is fine. But when evidence matters, always comment first, then close.
