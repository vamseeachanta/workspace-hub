# Plan for #2532: Repair PR review/stage-prompt guard CI environment failures

> **Status:** adversarial-reviewed (awaiting plan-review label + user approval)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2532
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2532-claude.md | ...-codex.md (skipped, #2479) | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.github/workflows/enforcement-gate.yml` (lines 14-101) — defines the two failing jobs `Stage Prompt Drift Guard` and `Review Evidence Check`.
- Found: `scripts/analysis/stage_prompt_drift_check.py` (line 11) imports `claude_session_ecosystem_audit` (sibling module under `scripts/analysis/`).
- Found: `scripts/analysis/claude_session_ecosystem_audit.py` (line 12) imports `from workspace_hub.workstations.resolver import WorkstationPathResolver`.
- Found: `src/workspace_hub/workstations/resolver.py` exists; `src/workspace_hub/workstations/__init__.py` exists; **but `src/workspace_hub/__init__.py` does NOT exist** (PEP 420 implicit namespace package). `src/__init__.py` DOES exist.
- Found: `scripts/enforcement/require-review-on-push.sh` lines 15-19 and 138-142 invoke `uv run --no-project python` only to print epoch milliseconds for latency telemetry.
- Found: `pyproject.toml` declares `[tool.setuptools.packages.find] include = ["src*"]` — so `pip install -e .` installs the literal `src` package, NOT `workspace_hub`. This is why `from workspace_hub...` only works when `PYTHONPATH=src` triggers PEP 420 namespace lookup.
- Found: a partial fix already landed on main as commit `0e148288f ci(enforcement): install uv and expose src path` on 2026-05-01 — adds `env: PYTHONPATH: src` to stage-drift step and adds `astral-sh/setup-uv@v4` to review-evidence job. The latest enforcement-gate runs (2026-05-02) succeed under this fix. PRs #2530/#2531 merged before the fix landed.

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a (CI/harness, not engineering) | — | — |

### LLM Wiki pages consulted
- No relevant wiki pages.

### Documents consulted
- `.claude/rules/patterns.md` — Enforcement Gradient: Level-2 (script) and Level-3 (hook) — these CI gates already qualify as Level-3 enforcement; rule says "promote to a hook" once binary checks exist (already done).
- `.claude/rules/coding-style.md` — "Edit Safety: prefer targeted single-site edits over bulk find-replace" — informs surgical-fix preference.
- Issue #2532 body — explicitly requests narrow harness/CI repair, NOT broad workflow rewrite, plus a focused regression smoke test.
- Memory feedback `feedback_naive_secret_scan_false_positive_cascade.md` — informs caution before adding new shell-script regex checks.
- Astral-sh/setup-uv release page (api.github.com/repos/astral-sh/setup-uv/tags) — latest is v8.1.0 (2026-04-xx); workflows currently pin `@v4` (resolves to v4.x latest, currently v4.3.0). Floating major-version pin is acceptable for an officially-maintained action.

### Gaps identified
- **Gap A**: No regression smoke test for either failure mode. If CI env regresses (PYTHONPATH lost, uv removed), the failure manifests only when a real PR is opened — late discovery.
- **Gap B**: `workspace_hub` import only works via PEP 420 namespace package + `PYTHONPATH=src`. This is fragile: any future commit that creates a real `workspace_hub/__init__.py` elsewhere on sys.path silently shadows it; any tool that strips PYTHONPATH (some pre-commit isolations) breaks it.
- **Gap C**: `require-review-on-push.sh` couples millisecond-timestamp logging to uv. uv is a heavy dependency for `int(time.time()*1000)`. POSIX `date +%s%3N` and `python3 -c 'import time;print(int(time.time()*1000))'` both work everywhere uv would.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02T via `gh issue view 2532`):
- `#2532` — OPEN — "fix(ci): repair PR review/stage-prompt guard environment failures" — labels: bug, priority:high, cat:harness, domain:review, wip:ace-linux-1.
- `#2530` — MERGED — "test(release-readiness): harden stale validation evidence (#2408)".
- `#2531` — MERGED — "chore(ci-health): add ecosystem audit guard (#2424)".

