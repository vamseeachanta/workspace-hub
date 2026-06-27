---
name: reference_digitalmodel_python_env_venv
description: digitalmodel Python env — use .venv/bin/python (uv run hangs); cold import ~117s
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4e19e539-dc4c-444f-8e16-f47bd024a295
---

In **digitalmodel** (`/mnt/local-analysis/digitalmodel`): `uv run python ...` HANGS (times out re-syncing the env). Use the venv interpreter directly: `/mnt/local-analysis/digitalmodel/.venv/bin/python` — it works.

**Cold `import digitalmodel` takes ~117s** on this box: the package `__init__.py` installs a "Layer 2 group redirect finder" import hook, and site-packages sits on a slow overlay filesystem. Bare interpreter startup is instant; the cost is the first heavy import only. After one warm-up the same process / warm cache is fast (full test suite 1.8s).

Practical rules:
- For parametric sweeps: import the analysis module ONCE in a single long-lived process and loop in-memory — never spawn a subprocess per case (each pays the cold import).
- Use `timeout 200-300` on first runs; ignore harmless stderr `OrcaFlex license not available` + pint `bbl` redefinition warnings.
- Submodules like `structural/structural_analysis/buckling.py` are self-contained (numpy only) but importing them still triggers the parent package `__init__` chain.

Differs from the broken-`.venv` notes in other repos (worldenergydata `.venv` broke → miniforge python3). Per-repo: digitalmodel `.venv` is fine.
