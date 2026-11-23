# Plan for #3206: provider-harness parity — assert the Gemini memory surface

> **Status:** adversarial-reviewed (r1 Claude MAJOR → revised; expanded scope)
> **Complexity:** T2
> **Date:** 2026-06-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3206
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-18-plan-3206-claude.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/provider_harness_parity.py` — `PROVIDERS = ("claude","codex","hermes")` (line 17); gemini absent. `_memory_read` (l.97) special-cases claude/codex/hermes; `_workflow_gates` (l.155) checks repo artifacts for claude but `_local_runtime_path` for non-claude (returns None for gemini → would false-flag `active_runtime_missing`); `_skills_invoke` (l.121) has no gemini branch. `_installed` (l.89) = `_command_exists(provider) or _local_runtime_exists`; `_local_runtime_path` returns None for gemini (l.76-81) so gemini install = command only.
- Found: `EXPECTED_DIVERGENCE_REASONS` (l.20) — the mechanism for "legitimately different, not a failure" (currently `external_skill_dirs_configured` for hermes).
- Found: gemini repo surface (the things to verify):
  - `config/agents/gemini/MEMORY.runtime.md` — 7KB, exists (the #3189 consolidated memory).
  - `GEMINI.md:4` — carries "Session start: read `config/agents/gemini/MEMORY.runtime.md` …" (the read instruction).
  - `config/agents/gemini/SOUL.runtime.md` — 18KB, contains all 3 `GATE_PHRASES` (verified `grep -c` = 3) → gemini gates ARE verifiable against a repo artifact.
- Found: `tests/readiness/test_provider_harness_parity.py:63` — `test_provider_harness_constants_use_exact_issue_capability_names` asserts `PROVIDERS == ("claude","codex","hermes")` → **will break**, must update. `test_repo_runtime_files_do_not_make_provider_installed` (l.109) pins the invariant: repo runtime files must NOT flip `installed` → gemini must follow it.

### Documents consulted
- Issue #3206 body — acceptance + the "scope carefully (gemini has no local AGENTS.md runtime)" warning.
- #3189 (memory bridge) — created the gemini memory surface this verifies.
- Memory `harness-provider-neutrality-state` — gemini integration is the repo `config/agents/gemini/` surface (no local CLI runtime); agy = Antigravity/Gemini CLI; per #3190 agy is router-first-class but **unsupported for dispatch** (no headless) → no local skill dispatch surface.

### Gaps identified
- No gemini branch in `_memory_read`/`_workflow_gates`/`_skills_invoke`; gemini not in `PROVIDERS`.
- `_workflow_gates` non-claude path requires `_local_runtime_path` → would false-flag gemini.

### Downstream ripple — discovered in r1 review (was under-scoped in draft)
- **`scripts/readiness/build-equality-matrix.py` duplicates the contract:** its own `PROVIDERS = (claude,codex,hermes)` (l.50) AND its own `EXPECTED_DIVERGENCE_REASONS = {external_skill_dirs_configured}` (l.52). To render gemini end-to-end AND have `skills:invoke` show `EXPECTED-DIVERGENCE` (not `DIVERGES`), gemini must be added to BOTH copies + the new reason added to BOTH divergence sets. (Matrix cell logic l.243-253 confirmed: registered divergence reason → `EXPECTED-DIVERGENCE`; unregistered → `DIVERGES`.)
- **Two parity tests break, not one:** `test_provider_harness_constants...` (l.61) asserts the `provider_rows()` 9-row list AND the 3-tuple; `test_provider_harness_helper_json_round_trip` (l.322) asserts `set(providers) == {claude,codex,hermes}`.
- **`_workspace` test fixture (l.29-48) creates NO gemini files** — every new "present" gemini test must extend it (SOUL.runtime.md + MEMORY.runtime.md + GEMINI.md pointer).
- `collect-equality.sh` embeds the collector's output verbatim (provider-agnostic) → no change needed.

### Evidence
**Files** (`ls`/`grep` 2026-06-18): EXISTS `config/agents/gemini/MEMORY.runtime.md` (7069B), `GEMINI.md` (read instr at line 4), `config/agents/gemini/SOUL.runtime.md` (gate phrases ×3). `gemini` + `agy` on PATH on ace-linux-2.
**Will-break test:** `test_provider_harness_constants_use_exact_issue_capability_names` asserts the 3-tuple (file l.63).

<!-- sources: issue + parity script + 3 gemini artifacts + the test file + memory = 7 -->

---

## Deliverable

`provider_harness_parity.py` includes `gemini`, verifying its memory surface (MEMORY.runtime.md non-empty + GEMINI.md read pointer) and its repo-artifact gates, while marking `skills:invoke` as an explicit `expected_divergence` (gemini has no local skill dispatch) — so the parity report verifies gemini without false-flagging its legitimately-different shape.

---

## Design / Pseudocode

```
PROVIDERS = ("claude", "codex", "hermes", "gemini")          # gemini added

