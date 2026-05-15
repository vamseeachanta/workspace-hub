# Plan for #2710: feat(solver-queue): conversational submit UX — /solver-submit skill + interactive CLI

> **Status:** draft (r1 → r2 cascading-false-premise → r3 inline rework applied per feedback_r3_inline_loop_break_pattern + feedback_r1_review_trust_hazard)
> **Complexity:** T2
> **Date:** 2026-05-14 (drafted) / 2026-05-15 (r1 + r2 + r3 inline rework)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2710
> **Review artifacts:**
> - r1 Codex — `scripts/review/results/2026-05-14-plan-2710-codex.md`
> - r1 Gemini — UNAVAILABLE (gemini CLI / sandbox; no artifact landed)
> - r2 Codex — UNAVAILABLE (`scripts/review/results/2026-05-15-plan-2710-codex.md`; codex CLI 0.124.0 stdin-hang regression — see #2713, follow-up to feedback_codex_cli_0_124_upstream_regression)
> - r2 Claude — `scripts/review/results/2026-05-15-plan-2710-claude.md` (MAJOR; 12 findings, 4 blockers)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/solver/submit-job.sh:1-44` — the authoritative single-source-of-truth CLI; accepts positional args `<solver> <input_file> [description]`; **validates BOTH solver enum (lines 13-16) AND input-file existence (lines 18-23)** before any git operation (commit at line 40, push at line 41). This plan proposes no modifications to this file.
- Found: `scripts/solver/submit-job.sh:13-16` — solver enum: `if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]` — hardcoded, not derived from schema.
- Found: `scripts/solver/submit-job.sh:18-23` — input-file existence check (present since commit `71a53898b` per `git log -S "input file not found" -- scripts/solver/submit-job.sh`):
  ```bash
  if [[ ! -f "${REPO_ROOT}/${INPUT_FILE}" ]]; then
      echo "ERROR: input file not found: ${INPUT_FILE}" >&2
      echo "Path must be relative to repo root: ${REPO_ROOT}" >&2
      exit 1
  fi
  ```
  This means the issue's AC "Both wrappers reject missing input files with a clear error before any git operations" is **already satisfied at the submit-job.sh layer for any caller** — wrapper, batch, or direct CLI. The wrapper does NOT need to re-implement this.
- Found: `queue/job-schema.yaml:14` — `solver: "orcawave | orcaflex"` — documented as pipe-separated string, not a YAML sequence enum; Option B (parse schema for supported solvers) carries fragility risk given this format.
- Found: `scripts/solver/submit-batch.sh:20-25,119-128` — `--dry-run` flag pattern; callers pass `--dry-run`, wrapper skips the `bash submit-job.sh` call and emits a dry-run trace instead; interactive wrapper will mirror this pattern.
- Found: `scripts/solver/README.md:65-79` — existing Usage section documents only positional-arg invocations; needs a new "Interactive Submission" section.
- Found: `.claude/skills/coordination/` — 55 SKILL.md subdirectories under this directory; three sampled for frontmatter shape:
  - `session-start-routine/SKILL.md:1-9` — frontmatter: `name`, `description`, `version`, `category`, `tags`, `related_skills`
  - `agent-label-routing/SKILL.md:1-17` — frontmatter: `name`, `description`, `version`, `category`, `type`, `trigger`, `auto_execute`, `capabilities`, `tools`, `scripts`
  - `licensed-machine-prompt-orchestration/SKILL.md:1-10` — frontmatter: `name`, `description`, `version`, `author`, `license`, `metadata.hermes.tags`
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md:1-10` — canonical reference: `name`, `description`, `version`, `author`, `category`, `tags`, `related_skills`
- Found: `output/orcaflex_validation/pipeline_test_model.dat` — git-tracked OrcaFlex input model (131,874 bytes); will be used as the real-file fixture for `--dry-run` acceptance check.
- Gap: `.claude/skills/coordination/solver-submit/` — does not exist; will be created by this plan.
- Gap: `scripts/solver/submit-job-interactive.sh` — does not exist; will be created by this plan.
- Gap: No test files for submit-job scripts (`ls scripts/solver/test_submit*.sh` → no results); new bats-style tests will be added under `scripts/solver/tests/`.

### Standards

Not applicable — harness/tooling UX change; no engineering standards involved.

### Harness/Infrastructure bundle (per `docs/plans/README.md:55` — `cat:harness`)

Issue #2710 carries label `cat:harness`. The repo planning workflow requires consulting `CONTROL_PLANE_CONTRACT.md`, `config/agents/` settings, and `.claude/rules/` for harness-class issues. Consulted:

