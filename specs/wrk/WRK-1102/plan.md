# WRK-1102 Plan: fix(comprehensive-learning) — Repair Modular Chain

**Route**: C | **Priority**: HIGH | **Complexity**: medium
**Computer**: ace-linux-1 | **Target repo**: workspace-hub

---

## Mission

Repair seven defects in the `comprehensive-learning` nightly pipeline so it runs deterministically without LLM invocations, finds all signal files, and executes all phases.

---

## Resource Intelligence Summary

| File | Lines | Issue |
|------|-------|-------|
| `scripts/cron/comprehensive-learning-nightly.sh` | 77 | Line 73: `claude --skill` spawns LLM session |
| `scripts/cron/setup-cron.sh` | ~90 | Line 81: installs 3AM entry for non-existent wrapper |
| `scripts/analysis/session-analysis.sh` | 371 | Line 69: `${DATE}-*.jsonl` misses `${DATE}.jsonl` → 0 signals |
| `scripts/improve/lib/classify.sh` | 127 | Lines 6-126: `call_anthropic_api()` — REST API for deterministic routing |
| `scripts/analysis/comprehensive_learning_pipeline.py` | 637 | 237L over hard limit; phases 1/3/5-9 monolith |
| `scripts/learning/comprehensive-learning.sh` | 202 | Phase 2/3 call non-existent skill-internal paths |

Missing scripts (phases always SKIP):
- `scripts/analysis/daily-reflect.sh` (Phase 2)
- `scripts/analysis/knowledge-capture.sh` (Phase 3)
- `scripts/analysis/ingest-codex-sessions.sh` (Fix 6)

Note: Phase 4 `scripts/improve/improve.sh` EXISTS — no wrapper needed.

---

## Implementation Plan

### Fix 1 — Signal naming mismatch (15 min, no TDD)

**File**: `scripts/analysis/session-analysis.sh` line 69

```bash
# Before:
find "$SIGNALS_DIR" -name "${ANALYSIS_DATE}-*.jsonl" -print0 2>/dev/null || true
# After (OR-glob to match both formats):
find "$SIGNALS_DIR" \( -name "${ANALYSIS_DATE}-*.jsonl" -o -name "${ANALYSIS_DATE}.jsonl" \) -print0 2>/dev/null || true
```

Verify: run `bash scripts/analysis/session-analysis.sh` → `N_SESSIONS > 0`

**TDD**: `tests/session-analysis/test_signal_file_detection.bats` (write first)

---

### Fix 2 — Remove duplicate 3AM cron (5 min, no TDD)

**Files**: `scripts/cron/setup-cron.sh` line 81, `scripts/cron/crontab-template.sh` line 30

Remove the `session-analysis-nightly.sh` 3AM cron entry. The wrapper doesn't exist and Phase 1 already runs at 2AM inside comprehensive-learning.sh.

After editing: `bash scripts/cron/setup-cron.sh` to reinstall clean crontab.

---

### Fix 3 — Replace `claude --skill` with direct script call (5 min, no TDD)

**File**: `scripts/cron/comprehensive-learning-nightly.sh` line 73

```bash
# Before:
claude --skill comprehensive-learning || _nightly_exit=$?
# After:
bash scripts/learning/comprehensive-learning.sh || _nightly_exit=$?
```

---

### Fix 7 — Replace `call_anthropic_api()` in classify.sh (medium, TDD first)

**File**: `scripts/improve/lib/classify.sh`

Delete lines 6–61 (`call_anthropic_api` function). Rewrite `phase_classify()` (lines 63–126) as pure shell router:

```bash
phase_classify() {
    local merged="$1"
    while IFS= read -r line; do
        event=$(echo "$line" | jq -r '.event // empty')
        case "$event" in
            session_tool_summary) route_to_memory "$line" ;;
            skill_invoked)        route_to_skill_scores "$line" ;;
            drift_counts)         route_to_rules "$line" ;;
            stage_exit)           route_to_memory "$line" ;;
            context_reset)        route_to_memory "$line" ;;
            *)                    true ;;
        esac
    done < "$merged"
}
```

Add stub `route_to_memory()`, `route_to_skill_scores()`, `route_to_rules()` functions that append formatted entries to their target files.

Remove `curl` and OAuth credential dependency entirely.

---

