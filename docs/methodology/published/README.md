# Methodology Publications Index

Publication-ready versions of ACE Engineering methodology documents for [aceengineer.com](https://aceengineer.com).

## Pages

| File | Website Path | Target Audience | Status |
|------|-------------|-----------------|--------|
| [compound-engineering-public.md](compound-engineering-public.md) | `/methodology/compound-engineering` | Engineering managers evaluating consultants | Ready for publication |
| [enforcement-over-instruction-public.md](enforcement-over-instruction-public.md) | `/methodology/enforcement` | Quality assurance teams, technical evaluators | Ready for publication |
| [orchestrator-worker-public.md](orchestrator-worker-public.md) | `/methodology/orchestrator-worker` | Technical directors, project managers | Ready for publication |
| [multi-agent-parity-public.md](multi-agent-parity-public.md) | `/methodology/multi-agent-parity` | Technical directors, tool maturity evaluators | Ready for publication |

## Source Documents

Each published page is derived from an internal methodology document in `docs/methodology/`. The internal versions contain implementation details (issue numbers, file paths, script references) that are not appropriate for client-facing content.

| Internal Document | Published Version | Key Changes |
|-------------------|-------------------|-------------|
| `compound-engineering.md` | `compound-engineering-public.md` | Removed issue numbers, internal paths, agent subscription costs; reframed for engineering managers |
| `enforcement-over-instruction.md` | `enforcement-over-instruction-public.md` | Removed hook file paths, script names, internal config details; generalized enforcement examples |
| `orchestrator-worker.md` | `orchestrator-worker-public.md` | Removed terminal launch commands, provider names, git worktree details; reframed for project delivery |
| `multi-agent-parity.md` | `multi-agent-parity-public.md` | Removed agent names, subscription costs, bridge script paths; generalized to "tools and team members" |

## Publication Notes

- All published pages include a call-to-action linking to aceengineer.com/contact
- Internal references (GitHub issue numbers, file paths, script names) have been removed
- Technical depth is preserved but made accessible to non-practitioner audiences
- The `compliance-dashboard.md` and `knowledge-to-website-pipeline.md` internal docs are not published (per issue #2030 scope)

## Deployment

These markdown files are ready for conversion to HTML using the aceengineer.com site template. See issue #2030 for deployment tracking.
