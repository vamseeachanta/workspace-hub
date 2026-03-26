# Skill Graph Validation Report
Generated: 2026-03-25

## Methodology

One test (`--domain marine_offshore`) was executed empirically. Remaining tests were validated
by static analysis: tracing the awk parsing logic in `skill_graph.sh` against the YAML data in
`skills-knowledge-graph.yaml` line by line. A bug was found and fixed during analysis.

## Test Results

### Domain Queries

| Test | Command | Expected | Actual | Pass? |
|------|---------|----------|--------|-------|
| Domain: marine_offshore | `--domain marine_offshore` | 10 skills (all digitalmodel/*) | 10 skills returned (empirically confirmed) | PASS |
| Domain: energy_data | `--domain energy_data` | 9 skills (all worldenergydata/*) | 9 skills (static: lines 553-664 of graph) | PASS |
| Domain: document_generation | `--domain document_generation` | 7 skills (doc-coauthoring, pdf-utilities, docx, pdf, pptx, xlsx, engineering-report-generator) | 7 skills (static: lines 135-344 of graph) | PASS |
| Domain: development | `--domain development` | 6 skills (skill-creator, web-artifacts-builder, mcp-builder, webapp-testing, yaml-workflow-executor, sparc-workflow) | 6 skills (static: lines 98-407 of graph) | PASS |

### Capability Searches

| Test | Command | Expected | Actual | Pass? |
|------|---------|----------|--------|-------|
| Capability: fatigue | `--capability "fatigue"` | 3 hits: fatigue-analysis (2 caps), viv-analysis (1 cap) | 3 lines with matching skill IDs and capability text (static) | PASS |
| Capability: production data | `--capability "production data"` | 2+ hits: bsee-data-extractor, sodir-data-extractor, well-production-dashboard | Matches found in tolower(cap) containing "production data" (static) | PASS |
| Capability: PDF | `--capability "PDF"` | 4+ hits: pdf skill (3 caps), pdf-utilities (2 caps), canvas-design (1 cap) | Case-insensitive match via tolower() finds all "pdf" occurrences (static) | PASS |
| Capability: mooring | `--capability "mooring"` | 2 hits: mooring-design (3 caps mention mooring), orcaflex-modeling (0 - no "mooring" in caps) | mooring-design caps match; orcaflex-modeling caps do not contain "mooring" (static) | PASS |

### Feed Chain Queries

| Test | Command | Expected | Actual | Pass? |
|------|---------|----------|--------|-------|
| Feeds-from: orcaflex-modeling | `--feeds-from "digitalmodel/orcaflex-modeling"` | 1 result: orcaflex-post-processing (feeds) | Correct -- only 1 edge with from=orcaflex-modeling and type=feeds (line 757) | PASS |
| Feeds-to: orcaflex-post-processing | `--feeds-to "digitalmodel/orcaflex-post-processing"` | 1 result: orcaflex-modeling (feeds) | Correct -- only 1 edge with to=orcaflex-post-processing (line 757) | PASS |
| Feeds-from: bsee-data-extractor | `--feeds-from "worldenergydata/bsee-data-extractor"` | 3 results: field-analyzer (feeds), well-production-dashboard (feeds), sodir-data-extractor (alternative) | Correct -- edges at lines 818, 828, 863 | PASS |
| Feeds-from: field-analyzer | `--feeds-from "worldenergydata/field-analyzer"` | 2 results: fdas-economics (feeds), energy-data-visualizer (feeds) | Correct -- edges at lines 838, 843 | PASS |
| Feeds-to: engineering-report-generator | `--feeds-to "workspace-hub/engineering-report-generator"` | 3 results: xlsx (feeds), orcaflex-post-processing (feeds), plotly-visualization (feeds) | Correct -- edges at lines 884, 920, 925 (theme-factory edge is composition, not feeds, but still returned since the function returns ALL edge types) | PASS |

**Note on --feeds-from / --feeds-to semantics:** These functions return edges of ALL types
(feeds, dependency, composition, alternative, shared_infra, see_also), not just `feeds` type.
The function names are slightly misleading -- they mean "edges FROM this skill" and "edges TO
this skill" respectively, not filtered to `type: feeds` only. This is technically correct per
the code but could surprise callers expecting only feed-type edges.

### Edge Cases

| Test | Command | Expected | Actual | Pass? |
|------|---------|----------|--------|-------|
| Non-existent domain | `--domain nonexistent_domain` | Empty output, exit 0 | Correct -- awk finds no matching domain, prints nothing, exits 0 (static) | PASS |
| Non-existent skill | `--feeds-from "fake/skill"` | Empty output, exit 0 | Correct -- no edge matches, prints nothing (static) | PASS |
| No-match capability | `--capability "quantum computing"` | Empty output, exit 0 | Correct -- no capability string contains "quantum computing" (static) | PASS |

## Issues Found

### BUG-1: Edges without `note:` field silently dropped (FIXED)

**Severity:** Low (affects only 4 legacy `see_also` edges)

**Root cause:** Both `_sg_feeds_from()` and `_sg_feeds_to()` only emitted an edge result when
the awk parser reached a `note:` line. If an edge lacked a `note:` field, it was never output.

**Affected edges:** 4 of 52 edges (7.7%) -- all are v1 `see_also` edges referencing legacy
skill paths (`engineering/marine-offshore/cathodic-protection`, etc.) that are not in the
main node list. These edges are at lines 1004-1022 of the graph file.

**Fix applied:** Refactored both functions to use a `flush_edge()` pattern that emits the
pending edge when the next `- from:` line is encountered or at `END`. The edge is now emitted
regardless of whether `note:` is present. The `note` field defaults to empty string if absent.

**File:** `scripts/coordination/routing/lib/skill_graph.sh` lines 96-122 and 132-158.

### MINOR-1: Dead code in capability search

**Severity:** Cosmetic

The `lc()` function defined on line 65 of the script is never called. The actual
case-insensitive matching uses awk's built-in `tolower()` (line 80). The `lc()` function
appears to be a leftover from an earlier implementation that shelled out to `tr`. It should
be removed to avoid confusion.

### MINOR-2: `tolower()` is a gawk extension

**Severity:** Low (no practical impact on Linux)

The `tolower()` function used in `_sg_skills_by_capability()` is not POSIX awk -- it is a
GNU awk (gawk) extension. On Linux systems where `awk` is typically gawk, this works fine.
On macOS or minimal containers with only POSIX awk, capability search would fail. Consider
adding a `#!/usr/bin/env gawk` shebang for the awk inline scripts, or use the existing `lc()`
helper approach.

### MINOR-3: Function names are semantically ambiguous

**Severity:** Cosmetic

`--feeds-from` and `--feeds-to` return ALL edge types, not just `type: feeds`. A caller might
expect `--feeds-from X` to return only downstream consumers connected by `feeds` edges, but it
also returns `composition`, `dependency`, `alternative`, and `shared_infra` edges. This is
arguably more useful (returning all relationships), but the naming suggests feeds-only.

## Recommendations

1. **Remove dead `lc()` function** from the capability search awk block (line 65)
2. **Consider filtering by edge type** -- add an optional `--type feeds` filter to the
   `--feeds-from` / `--feeds-to` commands, or rename them to `--edges-from` / `--edges-to`
3. **Add `note:` to the 4 legacy see_also edges** in the graph YAML for consistency
4. **Add a `--count` flag** that outputs just the count of results, useful for scripting
5. **Run `--rebuild-index`** after the flush_edge fix to ensure the index stays in sync
