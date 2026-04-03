---
name: github-code-review
description: Practical GitHub code review workflow with local diff inspection, PR review, inline comments, approval/request-changes decisions, and optional multi-agent review overlays.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.1.0
---

# GitHub Code Review

## Overview

Use this skill when reviewing commits or pull requests on GitHub. It combines the repo's multi-agent review intent with the concrete gh-driven workflow from Hermes.

## Quick Start

```bash
# View PR metadata
gh pr view 123 --json files,additions,deletions,title,body,author

# Review diff
gh pr diff 123

# Check out locally if needed
gh pr checkout 123

# Approve
gh pr review 123 --approve --body "APPROVE: looks good."

# Request changes
gh pr review 123 --request-changes --body "MAJOR: please address the items below."

# Comment only
gh pr review 123 --comment --body "MINOR: a few follow-ups below."
```

## When to Use

- Review pull requests before merge
- Review a local diff before opening a PR
- Leave inline GitHub comments on specific files/lines
- Perform adversarial review for security, performance, architecture, and test quality
- Run a multi-agent review where Claude/Codex/Gemini each provide a distinct perspective

## Review Workflow

1. Inspect scope
   - `gh pr view <N> --json files,additions,deletions,title,body`
   - `gh pr diff <N>`
2. Pull locally when needed
   - `gh pr checkout <N>`
   - run tests, linters, or targeted repro steps
3. Review against checklist below
4. Leave review comments
5. Submit verdict

## Review Checklist

- Correctness
  - Does the change do what the issue/plan requires?
  - Any broken edge cases or regressions?
- Security
  - Injection risks?
  - Missing auth/validation?
  - Secrets or unsafe defaults?
- Quality
  - Names, structure, duplication, maintainability
- Testing
  - Meaningful coverage?
  - TDD evidence or regression test?
- Performance
  - Obvious N+1, excessive scans, slow paths, unnecessary allocations
- Documentation
  - Need updates to README, AGENTS, docs, comments, or migration notes?

## Local Diff Review

Use this before PR creation or when GitHub is unavailable:

```bash
git diff --stat main...HEAD
git diff main...HEAD
```

Recommended review summary format:

```text
Summary: <1-3 sentences>

Critical Issues:
- <must-fix item>

Important Issues:
- <should-fix item>

Minor Issues:
- <nice-to-have>

Strengths:
- <what is good>

Verdict: APPROVE | MINOR | MAJOR | REJECT
```

## Inline Commenting

```bash
gh api repos/:owner/:repo/pulls/123/comments \
  -f body='Potential null dereference here.' \
  -f commit_id='SHA' \
  -f path='src/module.py' \
  -F line=42
```

## Multi-Agent Review Mode

Use this when you want more than one reviewer:
- Claude: orchestration, architecture, synthesis
- Codex: adversarial code review, implementation-focused criticism
- Gemini: third-lane synthesis, alternate perspective, large-context review

Treat the final decision as the merged outcome of all collected reviews, not just the first positive response.

## Verdict Guidance

- APPROVE
  - No meaningful issues found; safe to merge
- MINOR
  - Small follow-ups or polish items; merge can proceed with discretion
- MAJOR
  - Significant correctness, security, testing, or architecture concerns; fix before merge
- REJECT
  - Fundamentally unsafe, mis-scoped, or not ready for merge

## Fallback Without gh

If gh is unavailable, use git diff locally and the GitHub REST API via curl for comments/reviews if credentials are available.

## Notes

- Prefer specific, actionable comments over vague criticism
- Cite file paths and line ranges when possible
- For high-risk changes, run code/tests locally before approving
- Multi-agent review is an overlay, not a substitute for concrete diff inspection
