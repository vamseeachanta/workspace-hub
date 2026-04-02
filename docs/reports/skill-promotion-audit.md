# Skill Promotion Pipeline Audit

**Issue:** #1426 — Accelerate correction-to-skill promotion pipeline (8% → 40% target)
**Date:** 2026-04-01
**Auditor:** Claude (automated)

## Current State

### Session Signals Data

| Metric | Count |
|--------|-------|
| Total session signal records | 208,630 |
| `session_end` records | 344 |
| `session_tool_summary` records | 7,299 |
| Records with `correction_events` populated | **0** |
| Records with `skill_invocations` populated | **0** |

### Skills Inventory

| Metric | Count |
|--------|-------|
| Total SKILL.md files (including archive) | 2,734 |
| Active SKILL.md files (excluding `_archive/`) | 568 |
| Skill-related commits since 2026-01-01 | 424 |

### Diagnosis

**The correction-to-skill promotion pipeline does not exist yet.**

The `session_end` signal schema defines `correction_events` and `skill_invocations` arrays, but they are **always empty** across all 344 session records. The pipeline has the right schema but zero instrumentation.

**Current promotion rate: 0%** (not 8% — there is no measurable baseline because corrections are not being captured).

Corrections are happening in sessions (users saying "remember this", "use uv run not python3", etc.) but the session-signal emitter does not detect or log them. Without capture, there is nothing to promote.

## Gap Analysis

```
Correction happens in session
        ↓ (NOT CAPTURED)
session-signals correction_events: [] (always empty)
        ↓ (NO PIPELINE)
Skill promotion: never triggered automatically
        ↓
Skills created: only via manual agent effort or explicit user request
```

### What's Missing

1. **Correction detection** — No NLP/pattern-matching in the session signal emitter to identify user corrections, preference statements, or "remember this" directives.
2. **Signal-to-candidate pipeline** — No process to review captured corrections and nominate them as skill candidates.
3. **Candidate-to-skill promotion** — No automated or semi-automated workflow to draft a SKILL.md from a correction pattern.
4. **Feedback loop** — No tracking of which corrections recur (indicating a missed skill opportunity).

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
