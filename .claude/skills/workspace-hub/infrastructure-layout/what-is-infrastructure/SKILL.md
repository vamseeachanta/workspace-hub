---
name: infrastructure-layout-what-is-infrastructure
description: 'Sub-skill of infrastructure-layout: What Is `infrastructure/`?.'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# What Is `infrastructure/`?

## What Is `infrastructure/`?


`infrastructure/` is the **cross-cutting layer** of an engineering Python package. It holds
concerns shared by all domains that are not domain-specific logic:

- Configuration loading and validation
- Database connections, caching, provenance tracking
- Input validation pipelines
- Shared utilities (data I/O, ETL, visualization helpers, math)
- Numerical solver framework (base classes, protocols, benchmarks)

**Not** in `infrastructure/`:
- Domain solvers (cathodic protection → `structural/`, VIV → `subsea/`)
- Web application blueprints and Flask routes (→ `web/`)
- Domain-specific plate buckling, well trajectory (→ `structural/`, `well/`)
- Per-domain data loaders (→ domain packages)

---
