# Plan for #3703: reconcile-ecosystem.sh fails open when uv is off the non-interactive PATH

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-08-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3703
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-12-plan-3703-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/readiness/reconcile-ecosystem.sh:217` — the uv guard:
  ```bash
  command -v uv >/dev/null 2>&1 || { add OPERATOR-ONLY "$MACHINE" "uv missing — cannot read equality verdicts" "install uv"; return; }
  ```
  `command -v` checks only PATH; fails silently in non-interactive SSH where `~/.local/bin` is absent.

- Found: `scripts/readiness/reconcile-ecosystem.sh:52-57` — existing pattern for python probe:
  ```bash
  # `python` is a real interpreter — probe by RUNNING it, not `command -v` (the stub is on PATH).
  if python3 -c '' >/dev/null 2>&1; then PY=python3
  elif python -c '' >/dev/null 2>&1; then PY=python
  else PY=python3; fi
  ```
  The repo already knows `command -v` is unreliable for tools that may have PATH stubs. The fix mirrors this pattern.

- Found: `tests/readiness/test_reconcile_ecosystem.py` — test file exists. Contains static invariant checks and a smoke run. No test for the uv-off-PATH failure mode.

- Gap: No `_resolve_uv()` helper exists; no INCOMPLETE/partial-plan exit code convention exists in the script.

### Standards

Not applicable — harness script, not an engineering calculation.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- Issue #3703 body — contains reproduction evidence table: ace-linux-1 reported `AUTO-SAFE 0, OPERATOR-ONLY 1` under non-interactive SSH vs `AUTO-SAFE 28, OPERATOR-ONLY 0` under `bash -lc`. The silent empty equality section masked 27 of 28 planned actions.
- `docs/session-handoffs/2026-07-27-handoff-repo-sync-uv-path-outage.md` (referenced in issue) — same PATH failure class affected repo-sync; resolved there by ensuring a deterministic PATH prefix in cron. The cron install for reconcile-ecosystem.sh already prefixes `PATH=$HOME/.local/bin:$PATH`, but other callers (remote SSH, dispatch) do not.
- Related issue #3702 — STALE-CHECKOUT deadlock; the issue body notes that masking 27 equality actions hides this deadlock from view. Fixing #3703 restores visibility of #3702.
- `scripts/readiness/reconcile-ecosystem.sh` — full text read; `add()` function accumulates OPERATOR-ONLY/AUTO-SAFE/NEEDS-APPROVAL lines into a `PLAN` array; the function returns without setting any global INCOMPLETE flag today.

### Gaps identified

- No `_resolve_uv()` helper that checks known install paths before PATH.
- No mechanism to mark the plan output as INCOMPLETE when a required tool is unreachable.
- No test asserts that an invocation with `uv` off PATH produces a clearly degraded (not clean) output.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-08-12 via `gh issue view`):
- `#3703` — OPEN — bug(equality): reconcile-ecosystem.sh fails open to an empty equality plan when uv is off the non-interactive PATH

**File existence** (`ls -la` 2026-08-12):
- EXISTS: `scripts/readiness/reconcile-ecosystem.sh`
- EXISTS: `tests/readiness/test_reconcile_ecosystem.py`
- MISSING (new — this plan creates): no new files; all changes are in-place

**Line excerpts** (`sed -n 216,218p scripts/readiness/reconcile-ecosystem.sh`):
```
equality_plan() {
  command -v uv >/dev/null 2>&1 || { add OPERATOR-ONLY "$MACHINE" "uv missing — cannot read equality verdicts" "install uv"; return; }
```

**Line excerpts** (`sed -n 52,58p scripts/readiness/reconcile-ecosystem.sh`):
```
# `python` is a real interpreter — probe by RUNNING it, not `command -v` (the stub is on PATH).
if python3 -c '' >/dev/null 2>&1; then PY=python3
elif python -c '' >/dev/null 2>&1; then PY=python
else PY=python3; fi
```

**Gap proofs**:
- `grep -n "_resolve_uv\|INCOMPLETE" scripts/readiness/reconcile-ecosystem.sh` → no output → confirms neither helper nor INCOMPLETE flag exists yet.
- `grep -n "uv.*PATH\|PATH.*uv\|local.bin.uv" tests/readiness/test_reconcile_ecosystem.py` → no output → confirms no existing PATH-isolation test.

**Reproduction proofs**:
Per issue body (2026-07-29 measurement):

| host | plan under non-interactive SSH | plan under `bash -lc` |
|---|---|---|
| ace-linux-1 | AUTO-SAFE **0**, OPERATOR-ONLY 1 | AUTO-SAFE **28**, OPERATOR-ONLY 0 |
| gpu-claw | 11 actions total | 33 actions total |

- Reproduced at: 2026-07-29 (per issue body)
- Failure mode observed matches issue claim: YES — `command -v uv` exits non-zero in non-interactive SSH where `~/.local/bin` is absent, causing `equality_plan()` to return immediately with one misleading "install uv" advisory row.

