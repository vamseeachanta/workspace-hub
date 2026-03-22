# WRK-5110 AC-Test Matrix

| AC | Description | Test(s) | Result |
|----|-------------|---------|--------|
| AC1 | Orchestrator exists at `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md` | `test_skill_md_exists` | PASS |
| AC2 | SKILL.md is lean (<50 lines) and references detailed material | `test_skill_md_under_50_lines`, `test_skill_md_has_frontmatter` | PASS |
| AC3 | scripts/ contains orchestrator-owned helpers only; no stage-specific leakage | `test_no_stage_specific_scripts` | PASS |
| AC4 | references/ contains stage-gate-policy.md, transitions reference, canonical stage mapping | `test_stage_mapping_yaml_exists`, `test_stage_mapping_yaml_has_20_stages` | PASS |
| AC5 | references/hooks-schema.yaml defines the hooks.yaml schema | `test_hooks_schema_valid_yaml` | PASS |
| AC6 | hooks.yaml is valid and documents no-bypass constraints | `test_hooks_yaml_valid` | PASS |
| AC7 | Canonical stage-number to stage-folder-name mapping artifact exists | `test_produces_20_stages`, `test_stage_numbers_sequential`, `test_names_match_contracts`, `test_required_fields_present` | PASS |
| AC8 | Tests exist for mapping generation/resolution | 13 tests in `test_stage_mapping.py` | PASS |
