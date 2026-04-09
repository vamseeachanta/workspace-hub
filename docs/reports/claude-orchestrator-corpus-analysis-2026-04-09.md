# Claude orchestrator corpus analysis — 2026-04-09

Scope: analyzed Claude orchestrator logs at `logs/orchestrator/claude/session_*.jsonl`.
Method: counted only `hook == "post"` records per `session-corpus-audit` skill guidance.

## Corpus size
- Sessions analyzed: 24
- Post-hook records: 73646
- Unique prompt-like paths: 52

## Prompt classes
- stage_prompt: 39
- other_prompt_like: 11
- planning_template: 5
- plugin_prompt: 5
- review_template: 4

## Heaviest prompt sessions
- session_20260308.jsonl: 9 prompt reads
- session_20260309.jsonl: 9 prompt reads
- session_20260310.jsonl: 5 prompt reads
- session_20260316.jsonl: 5 prompt reads
- session_20260325.jsonl: 5 prompt reads

## Stage prompt distribution
- Stage 2: 18
- Stage 4: 8
- Stage 3: 3
- Stage 6: 3
- Stage 10: 3
- Stage 8: 2
- Stage 13: 1
- Stage 18: 1

## Most-read prompt paths
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

## Work items most associated with stage prompts
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

## Neighbor files around prompt reads
- `scripts/work-queue/verify-gate-evidence.py` — 7
- `.claude/work-queue/pending/WRK-1023.md` — 5
- `scripts/work-queue/wait-for-approval.sh` — 5
- `scripts/work-queue/exit_stage.py` — 4
- `specs/wrk/WRK-1019/plan.md` — 3
- `scripts/review/submit-to-codex.sh` — 3
- `/tmp/claude-1000/-mnt-local-analysis-workspace-hub/tasks/b5hfx5b6m.output` — 3
- `.claude/docs/orchestrator-pattern.md` — 3
- `scripts/work-queue/generate-html-review.py` — 3
- `scripts/review/cross-review.sh` — 3

## Neighbor commands around prompt reads
- `uv run --no-project python scripts/work-queue/exit_stage.py WRK-1023 5 2>&1` — 16
- `python3 -c "` — 14
- `grep -n "^## \` — 12
- `uv run --no-project python scripts/work-queue/generate-html-review.py --lifecycle WRK-1023 2>&1` — 11
- `gh run view 23101737831 -R vamseeachanta/digitalmodel --log 2>/dev/null` — 8
- `ls /mnt/local-analysis/workspace-hub/.claude/skills/ai/prompting/pandasai/ && echo "---" && ls /mnt/local-analysis/works` — 7
- `mkdir -p /mnt/local-analysis/workspace-hub/.claude/skills/ai/prompting/pandasai/references` — 7
- `cat /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/3cab08fb-7a98-4098-9f29-78be87a10d44/tool-results/to` — 6
- `uv run --no-project python scripts/work-queue/exit_stage.py WRK-1023 1 2>&1` — 5
- `python3 -c "import json` — 5

## Neighbor tool distribution
- Bash: 666
- Read: 325
- Write: 116
- Edit: 62
- Grep: 36
- TaskCreate: 19
- Glob: 12
- Skill: 8
- TaskUpdate: 7
- ToolSearch: 7

## Template inspection
- `scripts/planning/prompts/claude-adversarial.md` — verdict_format=False, adversarial_or_risk_language=True
- `scripts/planning/prompts/claude-conservative.md` — verdict_format=False, adversarial_or_risk_language=True
- `scripts/planning/prompts/codex-plan-draft.md` — verdict_format=False, adversarial_or_risk_language=True
- `scripts/planning/prompts/codex-architecture.md` — verdict_format=False, adversarial_or_risk_language=False
- `scripts/planning/prompts/gemini-risks.md` — verdict_format=False, adversarial_or_risk_language=True
- `scripts/review/prompts/plan-review.md` — verdict_format=True, adversarial_or_risk_language=True
- `scripts/review/prompts/implementation-review.md` — verdict_format=True, adversarial_or_risk_language=True
- `scripts/review/prompts/claude-compact-plan-review.md` — verdict_format=True, adversarial_or_risk_language=False


## Conclusions
1. Claude sessions are dominated by staged workflow prompt packages rather than ad hoc prompts.
2. Stage 2 and Stage 4 account for most stage-prompt reads, which indicates planning/resource-intelligence gates dominate the workflow.
3. Prompt adjacency is strongly coupled to work-queue evidence and verification scripts, so prompts are acting as workflow contracts.
4. Cross-provider prompt templates preserve role specialization: Claude for adversarial/conservative planning, Codex for architecture/implementation refinement, Gemini for risk analysis.
5. Explicit skill invocations are not the main delivery mechanism here; the workflow is largely script- and artifact-driven.

## Recommended next actions
1. Treat `.claude/work-queue/assets/*/stage-*-prompt.md`, `scripts/planning/prompts/*.md`, and `scripts/review/prompts/*.md` as the highest-leverage prompt surfaces for improvement.
2. Add a lightweight generated index of stage-prompt packages and their associated evidence artifacts to make stage behavior auditable without replaying logs.
3. Preserve model-role specialization when editing prompt templates; do not collapse Claude/Codex/Gemini prompts into one generic prompt.
4. If you want this operationalized, the next unfinished step is to extend the analysis across Hermes and Codex logs for a cross-agent routing baseline.
