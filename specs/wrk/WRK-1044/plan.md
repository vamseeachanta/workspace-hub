# WRK-1044 Plan — Deterministic Gate Enforcement D1-D16

> Route C | complex | dev-primary | Blocks: WRK-1045

## Mission

Convert 16 deterministic gate rules (D1-D16) from LLM prose into verifiable
scripts/hooks. Fix P1 bug in `exit_stage.py` Stage 1 path resolution. Add
`--json` CI flag to `verify-gate-evidence.py`. Add schema validator for
`stage-gate-policy.yaml`. Add Codex unavailability parking at Stage 6/13.

---

## Files to Create

| File | Purpose | Lines est. |
|------|---------|-----------|
| `scripts/work-queue/stage_exit_checks.py` | Stage-specific check functions extracted from exit_stage.py | ~180 |
| `scripts/work-queue/validate-stage-gate-policy.py` | L3 schema validator for stage-gate-policy.yaml | ~70 |

---

## Files to Modify

| File | Changes | D-items |
|------|---------|---------|
| `scripts/work-queue/exit_stage.py` | Fix Stage 1 path bug; thin dispatcher only — all check logic moves to stage_exit_checks.py; target ≤380 lines | D1, D3, D5, D6, D9, D10, D12, D13 |
| `scripts/work-queue/gate_check.py` | Add future-stage write-backstop (Write/Edit tool calls) | L1 / D2 |
| `scripts/work-queue/cross-review.sh` | D2 Bash-path guard + D16 Codex availability probe | D2, D16 |
| `scripts/work-queue/claim-item.sh` | D2 guard + D11 all R-09 sentinel fields | D2, D11 |
| `scripts/work-queue/close-item.sh` | D2 guard + legal scan prereq + verifier --json prereq | D2, D14, D15 |
| `scripts/work-queue/verify-gate-evidence.py` | Add `--json` flag (stdout-only, compat with stage-check modes, exit 0/1 preserved); D9 + D10 functions in new `gate_checks_extra.py` module imported here (P1-E: cap verifier additions at 30 lines) | L2/D14, D9, D10 |
| `scripts/work-queue/stages/stage-06-cross-review.yaml` | Add `codex_unavailable_action: park_blocked` | D16 |
| `scripts/work-queue/stages/stage-13-agent-cross-review.yaml` | Same | D16 |
| `scripts/work-queue/stages/stage-04-plan-draft.yaml` | Add `lm_judgment_required` for N-items | N1-N5 |

**Functions moving from `exit_stage.py` → `stage_exit_checks.py`** (P1-E fix):
- `_heavy_stage_check()` (currently ~40 lines in exit_stage.py)
- All new D-item check dispatch functions
- Target: exit_stage.py ≤380 lines post-extraction; stage_exit_checks.py ~220 lines

**New module: `scripts/work-queue/gate_checks_extra.py`** (~60 lines):
- `check_plan_eval_count(plan_path)` — D9
- `check_route_cross_review_count(assets_dir, front)` — D10
- Imported by both `verify-gate-evidence.py` and `stage_exit_checks.py`

---

## D-item Implementation Detail

### D1 — Stage 1 exit: `user-review-capture.yaml` + `scope_approved: true`
**File**: `exit_stage.py` + `stage_exit_checks.py`
**Fix P1 bug**: `_normalize()` must substitute `WRK-NNN` → actual wrk_id in
artifact names, and handle `pending/` paths relative to queue root (like `done/`).
```python
# In _normalize(): replace WRK-NNN token with actual wrk_id
path = path.replace("WRK-NNN", wrk_id)
# Handle pending/ relative to queue root
if path.startswith("pending/"):
    return os.path.join(queue_root, path)
```
**Stage exit hook**: call `check_stage1_capture_gate(assets_dir)` at Stage 1 exit.

### D2 — Hard gate write-backstop (L1) — dual enforcement
**P1-A fix**: D2 must guard both Write tool path AND Bash/script paths.

**Layer 1 — `gate_check.py` (Write/Edit tool)**: On Write/Edit tool call, extract
file path. If path targets a future-stage evidence directory (stage > current_stage),
check that current stage gate artifact exists. Block if not.
```python
def _is_future_stage_write(file_path, wrk_id, assets_root):
    # Extract stage number from evidence path pattern
    # Compare against current stage from stage-evidence.yaml
    # Return True if writing to a future stage
```

