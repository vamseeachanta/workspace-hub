# Plan for #2127: fix(governance): make plan-approval-gate honor FORCE_PLAN_GATE_STRICT and DISABLE_ENFORCEMENT

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2127
> **Review artifacts:** scripts/review/results/2026-04-11-plan-2127-claude.md | scripts/review/results/2026-04-11-plan-2127-codex.md | scripts/review/results/2026-04-11-plan-2127-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.claude/hooks/plan-approval-gate.sh` — PreToolUse hook enforcing plan-approval hard-stop for Write|Edit|MultiEdit|Bash. Checks `has_approval()`, `is_safe_path()`, and `is_self_approved()`. Does **not** source `enforcement-env.sh` or read `FORCE_PLAN_GATE_STRICT` / `DISABLE_ENFORCEMENT`. Only bypass is the undocumented `SKIP_PLAN_APPROVAL_GATE=1` env var (line 23).
- Found: `scripts/enforcement/enforcement-env.sh` — exports `FORCE_PLAN_GATE_STRICT=${FORCE_PLAN_GATE_STRICT:-1}`, `REVIEW_GATE_STRICT=${REVIEW_GATE_STRICT:-1}`, `DISABLE_ENFORCEMENT=${DISABLE_ENFORCEMENT:-0}`. Documented as the canonical source for enforcement mode control.
- Found: `.claude/settings.json` — wires `plan-approval-gate.sh` as PreToolUse hook (matcher: `Write|Edit|MultiEdit|Bash`, timeout: 5s). Does **not** set `FORCE_PLAN_GATE_STRICT` in the `env` block (only `REVIEW_GATE_STRICT` is set there).
- Found: `tests/work-queue/test_session_governor.py` — existing plan-gate coverage for hook existence, registration, matcher, block without marker, safe paths, and allow-with-marker. **No** tests for `FORCE_PLAN_GATE_STRICT` or `DISABLE_ENFORCEMENT` behavior in the plan gate.
- Found: `docs/governance/SESSION-GOVERNANCE.md` — documents `FORCE_PLAN_GATE_STRICT` as the plan gate control variable and `DISABLE_ENFORCEMENT` as the master kill switch for all gates. Documents installation to `.git/hooks/enforcement-env`.
- Found: `scripts/enforcement/require-review-on-push.sh` — a sibling enforcement hook that already reads `REVIEW_GATE_STRICT` and `DISABLE_ENFORCEMENT`, providing a reference implementation pattern.
- Gap: `plan-approval-gate.sh` does not read or respect either documented env var. Documented breakglass controls are inert in the runtime path.

### Standards

| Standard | Status | Source |
|---|---|---|
| N/A | N/A | No external standards apply |

### LLM Wiki pages consulted

- N/A — no domain wiki pages relevant to this enforcement plumbing issue.

### Documents consulted

- `docs/governance/SESSION-GOVERNANCE.md` — enforcement variable table (lines 335-339), pre-commit flow diagram (lines 369-375)
- `docs/plans/README.md` — planning workflow and template reference
- Issue #2127 body and comments — adversarial-review follow-up, recommended fix precedence, required test matrix

### Gaps identified

- `plan-approval-gate.sh` does not source `enforcement-env.sh` or read `FORCE_PLAN_GATE_STRICT` / `DISABLE_ENFORCEMENT` from any source.
- No test coverage for advisory mode (`FORCE_PLAN_GATE_STRICT=0`) or disabled mode (`DISABLE_ENFORCEMENT=1`) in the plan gate hook.
- `SKIP_PLAN_APPROVAL_GATE` (the current bypass) is not documented in `SESSION-GOVERNANCE.md` and has unclear relationship to the documented variables.
- The `git push` block path inside `plan-approval-gate.sh` (lines 101-108) also does not honor either variable.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md` |
| Hook under fix | `.claude/hooks/plan-approval-gate.sh` |
| Env source file | `scripts/enforcement/enforcement-env.sh` |
| Tests | `tests/work-queue/test_session_governor.py` (extend `TestPlanApprovalGate`) |
| Governance docs | `docs/governance/SESSION-GOVERNANCE.md` |
| Plan review — Claude | `scripts/review/results/2026-04-11-plan-2127-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-11-plan-2127-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-11-plan-2127-gemini.md` |
| Plans index | `docs/plans/README.md` |

