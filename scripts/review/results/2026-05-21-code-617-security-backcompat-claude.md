# Code-Stage Adversarial Review — digitalmodel#617 — Security + Back-Compat + Test Discipline

**Reviewer:** Claude (adversarial, code-stage)
**Commit:** `fbe548eeeda7870d59850a35b85e0ffa1da095b4` on digitalmodel main
**Scope:** security hygiene, back-compat surface, test discipline (companion review covers correctness)
**Date:** 2026-05-21

---

## VERDICT: MAJOR

Blockers below force replan or follow-on issues before this can be considered shipped-clean. The implementation passes happy-path tests but ships a duplicated resolver (`mooring_design._default_repo_root`) that diverges from the new canonical resolver in security-relevant ways, the path-traversal hygiene is not extended end-to-end, and one test asserts a fail-closed branch with a disjunction that masks regressions.

---

## FINDINGS

### [MAJOR] mooring_design.py:38-91 — Duplicated resolver bypasses the new canonical resolver entirely

`_default_repo_root()` is a parallel implementation of the same 6-level chain that lives in `resolver.py`. It is the one actually invoked by every `check_mbl_with_safety_factor`, `get_intact_safety_factor`, `get_damaged_safety_factor` call path (via `_resolve_sf_for_condition` line 420 → `_default_repo_root(repo_root_override)`).

Consequences:

1. **Back-compat contract violated.** The plan says `DIGITALMODEL_REPO_ROOT` stays with a `DeprecationWarning`. The canonical resolver does emit it (resolver.py:115-121). **`_default_repo_root` does not — it accepts the legacy env var silently** (mooring_design.py:72-84). Any caller routed through `MooringLineDesign` never sees the deprecation signal. Acceptance criterion "one-shot deprecation warning per session" is not met for the actual user-facing API.
2. **Resolver level 5 (known-local-clone fallback) is missing entirely** from the mooring_design copy — workflows that rely on `/mnt/local-analysis/llm-wiki` or `~/workspace-hub/llm-wiki` will fail-closed via mooring_design even though the canonical resolver would succeed.
3. **Two resolution chains will drift.** Any future hardening (e.g., symlink-resolve, allow-list, audit log) added to `resolver.py` will silently not apply to the mooring path. This is exactly the duplication class that #2722 promote-to-rule was meant to prevent.

**Why MAJOR:** the duplication is a back-compat correctness defect, not a style nit. Either `_default_repo_root` should delegate to `resolve_wiki_base` (passing the override through, catching `CitationResolutionError` and returning `None` for the standalone graceful path), or it must be deleted in favor of direct resolver use with a `standalone_mode=True` flag added to the resolver.

### [MAJOR] resolver.py:135 + 181-189 — `Path(__file__).resolve()` walks symlinks, but env-var path is NOT resolved

`resolve_wiki_base` calls `Path(__file__).resolve()` on the parent-walk path (line 135), but for explicit-override (line 71) and `LLM_WIKI_PATH` (line 84), `Path(override)` / `Path(llm_wiki_env)` are used **without `.resolve()`**. Combined with `resolve_wiki_path` joining (line 181, 185), this means:

- `LLM_WIKI_PATH=/some/symlink-to-attacker-dir` is honored as-is. `_validate_clone` checks `(base/"wikis").is_dir()` which **follows symlinks by default** (no `follow_symlinks=False`). An attacker who controls a writable directory adjacent to a legitimate clone can substitute a `wikis/` symlink at validation time and a different target by resolution time — TOCTOU on the file lookup.
- More concretely: a malicious or careless `LLM_WIKI_PATH` containing a `wikis/` symlink pointing into `/etc` or another user's home would pass `_validate_clone` and then `resolve_wiki_path` would read frontmatter from whatever the symlink targets at read time.

The defense is straightforward: call `.resolve(strict=True)` on `env_path` and the override at acceptance time, then verify the resolved path is a directory (not a file), and reject if the resolved path differs from the input AND the input was not under user-trusted prefix. At minimum, **document that LLM_WIKI_PATH is treated as a trusted input and the operator is responsible for not pointing it at adversary-controlled directories** — the current code does neither.

Note: companion correctness reviewer should also flag this as a layout-detection bug — `resolve_wiki_path` may return a non-existent `standalone_join` as the canonical "where it should be" path (line 189) even though the file was actually under the overlay. Callers downstream (`validate_citation` line 138) will then report `page_missing` against the wrong path.

### [MAJOR] test_resolver.py:127, 140 — Fail-closed assertions use OR-disjunctions that mask regressions

Two tests:

```
assert "llm_wiki_path_invalid" in exc.value.reason or "resolver_unconfigured" in exc.value.reason
assert "stale_clone" in reason or "llm_wiki_path_invalid" in reason or "resolver_unconfigured" in reason
```

These pass if **any** of the disjuncts appears. The resolver's intent is:
- nonexistent path → `llm_wiki_path_invalid` (specifically)
- path exists but no `wikis/` → `llm_wiki_path_stale_clone`

If someone refactors the resolver to always raise `resolver_unconfigured` regardless of the branch (e.g., by collapsing levels 2-5 into a single "no clone found" message), these tests still pass while losing the operator-facing diagnostic specificity that was the whole point of #617. The assertions should be **exact-match** on the reason prefix for the branch each test exercises.

### [MINOR] resolver.py:114-121 — One-shot warning cache uses module-global mutable dict — test isolation hazard

`_RESOLUTION_CACHE` is a module-level dict. Tests `_clean_cache` autouse fixture (test_resolver.py:68) clears it pre-and-post each test, but:

