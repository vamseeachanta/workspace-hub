# WRK-1028 AC Test Matrix

| AC | Description | Test(s) | Status |
|----|-------------|---------|--------|
| AC-01 | Gate 5→6: Write to cross-review.yaml blocked when user-review-plan-draft.yaml missing | TestGate5::test_gate5_blocked_when_no_approval_file | PASS |
| AC-01 | Gate 5→6: Write to cross-review.yaml blocked when decision != approved | TestGate5::test_gate5_blocked_when_decision_not_approved | PASS |
| AC-01 | Gate 5→6: Write to cross-review.yaml allowed when decision: approved | TestGate5::test_gate5_allowed_when_approved | PASS |
| AC-02 | Gate 7→8: Write to activation.yaml blocked when plan-final-review.yaml missing | TestGate7::test_gate7_blocked_when_no_final_review | PASS |
| AC-02 | Gate 7→8: Write to activation.yaml blocked when fields missing | TestGate7::test_gate7_blocked_when_fields_missing | PASS |
| AC-02 | Gate 7→8: Write to activation.yaml allowed when all fields present + decision: passed | TestGate7::test_gate7_allowed_when_all_fields_present | PASS |
| AC-03 | Gate 17→18: Write to done/WRK-NNN.md blocked when user-review-close.yaml missing | TestGate17::test_gate17_blocked_when_no_close_review | PASS |
| AC-03 | Gate 17→18: Write to done/WRK-NNN.md allowed when decision: approved | TestGate17::test_gate17_allowed_when_approved | PASS |
| AC-04 | False positive: non-WRK write paths not blocked | TestGateFalsePositive::test_non_wrk_write_not_blocked | PASS |
| AC-04 | False positive: non-Write tools not blocked | TestGateFalsePositive::test_non_write_tool_not_blocked | PASS |
| AC-05 | start_stage.py: task_agent route writes stage-N-prompt.md | TestStartStage::test_task_agent_writes_prompt_package | PASS |
| AC-06 | start_stage.py: human_session route emits checklist stdout | TestStartStage::test_human_session_emits_checklist | PASS |
| AC-07 | start_stage.py: chained_agent combines all stage contracts | TestStartStage::test_chained_agent_combines_all_stage_contracts | PASS |
| AC-08 | exit_stage.py: missing artifact → SystemExit(1) | TestExitStage::test_missing_artifact_raises | PASS |
| AC-09 | exit_stage.py: happy path exits zero | TestExitStage::test_happy_advance_exits_zero | PASS |
| AC-10 | exit_stage.py: human gate missing decision → SystemExit(1) | TestExitStage::test_human_gate_missing_decision_raises | PASS |
| AC-11 | exit_stage.py: human gate decision:approved → exits zero | TestExitStage::test_human_gate_approved_exits_zero | PASS |
| AC-12 | 20 stage YAML contracts present in scripts/work-queue/stages/ | ls count = 20 (verified manually) | PASS |
| AC-13 | 20 micro-skills present in .claude/skills/workspace-hub/stages/ | ls count = 20 (verified manually) | PASS |
| AC-14 | gate_check.py registered in .claude/settings.json PreToolUse Write hook | grep in settings.json confirms entry | PASS |
| AC-15 | process.md updated to 20-stage lifecycle with correct names + invocation types | process.md stage headers 1-20 verified | PASS |
| AC-16 | workflow-gatepass/SKILL.md references start_stage.py/exit_stage.py/gate_check.py | grep in SKILL.md confirms entries | PASS |
| AC-17 | work-queue-workflow/SKILL.md references stage orchestration scripts | Source of Truth section updated | PASS |

**Summary**: 23 checks — 23 PASS, 0 FAIL

Generated: 2026-03-07
