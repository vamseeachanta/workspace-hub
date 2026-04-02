# Skill Promotion Pipeline Audit

**Issue:** #1426 — Accelerate correction-to-skill promotion pipeline (8% → 40% target)
**Date:** 2026-04-01 (updated with correction data discovery)
**Auditor:** Claude (automated)

## Current State

### Correction Capture (ACTIVE — discovered post-initial-audit)

The `capture-corrections.sh` PostToolUse hook has been capturing corrections since
2026-01-21. Data lives in `.claude/state/corrections/` (NOT in `session-signals/`).

| Metric | Count |
|--------|-------|
| Total corrections captured | 8,965 |
| Unique files corrected | 3,127 |
| Files with 10+ corrections | 122 |
| Files with 5+ corrections | 418 |
| Capture period | Jan 21 – Apr 1, 2026 |
| Data size | 17 MB |

**Monthly trend:** Jan: 559, Feb: 2,935, Mar: 5,456, Apr: 15 (partial)

### Skills Inventory

| Metric | Count |
|--------|-------|
| Total SKILL.md files (including archive) | 2,734 |
| Active SKILL.md files (excluding `_archive/`) | 568 |
| Skill-related commits since 2026-01-01 | 424 |
| Skills with 5+ corrections (needing update) | 10 |

### Diagnosis (Revised)

**The correction capture pipeline EXISTS and is active.** The missing link is
the **candidate identification → promotion** pipeline. Corrections are captured
but never analyzed for promotion opportunities.

The `session-signals/correction_events[]` field is still empty — corrections go
to a separate data store. This is a data integration gap, not a capture gap.

## Gap Analysis (Revised)

```
Correction happens in session
        ↓ (CAPTURED ✓)
.claude/state/corrections/ (8,965 records, 17MB)
        ↓ (MISSING: candidate identification)
Skill promotion candidates: not generated
        ↓ (MISSING: promotion workflow)
Skills created: only via manual agent effort
```

### Top Correction Hotspots (Promotion Candidates)

| Corrections | Days | File |
|------------|------|------|
| 97 | 28 | MEMORY.md |
| 93 | 7 | scripts/work-queue/generate-html-review.py |
| 66 | 9 | scripts/work-queue/whats-next.sh |
| 50 | 6 | scripts/work-queue/verify-gate-evidence.py |
| 48 | 2 | digitalmodel wall_thickness_mt_report.py |

### Skills Needing Update (Most-Corrected)

| Corrections | Days | Skill |
|------------|------|-------|
| 50 | 15 | coordination/workspace/work-queue |
| 38 | 4 | workspace-hub/comprehensive-learning |
| 38 | 7 | workspace-hub/work-queue-workflow |
| 23 | 5 | workspace-hub/workstations |
| 23 | 5 | workspace-hub/workflow-html |

### What's Now Available

1. **Correction capture** ✓ — `capture-corrections.sh` hook (active since Jan 2026)
2. **Candidate identification** ✓ — `scripts/enforcement/correction-to-skill-candidates.sh` (new)
3. **Signal-to-candidate pipeline** — MISSING: automated periodic analysis
4. **Candidate-to-skill promotion** — MISSING: workflow to draft SKILL.md from candidates
5. **Feedback loop** — MISSING: track if promoted skills reduce correction frequency

## Recommendations to Hit 40%

### Phase 1: Instrument Correction Capture (Week 1-2)

1. **Add correction detection to session emitter.** Pattern-match for:
   - User says "no", "don't", "stop", "wrong" followed by a correction
   - Explicit "remember this/that", "always do X", "never do Y"
   - "Use X not Y" preference statements
   - Agent self-corrections after errors
2. **Schema already exists** — `correction_events` array in `session_end` is ready. Just populate it with `{type, text, context}` objects.

### Phase 2: Build Candidate Queue (Week 2-3)

3. **Create `.claude/state/skill-candidates/` directory.** Each candidate is a JSON file with:
   - Source correction(s) (with timestamps)
   - Proposed skill name
   - Draft content
   - Status: `candidate` → `reviewed` → `promoted` | `rejected`
4. **Frequency analysis.** Flag corrections that appear 2+ times across sessions as high-priority candidates.

### Phase 3: Promotion Workflow (Week 3-4)

5. **Add a `/gsd:promote-skills` command** that:
   - Reads the candidate queue
   - Drafts SKILL.md files for high-frequency candidates
   - Presents them for review
   - Commits promoted skills
6. **Weekly cron job** to scan recent session signals and generate promotion candidates.

### Phase 4: Measure & Iterate (Ongoing)

7. **Track metrics:**
   - Corrections captured per session
   - Candidates generated per week
   - Promotion rate (candidates → skills)
   - Recurrence rate (same correction appearing after skill exists = skill failure)
8. **Target: 40% of captured corrections become skills within 7 days.**

## Projected Impact

| Phase | Promotion Rate | Timeline |
|-------|---------------|----------|
| Current (no pipeline) | 0% | — |
| Phase 1 (capture only) | 0% (baseline established) | Week 2 |
| Phase 2 (candidate queue) | 10-15% | Week 3 |
| Phase 3 (promotion workflow) | 25-35% | Week 4 |
| Phase 4 (automated + cron) | 40%+ | Week 6 |

## Summary

The 8% baseline cited in the issue cannot be verified — the instrumentation does not exist. The actual rate is 0% because corrections are not captured. The schema is ready; the work is in wiring the detection, building the candidate queue, and creating the promotion workflow. Four phases over ~6 weeks can reach the 40% target.
