# Execution Pack: Production Decline Curve to Economics Cashflow Model

## 1. Issue Metadata

| Field          | Value |
|----------------|-------|
| Issue          | [#2054](https://github.com/vamseeachanta/workspace-hub/issues/2054) |
| Title          | feat(field-dev): add production decline curve to economics cashflow model |
| Labels         | enhancement, cat:engineering, domain:code-promotion, agent:claude |
| Parent epic    | #1858 (economics facade) — **CLOSED** |
| Related        | #1845 (production profiles) |
| Plan status    | **NOT APPROVED** — needs `status:plan-approved` label before implementation |
| Stage-1 source | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md` |
| Execution pack | 2026-04-09 |

---

## 2. Fresh Status Check (Since Stage-1 Dossier)

| Check | Stage-1 (2026-04-09) | Stage-2 Verification | Delta |
|-------|----------------------|----------------------|-------|
| `economics.py` line count | 693 | **693** | No change |
| `test_economics.py` line count | 583 | **590** (+7 lines) | Minor test additions, no decline curve tests added |
| `EconomicsInput` fields (L75-132) | No decline params | **Confirmed unchanged** | Still missing `decline_rate`, `decline_type`, `b_factor` |
| Hardcoded decline `_build_annual_cashflows()` L420-435 | Linear 60/40 plateau/decline | **Confirmed unchanged** | `prod_factor = 1.0 - 0.8 * frac_decline` still present |
| Hardcoded decline `build_economics_schedule()` L617-633 | Identical linear | **Confirmed unchanged** | Same duplicated logic |
| `reservoir_size_mmbbl` at L95 | Exists, unused | **Confirmed unused** | Still placeholder |
| `worldenergydata/.../decline.py` | `ArpsDeclineCurve` present | **Confirmed present** | Available if needed, but inline math recommended |
| Parent epic #1858 | Open | **CLOSED** | Epic completed; this issue remains as follow-on enhancement |
| Parallel work on economics.py | None detected | **None detected** | No new commits to this file |
| `status:plan-approved` label | Not applied | **Not applied** | BLOCKING — operator must apply before implementation |

**Staleness verdict**: Stage-1 dossier is **current**. Only delta is +7 test lines (unrelated to decline curves) and parent epic #1858 closure.

---

## 3. Minimal Plan-Review Packet

### 3.1 Scope

**1 production file + 1 test file. Zero submodule changes.**

| File | Change Type | Estimated Lines |
|------|------------|-----------------|
| `digitalmodel/src/digitalmodel/field_development/economics.py` | Add `DeclineType` enum, 3 fields on `EconomicsInput`, extract `_production_factors()` helper, update 2 functions | +60-80 LOC |
| `digitalmodel/tests/field_development/test_economics.py` | Add 4 test classes (validation, profiles, EUR, schedule) | +120 LOC |

### 3.2 Architecture Decision: Inline Arps Math

Use **pure inline Arps formulas** (3 one-liners) rather than importing `worldenergydata.production.forecast.decline.ArpsDeclineCurve`.

**Rationale** (from stage-1, re-validated):
- Economics module needs annual `prod_factor` values (0.0-1.0), not monthly bbl/day forecasts
- `ArpsDeclineCurve` is for fitting historical data; this use case generates synthetic forward profiles
- Avoids scipy/pandas dependency in the screening-level evaluator
- Formulas are trivial: `exp(-D*t)`, `(1+b*D*t)^(-1/b)`, `1/(1+D*t)`

### 3.3 Key Design Choices

| Decision | Choice | Alternative | Why |
|----------|--------|-------------|-----|
| Decline math source | Inline Arps formulas | Import `ArpsDeclineCurve` | Simpler, no new deps, different use case (forward vs. fit) |
| Duplication fix | Extract `_production_factors()` helper | Leave duplicated | Two identical 15-line blocks is a maintenance hazard |
| EUR parameterization | Default `recovery_factor=0.15` | Require user to specify | Typical offshore RF range 0.10-0.35; 0.15 is conservative |
| `b_factor` default | 0.5 for hyperbolic | Require explicit | Industry standard for offshore oil |
| Backward compat | No decline params = current linear model | Remove linear | Zero breaking changes for existing callers |

### 3.4 Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Missing `status:plan-approved` label | **BLOCKING** | Operator must apply label before implementation dispatch |
| EUR `reservoir_size_mmbbl` ambiguity (OOIP vs EUR?) | MEDIUM | Issue body says "EUR-based" — treat as OOIP with recovery factor, document assumption |
| Duplicate logic missed during update | LOW | `_production_factors()` extraction eliminates this class of bug |
| Test file grew +7 lines since dossier | NEGLIGIBLE | No structural conflict |

---

## 4. Issue Refinement Recommendations

The following refinements to issue #2054 would improve clarity for the implementing agent:

1. **Clarify `reservoir_size_mmbbl` semantics**: Is this OOIP (requiring a recovery factor) or EUR directly? Current issue body says "EUR-based decline curve parameterization" but the field name implies OOIP. Recommend adding: "When `reservoir_size_mmbbl` is provided, treat as OOIP and apply default RF=0.15 to derive EUR."

2. **Add acceptance criteria**: The issue body lists 4 requirements but no explicit acceptance criteria. Recommend adding:
   - `EconomicsInput` accepts `decline_type`, `decline_rate`, `b_factor` optional fields
   - Exponential, hyperbolic, harmonic decline types supported
   - Backward-compatible: omitting decline params reproduces current linear behavior
   - Production profile duplication eliminated via shared helper

3. **Note parent epic closure**: Epic #1858 is now CLOSED. This issue should be labeled as a follow-on enhancement, not a blocker for the epic.

4. **Add label `status:plan-review`**: Signal that a plan exists and is awaiting operator review.

---

## 5. Operator Command Pack

### 5.1 Label Management

```bash
# Add plan-review label (signals plan exists, awaiting review)
gh issue edit 2054 --add-label "status:plan-review"

# After operator reviews this execution pack, approve for implementation:
gh issue edit 2054 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### 5.2 Issue Body Refinement (Optional)

```bash
# Add clarification comment to issue
gh issue comment 2054 --body "$(cat <<'EOF'
## Plan Review Notes (Stage-2 Execution Pack)

**Plan location**: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md`

### Scope
- 1 file changed: `digitalmodel/src/digitalmodel/field_development/economics.py`
- 1 test file changed: `digitalmodel/tests/field_development/test_economics.py`
- Zero worldenergydata submodule changes
- Inline Arps math (3 one-liners), no new dependencies

### Design Decisions Needing Confirmation
1. `reservoir_size_mmbbl` treated as OOIP with default RF=0.15 — correct?
2. `b_factor` defaults to 0.5 for hyperbolic — acceptable?
3. Extract shared `_production_factors()` helper to eliminate duplication — approved?

### Acceptance Criteria
- [ ] `EconomicsInput` accepts `decline_type`, `decline_rate`, `b_factor`
- [ ] Exponential, hyperbolic, harmonic decline types work correctly
- [ ] No decline params = identical to pre-change linear behavior
- [ ] Production profile duplication eliminated
- [ ] All existing tests pass unchanged
EOF
)"
```

### 5.3 Implementation Dispatch (Run ONLY After `status:plan-approved`)

```bash
# Verify plan-approved label exists before dispatch
gh issue view 2054 --json labels --jq '.labels[].name' | grep -q "status:plan-approved" \
  && echo "APPROVED — safe to dispatch" \
  || echo "BLOCKED — not approved yet"
