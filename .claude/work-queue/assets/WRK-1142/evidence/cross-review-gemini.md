# Cross-Review: WRK-1142 — Gemini

## Verdict: APPROVE

### Pseudocode Review
- [PASS] `_load_stage_micro_skill` is clean; glob + read pattern is idiomatic Python.
- [PASS] migrate-stage-rules.py scope is clear enough for implementation.
- [PASS] Test matrix covers happy, edge, and error paths.

### Findings

**P3 — migrate-stage-rules.py error handling**
Include error handling for cases where a stage section is missing or malformed in SKILL.md.
Resolution: wrap extraction in try/except; print warning and skip malformed sections.

**P3 — micro-skill print position in start_stage.py**
Print stage micro-skill content unconditionally at stage entry, not only inside the resume
block (which requires a checkpoint). Every stage entry should show rules.
Resolution: call `_load_stage_micro_skill` in `route_stage()` before the invocation switch.

### Questions for Author
- Is the `.claude/skills/` path in the pseudocode correct for this repository?
- Do all 20 micro-skill files already exist, or does step 3 include creating missing files?
  (Clarification: all 20 exist; step 3 is fleshing out content, not creation.)
