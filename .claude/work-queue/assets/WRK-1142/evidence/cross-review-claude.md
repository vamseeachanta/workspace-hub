# Cross-Review: WRK-1142 — Claude

## Verdict: APPROVE

### Pseudocode Review
- [PASS] Phase 1 (start_stage.py patch): `_load_stage_micro_skill(stage, repo_root)` is clear;
  glob pattern correct; graceful fallback for missing file.
- [PASS] Phase 2 (migrate-stage-rules.py): extraction by heading pattern is deterministic.
- [PASS] ACs are specific and testable; tests cover happy + edge + error paths.

### Findings

**P2 — stage-04 and stage-10 rules should be the first items in the checklist**
The scripts-over-LLM rule should appear at checklist position 0 (before EnterPlanMode/TDD),
not appended at the end, so agents cannot proceed without seeing it.

**P2 — start_stage.py print position**
The micro-skill content should be printed AFTER the stage banner (not inside the resume block
which is conditional on checkpoint presence). Every stage entry should show the micro-skill,
not just resuming sessions.

**P3 — migrate-stage-rules.py is optional if micro-skill edits are small**
All micro-skills are already ≥5 lines. The actual migrations (stage-04, stage-10, and
SKILL.md trimming) are targeted edits. The script is still worth writing for the 25% rule,
but could be scoped to a one-pass extraction rather than a full interactive tool.
