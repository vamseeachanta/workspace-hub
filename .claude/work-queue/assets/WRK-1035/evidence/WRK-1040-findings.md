# WRK-1040 Findings — Nomenclature Canonicalisation

## Changes Made

### `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- Added **Canonical Terminology** section immediately after the operating principle (before "Start-to-Finish Chain"). Contains a definition table for WRK session / stage / phase / step / checkpoint / resume plus three anti-patterns to avoid.
- Bumped version `1.5.0 → 1.6.0`, updated date to 2026-03-08.
- Added version history entry for WRK-1040.

### `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- Stage 5 bullet changed from:
  `"User Review - Plan (Draft) as an agent-user interactive plan-mode session:"`
  to:
  `"User Review - Plan (Draft) as an interactive agent-user plan dialogue within this stage:"`
  — removed "session" where it was used to describe a within-stage interaction, not a WRK session.

### `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- Stage 5 bullet changed from:
  `"Run this stage as an interactive agent-user plan-mode session (not a one-way artifact drop)."`
  to:
  `"Run this stage as an interactive agent-user plan dialogue within Stage 5 (not a one-way artifact drop)."`
  — same pattern: "session" was used to describe the dialogue within a stage, not a WRK session.

### `.claude/commands/workspace-hub/wrk-resume.md`
- Added a "Note — `/wrk-resume` vs `/work run`" paragraph at the end of the file. Explains that `/wrk-resume` is session-level context restore (reads checkpoint.yaml, does not advance any stage) while `/work run` is stage-level pipeline execution (executes next stage, invokes scripts, produces stage exit artifacts). Instructs users to always run `/wrk-resume` first in a fresh session, then `/work run` to continue from the current stage.

---

## Artifact Field Names Needing Attention (not fixed — needs WRK-1035 plan coordination)

| Field name | File | Current usage | Canonical equivalent |
|-----------|------|--------------|---------------------|
| `decisions_this_session` | `checkpoint.yaml` (referenced in wrk-resume.md line 63) | Decisions made within one Claude conversation | Correct — "session" here IS a WRK session. No change needed. |
| `artifacts_written` (last session) | `checkpoint.yaml` (line 70) | Artifacts written in the previous WRK session | Correct — "session" context is implied. No change needed. |
| `current_stage` | `checkpoint.yaml` (line 44) | Which of the 20 lifecycle stages the WRK is at | Correct canonical use of "stage". |
| `stage_name` | `checkpoint.yaml` (line 44) | Human-readable name for current_stage | Correct. |
| `human_session` | Stage contract YAML `invocation:` field | Invocation type for stages that require a human in the loop | This field name conflates "session" with "stage invocation type". The canonical term for this would be `human_gate` or `human_interactive`. Changing is a breaking change — all 20 stage contract YAMLs and `start_stage.py` must be updated together. |
| `HUMAN_SESSION` | `work-queue-workflow/SKILL.md` Practical Lessons | Used as an invocation type label in documentation | Same as above — mirrors the YAML field. |

---

## Violations Not Fixed (out of scope or breaking change)

### `human_session` invocation type in stage contracts
The stage contract YAML files at `scripts/work-queue/stages/stage-NN-*.yaml` use `invocation: human_session` to mark stages that require interactive human participation. `start_stage.py` matches this string to route the stage. Renaming to `human_interactive` or `human_gate` requires coordinated changes across:
- All 20 stage contract YAML files
- `scripts/work-queue/start_stage.py` (match branch)
- `workflow-gatepass/SKILL.md` Practical Lessons note
- `work-queue-workflow/SKILL.md` Practical Lessons note

This is a breaking change with no functional impact until the rename is tested. Recommend capturing as a discrete sub-task of WRK-1035 rather than fixing here.

### "Two-phase capture and process pipeline" in work-queue/SKILL.md description
The description field uses "two-phase" to describe the top-level Capture/Process split of the work queue system (not stage sub-units). This is an architectural description predating the canonical definitions and refers to a distinct concept (the pipeline has two top-level phases). Renaming would be misleading. No fix applied.

### `phase-N` in review input filenames
`wrk-NNN-phase-N-review-input.md` naming convention in `scripts/review/results/` uses "phase" to label implementation sub-phases within Stage 10. This is canonical (phase = sub-unit within a stage). No fix needed.

### "Interactive planning sessions" for multi-agent planning (work-queue-workflow/SKILL.md)
Lines describing Route B/C planning use "separate interactive planning sessions" to refer to Codex and Gemini conversations. Each agent conversation is a WRK session in canonical terms, so this usage is technically correct. Left as-is.

### `test-session.sh` script name
`scripts/test/test-session.sh` uses "session" in the filename to mean "full regression run for the session". This is a script name (not a terminology inconsistency in prose) and renaming would break callers. No fix applied.
