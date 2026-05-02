# Plan for #2580: Fix digitalmodel citations and capsys tests currently collect-ignored

> **Status:** draft (nightly batch 2 recovered missing canonical plan; 2026-05-02 Codex/Claude MAJOR findings require narrowing before approval)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2580
> **Review artifacts:** `scripts/review/results/2026-05-02-plan-2580-codex.md`; `scripts/review/results/2026-05-02-plan-2580-claude.md`; `scripts/review/prompts/2026-05-02-plan-2580-gemini-rerun.md` if Gemini capacity/tooling is unavailable

---

## Resource Intelligence Summary

### Existing repo code
- Found: Issue #2580 owner comment at 2026-05-02T02:24:42Z — citations Option B is already implemented in digitalmodel PR https://github.com/vamseeachanta/digitalmodel/pull/542 on branch `feature/2580-vendor-citations-wiki-fixtures` commit `918d5b28`; 14 citation tests passed; citations collect-ignore entries were removed there. Codex verified the actual fixture path on that PR is `tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`. Do **not** duplicate citation fixture work in this plan.
- Historical context only: `/mnt/local-analysis/agent-worktrees/digitalmodel-integration-main-2490/tests/citations/test_registry.py` and `tests/citations/test_schema.py` showed the pre-PR upward `knowledge/wikis/` search. This stale worktree is no longer authoritative for citation implementation scope.
- Found: `/mnt/local-analysis/agent-worktrees/digitalmodel-integration-main-2490/tests/asset_integrity/test_yml_utilities_additional.py` — six issue-listed tests use `capsys` and assert printed output from `digitalmodel.asset_integrity.common.yml_utilities` helpers.
- Found: `/mnt/local-analysis/agent-worktrees/digitalmodel-integration-main-2490/tests/conftest.py` — central `collect_ignore` list exists; #2580 states #2574 added the citations and yml-utilities files to that list in the branch/CI context and requires removing those ratchet ignores after fixing the root causes.
- Gap: remaining unimplemented scope is `tests/asset_integrity/test_yml_utilities_additional.py` capture/xdist failure plus removal of its collect-ignore entry. The plan must first reproduce the actual failing command/error before changing `print()`/`capsys` to logging/`caplog`, because pytest supports `capsys` and xdist's documented limitation is not a blanket fixture incompatibility.

### Standards
| Standard | Status | Source |
|---|---|---|
| Plan approval hard stop | applies | `docs/standards/HARD-STOP-POLICY.md` — implementation remains blocked until user approval. |
| Engineering/code citation contract | relevant | `.claude/rules/calc-citation-contract.md` and the digitalmodel citation tests require fail-closed citation resolution. |
| TDD requirement | applies | Issue is test-remediation work; tests must be written/adjusted before implementation and fail before the production/test-fixture fix. |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — canonical workspace-hub wiki path named by `tests/citations/test_schema.py`; the implementation should vendor only the minimal fixture content needed by tests, not depend on this checkout at runtime.
- `knowledge/wikis/engineering/wiki/entities/digitalmodel.md` — confirms digitalmodel is tracked as a tier-1 engineering project in workspace-hub knowledge surfaces.

### Documents consulted
- Issue #2580 body — defines the two defect classes, explicitly recommends option B for citations (vendor small fixtures) and option A for yml utilities (replace `print()`/`capsys` path with logging/`caplog`).
- Issue #2574 — cited by #2580 as the temporary Quality Gates unblock that added ratchet ignores; this issue is the required cleanup, not a new ignore.
- Digitalmodel PR #542 — owner-supplied evidence that the citation half is already implemented and should be treated as dependency/merge evidence, not future work.
- `/mnt/local-analysis/agent-worktrees/digitalmodel-integration-main-2490/AGENTS.md` — digitalmodel test command contract: `PYTHONPATH=src uv run python -m pytest`; key modules include `src/digitalmodel/asset_integrity/`.

### Gaps identified
- `yml_utilities` output path must be made xdist-safe; tests should use `caplog` after source code emits logging records rather than relying on `capsys`.
- Remaining yml-utilities ratchet ignore in `digitalmodel/tests/conftest.py` must be removed after the yml tests pass.
- PR #542 must be merged or otherwise present in the implementation branch before closing #2580; if it is not merged, implementation must branch from it rather than recreating its citation fixture work.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02T05:08Z via `gh issue view`):
- `#2580` — OPEN, label `status:plan-review` — `fix(digitalmodel-tests): citations + capsys tests collect-ignored, need real fixes`
- `#2574` — referenced by #2580 as the temporary collect-ignore unblock.
- `digitalmodel#542` — OPEN PR per #2580 owner comment; citation fixture work shipped there.

