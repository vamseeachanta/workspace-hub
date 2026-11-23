# Research & Literature — Templates

## Research Brief Template

```yaml
# research-brief-<category>-<subcategory>.yaml
category: "<category>"
subcategory: "<subcategory>"
generated: "YYYY-MM-DD"

applicable_standards:
  - id: "<STANDARD-ID>"
    title: "<full title>"
    org: "<DNV/API/ISO/etc>"
    status: "available|needs_download|paywalled"
    doc_path: "<path in index or null>"
    key_sections: ["Sec X.Y — relevant topic"]

available_documents:
  - path: "<path from index>"
    source: "<og_standards|ace_standards|etc>"
    summary: "<from Phase B if available>"
    relevance: "high|medium|low"

download_tasks:
  - standard: "<STANDARD-ID>"
    url: "<where to find it>"
    notes: "paywalled — check ace_standards first"

key_equations:
  - name: "<equation name>"
    standard: "<STANDARD-ID>"
    section: "<Sec X.Y>"
    latex: "<LaTeX if known>"
    description: "<what it computes>"

university_resources:
  - source: "<textbook/course/lecture>"
    title: "<title>"
    author: "<author or institution>"
    relevance: "high|medium|low"
    archived_at: "knowledge/dark-intelligence/<category>/<subcategory>/<filename>"
    worked_examples_count: N
    notes: "<what makes this useful>"

worked_examples:
  - source: "<STANDARD-ID or textbook>"
    section: "<Sec X.Y or Ch N>"
    description: "<example problem description>"
    inputs: {}
    expected_output: {}
    use_as_test: true  # flag for TDD test generation

implementation_target:
  repo: "<digitalmodel|worldenergydata|etc>"
  module: "<discipline>/<module>"
  existing_code: "<path if any>"
  calc_report_template: "examples/reporting/<name>.yaml"
```

## Domain-to-Repo Mapping

See `config/research-literature/domain-repo-map.yaml` for the full mapping.

| Domain | Repo | Tier |
|--------|------|------|
| geotechnical | digitalmodel | 1 |
| cathodic_protection | digitalmodel | 1 |
| structural | digitalmodel | 1 |
| hydrodynamics | digitalmodel | 1 |
| drilling | OGManufacturing | 1 |
| pipeline | digitalmodel | 1 |
| bsee | worldenergydata | 1 |
| metocean | worldenergydata | 1 |
| subsea | digitalmodel | 1 |
| naval_architecture | digitalmodel | 1 |
| mooring | digitalmodel | 2 |
| risers | digitalmodel | 2 |
| economics | worldenergydata | 3 |