- `docs/standards/CONTROL_PLANE_CONTRACT.md:1-25` — Establishes `AGENTS.md` as canonical entry point and `.claude/` as the Claude provider adapter. **Relevance:** The new skill lives under `.claude/skills/coordination/solver-submit/`, which is the conformant adapter path; the bash wrapper sits under `scripts/solver/` and does not introduce a new provider adapter. No conflict.
- `config/agents/behavior-contract.yaml:1-25` — Workflow-equivalence contract (orchestrator/subagent roles). **Relevance:** None — this plan adds a passive UX skill and bash wrapper; it does not touch session-state, work-queue stages, or orchestrator/subagent role boundaries. No conflict.
- `config/agents/skill-graph-index.yaml` — Index of skill relationships. **Relevance:** Adding `solver-submit` does not require editing this index unless we want it cross-linked; this plan defers the cross-link to a follow-up (see Open Questions) since the issue does not require it.
- `.claude/rules/coding-style.md:1-14` — Constraint: "In scripts: use relative paths or `$(git rev-parse --show-toplevel)` / `${REPO_ROOT}` — never hardcode absolute paths (enforced: `scripts/enforcement/check-no-abs-paths.sh`)." **Relevance — APPLIES:** The wrapper computes `REPO_ROOT` via `git rev-parse --show-toplevel` and resolves `SUBMIT_SCRIPT` via `${SCRIPT_DIR}` (derived from `$0`); no absolute path is hardcoded. The `check-no-abs-paths.sh` enforcement script will pass for the new file.
- `.claude/rules/coding-style.md:13` — "CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md must not exceed 20 lines." **Relevance:** None — this plan creates a `SKILL.md` (not a top-tier harness file) which has no 20-line limit.
- `.claude/rules/patterns.md:1-16` — Enforcement gradient: prose → micro-skill → script → hook. **Relevance:** This plan operates at level 0/1 (prose skill + script wrapper). No promotion is required by the issue.
- `.claude/rules/calc-citation-contract.md` and `.claude/rules/goal-invocation.md` — **Not applicable:** no standards-derived constants are emitted (it's a job-submission UX), and `/goal` is not being invoked.

### LLM Wiki pages consulted

No relevant wiki pages. Solver queue is an internal workflow tool, not a domain knowledge area.

### Documents consulted

- Issue [#2710](https://github.com/vamseeachanta/workspace-hub/issues/2710) — full scope: skill at `.claude/skills/coordination/solver-submit/SKILL.md`, bash wrapper at `scripts/solver/submit-job-interactive.sh`, README update at `scripts/solver/README.md`; 6 acceptance criteria (skill generates valid YAML, bash produces identical outcome, invalid solver names rejected, missing files trigger pre-git errors, no duplicated validation logic, AQWA handled gracefully); also "Skill appears in available-skills listings".
- Issue [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) — OPEN — AQWA runner adapter; adds `aqwa` to solver enum in `submit-job.sh`; this plan must not add AQWA to the supported list until #2709 lands; plan addresses AQWA gracefully per acceptance criterion 6.
- Issue [#2708](https://github.com/vamseeachanta/workspace-hub/issues/2708) — OPEN — OrcaFlex live validation on licensed-win-1; informational for this plan; `orcaflex` is already in the enum; that issue validates the dispatch path end-to-end but does not change the submit-side API.
- Issue [#2713](https://github.com/vamseeachanta/workspace-hub/issues/2713) — follow-up tracking codex CLI 0.124.0 stdin-hang regression that blocked r2 Codex review; downgrade to 0.123.0 is the workaround per feedback_codex_cli_0_124_upstream_regression.
- `scripts/solver/README.md` — existing documentation; this plan adds an "Interactive Submission" section.
- `docs/plans/README.md:55` — class-specific retrieval bundle; harness-class requires CONTROL_PLANE_CONTRACT.md + config/agents/ + .claude/rules/ (now consulted, above).
- `docs/SKILLS_INDEX.md:1-50` — repo-level skill catalog. Coordination skills are summarised aggregate-wise (not individually enumerated). The canonical "available-skills listing" surface for a new coordination skill is the directory listing under `.claude/skills/coordination/` plus the per-category aggregate counts in SKILLS_INDEX.md. This drives a new acceptance criterion (see §Acceptance Criteria) verifying the skill is discoverable there.
- `docs/plans/_template-issue-plan.md` — template followed for this plan structure.

### Gaps identified

1. No Claude slash-skill for solver submission — users must remember positional CLI arguments; no discoverable interface exists.
2. No interactive bash wrapper — SSH terminal users cannot be guided through submission interactively.
3. No test coverage for submit-job.sh or any interactive wrapper — `scripts/solver/tests/` does not exist.
4. `queue/job-schema.yaml` solver enum is a prose pipe-separated string, not a parseable YAML sequence — Option B (schema-derived solver list) would require fragile string parsing.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-14):
- [#2710](https://github.com/vamseeachanta/workspace-hub/issues/2710) — OPEN — feat(solver-queue): conversational submit UX — /solver-submit skill + interactive CLI
- [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) — OPEN — feat(solver-queue): add AQWA runner adapter and schema extension
- [#2708](https://github.com/vamseeachanta/workspace-hub/issues/2708) — OPEN — feat(solver-queue): validate OrcaFlex dispatch on licensed-win-1 (#1586 child)

**File existence** (verified 2026-05-14 / re-verified 2026-05-15 for r1 + r3 reworks):
- EXISTS: `scripts/solver/submit-job.sh`
- EXISTS: `scripts/solver/submit-batch.sh`
- EXISTS: `scripts/solver/README.md`
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- EXISTS: `output/orcaflex_validation/pipeline_test_model.dat` (git-tracked, 131,874 bytes) — real fixture for `--dry-run` AC
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `config/agents/behavior-contract.yaml`, `config/agents/skill-graph-index.yaml`
- EXISTS: `.claude/rules/coding-style.md`, `.claude/rules/patterns.md`
- MISSING (new — this plan creates): `.claude/skills/coordination/solver-submit/SKILL.md`
- MISSING (new — this plan creates): `scripts/solver/submit-job-interactive.sh`
- MISSING (new — this plan creates): `scripts/solver/tests/test_submit_interactive.sh`

**Line excerpts** (`scripts/solver/submit-job.sh:8-23` — FULL validation block; r2 Finding 3 fix: prior r1 quote at `:8-16` was truncated immediately before the existence check, which is misleading by omission):
```
SOLVER="${1:?Usage: submit-job.sh <solver> <input_file> [description]}"
INPUT_FILE="${2:?Usage: submit-job.sh <solver> <input_file> [description]}"
DESCRIPTION="${3:-Solver job}"

# Validate solver type
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
    exit 1
fi

# Validate input file exists (relative to repo root)
if [[ ! -f "${REPO_ROOT}/${INPUT_FILE}" ]]; then
    echo "ERROR: input file not found: ${INPUT_FILE}" >&2
    echo "Path must be relative to repo root: ${REPO_ROOT}" >&2
    exit 1
fi
```

**Line excerpts** (`queue/job-schema.yaml:12-15`):
```
schema:
  required:
    solver: "orcawave | orcaflex"
    input_file: "relative path to .owd or .dat input file (from repo root)"
```

**Line excerpts** (`scripts/solver/submit-batch.sh:119-128` — confirms `--dry-run` pattern to mirror):
```
if [[ "${DRY_RUN}" == "true" ]]; then
    echo "  → [DRY RUN] Would call: submit-job.sh ${SOLVER} \"${INPUT_FILE}\" \"${DESCRIPTION}\""
    SUCCESS=$((SUCCESS + 1))
else
    if bash "${SUBMIT_SCRIPT}" "${SOLVER}" "${INPUT_FILE}" "${DESCRIPTION}"; then
        echo "  → Submitted successfully"
        SUCCESS=$((SUCCESS + 1))
    fi
fi
```

**Gap proofs:**
- `ls .claude/skills/coordination/solver-submit/` → No such file or directory → confirms skill does not exist
- `ls scripts/solver/submit-job-interactive.sh` → No such file or directory → confirms wrapper does not exist
- `ls scripts/solver/test_submit*.sh` → No such file or directory → confirms no existing submit tests

**Reproduction proofs**: N/A — new-feature issue; no alleged runtime failure to reproduce. The issue describes absent artifacts (skill, interactive wrapper), not broken existing behavior. Step 1.5 reproduction is intentionally skipped.

**Source count:** 14 distinct sources (issue body + #2709 + #2708 + #2713 + `submit-job.sh` + `submit-batch.sh` + `queue/job-schema.yaml` + 3x SKILL.md frontmatter sampling + `README.md` + `CONTROL_PLANE_CONTRACT.md` + `behavior-contract.yaml` + `coding-style.md` + `patterns.md` + `docs/SKILLS_INDEX.md`). Exceeds minimum of 3. (r2 Finding 11 fix: previous count of 13 omitted one harness-bundle source.)

---

## Architecture Decision

**Solver validation AND input-file existence: single-source-of-truth at `submit-job.sh`. The wrapper provides UX (menu + confirmation) but performs NO validation that duplicates the gate.**

(This decision was rewritten in the r3 inline rework after r2 caught a cascading false premise from the r1 Codex review. r1 had asserted that `submit-job.sh` lacked an input-file existence check, which led r1 to add a wrapper-layer `[[ -f ... ]]` check. That was empirically wrong: `submit-job.sh:18-23` has had the existence check since commit `71a53898b` — the original queue-infra commit. The r1 wrapper-layer check violated AC 5 ("No duplicate validation logic — both layers funnel into submit-job.sh"). r3 rips out the duplicate.)

**The wrapper does TWO things only:**

1. **Discovery / UX** — presents a numbered solver menu, prompts for input file path and description, prints a friendly preview ("File: <path>") before the confirmation prompt, and asks for explicit `y/N` confirmation. The preview is presentational text only; it does NOT stat the file or short-circuit on missing files.
2. **Delegation** — maps the menu choice to a solver token and invokes `bash submit-job.sh <solver> <input> <description>`. The wrapper relays the delegated exit status and stderr verbatim. `submit-job.sh` performs BOTH solver-enum validation (lines 13-16) AND input-file existence validation (lines 18-23) before any git operation, satisfying AC 4 ("missing files trigger pre-git errors") and AC 5 ("no duplicate validation") simultaneously.

**Why the hardcoded `case` menu is permitted (r2 Finding 4 acknowledgement):**

The wrapper's `case CHOICE in 1) SOLVER="orcawave"; 2) SOLVER="orcaflex"; 3) SOLVER="aqwa"` IS a hardcoded enumeration. Although it performs no rejection (any token is passed through to `submit-job.sh` which is the gate), the menu could drift out of sync with `submit-job.sh:13` over time. r2 Finding 4 correctly flagged that simply labelling the menu "UX-only" does not eliminate drift risk; it only eliminates duplicate-rejection. To close the drift surface, r3 RESTORES `test_solver_list_consistency` (which r1 had removed) as a **drift-catcher**: the test greps the wrapper menu and `submit-job.sh:13` for the same set of solver names and fails if they diverge. This is explicitly NOT duplicate validation — validation lives in `submit-job.sh`; this test only protects the menu's discoverability against silent staleness. The wrapper itself contains no enum check.

**AQWA handling before [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands:**

Per the decision above, the wrapper includes AQWA in the menu, delegates to `submit-job.sh` (which rejects it via the existing enum check), and prints a one-line hint that AQWA support depends on #2709. The user gets exit-code 1 from the delegated process plus an informative hint. The hint condition is `${DELEGATE_EXIT} -ne 0` AND the delegated stderr contains the canonical enum-rejection substring `"solver must be 'orcawave' or 'orcaflex'"`. Once #2709 lands and AQWA is accepted by `submit-job.sh`, this stderr substring will no longer appear on AQWA failures (it would be replaced by file-not-found, push-failure, etc.) and the hint will not fire — preventing the stale-hint risk r2 Finding 5 flagged.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2710-solver-submit-ux.md` |
| Skill | `.claude/skills/coordination/solver-submit/SKILL.md` |
| Interactive wrapper | `scripts/solver/submit-job-interactive.sh` |
| Tests | `scripts/solver/tests/test_submit_interactive.sh` |
| README update | `scripts/solver/README.md` |
| r1 review — Codex | `scripts/review/results/2026-05-14-plan-2710-codex.md` |
| r1 review — Gemini | UNAVAILABLE |
| r2 review — Codex | `scripts/review/results/2026-05-15-plan-2710-codex.md` (UNAVAILABLE; codex CLI stdin-hang — #2713) |
| r2 review — Claude | `scripts/review/results/2026-05-15-plan-2710-claude.md` |

---

## Deliverable

A `/solver-submit` Claude skill (`.claude/skills/coordination/solver-submit/SKILL.md`) and a `scripts/solver/submit-job-interactive.sh` bash wrapper that will guide users through job submission via interactive prompts, delegating **all** validation (solver enum AND input-file existence) and queue-write operations to the existing `scripts/solver/submit-job.sh`. The wrapper performs no validation of its own; it is a UX layer over the single gate.

---

## Pseudocode

**`submit-job-interactive.sh` flow:**

```
function main():
    REPO_ROOT = $(git rev-parse --show-toplevel)
    SCRIPT_DIR = $(dirname $(realpath $0))
    # SUBMIT_JOB_OVERRIDE lets tests substitute a mock at an absolute path.
    # Production callers never set this; tests set it to a tempdir mock.
    SUBMIT_SCRIPT = "${SUBMIT_JOB_OVERRIDE:-${SCRIPT_DIR}/submit-job.sh}"

    parse_args:
        --dry-run → DRY_RUN=true
        unknown flags → print usage, exit 1

    print_header: "=== Solver Job Submission ==="

    # Step 1: solver selection — MENU IS UX, NOT VALIDATION.
    # The wrapper does NOT validate the choice itself; it maps the choice
    # to a token and delegates. submit-job.sh is the single solver gate.
    print numbered menu:
        [1] orcawave   — OrcaWave hydrodynamic diffraction
        [2] orcaflex   — OrcaFlex dynamic mooring and riser
        [3] aqwa       — [may be unsupported — see #2709]
    read CHOICE from stdin
    case CHOICE in
        1) SOLVER="orcawave" ;;
        2) SOLVER="orcaflex" ;;
        3) SOLVER="aqwa"     ;;     # will be rejected by submit-job.sh until #2709 lands
        *) print "Invalid menu choice (must be 1, 2, or 3)"; exit 1 ;;
    esac

    # Step 2: input file — WRAPPER PERFORMS NO EXISTENCE CHECK.
    # submit-job.sh:18-23 is the canonical missing-file gate (since 71a53898b).
    # Only an empty-string guard remains, because submit-job.sh's `${2:?...}`
    # would emit a Usage line for an empty positional arg; the wrapper's
    # empty-string guard simply re-prompts via a clearer message before delegating.
    prompt "Input file path (relative to repo root): "
    read INPUT_FILE
    if [[ -z "${INPUT_FILE}" ]]; then
        print "ERROR: input file path is required" >&2
        exit 1
    fi
    # NO `[[ -f ... ]]` check here — that lives in submit-job.sh:18-23.
    # Friendly preview (UX only; does not stat or short-circuit):
    print "File: ${INPUT_FILE}"

    # Step 3: description
    prompt "Description [optional, press Enter to use default]: "
    read DESCRIPTION
    if [[ -z "${DESCRIPTION}" ]]; then DESCRIPTION="Solver job"; fi

    # Step 4: confirmation summary (raw user choice — no enum guard, no -f guard)
    print "  Solver:      ${SOLVER}"
    print "  Input file:  ${INPUT_FILE}"
    print "  Description: ${DESCRIPTION}"
    prompt "Submit? [y/N]: "
    read CONFIRM
    if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
        print "Cancelled."
        exit 0
    fi

    # Step 5: delegate to submit-job.sh (or override for tests).
    # Capture stderr so we can detect the canonical enum-rejection substring
    # for the AQWA hint (r2 Finding 5 fix — stderr-grep, not solver-name-only).
    if [[ "${DRY_RUN}" == "true" ]]; then
        print "[DRY RUN] Would call: bash ${SUBMIT_SCRIPT} ${SOLVER} ${INPUT_FILE} ${DESCRIPTION}"
        exit 0
    fi
    STDERR_CAPTURE=$(mktemp)
    bash "${SUBMIT_SCRIPT}" "${SOLVER}" "${INPUT_FILE}" "${DESCRIPTION}" 2> >(tee "${STDERR_CAPTURE}" >&2)
    DELEGATE_EXIT=$?
    # AQWA hint: fires only when (a) user chose aqwa, (b) delegate failed,
    # and (c) the failure was the canonical enum-rejection. Once #2709 lands
    # and aqwa is accepted, condition (c) will be false on any aqwa failure
    # (file-not-found, push-fail, etc.) and the hint will not fire.
    if [[ "${SOLVER}" == "aqwa" && "${DELEGATE_EXIT}" -ne 0 ]] \
       && grep -q "solver must be 'orcawave' or 'orcaflex'" "${STDERR_CAPTURE}"; then
        print "" >&2
        print "HINT: AQWA support depends on #2709 (not yet landed)." >&2
        print "      See https://github.com/vamseeachanta/workspace-hub/issues/2709" >&2
    fi
    rm -f "${STDERR_CAPTURE}"
    exit "${DELEGATE_EXIT}"
```

**`.claude/skills/coordination/solver-submit/SKILL.md` steps (what the skill document instructs Claude to do):**

```
1. Ask: "Which solver?" — present numbered menu with orcawave, orcaflex, and aqwa [may be unsupported — see #2709]
2. Ask: "What is the input file path?" (relative to repo root)
3. Ask: "Optional description? (press Enter to skip)"
4. Summarise: show the submit-job.sh command that will be run
5. Ask: "Confirm submission? [y/N]"
6. If confirmed: run `bash scripts/solver/submit-job.sh <solver> <input_file> <description>`
   — submit-job.sh validates BOTH solver enum AND input-file existence before any git op
7. Report: echo the job file path and queue processing ETA from submit-job.sh stdout
8. If user chose `aqwa` and the call exited non-zero with the canonical enum-rejection on stderr, surface the #2709 hint
```

The skill performs NO solver-enum validation and NO file-existence validation of its own. The menu is a discovery aid; the delegated call is the gate.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/skills/coordination/solver-submit/SKILL.md` | New skill — conversational submission guide for Claude sessions |
| Create | `scripts/solver/submit-job-interactive.sh` | New bash wrapper — guided interactive submission for SSH terminals |
| Create | `scripts/solver/tests/test_submit_interactive.sh` | TDD test suite for the interactive wrapper |
| Modify | `scripts/solver/README.md` | Add "Interactive Submission" section documenting both new artifacts |

`scripts/solver/submit-job.sh` is **NOT modified** — it remains the single source of truth for both solver-enum validation (lines 13-16) and input-file existence validation (lines 18-23), plus queue write logic. Both new layers delegate to it.

**Skill frontmatter shape** (mirrors `issue-planning-mode/SKILL.md:1-10` and `session-start-routine/SKILL.md:1-9`):

```yaml
---
name: solver-submit
description: Conversational solver job submission — guides the user through solver selection, input file, and description; delegates execution to scripts/solver/submit-job.sh
version: 1.0.0
author: Workspace Hub
category: coordination
tags: [solver, queue, submission, orcawave, orcaflex, interactive]
related_skills:
  - licensed-machine-prompt-orchestration
---
```

---

## TDD Test List

All tests live in `scripts/solver/tests/test_submit_interactive.sh`. Tests substitute a mock `submit-job.sh` by setting the `SUBMIT_JOB_OVERRIDE` env-var to an absolute path inside a per-test tempdir (e.g. `mktemp -d`). The wrapper honours `SUBMIT_JOB_OVERRIDE` and runs that path instead of `${SCRIPT_DIR}/submit-job.sh`, so tests CANNOT accidentally invoke the real submit-job.sh and trigger a git commit/push. The mock captures the positional args it receives to a tempfile and exits with a configurable status. The test harness also snapshots `git status --short queue/pending/` before and after each test and aborts if any pending YAML appears (no-leakage guard — r2 Finding 10 fix).

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_syntax_check` | Script passes `bash -n` | `bash -n scripts/solver/submit-job-interactive.sh` | exit 0 |
| `test_dry_run_orcawave` | `--dry-run` prints the would-call line; mock not invoked | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\nSmoke test\ny\n`; flag `--dry-run`; `SUBMIT_JOB_OVERRIDE=$MOCK` | stdout contains `[DRY RUN]` and `orcawave`; mock capture file empty |
| `test_dry_run_orcaflex` | `--dry-run` works for orcaflex with a real input file | stdin: `2\noutput/orcaflex_validation/pipeline_test_model.dat\n\ny\n`; flag `--dry-run` | stdout contains `[DRY RUN]` and `orcaflex` |
| `test_missing_file_rejected_by_submit_job_sh` | Wrapper passes through a missing-file path; submit-job.sh is the gate that rejects it BEFORE any git op | stdin: `1\ndoes/not/exist.owd\n` (only 2 lines — wrapper has no `-f` check so it reaches Step 3 only if the user provides them, but the live test exercises the real submit-job.sh path); see implementation note below | exit 1; stderr contains submit-job.sh's canonical `input file not found` message; `git status --short queue/pending/` shows no new file |
| `test_empty_input_file_rejected` | Empty input string rejected by wrapper's clear error (UX only — not duplicate validation, since `submit-job.sh`'s `${2:?...}` would emit a Usage line for an empty positional arg) | stdin: `1\n\n` | exit 1; stderr contains `input file path is required` |
| `test_aqwa_delegates_and_shows_hint` | Selecting aqwa delegates to submit-job.sh (single gate) AND surfaces #2709 hint when delegate exits non-zero AND its stderr contains the canonical enum-rejection. Fixture is an arbitrary input file (the mock ignores content; AQWA-shape is not required) | stdin: `3\noutput/orcaflex_validation/pipeline_test_model.dat\ntest\ny\n`; mock configured to exit 1 AND emit `solver must be 'orcawave' or 'orcaflex'` on stderr | exit 1; mock called with `aqwa <file> test`; stderr contains `#2709` |
| `test_aqwa_no_hint_on_unrelated_failure` | After #2709 lands, an AQWA delegation that fails for a different reason (e.g. file-not-found) MUST NOT emit the #2709 hint | stdin: `3\noutput/orcaflex_validation/pipeline_test_model.dat\ntest\ny\n`; mock exits 1 AND emits `input file not found: foo` (NOT the enum message) on stderr | exit 1; stderr does NOT contain `#2709` |
| `test_cancel_at_confirm` | Answering N at confirmation exits 0; mock not invoked | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\ntest\nN\n` | exit 0; mock capture file empty |
| `test_live_delegation_orcawave` | Happy-path orcawave submits with correct positional args | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\nMy description\ny\n`; `SUBMIT_JOB_OVERRIDE=$MOCK` | mock called with: `orcawave output/orcaflex_validation/pipeline_test_model.dat My description` |
| `test_live_delegation_orcaflex` | Happy-path orcaflex delegates correctly | stdin: `2\noutput/orcaflex_validation/pipeline_test_model.dat\n\ny\n`; `SUBMIT_JOB_OVERRIDE=$MOCK` | mock called with: `orcaflex output/orcaflex_validation/pipeline_test_model.dat Solver job` |
| `test_default_description` | Empty description defaults to "Solver job" | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\n\ny\n` | mock called with `Solver job` as third arg |
| `test_invalid_menu_choice_exits_nonzero` | Choices other than 1/2/3 exit 1 | stdin: `9\n` | exit 1; stderr contains `Invalid menu choice` |
| `test_unknown_flag_exits_nonzero` | Unrecognized CLI flag exits 1 with usage hint | `bash submit-job-interactive.sh --foobar` (no stdin) | exit 1; output contains "Usage" |
| `test_solver_list_consistency` | **Drift-catcher (RESTORED in r3 per r2 Finding 4).** Greps the wrapper's `case` block and `submit-job.sh:13` for the same set of solver names; fails if menu and gate diverge. NOT duplicate validation — validation is in submit-job.sh; this test only protects menu discoverability against silent staleness as the supported-solver list evolves (e.g. when #2709 adds `aqwa`). | grep extracts `orcawave|orcaflex|aqwa` from both files | match set is equal |
| `test_no_queue_file_leakage` | **No-leakage guard (NEW per r2 Finding 10).** Implemented as a harness fixture wrapping every delegation-mock test: snapshot `git status --short queue/pending/` before, run test, snapshot after; fail loudly if any new YAML appeared. Catches forgotten `SUBMIT_JOB_OVERRIDE`. | runs before/after each delegation test | before-snapshot == after-snapshot for every test |

**Note on `test_missing_file_rejected_by_submit_job_sh` (r2 Finding 9 fix):** Stdin is `1\ndoes/not/exist.owd\n` — 2 lines only. The wrapper has no `-f` check (per r3 architecture decision), so after the user provides a path the wrapper proceeds to the description prompt. The test therefore EITHER (a) supplies a full stdin `1\ndoes/not/exist.owd\ntest\ny\n` and asserts that submit-job.sh produces the `input file not found` message on stderr after the wrapper reaches Step 5, OR (b) runs in `--dry-run` mode and uses a separate live `bash submit-job.sh aqwa does/not/exist.owd` invocation to confirm the gate behavior. The implementation phase picks (a) since it exercises the full delegation path. The test asserts submit-job.sh's canonical error string `input file not found`, not the wrapper's (because the wrapper no longer produces a missing-file error — r2 Finding 6 fix).

**Skill behavior checks** (manual, no automated harness for SKILL.md):
- Load the skill in a Claude session; verify it asks for solver, input file, description in order.
- Verify the skill's AQWA menu entry references [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709).
- Verify the skill does not invoke `submit-job.sh` without user confirmation.

---

## Acceptance Criteria

- [ ] `bash -n scripts/solver/submit-job-interactive.sh` will exit 0
- [ ] `bash scripts/solver/tests/test_submit_interactive.sh` — all 15 tests will pass (r3: +1 restored drift-catcher, +1 no-leakage guard, +1 aqwa-no-hint, –1 prior wrapper-error-message test redirected to submit-job.sh's message)
- [ ] End-to-end dry-run with a real git-tracked file: `printf '1\noutput/orcaflex_validation/pipeline_test_model.dat\nSmoke test\ny\n' | bash scripts/solver/submit-job-interactive.sh --dry-run` will print `[DRY RUN]` and exit 0 without modifying `queue/pending/`
- [ ] End-to-end missing-file rejection delegated to submit-job.sh: `printf '1\ndoes/not/exist.owd\ntest\ny\n' | bash scripts/solver/submit-job-interactive.sh` will exit 1 with submit-job.sh's canonical `input file not found` substring in stderr, AND `git status` will show no new files in `queue/pending/` (single source of truth: submit-job.sh:18-23)
- [ ] Selecting AQWA (option 3) with a valid input file will delegate to `submit-job.sh` which exits non-zero with the canonical enum error; the wrapper will additionally emit a `#2709` hint after the delegated failure, conditioned on the canonical enum-rejection substring appearing on stderr
- [ ] `git diff scripts/solver/submit-job.sh` → empty (file unchanged — verifies single source of truth preserved for BOTH solver enum AND missing-file gate)
- [ ] `.claude/skills/coordination/solver-submit/SKILL.md` will contain valid YAML frontmatter with `name: solver-submit`, `category: coordination`
- [ ] **Skill-discovery listing** (per issue scope): the new skill will be discoverable via the canonical surfaces — (a) `ls .claude/skills/coordination/ | grep solver-submit` returns the directory entry; (b) `docs/SKILLS_INDEX.md` coordination/subcategory aggregate count will be incremented by 1, OR `docs/SKILLS_INDEX.md` `Last Updated` date will be advanced and the new skill named in the coordination-category prose (whichever update style the file's current shape supports); (c) the skill will load when a Claude session invokes its name. The implementation phase will choose whichever SKILLS_INDEX.md update mode is least invasive (the file currently uses category-aggregate counts rather than per-skill listings).
- [ ] `scripts/solver/README.md` will contain an "Interactive Submission" section with usage examples for both the skill and the bash wrapper
- [ ] Review artifacts: BOTH date-stamps are accepted as authoritative. r1 review at `scripts/review/results/2026-05-14-plan-2710-codex.md`; r2 review (the authoritative round) at `scripts/review/results/2026-05-15-plan-2710-claude.md`. r1 Gemini and r2 Codex are UNAVAILABLE for reasons documented in the review-artifacts header (r2 Finding 12 fix: AC accepts the 2026-05-15 versions, not only the 2026-05-14 set).

---

## Adversarial Review Summary

| Round | Provider | Verdict | Key findings |
|---|---|---|---|
| r1 | Claude | not run | — |
| r1 | Codex | MAJOR | 5 blockers — addressed in r1 revision; **r1 Blocker 1 retracted in r3** (see annotation below) |
| r1 | Gemini | UNAVAILABLE | gemini CLI / sandbox |
| r2 | Codex | UNAVAILABLE | codex CLI 0.124.0 stdin-hang regression — see #2713 |
| r2 | Claude | MAJOR | 12 findings, 4 blockers (Findings 1, 2, 3, 5) — addressed in r3 inline rework |

**Overall result:** MAJOR (r1) → MAJOR (r2 cascading-false-premise) → r3 inline rework applied (rip duplicate-validation, restore drift-catcher, add no-leakage guard, add stderr-grep for AQWA hint, fix divergent error messages, fix selective-quote retrieval); ready for plan-review surface.

### Revisions made based on r2 review (r3 inline rework, 2026-05-15)

1. **r2 Finding 1 (BLOCKER) — false claim about `submit-job.sh`'s missing-file behavior.** Rewrote §Architecture Decision. Removed line ~141 assertion that "the current `submit-job.sh` writes the YAML and commits without ever checking if the input file exists." `submit-job.sh:18-23` has had the existence check since `71a53898b`. The wrapper now delegates the missing-file gate entirely.
2. **r2 Finding 2 (BLOCKER) — wrapper-layer `-f` check duplicated submit-job.sh:18-23 and violated AC 5.** Removed the `[[ ! -f "${REPO_ROOT}/${INPUT_FILE}" ]]` block from §Pseudocode Step 2. Wrapper now only guards empty-string input (UX message before submit-job.sh's `${2:?...}` Usage line) and prints a friendly `File: <path>` preview, neither of which validates.
3. **r2 Finding 3 (BLOCKER) — selective `submit-job.sh:8-16` quote in §Evidence hid the existing check.** Replaced with full `:8-23` quote covering both the solver-enum block AND the existence-check block. Added an explicit "Found:" entry naming `:18-23` as the missing-file gate.
4. **r2 Finding 4 — hardcoded `case` IS a second solver list (drift surface).** Acknowledged in §Architecture Decision. Restored `test_solver_list_consistency` to §TDD as a drift-catcher (NOT duplicate validation — protects menu discoverability against silent staleness).
5. **r2 Finding 5 (BLOCKER) — AQWA hint Pseudocode-vs-Risks mismatch.** Updated §Pseudocode Step 5 to capture submit-job.sh stderr to a tempfile and grep for the canonical enum-rejection substring `"solver must be 'orcawave' or 'orcaflex'"` as a hint precondition. After #2709 lands, AQWA failures won't carry that substring and the hint won't fire.
6. **r2 Finding 6 — divergent missing-file error messages (wrapper said "does not exist", submit-job.sh says "not found").** Removed the wrapper's missing-file error message entirely (the wrapper no longer validates). Users see submit-job.sh's canonical `input file not found` message. Updated test expectations accordingly.
7. **r2 Finding 7 — stale Adversarial Review Summary table.** Rebuilt the table with r1/r2 rounds, marking r2 Codex UNAVAILABLE (#2713 stdin-hang), r2 Claude MAJOR with 12 findings.
8. **r2 Finding 8 — `test_aqwa_delegates_and_shows_hint` fixture realism.** Updated the test description to "arbitrary input file (the mock ignores content; AQWA-shape is not required)" — cosmetic honesty fix.
9. **r2 Finding 9 — `test_missing_file_rejected_before_git` stdin had 5 lines but wrapper exited after 2.** Renamed test to `test_missing_file_rejected_by_submit_job_sh`; redesigned stdin to flow all the way through to submit-job.sh and assert on submit-job.sh's stderr message (not the wrapper's).
10. **r2 Finding 10 — `git status` before/after mitigation was in §Risks but not implemented.** Added `test_no_queue_file_leakage` as a harness fixture wrapping every delegation-mock test.
11. **r2 Finding 11 — source count off-by-one (13 vs. 14).** Updated §Evidence source count to 14 (also adds #2713 to the list of issues consulted, which is the additional source in this rework).
12. **r2 Finding 12 — review-artifact AC cited only 2026-05-14 paths.** Updated the AC to accept both 2026-05-14 (r1) and 2026-05-15 (r2) date-stamps with explicit per-artifact status (UNAVAILABLE noted where applicable).

### Revisions made based on r1 review (r1 revision, 2026-05-15) — annotated post-r2

1. **Blocker 1 — missing-file validation gap.** ~~Added explicit `[[ -f "${REPO_ROOT}/${INPUT_FILE}" ]]` check to `Pseudocode > Step 2` *before* confirmation and *before* delegation.~~ **RETRACTED in r3 — r2 caught that `submit-job.sh:18-23` already had the existence check since commit `71a53898b`; the r1 fix was based on a cascading false premise from the r1 Codex review. r3 rework rips out the duplicate-validation block introduced by r1.** The original r1 additions (`test_missing_file_rejected_before_git`, `test_empty_input_file_rejected`, real git-tracked `pipeline_test_model.dat` fixture) are RETAINED where they don't depend on the false premise — empty-input test stays (UX guard, not duplicate validation); missing-file test renamed and redirected to assert on submit-job.sh's canonical message; real fixture stays.
2. **Blocker 2 — mock-via-PATH strategy invalid.** Replaced PATH manipulation with a `SUBMIT_JOB_OVERRIDE` env-var. The wrapper resolves `SUBMIT_SCRIPT="${SUBMIT_JOB_OVERRIDE:-${SCRIPT_DIR}/submit-job.sh}"`. Tests set `SUBMIT_JOB_OVERRIDE` to an absolute path inside a tempdir mock, so live tests cannot reach the real `submit-job.sh` and cannot trigger git operations. Pseudocode and all delegation tests updated accordingly. **(RETAINED in r3.)**
3. **Blocker 3 — duplicated solver validation.** Rewrote the Architecture Decision section: the wrapper's menu is now UX-only and performs NO solver-enum validation. **(RETAINED and reinforced in r3 — Finding 4 acknowledgement adds drift-catcher test back.)**
4. **Blocker 4 — harness retrieval bundle skipped.** Added a new "Harness/Infrastructure bundle" subsection under Resource Intelligence Summary. **(RETAINED in r3.)**
5. **Blocker 5 — skill-discovery listing requirement dropped.** Added an explicit acceptance criterion verifying the new skill is discoverable. **(RETAINED in r3.)**

---

## Risks and Open Questions

- **Risk:** Tests must always set `SUBMIT_JOB_OVERRIDE` — a forgotten override would silently invoke the real `submit-job.sh` and push to git. Mitigation: `test_submit_interactive.sh` will export `SUBMIT_JOB_OVERRIDE` once at the top of the test harness (not per-test) AND `test_no_queue_file_leakage` (new in r3) snapshots `git status --short queue/pending/` before/after each delegation-mock test and fails loudly if any pending file appeared.
- **Risk:** When [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands and `submit-job.sh` adds `aqwa`, the wrapper's #2709 hint could become stale (would fire on unrelated AQWA failures). Mitigation: the hint code path checks for `${DELEGATE_EXIT} -ne 0` AND greps the captured submit-job.sh stderr for the canonical enum-rejection substring `"solver must be 'orcawave' or 'orcaflex'"`. Once #2709 lands and AQWA is accepted, that substring will not appear on AQWA failures and the hint will not fire. `test_aqwa_no_hint_on_unrelated_failure` enforces this. A reminder comment in the wrapper code points the #2709 author to remove the hint block entirely once AQWA is fully supported.
- **Risk:** `submit-job-interactive.sh` uses `read` for stdin; in non-interactive environments (cron, CI) it will hang. Mitigation: `--dry-run` plus piped stdin is the only supported non-interactive mode; callers in CI must use `submit-job.sh` directly. Document this in the README update.
- **Risk:** The hardcoded `case` menu can drift out of sync with `submit-job.sh:13` (e.g. if a new solver is added to submit-job.sh but not to the menu). This is NOT a validation defect — the menu is presentation-only — but it is a discoverability defect. Mitigation: `test_solver_list_consistency` greps both files for the same set of solver names and fails on divergence. The test runs in CI alongside the other suite entries.
- **Open:** Should the wrapper accept pre-filled `--solver` and `--input-file` flags to skip prompts entirely? Not required by the issue; deferred. Can be added without breaking the interactive path.
- **Open:** Should `solver-submit` be cross-linked in `config/agents/skill-graph-index.yaml`? Not required by the issue; deferred to a follow-up if a related skill ever depends on it.
- **Open:** Should r2 be re-run once codex CLI 0.124.0 stdin-hang (#2713) is resolved? Per `feedback_r3_inline_loop_break_pattern`, r3 inline rework is appropriate when r1 and r2 surface DIFFERENT defects each round (the cascading-false-premise pattern); a third Codex round is not required to land plan-approval, though it remains optional follow-up.

---

## Complexity: T2

**T2** — 4 files: 2 new (SKILL.md, interactive bash wrapper), 1 new test file, 1 modified (README.md), plus a minor SKILLS_INDEX.md edit. No changes to existing implementation logic. The skill is a documentation artifact; the bash wrapper is ~70 lines with interactive `read` prompts and one delegation call (no validation logic — all delegated to submit-job.sh). Test suite is new infrastructure following an env-var-override mock pattern (safer than PATH manipulation for absolute-path invocations), plus a no-leakage harness fixture. No engineering domain knowledge required. Classification unchanged from r0/r1.