**File existence / excerpts** (verified 2026-05-02 from `/mnt/local-analysis/agent-worktrees/digitalmodel-integration-main-2490`):
- Historical stale-worktree evidence: `tests/citations/test_registry.py` and `tests/citations/test_schema.py` in `/mnt/local-analysis/agent-worktrees/digitalmodel-integration-main-2490` show the pre-PR `_repo_root()` defect. Current implementation scope must use PR #542 as the source of truth.
- EXISTS: `tests/asset_integrity/test_yml_utilities_additional.py` lines 99-120 show `capsys` usage in issue-listed tests.
- EXISTS: `tests/conftest.py` central `collect_ignore` list; exact #2574 ignore entries must be rechecked in the implementation worktree before editing.

**Gap proofs**:
- Owner comment says PR #542 vendored the fixture with the resolver-compatible `knowledge/wikis/...` prefix and passed `tests/citations/` locally; this supersedes the stale local worktree gap proof.
- `search_files` for prior `docs/plans/*2580*` in workspace-hub returned no canonical plan before this draft.

<!-- Verification: count distinct sources: issue #2580, issue #2574, digitalmodel AGENTS.md, three digitalmodel test/source paths, workspace-hub wiki path. Count >= 7. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2580-digitalmodel-collect-ignore-test-fixes.md` |
| Plan index | `docs/plans/README.md` |
| Citation tests | `digitalmodel/tests/citations/test_registry.py`, `digitalmodel/tests/citations/test_schema.py` |
| Citation fixture tree dependency from PR #542 | `digitalmodel/tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` (dependency evidence only; not created by this plan) |
| YML utility source | `digitalmodel/src/digitalmodel/asset_integrity/common/yml_utilities.py` |
| YML utility tests | `digitalmodel/tests/asset_integrity/test_yml_utilities_additional.py` |
| Collect-ignore cleanup | `digitalmodel/tests/conftest.py` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-2580-codex.md` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-2580-claude.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2580-gemini.md` or `scripts/review/prompts/2026-05-02-plan-2580-gemini-rerun.md` if unavailable |

---

## Deliverable

A digitalmodel test cleanup that completes the remaining yml-utilities half of #2580: make the six yml-utilities tests pytest-xdist-safe via logging/`caplog`, remove their temporary collect-ignore entry, and verify the already-open citation PR #542 is merged/present so the issue can close without duplicating citation fixture work.

---

## Pseudocode

