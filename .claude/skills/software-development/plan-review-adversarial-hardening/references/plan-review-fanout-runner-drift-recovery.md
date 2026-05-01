# Archived Skill: `plan-review-fanout-runner-drift-recovery`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/plan-review-fanout-runner-drift-recovery`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/plan-review-fanout-runner-drift-recovery`
Consolidation date: 2026-04-29

---

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

6. If the user explicitly waives the broken review-runner for a specific issue pair/batch and approves anyway, perform approval-state sync immediately.
   - Update the plan header to `plan-approved` and mention the exact waiver scope.
   - Update the `docs/plans/README.md` row to `plan-approved` with a note that the waiver is limited to those issue numbers.
   - Create `.planning/plan-approved/<issue>.md` markers that cite the user instruction as the approval source.
   - Post a GitHub approval comment on each issue.
   - Add `status:plan-approved` on GitHub.
   - Do **not** close or mark the runner-fix issue resolved; keep it open for future review waves.
   - Stage and commit only the approval-sync surfaces for those issues; avoid sweeping unrelated dirty workspace churn.

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

## Post-rerun artifact sanity check

After any rerun, verify the actual artifacts before posting an issue update or changing plan state:

```bash
PLAN=docs/plans/YYYY-MM-DD-issue-<issue>-<slug>.md
PLAN_SHA=$(sha256sum "$PLAN" | awk '{print $1}')
find scripts/review/results -maxdepth 1 -name '*<issue>*' -print | sort
for f in scripts/review/results/YYYY-MM-DD-plan-<issue>-{claude,codex,gemini}.md; do
  printf '%s\t' "$f"
  test -f "$f" && wc -c < "$f" || echo MISSING
  test -f "$f" && sed -n '1,20p' "$f"
  test -f "$f" && grep -q "Plan-SHA256: $PLAN_SHA" "$f" || echo "SHA_MISSING_OR_STALE: $f"
  test -f "$f" && grep -q '^## Verdict' "$f" || echo "VERDICT_MISSING: $f"
done
```

If the fanout exits `0` but only writes an empty/near-empty disagreement stub with no provider artifacts:
- Treat the rerun as **no usable review evidence**.
- Do not cite the disagreement stub as a review artifact.
- Remove the invalid stub if it would otherwise become misleading untracked evidence.
- Post a truthful status comment: plan remains draft, rerun produced no usable provider artifacts, next gate is a clean rerun or explicit waiver.

If the fanout remains unreliable but the issue needs to reach `status:plan-review`, use a manual side-effect-safe provider rerun. Generate a fresh prompt from the current on-disk plan, run each provider in read-only/review mode, save provider-specific artifacts, and prepend `Plan-SHA256: $PLAN_SHA` plus an explicit `## Verdict` block. Then write a synthesis/disagreement artifact with the same SHA. Do not apply `status:plan-review` until every required provider artifact is non-empty, current-SHA tagged, and verdicted `APPROVE` or `MINOR`.

If the fanout appears hung with no output, inspect child processes before killing or waiting indefinitely:

```bash
ps -o pid,ppid,etime,stat,cmd --forest -p <fanout-pid> --ppid <fanout-pid> || true
pgrep -P <child-pid> -a || true
ps -ef | grep -E 'claude|codex|gemini' | grep -v grep | tail -n 20 || true
```

A single provider leg (often Claude print-mode) can keep the fanout alive after other providers have finished. Preserve any real provider artifacts, but do not convert a hung/no-artifact run into approval evidence.

## Post-reboot / interrupted fanout salvage

Use a separate reconciliation worktree when the primary checkout may have active Hermes/Claude/Git writers or dirty user work. Preserve primary dirty state first (diff/stash/status snapshots), then run review recovery from the safe worktree.

When a fanout is interrupted by reboot or context loss:

1. Re-check live processes before doing anything else.

```bash
ps -eo pid,ppid,pgid,stat,comm,args \
  | awk '$0 ~ /wave_review_runner|plan-review-fanout|claude -p|codex exec|gemini -p|gemini exec/ && $0 !~ /awk/ {print}'
```

2. Stop only exact PIDs or process groups. Avoid `pkill -f 'long pattern from this shell command'` because the pattern can match and terminate the invoking shell/session.

```bash
# Prefer exact process group once verified from ps output.
kill -TERM -<pgid> 2>/dev/null || true
sleep 2
kill -KILL -<pgid> 2>/dev/null || true
```

