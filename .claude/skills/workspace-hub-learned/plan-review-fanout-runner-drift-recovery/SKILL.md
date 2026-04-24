---
name: plan-review-fanout-runner-drift-recovery
description: Recover plan-review waves when provider wrapper/cwd/date drift creates false MAJOR or UNAVAILABLE artifacts instead of substantive review.
version: 1.0.0
source: learned from OrcaWave/OrcaFlex #2475/#2476 review wave on 2026-04-23
metadata:
  tags: [plan-review, codex, gemini, review-runner, artifact-drift, workspace-hub]
---

# Plan Review Fanout Runner Drift Recovery

Use this when `scripts/review/plan-review-fanout.sh` or related cross-review tooling returns `UNAVAILABLE`, empty artifacts, or false file-existence `MAJOR` findings caused by provider invocation/cwd/sandbox issues rather than plan substance.

## Symptoms

- Codex artifact says:
  - `UNAVAILABLE`
  - `codex CLI failed, rc=2`
  - `unexpected argument '--no-interactive' found`
- Gemini reports repo files do not exist even though they exist under `/mnt/local-analysis/workspace-hub`.
- Gemini was invoked from `/tmp` and cannot access repo-relative paths or mounted workspace paths.
- Claude/Gemini artifacts are zero bytes or contain only tail/status text without an explicit `## Verdict` block.
- Review artifacts are dated differently from the plan header / Artifact Map because local date and UTC date differ.

## Recovery workflow

1. Classify the issue correctly.
   - Treat provider wrapper/cwd/sandbox failures as review-runner/package failures, not substantive plan defects.
   - Do not keep rewriting the plan to satisfy false “file not found” findings caused by inaccessible paths.

2. Preserve evidence.
   - Keep the failed artifacts in `scripts/review/results/`.
   - Ensure every provider slot has a non-empty artifact with an explicit verdict:
     - `APPROVE`, `MINOR`, `MAJOR`, or `UNAVAILABLE`.
   - Empty artifacts are not approval evidence. Treat them as `UNAVAILABLE`.

3. Create or use a bounded harness issue for the runner.
   - Example title: `fix(review-runner): update Codex exec invocation and harden plan-review path packaging`.
   - Include the failing artifacts and exact CLI error.
   - Scope should cover both Codex invocation drift and Gemini repo-access/cwd packaging.

4. Fix local plan defects separately.
   - If reviewers also found real plan-local issues, patch them.
   - Typical real issues from the #2475/#2476 wave:
     - artifact paths/date drift
     - Artifact Map missing files listed in Files to Change
     - validation commands written as prose instead of executable shell/Python
     - review-artifact acceptance criteria that only require file existence, not a verdict block

5. Re-run review only after runner/package fix or explicit waiver.
   - If the runner is still broken, rerunning usually reproduces `UNAVAILABLE`/false MAJOR.
   - If policy allows reduced-provider review, document the waiver explicitly in the plan and GitHub comment.

## Date-drift guard

Before dispatching plan review in late-evening sessions:

```bash
date
date -u
```

Align these surfaces with the review script’s actual date convention:
- plan filename
- plan frontmatter `Date`
- `Review artifacts` line
- `Artifact Map` review paths
- expected `scripts/review/results/YYYY-MM-DD-*` paths

In the observed failure, UTC was already 2026-04-24 while local date was still 2026-04-23, and the review script wrote `2026-04-23-*` artifacts. Future-dated plan paths caused legitimate artifact-map MAJOR findings.

## Executable validation rule

For plan TDD/validation tables, avoid prose placeholders such as:
- `test -f <page>`
- `grep headings/issue numbers`
- `small Python/YAML parser over changed pages`
- `targeted grep/link check`

Use concrete commands with real paths. When checking for multiple required anchors, do not use one `grep -E 'a|b|c'` because that passes if any one anchor exists. Use a loop:

```bash
for pat in "anchor A" "anchor B" "anchor C"; do
  grep -q "$pat" path/to/file || exit 1
done
```

## Good GitHub comment pattern

When review is blocked by runner drift, post a concise issue update:

```text
Review result: not approval-ready yet.
Plan-local MAJOR findings have been patched in vN.
Codex/Gemini review evidence is blocked by review-runner/package drift, tracked by #NNNN.
Next gate: rerun cross-provider review after #NNNN or explicit waiver. No implementation authorized yet.
```

## Pitfalls

- Do not self-approve because a provider artifact is empty.
- Do not classify sandbox false file-absence findings as repo truth without verifying from the parent shell.
- Do not leave review-artifact paths pointing at a different date than the files actually written.
- Do not stage/commit while active git operations hold `.git/index.lock`; check `ps` first and wait rather than deleting an active lock.
