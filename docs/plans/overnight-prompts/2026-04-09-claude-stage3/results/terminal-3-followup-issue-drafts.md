# Terminal 3 — Follow-Up Issue Drafts from Stage-2 Execution Packs

Generated: 2026-04-09 (Stage 3, Terminal 3)
Source: 10 stage-2 execution packs at `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/`

---

## 1. Which Issues Need Follow-Up and Why

| Issue | Title (current) | Follow-Up Type | Reason |
|---|---|---|---|
| **#2053** | feat(field-dev): concept selection probability matrix… | **SPLIT** — extract remaining scope item 1 | 4/5 scope items done; `production_rate_bopd` field and correlation extraction is independent of the completed probability matrix + decision tree. Keeping it in #2053 delays closure of a 90%-done issue. |
| **#2055** | feat(field-dev): subsea cost benchmarking… | **REFINE** — add data prerequisite gate + scope reduction | Equipment-count data is completely absent from `subseaiq-scan-latest.json`. The stated dependency ("SubseaIQ scraping with equipment count fields") is unmet. Without refinement, an implementing agent blocks immediately or invents data. |
| **#2062** | feat(naval-arch): drilling rig fleet adapter — 2,210 rigs… | **REFINE** — correct title and scope expectations | "2,210 rigs" is misleading — only ~138 have geometry. No DRAFT_M column exists. Title and body must reflect realistic v1 throughput. |
| **#2057** | Session governance Phase 3: restore lost session infrastructure | **SPLIT** — extract cleanup reconciliation | All 4 skill deliverables are implemented, but 5 broken links, 0 smoke tests, duplicate skill files, and stale governance doc remain. These are pure cleanup — should be a separate chore issue so #2057 can close. |
| **#2056** | Session governance Phase 2: wire runtime enforcement… | **SPLIT** — extract threshold regression fix + stale docs | 3 of 4 gaps resolved, but a threshold regression (`5000` instead of `200`) in `governance-checkpoints.yaml:54` means the documented 200-call ceiling is NOT enforced. This is a bug, not a feature — should be tracked separately so #2056 can close cleanly. |

---

## 2. Draft Issue Titles

| # | New Issue Title | Parent | Type |
|---|---|---|---|
| A | `feat(field-dev): add production_rate_bopd to SubseaProject and extract rate correlations` | #2053 | Split |
| B | `fix(governance): restore 200-call ceiling threshold in governance-checkpoints.yaml` | #2056 | Split (bug fix) |
| C | `chore(governance): reconcile #2057 cleanup — broken links, smoke tests, duplicate skills` | #2057 | Split (cleanup) |
| D | `docs(governance): update REVIEW_GATE_BYPASS_POLICY.md to reflect strict default` | #2056 | Split (doc fix) |
| E | *(refinement only — no new issue)* #2055 body replacement | #2055 | Refine in-place |
| F | *(refinement only — no new issue)* #2062 title + body replacement | #2062 | Refine in-place |

---

## 3. Draft Issue Bodies

### Draft A — `feat(field-dev): add production_rate_bopd to SubseaProject and extract rate correlations`

