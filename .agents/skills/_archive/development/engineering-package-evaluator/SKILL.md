---
name: engineering-package-evaluator
version: "1.0.0"
updated: 2026-02-26
category: development
description: |
  Reusable evaluation framework for assessing Python engineering packages
  for adoption — license compatibility, maintenance health, integration
  risk, and dependency strategy.
tags: [package, evaluation, license, dependency, python]
platforms: [linux, macos, windows]
invocation: engineering-package-evaluator
depends_on: []
requires: []
see_also:
  - plugin-management
---

# Engineering Package Evaluator Skill

Structured evaluation framework for Python engineering packages being
considered for adoption into digitalmodel or other MIT-licensed projects.

## When to Use This Skill

- Evaluating a new Python package for integration
- Assessing license compatibility for a dependency
- Reviewing maintenance health of an existing dependency
- Deciding between direct dependency vs optional extra vs wrapper

## Evaluation Checklist

### 1. License Compatibility

```
Package License?
  ├── MIT / BSD / Apache-2.0 → Direct dependency (safe)
  ├── LGPL-2.1 / LGPL-3.0 → Direct dependency (dynamic linking OK)
  ├── GPL-2.0 / GPL-3.0 → Optional extra ONLY (cannot bundle)
  ├── AGPL → Do not use (viral, affects SaaS)
  └── Proprietary / Unknown → Do not use without legal review
```

### 2. Maintenance Health

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Last commit | < 6 months | 6–18 months | > 18 months |
| Last release | < 12 months | 12–24 months | > 24 months |
| Open issues | < 50 | 50–200 | > 200 |
| Response time | < 1 week | 1–4 weeks | > 1 month |
| CI status | Passing | Flaky | Failing/none |
| Python 3.10+ | Supported | Untested | Incompatible |

### 3. Community & Quality

| Metric | Strong | Moderate | Weak |
|--------|--------|----------|------|
| GitHub stars | > 500 | 100–500 | < 100 |
| Contributors | > 10 | 3–10 | 1–2 |
| Documentation | Comprehensive | Basic | None/stale |
| Test suite | > 80% coverage | Some tests | No tests |
| JOSS/academic paper | Published | Preprint | None |

### 4. Dependency Risk

| Risk Factor | Mitigation |
|-------------|-----------|
| Single maintainer | Thin wrapper, plan for replacement |
| Breaking API changes | Pin version, adapter pattern |
| Large dependency tree | Evaluate transitive deps too |
| C/Fortran extensions | May not build on all platforms |
| Python version lag | Test in CI with target versions |

## Integration Patterns

### Direct Dependency
```toml
# pyproject.toml
[project]
dependencies = ["pygef>=0.12"]
```
Use when: MIT/BSD/Apache/LGPL, well-maintained, stable API.

### Optional Extra
```toml
[project.optional-dependencies]
geotechnical-gpl = ["groundhog>=0.12", "openpile>=1.0"]
```
Use when: GPL license, or large/heavy package not needed by all users.

### GPL Guard Pattern
```python
try:
    import groundhog
    HAS_GROUNDHOG = True
except ImportError:
    HAS_GROUNDHOG = False

def compute_with_groundhog(soil_profile):
    if not HAS_GROUNDHOG:
        raise ImportError(
            "groundhog required: pip install digitalmodel[geotechnical-gpl]"
        )
    return groundhog.some_function(soil_profile)
```

### Thin Wrapper (Isolation)
```python
# parsers/gef_reader.py — thin wrapper around pygef
"""Isolates pygef dependency. If pygef is abandoned, only this file changes."""

from pygef import read_gef

def parse_gef_file(path):
    gef = read_gef(path)
    return CPTData(
        depth_m=gef.df["depth"].values,
        qc_MPa=gef.df["qc"].values,
        fs_kPa=gef.df["fs"].values,
    )
```

## Evaluation Report Template

```yaml
package:
  name: groundhog
  version: "0.12.0"
  pypi: https://pypi.org/project/groundhog/
  repo: https://github.com/snakesonabrain/groundhog
  license: GPL-3.0

assessment:
  license_compatible: false  # GPL vs MIT host
  maintenance: green         # active development
  community: moderate        # ~200 stars, 3 contributors, JOSS paper
  test_coverage: moderate    # some tests, no coverage badge
  python_support: ">=3.8"
  api_stability: moderate    # breaking changes between 0.x versions

decision: optional_extra
strategy: |
  Add as optional dependency under [geotechnical-gpl] extra.
  Use GPL guard pattern. Core calculations independent.
  Thin adapter in _groundhog_adapter.py for cross-validation.

risks:
  - Single primary maintainer
  - GPL-3.0 prevents bundling in MIT distribution
  - 0.x version implies API not yet stable
```

## Related Skills

- `plugin-management` — managing plugin and extension systems

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-26 | Initial skill — license tree, health metrics, integration patterns |
