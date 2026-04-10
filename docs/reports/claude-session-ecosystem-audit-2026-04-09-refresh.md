# Claude session ecosystem audit — 2026-04-10

Scope: post-hook records from `logs/orchestrator/claude/session_*.jsonl` compared against the current repo checkout.

## Corpus
- Sessions analyzed: 24
- Post-hook records: 73646
- Prompt-like reads: 64 total / 52 unique
- Missing repo-local reads: 8194
- Missing external reads: 963
- Bash calls using bare `python3`: 635
- Bash calls using `uv run ... python`: 5898

## Top tool distribution
- `Bash` — 40093
- `Read` — 13811
- `Edit` — 6724
- `Write` — 6436
- `Grep` — 1758
- `Agent` — 730
- `ToolSearch` — 681
- `TaskUpdate` — 541
- `WebSearch` — 519
- `Glob` — 392

## Top repo distribution
- `workspace-hub` — 70303
- `digitalmodel` — 1900
- `assetutilities` — 535
- `worldenergydata` — 201
- `agent-a597ec3f` — 100
- `aceengineer-admin` — 87
- `agent-a1fcef76` — 58
- `wrk-1132-standards-search` — 55
- `agent-a4dd71d2` — 39
- `assethold` — 38

## Most-read files
- `scripts/work-queue/verify-gate-evidence.py` — 732
- `scripts/work-queue/generate-html-review.py` — 249
- `scripts/work-queue/exit_stage.py` — 137
- `scripts/work-queue/start_stage.py` — 135
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 120
- `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md` — 115
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66
- `scripts/work-queue/archive-item.sh` — 61
- `scripts/work-queue/claim-item.sh` — 60
- `scripts/quality/check-all.sh` — 47
- `scripts/data/doc_intelligence/schema.py` — 47
- `.claude/skills/development/skill-eval/scripts/eval-skills.py` — 45
- `scripts/review/cross-review.sh` — 43

## Missing repo-local reads
- `scripts/work-queue/verify-gate-evidence.py` — 732
- `scripts/work-queue/generate-html-review.py` — 249
- `scripts/work-queue/exit_stage.py` — 137
- `scripts/work-queue/start_stage.py` — 135
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — 120
- `scripts/work-queue/close-item.sh` — 94
- `scripts/work-queue/whats-next.sh` — 70
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` — 66
- `scripts/work-queue/archive-item.sh` — 61
- `scripts/work-queue/claim-item.sh` — 60
- `scripts/work-queue/verify_checklist.py` — 43
- `scripts/work-queue/stages/stage-01-capture.yaml` — 42
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` — 37
- `scripts/work-queue/stages/stage-05-user-review-plan-draft.yaml` — 35
- `.claude/work-queue/scripts/generate-index.py` — 33
- `.claude/hooks/enforce-active-stage.sh` — 33
- `scripts/work-queue/stage_exit_checks.py` — 32
- `.claude/skills/workspace-hub/session-start/SKILL.md` — 30
- `scripts/work-queue/stages/stage-10-work-execution.yaml` — 29
- `scripts/work-queue/stages/stage-07-user-review-plan-final.yaml` — 28

## Missing external reads
- `/tmp/tmp.4XN7Wckbxl/review-content.md` — 18
- `/mnt/workspace-hub/.claude/work-queue/assets/WRK-5082/geometry-dimensions-WRK-1360.md` — 13
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/solvers/gmsh_meshing/mesh_generator.py` — 12
- `/mnt/workspace-hub/digitalmodel/tests/solvers/calculix/test_fem_chain.py` — 11
- `/tmp/tmp.4fvalbgSpv/review-content.md` — 10
- `/mnt/workspace-hub/.claude/skills/engineering/cad/freecad-automation/SKILL.md` — 10
- `/tmp/tmp.Y7GHawx2jw/review-content.md` — 9
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/hydrodynamics/hull_library/profile_schema.py` — 9
- `/mnt/workspace-hub/.claude/work-queue/working/WRK-1251.md` — 8
- `/mnt/workspace-hub/scripts/work-queue/verify-gate-evidence.py` — 8
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/solvers/calculix/inp_writer.py` — 8
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/structural/parachute/__init__.py` — 8
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/visualization/design_tools/freecad_integration.py` — 7
- `/mnt/workspace-hub/digitalmodel/src/digitalmodel/structural/parachute/chute_assessment.py` — 7
- `/mnt/workspace-hub/.claude/work-queue/assets/WRK-5082/plan-WRK-1360-3d-cad.md` — 7

## Prompt reads
- `.claude/skills/ai/prompting/pandasai/SKILL.md` — 7
- `scripts/review/prompts/plan-review.md` — 3
- `.claude/skills/_diverged/digitalmodel/ai-prompting/pandasai/SKILL.md` — 2
- `/home/vamsee/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/subagent-driven-development/implementer-prompt.md` — 2
- `.claude/skills/ai/prompting/agenta/SKILL.md` — 2
- `scripts/planning/prompts/gemini-plan-draft.md` — 2
- `.claude/work-queue/assets/WRK-1030/stage-2-prompt.md` — 1
- `scripts/planning/prompts/codex-architecture.md` — 1
- `scripts/planning/prompts/gemini-risks.md` — 1
- `.claude/work-queue/assets/WRK-1068/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1074/stage-13-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1075/stage-10-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1067/stage-6-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1064/stage-3-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1064/stage-4-prompt.md` — 1

## Missing prompt reads
- `.claude/skills/_diverged/digitalmodel/ai-prompting/pandasai/SKILL.md` — 2
- `/home/vamsee/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/subagent-driven-development/implementer-prompt.md` — 2
- `.claude/work-queue/assets/WRK-1030/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1068/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1074/stage-13-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1075/stage-10-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1067/stage-6-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1064/stage-3-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1064/stage-4-prompt.md` — 1
- `.claude/work-queue/assets/WRK-658/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1090/stage-10-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1091/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1097/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1071/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1010/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1016/stage-2-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1016/stage-3-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1059/stage-4-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1069/stage-4-prompt.md` — 1
- `.claude/work-queue/assets/WRK-1112/stage-3-prompt.md` — 1

## Stage prompt distribution
- `2` — 18
- `4` — 8
- `10` — 3
- `6` — 3
- `3` — 3
- `8` — 2
- `13` — 1
- `18` — 1

## Stage prompt work items
- `workspace-hub-1405` — 3
- `WRK-1064` — 2
- `WRK-1016` — 2
- `WRK-1112` — 2
- `WRK-1156` — 2
- `WRK-1030` — 1
- `WRK-1068` — 1
- `WRK-1074` — 1
- `WRK-1075` — 1
- `WRK-1067` — 1
- `WRK-658` — 1
- `WRK-1090` — 1
- `WRK-1091` — 1
- `WRK-1097` — 1
- `WRK-1071` — 1

## Ecosystem strengthening recommendations
1. Add a periodic audit for stale work-queue references; the hottest missing reads are legacy `scripts/work-queue/*` paths that are still present in historical Claude workflows.
2. Keep a generated report in-repo so future refactors can measure whether missing-reference drift is shrinking or growing.
3. Reduce bare `python3` usage in automation and prompts; the session corpus still shows direct `python3` bash calls despite the repo-wide `uv run` policy.
4. Treat missing stage prompt assets as first-class evidence gaps. If the asset is intentionally ephemeral, generate an index or summary artifact before cleanup.

