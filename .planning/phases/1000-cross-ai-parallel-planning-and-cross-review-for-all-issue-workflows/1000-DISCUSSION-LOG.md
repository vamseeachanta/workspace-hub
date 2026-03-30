# Phase 1000: Cross-AI Parallel Planning and Cross-Review — Discussion Log (Assumptions Mode)

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-03-29
**Phase:** 1000-cross-ai-parallel-planning-and-cross-review-for-all-issue-workflows
**Mode:** assumptions (--auto)
**Areas analyzed:** Scope & Integration, Parallel Planning Architecture, Parallel Review Execution, Consensus Gate Strategy, Integration Points

## Assumptions Presented

### Scope & Integration Strategy
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Wire into existing GSD lifecycle as optional modes, not a parallel system | Confident | behavior-contract.yaml canonical 6-stage flow, GSD sole workflow since 2026-03-25 |
| Two new capabilities as mode toggles on existing skills | Confident | plan-phase.md, review.md, execute-phase.md existing patterns |

### Parallel Planning Architecture
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| True parallel planning — all 3 AIs produce independent plans, then merge | Unclear → Resolved | plan-phase.md single-agent pipeline, agent-delegation-templates.md sequential handoffs |
| Ensemble synthesis with structured diff pre-filtering | Likely (post-research) | LangGraph map-reduce pattern, CrewAI consensus pattern |

### Parallel Review Execution
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Switch from sequential to true parallel via bash & + wait | Likely → Confident (post-research) | review.md line 117 "not parallel — avoid rate limits", rate limits independent per provider |
| ~65% wall-clock improvement expected | Likely | 3 sequential → 1 parallel batch |

### Consensus Gate Strategy
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Tiered gates by complexity (Route A/B/C), not universal 2-of-3 | Likely | behavior-contract.yaml two_of_three_approve only for feature/C + architecture |
| Always use all 3 for planning; tier for review | Likely | User's explicit intent for diverse perspectives in planning |

### Integration Points
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Extend existing scripts + GSD skills, don't replace | Likely | cross-review-loop.sh, per-provider scripts, review.md already operational |

## Corrections Made

No corrections — all assumptions confirmed (--auto mode).

## Auto-Resolved

- **Parallel Planning Architecture:** Unclear → auto-selected Alternative A (true parallel planning with merge). Rationale: matches user's explicit intent ("plan independently, then merge") from GitHub #1501.
- **Consensus Gate:** auto-selected tiered approach over universal 2-of-3. Rationale: research showed cost is trivial but latency matters for simple tasks.

## External Research

- **API rate limits for parallel invocation:** Each CLI hits different provider API — rate limits independent. Sequential invocation in review.md is overly conservative. (Source: Anthropic/OpenAI/Google rate limit docs)
- **Plan merge strategies:** Ensemble-synthesis with structured diff is the LangGraph map-reduce pattern. Auto-merge agreed sections, LLM-synthesize divergent sections. CrewAI consensus voting (2-of-3 endorsement) for individual plan elements. (Source: LangGraph/CrewAI/AutoGen docs)
- **Cost of universal 2-of-3:** ~$0.124/task for 3 reviews, ~$37/month at 10 tasks/day. Tiered approach saves ~54% cost but the absolute amounts are immaterial. Latency is the stronger argument for tiering. (Source: provider pricing pages)
