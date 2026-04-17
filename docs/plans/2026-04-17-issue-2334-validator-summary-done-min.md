# Plan for #2334: Reconcile validator default `summary_done_min=0.55` with production reality

> **Status:** plan-review
> **Complexity:** T1
> **Date:** 2026-04-17 (rev-3 after Claude MINOR + Codex MAJOR on rev-2)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2334
> **Parents:** #1878 (closed), #2309 (closed)
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2334-claude.md | ...-codex.md

---

## Revision Note

- **rev-1:** draft — proposed default 0.55 → 0.10 (Option A). Both reviewers returned MAJOR.
- **rev-2:** rewrote with 0.13, test-count correction, motivation reframe, YAML additive, historical-contract reconciliation. Claude MINOR; Codex MAJOR (partly sandbox-read process issue, partly new content findings).
- **rev-3** — addresses the substantive findings from both rev-2 reviews:
  1. **"20% relative headroom precedent" framing dropped** (Claude F1 + Codex F3). Verified from `docs/plans/2026-04-17-issue-2309-summary-fields-split.md` that #2309's 0.70 default was not derived from a systemic rule — it was a single pragmatic floor below 75% against 87.90% measurement. Rev-3 defends 0.13 on its own terms: **absolute ~3pp margin below the 16.13% measurement, with any value in [0.12, 0.14] defensible.** 0.13 chosen over 0.12 because the one-significant-figure margin matches the granularity of the upstream measurement (16.1%); 0.14 rejected as too tight (only 2.1pp headroom).
  2. **Historical-contract framing corrected** (Codex F2). The `#1878` *plan* AC was actually `>=55%` (already relaxed from 60% per Gemini review — see `docs/plans/2026-04-16-issue-1878-restore-index-metadata.md:306`). `#2308` already acknowledged 16.1% reality in its own plan. Only the *issue bodies* of #1878/#2308 carry the 55% target as written text. Rev-3 frames this correctly and narrows the reclassification scope.
  3. **Aspirational target no longer goes into `status.index_jsonl_only`** (Codex F4). That block is a measured-facts block (see line 13 `status:` root + the `index_jsonl_only` sub-block containing only percentages and dates). Injecting `summary_done_aspirational_target: 0.55` pollutes the schema. Rev-3 records the aspirational target as a **comment in the validator module docstring** — the one place a reader of the CLI will actually see it — and drops the maturity-YAML addition entirely. No registry companion update needed.
  4. **Docstring-parity test tightened** (Claude F2). The test now imports `validate_index_metadata._parse_args` (Python module import — file name has hyphens, so we use `importlib.util` from the SCRIPT path) and asserts `ns.summary_done_min == 0.13`, plus reads the module's `__doc__` attribute and asserts it contains the anchored substring `"--summary-done-min           0.13"` (whitespace-exact match). This cannot pass spuriously because both must be updated in lockstep.
  5. **Test fixture coupling fixed** (Codex F5). Both rewritten tests now use `_mix_with_file_exists()` with enough `n_file_exists_true` to clear `--summary-file-exists-min 0.70`, isolating the `summary_done` dimension.
  6. **Closeout-comment gate limits documented** (Codex F6). The closeout-comment paste is a discipline gate, not a CI hook. Mechanical enforcement via pre-commit or CI is out of scope for T1 and filed as a future follow-up if the pattern recurs.
  7. **TDD row 4 reclassified as regression guard** (Claude F5 NIT). Minor note in TDD table; not a design change.

---

## Resource Intelligence Summary

### Existing repo code

- Verified: `scripts/data/document-index/validate-index-metadata.py:19` — docstring threshold line `    --summary-done-min           0.55`. Mirror edit required.
- Verified: `scripts/data/document-index/validate-index-metadata.py:35` — `p.add_argument("--summary-done-min", type=float, default=0.55)`. Only argparse default to change.
- Verified: `tests/data/document-index/test_validate_index_metadata.py` has **9 test functions**. The two that depend on the 0.55 default: `test_validator_rejects_low_summary_done` (line 85, uses `_mix(..., n_summary_true=50)`) and `test_validator_thresholds_overridable_via_cli` (line 107, uses `_mix_with_file_exists(..., n_summary_true=50, n_file_exists_true=80)`).
- Verified: neither test uses a fixture that isolates the `summary_done` dimension — both currently pass-through on the `summary_file_exists` dimension by accident (test 85 via empty `_mix()` fixtures that omit `summary_file_exists` entirely, which the validator sum-counts as 0 True). **Fixture rewrites must use `_mix_with_file_exists()` and supply `n_file_exists_true` high enough (≥70) to avoid triggering the 0.70 `--summary-file-exists-min` threshold.**
- Verified: no `.github/workflows/`, `.pre-commit-config.yaml`, `scripts/enforcement/`, or Makefile caller of `validate-index-metadata.py` exists today. Validator is manual/ad-hoc.
- Verified: `data/document-index/resource-intelligence-maturity.yaml::status.index_jsonl_only` contains only measured percentages + dates (see line 58-59 changelog notes). It is a telemetry block, not a policy block. No `targets:` or `policy:` block exists at any level.

