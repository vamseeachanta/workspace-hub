# Work Queue Workflow

Canonical linear workflow for every `WRK-*` item:

```text
CAPTURE -> TRIAGE -> PLAN -> CLAIM -> IMPLEMENT -> CROSS-REVIEW -> CLOSE -> ARCHIVE
   |         |        |       |          |              |             |         |
 pending/  pending/ pending/ working/  working/      working/       done/    archive/
```

## Stage Contract

| Stage | Folder | Required outcome |
|-------|--------|------------------|
| Capture | `pending/` | WRK created with baseline frontmatter |
| Triage | `pending/` | Priority, complexity, route, provider, computer assigned |
| Plan | `pending/` or `specs/wrk/WRK-<id>/` | Plan drafted and approved |
| Claim | `working/` | Active ownership and readiness confirmed |
| Implement | `working/` | Files changed and tests run |
| Cross-Review | `working/` | Required reviews collected and major findings resolved |
| Close | `done/` | Frontmatter updated, file moved, index regenerated |
| Archive | `archive/` | Merge and sync complete; item archived |

## Close Command

Use the closure helper rather than manual queue edits:

```bash
scripts/work-queue/close-item.sh WRK-NNN <commit-hash> [--commit]
```

## Completion Checklist

```markdown
## Completion Checklist
- [ ] Implementation committed: <hash>
- [ ] Tests pass: <command + result>
- [ ] Cross-review passed: <paths or summary>
- [ ] WRK frontmatter updated: status=done, percent_complete=100, commit=<hash>
- [ ] File moved to `done/`
- [ ] INDEX regenerated
- [ ] Hub state committed or intentionally left uncommitted
```