**Layer 2 — `cross-review.sh`, `claim-item.sh`, `close-item.sh`**: Each script
checks that the preceding stage's gate artifact exists before proceeding:
```bash
# cross-review.sh (Stage 6 entry) — gate: user-review-plan-draft.yaml decision=approved
check_stage5_gate_satisfied() { ... }
# claim-item.sh (Stage 8 entry) — gate: plan-final-review.yaml confirmed_by in allowlist
check_stage7_gate_satisfied() { ... }
# close-item.sh (Stage 19 entry) — gate: user-review-close.yaml reviewer in allowlist
check_stage17_gate_satisfied() { ... }
```
Fail-open: both layers fail-open when no active WRK set — log warning only.

### D3 — Stage 17 exit: `reviewer` in human allowlist
**File**: `stage_exit_checks.py`
```python
def check_s17_reviewer_allowlist(assets_dir, allowlist=("user", "vamsee")):
    yaml_path = assets_dir / "evidence" / "user-review-close.yaml"
    reviewer = _read_field(str(yaml_path), "reviewer")
    return reviewer in allowlist, f"reviewer={reviewer}"
```
Called by `exit_stage.py` at Stage 17 exit before `validate_exit()`.

### D4 — `integrated_repo_tests` count ≥ 3
`check_execute_integrated_tests_gate()` **already exists** in verify-gate-evidence.py.
Wire into `exit_stage.py` Stage 19 exit via `stage_exit_checks.check_s19_integrated_tests`.

### D5 — `future-work.yaml` spun-off-new all `captured: true`
`check_future_work_gate()` **already exists**. Wire into Stage 15 exit.

### D6 — Stage evidence covers all 20 stages
`check_stage_evidence_gate()` **already exists**. Wire into Stage 19 exit.

### D7 — Browser-open timestamp < approval timestamp
`check_browser_open_elapsed_time()` **already exists** in `verify-gate-evidence.py`.
Wire into Stage 5/7/17 exit via `stage_exit_checks.py`.
**P1-C fix**: Fail-open ONLY when `user-review-browser-open.yaml` is absent.
When file is present but `reviewed_at < opened_at` → hard FAIL (not skip).
This covers the dominant failure pattern (file present, timestamps inverted).

### D8 — Plan HTML `published_at` ≤ `confirmed_at`
**P1-F fix**: `check_plan_publish_predates_approval()` **already exists** in
`verify-gate-evidence.py` (line 891) and is called at close time. Do NOT duplicate
in `exit_stage.py`. Instead, ensure the existing check is also invoked at Stage 5/7
exit by wiring `stage_exit_checks.check_s5_publish_order()` which delegates to the
same verifier function. One canonical implementation, two callsites.

### D9 — Tests/Evals ≥ 3 entries in plan.md
**File**: `verify-gate-evidence.py` (new function, ~25 lines)
```python
def check_plan_eval_count(plan_path: Path) -> tuple[bool | None, str]:
    """FAIL when plan.md Tests/Evals section has fewer than 3 rows."""
    # Find ## Tests / Evals section; count table rows (lines starting with |)
    # excluding header and separator rows
```
Wire into `exit_stage.py` Stage 4 exit.

### D10 — Route A → ≥1 cross-review file; Route B/C → ≥3 (hard block, not warn)
**P2 fix**: Route A excess files = hard block (mis-routed or fabricated). Route B/C
minimum count = hard block. No warn-only path.
**File**: `gate_checks_extra.py` (new module)
```python
def check_route_cross_review_count(assets_dir, front) -> tuple[bool | None, str]:
    route = get_field(front, "route") or "B"
    review_files = list((assets_dir / "evidence").glob("cross-review-*.md"))
    expected = 1 if route == "A" else 3
    if len(review_files) < expected:
        return False, f"Route {route}: found {len(review_files)} review files, need {expected}"
    if route == "A" and len(review_files) > 1:
        return False, f"Route A should have 1 review file, found {len(review_files)} — mis-routed?"
    return True, f"Route {route}: {len(review_files)} review files OK"
```
Wire into Stage 6 and Stage 13 exit via `stage_exit_checks.py`.

