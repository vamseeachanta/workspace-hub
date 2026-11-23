# Plan for #2817: feat(harness): atomic approve-issue helper (label + marker in one command)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2817
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-27-plan-2817-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- **EXISTS**: `scripts/ai/approve-provider-plan.py` — heavyweight 670-line Python approval
  transaction CLI for provider-credit Kanban (#2665). Requires 3-provider review artifacts
  (claude/codex/gemini APPROVE/MINOR/MAJOR verdicts) and a canonical plan file before
  executing. Covers journal → quarantine marker → label transition → verification → promote.
  **Not a replacement**: its preconditions (review artifacts, plan-file SHA) are incompatible
  with the lightweight daily-approve use case (issue already reviewed by user; no
  multi-provider review yet; or Kanban ceremony intentionally skipped).
- **EXISTS**: `.planning/plan-approved/` — directory with per-issue markdown markers.
  Existing markers (e.g., `1962.md`, `2027.md`) use a minimal format: title, Approved by,
  Scope, Date.
- **EXISTS**: `scripts/enforcement/require-plan-approval.sh:68` — validates marker at
  `.planning/plan-approved/${REQUIRE_ISSUE}.md`; this is the gate the new script feeds.
- **EXISTS**: `scripts/enforcement/check-marker-label-parity.sh:93` — enforces label ↔
  marker parity (marker present ↔ `status:plan-approved` label present).
- **GAP**: No `approve-issue.sh` or equivalent lightweight bash helper anywhere in
  `scripts/`. The two-step process is documented in issue-planning-mode but not scripted.

### Standards

Not applicable — harness tooling issue.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — approve flow: apply label,
  create marker. No runnable command cited, only prose description.
- `scripts/ai/approve-provider-plan.py` — source of truth for marker content format
  (`build_marker_text()` at line 312) and label transition command (line 362–364).
- `.planning/plan-approved/2027.md` — example marker (Title, Approved by, Scope, Date).
- Issue #2801 — where the `&&` chain broke, orphaning the marker and blocking implementation.

### Gaps identified

- No lightweight bash helper for the simple (non-Kanban) daily-approve flow.
- `issue-planning-mode/SKILL.md` approve step has no runnable command — only prose.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-27 via GitHub MCP):
- `#2817` — OPEN — feat(harness): atomic approve-issue helper (label + marker in one command)

**File existence** (`ls` 2026-05-27):
- EXISTS: `scripts/ai/approve-provider-plan.py`
- EXISTS: `.planning/plan-approved/` (directory with 10+ markers)
- EXISTS: `scripts/enforcement/require-plan-approval.sh`
- EXISTS: `scripts/enforcement/check-marker-label-parity.sh`
- EXISTS: `scripts/workflow/` (directory — approve-issue.sh will live here)
- MISSING (new — this plan creates): `scripts/workflow/approve-issue.sh`
- MISSING (new — this plan creates): `tests/workflow/test_approve_issue.sh`

**Gap proofs:**
```
$ find scripts/ -name "approve-issue*" 2>/dev/null
(no output — script does not exist)
```

**Reproduction proofs:** N/A — tooling gap, not a runtime failure. The breakage from #2801
was a `&&` chain failure during manual execution; no automated test exists to catch it.

