# AC Test Matrix — WRK-1046

| Test ID | Acceptance Criterion | Scenario | Expected Result | Actual Result | Status |
|---------|---------------------|----------|-----------------|---------------|--------|
| T1 | exit_stage.py writes checkpoint with current_stage=N+1 after successful stage exit | Happy path — exit stage 3, real stage contract for 4 | checkpoint.yaml written; current_stage=4; checkpointed_at present | checkpoint written; current_stage=4; checkpointed_at present | PASS |
| T2 | entry_reads in checkpoint sourced from N+1 stage contract | Real stage-04 contract has entry_reads list | entry_reads populated in checkpoint | entry_reads list present | PASS |
| T3 | --context-summary arg propagated to checkpoint.yaml | Pass custom summary string to exit_stage.py | context_summary matches passed value | context_summary matches | PASS |
| T4 | Auto-generated context_summary when --context-summary absent | No summary arg | context_summary auto-generated with stage info | auto-generated summary present | PASS |
| T5 | stage_complete signal or STAGE_GATE appears in exit_stage.py output | Happy exit | stdout contains "STAGE_GATE" or "stage_complete" | "STAGE_GATE" present in stdout | PASS |
| T6 | STAGE_GATE action=spawn_subagent for non-gate next stage | Exit stage 3; stage 4 has human_gate=false | spawn_subagent action in STAGE_GATE block | spawn_subagent printed | PASS |
| T7 | STAGE_GATE action=await_user_approval when next stage has human_gate=true | Exit stage 4; stage 5 contract has human_gate=true | await_user_approval in STAGE_GATE | await_user_approval printed | PASS |
| T8 | Stages 7 and 17 produce await_user_approval (read from contract YAML) | Exit stage 6 (→7) and stage 16 (→17) | await_user_approval for both | await_user_approval for both | PASS |
| T9 | human_gate driven by contract YAML, not hardcoded list | Override stage 11 contract to human_gate=true | await_user_approval for normally auto stage | await_user_approval printed | PASS |
| T10 | start_stage.py shows resume block with entry_reads from checkpoint | checkpoint.yaml with current_stage=5, entry_reads list | stdout contains checkpoint.yaml and entry_reads | resume block printed | PASS |
| T11 | chained_stages from N+1 contract written to checkpoint | Stage 7 exit; stage 8 contract has chained_stages=[8,9] | chained_stages in checkpoint or output | chained_stages present | PASS |
| T12 | Stage 20 exit writes current_stage=complete; no STAGE_GATE emitted | Exit stage 20 | current_stage=complete; STAGE_GATE absent | terminal state correct | PASS |
| T13 | validate_checkpoint warns on missing fields (non-blocking) | Write checkpoint with wrk_id missing; call validate | Warning emitted to stderr; no SystemExit | warning printed; process continues | PASS |
