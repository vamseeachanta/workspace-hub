# Plan for #2710: feat(solver-queue): conversational submit UX — /solver-submit skill + interactive CLI

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-14
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
- Found: `.claude/skills/coordination/` — 60+ SKILL.md files in this directory; three sampled for frontmatter shape:
  - `session-start-routine/SKILL.md:1-9` — frontmatter: `name`, `description`, `version`, `category`, `tags`, `related_skills`
  - `agent-label-routing/SKILL.md:1-17` — frontmatter: `name`, `description`, `version`, `category`, `type`, `trigger`, `auto_execute`, `capabilities`, `tools`, `scripts`
  - `licensed-machine-prompt-orchestration/SKILL.md:1-10` — frontmatter: `name`, `description`, `version`, `author`, `license`, `metadata.hermes.tags`
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md:1-10` — canonical reference: `name`, `description`, `version`, `author`, `category`, `tags`, `related_skills`
- Gap: `.claude/skills/coordination/solver-submit/` — does not exist; will be created by this plan.
- Gap: `scripts/solver/submit-job-interactive.sh` — does not exist; will be created by this plan.
- Gap: No test files for submit-job scripts (`ls scripts/solver/test_submit*.sh` → no results); new bats-style tests will be added under `scripts/solver/tests/`.

### Standards

Not applicable — harness/tooling UX change; no engineering standards involved.

### LLM Wiki pages consulted

No relevant wiki pages. Solver queue is an internal workflow tool, not a domain knowledge area.

### Documents consulted

- Issue [#2710](https://github.com/vamseeachanta/workspace-hub/issues/2710) — full scope: skill at `.claude/skills/coordination/solver-submit/SKILL.md`, bash wrapper at `scripts/solver/submit-job-interactive.sh`, README update at `scripts/solver/README.md`; 6 acceptance criteria (skill generates valid YAML, bash produces identical outcome, invalid solver names rejected, missing files trigger pre-git errors, no duplicated validation logic, AQWA handled gracefully).
- Issue [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) — OPEN — AQWA runner adapter; adds `aqwa` to solver enum in `submit-job.sh`; this plan must not add AQWA to the supported list until #2709 lands; plan addresses AQWA gracefully per acceptance criterion 6.
- Issue [#2708](https://github.com/vamseeachanta/workspace-hub/issues/2708) — OPEN — OrcaFlex live validation on licensed-win-1; informational for this plan; `orcaflex` is already in the enum; that issue validates the dispatch path end-to-end but does not change the submit-side API.
- `scripts/solver/README.md` — existing documentation; this plan adds an "Interactive Submission" section.
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

**File existence** (verified 2026-05-14):
- EXISTS: `scripts/solver/submit-job.sh`
- EXISTS: `scripts/solver/submit-batch.sh`
- EXISTS: `scripts/solver/README.md`
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `.claude/skills/coordination/issue-planning-mode/SKILL.md`
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

**Source count:** 8 distinct sources (issue body + #2709 + #2708 + `submit-job.sh` + `submit-batch.sh` + `queue/job-schema.yaml` + 3x SKILL.md frontmatter sampling + `README.md`). Exceeds minimum of 3.

---

## Architecture Decision

**Solver enumeration approach: Option A — hardcoded list in both layers.**

`queue/job-schema.yaml:14` stores the solver enum as a prose pipe-separated string (`"orcawave | orcaflex"`), not a YAML sequence. Option B would require regex-splitting a human-prose field with no machine-contract guarantee on format. The hardcoded list in `submit-job.sh:13-16` is the actual runtime gate; the skill and interactive wrapper will mirror it exactly. When [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands and updates `submit-job.sh`, the wrapper and skill will be updated in the same PR — the correct coupling point is the runtime validator, not the documentation string in `job-schema.yaml`.

Trade-off: the solver list will drift if `submit-job.sh` is updated without updating the wrapper/skill. Mitigated by a `test_solver_list_consistency` test that cross-checks the wrapper's menu against `submit-job.sh`'s validator condition via grep.

**AQWA handling before [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands: Option B — include in the menu with `[blocked: #2709]` tag.**

Including AQWA in the menu with a clear "blocked by #2709" label is more informative than silently omitting it. Users who select AQWA receive an immediate, actionable error message pointing to the open issue rather than a confusing generic "invalid solver" error. The interactive wrapper will detect the `aqwa` selection, print the blocked message referencing #2709, and exit non-zero without calling `submit-job.sh`.

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

A `/solver-submit` Claude skill (`.claude/skills/coordination/solver-submit/SKILL.md`) and a `scripts/solver/submit-job-interactive.sh` bash wrapper that will guide users through job submission via interactive prompts, delegating all validation and queue-write operations to the existing `scripts/solver/submit-job.sh` without duplicating its logic.

---

## Pseudocode

**`submit-job-interactive.sh` flow:**

```
function main():
    parse_args:
        --dry-run → DRY_RUN=true
        unknown flags → print usage, exit 1

    print_header: "=== Solver Job Submission ==="

    # Step 1: solver selection
    print numbered menu:
        [1] orcawave   — OrcaWave hydrodynamic diffraction
        [2] orcaflex   — OrcaFlex dynamic mooring and riser
        [3] aqwa       — [blocked: #2709 not yet landed]
    read CHOICE from stdin
    if CHOICE == 3:
        print "ERROR: AQWA support requires #2709 to land first."
        print "       See https://github.com/vamseeachanta/workspace-hub/issues/2709"
        exit 1
    if CHOICE not in (1, 2): print "Invalid choice", exit 1
    resolve SOLVER: 1 → "orcawave", 2 → "orcaflex"

    # Step 2: input file
    prompt "Input file path (relative to repo root): "
    read INPUT_FILE
    if INPUT_FILE is empty: print "ERROR: input file required", exit 1

    # Step 3: description
    prompt "Description [optional, press Enter to use default]: "
    read DESCRIPTION
    if DESCRIPTION is empty: DESCRIPTION="Solver job"

    # Step 4: confirmation summary
    print "  Solver:      <SOLVER>"
    print "  Input file:  <INPUT_FILE>"
    print "  Description: <DESCRIPTION>"
    prompt "Submit? [y/N]: "
    read CONFIRM
    if CONFIRM not in ("y", "Y"): print "Cancelled.", exit 0

    # Step 5: delegate to submit-job.sh
    SCRIPT_DIR = $(dirname $(realpath $0))
    SUBMIT_SCRIPT = "${SCRIPT_DIR}/submit-job.sh"
    if DRY_RUN:
        print "[DRY RUN] Would call: bash ${SUBMIT_SCRIPT} ${SOLVER} ${INPUT_FILE} ${DESCRIPTION}"
        exit 0
    exec bash "${SUBMIT_SCRIPT}" "${SOLVER}" "${INPUT_FILE}" "${DESCRIPTION}"
```

**`.claude/skills/coordination/solver-submit/SKILL.md` steps (what the skill document instructs Claude to do):**

```
1. Ask: "Which solver?" — present numbered menu with orcawave, orcaflex, and aqwa [blocked: #2709]
2. If user picks aqwa: explain the block, reference #2709, stop.
3. Ask: "What is the input file path?" (relative to repo root)
4. Verify the file exists: use Read tool or ls to check before proceeding
5. Ask: "Optional description? (press Enter to skip)"
6. Summarise: show the submit-job.sh command that will be run
7. Ask: "Confirm submission? [y/N]"
8. If confirmed: run bash scripts/solver/submit-job.sh <solver> <input_file> <description>
9. Report: echo the job file path and queue processing ETA from submit-job.sh stdout
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/skills/coordination/solver-submit/SKILL.md` | New skill — conversational submission guide for Claude sessions |
| Create | `scripts/solver/submit-job-interactive.sh` | New bash wrapper — guided interactive submission for SSH terminals |
| Create | `scripts/solver/tests/test_submit_interactive.sh` | TDD test suite for the interactive wrapper |
| Modify | `scripts/solver/README.md` | Add "Interactive Submission" section documenting both new artifacts |

`scripts/solver/submit-job.sh` is **NOT modified** — it remains the single source of truth for validation and queue write logic. Both new layers delegate to it.

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

All tests live in `scripts/solver/tests/test_submit_interactive.sh`. Tests use a mock `submit-job.sh` injected via `PATH` manipulation so they do not touch git or the network. The mock captures args and exits 0 (or non-zero for error-path tests).

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_syntax_check` | Script passes `bash -n` | `bash -n scripts/solver/submit-job-interactive.sh` | exit 0 |
| `test_dry_run_orcawave` | `--dry-run` prints the would-call line; mock not invoked | stdin: `1\npath/to/test.owd\nSmoke test\ny\n`; flag `--dry-run` | stdout contains `[DRY RUN]` and `orcawave`; mock capture empty |
| `test_dry_run_orcaflex` | `--dry-run` works for orcaflex | stdin: `2\npath/to/test.dat\n\ny\n`; flag `--dry-run` | stdout contains `[DRY RUN]` and `orcaflex` |
| `test_aqwa_blocked_exit1` | Selecting aqwa (option 3) exits non-zero with `#2709` reference | stdin: `3\n` | exit 1; output contains `#2709` |
| `test_cancel_at_confirm` | Answering N at confirmation exits 0; mock not invoked | stdin: `1\npath/to/test.owd\ntest\nN\n` | exit 0; mock capture empty |
| `test_live_delegation_orcawave` | Happy-path orcawave submits with correct positional args | stdin: `1\npath/to/test.owd\nMy description\ny\n` | mock called with: `orcawave path/to/test.owd My description` |
| `test_live_delegation_orcaflex` | Happy-path orcaflex delegates correctly | stdin: `2\npath/to/model.dat\n\ny\n` | mock called with: `orcaflex path/to/model.dat Solver job` |
| `test_default_description` | Empty description defaults to "Solver job" | stdin: `1\npath/to/test.owd\n\ny\n` | mock called with `Solver job` as third arg |
| `test_solver_list_consistency` | Wrapper's non-blocked solver list matches `submit-job.sh` validator condition | grep both files for solver names | same set of non-blocked solvers in both files |
| `test_unknown_flag_exits_nonzero` | Unrecognized CLI flag exits 1 with usage hint | `bash submit-job-interactive.sh --foobar` (no stdin) | exit 1; output contains "Usage" |

**Skill behavior checks** (manual, no automated harness for SKILL.md):
- Load the skill in a Claude session; verify it asks for solver, input file, description in order.
- Verify the skill's AQWA menu entry references [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709).
- Verify the skill does not invoke `submit-job.sh` without user confirmation.

---

## Acceptance Criteria

- [ ] `bash -n scripts/solver/submit-job-interactive.sh` will exit 0
- [ ] `bash scripts/solver/tests/test_submit_interactive.sh` — all 10 tests will pass
- [ ] End-to-end: `echo "1\npath/to/test.owd\nSmoke test\ny" | bash scripts/solver/submit-job-interactive.sh --dry-run` will print `[DRY RUN]` and exit 0 without modifying `queue/pending/`
- [ ] Selecting AQWA (option 3) will exit non-zero and include `#2709` in the error output
- [ ] `git diff scripts/solver/submit-job.sh` → empty (file unchanged)
- [ ] `.claude/skills/coordination/solver-submit/SKILL.md` will contain valid YAML frontmatter with `name: solver-submit`, `category: coordination`
- [ ] `scripts/solver/README.md` will contain an "Interactive Submission" section with usage examples for both the skill and the bash wrapper
- [ ] Review artifacts will be posted to `scripts/review/results/2026-05-14-plan-2710-{claude,codex,gemini}.md`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING

Revisions made based on review: none yet — plan is draft.

---

## Risks and Open Questions

- **Risk:** `queue/job-schema.yaml` solver field is prose, not a machine-parseable YAML enum. Option B was rejected; Option A (hardcoded list) is used instead. If `submit-job.sh` adds a solver without updating the wrapper, `test_solver_list_consistency` will catch the drift — but only if that test is run as part of the #2709 PR CI. Mitigation: document this test as a required CI step in the #2709 plan.
- **Risk:** When [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) lands, the interactive wrapper and skill must be updated in the same PR to remove the `[blocked: #2709]` tag and add `aqwa` to the live menu. If this is missed, the AQWA block remains even after AQWA is live. Mitigation: add a reminder comment in the wrapper code and reference `#2709` explicitly so the PR author sees it.
- **Risk:** `submit-job-interactive.sh` uses `read` for stdin; in non-interactive environments (cron, CI) it will hang. Mitigation: `--dry-run` is the only supported non-interactive mode; callers in CI must use `submit-job.sh` directly. Document this in the README update.
- **Open:** Should the wrapper accept pre-filled `--solver` and `--input-file` flags to skip prompts entirely? Not required by the issue; deferred. Can be added without breaking the interactive path.
- **Open:** Should `test_solver_list_consistency` use `grep -E` or `grep -F` to match the solver names? Implementation decision — use `grep -F` on the string literals to avoid regex false matches. Flag for implementer.

---

## Complexity: T2

**T2** — 4 files: 2 new (SKILL.md, interactive bash wrapper), 1 new test file, 1 modified (README.md). No changes to existing implementation logic. The skill is a documentation artifact; the bash wrapper is ~70 lines with interactive `read` prompts and one `exec` delegation. Test suite is new infrastructure following the existing mock-via-PATH pattern from `scripts/review/tests/`. No engineering domain knowledge required.
