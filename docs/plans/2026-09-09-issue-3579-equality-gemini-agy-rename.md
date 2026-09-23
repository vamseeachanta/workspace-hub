# Plan for #3579: chore(readiness): rename equality/parity provider row gemini→agy (cross-machine snapshot schema migration)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-09-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3579
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-09-plan-3579-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/readiness/collect-equality.sh:446` — writes `providers: {claude: ..., codex: ..., gemini: $(prov gemini), hermes: ...}` where `prov()` checks CLI presence via `have "$1"` (line 148). Key `gemini` is the snapshot row name; `$(prov gemini)` checks the `gemini` binary, which agy replaced as the third provider per #3573.
- Found: `scripts/readiness/collect-equality.sh:473-475` — writes `gemini_present`, `gemini_unexpected`, `gemini_expected` to the `skill_currency` section of every snapshot.
- Found: `scripts/readiness/build-equality-matrix.py:51` — `PROVIDERS = ("claude", "codex", "hermes", "gemini")` controls matrix row labels and harness-capability row generation.
- Found: `scripts/readiness/build-equality-matrix.py:55` — `EXPECTED_DIVERGENCE_REASONS = {"external_skill_dirs_configured", "gemini_skill_dispatch_unsupported"}` — divergence reason string embeds the old provider key.
- Found: `scripts/readiness/build-equality-matrix.py:280-297` — reads `gemini_present`, `gemini_unexpected`, `gemini_expected` from snapshots for the `skill_currency` verdict.
- Found: `scripts/readiness/provider_harness_parity.py:17` — `PROVIDERS = ("claude", "codex", "hermes", "gemini")` — duplicate tuple that must stay in sync with `build-equality-matrix.py` per inline comment (`#3206/#3209`).
- Found: `scripts/readiness/provider_harness_parity.py:22-25` — comment acknowledges "The 'gemini' row = the Gemini surface (agy since #3573)" with `gemini_skill_dispatch_unsupported` reason. The rename was deferred at migration time.
- Found: `scripts/readiness/provider_harness_parity.py:93-148` — `_gemini_memory_runtime()` checks `config/agents/gemini/MEMORY.runtime.md`. This is a **filesystem path that does not change** — the config directory keeps the `gemini` name; only the YAML key and matrix row label rename.
- Gap: No `agy_*` key support in `build-equality-matrix.py` — the matrix reads `gemini_*` keys from snapshots; a machine running new `agy`-keyed collector output produces a silent `absent` verdict for the gemini row.
- Gap: `collect-equality.sh:446` calls `$(prov gemini)` — on machines where only the `agy` CLI is installed (not `gemini`), this reports `absent` in the harness providers block.

### Standards
Not applicable — infrastructure schema migration.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- Issue #3579 body — describes the required migration phases: dual-read window → roll collectors fleet-wide → flip writers to `agy` keys → drop `gemini` keys after all hosts re-snapshot. Explicitly defers to after the #3573 soak period.
- Issue #3573 (OPEN) — "feat(ai-orchestration): replace gemini with agy as the third worker/reviewer provider ecosystem-wide" — parent EPIC; confirms migration is live at the provider level but equality schema is a known tail.
- `docs/plans/2026-07-09-issue-3408-harness-checkup-equality-dimension.md` — prior plan for equality dimension additions; established the schema conventions and PROVIDERS-tuple sync requirement between `build-equality-matrix.py` and `provider_harness_parity.py`.
- `docs/plans/2026-07-22-issue-3592-equality-dimension-reclassification.md` — prior equality plan; established the acceptance pattern for matrix dimension changes (publish-equality.sh verification + before/after screenshot).

### Gaps identified
- No `agy_*`-key reading path in `build-equality-matrix.py` — skill_currency verdict is silently wrong on agy-keyed snapshots.
- `collect-equality.sh` still checks `$(prov gemini)` — reports `absent` on machines where only `agy` CLI is present.
- No test covers dual-read backward compatibility (both key families in the same snapshot set).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-09-09T~09:00Z):
- `#3579` — OPEN — chore(readiness): rename equality/parity provider row gemini→agy (cross-machine snapshot schema migration)
- `#3573` — OPEN — feat(ai-orchestration): replace gemini with agy as the third worker/reviewer provider ecosystem-wide

