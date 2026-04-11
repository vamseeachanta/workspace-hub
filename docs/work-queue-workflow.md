# Work Queue Workflow

Status: Legacy compatibility note

## Canonical tracking model

Workspace-hub now tracks work in GitHub issues.

Canonical flow:

```text
GitHub Issue -> TRIAGE -> GSD PLAN (.planning/) -> IMPLEMENT -> CROSS-REVIEW -> CLOSE ISSUE
```

This aligns with:
- `AGENTS.md` — "Tasks tracked as GitHub issues — no local work-queue"
- GSD workflow as the active planning/execution framework
- `.planning/` as the canonical location for active planning artifacts

## What is legacy

Older local queue surfaces such as:
- legacy assistant-managed queue directories
- status buckets like `pending/`, `working/`, `done/`, `archive/`
- legacy queue helper scripts

are retained only for compatibility with older hooks, reports, or historical artifacts. They are not the canonical source of truth for new work intake.

For the highest-signal legacy path mappings from historical Claude sessions, see `docs/ops/legacy-claude-reference-map.md`.

## Current execution contract

| Stage | Canonical location | Required outcome |
|-------|--------------------|------------------|
| Capture | GitHub issue | Issue created with priority / complexity / route / machine context |
| Triage | GitHub issue | Scope, dependencies, provider, and machine assignment clarified |
| Plan | `.planning/` | GSD plan/spec drafted and approved |
| Implement | repo files + issue/plan links | Files changed and tests run |
| Cross-Review | review artifacts / issue comments | Required reviews collected and major findings resolved |
| Close | GitHub issue | Issue updated/closed with evidence and links |

## Legacy closure helper

The old local closure helper appears in historical artifacts, but that script is not present in the current checkout.

Do not invoke any legacy local closure helper as a live workflow step. For current completion flow, update evidence in `.planning/`, run required reviews, and close the GitHub issue as described above.

## Completion checklist for current workflow

```markdown
## Completion Checklist
- [ ] Implementation committed: <hash>
- [ ] Tests pass: <command + result>
- [ ] Cross-review passed: <paths or summary>
- [ ] GSD planning artifacts updated if needed
- [ ] GitHub issue updated with final evidence / links
- [ ] Issue closed or explicitly deferred with next step
```

## See also

- `AGENTS.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- `docs/modules/ai/MINIMAL_HARNESS_ARCHITECTURE_2026-03.md`
- [data repo](https://github.com/vamseeachanta/data) — document index, standards ledger, and research briefs consumed by execution work
