# WRK-1009 Cross-Review — Gemini

**Date**: 2026-03-10
**Reviewer**: Gemini (plan_gemini.md output)
**Stage**: 6 — Plan Cross-Review
**Verdict**: APPROVE (reliability focus)

## Review

*(Derived from plan_gemini.md, "Reliability Focus" stance)*

### Phase 0 — Robustness Additions (P3)

- Script-candidate scan should emit **both** `specs/skills/script-conversion-candidates.md`
  (human-readable) and `.claude/state/skill-script-candidates/<UTC-date>.json`
  (machine-readable). Same-day runs should replace, not append.
- The 3-way classifier output (`candidate/not_candidate/needs_human_review`) should include
  the matched criterion that drove the classification for auditability.

### Phase 1 — Eval YAML Precision (P3)

Eval YAML declarations should list **exact markers/sections** expected in SKILL.md rather
than vague prose assertions. For example:
```yaml
required_sections:
  - "## Canonical 20-Stage Lifecycle"
  - "## Stage Contracts"
required_commands:
  - "/work add"
  - "/work run"
```
This makes eval checks deterministic and script-runnable without LLM judgment.

JSONL records must include `run_id` (UUID or timestamp-based) for result correlation
across multiple nightly runs. **(P3)**

### Phase 2 — Curation Reliability (P3)

- Cron step 4b must be clearly logged with a step name (e.g., `[skill-curation]`) so
  comprehensive-learning logs are grep-able for integration tests.
- All state writes: temp-file + rename (already captured from Codex review).

### Phase 3 — Graceful Degradation (P3)

`skill-evals.sh` section for /today must:
1. Exit 0 even when no nightly artifact exists
2. Print a human-readable notice ("No skill eval report yet — run nightly cron to generate")
3. Never block /today on first-day or cron-skip days

## Summary

| Finding | Severity | Status |
|---------|----------|--------|
| Script scan: both md+json outputs | P3 | ✓ in plan |
| Eval YAML: exact marker declarations | P3 | → incorporate Phase 1 |
| JSONL: run_id field | P3 | → incorporate |
| Step 4b: logged with step name | P3 | → incorporate |
| /today: graceful degradation | P3 | → incorporate Phase 3 |

**APPROVE — All findings are P3 (implementation-time). No blocking issues.**
