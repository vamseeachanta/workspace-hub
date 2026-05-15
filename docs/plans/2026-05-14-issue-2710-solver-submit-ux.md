# Plan for #2710: feat(solver-queue): conversational submit UX — /solver-submit skill + interactive CLI

> **Status:** draft (revised after r1 Codex review — 5 blockers addressed)
> **Complexity:** T2
> **Date:** 2026-05-14 (drafted) / 2026-05-15 (r1 revision)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2710
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2710-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/solver/submit-job.sh:1-44` — the authoritative single-source-of-truth CLI; accepts positional args `<solver> <input_file> [description]`; solver validation at lines 13–16 is hardcoded `orcawave | orcaflex`; creates YAML job file, commits, and pushes. This plan proposes no modifications to this file.
- Found: `scripts/solver/submit-job.sh:13-16` — solver enum: `if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]` — hardcoded, not derived from schema.
- Found: `queue/job-schema.yaml:14` — `solver: "orcawave | orcaflex"` — documented as pipe-separated string, not a YAML sequence enum; Option B (parse schema for supported solvers) carries fragility risk given this format.
- Found: `scripts/solver/submit-batch.sh:20-25,119-128` — `--dry-run` flag pattern; callers pass `--dry-run`, wrapper skips the `bash submit-job.sh` call and emits a dry-run trace instead; interactive wrapper will mirror this pattern.
- Found: `scripts/solver/README.md:65-79` — existing Usage section documents only positional-arg invocations; needs a new "Interactive Submission" section.
- Found: `.claude/skills/coordination/` — 55 SKILL.md subdirectories under this directory; three sampled for frontmatter shape:
  - `session-start-routine/SKILL.md:1-9` — frontmatter: `name`, `description`, `version`, `category`, `tags`, `related_skills`
  - `agent-label-routing/SKILL.md:1-17` — frontmatter: `name`, `description`, `version`, `category`, `type`, `trigger`, `auto_execute`, `capabilities`, `tools`, `scripts`
  - `licensed-machine-prompt-orchestration/SKILL.md:1-10` — frontmatter: `name`, `description`, `version`, `author`, `license`, `metadata.hermes.tags`
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md:1-10` — canonical reference: `name`, `description`, `version`, `author`, `category`, `tags`, `related_skills`
- Found: `output/orcaflex_validation/pipeline_test_model.dat` — git-tracked OrcaFlex input model (131,874 bytes); will be used as the real-file fixture for `--dry-run` acceptance check (replaces the previous fictional `path/to/test.owd`).
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

**File existence** (verified 2026-05-14 / re-verified 2026-05-15 for r1 revision):
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