<!-- Verification: 5 distinct sources (issue body + script line 217 + script lines 52-57 + test file + session-handoff). Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-08-12-issue-3703-reconcile-ecosystem-uv-path.md |
| Implementation | `scripts/readiness/reconcile-ecosystem.sh` |
| Tests | `tests/readiness/test_reconcile_ecosystem.py` |
| Plan review — Claude | scripts/review/results/2026-08-12-plan-3703-claude.md |
| Plan review — Codex | scripts/review/results/2026-08-12-plan-3703-codex.md |
| Plan review — Agy | scripts/review/results/2026-08-12-plan-3703-agy.md |

---

## Deliverable

`equality_plan()` in `reconcile-ecosystem.sh` will resolve uv by probing known install locations (`~/.local/bin/uv`, `~/.cargo/bin/uv`) before falling back to PATH, will use the resolved binary for the uv call, and will emit a clearly degraded (not clean-looking) output when uv is genuinely absent from all locations.

---

## Pseudocode

Trivial — see Files to Change.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/reconcile-ecosystem.sh` | Add `_resolve_uv()` helper; replace bare `command -v uv` guard in `equality_plan()` with the helper; set an INCOMPLETE flag when uv is genuinely missing |
| Modify | `tests/readiness/test_reconcile_ecosystem.py` | Add static invariant test that the script uses `_resolve_uv` (not bare `command -v uv`); add invocation test that a PATH with uv stripped still produces a flagged/INCOMPLETE output rather than a clean one |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_uses_resolve_uv_not_bare_command_v` | Static: script calls `_resolve_uv` not bare `command -v uv` in `equality_plan` | Script text | No bare `command -v uv` inside `equality_plan()` body |
| `test_resolve_uv_probes_local_bin` | Static: `_resolve_uv` checks `$HOME/.local/bin/uv` and `$HOME/.cargo/bin/uv` | Script text | Both paths present in `_resolve_uv` body |
| `test_equality_plan_without_uv_on_path_is_incomplete` | Invocation: running the script with a PATH that excludes uv (even when uv is installed) produces a clearly degraded output, not a clean 0-action plan | `PATH=/usr/bin:/bin bash reconcile-ecosystem.sh` (with real uv at `~/.local/bin/uv`) | Output contains INCOMPLETE marker or non-zero exit; does NOT look like a clean empty plan |
| `test_equality_plan_genuinely_no_uv_is_incomplete` | Invocation: running with no uv at any probed location produces INCOMPLETE, not a misleading OPERATOR-ONLY advisory | `HOME=/tmp/no-uv-home PATH=/usr/bin:/bin bash reconcile-ecosystem.sh` | INCOMPLETE or OPERATOR-ONLY with text distinguishing "not installed" from "off PATH"; exit code ≠ 0 |

---

## Acceptance Criteria

- [ ] `equality_plan()` no longer uses bare `command -v uv`; instead calls `_resolve_uv` or equivalent.
- [ ] When uv is installed at `~/.local/bin/uv` but not on PATH, the script finds it and completes the equality section normally.
- [ ] When uv is genuinely absent from all probed locations, the script emits output clearly marked INCOMPLETE (text and/or non-zero exit); the output does NOT look like a clean 0-action plan.
- [ ] The OPERATOR-ONLY advisory text distinguishes "uv not installed" from "uv not on PATH in this shell context".
- [ ] All new tests pass: `uv run pytest tests/readiness/test_reconcile_ecosystem.py -v`
- [ ] No regression: existing `test_bash_syntax_is_valid`, `test_no_dangerous_git_patterns`, and other invariants still pass.
- [ ] `bash -n scripts/readiness/reconcile-ecosystem.sh` exits 0 (syntax check).

---

## Adversarial Review Summary

<!-- To be filled after adversarial review completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Agy | pending | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** `HOME` may not be set in the execution environment (rare in bash but possible in some CI contexts). `_resolve_uv` should handle `${HOME:-}` gracefully.
- **Risk:** The INCOMPLETE output format needs to be legible to all consumers of the plan (human, dispatch, digest). If `add()` is the only mechanism, a new verdict class like `INCOMPLETE` needs adding. An alternative is to exit non-zero from `equality_plan()` itself and let the caller's `|| return` propagate. The implementer should choose the lighter option.
- **Open:** Should the script also probe for uv via `~/.cargo/bin/uv`? Cargo-installed uv is less common than `astral.sh` installs but not rare. Recommendation: probe both, document which paths are checked.
- **Open:** The issue notes that cron already prefixes `PATH=$HOME/.local/bin:$PATH`. This plan does not remove that prefix — both fixes are complementary. The PATH prefix handles cron; `_resolve_uv` handles all other callers.

---

## Complexity: T1

**T1** — single file change (~15 lines), one helper function added, two tests added. No new files created.
