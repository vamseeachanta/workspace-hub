# Archived Skill: `overnight-planning-noop-run-salvage`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-planning-noop-run-salvage`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-planning-noop-run-salvage`
Consolidation date: 2026-04-29

---

---
name: overnight-planning-noop-run-salvage
version: 1.0.0
description: Recover when unattended overnight Claude planning runs exit 0 but produce no required artifacts; salvage the wave by auditing existing plan state, generating missing summary artifacts manually, and preserving morning monitoring surfaces.
---

# Overnight Planning No-Op Run Salvage

## When to use

Use this when an unattended overnight planning or review wave appears to have run successfully but did not actually produce the expected artifacts.

Typical signals:
- Claude background process exits with code 0
- stdout/stderr logs are empty or missing
- expected `docs/reports/...summary.md` or `scripts/review/results/...` files do not exist
- no plan files or issue comments were materially updated

This showed up in the 2026-04-22 workspace-hub tier-1 knowledge beef-up wave across 6 separate unattended Claude launches.

## Core lesson

`exit_code == 0` is not sufficient proof that unattended Claude accomplished the task.

For planning-only overnight waves, the real success condition is artifact creation.
If the required artifact is missing, treat the run as failed/no-op even if the process exited cleanly.

## Recovery workflow

1. **Treat the run as failed if required artifacts are absent**
   - Do not report the lane as complete just because the process ended cleanly.
   - Check for the exact expected artifacts first.

2. **Audit whether the core plan work already exists in the main repo**
   - Search `docs/plans/` for the target issue plans.
   - Search `scripts/review/results/` for existing review artifacts.
   - Inspect `docs/plans/README.md` for missing index rows.
   - Query live GitHub issue state so your salvage summary reflects reality, not stale prompts.

3. **Do only one hardened rerun, then stop**
   - If the first unattended run no-op'd, one rerun is reasonable.
   - Harden the rerun so the first mandatory action is writing a unique summary/result file.
   - Use absolute prompt-file paths in the launcher.
   - If that rerun also exits 0 with no artifact, stop rerunning. Treat the unattended pattern itself as unreliable for that wave.

4. **Salvage by generating the missing control-plane artifacts manually**
   - If the plans already exist, do not recreate them blindly.
   - Create the missing terminal summary/report artifacts yourself under `docs/reports/`.
   - Summaries should capture:
     - what exists already
     - what was missing from the overnight run
     - current blockers
     - recommended morning execution order

5. **Repair discovery/index surfaces if needed**
   - If the overnight wave was supposed to create plan index rows, add the missing `docs/plans/README.md` rows.
   - Keep these updates grounded in actual on-disk artifacts and live issue state.

6. **If a monitor expects artifacts in isolated worktrees, copy the salvaged summaries there**
   - When a morning monitor job is pointed at specific worktrees, copy the generated summary artifacts into those worktree paths so the monitor sees the expected outputs.
   - This preserves operational continuity even though the original unattended workers no-op'd.

7. **Document the no-op pattern explicitly**
   - In your final report, say the unattended run exited 0 but produced no durable outputs.
   - Do not let future operators mistake the run for a success.
   - If you attempted a hardened rerun and it also no-op'd, say that explicitly too; this justifies switching to manual salvage instead of a third unattended retry.

## Strong verification pattern

For each lane, verify these in order:
1. expected summary artifact exists
2. target plan files exist
3. review artifacts exist
4. GitHub issue state matches the summary narrative

If (1) is false but (2)/(3) are true, the lane likely needs salvage summaries, not fresh plan drafting.

## What this pattern is best for

- planning-only overnight waves
- repo-governance / routing / documentation waves
- multi-worktree Claude batches where each lane is expected to emit one result artifact
- morning runbooks that depend on deterministic summary files

## Pitfalls

- Do not trust empty or missing logs as the only signal; logs can be buffered or omitted.
- Do not rerun the same prompt indefinitely if multiple clean exits produce no artifacts.
- Do not overwrite existing good plans just because the overnight worker failed to summarize them.
- Do not leave the morning monitor pointed at nonexistent artifacts if you can salvage them manually.

## Reusable rule

For unattended planning waves, artifact existence is the contract.
No artifact = no success, regardless of process exit code.
