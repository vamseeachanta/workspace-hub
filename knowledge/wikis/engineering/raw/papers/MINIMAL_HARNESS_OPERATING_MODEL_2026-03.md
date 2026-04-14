# Minimal Harness Operating Model

Issue: #1514  
Date: 2026-03-31

## Recommendation

For the next 30-60 days, use a minimal operating model:

- Make Claude Code the default orchestrator.
- Use Codex more aggressively as the main coding worker for bounded implementation, test writing, refactors, and implementation review.
- Use Gemini narrowly for large-context research, comparison passes, and overflow analysis where its context window materially helps.
- Require adversarial review for plans by default on non-trivial work, and for code/artifacts before completion when the change is risky, architectural, cross-cutting, or hard to verify locally.
- Treat provider plugins, slash commands, and adapters as optional frontends only, not the core architecture.
- Do not build a new provider-neutral control plane now.

This is the simplest workable model because the repo already has a thick `.claude` surface, while `.codex` and `.gemini` are already thin adapters around the same contract. The visible drift is coming from trying to preserve multiple control planes at once, not from lacking one more framework.

## Role Assignment

Explicit answers:

- Should Claude Code be the default orchestrator now? Yes.
- What should Codex be used for more aggressively? Bounded implementation, test writing, refactors, implementation review, and parallel worker execution.
- What should Gemini be used for narrowly? Large-context research, comparison passes, and overflow analysis.

### Claude

Claude should be the default orchestrator now.

Claude is the best near-term orchestrator because:

- `.claude` is already the richest maintained surface in this repo.
- Claude has the strongest existing command, hook, and orchestration shape here.
- Related issues already point to provider-specific review and routing differences rather than a missing orchestrator abstraction.
- Using Claude as the primary planner/router requires the least new harness work.

Claude role for the next 30-60 days:

- gather task context
- choose the execution path
- decide when Codex or Gemini should be invoked
- keep final responsibility for plan quality and task framing
- own the repo-facing workflow language

### Codex

What should Codex be used for more aggressively?

Use Codex as the primary coding worker, not as a secondary novelty lane.

Codex should be used aggressively for:

- bounded implementation tasks after Claude frames the work
- test-first changes and patch generation
- refactors with clear file scope
- implementation review and diff scrutiny
- rescue work on stalled implementation tasks
- parallelizable worker tasks when the write scopes are disjoint

Reasoning:

- The repo already describes Codex as strong on focused code tasks.
- The current paid setup has two Codex accounts, which is the cheapest scalable execution capacity in the current mix.
- This shifts expensive long-context orchestration away from the execution lane while preserving throughput.

### Gemini

What should Gemini be used for narrowly?

Use Gemini narrowly as a research and comparison lane.

Gemini should be limited to:

- large-document or large-context research passes
- alternative-approach comparison
- synthesis across multiple sources or artifacts
- overflow analysis when Claude context is already saturated

Gemini should not be a default execution lane for repo mutations unless there is a specific reason. Related issue #1326 is a warning that Gemini output reliability in structured review flows is not the place to increase harness complexity right now.

## Review Policy

Adversarial review should be part of the operating model.

Default rule:

- plans should get adversarial review by default for non-trivial work
- code and other deliverable artifacts should get adversarial review before completion when the change is risky, architectural, cross-cutting, or hard to verify locally

Provider policy:

- two-provider review by default
- three-provider review only for higher-stakes work

Recommended routing:

- Claude produces the plan or orchestrates the task framing
- Codex provides the default adversarial review for implementation, diffs, tests, and concrete artifacts
- Gemini provides an additional adversarial review only when the task is architecture-heavy, research-heavy, ambiguous, or high stakes enough to justify a third independent angle

This keeps adversarial pressure in the workflow without turning every task into a three-provider ceremony.

## Tradeoffs

