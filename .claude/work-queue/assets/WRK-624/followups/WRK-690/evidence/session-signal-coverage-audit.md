# Session Signal Coverage Audit

- Required signals: 23
- Required currently measured: 8

| Signal | Stage | Required | Currently measured | Relaxed (inferred) | Strict (inferred) |
|---|---|---|---|---|---|
| wrk_created | 1 Capture | Yes | No | 0/10 | 0/1 |
| resource_intelligence | 2 Resource Intelligence | Yes | Yes | 6/10 | 1/1 |
| triage_contract_complete | 3 Triage | Yes | No | 0/10 | 0/1 |
| plan_draft_complete | 4 Plan Draft | Yes | No | 5/10 | 1/1 |
| plan_html_review_draft | 5 User Review - Plan (Draft) | Yes | No | 0/10 | 0/1 |
| html_open_default_browser | 5/7/17 User Reviews | Yes | No | 0/10 | 0/1 |
| cross_review | 6 Cross-Review | Yes | Yes | 10/10 | 1/1 |
| plan_html_review_final | 7 User Review - Plan (Final) | Yes | No | 0/10 | 0/1 |
| claim_evidence | 8 Claim / Activation | Yes | Yes | 10/10 | 1/1 |
| set_active_wrk | 8 Claim / Activation | Yes | Yes | 1/10 | 1/1 |
| work_queue_skill | 9 Work-Queue Routing | Yes | No | 10/10 | 1/1 |
| work_execution | 10 Work Execution | Yes | No | 4/10 | 0/1 |
| artifact_generation | 11 Artifact Generation | Yes | No | 5/10 | 0/1 |
| tdd_eval | 12 TDD / Eval | Yes | No | 0/10 | 0/1 |
| agent_cross_review | 13 Agent Cross-Review | Yes | No | 5/10 | 1/1 |
| verify_gate_evidence | 14 Verify Gate Evidence | Yes | Yes | 7/10 | 1/1 |
| future_work | 15 Future Work Synthesis | Yes | Yes | 4/10 | 0/1 |
| resource_intelligence_update | 16 Resource Intelligence Update | Yes | No | 0/10 | 0/1 |
| user_review_close | 17 User Review - Implementation | Yes | No | 0/10 | 0/1 |
| reclaim | 18 Reclaim | Conditional | Yes | 2/10 | 0/1 |
| close_item | 19 Close | Yes | No | 5/10 | 0/1 |
| archive_item | 20 Archive | Yes | No | 2/10 | 0/1 |
| close_or_archive | 19/20 Terminal | Yes | Yes | 10/10 | 1/1 |
| init | Session bootstrap | Yes | Yes | 10/10 | 1/1 |

## Missing Required Signals

- `wrk_created`
- `triage_contract_complete`
- `plan_draft_complete`
- `plan_html_review_draft`
- `html_open_default_browser`
- `plan_html_review_final`
- `work_queue_skill`
- `work_execution`
- `artifact_generation`
- `tdd_eval`
- `agent_cross_review`
- `resource_intelligence_update`
- `user_review_close`
- `close_item`
- `archive_item`
