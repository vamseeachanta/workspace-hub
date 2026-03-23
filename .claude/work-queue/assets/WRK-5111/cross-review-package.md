# WRK-5111 Cross-Review Package: Convert 20 Stages to Folder-Skills

## Context
Child-b of WRK-1321 (Two-Tier Folder-Skill Architecture). Converts 20 bare stage micro-skill .md files into Anthropic folder-skill format.

## Plan Summary
1. Create `migrate-stage-to-folder.sh` — scaffolds one stage folder from bare .md + contract YAML
2. Create `validate-folder-skill.sh` — verifies folder structure (SKILL.md, contract.yaml, gotchas.md, hooks.yaml)
3. Run migration for all 20 stages
4. Distribute gatepass sub-skill content to stage-specific gotchas.md files
5. Validate all 20 stage folders

## Acceptance Criteria
- AC1: 20 directories: `.claude/skills/workspace-hub/stages/stage-NN-name/SKILL.md`
- AC2: Each folder contains: SKILL.md, contract.yaml, gotchas.md, hooks.yaml
- AC3: Gatepass sub-skill content distributed to relevant stage folders
- AC4: migrate-stage-to-folder.sh script created and used
- AC5: validate-folder-skill.sh passes for all 20 stages
- AC6: Bare stage-NN.md files removed after migration

## Review Questions
1. Is the SKILL.md template appropriate for stage folder-skills?
2. Are there any stages that need special handling beyond the standard migration?
3. Is the gatepass distribution mapping correct?
4. Any risks with removing bare .md files before WRK-5113 (path updates)?