1. **Other test files** (test_registry.py, test_mooring_design_citations.py) do NOT clear it. If they run before test_resolver in pytest collection order, the cache may already contain `deprecation_warned=True`, suppressing the warning the deprecation-test wants to assert.
2. **Parallel pytest** (e.g., pytest-xdist) shares process state per worker — the cache will desync across workers. This is fine today (tests don't run xdist) but becomes a silent flaky-test factory when someone enables it.

Fix: scope the cache to a `threading.local()` OR document the autouse-clear requirement and add it to a shared conftest.

### [MINOR] resolver.py:73, 96, 122-125, 139, 147 — INFO logs leak full filesystem paths

Every successful resolution emits an INFO log including the resolved path. In environments that ship application logs to centralized aggregators (Datadog, Splunk, ELK), this exposes:

- The username component of `~/workspace-hub/llm-wiki` (`/home/<user>/workspace-hub/...`)
- The mount layout (`/mnt/local-analysis/...`)
- The CI runner working directory shape

For a defense-in-depth library used in engineering calc paths, **DEBUG would be a more defensible default** for the success branch; reserve INFO for the legacy-env-var resolution (operationally important) and ERROR for failures.

Not a blocker — the data is not credential-grade — but worth flagging. The resolver also has no log redaction for the `LLM_WIKI_PATH` env-var value, which a careful operator might legitimately set to a path under `/secrets/wiki-snapshot/`.

### [MINOR] resolver.py:127-132 — DIGITALMODEL_REPO_ROOT-set-but-invalid falls through silently with only a WARNING

When the legacy env var is set but invalid (line 127-132), the code emits a `_LOGGER.warning(...)` and falls through to parent-walk + known-local-clones. This is friendly behavior but it differs from `LLM_WIKI_PATH`-set-but-invalid which raises immediately (line 87-93, 99-106). Asymmetric behavior between the primary and legacy env vars is a footgun: an operator who set `DIGITALMODEL_REPO_ROOT=/bad/path` to test fail-closed will instead get success via parent-walk and never know the env var was ignored.

Recommend: legacy-invalid should raise the same way primary-invalid does, OR the asymmetry should be documented in the actionable error message ("Note: DIGITALMODEL_REPO_ROOT is also accepted as a legacy alias; set-but-invalid is treated as unset").

### [MINOR] test_resolver.py:271-279 — `test_resolver_info_log_on_success` doesn't catch the DEBUG-vs-INFO regression

The test asserts an INFO log fires on success and that the resolved-path string appears in it. If someone fixes the over-logging finding above by downgrading success to DEBUG, this test fails — fine, but the test fails for the wrong reason (assertion against INFO records). A more durable test would assert the **count and level distribution** so the intent ("at-least-one record at intended level") is decoupled from level choice.

### [MINOR] test_mooring_design_citations.py:139-160 — Sentinel test uses `@patch.object(md, "__file__", ...)` but reads from `_default_repo_root` which calls `Path(__file__).resolve()` at runtime

The test patches `md.__file__` to a deep fake path and asserts the bounded walk terminates. But mooring_design.py:86 reads `Path(__file__).resolve()` — `__file__` is a module-global string that the patch does modify, so this works. However, the **canonical resolver `resolve_wiki_base` is NOT exercised in this sentinel test at all** — only the duplicated `_default_repo_root` is. The corresponding `test_resolver_parent_walk_has_sentinel` (test_resolver.py:189-207) covers the canonical resolver. Net effect: both paths have sentinel coverage, but if the duplicated resolver is deleted (per MAJOR finding above) this test silently becomes dead code, not failing — meaning the lookup-by-test for "is the canonical resolver sentinel-safe" is split across two files.

### [MINOR] No test exercises `validate_citation(repo_root=Path(...))` against the new `_join_with_layout_detection`

`validate_citation` now branches on `repo_root is None` (schema.py:132). The `repo_root is not None` branch calls `_join_with_layout_detection` (schema.py:137). test_schema.py:75-94 covers this branch with overlay-shape fixtures, but **no test covers the standalone-shape (`base/wikis/...`) repo_root-explicit path**. A caller migrating an old harness that explicitly passed `repo_root=Path("/some/standalone-clone")` will hit the un-tested branch. Add at least one `test_resolution_passes_for_standalone_layout_with_explicit_repo_root`.

### [INFO] Schema-change ripple grep is clean

`grep wiki_path` across src/ + tests/ found only the migrated callers and the unrelated `url_or_path` field in `subsea/cross_sections/test_validation.py:21` (different type, unaffected). No downstream string-manipulation on `wiki_path` assumes a `knowledge/` prefix. Schema change is well-contained.

### [INFO] `_validate_wiki_path` traversal hygiene is intact for *new* Citation objects

schema.py:64-76 still rejects `..`, absolute paths, and backslashes at Citation construction time. The new resolver code does NOT introduce a path-traversal regression through `Citation.wiki_path` — only through the LLM_WIKI_PATH env var, which is covered in the MAJOR finding above. Tests at test_schema.py:60-72 still pass.

---

## SUMMARY

Citation-resolver hardening passes happy-path tests and meets the visible #617 acceptance criteria, but ships with three structural problems: (1) a duplicated resolver in `mooring_design.py` that silently bypasses the deprecation warning and known-local-clone fallback, breaking the documented back-compat contract for the actual user-facing API; (2) symlink/TOCTOU hygiene gap on the LLM_WIKI_PATH env-var path that the canonical resolver does not address even though it `.resolve()`s the parent-walk start; (3) two fail-closed tests using OR-disjunctions that mask diagnostic regressions. Minor findings cover INFO-log path leakage, asymmetric legacy-env-var failure handling, and missing test coverage for the standalone-layout explicit-`repo_root` branch. Recommend MAJOR — file follow-on issues for (1) resolver consolidation + (2) env-var path hardening; tighten (3) inline before next release.