**File existence** (`ls -la` 2026-09-09):
- EXISTS: `scripts/readiness/collect-equality.sh` (30,988 bytes)
- EXISTS: `scripts/readiness/build-equality-matrix.py` (52,338 bytes)
- EXISTS: `scripts/readiness/provider_harness_parity.py` (11,901 bytes)

**Line excerpts** (`sed -n` from main at 90596e79b):
```
# collect-equality.sh:446
    providers: {claude: $(prov claude), codex: $(prov codex), gemini: $(prov gemini), hermes: $(prov hermes)}

# collect-equality.sh:473-475
    gemini_present: ${skc_gp}
    gemini_unexpected: ${skc_gu}
    gemini_expected: ${skc_ge}

# build-equality-matrix.py:51,55
PROVIDERS = ("claude", "codex", "hermes", "gemini")
EXPECTED_DIVERGENCE_REASONS = {"external_skill_dirs_configured", "gemini_skill_dispatch_unsupported"}

# provider_harness_parity.py:17
PROVIDERS = ("claude", "codex", "hermes", "gemini")
```

**Gap proofs**:
- `grep -c "agy_present\|agy_unexpected\|agy_expected" scripts/readiness/build-equality-matrix.py` → **0** → no dual-read support
- `grep -c "agy_present\|agy_unexpected\|agy_expected" scripts/readiness/collect-equality.sh` → **0** → writer still uses gemini keys

**Reproduction proofs**: N/A — this is a silent-incorrect-output defect (matrix reads 0/absent for `gemini_*` fields on machines producing `agy_*` keys; no crash). Mark intentional skip.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-09-09-issue-3579-equality-gemini-agy-rename.md` |
| Tests | `tests/readiness/test_equality_schema_migration.py` |
| Phase 1: dual-read reader | `scripts/readiness/build-equality-matrix.py` |
| Phase 2: writer update | `scripts/readiness/collect-equality.sh` |
| Phase 3: harness parity | `scripts/readiness/provider_harness_parity.py` |
| Plan review — Claude | `scripts/review/results/2026-09-09-plan-3579-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-09-09-plan-3579-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-09-09-plan-3579-agy.md` |

---

## Deliverable

All equality snapshot consumers (`build-equality-matrix.py`, `provider_harness_parity.py`) accept both `gemini_*` and `agy_*` keys; `collect-equality.sh` writes `agy` keys by default; the published equality matrix shows "agy" in the provider row with no regression on machines whose snapshots still carry old `gemini_*` keys.

---

## Pseudocode

```
# Phase 1 — Dual-read in build-equality-matrix.py (skill_currency verdict)
def _read_skc_field(snapshot, field):
    # Accept both agy_* (new) and gemini_* (old); agy takes precedence if present
    return snapshot.get(f"agy_{field}", snapshot.get(f"gemini_{field}", 0))

# Also update the two Python-level constants:
# build-equality-matrix.py:51
PROVIDERS = ("claude", "codex", "hermes", "agy")   # was "gemini"
# build-equality-matrix.py:55
EXPECTED_DIVERGENCE_REASONS = {
    "external_skill_dirs_configured",
    "agy_skill_dispatch_unsupported",  # was "gemini_skill_dispatch_unsupported"
}

# Phase 2 — Writer in collect-equality.sh
# Change harness providers block (line 446):
#   OLD: providers: {gemini: $(prov gemini)}
#   NEW: providers: {agy: $(prov agy)}
# Change skill_currency block (lines 473-475):
#   OLD: gemini_present / gemini_unexpected / gemini_expected
#   NEW: agy_present    / agy_unexpected    / agy_expected
# Note: $(prov agy) checks for the `agy` CLI binary (not `gemini`)

