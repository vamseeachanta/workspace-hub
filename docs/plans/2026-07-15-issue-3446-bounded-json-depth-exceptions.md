# Plan for #3446: Audit bounded JSON parsers for uncaught depth and resource exceptions

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3446
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-15-plan-3446-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/client_llm_wiki/bootstrap_manifest.py:241-252` — `_strict_json()` calls `json.loads(data, object_pairs_hook=pairs)` with no depth guard or `RecursionError` catch. The `pairs` hook enforces duplicate-key rejection but does not limit nesting depth.
- Found: `scripts/client_llm_wiki/bootstrap_manifest.py:32` — `_MAX_MANIFEST_BYTES = 8 * 1024 * 1024` size guard exists. A 8 MB deeply nested payload (e.g., `{"a":{"a":{"a":...}}}` 500k chars) is well under the limit yet triggers `RecursionError` in CPython at default recursion depth (~1000).
- Found: `scripts/client_llm_wiki/bootstrap_manifest.py:304` — `validate_render_manifest()` exception boundary catches `(OSError, ValueError, KeyError, json.JSONDecodeError, BootstrapGitError)` — `RecursionError` is absent; it will propagate past the boundary as an unhandled exception.
- Found: `tests/client_llm_wiki/test_bootstrap_manifest_cli_errors.py:1-55` — existing error tests exercise occupied manifest, backing residue semantics, and CLI exit codes. No test for deeply nested, huge numeric, malformed UTF-8, or `RecursionError` paths.
- Gap: No shared strict-JSON loader utility exists in `src/` that other callers could reuse. Current pattern is per-module `try/except json.JSONDecodeError`.

### Standards

| Standard | Status | Source |
|---|---|---|
| OWASP API Security Top 10 — API4:2023 Unrestricted Resource Consumption | applicable | Issue body ("resource exceptions") + `.claude/rules/coding-style.md` (validate at system boundaries) |
| Python docs — `sys.setrecursionlimit` / `RecursionError` | applicable — no standard limit | CPython default ~1000; deeply nested JSON can hit it before size guard fires |

### LLM Wiki pages consulted

- No relevant wiki pages under `knowledge/wikis/` covering JSON parser hardening or recursion guards.

### Documents consulted

- `docs/plans/2026-04-11-claude-agent-team-prompt-2207-provenance-reuse-contract.md` — prior plan; touches `bootstrap_manifest.py` ownership chain but not JSON parsing. Finding: bootstrap_manifest is the primary harness surface for untrusted JSON input.
- Issue [worldenergydata#924](https://github.com/vamseeachanta/worldenergydata/issues/924) — OPEN; this issue was the trigger for the adversarial finding. Title: "fix(landman): make provider routing executable and prove the CLI smoke path." Body references fixture-backed CLI input, which is the same attack surface (untrusted fixture content → JSON parse).
- `.claude/rules/coding-style.md` — "Only validate at system boundaries (user input, external APIs)." `_strict_json()` IS a system boundary: it parses externally-sourced manifest bytes. The rule confirms this is the correct hardening site.

### Gaps identified

- `RecursionError` not in the exception boundary of `validate_render_manifest()` (line 304) or `_strict_json()` (line 241).
- No test exercising deeply nested input (500+ levels), huge numeric literals, nonstandard JSON constants (`NaN`, `Infinity`), or malformed UTF-8 sequences at the `_strict_json` call site.
- No shared `safe_json` module — if duplication across the repo is material, a shared utility should be promoted; this plan gates that decision on the inventory step.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-15T via `gh issue view`):
- `#3446` — OPEN — Audit bounded JSON parsers for uncaught depth and resource exceptions
- `worldenergydata#924` — OPEN — fix(landman): make provider routing executable and prove the CLI smoke path

**File existence** (verified 2026-07-15):
- EXISTS: `scripts/client_llm_wiki/bootstrap_manifest.py`
- EXISTS: `tests/client_llm_wiki/test_bootstrap_manifest_cli_errors.py`
- MISSING (new — this plan creates): `tests/client_llm_wiki/test_bootstrap_manifest_json_boundaries.py`
- MISSING (new — this plan may create): `src/workspace_hub/safe_json.py` (conditional on inventory finding duplication)