```text
preflight dependency check:
  verify digitalmodel PR #542 is merged or checked out as the base branch
  verify citations tests pass from that base: PYTHONPATH=src uv run python -m pytest -q tests/citations/
  do not edit citation fixtures/tests unless #542 is unavailable; if unavailable, stop and report dependency blocker

capture-root-cause preflight:
  run the exact failing command from CI/#2574/#2580 for tests/asset_integrity/test_yml_utilities_additional.py with and without xdist
  record the failing assertion/error in the issue closeout evidence
  only proceed with print->logging/caplog refactor if the reproduced failure shows captured stdout is the root cause; otherwise patch the actual failing behavior and update tests accordingly

logging/caplog remediation:
  identify yml_utilities print statements exercised by six ignored tests
  add module logger = logging.getLogger(__name__)
  replace user-visible print diagnostics with logger.info/warning/error as appropriate
  update issue-listed tests to use caplog.at_level(...) and assert record messages
  avoid monkeypatching sys.stdout unless a reviewed line is intentionally stdout-only

collect-ignore cleanup:
  confirm exact #2574 ignore entries in the implementation branch
  if base branch already includes PR #542:
    remove only the remaining yml_utilities additional entry tied to #2580
  else if base branch is main without PR #542:
    stop and merge/rebase PR #542 first, or explicitly remove citation ignores only as part of bringing in that PR; do not partially close #2580 from a branch that lacks the citation fix
  run targeted pytest for the ten affected tests
  run the digitalmodel quality-gate subset / full available suite per repo contract
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/asset_integrity/common/yml_utilities.py` | emit log records for diagnostics asserted by tests |
| Modify | `digitalmodel/tests/asset_integrity/test_yml_utilities_additional.py` | replace `capsys` assertions with `caplog` assertions for six issue-listed tests |
| Modify | `digitalmodel/tests/conftest.py` | remove only the remaining #2574 temporary collect-ignore entry for `tests/asset_integrity/test_yml_utilities_additional.py` after fixes pass; citation entries are handled by PR #542 |
| Update | `docs/plans/README.md` | index this recovered plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_yml_utilities_current_failure_reproduced_without_collect_ignore` | actual #2580 yml failure is captured before refactor | branch with yml collect-ignore temporarily disabled | exact failing command/error recorded; if failure is not stdout/capture related, plan is revised before implementation |
| `test_ymlinput_ignores_bad_update_file_uses_stable_capture_or_logging` | one issue-listed yml diagnostic path is xdist-safe | `caplog` or source-appropriate capture and temp files | expected diagnostic observed under local and `pytest -n auto` runs |
| `test_ymlinput_ignores_bad_update_stem_uses_stable_capture_or_logging` | second issue-listed diagnostic path is xdist-safe | same | expected diagnostic observed under local and `pytest -n auto` runs |
| `test_ymlinput_ignores_bad_master_file_uses_stable_capture_or_logging` | third issue-listed diagnostic path is xdist-safe | same | expected diagnostic observed under local and `pytest -n auto` runs |
| `test_ymlinput_ignores_bad_master_stem_uses_stable_capture_or_logging` | fourth issue-listed diagnostic path is xdist-safe | same | expected diagnostic observed under local and `pytest -n auto` runs |
| `test_ymlinput_logs_saved_output_path_with_worker_safe_tmpdir` | output-path diagnostic is worker-safe | pytest tmp_path/worker-specific output root | no shared output collision; diagnostic observed |
| `test_ymlinput_collect_ignore_removed_after_fix` | yml ratchet ignore is gone after tests pass | `tests/conftest.py` content | yml test file/function is not collect-ignored; citation ignores absent only when PR #542 is merged/present |
| collect-ignore regression check | ratchet ignores are gone | `tests/conftest.py` content | no #2580 citation/yml utility entries remain |

---

## Acceptance Criteria

- [ ] PR #542 (or its merge commit) is present before closeout; citations tests pass without workspace-hub `knowledge/wikis/` checkout and are not reimplemented by this plan. The dependency fixture path is `tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`.
- [ ] The actual yml failure is reproduced and recorded before the refactor; if the root cause is not captured stdout under xdist, the implementation follows the observed failure rather than forcing `caplog`.
- [ ] All six `test_yml_utilities_additional.py` tests listed in #2580 pass under the reproduced CI/xdist mode using source-appropriate stable diagnostics.
- [ ] Temporary #2574 collect-ignore entry for `tests/asset_integrity/test_yml_utilities_additional.py` is removed from `digitalmodel/tests/conftest.py`; citation ignore cleanup remains credited to PR #542.
- [ ] Targeted command passes from digitalmodel root after PR #542 is present: `PYTHONPATH=src uv run python -m pytest tests/citations/ tests/asset_integrity/test_yml_utilities_additional.py -q`.
- [ ] Broader quality gate shows no regression in pass count from the current post-#2574 baseline (issue states 925+ on CI after #2574 lands), or any unrelated failures are documented with exact failing tests.
- [ ] No implementation starts until #2580 has valid adversarial review evidence and user approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | MAJOR (latest 2026-05-02 rerun) | `scripts/review/results/2026-05-02-plan-2580-codex.md` — found fixture path mismatch, unproven xdist/capture root cause, grouped/non-concrete TDD rows, and branch-state ambiguity for collect-ignore cleanup. This revision patches those defects; fresh rerun still required. |
| Claude | UNAVAILABLE (latest 2026-05-02 rerun) | `scripts/review/results/2026-05-02-plan-2580-claude.md` — provider timed out after patch; earlier same-day Claude findings about PR #542 drove the narrowing but the durable latest artifact is unavailable, not approval evidence. |
| Gemini | pending / unavailable artifact if capacity fails | `scripts/review/results/2026-05-02-plan-2580-gemini.md` or rerun prompt artifact |

**Overall result:** missing-plan drift recovered to `draft`, then fresh Codex MAJOR findings plus earlier same-day Claude narrowing findings were patched in this revision. Latest Claude is `UNAVAILABLE`, so this is still not approval-ready until a fresh rerun confirms the narrowed yml-utilities scope and PR #542 dependency handling.

---

## Risks and Open Questions

- **Risk:** The inspected digitalmodel worktree may not include the exact #2574 collect-ignore additions or PR #542 branch state. Implementation must re-sync the target digitalmodel branch before editing and remove only verified remaining #2580-related ignore entries.
- **Risk:** Vendoring a wiki fixture can drift from canonical workspace-hub content. Mitigation: keep the fixture minimal, document it as a test contract fixture, and do not use it as engineering source authority.
- **Risk:** Some yml utility output may intentionally be CLI stdout rather than diagnostics. Mitigation: only convert issue-listed diagnostic paths to logging; if user-facing stdout is contractual, use `monkeypatch.setattr(sys, "stdout", io.StringIO())` in those tests instead of broad refactors.
- **Open:** Exact xdist failure signature should be captured from CI or a local xdist run during implementation; this plan preserves the issue's `caplog` recommendation unless live evidence shows stdout is contractual.

---

## Complexity: T2

Multiple test files, one production utility module, dependency/branch-state verification for PR #542, and collect-ignore cleanup. TDD and plan approval gate apply.