### Standards
Not applicable.

### LLM Wiki pages consulted
Not applicable.

### Documents consulted

| Source | Finding |
|---|---|
| Issue #2334 body | Three options (A lower default / B document aspirational / C two modes). Rev-3 still recommends A with floor **0.13**. |
| `docs/plans/2026-04-16-issue-1878-restore-index-metadata.md:306` | Final #1878 plan AC: `>=55% summary_done=True (relaxed from 60% per Gemini; still well under projected 83.7%)`. Corrects rev-2's claim of 60%. |
| `docs/plans/2026-04-16-issue-2308-gotcha-refresh.md:32` | #2308 plan already acknowledged 16.1% reality — "This plan corrects the second pre-condition to reality." No binding `>=55%` AC at #2308 close. |
| Issue #1878 body | Carries `>=60%` as an aspirational statement in the body text; never amended. |
| Issue #2308 body | Carries `>=55%` as a pre-condition; plan revised it downward but issue body untouched. |
| `docs/plans/2026-04-17-issue-2309-summary-fields-split.md` | Verified the 0.70 default for `summary_file_exists_min` was NOT derived from a "20% relative headroom rule". It was a single pragmatic reviewer-suggested floor. Rev-3 no longer cites it as precedent. |
| `data/document-index/resource-intelligence-maturity.yaml` | Telemetry block; not suitable for policy/aspirational fields. |
| `docs/handoffs/2026-04-17-issue-1878-family-complete-handoff.md::gotcha #6` | Empirical observation that motivated this issue. |

Source count: 8 distinct.

### Gaps identified

- No test pins docstring-vs-argparse-default parity today — a one-sided edit currently passes review unnoticed.
- Aspirational 55% target is not documented anywhere a future reader of the validator CLI will see it.
- Validator docstring has no calibration context (which corpus it was tuned for, measurement date).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2334-validator-summary-done-min.md` |
| Implementation | `scripts/data/document-index/validate-index-metadata.py` |
| Tests | `tests/data/document-index/test_validate_index_metadata.py` |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2334-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2334-codex.md` |

**Artifacts NOT changed (rev-3):** `data/document-index/resource-intelligence-maturity.yaml` (the aspirational field was dropped); `intelligence-accessibility-registry.yaml` (no new field to declare).

---

## Deliverable

Validator default `--summary-done-min` = `0.13`. Module docstring threshold line and argparse default are updated in lockstep. Module docstring gains a calibration note: "calibrated against `data/document-index/index.jsonl` at 2026-04-17, observed rate 16.13%; original aspirational target 55% preserved here as design history, not a live threshold." Two existing tests are rewritten with fixtures that isolate the `summary_done` dimension. Two new tests pin the default value and the docstring-argparse parity. Closeout comment on #2334 pastes validator stdout from a no-override production run (exit 0 required).

**Options not taken:** B (keep 0.55 + doc loudly) rejected — the friction of per-call override outweighs the aspirational signal, now captured in the docstring. C (two modes) rejected — T2-sized surface for a T1 problem.

---

## Pseudocode

T1 — trivial. See Files to Change.

---

## Files to Change

### 1. `scripts/data/document-index/validate-index-metadata.py`

| Line | Before | After |
|---|---|---|
| 19 | `    --summary-done-min           0.55   (reject if <55% records are summary_done=True)` | `    --summary-done-min           0.13   (reject if <13% records are summary_done=True; calibrated 2026-04-17 vs 16.13% observed. Original aspirational target 55% preserved as design history per #2334.)` |
| 35 | `    p.add_argument("--summary-done-min", type=float, default=0.55)` | `    p.add_argument("--summary-done-min", type=float, default=0.13)` |

### 2. `tests/data/document-index/test_validate_index_metadata.py`

Rewrite two existing tests and add two new tests.