```markdown
## Context

Follow-up to #2053 scope item 1. The `SubseaProject` dataclass in `benchmarks.py` currently
lacks a `production_rate_bopd` field. The `GoMField` dataclass in `subsea_bridge.py` has
`capacity_bopd` but there is no bridge between the two data models for production rate.

#2053 is otherwise complete — items 2-5 (probability matrix, decision tree, case validation,
concept_selection integration) are implemented and tested as of commit `77b47195`.

## Problem

The original #2053 scope asked for "concept_type + water_depth + production_rate correlations"
but the production_rate axis was never added. Without it, the probability matrix and decision
tree only operate on water_depth and reservoir_size dimensions.

## Scope

- [ ] Add `production_rate_bopd: Optional[float] = None` to `SubseaProject` dataclass
      (`digitalmodel/src/digitalmodel/field_development/benchmarks.py:59-75`)
- [ ] Update `load_projects()` to parse `production_rate_bopd` via `_opt_float()`
      (`benchmarks.py:130-141`)
- [ ] Implement `_extract_rate_correlations(projects) -> dict` mapping concept_type +
      water_depth + production_rate trends
      (`benchmarks.py`, new function after line ~570)
- [ ] Bridge `GoMField.capacity_bopd` to `SubseaProject.production_rate_bopd` in subsea_bridge
      if a bridge module exists; otherwise add mapping in `load_projects()`
- [ ] Add test class `TestProductionRateCorrelations` to `test_benchmarks.py` (~5 tests)
- [ ] Export new function from `digitalmodel/src/digitalmodel/field_development/__init__.py`

## Target Files

| File | Action | Current Lines |
|---|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Extend dataclass + add function | 572 |
| `digitalmodel/tests/field_development/test_benchmarks.py` | Add test class | 763 |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | Add export | 93 |
| `data/field-development/subseaiq-scan-latest.json` | Optionally backfill production_rate fields | 112 |

## Acceptance Criteria

- [ ] `SubseaProject` accepts `production_rate_bopd` kwarg without breaking existing callers
- [ ] `load_projects()` round-trips production_rate_bopd from JSON
- [ ] `_extract_rate_correlations()` returns a dict keyed by concept_type with mean/median
      production rates per water depth band
- [ ] All existing 27+ benchmark tests pass unchanged
- [ ] New tests pass (≥5 tests covering field presence, parsing, correlation output structure)
- [ ] No regressions in `concept_probability_matrix` or `predict_concept_type`

## Dependencies

- #2053 (probability matrix — DONE, commit `77b47195`)
- #1861 (scaffold — DONE)

## Labels

`enhancement`, `cat:engineering`, `agent:claude`
```

---

### Draft B — `fix(governance): restore 200-call ceiling threshold in governance-checkpoints.yaml`

```markdown
## Context

During Phase 2c implementation (commit `d4f46c770`), the tool-call ceiling threshold in
`governance-checkpoints.yaml` was changed from `200` to `5000`. This was likely accidental —
the same commit also flipped `enforced: true` and the review gate strict default.

## Bug Description

**File**: `scripts/workflow/governance-checkpoints.yaml`
**Line 54**: `threshold: 5000` (should be `200`)

### Impact Analysis

The session governor reads the threshold from YAML at runtime:
- **Below 160**: Hook fast-path (`FAST_PATH_CEILING=160` in `session-governor-check.sh:30`)
  allows the call — correct behavior
- **160–3999**: Governor evaluates but returns CONTINUE (threshold not reached) — **WRONG**,
  should PAUSE at 160 and STOP at 200
- **4000+**: Governor returns PAUSE — too late
- **5000+**: Governor returns STOP — far too late

The documented 200-call ceiling is effectively non-functional at the governor level. Only the
hook's hardcoded fast-path constant at 160 provides any partial coverage.

### Why Tests Don't Catch It

`tests/work-queue/test_session_governor.py` uses inline YAML fixtures with `threshold: 200`,
not the production YAML file. Tests pass because they test the correct value, but the
production config has the wrong value.

## Fix

One-line change:

```yaml
# Line 54 of scripts/workflow/governance-checkpoints.yaml
# BEFORE:
threshold: 5000
# AFTER:
threshold: 200
```

Plus one integration test that reads the production YAML:

```python
# In tests/work-queue/test_session_governor.py
def test_production_yaml_tool_call_ceiling_threshold(self):
    """Verify production YAML has correct 200-call ceiling (not 5000 regression)."""
    import yaml
    yaml_path = Path(__file__).parent.parent.parent / "scripts" / "workflow" / "governance-checkpoints.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    ceiling = next(c for c in data["checkpoints"] if c["id"] == "tool-call-ceiling")
    assert ceiling["threshold"] == 200, (
        f"Tool-call ceiling threshold is {ceiling['threshold']}, expected 200. "
        f"Regression from d4f46c770."
    )
```

## Target Files

| File | Change | Lines Affected |
|---|---|---|
| `scripts/workflow/governance-checkpoints.yaml` | Fix `threshold: 5000` → `200` | Line 54 (1 LOC) |
| `tests/work-queue/test_session_governor.py` | Add production YAML integration test | +10 LOC |

## Acceptance Criteria

- [ ] `governance-checkpoints.yaml` tool-call-ceiling threshold is `200`
- [ ] Governor returns STOP (exit 2) when tool-call count reaches 200:
      `uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200 --consecutive-errors 0`
- [ ] Governor returns CONTINUE (exit 0) at 150 tool calls
- [ ] New integration test reads production YAML and asserts `threshold == 200`
- [ ] All 55 existing governor tests still pass
- [ ] Hook fast-path constant (`FAST_PATH_CEILING=160`) is consistent with 200 ceiling (80%)

## Dependencies

- #2056 (parent — nearly complete; this is the remaining bug fix)
- #1839 (governance Phase 1 — DONE)

## Labels

`bug`, `priority:high`, `cat:ai-orchestration`, `agent:claude`
```