```

---

## 6. Self-Contained Future Implementation Prompt

The following prompt is ready to paste into a Claude Code session to implement #2054 after approval:

```
You are implementing GitHub issue #2054: feat(field-dev): add production decline curve to economics cashflow model.

## Context
- Primary file: digitalmodel/src/digitalmodel/field_development/economics.py (693 lines)
- Test file: digitalmodel/tests/field_development/test_economics.py (590 lines)
- Stage-1 dossier: docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md
- Stage-2 execution pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md
- Parent epic #1858 is CLOSED; this is a follow-on enhancement.

## Current State
- `_build_annual_cashflows()` (L420-435) and `build_economics_schedule()` (L617-633) contain
  identical hardcoded linear decline: 60% plateau then linear to 20%.
- `EconomicsInput` (L75-132) has `reservoir_size_mmbbl` (L95) but no decline parameters.
- `worldenergydata/src/worldenergydata/production/forecast/decline.py` has `ArpsDeclineCurve`
  but we use inline math instead (different use case: forward profiles vs historical fit).

## Implementation Steps (TDD)

### Step 1 — Add DeclineType enum (after imports, before EconomicsInput ~L60)
```python
class DeclineType(Enum):
    EXPONENTIAL = "exponential"
    HYPERBOLIC = "hyperbolic"
    HARMONIC = "harmonic"
```

### Step 2 — Add fields to EconomicsInput (after L102)
```python
    decline_type: Optional[str] = None   # "exponential" | "hyperbolic" | "harmonic"
    decline_rate: Optional[float] = None  # annual nominal decline rate (0, 1]
    b_factor: Optional[float] = None      # hyperbolic exponent, default 0.5
```

