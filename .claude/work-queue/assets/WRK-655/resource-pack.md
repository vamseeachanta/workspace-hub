# Resource Pack

## Problem Context

`WRK-655` operationalizes the `Resource Intelligence` stage defined in `WRK-624` so that agents follow one canonical workflow instead of ad hoc research steps.

## Relevant Documents/Data

- `AGENTS.md`
- `specs/wrk/WRK-624/plan.md`
- `assets/WRK-624/wrk-624-workflow-review.html`
- `data/document-index/registry.yaml`
- `data/document-index/index.jsonl`
- `data/document-index/mounted-source-registry.yaml`

## Constraints

- Existing document-intelligence sources must be complemented, not duplicated.
- User pause is required when unresolved `P1` gaps remain.
- Legal-sanity evidence must be recordable.
- YAML is canonical where paired YAML/Markdown tracking exists.

## Assumptions

- `workspace_spec`, `ace_project`, `ace_standards`, `og_standards`, and `dde_project` are valid existing source buckets.
- A dedicated canonical skill is preferable to extending multiple looser skills.

## Open Questions

- Whether routing authority should require full capability review immediately or accept an interim rule first.

## Domain Notes

- This is workflow/governance work with direct coupling to queue validators and document-intelligence assets.

## Source Paths

- `/mnt/local-analysis/workspace-hub`
- `/mnt/ace/docs`
- `/mnt/ace/0000 O&G`
- `/mnt/remote/ace-linux-2/dde`