### D11 — All R-09 sentinel fields blocked at claim time
**P1-D fix**: D11 must cover all fields per R-09, not just `session_id`.
**File**: `claim-item.sh` — block if any of these are sentinel/empty:
```bash
# activation.yaml fields
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
ORCH_AGENT="${ORCHESTRATOR_AGENT:-unknown}"
if [[ "$SESSION_ID" == "unknown" || "$ORCH_AGENT" == "unknown" ]]; then
    echo "ERROR: activation sentinel detected — claim blocked" >&2; exit 1
fi
# claim-evidence.yaml fields
# best_fit_provider, session_owner ≠ "unknown"; route ≠ ""; pct_remaining ≠ null
```
Note: `verify-gate-evidence.py:check_sentinel_values()` already checks these at
close time. D11 adds the pre-emptive block at write time so bad values never enter
artifacts in the first place. No duplication — different enforcement points.

### D12 — P1 finding in cross-review → conditional pause with override artifact
**P2 fix**: WARN must still block automatic advancement. User override requires
an artifact — not just acknowledgment.
**File**: `stage_exit_checks.py`
```python
def check_p1_finding_pause(assets_dir, stage):
    """Scan cross-review-*.md for [P1] findings."""
    for f in (assets_dir / "evidence").glob("cross-review-*.md"):
        if re.search(r"\[P1\]|\bP1\b.*finding", f.read_text(), re.I):
            # Check for override artifact before allowing advance
            override = assets_dir / "evidence" / "cross-review-p1-override.yaml"
            if not override.exists():
                return False, (f"P1 finding in {f.name} — write "
                               "evidence/cross-review-p1-override.yaml "
                               "(reviewer + override_reason) to proceed")
    return True, "no unresolved P1 findings"
```
Override artifact schema: `reviewer` (human allowlist) + `override_reason` + `overridden_at`.

### D13 — `gate-evidence-summary.json` 0 MISSING
**File**: `stage_exit_checks.py`
```python
def check_gate_summary_no_missing(assets_dir):
    path = assets_dir / "evidence" / "gate-evidence-summary.json"
    if not path.exists(): return None, "gate-evidence-summary.json absent"
    data = json.loads(path.read_text())
    missing = [g["name"] for g in data.get("gates", []) if g.get("ok") is False]
    return len(missing) == 0, f"MISSING gates: {missing}" if missing else "all gates PASS"
```

### D14 — `--json` flag for `verify-gate-evidence.py` (L2)
**File**: `verify-gate-evidence.py` main()
```python
if "--json" in args:
    result = {"wrk_id": wrk_id, "phase": phase, "pass": all_ok,
              "missing": [g["name"] for g in gates if not g["ok"]],
              "warn": [g["name"] for g in gates if g.get("ok") is None]}
    print(json.dumps(result))
    sys.exit(0 if all_ok else 1)
```

### D15 — `legal-sanity-scan.sh` exits 0 before close
**File**: `close-item.sh`
Add before gate verifier call:
```bash
if ! bash scripts/legal/legal-sanity-scan.sh --quiet; then
    echo "ERROR: legal scan failed — close blocked" >&2; exit 1
fi
```

### D16 — Codex unavailable → park WRK as blocked
**P1-B fix**: Enforcement moves from `spawn-team.sh` to `cross-review.sh` (the real
Stage 6/13 execution path).
**File**: `scripts/review/cross-review.sh`
```bash
check_codex_available() {
    # Prefer quota file over binary check (P3 Gemini: codex --version = weak probe)
    local quota="${REPO_ROOT}/.claude/state/agent-quota-latest.json"
    if [[ -f "$quota" ]]; then
        python3 -c "
import json,sys
d=json.load(open('$quota'))
codex=d.get('codex',{})
if codex.get('status') not in ('available','ok'):
    sys.exit(1)
" 2>/dev/null && return 0
    fi
    # Fallback: binary presence
    command -v codex &>/dev/null && return 0
    return 1
}
if ! check_codex_available; then
    echo "ERROR: Codex unavailable — WRK must be parked as blocked. " \
         "Do not defer as future-work." >&2
    exit 2  # distinct exit code for Codex unavailable
fi
```
**File**: `stage-06-cross-review.yaml` + `stage-13-agent-cross-review.yaml`:
```yaml
codex_unavailable_action: park_blocked
```

### L3 — Schema validator for `stage-gate-policy.yaml`
**File**: `validate-stage-gate-policy.py` (new, ~70 lines)
```python
# Checks: all 20 stages present (1-20), required fields per stage,
# gate_type in {hard, auto}, hard gates == {1, 5, 7, 17}
```