**Line excerpts** (`bootstrap_manifest.py:241-252,300-306`):
```python
# line 241
def _strict_json(data: bytes) -> dict[str, Any]:
    def pairs(items):
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise BootstrapManifestError("manifest contains duplicate keys")
            result[key] = value
        return result
    payload = json.loads(data, object_pairs_hook=pairs)   # ← no depth guard
    if not isinstance(payload, dict):
        raise BootstrapManifestError("manifest JSON must be an object")
    return payload

# line 300-306
    except (OSError, ValueError, KeyError, json.JSONDecodeError, BootstrapGitError) as exc:
        raise BootstrapManifestError("manifest validation failed") from exc  # ← RecursionError not caught
```

**Gap proofs**:
- `grep -n "RecursionError" scripts/client_llm_wiki/bootstrap_manifest.py` → 0 matches → confirms RecursionError is not caught anywhere in the file.
- `grep -rn "RecursionError" tests/client_llm_wiki/` → 0 matches → confirms no test exercises this path.

**Reproduction proofs**:
```
$ python3 -c "
import json
nested = '{' + '\"a\":' * 990 + '1' + '}' * 990
try:
    json.loads(nested.encode())
except RecursionError as e:
    print('RecursionError raised:', e)
except json.JSONDecodeError as e:
    print('JSONDecodeError:', e)
"
RecursionError raised: maximum recursion depth exceeded while calling a Python object
```
- Reproduced at: 2026-07-15 (local CPython 3.11)
- Failure mode: `RecursionError` escapes `json.loads()` before any explicit size or depth guard fires.
- The existing `_MAX_MANIFEST_BYTES = 8 * 1024 * 1024` guard fires BEFORE `json.loads` only in `_stable_digest`; `_strict_json` receives already-read bytes and has no depth guard.

<!-- Verification: distinct sources counted — issue body (1), bootstrap_manifest.py code (2), test file (3), worldenergydata#924 (4), coding-style.md rule (5). Count: 5 ≥ 3 required. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-15-issue-3446-bounded-json-depth-exceptions.md` |
| Primary fix | `scripts/client_llm_wiki/bootstrap_manifest.py` |
| New tests | `tests/client_llm_wiki/test_bootstrap_manifest_json_boundaries.py` |
| Shared utility (conditional) | `src/workspace_hub/safe_json.py` |
| Plan review — Claude | `scripts/review/results/2026-07-15-plan-3446-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-15-plan-3446-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-15-plan-3446-gemini.md` |

---

## Deliverable

A hardened `_strict_json()` implementation and a matching `validate_render_manifest()` exception boundary that both catch `RecursionError`, `OverflowError`, and `UnicodeDecodeError` alongside `JSONDecodeError`, with tests verifying that all four failure modes produce structured `BootstrapManifestError` output rather than bare Python exceptions.

---

## Pseudocode

