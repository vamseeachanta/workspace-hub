# Code Review — digitalmodel #617 (citation-resolver hardening)

Reviewer: Claude (code-stage, correctness + edge-case angle)
Commit: `fbe548ee` on `main`
Plan: `/mnt/local-analysis/digitalmodel/docs/plans/2026-05-20-issue-617-citation-resolver-hardening.md`
Tests at landing: 50 passed, 1 skipped

## Verdict

**MINOR**

The 6-level precedence chain is correct, edge cases I probed (empty-string env var, file-not-dir, trailing slash, both-env-vars-set deprecation suppression) all behave as expected, and the fail-closed message contains every substring the test asserts. Two actionable items below; none block merge but two should be closed out as follow-ons.

## Findings

### MAJOR

None. The correctness core is sound.

### MINOR

- **MINOR — `src/digitalmodel/citations/resolver.py:99-106` — "stale_clone" assertion vs error reason mismatch is masked by an over-broad test.** The error `reason` field in this branch is `llm_wiki_path_stale_clone:...`, but the test at `tests/citations/test_resolver.py:140` accepts `"stale_clone" in reason OR "llm_wiki_path_invalid" in reason OR "resolver_unconfigured" in reason`. The triple-OR is sloppy — any future regression that changes the reason prefix to something containing the substring "stale_clone" (or that accidentally falls through to `resolver_unconfigured`) silently passes. Tighten to `assert reason.startswith("llm_wiki_path_stale_clone:")` so a real defect surfaces. Why this matters: the test is supposed to be the regression-fence for this exact distinct-reason branch; weakening it removes the fence.

- **MINOR — `src/digitalmodel/citations/resolver.py:114-121` — TOCTOU race on `_RESOLUTION_CACHE["deprecation_warned"]` under concurrent first-resolution.** The check-then-set pattern is not atomic: two threads can both observe the key missing, both call `warnings.warn`, and both set the key. CPython's GIL makes the dict ops themselves safe but the `if` / `warnings.warn` / `__setitem__` sequence interleaves. No test asserts single-warn under concurrency. The window is tiny (microseconds during process bootstrap) and the failure mode is at-most-N warnings instead of one — strictly cosmetic. Cheapest fix: `_RESOLUTION_CACHE.setdefault("deprecation_warned", False)` plus a `threading.Lock`, or accept "best-effort one-shot" and document it. Why this matters: the test `test_resolver_one_shot_warning_cached` only exercises sequential calls; the contract is overstated in the docstring.

- **MINOR — `src/digitalmodel/citations/resolver.py:153` — log message says "all 5 resolution paths exhausted" but the precedence chain has 6 levels** (explicit override = 1; env, legacy, walk, known-clones, fail = 2-6). Off-by-one in operator-facing log. Either the comment is wrong or the count is. The explicit-override branch doesn't reach this code path, so "all 5 fallback paths" would be defensible, but the message as written is internally inconsistent with the chain documented at the top of the same file (resolver.py:3-9).

- **MINOR — `src/digitalmodel/orcaflex/mooring_design.py:38-91` — divergent `_default_repo_root` implementation duplicates resolver logic with different semantics.** The orcaflex module has its own 4-step chain (explicit → LLM_WIKI_PATH → DIGITALMODEL_REPO_ROOT → walk → return None) that does NOT consult `_KNOWN_LOCAL_CLONES` and does NOT emit a DeprecationWarning when DIGITALMODEL_REPO_ROOT is used. This is intentional per the docstring ("caller treats None as 'skip citation emission, warn once'") but it means an operator setting only the legacy env var sees the deprecation warning in some call paths and not in others depending on which entry point they hit. Either delegate to `resolve_wiki_base` with a `standalone_ok=True` shim, or document explicitly in `_default_repo_root`'s docstring that "legacy-env-var deprecation is intentionally suppressed in standalone-graceful mode". Why this matters: two implementations of the same precedence chain drift over time; the legacy var will outlive its sunset because half the code paths quietly accept it without warning.