---

### Draft C — `chore(governance): reconcile #2057 cleanup — broken links, smoke tests, duplicate skills`

```markdown
## Context

Issue #2057 (Session Governance Phase 3) delivered all 4 skill files during overnight batch
(commits `e582d7e70`..`ef8e7826b`). However, several cleanup items remain that block clean
closure of #2057.

## Cleanup Items

### 1. Fix 5 Broken Internal Links (MEDIUM priority)

Files in `.claude/skills/_internal/` reference `../session-start-routine/SKILL.md` relative to
`_internal/meta/`, but the skill was created at `.claude/skills/coordination/session-start-routine/`.

| File | Line | Current (Broken) | Fix To |
|---|---|---|---|
| `.claude/skills/_internal/meta/repo-cleanup/SKILL.md` | ~51 | `../session-start-routine/SKILL.md` | `../../../coordination/session-start-routine/SKILL.md` |
| `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md` | ~42 | `../session-start-routine/SKILL.md` | `../../../coordination/session-start-routine/SKILL.md` |
| `.claude/skills/_internal/meta/module-based-refactor/SKILL.md` | ~141 | `../meta/session-start-routine/SKILL.md` | `../../coordination/session-start-routine/SKILL.md` |
| `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md` | ~177 | `../../meta/session-start-routine/SKILL.md` | `../../../coordination/session-start-routine/SKILL.md` |
| `.claude/skills/_internal/builders/skill-creator/SKILL.md` | ~128 | `../../meta/session-start-routine/SKILL.md` | `../../../coordination/session-start-routine/SKILL.md` |

**Verify line numbers with `grep -n session-start-routine <file>` before editing.**

### 2. Create 4 Smoke Tests (MEDIUM priority)

Create `tests/skills/` directory with:
- `test_session_start_routine_smoke.py` — assert skill exists at coordination path, has YAML
  frontmatter, body contains "Pre-flight"
- `test_session_corpus_audit_smoke.py` — assert skill exists, has frontmatter
- `test_comprehensive_learning_smoke.py` — assert wrapper exists, cron script exists
- `test_cross_review_policy_smoke.py` — assert skill exists, body references
  `AI_REVIEW_ROUTING_POLICY`

### 3. Update SESSION-GOVERNANCE.md (LOW priority)

Add #2057 section after existing Phase 3d content (~line 320) in
`docs/governance/SESSION-GOVERNANCE.md` documenting the 4 restored skills with paths and
line counts.

### 4. Reconcile Duplicate session-corpus-audit (LOW priority)

Two versions exist:
- `.claude/skills/workspace-hub/session-corpus-audit/SKILL.md` (434 lines, Hermes-authored,
  comprehensive analysis tool)
- `.claude/skills/coordination/session-corpus-audit/SKILL.md` (58 lines, overnight build,
  slim summary)

**Recommendation**: Keep workspace-hub version as canonical. Add a note to the coordination
version that it's a slim reference, or delete the coordination version.

## Target Files

| File | Action |
|---|---|
| `.claude/skills/_internal/meta/repo-cleanup/SKILL.md` | Fix link |
| `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md` | Fix link |
| `.claude/skills/_internal/meta/module-based-refactor/SKILL.md` | Fix link |
| `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md` | Fix link |
| `.claude/skills/_internal/builders/skill-creator/SKILL.md` | Fix link |
| `tests/skills/test_*_smoke.py` (4 files) | Create |
| `docs/governance/SESSION-GOVERNANCE.md` | Extend |
| `.claude/skills/coordination/session-corpus-audit/SKILL.md` | Reconcile or annotate |

## Acceptance Criteria

- [ ] `grep -rn 'session-start-routine' .claude/skills/_internal/` shows only valid paths
- [ ] All 4 smoke tests pass: `uv run pytest tests/skills/test_*_smoke.py -v`
- [ ] `grep -n '#2057' docs/governance/SESSION-GOVERNANCE.md` returns at least 1 match
- [ ] Duplicate session-corpus-audit decision documented (keep one, annotate or remove other)
- [ ] Existing tests still pass: `uv run pytest tests/work-queue/test_session_governor.py -v`

## Dependencies

- #2057 (parent — all 4 deliverables complete; this is cleanup tail)

## Labels

`chore`, `cat:ai-orchestration`, `agent:claude`
```

