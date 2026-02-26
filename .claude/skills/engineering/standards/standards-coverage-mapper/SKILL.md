---
name: standards-coverage-mapper
version: "1.0.0"
updated: 2026-02-26
category: engineering/standards
description: |
  Map and track implementation status of engineering standards across
  digitalmodel modules — gap analysis, clause-level coverage, and
  integration with WRK work items.
tags: [standards, coverage, gap-analysis, capability-map]
platforms: [linux, macos, windows]
invocation: standards-coverage-mapper
depends_on: []
requires: []
see_also:
  - geotechnical-engineering
---

# Standards Coverage Mapper Skill

Track which engineering standards are implemented, partially implemented,
or missing across digitalmodel modules. Uses the capability map YAML as
the single source of truth.

## When to Use This Skill

- Auditing standards coverage for a module or discipline
- Planning new WRK items based on standards gaps
- Updating the capability map after implementing a standard
- Cross-referencing standards clauses with code implementations

## Capability Map Location

```
specs/capability-map/digitalmodel.yaml
```

## Status Taxonomy

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| `implemented` | Full coverage of relevant sections | Maintenance only |
| `partial` | Some sections coded, gaps remain | Create WRK for remaining |
| `reference` | Standard referenced but not computed | Assess if computation needed |
| `gap` | Standard needed but not implemented | Create WRK item |

## Capability Map Entry Format

```yaml
- module: geotechnical/soil_models
  standards_count: 2
  standards:
  - id: API_RP_2GEO_Geotechnical_and_Foundation_Design
    title: API RP 2GEO Geotechnical and Foundation Design Considerations
    org: API
    discipline: geotechnical
    summary: |
      Soil characterisation, CPT correlation, pile capacity (Sec 6-8),
      foundation design considerations.
    status: gap
```

## Gap Identification Workflow

1. **Scan capability map** for entries with `status: gap`
2. **Cross-reference WRK items** — does a WRK exist to fill the gap?
3. **Identify unmapped standards** — standards referenced in code but not
   in the capability map
4. **Prioritise** — which gaps block downstream work?

### Quick Scan Command
```bash
grep -n 'status: gap' specs/capability-map/digitalmodel.yaml | head -20
```

### Find Unmapped Standards
```bash
# Standards referenced in code but not in capability map
grep -rh 'DNV-RP\|API RP\|ISO 19901' digitalmodel/src/ | \
  sort -u | head -20
```

## Clause-Level Tracking

For detailed tracking, use comments in the capability map summary field:

```yaml
summary: |
  Sec 3.3 absolute stability: implemented (absolute_stability.py)
  Sec 3.4 generalized method: implemented (generalized_stability.py)
  Sec 4 soil resistance: implemented (soil_resistance.py)
  Sec 5 scour: gap (see WRK-623)
  Appendix B examples: used as test validation
```

## Output: Standards Coverage Table

Generate a markdown summary for reviews:

```markdown
| Standard | Module | Status | WRK | Notes |
|----------|--------|--------|-----|-------|
| API RP 2GEO | geotechnical/soil_models | gap | WRK-618 | Phase 1 |
| API RP 2GEO | geotechnical/piles | gap | WRK-619 | Phase 2 |
| DNV-RP-F109 | geotechnical/on_bottom_stability | gap | WRK-620 | Phase 3 |
| DNV-RP-C212 | geotechnical/foundations | gap | WRK-621 | Phase 4 |
| DNV-RP-E303 | geotechnical/anchors | gap | WRK-622 | Phase 5 |
| DNV-RP-F107 | geotechnical/scour | gap | WRK-623 | Phase 6 |
```

## Updating the Capability Map

When a standard transitions from `gap` to `partial` or `implemented`:

1. Update `status` field in the YAML entry
2. Update `summary` with clause-level detail
3. Reference the implementing WRK in the summary
4. Verify no orphaned entries (`unlinked_doc_count: 0`)

## Related Skills

- `geotechnical-engineering` — domain expertise for geotechnical standards

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-26 | Initial skill — status taxonomy, gap workflow, coverage tables |
