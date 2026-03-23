# Cross-Review: Claude (Plan)

## Verdict: REQUEST_CHANGES → Addressed

### P2 Findings (all addressed)
1. **AC6 ordering risk**: Defer bare file removal to after validation passes. Keep originals until WRK-5113 path updates.
   - **Resolution**: Change migration to copy (not move). Add `--remove-originals` flag only after all 20 validated.
2. **Gatepass mapping missing**: Need explicit mapping table.
   - **Resolution**: Already documented in resource-intelligence.yaml (stage_specific section). Will make explicit in gotchas.
3. **Validation too shallow**: Only structural checks.
   - **Resolution**: Add YAML parsing check and non-empty SKILL.md frontmatter validation to validate-folder-skill.sh.
4. **No rollback strategy**: Partial failure undefined.
   - **Resolution**: Migration copies (not removes originals). Mixed state is safe — old files remain until explicit cleanup.

### Questions Answered
- Stage skills loaded by start_stage.py via stage-mapping.yaml path — auto-discovered by order number
- contract.yaml already exists for all 20 stages (scripts/work-queue/stages/) — copied, not generated
- Empty hooks.yaml with `pre_exit_hooks: []` for stages without hooks — valid per schema
