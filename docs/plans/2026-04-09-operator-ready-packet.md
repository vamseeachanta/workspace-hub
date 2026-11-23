# Operator-ready packet (2026-04-09)

This packet consolidates the Claude worker outputs into one place for immediate operator use.

## Primary artifacts

### Execution packs
- `docs/plans/claude-followup-2026-04-09/results/issue-2059-execution-pack.md`
- `docs/plans/claude-followup-2026-04-09/results/issue-2063-execution-pack.md`
- `docs/plans/claude-followup-2026-04-09/results/issue-2056-execution-pack.md`

### Refinement drafts
- `docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md`

### Ops packs
- `docs/plans/claude-ops-2026-04-09/results/plan-review-command-pack.md`
- `docs/plans/claude-ops-2026-04-09/results/refinement-application-pack.md`
- `docs/plans/claude-ops-2026-04-09/results/implementation-launch-pack.md`

## Recommended next sequence

1. Refine blocked/lower-confidence issues first
   - apply refinement pack for `#2055` and `#2062`
   - artifact: `docs/plans/claude-ops-2026-04-09/results/refinement-application-pack.md`

2. Move top implementation issues to plan review
   - `#2059`
   - `#2063`
   - `#2056`
   - artifact: `docs/plans/claude-ops-2026-04-09/results/plan-review-command-pack.md`

3. After user approval, move approved issues to `status:plan-approved`
   - same command pack as above

4. Launch implementation batch using the implementation launch pack
   - artifact: `docs/plans/claude-ops-2026-04-09/results/implementation-launch-pack.md`

## Best first implementation batch

1. `#2059` — highest confidence, smallest delta, mostly test-only
2. `#2063` — focused adapter work in `digitalmodel`
3. `#2056` — governance hooks, parallel-safe but most operationally sensitive

## Parallelization guidance

Run all 3 implementation issues in parallel after labels are approved.

Why this is safe:
- `#2059` touches `digitalmodel/tests/naval_architecture/` and maybe a small conditional edit in `ship_data.py`
- `#2063` touches `digitalmodel/src/digitalmodel/drilling_riser/` and `digitalmodel/tests/drilling_riser/`
- `#2056` touches `.claude/hooks/`, `.claude/settings.json`, `scripts/enforcement/`, `tests/hooks/`, governance docs
- zero file overlap across the three issue scopes

Important coordination note:
- `#2059` and `#2063` both require `digitalmodel/` submodule pointer updates in workspace-hub after their inner `digitalmodel` commits land
- those pointer updates must be serialized: merge/update the `#2059` pointer first, then rebase/apply the `#2063` pointer update second

## Caveats

### `#2055`
- do not approve for implementation until refinement is applied and data prerequisites are accepted

### `#2062`
- refine title/scope before implementation
- realistic v1 scope is ~138 rigs with geometry, not all 2,210 rigs

## Immediate operator checklist

- [ ] Review `refinement-application-pack.md`
- [ ] Backup current bodies for `#2055` and `#2062`
- [ ] Apply refined issue bodies for `#2055` and `#2062`
- [ ] Review `plan-review-command-pack.md`
- [ ] Move `#2059`, `#2063`, `#2056` to `status:plan-review`
- [ ] Review execution packs for those 3 issues
- [ ] After approval, move selected issues to `status:plan-approved`
- [ ] Launch implementation agents using `implementation-launch-pack.md`

## Fast-start file order for a human operator

1. `docs/plans/2026-04-09-operator-ready-packet.md`
2. `docs/plans/claude-ops-2026-04-09/results/refinement-application-pack.md`
3. `docs/plans/claude-ops-2026-04-09/results/plan-review-command-pack.md`
4. `docs/plans/claude-ops-2026-04-09/results/implementation-launch-pack.md`

## Final recommendation

Proceed in this order:
1. refine `#2055` and `#2062`
2. submit `#2059`, `#2063`, `#2056` for plan review
3. approve the subset you want to execute first
4. launch all approved implementation issues in parallel