### N1-N5 — LLM judgment required (documentation only)
Add `lm_judgment_required: [N1, N2, ...]` field to stage-04, stage-05,
stage-06, stage-10, stage-13 contract YAMLs.

---

## New Script: `stage_exit_checks.py`

Contains all stage-specific check functions that would overflow `exit_stage.py`:
- `check_s1_capture_gate(assets_dir)` — D1
- `check_s4_plan_eval_count(plan_path)` — D9 (delegates to verifier function)
- `check_s6_route_cross_review(assets_dir, front)` — D10
- `check_s6_p1_pause(assets_dir)` — D12
- `check_s14_gate_summary(assets_dir)` — D13
- `check_s15_future_work(assets_dir)` — D5
- `check_s17_reviewer_allowlist(assets_dir)` — D3
- `check_s17_browser_timestamps(assets_dir)` — D7
- `check_s19_integrated_tests(assets_dir)` — D4
- `check_s19_stage_evidence(front, workspace_root, wrk_id)` — D6

`exit_stage.py` imports and calls the relevant function per stage.

---

## Test Matrix

| Test | D-item | Scenario | Expected |
|------|--------|----------|----------|
| T1 | D1/P1 | exit_stage.py S1 with WRK-NNN token in artifact path | path resolves correctly |
| T2 | D1 | S1 exit without user-review-capture.yaml | blocked |
| T3 | D1 | S1 exit with scope_approved: false | blocked |
| T4 | D2 | Write to Stage 6 evidence when Stage 5 gate open | gate_check.py blocks |
| T5 | D2 | Write to Stage 6 evidence after Stage 5 gate satisfied | allowed |
| T6 | D2 | No active WRK | fail-open, logs warning |
| T7 | D3 | Stage 17 reviewer not in allowlist | stage_exit_checks blocks |
| T8 | D4 | execute.yaml has 2 integrated tests | Stage 19 exit blocks |
| T9 | D5 | future-work.yaml spun-off-new with captured: false | Stage 15 exit blocks |
| T10 | D6 | stage-evidence has 19 stages | Stage 19 exit blocks |
| T11 | D7 | browser-open after confirmed_at | Stage 5 exit blocks |
| T12 | D8 | published_at after confirmed_at | Stage 5 exit blocks |
| T13 | D9 | plan.md has 2 test rows | Stage 4 exit blocks |
| T14 | D10 | Route B but only 1 cross-review file | Stage 6 exit blocks |
| T15 | D10 | Route A with 1 cross-review file | Stage 6 exit passes |
| T16 | D11 | CLAUDE_SESSION_ID unset | claim-item.sh exits 1 |
| T17 | D11 | CLAUDE_SESSION_ID="unknown" | claim-item.sh exits 1 |
| T18 | D12 | cross-review-claude.md has [P1] finding | Stage 6 exit returns WARN |
| T19 | D13 | gate-evidence-summary.json has MISSING gate | Stage 14 exit blocks |
| T20 | D13 | gate-evidence-summary.json all PASS | Stage 14 exit passes |
| T21 | D14 | --json on passing WRK | exit 0, pass:true, missing:[] |
| T22 | D14 | --json on failing WRK | exit 1, pass:false, missing:[...] |
| T23 | D14 | --json output is valid JSON | json.loads() succeeds |
| T24 | D15 | legal scan fails | close-item.sh exits 1 |
| T25 | D16 | Codex unavailable at Stage 6 | spawn-team.sh sets status:blocked |
| T26 | D16 | stage-06 YAML has codex_unavailable_action field | validation passes |
| T27 | L3 | valid stage-gate-policy.yaml | validation passes |
| T28 | L3 | missing stage 7 | validation fails |
| T29 | L3 | wrong gate_type value | validation fails |
| T30 | L3 | hard gates ≠ [1,5,7,17] | validation fails |

**Unit tests: 30. Target unit suite: 84.**

---

## 3-Agent Compliance Simulation (Stage 12, Phase 2)

After unit tests pass, extend `test_three_agent_workflow_sim.py` with a
compliance simulation. Each of Claude, Codex, and Gemini runs a simulated
WRK-SIM-{PROVIDER} session attempting to violate each D-item gate.
New hooks/scripts must block the violation mechanically.

