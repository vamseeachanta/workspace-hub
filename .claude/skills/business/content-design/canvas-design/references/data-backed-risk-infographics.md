# Data-backed risk infographic workflow

Use when a visual artifact must translate a source document plus repository data into a stakeholder-facing risk narrative.

## Pattern

1. Extract the source document's decision themes first: hazards, decisions avoided, mitigations, responsible parties, and operational timeline.
2. Locate repository datasets that can quantify the narrative. Prefer canonical data under `data/` or module input folders over ad hoc copied CSVs.
3. Create a small statistics sidecar next to the visual artifact, e.g. `*_stats.json`, containing:
   - source file paths
   - record counts and filtered counts
   - derived percentages
   - severity/category breakouts
   - timestamp or code version if applicable
4. Build the primary visual as self-contained HTML when the artifact benefits from styled layout, then export static PNG/PDF for sharing.
5. Make the risk story explicit: pair each statistic with an avoidable failure mode and a corresponding planning/engineering control.
6. Verification before handoff:
   - HTML parses/loads without missing local assets
   - PNG dimensions are suitable for preview/sharing
   - PDF export is readable and not clipped
   - source-data provenance is visible in the artifact or sidecar
   - git status identifies whether artifacts are untracked, staged, or committed

## Recommended artifact set

```text
reports/modules/<domain>/<name>.html
reports/modules/<domain>/<name>_stats.json
reports/modules/<domain>/assets/<name>.png
reports/modules/<domain>/assets/<name>.pdf
```

## Pitfalls

- Do not make a polished visual first and then backfill statistics. Compute and preserve the stats sidecar before final copy/layout tuning.
- Do not cite incident counts without naming the exact dataset files used.
- Do not rely on only an HTML artifact for stakeholder use; export PNG/PDF unless the user explicitly wants web-only delivery.
- Do not claim completion until the rendered static exports have been checked for clipping/readability.