3. Normalize artifacts immediately after killing or timeout.
   - Non-empty provider artifacts with a valid verdict are retained.
   - Missing or zero-byte provider artifacts become canonical `UNAVAILABLE` stubs with the concrete reason: `timeout`, `provider rc`, `workspace trust`, `empty artifact`, or `interrupted fanout`.
   - Move noisy `.md.err` provider logs out of `scripts/review/results/` into a salvage log directory unless they are intentionally tracked; otherwise they become untracked churn.

4. Record a status handoff before rerunning anything.
   - Include all issue/provider statuses: `PENDING`, `UNAVAILABLE`, `APPROVE`, `MINOR`, `MAJOR`.
   - Distinguish unattempted `PENDING` from attempted-but-failed `UNAVAILABLE`.
   - Mention the exact provider-wrapper failure issue if one exists.

5. If future work is needed, schedule a narrow one-shot retry for only the still-`PENDING` plans. Do not rerun the whole wave, do not auto-approve, and do not change labels/comments from the retry job.

## Provider-specific recovery notes

- Gemini may fail with workspace-trust rc=55. For bounded retry jobs, set `GEMINI_CLI_TRUST_WORKSPACE=true` or use the approved trust/skip-trust flag from a trusted cwd.
- Codex may emit useful session output to `.md.err` while the canonical `.md` artifact remains empty. The wrapper should capture/normalize stdout and stderr; until fixed, treat empty canonical artifacts as `UNAVAILABLE` and archive `.err` logs as salvage evidence.
- A shell-level `timeout -k 5s <duration>s bash scripts/review/plan-review-fanout.sh ...` is safer than letting provider CLIs hang indefinitely. Still verify child/orphan processes after timeout.

## Wrapper hardening checklist

When the root cause is the fanout wrapper itself, harden the wrapper before rerunning broad review waves:

- Add a bounded per-provider timeout knob (for example `PLAN_REVIEW_PROVIDER_TIMEOUT_SEC`) so one hung Claude/Codex/Gemini leg cannot stall the whole fanout indefinitely.
- Keep Codex non-interactive invocation on the known-safe path: pass the combined prompt/plan body as argv and close stdin with `</dev/null`; avoid `codex exec -` stdin-sentinel patterns because they can hang in some Codex CLI versions.
- For Gemini CLI trust failures, set the approved trust environment (for example `GEMINI_CLI_TRUST_WORKSPACE=true`) and run from a cwd that avoids local `.gemini/agents/*.md` permission-mode bugs when appropriate.
- Normalize every provider slot into a canonical artifact:
  - successful stdout with content -> canonical artifact
  - successful stdout empty but stderr contains a complete structured review -> promote stderr only if required headers are present, such as `## Verdict`, `## Findings`, and `## Blockers`
  - timeout/nonzero exit/empty unstructured output -> explicit `UNAVAILABLE` stub with concrete reason
  - partial stderr followed by timeout -> `UNAVAILABLE`, not promotion
- Sanitize failure excerpts written into `UNAVAILABLE` artifacts: trim length, flatten newlines, remove control characters, and escape quotes.
- If adding cleanup traps for background provider jobs, unregister them after all provider PIDs have been waited and clear the PID list (`pids=(); trap - INT TERM EXIT`) so normal shell exit cannot kill already-reaped/recycled PIDs.
- Add shell tests/mocks for each failure mode before accepting the wrapper fix: argv/stdin capture, trust env capture, timeout, stderr promotion, partial-stderr-timeout, empty output, and parallel completion.

## Pitfalls

- Do not self-approve because a provider artifact is empty.
- Do not classify sandbox false file-absence findings as repo truth without verifying from the parent shell.
- Do not leave review-artifact paths pointing at a different date than the files actually written.
- Do not treat a `0` exit from the fanout as proof that provider artifacts exist; verify artifact files and verdict blocks explicitly.
- Do not keep an empty disagreement stub when provider artifacts are missing; it is misleading evidence, not a review.
- Do not leave `.md.err` logs untracked in `scripts/review/results/` after committing canonical `.md` artifacts; archive them under a reboot/review salvage log directory.
- Do not stage/commit while active git operations hold `.git/index.lock`; check `ps` first and wait rather than deleting an active lock.
- Do not use broad `pkill -f` patterns copied from the command line; they can kill the shell running the cleanup. Kill verified exact PIDs/PGIDs instead.