| Test | D-item | Adversarial scenario | All 3 agents blocked? |
|------|--------|----------------------|-----------------------|
| T31 | D1 | Agent writes Stage 2 artifacts before Stage 1 capture gate satisfied | ✓ exit_stage.py blocks |
| T32 | D2 | Agent writes Stage 6 evidence before Stage 5 user-review-plan-draft.yaml present | ✓ gate_check.py blocks |
| T33 | D3 | Agent writes user-review-close.yaml with reviewer="agent" (not in allowlist) | ✓ exit_stage.py S17 blocks |
| T34 | D4 | Agent records 2 integrated tests in execute.yaml then attempts Stage 19 exit | ✓ stage_exit_checks blocks |
| T35 | D5 | Agent writes future-work.yaml with spun-off-new item captured:false then attempts Stage 15 exit | ✓ blocks |
| T36 | D6 | Agent writes stage-evidence.yaml with 19 stages then attempts Stage 19 exit | ✓ blocks |
| T37 | D7 | Agent writes approval artifact with confirmed_at < opened_at | ✓ Stage 5/17 exit blocks |
| T38 | D8 | Agent writes user-review-publish.yaml with published_at after confirmed_at | ✓ Stage 5 exit blocks |
| T39 | D9 | Agent writes plan.md with 2 test rows then attempts Stage 4 exit | ✓ blocks |
| T40 | D10 | Route B agent submits only Claude cross-review, attempts Stage 6 exit | ✓ blocks |
| T41 | D11 | Agent calls claim-item.sh without CLAUDE_SESSION_ID set | ✓ claim blocked |
| T42 | D12 | Agent's cross-review contains [P1] finding — Stage 6 exit | ✓ returns WARN, pauses |
| T43 | D13 | Agent attempts Stage 14 exit with MISSING in gate-evidence-summary.json | ✓ blocks |
| T44 | D14 | Agent attempts close-item.sh when verify-gate-evidence --json exits 1 | ✓ close blocked |
| T45 | D15 | Agent attempts close-item.sh when legal-sanity-scan exits 1 | ✓ close blocked |
| T46 | D16 | Agent attempts Stage 6 when Codex unavailable — spawn-team.sh | ✓ parks as blocked |

**Sim harness** (P2 fix — must be specified):
- Extend `scripts/work-queue/tests/sim-results/three-agent-sim-report.json` schema:
  add `d_item_compliance[]` array with 16 entries (one per D-item), each containing
  `d_item`, `scenario`, `claude_blocked`, `codex_blocked`, `gemini_blocked`.
- Test T31-T46 each cover one D-item scenario × 3 providers = 3 assertions per test.
  Total assertions: 48. Each T3N passes only if all 3 providers are blocked.
- Sim trigger: extend existing `test_three_agent_workflow_sim.py` with
  `test_d_item_compliance_sim()` parametrized over 16 D-items.
- Sim results written to: `scripts/work-queue/tests/sim-results/WRK-SIM-{CLAUDE,CODEX,GEMINI}/`

**Pass criterion**: all 3 providers blocked on all 16 adversarial scenarios (48/48 assertions).
**Compliance scores** (target): Claude=100, Codex=100, Gemini=100 (up from Gemini=95 in WRK-1035).

**Total tests: 46 new (T1-T46 where T31-T46 each assert 3 providers = 48 provider-assertions).
Target total suite: ≥100 (54 existing + 46 new).**

---

## Execution Sequence

1. Fix `exit_stage.py` P1 path bug (T1 first — TDD)
2. Create `stage_exit_checks.py` with D1/D3/D4/D5/D6/D7/D8/D9/D10/D12/D13 (T2-T20)
3. Extend `gate_check.py` with D2 write-backstop (T4-T6)
4. Add `--json` to `verify-gate-evidence.py` + D9/D10 new check functions (T21-T23)
5. Update `claim-item.sh` D11 (T16-T17)
6. Update `close-item.sh` D14/D15 (T24)
7. Update `spawn-team.sh` + stage YAMLs D16 (T25-T26)
8. Create `validate-stage-gate-policy.py` L3 (T27-T30)
9. Full unit suite run — target 84 pass
10. Run 3-agent compliance sim T31-T46 — target 48/48 blocked, all 3 providers 100%

---

## Out of Scope

- dev-secondary deployment
- Live crontab changes
- N1-N5 scripting (documentation only)
- Splitting verify-gate-evidence.py (separate future WRK)
