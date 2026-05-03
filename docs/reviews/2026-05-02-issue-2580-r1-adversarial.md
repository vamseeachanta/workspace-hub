# Issue #2580 Plan — Adversarial Review r1

**Verdict:** MAJOR
**Reviewer:** Claude (Opus 4.7) — adversarial stance
**Plan SHA at review:** 72765593c0ad3a010b78c7ab5d64e4cf2b062f14

## P1 Defects (block approval)

1. **Stale local conftest contradicts plan's "remaining ignores" claim.** The local working-tree `digitalmodel/tests/conftest.py` (lines 43-50) still ignores both `citations/test_registry.py` AND `citations/test_schema.py`. The plan asserts citation ignores were already removed by PR #542 and the implementation is "yml-utilities only". But the digitalmodel checkout at `/mnt/local-analysis/workspace-hub/digitalmodel` is on branch `fix/triage-punch-list-2026-05-02` at SHA `0faf6416`, which does not include #542's removals. `origin/main` (commit `b1346acb`, "test(citations): vendor wiki fixtures..." merged 2026-05-02T10:57:49Z) DOES remove them. The plan must explicitly state which base commit the implementation rebases onto and verify locally before editing — pseudocode line "if base branch already includes PR #542 ... else ... do not partially close" is too soft. Without a hard preflight `git merge-base --is-ancestor b1346acb HEAD` check the implementer will edit the wrong tree.

2. **TDD test list is structurally invalid.** Six rows are stub-named identically (`..._uses_stable_capture_or_logging`) and target unspecified diagnostic paths. The actual six capsys-using test functions in `test_yml_utilities_additional.py` are: `test_ymlinput_ignores_bad_update_file_and_keeps_defaults` (line 99), `test_analyze_yaml_keys_prints_root_keys` (113), `test_compare_yaml_root_keys_same_and_different` (169 — two assertions), `test_compare_yaml_files_deepdiff_emits_same_message_for_identical` (189), `test_save_diff_files_writes_expected_outputs_and_invokes_save_data` (204), `test_save_diff_files_reports_same_when_no_diff` (230). Plan must name these directly. Codex's earlier MAJOR called out grouped/non-concrete TDD rows; the patch did not actually fix the smell.

3. **Plan undercounts capsys sites.** Plan and issue say "6 tests use `capsys`". `grep -c capsys` returns **13 occurrences** across **8 test functions** (added: `test_save_diff_files_handles_mixed_diff_keys` at 242 uses monkeypatch — but counting by signature, 7 test functions accept `capsys`). The off-by-one between issue ("6") and ground truth means either the issue scope is wrong or the plan inherits an undercounted scope. The plan must reconcile and explicitly enumerate, not paraphrase.

## P2 Concerns (fix recommended, not blocking)

1. **Mock-vs-live divergence risk** (memory: `feedback_mock_vs_live_invocation_divergence.md`). Plan proposes converting `print()` in `yml_utilities.py` to `logger.info/warning`. But `analyze_yaml_keys` (line 84), `compare_yaml_root_keys` (93-96), and `compare_yaml_files_deepdiff` (108) appear to be a user-facing CLI/REPL surface — switching to `logging` silently changes production behavior for any caller that relied on stdout. Plan acknowledges this in Risks but the "Files to Change" row says "emit log records" unconditionally. Required: enumerate each `print()` call (there are ~7 in the source) and tag KEEP-as-print vs. CONVERT-to-log per call site, with caller analysis.

2. **No xdist-mode CI verification procedure.** Acceptance criterion says "pass under reproduced CI/xdist mode" but does not specify the invocation: `pytest -n auto`? `-n 4`? Issue claims `worker_id` is loaded but `capsys` is not — plan never verifies this claim against pytest-xdist documentation or a live repro. Add concrete: `PYTHONPATH=src uv run pytest -n auto tests/asset_integrity/test_yml_utilities_additional.py` before/after.

3. **No before/after pass-count procedure.** AC says "no regression in pass count from current post-#2574 baseline (925+)". No baseline-capture step in pseudocode. Add: `pytest --collect-only | wc -l` and `pytest -q | tail -1` before refactor, save to issue closeout evidence.

4. **Vendored-fixture freshness mechanism missing for #542 dependency.** Plan calls out staleness risk in Risks but proposes no mechanism. Suggest: add a check that hashes `tests/citations/fixtures/.../dnv-os-e301.md` against `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` when both are present, and emit a stale-fixture warning. (Out of scope for #2580 closeout but should be a follow-up issue, not a silent gap.)

5. **Past-tense drift faint signal.** Resource Intelligence line 14 ("Option B is already implemented in digitalmodel PR #542... 14 citation tests passed") describes upstream work as fact. Verified true (PR merged 10:57Z), but section structure invites future plans to copy this pattern for non-merged PRs. Tag merged-vs-open clearly.

## Verified Claims

- `digitalmodel#542` MERGED 2026-05-02T10:57:49Z to `origin/main` at SHA `b1346acb`. Citation entries removed from `origin/main:tests/conftest.py`.
- Local working-tree conftest still has citation entries (branch `fix/triage-punch-list-2026-05-02`, behind origin/main).
- `yml_utilities.py` contains 7 `print()` calls at lines 43, 84, 93, 95-96, 108, 135, 162. Source-under-test exists.
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` exists in workspace-hub.
- No `llm-wiki` references found in the plan (clean on hyphen-path pattern).
- `_repo_root()` walks `here.parents` for `knowledge/wikis/` ancestor — matches plan description.
- 8 test functions accept `capsys` parameter in the file (not 6 as issue states).
- Other `capsys` users elsewhere in digitalmodel (8+ files) are unaffected by this plan's scope.

## Recommendation

Plan needs a revision (r2 draft) addressing the three P1 items before it is review-ready. Specifically: (a) hard preflight on `b1346acb` ancestry, (b) name all 7-8 affected test functions explicitly with line numbers, (c) reconcile the "6 vs 8" capsys count with issue scope. Do NOT transition labels; user retains approval gate.