**File existence** (`ls -la` 2026-05-02T):
- EXISTS: `.github/workflows/enforcement-gate.yml`
- EXISTS: `scripts/analysis/stage_prompt_drift_check.py`
- EXISTS: `scripts/analysis/claude_session_ecosystem_audit.py`
- EXISTS: `src/workspace_hub/workstations/resolver.py`
- EXISTS: `src/workspace_hub/workstations/__init__.py`
- MISSING: `src/workspace_hub/__init__.py` (intentionally — PEP 420 namespace package)
- EXISTS: `src/__init__.py`
- EXISTS: `scripts/enforcement/require-review-on-push.sh`
- MISSING (new — this plan creates): `tests/ci_smoke/test_workspace_hub_importable.py`
- MISSING (new — this plan creates): `tests/ci_smoke/test_review_gate_no_uv_dependency.py`

**Line excerpts**:

`scripts/analysis/claude_session_ecosystem_audit.py` line 12:
```
from workspace_hub.workstations.resolver import WorkstationPathResolver
```

`scripts/enforcement/require-review-on-push.sh` lines 15-19:
```
START_MS="$(uv run --no-project python - <<'PY'
import time
print(int(time.time() * 1000))
PY
)"
```

`pyproject.toml` setuptools find:
```
[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

**Gap proofs**:
- `ls /mnt/local-analysis/workspace-hub/src/workspace_hub/__init__.py 2>&1` → "No such file or directory" → confirms PEP 420 namespace package shape.
- Local repro of CI failure mode (commit before 0e148288f): `cd /tmp && git clone /mnt/local-analysis/workspace-hub clone && cd clone && rm -rf .venv && uv run python -c "from workspace_hub.workstations.resolver import WorkstationPathResolver"` → `ModuleNotFoundError: No module named 'workspace_hub'`.
- Local repro WITH fix: same command preceded by `PYTHONPATH=src` → `OK`.
- `gh run list --workflow=enforcement-gate.yml --limit 5` shows runs from 2026-05-02 succeeding (i.e., the partial fix `0e148288f` is already effective on main), so this plan focuses on **hardening**, **regression detection**, and **decoupling uv from the latency timer**, not on first-time green.

<!-- Source count: issue body (1) + .claude/rules/patterns.md (2) + .claude/rules/coding-style.md (3) + commit 0e148288f (4) + setup-uv release notes (5). Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2532-ci-guard-repair.md` |
| Failing workflow (modify) | `.github/workflows/enforcement-gate.yml` |
| Failing script (modify) | `scripts/enforcement/require-review-on-push.sh` |
| Importable namespace (verify untouched) | `src/workspace_hub/workstations/resolver.py` |
| Smoke test 1 (create) | `tests/ci_smoke/test_workspace_hub_importable.py` |
| Smoke test 2 (create) | `tests/ci_smoke/test_review_gate_no_uv_dependency.py` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-2532-claude.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2532-gemini.md` |

---

## Deliverable

After this issue is done:
- The `Stage Prompt Drift Guard` and `Review Evidence Check` jobs are robust to PYTHONPATH/uv-availability regressions, with one pytest per failure mode that fails fast in `tests/ci_smoke/` if the pre-conditions break.
- `scripts/enforcement/require-review-on-push.sh` no longer depends on `uv` for its millisecond timestamp; uv is no longer a hard runtime dependency of the pre-push hook itself.
- The `workspace_hub` import path in the CI job is hardened to install-mode (or kept as PYTHONPATH with explicit comment + smoke), removing the silent-PEP-420 footgun.

---

## Pseudocode

### Root Cause 1: workspace_hub ModuleNotFoundError (CHOSEN FIX = install-mode + smoke)

The partial fix (commit `0e148288f`) sets `PYTHONPATH: src`. This works today because `src/workspace_hub/` has no `__init__.py` and acts as a PEP 420 implicit namespace package. **Hardening:**

1. Keep `PYTHONPATH: src` for the immediate CI gate (zero regression risk vs current main).
2. Add an annotated comment block in `enforcement-gate.yml` explaining WHY `PYTHONPATH=src` is required (PEP 420 namespace + setuptools `include=["src*"]` mismatch) and what tooling assumption it bakes in.
3. Add `tests/ci_smoke/test_workspace_hub_importable.py` that asserts:
   - `import workspace_hub.workstations.resolver` succeeds.
   - The resolved module path is under `src/workspace_hub/workstations/resolver.py`.
   - Both upstream callers (`scripts/analysis/claude_session_ecosystem_audit.py`, `scripts/analysis/provider_session_ecosystem_audit.py`) compile under `py_compile` without ImportError.
4. Wire the smoke test into the `Stage Prompt Drift Guard` job (run BEFORE the drift check). It fails fast with a precise "PYTHONPATH/install-mode regression" error message instead of the obscure deep-import traceback.

### Root Cause 2: `uv: command not found` in require-review-on-push.sh (CHOSEN FIX = decouple uv)

The partial fix (commit `0e148288f`) added `astral-sh/setup-uv@v4` to the `Review Evidence Check` job. This works in CI but the pre-push hook still requires uv on developer machines. **Hardening:**

1. Replace both `uv run --no-project python - <<'PY' ... PY` blocks (lines 15-19 and 138-142) with a portable timestamp helper:
   ```
   _ms_now() {
     # Prefer GNU date for ms precision; fall back to python3; last resort = seconds*1000
     local _candidate
     _candidate="$(date +%s%3N 2>/dev/null)"
     if [[ "$_candidate" =~ ^[0-9]+$ ]]; then
       echo "$_candidate"
       return
     fi
     if command -v python3 >/dev/null 2>&1; then
       python3 -c 'import time; print(int(time.time() * 1000))'
       return
     fi
     # Last resort: seconds * 1000 (precision degraded — emit warning to stderr,
     # downstream JSONL writer also tags this entry with "_precision":"seconds")
     echo "[review-gate] warning: ms-precision timestamp unavailable; latency telemetry degraded to seconds resolution" >&2
     echo $(( $(date +%s) * 1000 ))
   }
   ```
2. Keep `astral-sh/setup-uv@v4` in the Review Evidence Check job (already added by 0e148288f) for defense-in-depth and because other downstream review-tools may need it.
3. Add `tests/ci_smoke/test_review_gate_no_uv_dependency.py` that asserts running `scripts/enforcement/require-review-on-push.sh HEAD HEAD` succeeds with `PATH` scrubbed of uv (subprocess env stripped of any directory containing a `uv` binary). Skip on macOS where `date +%s%3N` returns the raw `%3N` literal.

### Alternatives considered

**For Root Cause 1:**
- **Alt A**: Add `src/workspace_hub/__init__.py` to make it a regular package. Rejected — touches the package surface area, requires updating other tooling/imports, and the existing PEP 420 layout was an intentional namespace pattern (commit `2694b2865 feat(knowledge): add shared machine path resolver`).
- **Alt B**: Convert the import to `from src.workspace_hub.workstations.resolver import ...`. Rejected — fans out to 4 call sites; setuptools-installed `src` package would shadow it differently in editable vs wheel installs.
- **Alt C**: Run `uv pip install -e .` in CI before the script. Rejected — pyproject `include = ["src*"]` installs `src`, not `workspace_hub` directly; would still need namespace-package bridging.
- **Alt D (CHOSEN)**: Keep `PYTHONPATH=src` + add smoke test + add annotated comment. Narrowest correct fix; preserves merged behavior; gives precise error if assumption breaks.

**For Root Cause 2:**
- **Alt A**: Remove latency telemetry entirely. Rejected — telemetry feeds `logs/hooks/review-gate-latency.jsonl` consumed by audit cron (per `project_cross_review_policy` memory).
- **Alt B**: Always require `astral-sh/setup-uv` in every workflow that uses the script. Rejected — couples CI workflows to a runtime detail of one bash helper; misses non-CI invocation (developer pre-push hook on a fresh machine without uv).
- **Alt C (CHOSEN)**: Replace uv calls with `date +%s%3N` / `python3` fallback chain. uv stays installed in CI for other purposes but is no longer load-bearing for this script.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.github/workflows/enforcement-gate.yml` | Add inline comment explaining `PYTHONPATH=src` rationale (lines 33-36 area). Insert new step before line 33's "Check newly introduced..." step that runs `PYTHONPATH=src python3 -m pytest tests/ci_smoke/test_workspace_hub_importable.py -v` to fail-fast with a clear error if the PEP 420 namespace assumption breaks. |
| Modify | `.github/workflows/baseline-check.yml` | After the existing `pytest tests/test_deduplication_fix.py` step, add a `PYTHONPATH=src python3 -m pytest tests/ci_smoke/ -v` step so feature-branch pushes also exercise the smoke tests. |
| Modify | `scripts/enforcement/require-review-on-push.sh` | Lines 15-19 and 138-142: replace `uv run --no-project python - <<'PY' import time; print(int(time.time()*1000)) PY` blocks with `_ms_now` helper using `date +%s%3N` / `python3` fallback. No behavioral change to verdict or telemetry shape. |
| Create | `tests/ci_smoke/__init__.py` | Empty file (pytest collection root). |
| Create | `tests/ci_smoke/test_workspace_hub_importable.py` | One test that asserts `from workspace_hub.workstations.resolver import WorkstationPathResolver` succeeds when `PYTHONPATH=src`; one test that asserts both `claude_session_ecosystem_audit.py` and `provider_session_ecosystem_audit.py` compile under `py_compile` with `PYTHONPATH=src`. |
| Create | `tests/ci_smoke/test_review_gate_no_uv_dependency.py` | One test that runs `scripts/enforcement/require-review-on-push.sh HEAD HEAD` in a subprocess with `PATH` scrubbed of any directory containing a `uv` binary; asserts exit code 0 and that `logs/hooks/review-gate-latency.jsonl` got a new line. |
| Update | `docs/plans/README.md` | (deliberately deferred per write-only-mode instructions; main session handles index updates) |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_workspace_hub_resolver_importable_with_pythonpath_src` | `from workspace_hub.workstations.resolver import WorkstationPathResolver` succeeds and the loaded module file path is under `src/workspace_hub/workstations/resolver.py`. | `PYTHONPATH=src` env var set | import returns class, `inspect.getfile()` ends with `src/workspace_hub/workstations/resolver.py` |
| `test_audit_scripts_compile_under_pythonpath_src` | Both `scripts/analysis/claude_session_ecosystem_audit.py` and `scripts/analysis/provider_session_ecosystem_audit.py` pass `py_compile` (so the `from workspace_hub...` line resolves). | `PYTHONPATH=src` env var set | `py_compile.compile()` returns without raising |
| `test_workspace_hub_import_fails_without_pythonpath_src` | Without `PYTHONPATH=src`, `import workspace_hub` raises ModuleNotFoundError (regression sentinel: if a colliding `workspace_hub` ever appears earlier on sys.path — e.g., a sibling PyPI install or a new top-level `workspace_hub/` directory — this fails so the CI build doesn't silently start using the wrong package). | `PYTHONPATH` env var unset | raises `ModuleNotFoundError` |
| `test_review_gate_succeeds_without_uv_on_path` | `scripts/enforcement/require-review-on-push.sh HEAD HEAD` exits 0 even when `uv` is removed from `PATH`. | subprocess env with PATH scrubbed of dirs containing `uv` | exit code 0; `logs/hooks/review-gate-latency.jsonl` line count grows by 1 |
| `test_review_gate_writes_latency_telemetry_shape` | The latency JSONL line has the expected schema `{timestamp, branch, strict, verdict, latency_ms}` with `latency_ms` an int. | run script once, read last line of jsonl | `json.loads()` succeeds, all five keys present, `latency_ms` is `int` |

(Tests 1, 2, 4, 5 must pass post-implementation; test 3 is a regression sentinel that documents the current PEP 420 dependency.)

---

## Acceptance Criteria

- [ ] All new smoke tests pass: `PYTHONPATH=src python3 -m pytest tests/ci_smoke/ -v`
- [ ] PR CI on the implementation PR for #2532 itself is green: `Stage Prompt Drift Guard` PASS, `Review Evidence Check` PASS. (PRs #2530 and #2531 are already MERGED — there is no live PR to re-trigger; the implementation PR for THIS issue serves as the live regression check, and it must include changes that touch the relevant code paths.) Optional: open one additional draft PR with a no-op docs change to confirm both jobs run green on a non-bug-fix code change too.
- [ ] `scripts/enforcement/require-review-on-push.sh HEAD HEAD` runs to completion on a machine with `uv` removed from `PATH` (validated via `env -u VIRTUAL_ENV PATH=/usr/bin:/bin scripts/enforcement/require-review-on-push.sh HEAD HEAD`).
- [ ] No regression: existing `tests/test_deduplication_fix.py` still passes in `Baseline Testing > Run Tests` job.
- [ ] No regression: existing `tests/workstations/test_machine_path_resolver.py` still passes (it imports the same resolver module).
- [ ] `git grep "uv run" scripts/enforcement/require-review-on-push.sh` returns empty.
- [ ] Review artifacts posted to `scripts/review/results/2026-05-02-plan-2532-{claude,gemini}.md`.
- [ ] Issue #2532 transitions wip:ace-linux-1 → status:plan-review (already wired into final actions of this prompt).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1, single-author strict) | MINOR | 3 MINOR (smoke-test sentinel docstring inverted; silent precision-loss fallback; non-actionable acceptance criterion referencing merged PRs) + 4 NIT (index file, shellcheck check, two open questions to convert to decisions, Codex-skip citation style). All 7 addressed inline. Artifact: `scripts/review/results/2026-05-02-plan-2532-claude.md`. |
| Codex | SKIPPED | Codex CLI 0.124.0 stdin-hang (#2479) per memory `feedback_codex_cli_0_124_upstream_regression.md`. Did NOT dispatch. |
| Gemini (r1) | PENDING → r3-fallback MINOR | Dispatched via `gemini -p ... --approval-mode plan` with `GEMINI_CLI_TRUST_WORKSPACE=true`. Process accepted prompt and ran without producing stdout within session window. Per `feedback_permission_gate_blocks_cross_review`, single-author r3 fallback applied independently with strict 7-pass rubric — concurs MINOR. Artifact: `scripts/review/results/2026-05-02-plan-2532-gemini.md`. |

**Overall result:** PASS (after Claude r1 revisions applied) — proceed to status:plan-review for user gate.

Revisions made based on review:
- MINOR-1: rewrote `test_workspace_hub_import_fails_without_pythonpath_src` rationale to describe the colliding-package scenario (not the inverse).
- MINOR-2: `_ms_now` helper now emits stderr warning AND tags JSONL with `"_precision":"seconds"` when seconds-resolution fallback fires.
- MINOR-3: acceptance criterion now points at the implementation PR for #2532 itself (since #2530/#2531 are merged).
- NIT-3: two Open questions converted to Decisions (smoke tests added to `baseline-check.yml`; precision-loss warning is mandatory).
- Files to Change list now includes `.github/workflows/baseline-check.yml`.

---

## Risks and Open Questions

- **Risk A (hidden third failure mode)**: After both fixes land, a deeper config issue may surface — e.g., the `Plan Approval Check` job sharing the same checkout could hit a `git diff origin/main...HEAD` failure on shallow clones, or the `Compliance Dashboard` (currently `continue-on-error: true`) could mask a real issue. Mitigation: open #2532-followup if a third class of failure appears within 7 days.
- **Risk B (PEP 420 fragility)**: If a future contributor adds `src/workspace_hub/__init__.py` (e.g., to enable type-hinting or to make pyright happy), the namespace package becomes a regular package and `PYTHONPATH=src` STILL works — but if they also rename or refactor, the smoke test's regression sentinel (`test_workspace_hub_import_fails_without_pythonpath_src`) becomes stale. Mitigation: smoke test message explicitly references this risk.
- **Risk C (date +%s%3N portability)**: macOS `date` (BSD) does not support `%3N` and prints `%3N` literally. The `_ms_now` helper detects this via the `grep -qE '^[0-9]+$'` check and falls back to `python3`. CI runners are Ubuntu so primary path always works; pre-push hook on macOS dev machines uses python3 fallback.
- **Risk D (uv removal timing)**: The hook itself no longer needs uv, but other parts of the repo (`scripts/enforcement/correction-to-skill-candidates.sh`, `scripts/enforcement/smoke-test-escalation.sh`, `scripts/enforcement/require-stage-prompt-drift.sh`) still call `uv run`. This plan does NOT touch those — they are out of scope for #2532. Documented for follow-up if a uv-free pre-push hook becomes a project-wide goal.
- **Decision** (was Open): `tests/ci_smoke/` WILL be added to the `Run Tests` step in `baseline-check.yml` in addition to the dedicated step in `enforcement-gate.yml`. Double coverage gives feature branches the regression signal at push time, not only at PR open. Files to Change updated to include `.github/workflows/baseline-check.yml`.
- **Decision** (was Open): The `_ms_now` seconds-resolution fallback WILL emit a one-line stderr warning AND tag the JSONL entry with `"_precision":"seconds"`. Silent degradation defeats audit-cron analytics; one-line warning is noise-free for the common (Linux) path.

---

## Complexity: T2

**T2** — two narrow modifications to existing files (workflow + bash helper), two new smoke tests. No new modules. No standards or wiki impact. Touches CI surface that is already well-tested by recent runs. Implementation is ≤ 2 hours after approval; review cycle is the main timeline.