---

### Draft D — `docs(governance): update REVIEW_GATE_BYPASS_POLICY.md to reflect strict default`

```markdown
## Context

The pre-push review gate was changed to default-strict (`REVIEW_GATE_STRICT=1`) in
`require-review-on-push.sh:255` as part of #2056 Phase 2 work, but the bypass policy doc
was not updated to match.

## Problem

`docs/standards/REVIEW_GATE_BYPASS_POLICY.md:10` currently says:
> "Default interactive behavior may remain warning-based unless REVIEW_GATE_STRICT=1 is
> explicitly enabled."

This contradicts the current code which defaults to strict mode. The doc misleads operators
into thinking strict mode is opt-in when it is actually the default.

Additionally, `.claude/hooks/tool-call-ceiling.sh` is 59 lines of dead code (removed from
settings.json in Phase 2c) with a `CEILING="${TOOL_CALL_CEILING:-500}"` constant that
confuses readers who don't realize it's unwired.

## Fix

### REVIEW_GATE_BYPASS_POLICY.md

Line 10: Replace warning-based language with:
> "Default behavior is strict mode (blocks unreviewed pushes). Override with
> REVIEW_GATE_STRICT=0 for a single push."

Line 11: Replace:
> "Use strict mode for high-risk pushes..."
with:
> "Use REVIEW_GATE_STRICT=0 override only for the acceptable bypass cases listed below."

### tool-call-ceiling.sh (optional)

Add deprecation header at line 2:
```bash
# DEPRECATED: replaced by session-governor-check.sh (Phase 2c, #1839). Not wired in settings.json.
```

Or delete the file entirely (confirm no external references first with
`grep -rn tool-call-ceiling .claude/ scripts/`).

## Target Files

| File | Change |
|---|---|
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | Update default policy text (~3 LOC) |
| `.claude/hooks/tool-call-ceiling.sh` | Add DEPRECATED header or delete (optional) |

## Acceptance Criteria

- [ ] `REVIEW_GATE_BYPASS_POLICY.md` states strict mode is the default
- [ ] No references to "warning-based" as the default behavior in governance docs
- [ ] If `tool-call-ceiling.sh` kept: has DEPRECATED header
- [ ] If `tool-call-ceiling.sh` deleted: no references to it in settings.json or scripts

## Dependencies

- #2056 (parent — strict default already implemented in code)

## Labels

`documentation`, `cat:ai-orchestration`, `agent:claude`
```

---

### Draft E — #2055 Refinement (In-Place Body Replacement)

The existing refinement draft at `docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md` provides a paste-ready body. Key additions to the current issue body:

1. **Explicit data prerequisites section** — equipment counts must be backfilled before implementation can begin
2. **Architecture decision** — band-level aggregation (Option C) as v1 target; per-project join deferred to v2
3. **Corrected line counts** — `benchmarks.py` is now 572 lines (not 241), `test_benchmarks.py` is 763 lines (not 417)
4. **Label addition** — `status:needs-refinement` until data source decision is resolved

No new issue needed. Apply the body replacement from Section 1 of the refinement doc, then add `status:needs-refinement` label.

---

### Draft F — #2062 Refinement (Title + Body Replacement)

The existing refinement draft provides a paste-ready replacement. Key corrections:

1. **Title change**: "2,210 rigs into hull form validation" → "drillship and semi-sub hull form validation (~138 rigs with geometry)"
2. **Data limitations section** — explicitly states NO DRAFT_M column, 100% empty DISPLACEMENT_TONNES, jack-ups have zero geometry
3. **Deferred items list** — jack-up registration, displacement validation, CSV enrichment
4. **Corrected throughput** — ~138 registerable rigs, not 2,210

No new issue needed. Apply the title + body replacement from Section 2 of the refinement doc.

---

## 4. Suggested Labels