| Test | Line | Fixture change | Assertion change |
|---|---|---|---|
| `test_validator_rejects_low_summary_done` (existing) | 85-92 | Was: `_mix(n_non_other=95, n_other=5, n_missing=0, n_summary_true=50, n_summary_false=0)`. Change to: `_mix_with_file_exists(n_non_other=95, n_other=5, n_summary_true=10, n_file_exists_true=80)`. Rationale: 10% summary_done < 13% default → fails the correct threshold; 80% file_exists > 70% default → passes the adjacent dimension cleanly. | Docstring `<55%` → `<13%`. Assertion unchanged (still `returncode == 1` with `"summary_done"` in output). |
| `test_validator_thresholds_overridable_via_cli` (existing) | 107-116 | Was: `_mix_with_file_exists(n_non_other=95, n_other=5, n_summary_true=50, n_file_exists_true=80)`. Change to: `_mix_with_file_exists(n_non_other=95, n_other=5, n_summary_true=10, n_file_exists_true=80)`. | Docstring `0.40` → `0.05`. Line 114 assertion unchanged (default fails: 10% < 13%). Line 116 override `"--summary-done-min", "0.40"` → `"--summary-done-min", "0.05"` → passes (10% > 5%). |

New tests (appended at bottom of file):

```python
# ═══════════════ #2334 default calibration tests ═══════════════

def test_default_summary_done_min_is_point_one_three(tmp_path):
    """Pin the post-#2334 calibration floor."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("validator_mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ns = mod._parse_args(["--index", str(tmp_path / "ignored.jsonl")])
    assert ns.summary_done_min == 0.13


def test_docstring_summary_done_min_matches_argparse_default():
    """Prevent docstring-argparse drift (pins both sides in lockstep)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("validator_mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Anchored substring match — exact whitespace alignment of the threshold table
    assert "--summary-done-min           0.13" in mod.__doc__, (
        "Docstring threshold value drifted from argparse default. "
        "Both scripts/data/document-index/validate-index-metadata.py:19 and :35 must be updated together."
    )
```

---

## TDD Test List

| # | Test | Fails before change | Passes after change |
|---|---|---|---|
| 1 | `test_default_summary_done_min_is_point_one_three` (new) | Yes — current default 0.55 | Yes |
| 2 | `test_docstring_summary_done_min_matches_argparse_default` (new) | Yes — current docstring says `0.55`, not `0.13`. Also fails during a one-sided edit (e.g., if someone changes only line 35 but forgets line 19). | Yes |
| 3 | `test_validator_rejects_low_summary_done` (rewritten fixture) | With 10% fixture: passes at 0.55 (10% < 55% → still exit 1). So this assertion would not detect the behavior change on its own. The rewrite is to keep the test semantically correct *after* the default change (ensuring 10% still fails under 0.13). | Yes (10% < 13% → exit 1). |
| 4 | `test_validator_thresholds_overridable_via_cli` (rewritten fixture + override) | The sequence fails today because the 0.40 override against 50% passes; after moving fixture to 10% and override to 0.05, the whole sequence exercises the new default floor. | Yes. |
| 5 | All 7 pre-existing tests | Pass today | Must still pass. |

**Note on test #2 robustness** (per Claude rev-2 F2): we use `mod.__doc__` not source-file regex. `__doc__` only contains the module-level docstring (not argparse help text), so the string `"--summary-done-min           0.13"` is only present if line 19 is updated. Line 35's default is read through `_parse_args`. Both must be updated for both assertions to pass.

---

## Acceptance Criteria

1. `_parse_args(["--index", ...]).summary_done_min` equals `0.13`.
2. Module docstring (line 19) threshold table contains the exact substring `"--summary-done-min           0.13"`.
3. Module docstring includes the calibration note referencing 2026-04-17 and the 55% aspirational historical target.
4. All 11 tests in `tests/data/document-index/test_validate_index_metadata.py` pass (7 untouched + 2 rewritten + 2 new).
5. **Closeout-comment gate (manual discipline):** before closing #2334, post a GH comment with the stdout of:
   `uv run python scripts/data/document-index/validate-index-metadata.py --index data/document-index/index.jsonl`
   (no override flags). Exit code must be `0`. Not mechanically enforced — T1 scope. If a future issue wires the validator into CI, upgrade the gate then.
