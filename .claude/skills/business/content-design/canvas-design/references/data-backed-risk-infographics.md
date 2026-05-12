# Data-backed risk infographic workflow

Use when a visual artifact must translate a source document plus repository data into a stakeholder-facing risk narrative.

## Pattern

1. Extract the source document's decision themes first: hazards, decisions avoided, mitigations, responsible parties, and operational timeline.
2. Locate repository datasets that can quantify the narrative. Prefer canonical data under `data/` or module input folders over ad hoc copied CSVs.
3. Before designing, define a metric contract for every displayed number:
   - dataset path(s) and source document path
   - inclusion/exclusion rules
   - matched incident IDs or record identifiers for each key count
   - calculation formula for percentages/rates
   - caveats and timestamp/code version
4. Create a small statistics sidecar next to the visual artifact, e.g. `*_stats.json`, containing:
   - source file paths
   - record counts and filtered counts
   - derived percentages
   - severity/category breakouts
   - timestamp or code version if applicable
   - matched incident IDs / row identifiers for auditability
5. Build the primary visual as self-contained HTML when the artifact benefits from styled layout. Export static PNG/PDF only when requested or size-safe; if binary bloat is a concern, deliver HTML + JSON first and document the gated static-export step.
6. Make the risk story explicit: pair each statistic with an avoidable failure mode and a corresponding planning/engineering control.
7. Verification before handoff:
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
- Do not treat an existing infographic/draft as irrelevant just because it is not fully data-backed. Use it as a positioning/reference artifact, then replace unsupported claims with auditable statistics.
- Do not count control rows, synthetic examples, or non-incident records as incidents. Explicitly exclude rows whose IDs/categories mark them as controls or non-incidents, and preserve that exclusion rule in the stats sidecar.
- Do not cite incident counts without naming the exact dataset files used and the matched incident IDs.
- Do not add PNG/PDF exports automatically when artifact size or repo hygiene is a concern; default to HTML + JSON and gate static exports unless the user needs shareable files.
- Do not claim completion until the rendered static exports have been checked for clipping/readability when static exports are part of scope.