---

## Deliverable

The `plan-approval-gate.sh` hook correctly reads and honors `FORCE_PLAN_GATE_STRICT` and `DISABLE_ENFORCEMENT` in both implementation-write and `git push` paths, with regression tests and governance documentation aligned to the live behavior.

---

## Pseudocode

```
# At top of plan-approval-gate.sh, after SCRIPT_DIR/WS resolution:

source_enforcement_env():
    CONTRACT_FILE = "$WS/scripts/enforcement/enforcement-env.sh"
    if file exists "$CONTRACT_FILE":
        source "$CONTRACT_FILE"
    # Fallback defaults if contract file absent:
    FORCE_PLAN_GATE_STRICT = ${FORCE_PLAN_GATE_STRICT:-1}
    DISABLE_ENFORCEMENT    = ${DISABLE_ENFORCEMENT:-0}

# New early-exit before any tool-name checks:

if DISABLE_ENFORCEMENT == "1":
    stderr: "[plan-gate] SKIP: All enforcement disabled (DISABLE_ENFORCEMENT=1)."
    exit 0

# Replace existing block JSON emission (Write/Edit and git-push paths):

emit_decision(tool_context):
    if FORCE_PLAN_GATE_STRICT == "1":
        stdout: {"decision":"block","reason":"Plan approval required..."}
    else:
        stderr: "[plan-gate] ADVISORY: No plan-approval marker. Proceeding (non-strict)."
        # No stdout JSON — tool call proceeds

# Keep existing documented/non-documented bypass behavior unchanged unless required for compatibility.
# Scope this issue to honoring FORCE_PLAN_GATE_STRICT and DISABLE_ENFORCEMENT consistently.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.claude/hooks/plan-approval-gate.sh` | Source `enforcement-env.sh`; add `DISABLE_ENFORCEMENT` early exit; replace unconditional block with mode-aware behavior for strict and advisory modes |
| Extend | `tests/work-queue/test_session_governor.py` | Add caller-level regression tests for write/edit and `git push` behavior across env combinations |
| Update | `docs/governance/SESSION-GOVERNANCE.md` | Document that `plan-approval-gate.sh` now honors both variables and align runtime semantics with live behavior |
| Update | `docs/plans/README.md` | Add this plan to the Plan Index table |
| Create | `scripts/review/results/2026-04-11-plan-2127-claude.md` | Adversarial review artifact (Claude) |
| Create | `scripts/review/results/2026-04-11-plan-2127-codex.md` | Adversarial review artifact (Codex) |
| Create | `scripts/review/results/2026-04-11-plan-2127-gemini.md` | Adversarial review artifact (Gemini) |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_default_strict_blocks_without_marker` | Default env (FORCE_PLAN_GATE_STRICT=1, DISABLE_ENFORCEMENT=0) blocks impl writes | Write to `/src/app.py`, no marker, default env | stdout contains `"decision":"block"` |
| `test_advisory_mode_warns_without_marker` | FORCE_PLAN_GATE_STRICT=0 emits warning, does not block | Write to `/src/app.py`, no marker, FORCE_PLAN_GATE_STRICT=0 | stderr contains `ADVISORY`, stdout has no `block` |
| `test_disable_enforcement_skips_entirely` | DISABLE_ENFORCEMENT=1 bypasses all checks | Write to `/src/app.py`, no marker, DISABLE_ENFORCEMENT=1 | stderr contains `SKIP`, stdout has no `block` |
| `test_disable_overrides_strict` | DISABLE_ENFORCEMENT=1 takes precedence over FORCE_PLAN_GATE_STRICT=1 | Write to `/src/app.py`, no marker, both set | No block; DISABLE wins |
| `test_strict_blocks_git_push_without_marker` | Strict mode blocks `git push` without approval | Bash with `git push`, no marker, FORCE_PLAN_GATE_STRICT=1 | stdout contains `"decision":"block"` |
| `test_advisory_allows_git_push_without_marker` | Advisory mode warns but allows `git push` | Bash with `git push`, no marker, FORCE_PLAN_GATE_STRICT=0 | stderr warning, no block on stdout |
| `test_disable_allows_git_push` | DISABLE_ENFORCEMENT=1 allows `git push` without checks | Bash with `git push`, no marker, DISABLE_ENFORCEMENT=1 | No block |
| `test_contract_file_sourced` | Hook sources `enforcement-env.sh` when present | Contract file exists at expected path | Variables set from contract file |
| `test_contract_file_missing_uses_defaults` | Hook falls back to defaults when contract file absent | No contract file in workspace | FORCE_PLAN_GATE_STRICT=1, DISABLE_ENFORCEMENT=0 (strict) |

---

## Acceptance Criteria

- [ ] `plan-approval-gate.sh` sources `scripts/enforcement/enforcement-env.sh` at startup
- [ ] `DISABLE_ENFORCEMENT=1` causes immediate exit 0 with stderr notice (no block JSON)
- [ ] `FORCE_PLAN_GATE_STRICT=0` emits advisory stderr warning instead of block JSON when no marker exists
- [ ] `FORCE_PLAN_GATE_STRICT=1` (default) preserves current strict-block behavior
- [ ] `DISABLE_ENFORCEMENT` takes precedence over `FORCE_PLAN_GATE_STRICT` (checked first)
- [ ] Both Write/Edit and `git push` code paths honor both variables
- [ ] All 9 new tests pass: `uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v -k "PlanApprovalGateEnforcement"`
- [ ] Existing `TestPlanApprovalGate` tests still pass (no regression)
- [ ] Full suite passes: `uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v`
- [ ] `docs/governance/SESSION-GOVERNANCE.md` updated to reflect runtime hook honoring both variables
- [ ] `docs/plans/README.md` updated with this plan entry
- [ ] Review artifacts posted to `scripts/review/results/2026-04-11-plan-2127-*.md`

---

## Adversarial Review Summary

Formal adversarial review has **not yet been conducted**. No review artifacts exist at the expected paths:
- `scripts/review/results/2026-04-11-plan-2127-claude.md` — pending
- `scripts/review/results/2026-04-11-plan-2127-codex.md` — pending
- `scripts/review/results/2026-04-11-plan-2127-gemini.md` — pending

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Not yet reviewed |
| Codex | PENDING | Not yet reviewed |
| Gemini | PENDING | Not yet reviewed |

**Overall result:** PENDING (review required before status can advance past draft)

**Preliminary risk assessment from issue comments and live findings:**
- Issue comments confirm this is an adversarial-review follow-up from the governance audit cycle; the fix is well-scoped.
- Live reproduction confirms all four env combinations (default, FORCE_PLAN_GATE_STRICT=0, DISABLE_ENFORCEMENT=1, both) produce identical block JSON today — the bug is real and reproducible.
- Comments specifically call out the risk that documented breakglass controls are not functional in the runtime path — this plan addresses that directly.
- Comments recommend fixing env loading and precedence in the runtime hook first, which aligns with this plan's approach.

Revisions made based on review:
- (none yet — awaiting formal review)

---

## Risks and Open Questions

- **Risk:** Sourcing `enforcement-env.sh` adds a file read to every Write/Edit/Bash hook invocation. Mitigation: the hook already has a 5s timeout budget and `enforcement-env.sh` is small and local.
- **Risk:** If `enforcement-env.sh` is absent (e.g., fresh clone before install), hook must not crash. Mitigation: fallback defaults should preserve the current strict behavior.
- **Risk:** Advisory-mode behavior can regress silently if only write-path tests are added. Mitigation: require the same matrix for the Bash `git push` branch.
- **Open:** Should `.claude/settings.json` `env` block also set `FORCE_PLAN_GATE_STRICT=1` (like it already sets `REVIEW_GATE_STRICT=1`) for symmetry, or should the runtime hook rely solely on `enforcement-env.sh` defaults?
- **Open:** Should documentation explicitly mention the current undocumented `SKIP_PLAN_APPROVAL_GATE` bypass, or leave it out of scope for this issue?

---

## Complexity: T2

**T2** — multi-file change spanning a runtime hook, its test suite, and governance documentation. Requires careful env-sourcing and precedence logic plus a 9-test matrix covering both the Write/Edit and `git push` code paths. Not T3 because the scope stays contained to one hook and its direct dependencies.
