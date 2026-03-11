# WRK-1102 Cross-Review Package — Phase 1 (Plan)

## Codex Verdict: REQUEST_CHANGES

### P1 Issues (must fix before Stage 7)

**Issue 1 — Fix 6 stage_exit source is wrong**
The plan proposes emitting `stage_exit` from the Stop hook, but the Stop hook doesn't know the stage. The authoritative source is `exit_stage.py` (line 334) via `log-action.sh` (line 15). Fix: emit JSONL signal alongside the audit write in `exit_stage.py`, or add an ingester from `logs/audit/agent-actions-*.jsonl` into Phase 1.

**Issue 2 — Fix 4 missing call-site updates**
Creating `daily-reflect.sh` and `knowledge-capture.sh` is insufficient — `comprehensive-learning.sh` lines 151/164 still call non-existent skill-local paths. Plan must explicitly include rewriting those call sites.

### P2 Issues (should fix)

**Issue 3 — Fix 7 apply.sh dependency**
`scripts/improve/lib/apply.sh:53` sources `classify.sh` and calls `call_anthropic_api()` when `IMPROVE_API_ENHANCE=true`. Deleting the function without handling this leaves a broken code path. Fix: remove `IMPROVE_API_ENHANCE` from the nightly path or replace with deterministic fallback in `apply.sh`.

**Issue 4 — route_to_skill_scores() needs read-modify-write**
Append-only will corrupt `state/skill-scores.yaml` (loaded as structured YAML in pipeline.py line 383). This stub needs explicit read-modify-write behavior.

## Gemini Verdict: MINOR

**Issue A — Fix 4 JSON append corruption**
`state/learned-patterns.json` append would produce invalid JSON. Use `.jsonl` format or `jq` merge.

**Issue B — Fix 7 TDD gap**
No test listed for `classify.sh` routing logic. Add `tests/session-analysis/test_classify_routing.bats`.

**Issue C — Fix 7 jq malformed line handling**
Guard `jq` calls against malformed JSONL lines to avoid halting the while loop.

## Plan Amendments

| Issue | Amendment |
|-------|-----------|
| 1 | Fix 6: emit `stage_exit` from `exit_stage.py` or ingest `logs/audit/agent-actions-*.jsonl` |
| 2 | Fix 4: explicitly update comprehensive-learning.sh lines 151/164 to new script paths |
| 3 | Fix 7: also handle `apply.sh` — remove or replace `IMPROVE_API_ENHANCE` path |
| 4 | Fix 7: `route_to_skill_scores()` uses read-modify-write YAML (not append) |
| A | Fix 4: `state/learned-patterns.jsonl` (jsonl, not json) |
| B | Add `tests/session-analysis/test_classify_routing.bats` to TDD strategy |
| C | Add `|| true` guard on jq calls in phase_classify() |

## Resolution

All P1 issues addressed by plan amendment. P2 issues addressed. Codex: APPROVE after amendments.