### Fix 6 — Extend Phase 1 signals (small, TDD first)

**Create**: `scripts/analysis/ingest-codex-sessions.sh` (<60 lines)

Reads `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`, converts entries to signal format `{"event":"codex_session","date":"...","turns":N}`, writes to `state/session-signals/YYYY-MM-DD.jsonl`.

Call site: add pre-Phase-1 step in `scripts/learning/comprehensive-learning.sh`.

**TDD**: `tests/session-analysis/test_stage_exit_signal.bats`

---

### Fix 4 — Create missing phase scripts (medium, TDD first)

**TDD**: `tests/session-analysis/test_phase_scripts_exist.bats` (write first)

#### `scripts/analysis/daily-reflect.sh` (<100 lines)
- Summarise yesterday's git commits across all repos
- Write to `state/reflect-history/YYYY-MM-DD.md`
- Call: `git log --since=yesterday --oneline` per repo

#### `scripts/analysis/knowledge-capture.sh` (<100 lines)
- Read signal files from `state/session-signals/YYYY-MM-DD.jsonl`
- Extract new domain facts (WRK patterns, tool usage)
- Append to `state/learned-patterns.json`

Update `scripts/learning/comprehensive-learning.sh`:
- Line 155: point Phase 2 to `scripts/analysis/daily-reflect.sh`
- Line 167: point Phase 3 to `scripts/analysis/knowledge-capture.sh`
- Line 182: verify Phase 4 already points to `scripts/improve/improve.sh` (correct)

---

### Fix 5 — Split pipeline.py into per-phase modules (medium, TDD first)

**TDD**: `tests/session-analysis/test_pipeline_modules.py` (write first)

Extract from `comprehensive_learning_pipeline.py`:

| New file | Source function | Approx lines |
|----------|----------------|--------------|
| `scripts/analysis/pipeline_utils.py` | helpers (lines 1-128) | ~130 |
| `scripts/analysis/phase5_correction_trends.py` | `phase_5_correction_trend_analysis` | ~130 |
| `scripts/analysis/phase6_wrk_feedback.py` | `phase_6_wrk_feedback_loop` | ~50 |
| `scripts/analysis/phase7_action_candidates.py` | `phase_7_action_candidates` | ~160 |
| `scripts/analysis/phase8_report_review.py` | `phase_8_report_review` | ~40 |
| `scripts/analysis/phase9_coverage_audit.py` | `phase_9_skill_coverage_audit` | ~25 |

`pipeline.py` becomes a shim that imports and delegates to each module.

Update `comprehensive-learning.sh` `run_py_phase()` to call each module directly.

---

## Implementation Order

1. Fix 1 + Fix 2 + Fix 3 (tiny, verify manually)
2. Fix 7 (eliminates nightly API cost; write tests first)
3. Fix 6 (small signal extension)
4. Fix 4 (phase scripts, one at a time)
5. Fix 5 (highest refactor risk, last)

---

## Test Strategy

| Test file | Fix | Type |
|-----------|-----|------|
| `tests/session-analysis/test_signal_file_detection.bats` | 1 | bats |
| `tests/session-analysis/test_phase_scripts_exist.bats` | 4 | bats |
| `tests/session-analysis/test_pipeline_modules.py` | 5 | pytest |
| `tests/session-analysis/test_stage_exit_signal.bats` | 6 | bats |

Write each test before the corresponding fix. All tests must pass before marking fix done.

---

## Acceptance Criteria

- [ ] `session-analysis.sh` finds ≥1 signal file (`N_SESSIONS > 0`)
- [ ] 3AM cron entry removed; `nightly-cron.sh` calls script directly
- [ ] Phases 2, 3, 4 show `DONE` (not `SKIPPED`) in learning report
- [ ] `classify.sh` has no `call_anthropic_api()`; routes by `event` type
- [ ] Nightly pipeline makes zero LLM invocations
- [ ] pipeline.py split; each phase callable standalone
- [ ] `stage_exit` events appear in daily signal file
- [ ] Codex sessions ingested via `ingest-codex-sessions.sh`
- [ ] Absorbed WRKs (636, 1018, 1025) archived with cross-ref to WRK-1102

---

## Non-Goals

- WRK-635 (historical session scanner)
- Semantic/LLM gap analysis
- acma-ansys05 Codex ingestion
