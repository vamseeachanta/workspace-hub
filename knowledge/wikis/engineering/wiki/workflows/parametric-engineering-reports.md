---
title: "Parametric Engineering Reports"
tags: [parametric, reports, demo, html, gtm, automation]
sources:
  - career-learnings-seed
  - solver-queue-architecture-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Parametric Engineering Reports

The parametric engineering report pipeline generates branded HTML+PDF engineering reports from parameterized inputs, automating the full loop from design parameters through solver execution to formatted deliverables. This is the primary GTM (go-to-market) demonstration capability of the digitalmodel platform.

## Pipeline Architecture

```
Input Parameters (YAML/JSON)
    → Solver Queue (batch manifest)
        → OrcaFlex/OrcaWave execution
            → Results collection (queue/completed/)
                → Report template (Jinja2 + Plotly)
                    → HTML + PDF output
```

Each stage is automated and can run unattended via the solver queue batch system.

## Five Flagship Demos

| Demo | Domain | Typical Cases | Key Output |
|------|--------|---------------|------------|
| Wall Thickness | Pipeline design | ~200 | Min wall thickness vs pressure/temperature |
| Mudmat | Foundation design | ~100 | Required mudmat dimensions for given loads |
| Freespan | Pipeline integrity | ~300 | Allowable freespan length vs current/soil |
| Pipelay | Installation | ~680 | Vessel tension and stinger configuration |
| Jumper | Riser/flowline | ~150 | Jumper geometry and stress utilization |

## Batch Execution

- Each demo runs **100-680 parametric cases** via solver queue batch manifests
- Cases vary key design parameters across their full range
- Batch manifests are YAML files listing all parameter combinations
- Results are collected in `queue/completed/` and aggregated for reporting

## Report Features

### Interactive Charts

Reports embed **Plotly** interactive charts directly in HTML:
- Hover for exact values
- Zoom, pan, and export
- Multiple traces for parameter comparisons
- Contour plots for 2D parameter sweeps

### Branded Output

- Company branding (logo, colors, fonts)
- Standard cover page with project metadata
- Table of contents with section links
- Engineering notation and unit formatting
- PDF export via headless Chrome rendering

## Integration Points

- **Solver Queue**: Batch manifests dispatch all parametric cases
- **Results Dashboard**: Monitor batch progress in real-time
- **Template System**: Jinja2 templates with Plotly chart blocks
- **Export**: HTML (primary), PDF (via Chrome headless), data tables (CSV)

## Cross-References

- **Related concept**: [Knowledge to Website Pipeline](../concepts/knowledge-to-website-pipeline.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [digitalmodel](../entities/digitalmodel.md)
