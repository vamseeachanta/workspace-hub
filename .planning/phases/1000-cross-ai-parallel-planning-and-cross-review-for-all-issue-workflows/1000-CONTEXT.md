# Phase 1000: Cross-AI Parallel Planning and Cross-Review — Context

**Gathered:** 2026-03-29 (assumptions mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Add cross-AI parallel planning (Claude, Codex, Gemini plan independently then merge) and parallel cross-review (all 3 review with 2-of-3 gate) to the GSD issue workflow. Extends existing infrastructure — does not replace it. GitHub #1501.

</domain>

<decisions>
## Implementation Decisions

### Scope & Integration Strategy
- **D-01:** Wire into existing GSD lifecycle (discuss → plan → execute → review) as optional modes, not a parallel system. The GSD framework is the sole workflow engine; `behavior-contract.yaml` defines the canonical 6-stage flow.
- **D-02:** Two new capabilities: (a) cross-planning at plan-phase stage, (b) parallel cross-review at review stage. Both are mode toggles on existing skills, not new standalone tools.

### Parallel Planning Architecture
- **D-03:** True parallel planning — all three AIs receive the same phase spec + CONTEXT.md and independently produce a PLAN.md. A designated merge agent (Claude, given architecture strength) synthesizes the three into a final plan.
- **D-04:** Adopt ensemble-synthesis with structured diff pre-filtering: parse plans into structured sections, auto-merge agreed elements, only call a synthesis LLM for divergent sections (LangGraph map-reduce pattern adapted to PLAN.md template).
- **D-05:** Each provider plans in isolation (no visibility into others' plans) to avoid anchoring bias.

### Parallel Review Execution
- **D-06:** Switch review invocation from sequential to true parallel — use bash `&` background processes with `wait`. Rate limits are independent across providers (Anthropic, OpenAI, Google APIs). The sequential constraint in current `review.md` is overly conservative.
- **D-07:** Expected wall-clock improvement: ~65% faster reviews (3 sequential → 1 parallel batch, gated by slowest provider).

### Consensus Gate Strategy
- **D-08:** Tiered review gates based on task complexity, not universal 2-of-3. Route classification uses existing Route A/B/C from behavior-contract.yaml:
  - **Route A (simple):** Single-provider review (cheapest/fastest provider)
  - **Route B (medium):** 2-of-3 cross-review
  - **Route C (complex):** Full 3-of-3 with synthesis
- **D-09:** For cross-planning: always use all 3 providers (the value is in diverse perspectives). For cross-review: tier by complexity per D-08.
- **D-10:** Reuse existing `two_of_three_approve` semantics from behavior-contract.yaml: 2+ APPROVE/MINOR passes; 1 MAJOR + 2 APPROVE still fails; NO_OUTPUT + 2 APPROVE = CONDITIONAL_PASS.

### Integration Points
- **D-11:** Extend `scripts/development/ai-review/cross-review-loop.sh` for parallel invocation mode. Create new `scripts/development/ai-plan/cross-plan.sh` for planning dispatch.
- **D-12:** Update `agent-delegation-templates.md` with `phase_0_plan` block for all task types.
- **D-13:** Update GSD skills (`plan-phase.md`, `review.md`) to detect cross-plan/cross-review mode from config and invoke accordingly.

### Claude's Discretion
- Exact synthesis prompt for merging divergent plan sections
- Structured diff algorithm for plan comparison (regex parsing vs JSON intermediate)
- Temp file handling for parallel plan collection
- Progress display during parallel invocations

### Folded Todos
None — no todos matched at >=0.4 threshold.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Cross-review infrastructure
- `scripts/development/ai-review/cross-review-loop.sh` — existing 3-iteration review loop with feedback extraction
- `scripts/development/ai-review/codex-review.sh` — Codex review invocation
- `scripts/development/ai-review/claude-review.sh` — Claude review invocation
- `scripts/development/ai-review/gemini-review.sh` — Gemini review invocation
- `scripts/development/ai-review/codex-review-manager.sh` — review management (list, approve, reject, stats)

### Policy & routing
- `docs/modules/ai/CROSS_REVIEW_POLICY.md` — mandatory cross-review policy
- `docs/modules/ai/MULTI_AI_WORKFLOW.md` — multi-AI pipeline architecture
- `.claude/docs/agent-delegation-templates.md` — task_agents role matrix (primary/secondary/tertiary per task type)
- `.claude/docs/provider-behavioral-differences.md` — provider strength routing rationale
- `config/agents/behavior-contract.yaml` — canonical task_type_matrix, quality gate definitions, 6-stage flow
- `config/agents/routing-config.yaml` — tier routing configuration

### GSD workflow skills (to be extended)
- `.claude/get-shit-done/workflows/plan-phase.md` — plan-phase skill (add cross-plan mode)
- `.claude/get-shit-done/workflows/review.md` — review skill (add parallel mode)
- `.claude/get-shit-done/workflows/execute-phase.md` — execution skill (reference for parallel subagent patterns)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cross-review-loop.sh` — iteration tracking, review ID generation, feedback extraction (adapt for parallel mode)
- Per-provider review scripts (`codex-review.sh`, `claude-review.sh`, `gemini-review.sh`) — invocation patterns already abstracted
- `codex-review-manager.sh` — verdict aggregation, stats tracking (extend for plan reviews)
- GSD `review.md` workflow — already invokes all 3 CLIs and produces combined REVIEWS.md
- GSD `execute-phase.md` — demonstrates parallel `Task()` subagent spawning pattern

### Established Patterns
- `behavior-contract.yaml` task_type_matrix — source of truth for routing; extend with `phase_0_plan` entries
- Normalized verdict set: `[APPROVE, MINOR, MAJOR, NO_OUTPUT, CONDITIONAL_PASS, ERROR]`
- PLAN.md structured template — consistent format enables deterministic diff for merge
- Route A/B/C complexity classification — reuse for gate tier selection

### Integration Points
- `plan-phase.md` research → plan → check pipeline — insert cross-plan dispatch before single-planner step
- `review.md` sequential invocation loop — replace with parallel invocation + wait + aggregate
- `routing-config.yaml` — add cross-plan/cross-review mode flags per route tier
- `agent-delegation-templates.md` — add `phase_0_plan` and `phase_N_review` parallel blocks

</code_context>

<specifics>
## Specific Ideas

- Independent planning avoids anchoring bias — this was the user's explicit rationale for parallel-not-serial planning
- Ensemble synthesis: auto-merge where plans agree, LLM synthesis only for divergent sections — minimizes cost while preserving quality
- Cost is trivial (~$18-37/month at realistic volumes); the real argument for tiering is latency on simple tasks

</specifics>

<deferred>
## Deferred Ideas

- Cross-AI parallel execution (not just planning/review) — separate phase
- Auto-selection of synthesis agent based on task type — future enhancement
- Cost tracking dashboard for cross-AI operations — future phase

### Reviewed Todos (not folded)
- "Automate OrcaFlex model generation on licensed machine" (score 0.2) — unrelated to cross-AI workflow

</deferred>

---

*Phase: 1000-cross-ai-parallel-planning-and-cross-review-for-all-issue-workflows*
*Context gathered: 2026-03-29*
