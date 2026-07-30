---
name: reference_wed_local_build_run_recipe
description: "How to run worldenergydata builders + contract tests on this box (namespace-package PYTHONPATH, light deps, sparse-clone gotchas)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 468a3d4d-74ba-473e-b6c7-e195d94a7036
---

**Running worldenergydata (wed) builders / tests locally on ace-linux boxes (2026-07).**
wed is a **namespace-package monorepo**: code is split across `src/`,
`packages/worldenergydata-core/src/`, and `packages/worldenergydata-bsee/src/` (+ per-country
packages). To run any script that imports `worldenergydata.*`:

```
export PYTHONPATH="src:packages/worldenergydata-core/src:packages/worldenergydata-bsee/src:scripts:scripts/lower_tertiary"
```

- **Light deps needed** by the lifecycle/onepager builders: `pydantic-settings`, `pyyaml`
  (`uv pip install` into a venv). Data file `config/fields.yml` must be present
  (`fields_registry.load_fields`). PDF one-pagers need **Chrome** (`/usr/bin/google-chrome`
  present on ace-linux-1) — set `CHROME=` to override.
- **Builder chain / outputs:** `build_field_performance_comparison.py` → `_performance.json`
  + comparison `.md`; `build_lifecycle_posters.py` (HTML only, NO Chrome) → `_explorer.json`
  + `index.html` + 10 `*_lifecycle.html`; `build_field_onepagers.py` (Chrome) → 10
  `reports/field-atlas/onepagers/field-*.html` + `.pdf`; `scripts/hf_export/build_explorer_results_bundle.py`
  (stdlib) → HF `explorer_results_bundle.json` + card (its sha256 pins `_explorer.json`, so
  re-run it AFTER the posters rewrite `_explorer.json`).
- **Contract test fast loop** (pure stdlib; skip the numpy/pandas conftest + pytest-cov addopts):
  `uv run --no-sync python -m pytest <path> --noconftest -o addopts="" -p no:cacheprovider -q`
  (install just `pytest`). Tests that import the package (e.g. `test_lifecycle_poster_links.py`)
  need the PYTHONPATH above.
- pyproject has a `[tool.uv]`-adjacent stray `python = "3.11"` that makes `uv` warn on every run —
  harmless, ignore.

**Sparse/partial-clone gotcha:** cloning wed with `--filter=blob:none --depth 1` + cone
sparse-checkout on the NTFS-FUSE box is FLAKY — lazy blob fetch stalls and can leave files
**truncated to 0 bytes** (they show in `git status` as full-file deletions, index `e69de29`).
Under a process storm (other sessions pushing/pytest-ing) `.git/index.lock` collides. Recipe that
worked: clone blobless, `git sparse-checkout set <dirs>`, then targeted `git checkout HEAD -- <dir>`
one at a time (kill stray procs + `rm -f .git/index.lock` between). Before committing:
`git reset -q HEAD` to clear staged sparse-deletions, then **explicit-path** `git add` +
verify no 0-byte files in the commit set (`[ -s "$f" ]`), never `git add -A`. See
[[reference_ntfs_fuse_git_stalls_local_analysis]] and [[reference_fuse_mount_saturation_process_storm]].
