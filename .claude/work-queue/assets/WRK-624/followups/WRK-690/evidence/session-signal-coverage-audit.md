# Session Signal Coverage Audit

- Required signals: 23
- Required currently measured: 23
- Required inferred in >=1 session: 23
- Policy: inferred coverage is diagnostic only and is **not** counted as measured coverage.

| Signal | Stage | Required | Currently measured | Inferred any session | Relaxed (inferred) | Strict (inferred) |
|---|---|---|---|---|---|---|
| wrk_created | 1 Capture | Yes | Yes | Yes | 14/14 | 7/7 |
| resource_intelligence | 2 Resource Intelligence | Yes | Yes | Yes | 14/14 | 7/7 |
| triage_contract_complete | 3 Triage | Yes | Yes | Yes | 6/14 | 3/7 |
| plan_draft_complete | 4 Plan Draft | Yes | Yes | Yes | 14/14 | 7/7 |
| plan_html_review_draft | 5 User Review - Plan (Draft) | Yes | Yes | Yes | 13/14 | 6/7 |
| html_open_default_browser | 5/7/17 User Reviews | Yes | Yes | Yes | 7/14 | 4/7 |
| cross_review | 6 Cross-Review | Yes | Yes | Yes | 14/14 | 7/7 |
| plan_html_review_final | 7 User Review - Plan (Final) | Yes | Yes | Yes | 14/14 | 7/7 |
| claim_evidence | 8 Claim / Activation | Yes | Yes | Yes | 14/14 | 7/7 |
| set_active_wrk | 8 Claim / Activation | Yes | Yes | Yes | 9/14 | 7/7 |
| work_queue_skill | 9 Work-Queue Routing | Yes | Yes | Yes | 14/14 | 7/7 |
| work_execution | 10 Work Execution | Yes | Yes | Yes | 13/14 | 7/7 |
| artifact_generation | 11 Artifact Generation | Yes | Yes | Yes | 7/14 | 4/7 |
| tdd_eval | 12 TDD / Eval | Yes | Yes | Yes | 14/14 | 7/7 |
| agent_cross_review | 13 Agent Cross-Review | Yes | Yes | Yes | 11/14 | 6/7 |
| verify_gate_evidence | 14 Verify Gate Evidence | Yes | Yes | Yes | 10/14 | 7/7 |
| future_work | 15 Future Work Synthesis | Yes | Yes | Yes | 6/14 | 5/7 |
| resource_intelligence_update | 16 Resource Intelligence Update | Yes | Yes | Yes | 1/14 | 1/7 |
| user_review_close | 17 User Review - Implementation | Yes | Yes | Yes | 1/14 | 1/7 |
| reclaim | 18 Reclaim | Conditional | Yes | Yes | 6/14 | 6/7 |
| close_item | 19 Close | Yes | Yes | Yes | 14/14 | 7/7 |
| archive_item | 20 Archive | Yes | Yes | Yes | 8/14 | 4/7 |
| close_or_archive | 19/20 Terminal | Yes | Yes | Yes | 14/14 | 7/7 |
| init | Session bootstrap | Yes | Yes | Yes | 14/14 | 7/7 |

## Coverage by Agent Source

| Signal | claude-native | codex-native | gemini-native |
|---|---|---|---|
| wrk_created | 35/50 | 60/60 | 59/65 |
| resource_intelligence | 12/50 | 40/60 | 25/65 |
| triage_contract_complete | 3/50 | 6/60 | 1/65 |
| plan_draft_complete | 18/50 | 13/60 | 7/65 |
| plan_html_review_draft | 12/50 | 20/60 | 13/65 |
| html_open_default_browser | 2/50 | 5/60 | 1/65 |
| cross_review | 20/50 | 18/60 | 12/65 |
| plan_html_review_final | 15/50 | 24/60 | 16/65 |
| claim_evidence | 13/50 | 23/60 | 12/65 |
| set_active_wrk | 10/50 | 9/60 | 2/65 |
| work_queue_skill | 49/50 | 60/60 | 54/65 |
| work_execution | 20/50 | 8/60 | 1/65 |
| artifact_generation | 4/50 | 9/60 | 5/65 |
| tdd_eval | 23/50 | 60/60 | 20/65 |
| agent_cross_review | 10/50 | 14/60 | 6/65 |
| verify_gate_evidence | 10/50 | 16/60 | 11/65 |
| future_work | 4/50 | 4/60 | 1/65 |
| resource_intelligence_update | 0/50 | 1/60 | 0/65 |
| user_review_close | 0/50 | 1/60 | 0/65 |
| reclaim | 2/50 | 4/60 | 0/65 |
| close_item | 8/50 | 20/60 | 7/65 |
| archive_item | 2/50 | 7/60 | 1/65 |
| close_or_archive | 8/50 | 20/60 | 7/65 |
| init | 19/50 | 13/60 | 6/65 |
