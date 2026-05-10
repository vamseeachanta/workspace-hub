# Iter-Shape Recipes

How to structure a single iter's agent fanout. Default is 4-agent parallel; the bundled-sequential exception applies when there's a hard dependency. This file captures the empirical lessons including the W231 race-block.

## Default: 4-Agent Fanout

```
iter-N
├── Lane A (audit, read-only)
├── Lane B (content lane 1)
├── Lane C (content lane 2)
└── Lane D (content lane 3)
```

**Why 4 agents:** llm-wiki experimented with 1, 2, 3, 5, and 6-agent iters. 4 is the sweet spot:

- Below 4 (1-3 agents): throughput-limited; iter cycle time dominates. Substrate-fill at <4 agents took 2-3x longer per iter.
- Above 4 (5-6 agents): race-conflict frequency rises non-linearly. With 5 agents, ~30% of iters had at least one merge conflict requiring resolution. With 6, ~50%.
- 4 agents: race conflicts are rare (<10% of iters); throughput is high.

**Audit lane is constant.** The audit lane (A) runs every iter regardless of phase. Skipping the audit causes iter-N+1 to mis-target gap-clusters.

**Content lanes vary by phase:**

- Phase 1: B = resolver-fill, C = concept-page-creation, D = cross-wiki bridge
- Phase 2: B/C/D = depth-expansion agents, each owning ~3-4 pages from the ranked list
- Phase 3: B/C/D = orphan-fix / bridge-reciprocation / frontmatter / link-repair (depending on diagnostic vs execution iter)

## Race-Management Discipline

Three rules keep race conflicts <10%:

### Rule 1: Lanes own disjoint file-sets at iter-start

Before kickoff, each agent receives an explicit file-set or topic-region. Two agents should never start the iter with overlapping file-sets. The audit doc's iter-N+1 recommendation is responsible for partitioning.

### Rule 2: Cross-wiki bridge lanes touch both wikis

The bridge lane (Phase 1, Lane D) is the exception that proves the rule — it intentionally touches both sides. Mitigation: bridge lane runs **after** content lanes B and C land, not in parallel. This serializes the cross-wiki touches.

### Rule 3: Execution iters in Phase 3 may need worktrees

Phase-3 execution iters (orphan-removal, link-repair) often touch overlapping link-graph state. If diagnostic reports show overlap, run execution lanes in worktrees and merge sequentially. See `feedback_worktree_isolation_large_repo_cost.md` for the cost trade-off.

## Bundled-Sequential Exception (W231 Race-Block Lesson)

**The pattern that almost broke llm-wiki:** in W231, two parallel agents had a sequential dependency that wasn't recognized at iter-kickoff:

- Agent 1: create resolver-page X (new file)
- Agent 2: create concept-page Y (new file) that links to X

If Agent 2 started before Agent 1's commit landed, Agent 2's outbound link to X was a broken link. If Agent 2 ran after Agent 1, the link resolved. The race was non-deterministic; some iters produced broken links, some didn't.

**Two valid resolutions:**

1. **Bundle into a single agent** (preferred when dependency is tight). Agent 1 creates both X and Y in one PR. No race because no parallelism.

2. **Parallel-wait with SendMessage** (when bundling is unwieldy). Agent 1 creates X, commits, then sends a message to Agent 2. Agent 2 waits for the message before creating Y. Use the SendMessage primitive (see `dispatching-parallel-agents` skill).

**Anti-pattern:** "we'll just retry if it breaks." Race-driven broken links are detected by the Phase-3 link-integrity check, not at iter-time. They accumulate silently and surface as a Phase-3 backlog.

## Detecting Hidden Sequential Dependencies

Before assigning lanes, ask for each pair of lanes:

1. Does Lane X create a new file that Lane Y links to?
2. Does Lane X delete a file that Lane Y links to?
3. Does Lane X rename a file that Lane Y references?
4. Does Lane X modify frontmatter that Lane Y reads (e.g., `code_id`)?

If any answer is yes, the lanes have a sequential dependency. Either bundle them or use parallel-wait.

## Audit-Lane Independence

The audit lane is parallel-safe with all content lanes because it's read-only. Audit reads the wiki state at iter-start (the commit before any content lane lands). The audit doc reflects pre-iter state, not mid-iter state.

This is by design: the audit is forward-looking ("what should iter-N+1 do?"), so it bases recommendations on the most recent stable state. Mid-iter state is unstable and shouldn't drive recommendations.

## Iter Kickoff Checklist

- [ ] Audit doc V<N-1>.md exists and has iter-N lane recommendations
- [ ] Each lane has a disjoint file-set or topic-region
- [ ] Hidden-sequential-dependency check passed for all lane pairs
- [ ] Audit lane (A) is launched first (or in parallel if reading prior commit)
- [ ] Content lanes (B/C/D) have explicit success criteria from V<N-1>
- [ ] Phase-3 execution iters: worktree decision made (yes if link-graph overlap, no otherwise)

## Iter Closure Checklist

- [ ] All 4 lanes report completion
- [ ] No merge conflicts unresolved
- [ ] Audit doc V<N>.md committed and reflects post-iter state
- [ ] Iter-N+1 lane assignments drafted (in V<N>.md section 6)
- [ ] Race-conflict count for this iter logged (to track <10% target)

## Reference Exemplar

llm-wiki commits show 4-agent fanout pattern from V8 onward (V1-V7 were solo or 2-agent). W231 work-item history captures the race-block recovery.
