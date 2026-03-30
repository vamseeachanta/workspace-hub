---
name: clean-code-pattern-1-responsibility-split-most-common
description: 'Sub-skill of clean-code: Pattern 1: Responsibility Split (most common)
  (+5).'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Pattern 1: Responsibility Split (most common) (+5)

## Pattern 1: Responsibility Split (most common)


```
# BEFORE: one 1200-line file
src/digital_model/bsee/analysis.py  ← does: fetch + parse + validate + report

# AFTER: four focused files
src/digital_model/bsee/
  fetcher.py        ← HTTP, pagination, rate-limiting (≤150L)
  parser.py         ← raw→structured data transform (≤200L)
  validator.py      ← business rules, schema checks (≤150L)
  reporter.py       ← HTML/CSV/JSON report generation (≤200L)
  __init__.py       ← re-exports public API (≤30L)
```


## Pattern 2: Extract Report Generator


Report generation always violates SRP when mixed with domain logic.

```python
# BEFORE: domain class with 300-line report method
class WellDataAnalyzer:
    def generate_report(self, ...):  # 300 lines of HTML templating
        ...

# AFTER: separate reporter
class WellDataAnalyzer:
    def analyze(self, ...) -> AnalysisResult:  # pure domain logic
        ...

class WellDataReporter:               # src/<pkg>/<domain>/reporter.py
    def generate(self, result: AnalysisResult) -> str:
        ...
```


## Pattern 3: Extract Constants and Config


Inlined magic numbers bloat files and hide domain knowledge.

```python
# BEFORE
def check_wall_thickness(t, D, SMYS):
    if t / D < 0.01:    # magic ratio
        ...
    safety_factor = 1.25  # magic number

# AFTER — constants.py (≤50 lines)
WALL_RATIO_MIN = 0.01        # API 5L minimum D/t ratio
DESIGN_SAFETY_FACTOR = 1.25  # ASME B31.4 Table 403.2.1

# domain file uses named constants
from .constants import WALL_RATIO_MIN, DESIGN_SAFETY_FACTOR
```


## Pattern 4: Extract Sub-Package for Large Domains


When a domain grows beyond 3–4 files, promote to sub-package:

```
# BEFORE
src/digitalmodel/structural/
  pipe_capacity.py   (1476 lines)  ← God Object

# AFTER
src/digitalmodel/structural/pipe_capacity/
  __init__.py          ← public API (re-exports)
  models.py            ← dataclasses, enums
  burst.py             ← burst pressure checks
  collapse.py          ← external pressure / collapse
  bending.py           ← combined bending checks
  api_5l.py            ← API 5L specific rules
  dnv_st_f101.py       ← DNV-ST-F101 specific rules
```


## Pattern 5: Horizontal Split with Shared Shim


When a single file has many functions of the same *type* (e.g., 14 HTML builder functions),
split horizontally by sub-domain, keep the original as a pure re-export shim.

```
# BEFORE: report_builders.py (954 lines) — 14 _build_*_html() functions
#   mixed: header/TOC + hydrostatics + responses + appendices

# AFTER: three focused files + shim
report_builders_header.py      (352L) ← header, TOC, executive summary, hull description
report_builders_hydrostatics.py(390L) ← stability, natural periods, added mass, damping, coupling
report_builders_responses.py   (272L) ← load RAOs, roll damping, phase guide, appendices
report_builders.py              (25L) ← shim: re-exports all three sub-modules
```

```python
# report_builders.py (shim)
"""Split into report_builders_header/hydrostatics/responses. Re-exported for compat."""
from .report_builders_header import *        # noqa: F401,F403
from .report_builders_hydrostatics import *  # noqa: F401,F403
from .report_builders_responses import *     # noqa: F401,F403
```

Key rule: each sub-file imports only from upstream data/model modules — never from sibling
builder sub-files. The shim is the only file that imports from all three.


## Pattern 6: Re-export Chain for Layered Helpers


When a large file has callers that import helpers *through* it, preserve that import path
using a re-export chain. Callers need not be updated.

```
# benchmark_rao_plots.py was 699L:
#   5 plot functions + 15 helper functions (get_x_values, add_solver_traces, etc.)

# AFTER split:
benchmark_rao_helpers.py  (237L) ← helper functions (leaf module)
benchmark_rao_summary.py  (218L) ← summary/table functions
benchmark_rao_plots.py    (291L) ← 5 plot functions + re-exports helpers/summary

# benchmark_correlation.py imports from benchmark_rao_plots — no change needed:
from .benchmark_rao_plots import add_solver_traces, get_heading_indices  # still works
```

```python
# benchmark_rao_plots.py (reduced + re-exports)
from .benchmark_rao_helpers import (  # noqa: F401
    add_solver_traces, apply_layout, get_heading_indices,
    get_significant_heading_indices, get_solver_style,
    get_x_values, save_figure, x_axis_label,
)
from .benchmark_rao_summary import (  # noqa: F401
    build_summary_table, compute_amplitude_summary,
    compute_phase_summary, render_html_with_table,
)
# ... 5 plot functions remain here
```

---
