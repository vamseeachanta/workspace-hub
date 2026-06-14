# Disagreement report — plan #1579 (2026-06-14)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=0: Reading additional input from stdin... ) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: Warning: Basic terminal detected (TERM=dumb). Visual rendering will be limited. For the best experience, use a terminal emulator with truecolor support. Warning: 256-color support not detected. Using a terminal with at least 256-color support is recommended for a better visual experience. Ripgrep is not available. Falling back to GrepTool. Error when talking to Gemini API Full report available at:) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **The completeness-closeout "auto-derived class" rests on a `path_package_map` that does not exist in the repo.** Pseudocode line 287 ("use the implementation-time `path_package_map` from the current completeness caller") and Acceptance Criterion line 401 ("If the current path-package map derives `code`…") both treat the path-package map as a fixed, repo-provided input. It is not. The sole caller `completeness_gate_runner.py:32-85` only parses a stamped `completeness {json}` record and calls `evaluate_close`; it never constructs a map or invokes `classify()`/`score_evidence()`. Grep finds no `path_package_map` data file anywhere. Consequence: the implementer hand-constructs the `classify()` inputs, so the class is effectively *selectable*, and the plan's repeatedly-marketed "non-selectable, anti-dodge" property (lines 40, 288, 357, 401, 433) is illusory. The closeout is still *achievable* (agent computes `score_evidence`, stamps record, runner validates), but the plan specifies a mechanism that isn't wired up.
- **`registered-slug-mismatch` for `fdas`↔`frontierdeepwater` is unspecified and risks a fixture-only test (AC line 392, pseudocode line 263, test `test_registered_slug_mismatch_is_flagged` line 342).** The live remote is `vamseeachanta/llm-wiki-fdas`; the registry row is `frontierdeepwater` / `vamseeachanta/llm-wiki-frontierdeepwater`. There is no string-derivable link between "fdas" and "frontierdeepwater" (the acronym = "Frontier Deepwater" is domain knowledge per memory, not data in `config/client-wikis.yml`, which has no `fdas`/`aliases` entry). The plan never says *how* the code establishes "same client." The fixture hardcodes the pairing and asserts `registered-slug-mismatch`, but production code, lacking any mapping, will hit the `observed-unregistered` fallback (pseudocode line 262) — so the test passes on data production can't reproduce. Fix: add an explicit alias (e.g. an `aliases:`/`slug_aliases:` field on the `frontierdeepwater` row, or an `fdas` row) so the linkage is real data, OR downgrade the AC to "fdas → `observed-unregistered` + queued reconciliation" and stop asserting automatic slug-mismatch.
- **The required r4 review wave produced zero usable provider signal; the plan must not advance to `status:plan-review` claiming a clean r4.** Plan header line 10: "r4 is required after this revision before `status:plan-review`." The r4 artifacts (`scripts/review/results/2026-06-14-plan-1579-r4/`) are 0-byte for `claude.md` and `codex.md`, and `gemini.md` is `UNAVAILABLE (rc=1, Gemini API error)`. This inline review can stand as the Claude r4 signal, but Codex r4 and Gemini r4 are UNAVAILABLE — a T3→T2 (or worse) degradation that must be documented per the `scripts/review/results/` convention (SHARED_SOUL "Provider quota outages … document UNAVAILABLE") before the plan claims its review gate is satisfied.
- **(MINOR) Redundant pass guard.** Pseudocode line 291 / AC line 401 require `result.passed is true AND result.pct >= THRESHOLDS["evidence"]`. `CompletenessResult.passed` is defined as `pct >= threshold` (completeness_score.py:59-61) and the evidence threshold *is* `THRESHOLDS["evidence"]` (=80), so the second clause is tautological. Harmless, but trim it or the redundancy invites a future reader to think two independent checks exist.

### codex

(no findings unique to this provider)

### gemini

(no findings unique to this provider)
