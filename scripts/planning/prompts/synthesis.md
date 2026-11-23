# Orchestrator Synthesis Prompt

You are synthesising 9 independent planning reports (3×Claude, 3×Codex, 3×Gemini) for a
software work item. Each agent worked from the same context but with a different reasoning
stance. Your job is to merge them into a single, de-biased plan.

## Output format

You MUST output your response using exactly the structured markers below — no other format.
The markers are machine-parsed; do not alter them or add extra text outside the blocks.

```
SYNTHESIS_START
CONSENSUS_SCORE: <integer 0-100>
DECISIONS_START
[<VERDICT>:<confidence>] <one-line decision text>
[<VERDICT>:<confidence>] <one-line decision text>
...
DECISIONS_END
SPLITS_START
<one block per SPLIT decision; write NONE if no splits>
[SPLIT:<confidence>] <decision text>
  Option A (<N> agents): <summary> — <agent-list>
  Option B (<N> agents): <summary> — <agent-list>
SPLITS_END
MERGED_PLAN_START
<Full merged implementation plan — numbered phases, file paths, test strategy>
MERGED_PLAN_END
SYNTHESIS_END
```

## Rules

- VERDICT is exactly one of: CONSENSUS, SPLIT, SOLO
- CONSENSUS = 7 or more agents agree on this point
- SPLIT = two or more meaningfully different positions; agents are roughly divided
- SOLO = only 1-2 agents raised this point; worth noting but not blocking
- confidence is an integer 0-100 representing how strongly agents converged
- CONSENSUS_SCORE = integer(# CONSENSUS decisions / total decisions x 100)
- If CONSENSUS_SCORE < 70, there are SPLIT decisions requiring user resolution
- MERGED_PLAN: use CONSENSUS decisions as the basis; note SPLIT options inline;
  incorporate high-value SOLO insights where they add clear value

## Analysis steps

1. Read all agent reports
2. Extract every distinct decision or recommendation each agent makes
3. Group equivalent decisions across agents
4. Classify each group as CONSENSUS / SPLIT / SOLO per the rules above
5. Compute CONSENSUS_SCORE
6. Write the SPLITS block (decisions requiring user input before implementation)
7. Write the MERGED_PLAN incorporating consensus decisions + flagged splits + solo insights
