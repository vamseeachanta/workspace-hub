# Oracle Fixture Authoring Guide

Oracle fixtures under this directory are human-authored (or agent-authored per the
`from-source` protocol) ground-truth markdown representations of the paired `.html`
snapshots. They are the reference against which `html_to_markdown()` output is scored.

## Directory layout

```
conversion-oracle/
  README.md                     # this file
  sample-manifest.yaml          # 20-entry stratified sample manifest
  sample-manifest.schema.json   # JSON Schema for manifest validation
  {slug}.html                   # frozen HTML snapshot
  {slug}.md                     # oracle markdown (from-source, provenance in HTML comments)
```

## Oracle metadata format (v6)

Every oracle `.md` file MUST start with HTML-comment provenance metadata — one field
per line — so the heading-preservation regex `^(#{1,6})\s+(.*)$` can NEVER match a
metadata line (HTML comments do not start with `#`):

```
<!-- oracle_authored_by: <github-handle> -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: <ISO-8601 UTC> -->
<!-- oracle_second_reviewer: <handle | "self-reviewed-with-24h-delay"> -->
<!-- oracle_reviewed_at: <ISO-8601 UTC> -->
<!-- single_reviewer_timelag: <true | false> -->
<!-- source: <source_url> -->
```

The same fields must appear in `sample-manifest.yaml` for the same slug; test #16
(`test_oracle_md_provenance_matches_manifest`) enforces that the two sources agree.

## Blinding protocol

1. Open the `.html` snapshot file in a browser (or read the raw HTML directly).
2. Write the oracle `.md` based solely on what the HTML should render to.
3. **NEVER view `html_to_markdown()` output during authorship or re-review.**
4. Two-reviewer sign-off required, OR the 24-hour-delay solo path (below).

### Solo-contributor 24-hour-delay path

If a second reviewer is unavailable:

1. At `T0`: write the `.md` from HTML only. Commit with `fixture(initial): <slug>`.
   Record `oracle_authored_at: T0` in manifest and HTML-comment header.
2. At `T0 + ≥24h`: re-open ONLY the `.html` file or the live URL. Confirm or amend
   the fixture in a second commit `fixture(second-review): <slug>`. Set
   `oracle_reviewed_at` to the re-review timestamp.
3. Set `oracle_second_reviewer: self-reviewed-with-24h-delay` and
   `single_reviewer_timelag: true` in both the manifest and HTML-comment header.

## Conflict resolution

If two reviewers disagree on a specific cell or structure:

1. Open a `fixture-disagreement` comment on #2126 citing file and element.
2. Both annotate the HTML element they interpret.
3. If unresolved after one round, use the rendered view at `source_url`.
4. If still unresolved, swap the topic out and record `previous_slug` in the manifest.

## Hard-tier encoding_stress candidates (v6 step-0 pre-scan)

`data/llm-wiki/` is gitignored and was not present in the execution environment at
plan-execution time (2026-04-26), so the prescribed corpus grep could not be run:

```
grep -lE '\xc2\xb0|[\xce\xb1-\xcf\x89]|[\xe2\x88]' data/llm-wiki/orca*/topics/*.html | head -8
```

Known encoding-stress topics in OrcaFlex webhelp based on documentation structure:

| Slug | Reason |
|---|---|
| `orcaflex-coordinate-system` | α, β, θ, φ angles; degree sign (°) |
| `orcaflex-wave-kinematics` | ω angular frequency; ∑, ∂ operators |
| `orcaflex-dynamics-theory` | ρ density; α, β damping ratios |
| `orcaflex-fatigue-theory` | σ stress; Δ delta; ε strain |
| `orcawave-diffraction-theory` | ω, θ; Σ summation |
| `orcaflex-modal-analysis` | φ mode shapes; λ eigenvalues |
| `orcaflex-line-bending` | κ curvature; θ angle |
| `orcawave-radiation-theory` | μ, ν fluid coefficients |

The current manifest uses `orcaflex-coordinate-system` and `orcaflex-wave-kinematics`
as the two `encoding_stress: true` Hard-tier entries, satisfying the `>=2` requirement.

When `data/llm-wiki/` becomes available, run the grep above to refresh this list
and optionally swap in higher-quality real-page snapshots.