<!-- Verification: sources consulted = issue body (#1) + approve-provider-plan.py (#2) +
     .planning/plan-approved/2027.md (#3) + require-plan-approval.sh (#4) +
     issue-planning-mode/SKILL.md (#5). Count: 5 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-27-issue-2817-atomic-approve-issue-helper.md` |
| Implementation | `scripts/workflow/approve-issue.sh` |
| Tests | `tests/workflow/test_approve_issue.sh` |
| Skill doc update | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Plan review — Claude | `scripts/review/results/2026-05-27-plan-2817-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-27-plan-2817-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-27-plan-2817-gemini.md` |

---

## Deliverable

A `scripts/workflow/approve-issue.sh` script that atomically applies `status:plan-approved`
label AND creates `.planning/plan-approved/<N>.md` marker in a single user-run command, with
fail-loud behavior if either step fails, and an optional `--commit` flag to immediately
commit and push the marker.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/workflow/approve-issue.sh` | main implementation (~60 lines) |
| Create | `tests/workflow/test_approve_issue.sh` | TDD test suite using pattern from `tests/enforcement/test_client_wiki_registry.sh` |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | add runnable command to approve step |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

Tests live in `tests/workflow/test_approve_issue.sh` using the same bash-test harness
pattern as `tests/enforcement/test_client_wiki_registry.sh`. Each test uses a tmp dir for
`.planning/plan-approved/` and a mock `gh` binary on PATH.

| Test name | What it verifies | Setup | Expected result |
|---|---|---|---|
| `test_missing_issue_arg` | exits non-zero without args | bare invocation | exit 1 + usage message on stderr |
| `test_non_numeric_issue` | rejects non-numeric issue number | `approve-issue.sh abc` | exit 1 |
| `test_label_applied_and_marker_created` | happy path end-to-end | mock `gh` exits 0; writable tmp marker dir | `.planning/plan-approved/2817.md` exists, exit 0 |
| `test_marker_content_fields` | marker contains required fields | same setup | file contains "Approved by:" and today's date |
| `test_no_marker_if_label_fails` | atomicity: no marker if label step fails | mock `gh` exits 1 | marker NOT created, exit non-zero |
| `test_commit_flag_triggers_git` | `--commit` calls `git add` + `git commit` | mock `git` binary records calls | git commit called with `#2817` in message |
| `test_already_approved_exits_nonzero` | idempotency guard: exits if marker already exists | pre-create marker file | exit 1, no duplicate label call |

---

## Acceptance Criteria

- [ ] `scripts/workflow/approve-issue.sh <N>` applies `status:plan-approved` label and creates
  `.planning/plan-approved/<N>.md` in a single command
- [ ] If `gh issue edit` fails: no marker is created; script exits non-zero with explicit error
- [ ] If marker creation fails after label succeeds: script prints manual recovery command
  (`gh issue edit <N> --remove-label status:plan-approved`) and exits non-zero
- [ ] `--commit` flag: `git add .planning/plan-approved/<N>.md && git commit -m "chore: approve #<N>"` on success
- [ ] Marker format matches existing markers (Title, Approved by, Date fields)
- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` references `approve-issue.sh` in the approve step
- [ ] All tests pass: `bash tests/workflow/test_approve_issue.sh`
- [ ] `scripts/enforcement/require-plan-approval.sh` still validates the produced marker
  (spot-check: run with `REQUIRE_ISSUE=<test-N>` against a marker the script created)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Gemini | TBD | — |

**Overall result:** PENDING (review not yet run)

---

## Risks and Open Questions

- **Risk (partial-apply):** If label succeeds but marker write fails, the issue carries
  `status:plan-approved` without a marker — which trips `check-marker-label-parity.sh`.
  Mitigation: write marker to a tmp file first, then atomic `mv`; only set the label AFTER
  `mv` succeeds. This reverses the order from the issue body's suggestion.
- **Risk (overlap with approve-provider-plan.py):** The two scripts coexist with different
  preconditions. Documenting this split clearly in `issue-planning-mode/SKILL.md` is
  required to prevent confusion about when each applies.
- **Open:** Should `approve-issue.sh` also remove `status:plan-review` (the mirror of what
  `approve-provider-plan.py` does)? The issue body only says "apply `status:plan-approved`",
  but removing `plan-review` too is operationally cleaner. Recommend: yes, remove `plan-review`
  if present (non-fatal if absent).

---

## Complexity: T1

**T1** — single new shell script (~60 lines), one skill-doc section update, no new
dependencies, no multi-file implementation cascade.