| Draft | Labels |
|---|---|
| A (production_rate split from #2053) | `enhancement`, `cat:engineering`, `agent:claude` |
| B (threshold regression fix from #2056) | `bug`, `priority:high`, `cat:ai-orchestration`, `agent:claude` |
| C (cleanup reconciliation from #2057) | `chore`, `cat:ai-orchestration`, `agent:claude` |
| D (bypass policy doc fix from #2056) | `documentation`, `cat:ai-orchestration`, `agent:claude` |
| E (#2055 in-place refinement) | Add `status:needs-refinement` |
| F (#2062 in-place refinement) | No label change needed |

---

## 5. Dependency Map

```
#1861 (scaffold) ─── DONE
  ├─► #2053 (probability matrix) ─── 90% DONE
  │     └─► Draft A (production_rate_bopd split)
  │           └─ No downstream dependents
  │
  └─► #2055 (subsea cost benchmarking) ─── BLOCKED on data
        └─ Draft E (in-place refinement: add data prerequisite gate)
              └─ Needs equipment-count backfill before unblocking

#1839 (governance Phase 1) ─── DONE
  ├─► #2056 (Phase 2 runtime hooks) ─── 90% DONE
  │     ├─► Draft B (threshold regression fix) ── URGENT, 1 LOC
  │     └─► Draft D (bypass policy doc update) ── LOW, 3 LOC
  │
  └─► #2057 (Phase 3 skill restoration) ─── DONE (skills committed)
        └─► Draft C (cleanup reconciliation) ── MEDIUM, link fixes + smoke tests

#1859 (vessel fleet adapter) ─── DONE
  └─► #2062 (drilling rig fleet adapter) ─── NOT STARTED
        └─ Draft F (in-place refinement: title/scope correction)
              └─ No downstream dependents
```

### Cross-Issue Interactions

- **Drafts B and D** are both children of #2056 — could be implemented in a single session.
  Draft B (bug fix) should land first since it's priority:high.
- **Draft C** is independent of all other drafts — can be dispatched in parallel.
- **Draft A** depends on #2053 being functionally complete (it is) but not on closure.
- **Drafts E and F** are refinements, not new issues — execute the `gh issue edit` commands
  from the refinement doc before dispatching implementation.

---

## 6. Final Recommendation: What to Split vs. Keep

### SPLIT — Create New Issues (3 drafts)

| Draft | Justification |
|---|---|
| **A** (production_rate_bopd from #2053) | Independent scope item. Keeping it in #2053 delays closure of a 90%-done issue with comprehensive tests. The remaining work is ~1 hour and cleanly separable. **Create as new issue.** |
| **B** (threshold regression from #2056) | This is a **bug** introduced by a prior commit, not remaining feature work. It deserves its own tracking because: (1) it's priority:high, (2) it's a 1-line fix that can be merged immediately, (3) the parent issue is otherwise ready to close. **Create as new issue.** |
| **C** (cleanup from #2057) | All 4 deliverables are done. The cleanup (broken links, smoke tests, doc update, duplicate reconciliation) is pure chore work that shouldn't block closing #2057 as "delivered." **Create as new issue.** |

### KEEP — Refine In-Place (2 refinements + 1 optional)

| Item | Justification |
|---|---|
| **E** (#2055 refinement) | The issue itself is correct in intent; it just needs a data prerequisite gate and scope reduction. Replacing the body in-place preserves the discussion thread and avoids issue number churn. **Refine in-place with `gh issue edit`.** |
| **F** (#2062 refinement) | Title and body corrections, not a scope change. The implementation approach is sound; the issue just overstates what's achievable with current data. **Refine in-place with `gh issue edit`.** |
| **D** (bypass policy doc from #2056) | This is a 3-line doc fix. Could be a new issue or bundled into the Draft B fix session. **Optional: either create as separate issue or include in Draft B implementation.** Recommendation: bundle with Draft B for efficiency. |

### Execution Priority Order

1. **Draft B** (threshold fix) — URGENT, 1 LOC bug fix, enables #2056 closure
2. **Draft F** (#2062 refinement) — Quick, unblocks plan-review for #2062
3. **Draft E** (#2055 refinement) — Quick, clarifies blockers for #2055
4. **Draft C** (#2057 cleanup) — Medium effort, enables #2057 closure
5. **Draft A** (#2053 production_rate) — Can be scheduled independently
6. **Draft D** (doc fix) — Bundle with Draft B or schedule independently

---

## Verification Checklist

- [x] At least 3 complete draft issue bodies produced (Drafts A, B, C, D = 4 complete bodies)
- [x] Concrete file paths included in every draft
- [x] Acceptance criteria included in every draft
- [x] Dependency map covers all 5 focus issues
- [x] Split vs. keep recommendation for each issue
- [x] No GitHub issues created
- [x] No production code mutated