- This is not provider-neutral in the abstract. It is provider-neutral at the contract level, but intentionally provider-asymmetric in operation.
- Claude becomes a partial single point of orchestration. That is acceptable because it already is the thickest maintained surface.
- Codex gets more responsibility, which means task framing quality from Claude matters more.
- Gemini is underused relative to its theoretical capability, but that is preferable to paying a maintenance tax for broad parity.
- Existing legacy surfaces such as `.hive-mind`, `.swarm`, and `.SLASH_COMMAND_ECOSYSTEM` may remain on disk for a while, but they should not drive new architecture decisions.

Alternatives considered and rejected for now:

- New shared CLI backend as the main control plane: rejected because it adds harness work before proving that the current `.claude`-led flow is insufficient.
- MCP-first control plane: rejected as the default because provider surfaces are changing too quickly and MCP adoption is still surface-dependent.
- Full parity across Claude, Codex, and Gemini commands: rejected because the repo is already paying drift cost for parity work.
- Plugin-centric architecture: rejected as the core because plugins and adapters are useful frontends, not the canonical operating model.

## Migration Steps

1. Declare Claude Code as the default orchestrator for active work in workspace-hub.
2. Keep `AGENTS.md` as the canonical contract and continue treating `.codex` and `.gemini` as provider adapters.
3. Route more bounded build, test, refactor, and review tasks to Codex by default once Claude has framed the task.
4. Restrict Gemini to explicit research, comparison, and large-context synthesis requests.
5. Stop creating new workflow logic in `.hive-mind`, `.swarm`, or `.SLASH_COMMAND_ECOSYSTEM` unless a live workflow proves it is still required.
6. When provider-specific commands are needed, make them thin frontends over the same workflow intent instead of separate control planes.
7. Prefer deleting or freezing stale provider-specific leftovers over trying to preserve behavior parity everywhere.

## Do Less Harness

Rules for the next 30-60 days:

- Do not build a large provider-neutral framework.
- Do not standardize on slash commands as the core abstraction.
- Do not chase command parity across all providers.
- Do not treat provider plugins or adapters as the architecture center.
- Do not make three-provider review mandatory for every task.
- Do not expand cross-review routing beyond the minimal default until current Claude/Codex/Gemini paths are reliable.
- Do use one canonical workflow contract and thin provider adapters.
- Do prefer human-readable architecture notes and small scripts over new orchestration layers.
- Do remove or freeze stale surfaces that create ambiguity about the real control plane.

Practical interpretation:

- one orchestrator
- one canonical contract
- one main worker lane
- one narrow research lane

## Adversarial Review

Strongest case against this recommendation:

- Claude as default orchestrator may deepen lock-in around the thickest current surface instead of reducing it.
- Codex may be better used as the orchestrator in some coding-heavy sessions because it is closer to patch generation.
- Gemini has a 1M-token context and could be the better synthesis hub for some planning tasks.
- Freezing parity work now might leave the repo permanently inconsistent across providers.
- Requiring adversarial review could still add process weight and latency.

Why the recommendation still holds:

- The problem in #1514 is not lack of theoretical options. It is too much harness drift relative to the value produced.
- The repo already shows a de facto architecture: `.claude` as the thick surface, `.codex` and `.gemini` as adapters, plus extra legacy control planes.
- The related issues show reliability problems in provider-specific review and dispatch flows, which argues for narrowing responsibilities, not widening them.
- The paid account mix strongly favors Claude for orchestration quality and Codex for cheap execution capacity.
- A two-provider review default preserves most of the value of adversarial review without forcing a three-provider tax on normal work.
- A minimal asymmetric model can be reversed later. A new framework creates maintenance immediately.

Conclusion from adversarial review:

The main risk is overcommitting to the current Claude-heavy shape. The mitigating move is not to build a neutral framework now. It is to keep the contract canonical in `AGENTS.md`, keep adapters thin, and delay any larger control-plane work until this simpler model clearly fails.