# _installed: unchanged. gemini -> _local_runtime_path None -> install = _command_exists("gemini").
#   (respects test_repo_runtime_files_do_not_make_provider_installed: repo SOUL.runtime.md
#    does NOT flip installed.)

_memory_read(... provider == "gemini"):
    mem = workspace/config/agents/gemini/MEMORY.runtime.md
    gmd = workspace/GEMINI.md
    # r1-F6: anchor on the basename, not the full repo-relative path (survives a
    # path-prefix edit / GEMINI.md reword that keeps the pointer).
    if mem.is_file() and mem read non-empty and "MEMORY.runtime.md" in GEMINI.md text:
        return present "gemini_memory_runtime_found"
    return absent "gemini_memory_runtime_missing"

_workflow_gates(... provider == "gemini"):                   # repo-artifact, NOT _local_runtime_path
    # PLACEMENT (r1-F2): insert immediately AFTER the claude block and BEFORE the
    # `runtime = _local_runtime_path(...)` line — else gemini (runtime None) hits
    # the `active_runtime_missing` early-return and false-flags.
    soul = workspace/config/agents/gemini/SOUL.runtime.md
    if soul.is_file() and _contains_all(text, GATE_PHRASES):
        return present "gemini_soul_runtime_gates_found"
    return absent "hard_gates_runtime_missing"

_skills_invoke(... provider == "gemini"):
    # agy is router-first-class but unsupported for dispatch (#3190): no local skill adapter.
    return expected_divergence "gemini_skill_dispatch_unsupported"
EXPECTED_DIVERGENCE_REASONS += {"gemini_skill_dispatch_unsupported"}
```
`provider_rows`, `collect_provider_harness`, `emit_yaml`, `unknown_provider_harness` all iterate `PROVIDERS` → gemini included automatically.

**Scoping note (the #3206 warning):** gemini's gates are checked against the **repo** `SOUL.runtime.md` (same pattern as claude's repo `AGENTS.md`/`SOUL.runtime.md`), NOT a local CLI runtime — so the absence of a local AGENTS.md does not false-flag. `skills:invoke` is `expected_divergence`, not `absent`, so the matrix stays green. `memory:read`/`gates` are still install-gated (consistent with all providers: a provider not installed on a box reports `not_installed`).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/provider_harness_parity.py` | gemini in PROVIDERS + 3 branches + EXPECTED_DIVERGENCE_REASONS reason |
| Modify | `tests/readiness/test_provider_harness_parity.py` | fix BOTH breaking tests (provider_rows 12 rows + json set); extend `_workspace` fixture; add gemini tests |
| Modify | `scripts/readiness/build-equality-matrix.py` | gemini in its PROVIDERS (l.50) + reason in its EXPECTED_DIVERGENCE_REASONS (l.52) so gemini renders + skills shows EXPECTED-DIVERGENCE |
| Modify | `tests/readiness/test_build_equality_matrix.py` | extend fixtures/assertions for gemini rows |
| Modify | `tests/readiness/test_collect_equality.py` | r3-F1: provider-set assertion += gemini |
| Modify | `tests/readiness/test_collect_equality_ps1_schema.py` | r3-F1: provider-set assertions += gemini |
| Modify | `tests/readiness/fixtures/equality-ace-win-1.sample.yaml` | r3-F1: add gemini provider_harness block |
| Update | docs/plans/README.md | index |

> Drift note for #3058: the duplicated `PROVIDERS`/`EXPECTED_DIVERGENCE_REASONS` across the two scripts is itself a drift surface. Out of scope here (matching the existing pattern in both copies), but a candidate follow-up to import one from the other.

---

## TDD Test List

| Test | Verifies | Expected |
|---|---|---|
| test_providers_includes_gemini (update existing) | PROVIDERS tuple | `(claude,codex,hermes,gemini)` |
| test_gemini_memory_read_present | installed gemini + repo surface | present `gemini_memory_runtime_found` |
| test_gemini_memory_read_absent_when_pointer_missing | GEMINI.md lacks read instruction | absent `gemini_memory_runtime_missing` |
| test_gemini_memory_read_absent_when_runtime_empty | empty MEMORY.runtime.md | absent |
| test_gemini_workflow_gates_from_repo_soul | repo SOUL.runtime.md has gate phrases | present `gemini_soul_runtime_gates_found` |
| test_gemini_workflow_gates_absent_without_phrases | SOUL lacks phrases | absent |
| test_gemini_skills_expected_divergence | no local dispatch | expected_divergence `gemini_skill_dispatch_unsupported` |
| test_gemini_not_installed_reports_not_installed | gemini not on PATH | all caps `absent/provider_not_installed` |
| test_gemini_repo_files_do_not_make_installed | repo SOUL/MEMORY present, no gemini cmd | installed False (invariant) |
| test_expected_divergence_includes_gemini_reason | divergence reason registered | `is_expected_divergence("gemini_skill_dispatch_unsupported")` True |

---

## Acceptance Criteria

