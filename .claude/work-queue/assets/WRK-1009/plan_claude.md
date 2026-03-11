# WRK-1009 — Claude Plan View

## Alignment with WRK Mission

The eval harness targets automated, repeatable quality measurement for 508 skills.
Keeping evals static (no live model runs) is the right call for v1 — reduces cost
and latency while still catching schema drift and broken step sequences.

## Key Design Decisions (Claude perspective)

### Retirement Threshold (0.05 / 10 invocations)
This is appropriately conservative. `skill-scores.yaml` shows a clear adoption cliff:
active skills sit at 0.10-0.65 baseline usage; marginal ones fall to 0.005-0.014.
The 0.05 threshold catches true dead-weight while preserving niche agent-loaded skills.
The 10-invocation minimum prevents noisy data from triggering false retirements.

### Central eval definitions (`specs/skills/evals/`)
Preferred over per-skill for operational simplicity: one directory to audit, one grep
to find all evals, consistent naming convention.

### Phase 0 (Script-candidate scan) — Strategic fit
Directly implements `.claude/rules/patterns.md` §Scripts-Over-LLM-Judgment. The scan
output feeds a separate conversion WRK per candidate — correct granularity.

### Pilot skill selection
`work-queue` + `workflow-gatepass` + `comprehensive-learning` are the highest-leverage
procedural skills in the harness. Evals here will catch lifecycle regressions early.

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Eval definitions go stale as skills evolve | Cron re-runs evals nightly; failures surface immediately |
| Script-candidate scan has false positives | Output is candidate list only — human reviews before conversion WRK |
| Retirement candidates grow unbounded | Candidate log is append-only; orchestrator reviews weekly |

## Synthesis note
No conflicts with Codex/Gemini views anticipated — this is infrastructure tooling
with clear implementation boundaries. Plan is ready for Stage 6 cross-review.
