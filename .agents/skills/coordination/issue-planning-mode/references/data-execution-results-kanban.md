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
3. **Keep planning work and implementation work separate.** Planning/recon/delegated review establish the implementation basis. The task request or standing authority authorizes implementation without a separate plan-approved label or local approval marker; planning, TDD, reviews and required domain decisions remain controls. Honor explicit planning-only requests.
4. **Delegate by layer and work type.** Typical split:
   - Codex: deterministic repo edits, plan drafting, test scaffolding, narrow file work
   - Claude: broad orchestration, plan synthesis, cross-issue dependency reasoning
   - Gemini: read-only adversarial review, metadata-only disposition analysis, large-context consistency checks
5. **Verify every delegate claim in the orchestrator context.** For each delegated lane, check:
   - intended worktree/path
   - `git status --short`
   - expected plan/report/review artifacts exist
   - issue comments/labels were actually posted/applied if claimed
6. **Reconcile live scope and blockers before implementation.** Inspect the current issue, plan, review findings and task/standing authority before launching write-capable work. Labels, local markers, branch names and README rows are display evidence, not prerequisites or authorization. Preserve approval history; do not remove markers opportunistically.
7. **Recover from sandbox/write limits without losing the gate.** If a delegated agent cannot write into the orchestrator checkout, pull the useful reasoning into the orchestrator, create the canonical artifact directly, and then run/record adversarial review before changing live issue state.
8. **Surface a concise execution checkpoint.** List reviewed plans, unresolved upstream/domain blockers and the recommended execution order. Continue authorized implementation without asking for separate plan approval. Never self-apply `status:plan-approved`; consequential actions outside existing authority require explicit authorization.
9. **After downstream work completes, reconcile the parent board/epic.** Re-check each child issue live state, close stale-open completed child issues only after evidence exists, then post a compact parent roll-up table with layer, issue, state, evidence, and remaining adjacent work. Keep unrelated residue (for example backup disposition or storage cleanup) as a separate lane instead of mixing it back into the completed data→execution→results flow.

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
- Wave B — authorized implementation in isolated worktrees
- Wave C — result-layer validation and closeout after upstream gates clear

## Execution checkpoint

List each issue with task/standing authority, reviewed plan, unresolved blockers and next implementation action:
1. #<issue>
2. #<issue>
```

## Pitfalls

- Do not collapse a data→execution→results portfolio into one mega-plan when child issues can be independently reviewed and dispatched.
- Do not treat a board/report as implementation approval. It is an orchestration artifact only.
- Do not trust delegate self-reports for commits, labels, or comments; verify with local repo state or issue state before telling the user work is complete.
- Do not let result-layer output work start before source/provenance and execution interface contracts are explicit.
- Do not treat stale local approval markers, prompt artifacts, branch names, or README rows as authority. Re-check current task scope, blockers and review evidence before each write-capable delegation wave.
- If a result/output issue is technically `status:plan-approved` but its own plan names upstream data/execution contracts as blockers, keep it parked until those upstream contracts land or the reviewed plan explicitly defines an authorized mock/stub boundary.
- Do not leave a parent board/epic stale after children close. Post a final layer-by-layer roll-up and explicitly name the next lane so the user is not left with an obsolete Kanban picture.
- Do not blend adjacent cleanup/storage-disposition issues into a completed architectural flow. Preserve them as separate follow-on work with their own blocker/evidence surface.