### Step 3 — Add __post_init__ validation (after L131)
- `decline_type` must be in DeclineType values if provided
- `decline_rate` must be in (0, 1] if provided
- `decline_type` without `decline_rate` raises ValueError
- `decline_rate` without `decline_type` defaults to exponential
- `b_factor` only valid with hyperbolic type

### Step 4 — Extract _production_factors() helper
```python
def _production_factors(
    field_life_years: int,
    plateau_fraction: float = 0.6,
    decline_type: Optional[str] = None,
    decline_rate: Optional[float] = None,
    b_factor: float = 0.5,
    reservoir_size_mmbbl: Optional[float] = None,
    production_capacity_bopd: Optional[float] = None,
) -> list[float]:
    """Return per-year production factors [0..n] where year 0 = 0.0 (pre-production).

    When decline_type/rate provided: uses Arps formulas.
    When neither provided: falls back to legacy linear (60% plateau, linear to 20%).
    When reservoir_size_mmbbl provided without decline_rate: derives rate from EUR.
    """
```

Arps formulas (t = years after plateau ends):
- Exponential: `prod_factor = exp(-D * t)`
- Hyperbolic: `prod_factor = (1 + b * D * t) ** (-1/b)`
- Harmonic: `prod_factor = 1 / (1 + D * t)`

### Step 5 — Wire _production_factors() into both callers
Replace L420-435 in `_build_annual_cashflows()` and L617-633 in `build_economics_schedule()`
with calls to the shared helper.

### Step 6 — EUR-based parameterization (optional path)
When `reservoir_size_mmbbl` provided without `decline_rate`:
- EUR = reservoir_size_mmbbl * recovery_factor (default RF=0.15)
- Derive `decline_rate` such that cumulative production over field life ≈ EUR
- For exponential: D = -ln(q_limit/qi) / t_decline

## Tests to Write (in test_economics.py)
1. **TestDeclineCurveInput**: 8 tests — validation of types, rates, combinations
2. **TestDeclineCurveProfiles**: 6 tests — shape monotonicity, type comparison, fallback
3. **TestEURDeclineParameterization**: 2 tests — reservoir_size constrains volume
4. **TestDeclineCurveSchedule**: 2 tests — schedule integration, fallback match

## Verification Commands
```bash
cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v
cd digitalmodel && uv run pytest tests/field_development/test_economics.py --cov=digitalmodel.field_development.economics --cov-report=term-missing
cd digitalmodel && uv run pytest tests/field_development/ -v
cd digitalmodel && uv run python -c "from digitalmodel.field_development.economics import EconomicsInput, DeclineType; print(list(DeclineType))"
```

## Commit
```bash
git add digitalmodel/src/digitalmodel/field_development/economics.py digitalmodel/tests/field_development/test_economics.py
git commit -m "feat(field-dev): add Arps decline curves to economics cashflow model (#2054)"
```

Post-commit: run cross-review per AGENTS.md policy, then comment on issue #2054 with implementation summary.
```

---

## 7. Morning Handoff

### For the operator (Vamsee):

**What happened overnight**: Stage-1 research dossier was produced for issue #2054. This stage-2 execution pack validates the dossier against current repo state and packages it for operator review.

**What's fresh**: All stage-1 findings confirmed current. economics.py is untouched (693 lines), no parallel work detected, worldenergydata backends still in place. Only delta: test file grew +7 lines (unrelated) and parent epic #1858 is now CLOSED.

**What you need to do**:
1. Review this execution pack (especially Section 3.3 design decisions and Section 4 refinements)
2. Decide on `reservoir_size_mmbbl` semantics (OOIP with RF=0.15, or direct EUR?)
3. Apply `status:plan-approved` label to issue #2054
4. Dispatch implementation using the prompt in Section 6

**Key file paths**:
- `digitalmodel/src/digitalmodel/field_development/economics.py` — primary implementation target (693 lines)
- `digitalmodel/tests/field_development/test_economics.py` — test target (590 lines)
- `worldenergydata/src/worldenergydata/production/forecast/decline.py` — upstream reference (read-only)
- `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-9-decline-curve-cashflows.md` — stage-1 dossier

**Estimated implementation effort**: ~60-80 LOC production + ~120 LOC tests = ~200 LOC total. Single-file change with zero external dependencies added.

---

## 8. Final Recommendation

**READY FOR PLAN REVIEW** — Issue #2054 is well-scoped with a validated stage-1 dossier, confirmed-current codebase state, and a self-contained implementation prompt. Apply `status:plan-review` now, then `status:plan-approved` after review to unblock implementation dispatch. No blockers beyond label approval.
