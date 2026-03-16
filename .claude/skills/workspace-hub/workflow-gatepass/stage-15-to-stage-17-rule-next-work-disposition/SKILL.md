---
name: workflow-gatepass-stage-15-to-stage-17-rule-next-work-disposition
description: 'Sub-skill of workflow-gatepass: Stage 15 to Stage 17 Rule (Next-Work
  Disposition).'
version: 1.0.6
category: workspace-hub
type: reference
scripts_exempt: true
---

# Stage 15 to Stage 17 Rule (Next-Work Disposition)

## Stage 15 to Stage 17 Rule (Next-Work Disposition)


Before Stage 17 (User Review - Implementation), any "next work" discovered from the
current WRK must be captured using one of these paths:

1. Update an existing WRK item with revised scope and set status to `pending`
   (or another appropriate non-closed status).
2. Spin off a new WRK item with explicit scope and links back to the source WRK.

The agent chooses the path, but the decision is mandatory evidence and must be
recorded in:
- `assets/WRK-<id>/evidence/future-work.yaml`
- stage ledger order 15 evidence reference (`stage-evidence.yaml`)

Use `specs/templates/future-work-template.yaml` for the canonical YAML artifact.
Optional human-readable mirror: `specs/templates/future-work-recommendations-template.md`.

**Category at Stage 15 (mandatory):**
Any WRK item generated during Future Work Synthesis must include inferred `category:` and
`subcategory:` fields. Run before writing the WRK file:
```bash
python scripts/work-queue/infer-category.py "<wrk-title>" "<brief-body-text>"
# Returns: {"category": "engineering", "subcategory": "pipeline"}
```
Write both fields into the frontmatter. Default to `uncategorised` only if the script is unavailable.

When documenting next work in markdown artifacts, use a table with an explicit
`Captured` column:
- `yes`/`✓` when captured as `existing-updated` or `spun-off-new`
- `no`/`✗` when identified but not yet captured (must be cleared before Stage 17)