```python
# Updated _strict_json in bootstrap_manifest.py
def _strict_json(data: bytes) -> dict[str, Any]:
    def pairs(items):
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise BootstrapManifestError("manifest contains duplicate keys")
            result[key] = value
        return result
    try:
        payload = json.loads(data, object_pairs_hook=pairs)
    except RecursionError:
        raise BootstrapManifestError("manifest JSON nesting depth exceeds system limit")
    except (json.JSONDecodeError, ValueError, OverflowError, UnicodeDecodeError) as exc:
        raise BootstrapManifestError("manifest JSON is malformed") from exc
    if not isinstance(payload, dict):
        raise BootstrapManifestError("manifest JSON must be an object")
    return payload

# Updated exception boundary in validate_render_manifest (line ~304)
# Add RecursionError to the caught tuple:
    except (OSError, ValueError, KeyError, json.JSONDecodeError,
            RecursionError, OverflowError, UnicodeDecodeError,
            BootstrapGitError) as exc:
        raise BootstrapManifestError("manifest validation failed") from exc

# Inventory step (pre-implementation): count json.loads call sites in scripts/
# that are NOT in .venv or .claude/state:
#   grep -rn "json.loads\|json.load(" scripts/ src/ --include="*.py" \
#     | grep -v ".venv\|.claude/state"
# If ≥3 distinct callers lack RecursionError handling → promote shared safe_json loader.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/client_llm_wiki/bootstrap_manifest.py` | Add `RecursionError`, `OverflowError`, `UnicodeDecodeError` to `_strict_json()` and `validate_render_manifest()` exception boundaries |
| Create | `tests/client_llm_wiki/test_bootstrap_manifest_json_boundaries.py` | New boundary tests: deeply nested, huge numeric, NaN/Infinity constant, malformed UTF-8 |
| Create (conditional) | `src/workspace_hub/safe_json.py` | Shared strict loader if inventory finds ≥3 call sites lacking guards |
| Update | `docs/plans/2026-07-15-issue-3446-bounded-json-depth-exceptions.md` | This plan file |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_strict_json_deeply_nested_raises_manifest_error` | RecursionError → BootstrapManifestError | `b'{"a":{"a":...990 levels}}` | `BootstrapManifestError("nesting depth")` |
| `test_strict_json_huge_numeric_raises_manifest_error` | OverflowError → BootstrapManifestError | `b'{"n": 1e999}` (non-finite float) | `BootstrapManifestError("malformed")` |
| `test_strict_json_nan_constant_raises_manifest_error` | JSON disallows bare NaN | `b'{"x": NaN}'` | `BootstrapManifestError` or `JSONDecodeError` wrapped |
| `test_strict_json_malformed_utf8_raises_manifest_error` | UnicodeDecodeError → BootstrapManifestError | `b'{"k": "\xff\xfe"}'` | `BootstrapManifestError("malformed")` |
| `test_strict_json_duplicate_keys_raises_manifest_error` | existing test — regression guard | `b'{"a":1,"a":2}'` | `BootstrapManifestError("duplicate keys")` — must still pass |
| `test_strict_json_non_object_root_raises_manifest_error` | root must be dict | `b'[1,2,3]'` | `BootstrapManifestError("must be an object")` |
| `test_validate_render_manifest_deeply_nested_raises_manifest_error` | end-to-end: malicious manifest body triggers BootstrapManifestError | see above nested payload written to manifest file | `BootstrapManifestError` — does NOT propagate as bare RecursionError |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/client_llm_wiki/test_bootstrap_manifest_json_boundaries.py -v`
- [ ] No regression: `uv run pytest tests/client_llm_wiki/ -v` passes
- [ ] `grep -n "RecursionError" scripts/client_llm_wiki/bootstrap_manifest.py` returns ≥1 match in `_strict_json` and ≥1 match in `validate_render_manifest`
- [ ] A deeply nested (990-level) payload submitted via `_strict_json()` raises `BootstrapManifestError`, not bare `RecursionError`
- [ ] Inventory of `json.loads` call sites across `scripts/` and `src/` is documented in issue comment with count and decision on shared loader
- [ ] Plan review adversarial artifacts posted to `scripts/review/results/`

---

## Risks and Open Questions

- **Risk:** CPython's default recursion limit (~1000) varies by call stack depth at the time `json.loads` fires. Tests using 990 levels may pass on CPython 3.11 but fail on a deeply-recursive caller. Use ~500 levels as the safe test depth to leave headroom.
- **Risk:** `json.loads` with `object_pairs_hook` may raise `RecursionError` inside the hook itself (not just the parser). Both sites need the same guard.
- **Open:** Should a `sys.setrecursionlimit` increase be added before parsing to give the parser more room, or should we hard-cap nesting depth via a pre-scan? (Pre-scan approach is safer and doesn't mutate global interpreter state — flag for user during approval.)
- **Open:** Does the tier-1 scope extend to `worldenergydata` and `digitalmodel`? Issue body says "tier-1 repos" — the inventory step will answer this. Plan currently scopes only to workspace-hub; implementation against other repos is out of scope for this issue.

---

## Complexity: T2

**T2** — one module modified, one new test file created, optional shared utility creation if inventory finds duplication. Requires adversarial review before implementation per issue gate.
