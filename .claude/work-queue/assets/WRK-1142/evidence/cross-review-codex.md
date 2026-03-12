# Cross-Review: WRK-1142 — Codex

## Verdict: MINOR

### Pseudocode Review
- [PASS] `_load_stage_micro_skill` glob pattern is correct; fallback message is clear.
- [PASS] ACs map to test entries cleanly.
- [PASS] migrate-stage-rules.py scope is reasonable.

### Findings

**MINOR — test placement**
Either place coverage in the existing `scripts/work-queue/tests/` suite or add explicit runner
wiring for `tests/scripts/test_stage_micro_skills.sh`. Currently underspecified.
Resolution: place test in `scripts/work-queue/tests/` to match existing test runner setup.

**MINOR — missing-micro-skill edge case clarity**
`start_stage.py` should tolerate a missing micro-skill file (warn, not crash). The plan
pseudocode shows a fallback message; make it explicit in the AC.
Resolution: update AC to state "prints warning, continues" when micro-skill not found.

**MINOR — migration helper scope**
The migration helper should extract only stage-numbered sections, NOT shared cross-cutting
rules (terminology, gate policy, banner rules) — those stay in SKILL.md.
Resolution: explicitly scope migrate-stage-rules.py to stage-numbered sections only.

### Questions for Author
- For the missing-micro-skill edge case, should `start_stage.py` also tolerate a missing
  stage contract, or only a missing micro-skill?
- Should the migration helper extract only stage-numbered sections, or also shared rules?