- [ ] Parity report includes gemini and verifies its memory surface (`memory:read` present when installed + surface intact)
- [ ] gemini `workflow:gates` verified against repo `SOUL.runtime.md`; `skills:invoke` = `expected_divergence` (no false `absent`)
- [ ] gemini absence of a local runtime does NOT false-flag (no `active_runtime_missing`)
- [ ] repo files do not flip gemini `installed` (invariant preserved)
- [ ] `test_provider_harness_constants...` updated; `uv run pytest tests/readiness/ -q` green; no regression in `tests/ai/ tests/readiness/`
- [ ] Review artifact posted

---

## Adversarial Review Summary

**r1 — Claude (adversarial subagent), 2026-06-18:** verdict **MAJOR**. Verified findings, incorporated:

| # | Sev | Finding | Resolution |
|---|---|---|---|
| F1 | MAJOR | TWO parity tests break (provider_rows 9-row list + json round-trip set), draft named one | both in Files to Change + TDD; provider_rows now 12 rows |
| F2 | MAJOR | gemini `_workflow_gates` branch must precede the `_local_runtime_path` early-return or it false-flags `active_runtime_missing` | placement pinned in pseudocode + regression test |
| F-new | MAJOR | downstream `build-equality-matrix.py` duplicates `PROVIDERS` + `EXPECTED_DIVERGENCE_REASONS` → gemini won't render / skills shows DIVERGES unless both extended | added to Files to Change |
| F3 | MAJOR | install-gating: `memory:read` reports `not_installed` where the gemini CLI is absent — possibly vacuous on the report-generating box (ace-linux-1) | **open decision for user** (see Risks) |
| F4 | MINOR | `_workspace` fixture creates no gemini files | extend fixture (in scope) |
| F5 | MINOR | does the matrix treat `expected_divergence` as pass? | verified: registered reason → `EXPECTED-DIVERGENCE` cell (l.243-253) |
| F6 | MINOR | GEMINI.md full-path substring brittle | anchor on basename `MEMORY.runtime.md` |
| F7 | PASS | stdlib-only/cross-platform respected | — |

**r2 — Codex:** UNAVAILABLE (codex exec timed out twice earlier today, same sandbox-PreToolUse-hook root cause; not re-spent per zero-waste). Degraded T1 documented.

**Overall:** PASS pending the F3 user decision (below) + scope confirmation.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR→addressed | F1/F2/F-new/F4/F6 fixed; F5 verified; F3 → user |

**Code-stage r3 — Claude (adversarial subagent), 2026-06-18:** verdict **MAJOR**, all verified + fixed. Core impl in the two named files correct (install-invariant preserved, gates placement correct, stdlib/secrets-safe, no matrix percentage skew). The MAJOR was **incomplete consumer coverage** (the "enumerate all consumers" lesson): changing the shared collector output broke THREE more sibling tests not in the original scope — `test_collect_equality.py` (provider-set assertion), `test_collect_equality_ps1_schema.py` (×2: field-parity + sample-parse), and the golden fixture `fixtures/equality-ace-win-1.sample.yaml` (missing gemini sub-tree). All fixed: provider sets expanded + gemini block added to the fixture. Also tightened the GEMINI.md pointer to the full path (r3-F3). Final: the 4 + 3 affected test files green (147 passed); the only remaining `tests/readiness/` failures are pre-existing telegram git-state tests (proven isolated — no import of the parity modules).

---

## Risks and Open Questions

- **OPEN DECISION 1 (F3) — install-gating of gemini `memory:read`:** the gemini memory surface is a REPO artifact (exists on every checkout), unlike claude/codex/hermes whose memory is partly local. If gemini's `memory:read` stays install-gated (option A), it reports `not_installed` on any box without the gemini CLI — and if the report-generating box **ace-linux-1** lacks the gemini CLI (unverifiable from here), the surface this issue exists to verify is **never actually checked in the canonical report** (vacuous acceptance). Option B: verify the repo surface install-independently for gemini (most faithful to "the surface is verifiable"), at the cost of model asymmetry (other providers install-gate). **Needs user input** (they know ace-linux-1's gemini status + how they read the matrix).
- **OPEN DECISION 2 — scope:** include `build-equality-matrix.py` (so gemini renders end-to-end + skills shows EXPECTED-DIVERGENCE) — recommended — vs collector-only (#3206 literal scope) with the matrix render as a follow-up. Recommended = include it (else the two PROVIDERS lists drift, which #3058 is trying to kill).
- **Resolved:** `skills:invoke(gemini)` = `expected_divergence` (agy dispatch-unsupported per #3190); registered in both divergence sets so the matrix shows EXPECTED-DIVERGENCE, not DIVERGES.
- **Risk — must update the constants test** (`PROVIDERS == 3-tuple`); in Files to Change.
- **Risk — emit_yaml/JSON consumers:** anything parsing the parity YAML must tolerate a 4th provider; the schema is per-provider keyed, so additive (low risk).

## Complexity: T2

**T2** — single script + its test, but harness-parity (cross-provider semantics + a will-break invariant test). Review = Claude inline (+ Codex if the env permits; #3209 showed codex exec times out under Claude-Code Bash).
