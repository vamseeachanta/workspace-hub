# Execution Monitoring Pack — Batch 1 (#2059, #2063, #2056)

> Date: 2026-04-09 | Use after all 3 implementation agents complete

---

## 1. Success Signal Checklist

### #2059 — Vessel Stability Tests
- [ ] Commit message matches: `feat(naval-arch): real vessel stability test cases for Sleipnir, Thialf, Balder (#2059)`
- [ ] Branch: `feat/2059-vessel-stability-tests`
- [ ] 3 vessels (Sleipnir, Thialf, Balder) produce non-trivial StabilityResult with GM > 0
- [ ] All new tests pass; no regressions (pre-existing `test_register_multiple_vessels` excluded)
- [ ] GitHub issue #2059 has a summary comment posted

### #2063 — Drilling Riser Adapter
- [ ] Commit message matches: `feat(drilling-riser): add worldenergydata adapter for riser components (#2063)`
- [ ] Branch: `feat/2063-drilling-riser-adapter`
- [ ] 6 new integration tests pass + ~37 existing drilling_riser tests pass
- [ ] Import works: `from digitalmodel.drilling_riser.adapter import normalize_riser_component_record`
- [ ] GitHub issue #2063 has a summary comment posted

### #2056 — Governance Phase 2 Hooks
- [ ] Commit message matches: `feat(governance): wire Phase 2 runtime enforcement into hooks (#2056)`
- [ ] Branch: `feat/2056-governance-phase2-hooks`
- [ ] Tool-call ceiling fires at 200 (not 500) with `additionalContext` JSON
- [ ] Error-loop-breaker detects 3x identical errors and outputs STOP context
- [ ] Pre-push review gate defaults strict (exit 1)
- [ ] GitHub issue #2056 has a summary comment posted

---

## 2. Files / Tests / Commits / Comments to Verify

### #2059
| Check | Command |
|-------|---------|
| Tests pass | `cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v` |
| No regressions | `cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v` |
| BALDER fixture | `grep -c BALDER_RECORD digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` |
| Docstrings | `grep -c "ASSUMED\|MEASURED" digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` |
| Commit exists | `git log --oneline --all --grep="#2059" | head -3` |
| GH comment | `gh issue view 2059 --comments --json comments -q '.comments[-1].body' | head -5` |

### #2063
| Check | Command |
|-------|---------|
| Tests pass | `cd digitalmodel && uv run pytest tests/drilling_riser/ -v` |
| Import smoke | `cd digitalmodel && uv run python -c "from digitalmodel.drilling_riser.adapter import normalize_riser_component_record; print('OK')"` |
| Unit conversions | `cd digitalmodel && uv run python -c "from digitalmodel.drilling_riser.adapter import normalize_riser_component_record as n; r=n({'COMPONENT_ID':'T','OD_IN':21.0,'WEIGHT_WATER_KIPS':3.8,'LENGTH_FT':75.0,'PRESSURE_RATING_PSI':5000.0}); print(f'od={r.get(\"od_mm\",0):.1f} wt={r.get(\"submerged_weight_kn\",0):.3f}')"` |
| No worldenergydata changes | `cd worldenergydata && git diff HEAD --name-only` |
| Submodule pointer | `git diff --name-only feat/2063-drilling-riser-adapter -- digitalmodel` |
| Commit exists | `git log --oneline --all --grep="#2063" | head -3` |
| GH comment | `gh issue view 2063 --comments --json comments -q '.comments[-1].body' | head -5` |

### #2056
| Check | Command |
|-------|---------|
| Governor tests | `uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v` |
| Hook tests | `uv run --no-project python -m pytest tests/hooks/ -v` |
| Shell tests | `bash scripts/enforcement/tests/test_require_review_on_push.sh` |
| Ceiling=200 | `grep 'TOOL_CALL_CEILING:-' .claude/hooks/tool-call-ceiling.sh` |
| Strict=1 | `grep 'REVIEW_GATE_STRICT:-' scripts/enforcement/require-review-on-push.sh` |
| Hook registered | `test -f .claude/hooks/error-loop-breaker.sh && echo PASS` |
| Governor STOP@200 | `uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200; echo "exit=$?"` |
| Governor STOP@3err | `uv run scripts/workflow/session_governor.py --check-limits --consecutive-errors 3; echo "exit=$?"` |
| Commit exists | `git log --oneline --all --grep="#2056" | head -3` |
| GH comment | `gh issue view 2056 --comments --json comments -q '.comments[-1].body' | head -5` |

---

## 3. 10-Minute Review Checklist

### #2059 (3 min)
1. `git log --oneline feat/2059-vessel-stability-tests..HEAD 2>/dev/null || git log --oneline -3 feat/2059-vessel-stability-tests` — single atomic commit
2. Run test suite command from section 2 — all green
3. Spot-check: GM values in [0.5, 50] m for all 3 vessels
4. Verify no files changed outside `digitalmodel/tests/naval_architecture/` (+ optional `ship_data.py`)

### #2063 (3 min)
1. `git log --oneline feat/2063-drilling-riser-adapter..HEAD 2>/dev/null || git log --oneline -3 feat/2063-drilling-riser-adapter` — 1-2 commits (adapter + submodule pointer)
2. Run test suite command from section 2 — all green
3. Spot-check: `adapter.py` uses `_KIPS_TO_KN = 4.44822` (not pint)
4. Verify no files changed in `worldenergydata/`

### #2056 (4 min)
1. `git log --oneline feat/2056-governance-phase2-hooks..HEAD 2>/dev/null || git log --oneline -3 feat/2056-governance-phase2-hooks` — single commit
2. Run all test commands from section 2 — all green
3. Spot-check: `governance-checkpoints.yaml` has `enforced: true`
4. Verify `.claude/settings.json` edits are minimal (2 env vars + 1 PostToolUse)
5. Verify `error-loop-breaker.sh` is executable: `test -x .claude/hooks/error-loop-breaker.sh`

---

## 4. Combined Closeout Checklist

- [ ] All 3 branches exist with correct commit messages
- [ ] All tests pass per section 2 (zero regressions)
- [ ] All 3 GitHub issues have summary comments posted
- [ ] No file overlap between branches: `comm -12 <(git diff --name-only main..feat/2059-vessel-stability-tests | sort) <(git diff --name-only main..feat/2063-drilling-riser-adapter | sort)` returns empty (repeat for all pairs)
- [ ] digitalmodel submodule pointer consistent if both #2059 and #2063 landed
- [ ] Cross-review dispatched per policy: Codex + Gemini for each issue
- [ ] Merge order: #2059 first, #2063 second (rebase submodule pointer), #2056 last
- [ ] After merge: `git log --oneline -6 main` shows 3 feature commits + pointer updates
- [ ] Labels updated: `status:plan-approved` removed, `status:done` applied to all 3 issues
- [ ] Close all 3 issues after merge confirmation

RECOMMENDATION: USE AFTER IMPLEMENTATION RUNS COMPLETE
