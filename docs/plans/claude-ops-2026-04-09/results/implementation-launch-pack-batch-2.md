# Implementation Launch Pack — Batch 2

> Issues: #2054, #2058, #2057
> Date: 2026-04-09
> Source execution packs:
> - `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md`
> - `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-5-architecture-patterns-execution-pack.md`
> - `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-6-governance-phase3-execution-pack.md`

---

## 1. Recommended Execution Order

| Priority | Issue | Title | Status | Confidence | Est. Delta |
|----------|-------|-------|--------|------------|------------|
| 1 | #2057 | Session governance Phase 3 cleanup tail | Retroactive approval + cleanup | Highest | ~5 link fixes + 4 smoke tests + 1 doc section |
| 2 | #2054 | Add production decline curve to economics cashflow model | Ready for plan-review -> plan-approved | High | ~60-80 LOC prod + ~120 LOC tests |
| 3 | #2058 | Subsea architecture patterns — flowline trends and layout classification | Ready for plan-review -> plan-approved | High | ~3 field additions + 1 new module + tests |

Rationale:
- `#2057` is the fastest closeable item: the four skill deliverables are already committed; only hygiene remains.
- `#2054` is well-scoped, single-domain, and isolated to `economics.py` + `test_economics.py`.
- `#2058` is also implementation-ready, but it adds a new module and touches both `digitalmodel/` and `worldenergydata/`, so it is slightly broader than `#2054`.

---

## 2. Parallel vs. Sequential: PARALLEL (3 concurrent Claude sessions)

### Decision: Run all three in parallel

Why parallel works:
- Zero file overlap at the source-file level
- Independent test surfaces
- Independent issue domains (governance, economics, subsea architecture)
- No shared hot files like `.claude/settings.json` or `digitalmodel/src/digitalmodel/naval_architecture/*`

Coordination note:
- `#2058` touches both `digitalmodel/` and `worldenergydata/` because of `normalize.py`; treat it as its own isolated terminal.
- `#2054` and `#2058` are both under field development, but they do not touch the same files.

---

## 3. Non-Overlapping Write Boundaries

### #2057 — Governance Phase 3 Cleanup
| File | Action |
|------|--------|
| `.claude/skills/_internal/meta/repo-cleanup/SKILL.md` | MODIFY link |
| `.claude/skills/_internal/meta/hidden-folder-audit/SKILL.md` | MODIFY link |
| `.claude/skills/_internal/meta/module-based-refactor/SKILL.md` | MODIFY link |
| `.claude/skills/operations/devtools/ai-tool-assessment/SKILL.md` | MODIFY link |
| `.claude/skills/_internal/builders/skill-creator/SKILL.md` | MODIFY link |
| `tests/skills/conftest.py` | CREATE or EXTEND |
| `tests/skills/test_session_start_routine_smoke.py` | CREATE |
| `tests/skills/test_session_corpus_audit_smoke.py` | CREATE |
| `tests/skills/test_comprehensive_learning_smoke.py` | CREATE |
| `tests/skills/test_cross_review_policy_smoke.py` | CREATE |
| `docs/governance/SESSION-GOVERNANCE.md` | MODIFY |

### #2054 — Decline Curve Cashflow Model
| File | Action |
|------|--------|
| `digitalmodel/src/digitalmodel/field_development/economics.py` | MODIFY |
| `digitalmodel/tests/field_development/test_economics.py` | MODIFY |

### #2058 — Subsea Architecture Patterns
| File | Action |
|------|--------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | MODIFY (3 dataclass fields + load_projects mapping only) |
| `digitalmodel/src/digitalmodel/field_development/architecture_patterns.py` | CREATE |
| `digitalmodel/tests/field_development/test_benchmarks.py` | MODIFY |
| `digitalmodel/tests/field_development/test_architecture_patterns.py` | CREATE |
| `worldenergydata/subseaiq/analytics/normalize.py` | MODIFY |
| normalize test file in worldenergydata | MODIFY or CREATE |

### Overlap Matrix

| | #2057 files | #2054 files | #2058 files |
|---|---|---|---|
| **#2057** | — | NONE | NONE |
| **#2054** | NONE | — | NONE |
| **#2058** | NONE | NONE | — |

Verdict: zero file overlap. Safe for full parallel Claude execution.

---

## 4. Pre-Dispatch Gate Checklist

### #2057
- Apply `status:plan-approved` retroactively before cleanup dispatch
- Note in the issue comment that core deliverables were already implemented and the remaining session is hygiene-only

### #2054
- Move issue from `status:plan-review` to `status:plan-approved`
- Decide whether `reservoir_size_mmbbl` should be treated as OOIP with recovery factor or as direct EUR
- Recommended default from the execution pack: proceed with the documented EUR-based helper path and record the assumption in the issue comment

### #2058
- Move issue from `status:plan-review` to `status:plan-approved`
- Approve the required file split: new `architecture_patterns.py` instead of growing `benchmarks.py`
- If `#2055` is still active elsewhere, ensure no one is concurrently editing `SubseaProject` fields

---

## 5. Session Assignment

| Terminal | Issue | Prompt source |
|----------|-------|---------------|
| T1 | #2057 | Section 6 in `terminal-6-governance-phase3-execution-pack.md` |
| T2 | #2054 | Section 6 in `terminal-9-decline-curve-execution-pack.md` |
| T3 | #2058 | Section 5 in `terminal-5-architecture-patterns-execution-pack.md` |

---

## 6. Operator Quick Commands

### Mark #2057 approved for cleanup
```bash
gh issue edit 2057 --add-label "status:plan-approved"
```

### Mark #2054 approved
```bash
gh issue edit 2054 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### Mark #2058 approved
```bash
gh issue edit 2058 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

## 7. Launch Instructions

Use the self-contained prompt text already embedded in each source execution pack:
- `#2057`: paste Section 6 from `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-6-governance-phase3-execution-pack.md`
- `#2054`: paste Section 6 from `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md`
- `#2058`: paste Section 5 from `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-5-architecture-patterns-execution-pack.md`

Recommended unattended Claude pattern:
```bash
PROMPT=$(python - <<'PY'
from pathlib import Path
text = Path('PATH/TO/PROMPT-SOURCE.md').read_text()
print(text)
PY
)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null
```

---

## 8. What You’ll Have After Batch 2

From T1 / #2057:
- broken internal skill links fixed
- smoke tests for restored session-governance skills
- governance doc updated for Phase 3e
- issue ready to close

From T2 / #2054:
- decline-curve support wired into the economics cashflow model
- validation tests for decline types and schedule integration
- backward-compatible fallback to the legacy linear decline path

From T3 / #2058:
- new subsea architecture analytics module
- extended normalized SubseaIQ fields for flowline diameter/material/layout
- test coverage for layout distributions, tieback segmentation, equipment stats, and flowline trends

---

## 9. Recommendation

Run this as the next Claude-only wave after the current Batch 1 work. If you want the safest first follow-up, start with `#2057` and `#2054`; add `#2058` once you are comfortable approving the mandatory file-split strategy.
