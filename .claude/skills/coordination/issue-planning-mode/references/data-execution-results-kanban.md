# Data → Execution → Results Kanban Planning Pattern

Use this when a user asks to review a family of GitHub issues around architectural flow such as a data layer, execution layer, and result/output layer, then asks to prepare a Kanban board and delegate work.

## Pattern

1. **Inventory issue portfolio first.** Identify issues by layer and dependency, not by issue number order alone:
   - Data/provenance/residency/source-freeze issues
   - Execution orchestration/backbone/gate issues
   - Result/output/report/client/publication issues
   - Cross-layer governance blockers and approval gates
2. **Create a reviewable board artifact.** Prefer a repo-tracked report under `docs/reports/YYYY-MM-DD-<topic>-execution-plan.md` that includes:
   - lane definitions
   - issue table with labels/status/plan path
   - dependency graph from data → execution → results
   - delegation wave plan by provider/agent
   - explicit approval-gate boundaries
3. **Keep planning work and implementation work separate.** Planning/recon/delegated review may run before approval; implementation lanes for issue work require `status:plan-approved` plus local approval marker and TDD.
4. **Delegate by layer and work type.** Typical split:
   - Codex: deterministic repo edits, plan drafting, test scaffolding, narrow file work
   - Claude: broad orchestration, plan synthesis, cross-issue dependency reasoning
   - Gemini: read-only adversarial review, metadata-only disposition analysis, large-context consistency checks
5. **Verify every delegate claim in the orchestrator context.** For each delegated lane, check:
   - intended worktree/path
   - `git status --short`
   - expected plan/report/review artifacts exist
   - issue comments/labels were actually posted/applied if claimed
6. **Recover from sandbox/write limits without losing the gate.** If a delegated agent cannot write into the orchestrator checkout, pull the useful reasoning into the orchestrator, create the canonical artifact directly, and then run/record adversarial review before changing live issue state.
7. **Surface a concise approval checkpoint.** End by listing which plans are in `status:plan-review`, which issues are blocked by upstream approvals, and the recommended approval order. Never self-apply `status:plan-approved`.

## Kanban lane template

```markdown
# <Topic> Data → Execution → Results Board

## Lanes

### Data layer
| Issue | Status | Owner/provider | Artifact | Blocker |
|---|---|---|---|---|

### Execution layer
| Issue | Status | Owner/provider | Artifact | Blocker |
|---|---|---|---|---|

### Results / output layer
| Issue | Status | Owner/provider | Artifact | Blocker |
|---|---|---|---|---|

## Dependency chain

```text
<data/source/provenance> → <execution/backbone> → <results/output/publication>
```

## Delegation waves

- Wave A — read-only inventory and plan drafting
- Wave B — approved implementation in isolated worktrees
- Wave C — result-layer validation and closeout after upstream gates clear

## Approval checkpoint

Do not implement these issues until the user approves the listed plans:
1. #<issue>
2. #<issue>
```

## Pitfalls

- Do not collapse a data→execution→results portfolio into one mega-plan when child issues can be independently reviewed and dispatched.
- Do not treat a board/report as implementation approval. It is an orchestration artifact only.
- Do not trust delegate self-reports for commits, labels, or comments; verify with local repo state or issue state before telling the user work is complete.
- Do not let result-layer output work start before source/provenance and execution interface contracts are explicit.
