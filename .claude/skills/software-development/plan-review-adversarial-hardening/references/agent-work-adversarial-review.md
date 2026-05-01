# Archived Skill: `agent-work-adversarial-review`

Original path: `/home/vamsee/.hermes/skills/coordination/agent-work-adversarial-review`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/agent-work-adversarial-review`
Consolidation date: 2026-04-29

---

---
name: agent-work-adversarial-review
description: Adversarially review the last 24h of multi-agent work by combining git history, GitHub issue state, generated analysis artifacts, governance tests, and duplicate-checked follow-up issue creation.
version: 1.0.0
category: coordination
tags: [audit, adversarial-review, github, governance, artifacts, issues]
related_skills:
  - coordination/session-corpus-audit
  - github/github-issues
  - development/code-reviewer
---

# Agent Work Adversarial Review

Use when asked to review recent work done by multiple agents across the ecosystem, especially the last 24h. This is not a normal progress summary — the goal is to find regressions, contradictions, stale claims, enforcement gaps, and missing follow-through.

## What this skill is for

Produce an evidence-backed review of recent agent work and create high-value follow-up GitHub issues without spamming duplicates.

## Inputs

- Target repo (usually current repo)
- Time window (default: last 24 hours)
- Optional focus area: governance, generated artifacts, issue hygiene, code changes

## Workflow

### 1. Establish live repo context
Run:
```bash
pwd
git rev-parse --show-toplevel
git remote get-url origin
date -u '+%Y-%m-%d %H:%M:%S UTC'
gh auth status
```

### 2. Gather recent work signals from multiple sources
Do not rely on only git log or only session logs.

Use:
```bash
git log --since='24 hours ago' --date=iso --pretty=format:'%h%x09%ad%x09%an%x09%s' --stat --no-merges
```

Also inspect:
- `.claude/state/session-signals/YYYY-MM-DD.jsonl`
- `logs/orchestrator/claude/session_*.jsonl`
- recent GitHub issues:
```bash
gh issue list --state all --limit 30 --json number,title,state,createdAt,updatedAt,labels,author,url
```

### 3. Audit generated analysis artifacts directly
Treat generated result docs as first-class review targets.

Check recent files under patterns like:
- `docs/plans/*/results/*.md`
- `docs/handoffs/*.md`

Look for:
- "directly executable" claims that are no longer true
- blocked-status artifacts whose blockers were later cleared
- false negatives about file/module existence
- recommended next actions already completed elsewhere

### 4. Reproduce at least one concrete check
Do not stop at document review. Re-run focused tests or scripts for the changed area.

Good pattern for governance/runtime work:
```bash
uv run pytest <focused test subset> -q
```

Also exercise both human-facing and machine-facing entrypoints when a tool claims automation support:
- run the normal CLI mode
- run `--json` / structured-output mode separately
- verify exit codes as well as stdout shape

Adversarial check for governance/checker work:
- compare the checker's enforced contract against the canonical schema/constants used by the main implementation
- do not trust comments or issue summaries alone
- if docs and implementation require fields A/B/C/D but the new checker only validates A/B/C, classify that as a real enforcement gap and fix it

Adversarial check for scheduled governance/cron wrappers:
- inspect the exact JSON/status values emitted by the underlying tool and verify wrapper scripts compare against the real casing/spelling (`fail` vs `FAIL`, etc.)
- verify any labels used for auto-created GitHub issues actually exist in the repo; do not assume descriptive labels like `conformance` or `registry-health` are defined
- when labels do not exist, prefer existing repo taxonomy plus dedupe by issue-title search rather than by nonexistent labels
- add a small regression test that reads the shell script text and asserts the expected status token and label strings are present

If one file fails in a combined run but passes alone, record it as a possible invocation-context/import-path problem rather than claiming a stable failure.

### 5. Use adversarial subreviews when scope is broad
Delegate independent subreviews for parallel adversarial pressure, for example:
- governance/runtime enforcement changes
- generated artifacts and issue-follow-up quality

Ask subreviewers for:
- exact repro steps
- concrete files/commits reviewed
- suggested issue titles
- whether the finding is already covered by an open GitHub issue

### 6. Check for duplicate issues before creating anything
Always search GitHub before opening follow-up items.

Use targeted searches such as:
```bash
gh issue list --state open --search '<keywords>' --limit 20
```

Important: distinguish exact duplicates from umbrella issues. If an umbrella exists, reference it in the new issue instead of skipping automatically.

### 6.5 Reopen incorrectly closed issues when live validation contradicts prior completion claims
If a previously closed issue is directly contradicted by a reproduced live failure, prefer reopening the original issue instead of creating a duplicate regression ticket.

Use this when:
- the closed issue claimed a fix landed
- your focused repro shows the same path still fails now
- the reopened issue is a hard blocker for a downstream approval gate

Pattern:
```bash
gh issue reopen <number>
gh issue comment <number> --body-file /tmp/repro.md
```

Your comment should include:
- exact repro command
- current result vs expected result
- concrete error message/stack clue
- downstream issue(s) now blocked by the regression

### 7. Prefer root-cause follow-up issues
Create issues for systemic gaps, not every symptom.

High-value categories:
- documented governance behavior not honored by runtime hooks
- installer scripts that claim stronger enforcement than they actually wire
- automation gaps causing stale or redundant issue backlog

Avoid filing noise issues unless the evidence is concrete and reproducible.

### 8. Final report structure
Return a concise summary with:
1. strongest findings
2. evidence basis
3. what was verified live
4. issues created (or why none were created)
5. confidence / uncertainty, especially for flaky failures

## Practical heuristics

- If a combined pytest invocation fails but direct-file invocation passes later, label it as flaky or context-dependent until reproduced cleanly.
- Generated analysis docs can be wrong even when code/tests are green.
- A repo with increasing agent throughput usually needs issue-hygiene automation, not just more tickets.
- Governance drift often appears as mismatch between docs, env scripts, and actual hooks.

## Output expectations

Good output is short but evidence-backed. Keep the detailed proof in issue bodies or internal notes; keep the user summary compact.