6. Fresh adversarial review on rev-3 must return no new MAJOR findings.

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| 0.13 floor misses a real enrichment regression that halves the rate to ~8% | Low | 0.13 is 3pp below the current production rate. A drop below 0.13 means enrichment is genuinely broken (not a measurement-noise artifact). |
| Someone in the future re-tightens the default without updating the docstring (or vice versa) | Low | New test `test_docstring_summary_done_min_matches_argparse_default` pins them together mechanically. |
| Subcorpus mis-calibration — validator run against the conference batch (#2325) or shards/ corpus produces meaningless FAIL/PASS | Medium | Docstring now explicitly notes calibration corpus and date. Future callers on other corpora must pass explicit overrides. |
| Aspirational 55% target is forgotten because it lives only in docstring | Low | `#1878` and `#2308` issue bodies still carry the original 55%/60% language; they are not rewritten. Docstring note is recorded design history, not the only surviving reference. |
| Reviewer argues 0.13 is still wrong number | Medium | The absolute-margin argument is explicit (3pp below measurement, matches 1-sig-fig granularity). Any number in [0.12, 0.14] acceptable if review returns MAJOR. |

---

## Adversarial Review Summary

| Rev | Claude verdict | Codex verdict |
|---|---|---|
| rev-1 | MAJOR | MAJOR |
| rev-2 | MINOR | MAJOR (incl. sandbox-read process finding) |
| rev-3 | **APPROVE** | PROCESS FAILURE (sandbox `bwrap: Operation not permitted`) — no content review produced; `scripts/review/results/2026-04-17-plan-2334-codex.md` not written |

### Rev-3 Claude verdict summary

APPROVE with 3 non-blocking findings (1 MINOR residual-risk + 2 NITs):
- **F1 MINOR (non-blocking):** aspirational-55% note now lives only in docstring prose; the parity test pins `0.13` but not the `55%` reference. A future docstring rewrite could silently drop the design-history line. Residual risk low because #1878/#2308 issue bodies still carry the 55%/60% language independently.
- **F2 NIT:** Risks row 5 pre-concedes `[0.12, 0.14]` as interchangeable, which Claude says undercuts the one-sig-fig-granularity rationale. Accepted as deliberate flexibility signalling — the row is "what to do if review returns MAJOR", not the primary justification.
- **F3 NIT:** typo `"agains"` → `"against"` in Revision Note #1. **Fixed in rev-3.1.**

Claude verified all load-bearing rev-3 claims against live repo (#1878 plan AC = 55%, importlib test is runnable, fixture math produces 10% summary_done + 80% file_exists, whitespace-exact docstring match achievable, no orphan YAML consumers).

### Rev-3 Codex — process-failure finding, not content

Codex's rev-3 review failed due to sandbox environment issues (`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`) that prevented any file reads and the review-file write. Codex explicitly declined to fabricate verification and returned MAJOR on the process failure itself, not on plan content. Per the skill's provider-unavailability rule (Gemini 429 precedent), the process failure is documented here and the plan proceeds on the remaining review evidence. If the user wants a fresh Codex content review before approval, the next session can re-run once the sandbox is healthy.

### Rev-2 findings traceability (all addressed in rev-3)

| Finding | Addressed in rev-3 |
|---|---|
| Claude F1 / Codex F3 — "20% headroom precedent" is a retrofit | Revision Note #1; dropped precedent framing, replaced with absolute-margin argument. |
| Claude F2 — docstring-parity test underspecified | TDD Test #2 rewritten using `__doc__` + anchored whitespace-exact substring; Revision Note #4 + Files to Change §2 give the full test body. |
| Claude F3 — registry consumer contract for aspirational YAML field | Resolved by dropping the YAML field entirely (per Codex F4); no registry companion needed. |
| Claude F4 / F5 / F6 / F7 — NIT-class | Accepted (F5 reclassification noted in Revision Note #7); others are accepted noise. |
| Codex F2 — historical contract misstated (#1878 plan AC was 55%, not 60%) | Revision Note #2 + RIS documents table corrected with line-accurate cites. |
| Codex F4 — aspirational target in wrong YAML block | Revision Note #3 + Files to Change — YAML addition dropped; aspirational note moves to validator module docstring. |
| Codex F5 — fixture coupling in rewritten tests | Revision Note #5 + Files to Change §2 — both fixtures use `_mix_with_file_exists()` with `n_file_exists_true=80` to isolate dimension. |
| Codex F6 — closeout gate not mechanically enforceable | Revision Note #6 + AC #5 — documented as manual discipline gate; T1 scope; automation deferred. |

---

## References

- Issue: https://github.com/vamseeachanta/workspace-hub/issues/2334
- Parents: #1878 (closed), #2309 (closed)
- Prior-art plan: `docs/plans/2026-04-17-issue-2309-summary-fields-split.md`
- Handoff memo: `docs/handoffs/2026-04-17-issue-1878-family-complete-handoff.md`
