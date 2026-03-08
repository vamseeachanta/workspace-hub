# WRK-1046 Cross-Review Synthesis — Plan

## Verdicts
- Gemini: REQUEST_CHANGES
- Codex: REQUEST_CHANGES

## P1 Findings (resolved in plan update)

| # | Reviewer | Finding | Resolution |
|---|----------|---------|------------|
| P1-1 | Codex | Checkpoint schema conflicts: plan used `stage`/`stage_complete_at`/`updated_at` but checkpoint.sh uses `current_stage`/`checkpointed_at` | Plan updated: exit_stage.py writes `current_stage` (N+1) and `checkpointed_at` — same schema as checkpoint.sh |
| P1-2 | Codex | `current_stage: N` after completing N means start_stage.py resume block won't fire for N+1 | Plan fixed: `current_stage` = N+1 (next stage), `completed_stage` = N (informational) |
| P1-3 | Codex, Gemini | `human_gate` hardcoded to [5,7,17] — will drift if gate list changes | Plan fixed: read `human_gate` field from next stage contract YAML |

## P2 Findings (resolved in plan update)

| # | Reviewer | Finding | Resolution |
|---|----------|---------|------------|
| P2-1 | Codex | Stage 4 is chained_agent covering stages 2/3/4; "one subagent per stage" contradicts this | Plan updated: auto-loop honours `chained_stages` groups — one subagent per group |
| P2-2 | Codex | log-gate-event.sh signature underspecified | Plan fixed: `log-gate-event.sh WRK-NNN N stage_complete claude "Stage N complete"` |
| P2-3 | Codex | Stage 20 terminal boundary unhandled | Plan fixed: stage 20 exit writes `current_stage: complete`, no STAGE_GATE printed |

## Open Questions (deferred)

- Gemini: "How does orchestrator handle subagent failure/timeout?" → deferred to retry WRK
- Codex: "Should checkpoint.sh be deprecated?" → No; both checkpoint.sh (manual) and exit_stage.py (auto) write the same schema; they coexist
- Gemini: "Use checkpoint.yaml for signaling instead of stdout?" → stdout is appropriate here; the orchestrator reads tool output; checkpoint.yaml is the durable state; they serve different purposes

## Plan Updated: Yes
All P1 and P2 findings addressed. Tests expanded to T1-T12.