**Line excerpts** (`scripts/solver/submit-job.sh:8-16`):
```
SOLVER="${1:?Usage: submit-job.sh <solver> <input_file> [description]}"
INPUT_FILE="${2:?Usage: submit-job.sh <solver> <input_file> [description]}"
DESCRIPTION="${3:-Solver job}"

# Validate solver type
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
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

**Source count:** 13 distinct sources (issue body + #2709 + #2708 + `submit-job.sh` + `submit-batch.sh` + `queue/job-schema.yaml` + 3x SKILL.md frontmatter sampling + `README.md` + `CONTROL_PLANE_CONTRACT.md` + `behavior-contract.yaml` + `coding-style.md` + `patterns.md` + `docs/SKILLS_INDEX.md`). Exceeds minimum of 3.

---

## Architecture Decision

**Solver validation: single-source-of-truth — wrapper presents a menu for UX only; canonical validation happens in `submit-job.sh`.**

(This decision was rewritten in the r1 revision in response to Codex blocker 3.) The wrapper presents a numbered menu so the user can discover supported solvers, but the wrapper itself performs no string-level enum validation. The user's menu choice is mapped to a solver token and passed raw to `submit-job.sh`. If the user picks a choice that `submit-job.sh` does not yet accept (e.g. `aqwa` before [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands), the wrapper relays whatever exit status and stderr `submit-job.sh` produces — there is no parallel rejection path. This keeps `submit-job.sh:13-16` as the single solver gate, which satisfies the issue's "No duplicate validation logic" acceptance criterion.

Two consequences:
1. The menu still includes `aqwa` because the issue requires graceful handling. The wrapper labels that entry `[may be unsupported — see #2709]` but does NOT short-circuit; on selection, the wrapper still delegates to `submit-job.sh` and the user sees the canonical error: `ERROR: solver must be 'orcawave' or 'orcaflex', got 'aqwa'`. The wrapper additionally prints a one-line hint pointing to #2709 *after* the delegated call returns non-zero. This hint is presentation, not validation.
2. Input-file existence checking is also delegated to `submit-job.sh` for the validation gate proper. **However**, per the issue acceptance ("Both wrappers reject missing input files with a clear error before any git operations") the wrapper performs an *early existence check* against `${REPO_ROOT}/${INPUT_FILE}` purely to *short-circuit before any git operations*. This is not duplicate enum-style validation — it's a UX guard that mirrors a precondition `submit-job.sh` is silent about (the current `submit-job.sh` writes the YAML and commits without ever checking if the input file exists; the issue acceptance demands this gap be closed at the wrapper layer until `submit-job.sh` itself is extended).

**AQWA handling before [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands:**

Per the decision above, the wrapper includes AQWA in the menu, delegates to `submit-job.sh` (which rejects it), and prints a one-line hint that AQWA support depends on #2709. The user gets exit-code 1 from the delegated process plus an informative hint — no parallel validation logic.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2710-solver-submit-ux.md` |
| Skill | `.claude/skills/coordination/solver-submit/SKILL.md` |
| Interactive wrapper | `scripts/solver/submit-job-interactive.sh` |
| Tests | `scripts/solver/tests/test_submit_interactive.sh` |
| README update | `scripts/solver/README.md` |
| Plan review — Claude | `scripts/review/results/2026-05-14-plan-2710-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-14-plan-2710-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-14-plan-2710-gemini.md` |

---

## Deliverable

A `/solver-submit` Claude skill (`.claude/skills/coordination/solver-submit/SKILL.md`) and a `scripts/solver/submit-job-interactive.sh` bash wrapper that will guide users through job submission via interactive prompts, delegating all validation and queue-write operations to the existing `scripts/solver/submit-job.sh` without duplicating its solver-enum logic. The wrapper performs only one early check — input-file existence — to satisfy the issue's pre-git-rejection acceptance criterion.

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

    # Step 2: input file — empty AND missing-file checks BEFORE git operations.
    # (r1 revision: added explicit file-existence check per issue acceptance.)
    prompt "Input file path (relative to repo root): "
    read INPUT_FILE
    if [[ -z "${INPUT_FILE}" ]]; then
        print "ERROR: input file path is required" >&2
        exit 1
    fi
    if [[ ! -f "${REPO_ROOT}/${INPUT_FILE}" ]]; then
        print "ERROR: input file does not exist: ${REPO_ROOT}/${INPUT_FILE}" >&2
        print "       (resolved from REPO_ROOT=${REPO_ROOT})" >&2
        exit 1
    fi

    # Step 3: description
    prompt "Description [optional, press Enter to use default]: "
    read DESCRIPTION
    if [[ -z "${DESCRIPTION}" ]]; then DESCRIPTION="Solver job"; fi

    # Step 4: confirmation summary (raw user choice — no enum guard here)
    print "  Solver:      ${SOLVER}"
    print "  Input file:  ${INPUT_FILE}"
    print "  Description: ${DESCRIPTION}"
    prompt "Submit? [y/N]: "
    read CONFIRM
    if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
        print "Cancelled."
        exit 0
    fi

    # Step 5: delegate to submit-job.sh (or override for tests)
    if [[ "${DRY_RUN}" == "true" ]]; then
        print "[DRY RUN] Would call: bash ${SUBMIT_SCRIPT} ${SOLVER} ${INPUT_FILE} ${DESCRIPTION}"
        exit 0
    fi
    # Capture exit status so we can append the AQWA hint when relevant.
    bash "${SUBMIT_SCRIPT}" "${SOLVER}" "${INPUT_FILE}" "${DESCRIPTION}"
    DELEGATE_EXIT=$?
    if [[ "${SOLVER}" == "aqwa" && "${DELEGATE_EXIT}" -ne 0 ]]; then
        print "" >&2
        print "HINT: AQWA support depends on #2709 (not yet landed)." >&2
        print "      See https://github.com/vamseeachanta/workspace-hub/issues/2709" >&2
    fi
    exit "${DELEGATE_EXIT}"
```

**`.claude/skills/coordination/solver-submit/SKILL.md` steps (what the skill document instructs Claude to do):**

```
1. Ask: "Which solver?" — present numbered menu with orcawave, orcaflex, and aqwa [may be unsupported — see #2709]
2. Ask: "What is the input file path?" (relative to repo root)
3. Verify the file exists: use Read tool or `ls "${REPO_ROOT}/<path>"` before proceeding; refuse to delegate if missing
4. Ask: "Optional description? (press Enter to skip)"
5. Summarise: show the submit-job.sh command that will be run
6. Ask: "Confirm submission? [y/N]"
7. If confirmed: run `bash scripts/solver/submit-job.sh <solver> <input_file> <description>`
8. Report: echo the job file path and queue processing ETA from submit-job.sh stdout
9. If user chose `aqwa` and the call exited non-zero, surface the #2709 hint
```

The skill performs NO solver-enum validation of its own. The menu is a discovery aid; the delegated call is the gate.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/skills/coordination/solver-submit/SKILL.md` | New skill — conversational submission guide for Claude sessions |
| Create | `scripts/solver/submit-job-interactive.sh` | New bash wrapper — guided interactive submission for SSH terminals |
| Create | `scripts/solver/tests/test_submit_interactive.sh` | TDD test suite for the interactive wrapper |
| Modify | `scripts/solver/README.md` | Add "Interactive Submission" section documenting both new artifacts |

`scripts/solver/submit-job.sh` is **NOT modified** — it remains the single source of truth for solver-enum validation and queue write logic. Both new layers delegate to it; only input-file existence is checked early at the wrapper layer (per issue acceptance).

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

All tests live in `scripts/solver/tests/test_submit_interactive.sh`. Tests substitute a mock `submit-job.sh` by setting the `SUBMIT_JOB_OVERRIDE` env-var to an absolute path inside a per-test tempdir (e.g. `mktemp -d`). The wrapper honours `SUBMIT_JOB_OVERRIDE` and runs that path instead of `${SCRIPT_DIR}/submit-job.sh`, so tests CANNOT accidentally invoke the real submit-job.sh and trigger a git commit/push. The mock captures the positional args it receives to a tempfile and exits with a configurable status. (This replaces the r0 PATH-based mock strategy, which was invalid for absolute-path invocations — Codex blocker 2.)

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_syntax_check` | Script passes `bash -n` | `bash -n scripts/solver/submit-job-interactive.sh` | exit 0 |
| `test_dry_run_orcawave` | `--dry-run` prints the would-call line; mock not invoked | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\nSmoke test\ny\n`; flag `--dry-run`; `SUBMIT_JOB_OVERRIDE=$MOCK` | stdout contains `[DRY RUN]` and `orcawave`; mock capture file empty |
| `test_dry_run_orcaflex` | `--dry-run` works for orcaflex with a real input file | stdin: `2\noutput/orcaflex_validation/pipeline_test_model.dat\n\ny\n`; flag `--dry-run` | stdout contains `[DRY RUN]` and `orcaflex` |
| `test_missing_file_rejected_before_git` | Wrapper exits 1 BEFORE any delegation when input file does not exist (issue acceptance) | stdin: `1\ndoes/not/exist.owd\nx\ny\n`; `SUBMIT_JOB_OVERRIDE=$MOCK` | exit 1; stderr contains `input file does not exist`; mock capture file empty |
| `test_empty_input_file_rejected` | Empty input string rejected with clear error | stdin: `1\n\n` | exit 1; stderr contains `input file path is required` |
| `test_aqwa_delegates_and_shows_hint` | Selecting aqwa delegates to submit-job.sh (single gate) AND surfaces #2709 hint when delegate fails | stdin: `3\noutput/orcaflex_validation/pipeline_test_model.dat\ntest\ny\n`; mock configured to exit 1 simulating submit-job.sh's enum rejection | exit 1; mock called with `aqwa <file> test`; stderr contains `#2709` |
| `test_cancel_at_confirm` | Answering N at confirmation exits 0; mock not invoked | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\ntest\nN\n` | exit 0; mock capture file empty |
| `test_live_delegation_orcawave` | Happy-path orcawave submits with correct positional args | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\nMy description\ny\n`; `SUBMIT_JOB_OVERRIDE=$MOCK` | mock called with: `orcawave output/orcaflex_validation/pipeline_test_model.dat My description` |
| `test_live_delegation_orcaflex` | Happy-path orcaflex delegates correctly | stdin: `2\noutput/orcaflex_validation/pipeline_test_model.dat\n\ny\n`; `SUBMIT_JOB_OVERRIDE=$MOCK` | mock called with: `orcaflex output/orcaflex_validation/pipeline_test_model.dat Solver job` |
| `test_default_description` | Empty description defaults to "Solver job" | stdin: `1\noutput/orcaflex_validation/pipeline_test_model.dat\n\ny\n` | mock called with `Solver job` as third arg |
| `test_invalid_menu_choice_exits_nonzero` | Choices other than 1/2/3 exit 1 | stdin: `9\n` | exit 1; stderr contains `Invalid menu choice` |
| `test_unknown_flag_exits_nonzero` | Unrecognized CLI flag exits 1 with usage hint | `bash submit-job-interactive.sh --foobar` (no stdin) | exit 1; output contains "Usage" |

**Note on solver-list drift:** the r0 plan included `test_solver_list_consistency`, which grepped both files for the solver names. Removed in r1 because the new architecture has no second solver list in the wrapper — `submit-job.sh:13-16` is the single gate; nothing to cross-check. If `submit-job.sh` accepts new solvers, the wrapper's menu remains a UX-only advisory and stays valid.

**Skill behavior checks** (manual, no automated harness for SKILL.md):
- Load the skill in a Claude session; verify it asks for solver, input file, description in order.
- Verify the skill's AQWA menu entry references [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709).
- Verify the skill does not invoke `submit-job.sh` without user confirmation.

---

## Acceptance Criteria

- [ ] `bash -n scripts/solver/submit-job-interactive.sh` will exit 0
- [ ] `bash scripts/solver/tests/test_submit_interactive.sh` — all 12 tests will pass (note: count increased from 10 in r0; +2 missing-file/empty-input tests, –1 solver-list-consistency removed, +1 invalid-menu, +1 aqwa-with-hint)
- [ ] End-to-end dry-run with a real git-tracked file: `printf '1\noutput/orcaflex_validation/pipeline_test_model.dat\nSmoke test\ny\n' | bash scripts/solver/submit-job-interactive.sh --dry-run` will print `[DRY RUN]` and exit 0 without modifying `queue/pending/`
- [ ] End-to-end missing-file rejection: `printf '1\ndoes/not/exist.owd\nx\ny\n' | bash scripts/solver/submit-job-interactive.sh` will exit 1 with `input file does not exist` in stderr, AND `git status` will show no new files in `queue/pending/` (proves no git operation occurred)
- [ ] Selecting AQWA (option 3) with a valid input file will delegate to `submit-job.sh` which exits non-zero with the canonical enum error; the wrapper will additionally emit a `#2709` hint after the delegated failure
- [ ] `git diff scripts/solver/submit-job.sh` → empty (file unchanged — verifies single source of truth preserved)
- [ ] `.claude/skills/coordination/solver-submit/SKILL.md` will contain valid YAML frontmatter with `name: solver-submit`, `category: coordination`
- [ ] **Skill-discovery listing** (per issue scope): the new skill will be discoverable via the canonical surfaces — (a) `ls .claude/skills/coordination/ | grep solver-submit` returns the directory entry; (b) `docs/SKILLS_INDEX.md` coordination/subcategory aggregate count will be incremented by 1, OR `docs/SKILLS_INDEX.md` `Last Updated` date will be advanced and the new skill named in the coordination-category prose (whichever update style the file's current shape supports); (c) the skill will load when a Claude session invokes its name. The implementation phase will choose whichever SKILLS_INDEX.md update mode is least invasive (the file currently uses category-aggregate counts rather than per-skill listings).
- [ ] `scripts/solver/README.md` will contain an "Interactive Submission" section with usage examples for both the skill and the bash wrapper
- [ ] Review artifacts will be posted to `scripts/review/results/2026-05-14-plan-2710-{claude,codex,gemini}.md`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex (r1) | MAJOR | 5 blockers — addressed in this revision (see "Revisions made" below) |
| Codex (r2) | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** MAJOR — revised. r2 pending.

### Revisions made based on r1 review

1. **Blocker 1 — missing-file validation gap.** Added explicit `[[ -f "${REPO_ROOT}/${INPUT_FILE}" ]]` check to `Pseudocode > Step 2` *before* confirmation and *before* delegation, so the rejection occurs before any git operation. Added `test_missing_file_rejected_before_git` and `test_empty_input_file_rejected` to TDD list. Updated all dry-run examples in TDD and Acceptance Criteria to use `output/orcaflex_validation/pipeline_test_model.dat` (git-tracked, verified 131,874 bytes) instead of the fictional `path/to/test.owd`.
2. **Blocker 2 — mock-via-PATH strategy invalid.** Replaced PATH manipulation with a `SUBMIT_JOB_OVERRIDE` env-var. The wrapper resolves `SUBMIT_SCRIPT="${SUBMIT_JOB_OVERRIDE:-${SCRIPT_DIR}/submit-job.sh}"`. Tests set `SUBMIT_JOB_OVERRIDE` to an absolute path inside a tempdir mock, so live tests cannot reach the real `submit-job.sh` and cannot trigger git operations. Pseudocode and all delegation tests updated accordingly.
3. **Blocker 3 — duplicated solver validation.** Rewrote the Architecture Decision section: the wrapper's menu is now UX-only and performs NO solver-enum validation. The user's menu choice is mapped to a solver token and passed raw to `submit-job.sh`, which remains the single gate. AQWA is included in the menu but delegated through; the canonical rejection comes from `submit-job.sh`. The wrapper only appends a #2709 hint *after* the delegated failure. Pseudocode rewritten; `test_solver_list_consistency` removed (no second list to drift-check); `test_aqwa_delegates_and_shows_hint` added to prove the single-gate behaviour.
4. **Blocker 4 — harness retrieval bundle skipped.** Added a new "Harness/Infrastructure bundle" subsection under Resource Intelligence Summary documenting consultation of `docs/standards/CONTROL_PLANE_CONTRACT.md`, `config/agents/behavior-contract.yaml`, `config/agents/skill-graph-index.yaml`, and all four files under `.claude/rules/`. Surfaced one APPLIES constraint (`.claude/rules/coding-style.md:9` — no hardcoded absolute paths; the wrapper uses `git rev-parse --show-toplevel` and `${SCRIPT_DIR}` resolution to comply).
5. **Blocker 5 — skill-discovery listing requirement dropped.** Identified `docs/SKILLS_INDEX.md` as the canonical skill catalog (currently aggregates by category rather than enumerating each skill). Added an explicit acceptance criterion verifying the new skill is discoverable via (a) directory entry, (b) SKILLS_INDEX.md update, and (c) Claude-session load. The implementation phase will pick the least-invasive SKILLS_INDEX.md edit shape given the file's existing aggregate format.

---

## Risks and Open Questions

- **Risk:** Tests must always set `SUBMIT_JOB_OVERRIDE` — a forgotten override would silently invoke the real `submit-job.sh` and push to git. Mitigation: `test_submit_interactive.sh` will export `SUBMIT_JOB_OVERRIDE` once at the top of the test harness (not per-test) and the harness will additionally check `git status --short queue/pending/` before/after each test to fail loudly if any pending file appeared.
- **Risk:** When [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands and `submit-job.sh` adds `aqwa`, the wrapper's #2709 hint becomes stale (would fire on unrelated AQWA failures). Mitigation: the hint code path checks for `${DELEGATE_EXIT} -ne 0` AND specifically grep for the canonical enum-rejection message in stderr; once #2709 lands and AQWA is accepted, the hint will not fire. A reminder comment in the wrapper code points the #2709 author to remove the hint block entirely.
- **Risk:** `submit-job-interactive.sh` uses `read` for stdin; in non-interactive environments (cron, CI) it will hang. Mitigation: `--dry-run` plus piped stdin is the only supported non-interactive mode; callers in CI must use `submit-job.sh` directly. Document this in the README update.
- **Risk:** Input-file existence check at the wrapper layer creates a small surface for divergence: if `submit-job.sh` ever grows its own missing-file check with different semantics (e.g. different error message), the two layers could disagree. Mitigation: the wrapper's error message is intentionally distinct ("input file does not exist") so it's traceable to the wrapper layer; if `submit-job.sh` adds the same check, the wrapper check becomes a redundant early-exit and the duplication is a UX latency optimisation, not a validation conflict.
- **Open:** Should the wrapper accept pre-filled `--solver` and `--input-file` flags to skip prompts entirely? Not required by the issue; deferred. Can be added without breaking the interactive path.
- **Open:** Should `solver-submit` be cross-linked in `config/agents/skill-graph-index.yaml`? Not required by the issue; deferred to a follow-up if a related skill ever depends on it.

---

## Complexity: T2

**T2** — 4 files: 2 new (SKILL.md, interactive bash wrapper), 1 new test file, 1 modified (README.md), plus a minor SKILLS_INDEX.md edit. No changes to existing implementation logic. The skill is a documentation artifact; the bash wrapper is ~80 lines with interactive `read` prompts, one early file-existence check, and one delegation call. Test suite is new infrastructure following an env-var-override mock pattern (safer than PATH manipulation for absolute-path invocations). No engineering domain knowledge required. Classification unchanged from r0.