- **MINOR — `src/digitalmodel/marine_ops/marine_engineering/environmental_loading/ocimf.py:22` — stale comment references `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` in canonical-prefix form.** Post-flip this prose should match the new `wikis/...` canonical form to avoid drift. No code impact; documentation hygiene.

### NIT

- **NIT — `src/digitalmodel/citations/resolver.py:171-189` — `resolve_wiki_path` returns the `standalone_join` path when neither layout hits.** The function comment says "caller (validate_citation) handles page_missing" but returns a path that's deliberately wrong for the overlay layout. This is fine because the caller does `is_file()` check, but a `# returns canonical-form path so error message shows what we tried` reminder for the next maintainer would help.

- **NIT — `src/digitalmodel/citations/resolver.py:75-79` — explicit `override` rejection raises `CitationResolutionError` with reason `override_invalid:` but the override case is the only branch where the caller passed the value explicitly; raising vs returning None loses information about what they intended.** Consider raising `ValueError` instead — the override was a programmer mistake, not a wiki-resolution failure. Low priority; behavior is correct, taxonomy is just slightly off.

- **NIT — drift residue in `src/digitalmodel/subsea/cross_sections/fixtures/*.yml`** (8 fixture files) still embed `url_or_path: knowledge/wikis/...` strings. These are display-only (consumed by `reporting.py` for human-readable Source rendering, NOT the citation resolver), so out of scope for #617 — but post-flip they should migrate to `wikis/...` form for consistency. File as separate follow-on, not a blocker.

## What looks solid

- **Precedence ordering is correct.** Explicit override beats env vars; LLM_WIKI_PATH beats legacy; legacy emits deprecation only when it actually resolved (verified: when both env vars set and LLM wins, NO deprecation fires — `Test 3` of my manual probe).
- **Fail-closed message contract honored.** Every substring the test asserts (`"LLM_WIKI_PATH"`, `"vamseeachanta/llm-wiki"`, `"codes-standards-data-routing"`, `"export LLM_WIKI_PATH="`) is present in the actual message I extracted. No spelling drift.
- **Empty-string env var (`LLM_WIKI_PATH=""`)** is correctly treated as unset (Python `if llm_wiki_env:` short-circuit). Falls through to legacy/walk/known-clones.
- **File-not-directory case (`LLM_WIKI_PATH=/tmp/somefile`)** correctly raises `llm_wiki_path_stale_clone` because `_validate_clone` checks `is_dir()` first.
- **Trailing-slash on env var** is correctly normalized by `pathlib.Path`.
- **Bounded parent walk** has a sentinel test that asserts wall-clock <0.5s under a 20-deep fake tree — guards against `feedback_path_parent_infinite_loop`.
- **DIGITALMODEL_REPO_ROOT invalid + LLM_WIKI_PATH unset** correctly falls through to parent-walk (resolver.py:127-132 logs warning and falls through — verified by reading code; no explicit test for this exact ordering but the behavior is unambiguous from the source).
- **Layout-detection** correctly tries standalone first then overlay (both `_join_with_layout_detection` and `resolve_wiki_path` use the same try-order). Back-compat tests (`test_resolution_passes_for_real_page`, `test_repo_root_invalid_env_var_raises`) still pass.
- **`knowledge/wikis` prefix-change ripple is contained.** No production Citation `wiki_path` literal still embeds the old prefix in `src/`. Hits are: (a) docstrings and error-message strings that legitimately mention BOTH layouts, (b) `subsea/cross_sections/fixtures/*.yml` display-only `url_or_path` values not consumed by the citation resolver, (c) `docs/` historical plan files (acceptable as historical artifacts).
- **Re-running the full pytest suite reproduces the landing result**: 50 passed, 1 skipped.

## Blockers for close-out

None. Merge can stand; suggest filing one follow-on for the test-tightening (Finding #1) and the divergent-resolver consolidation (Finding #4) since those are the items most likely to bite during the next change in this area.
