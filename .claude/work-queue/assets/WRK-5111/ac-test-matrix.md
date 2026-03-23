# WRK-5111 AC-Test Matrix

| AC | Description | Test | Result | Evidence |
|----|-------------|------|--------|----------|
| AC1 | 20 directories created with SKILL.md | `ls -d stages/stage-*/` count = 20 | PASS | 20 folders exist |
| AC2 | Each folder has SKILL.md, contract.yaml, gotchas.md, hooks.yaml | `validate-folder-skill.sh` on all 20 | PASS | 20/20 PASS |
| AC3 | Gatepass content distributed | gotchas.md content check on stages 1,5,6,7,15,17,19 | PASS | No-bypass, close-gate, stage-15 rule, operational lessons distributed |
| AC4 | migrate-stage-to-folder.sh created and used | Script exists + ran for all 20 | PASS | All 20 stages migrated via script |
| AC5 | validate-folder-skill.sh passes for all 20 | Ran validation loop | PASS | 20/20 PASS with frontmatter + YAML + body checks |
| AC6 | Bare .md files removed after migration | N/A | DEFERRED | Per cross-review P2: removal deferred to WRK-5113 (path updates first) |