# Phase 3 — provider_harness_parity.py
# Update PROVIDERS tuple (line 17): "gemini" → "agy"
# Update EXPECTED_DIVERGENCE_REASONS string: "gemini_skill_dispatch_unsupported"
#   → "agy_skill_dispatch_unsupported"
# Update all `if provider == "gemini":` branches → `if provider == "agy":`
# Rename _gemini_memory_runtime() → _agy_memory_runtime()
# IMPORTANT: filesystem path config/agents/gemini/ does NOT change —
#   _agy_memory_runtime() still resolves to config/agents/gemini/MEMORY.runtime.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/build-equality-matrix.py` | Dual-read `agy_*`/`gemini_*` skill_currency keys; rename PROVIDERS "gemini"→"agy"; rename EXPECTED_DIVERGENCE_REASONS string |
| Modify | `scripts/readiness/collect-equality.sh` | Write `agy:` in harness providers block; write `agy_present/unexpected/expected` in skill_currency; update `$(prov gemini)` → `$(prov agy)` |
| Modify | `scripts/readiness/provider_harness_parity.py` | Rename PROVIDERS; rename all `if provider == "gemini"` branches to `if provider == "agy"`; rename helper function; update EXPECTED_DIVERGENCE_REASONS |
| Create | `tests/readiness/test_equality_schema_migration.py` | TDD tests for dual-read and new-key correctness |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_dual_read_agy_keys_preferred` | `agy_*` keys take precedence when both key families present | snapshot dict with `agy_present=True` and `gemini_present=False` | skill_currency reads `agy_present=True` |
| `test_dual_read_old_gemini_keys_fallback` | `gemini_*` keys used as fallback when no `agy_*` keys (old snapshot) | snapshot dict with `gemini_present=True`, no `agy_*` keys | skill_currency reads `gemini_present=True` (non-zero) |
| `test_providers_tuple_contains_agy` | PROVIDERS constant in both py files contains "agy" not "gemini" | import both modules | `"agy" in PROVIDERS`; `"gemini" not in PROVIDERS` |
| `test_expected_divergence_reason_renamed` | EXPECTED_DIVERGENCE_REASONS uses `agy_` prefix | import both modules | `"agy_skill_dispatch_unsupported" in reasons`; `"gemini_skill_dispatch_unsupported" not in reasons` |
| `test_skill_currency_verdict_agy_snapshot` | Full verdict pipeline correct on new-format snapshot | snapshot with `agy_present=True`, `agy_unexpected=0`, `agy_expected=0` | SKILLS-CURRENT verdict |
| `test_skill_currency_verdict_old_snapshot` | Full verdict pipeline correct on old-format snapshot (backward compat) | snapshot with `gemini_present=True`, `gemini_unexpected=0`, `gemini_expected=0` | SKILLS-CURRENT verdict (via fallback read) |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/readiness/test_equality_schema_migration.py -v`
- [ ] No regression: existing test suite passes
- [ ] `collect-equality.sh` produces `agy: present/absent` in the harness providers block on a machine with the `agy` CLI installed
- [ ] `build-equality-matrix.py` reads `agy_*` fields and produces the correct skill_currency verdict on a new-format snapshot
- [ ] `build-equality-matrix.py` reads `gemini_*` fields and produces the correct skill_currency verdict on an old-format snapshot (fallback)
- [ ] `provider_harness_parity.py` PROVIDERS tuple contains "agy", not "gemini"
- [ ] The published equality matrix shows "agy" not "gemini" in the provider row display label
- [ ] `scripts/readiness/publish-equality.sh` runs without error after the changes (`./publish-equality.sh --dry-run` or equivalent)
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- Filled in after adversarial review completes. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Agy | PENDING | — |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk — filesystem path unchanged:** `config/agents/gemini/` path is NOT renamed. `_agy_memory_runtime()` (renamed from `_gemini_memory_runtime()`) still resolves to `config/agents/gemini/MEMORY.runtime.md`. If the config directory is later renamed to `config/agents/agy/`, a follow-on issue must update the helper. Declare this explicitly at implementation time.
- **Risk — fleet re-snapshot timing:** Machines running old `collect-equality.sh` produce `gemini_*` keys; machines running the new version produce `agy_*` keys. The dual-read window in `build-equality-matrix.py` must remain active until ALL machines (ace-linux-1, ace-linux-2, gpu-claw) have re-snapshotted with new keys. Do NOT drop `gemini_*` fallback until fleet sweep confirms all snapshots use `agy_*` keys.
- **Open — `prov agy` vs `prov gemini`:** The transition PR should check whether the `agy` CLI binary name is actually `agy` or an alias. On ace-linux-1, verify with `which agy` before committing the `$(prov agy)` change.
- **Open — sync requirement:** The inline comment in `build-equality-matrix.py:53` says PROVIDERS must stay in sync with `provider_harness_parity.py`. Both files must be updated in the same commit to avoid a window where they disagree.

---

## Complexity: T2

**T2** — three implementation files modified, one new test module created, fleet rollout timing coordination required, dual-read backward-compat window. Single repo (workspace-hub/scripts/readiness/).
