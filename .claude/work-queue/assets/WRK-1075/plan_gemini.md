# WRK-1075 Plan — MkDocs API Documentation Pipeline

## Summary
Build a MkDocs + mkdocstrings API documentation generation pipeline for all 5 tier-1 Python
repos (assetutilities, digitalmodel, worldenergydata, assethold, ogmanufacturing).

## Acceptance Criteria
1. `mkdocs.yml` + mkdocstrings config for all 5 tier-1 repos
2. `build-api-docs.sh` generates HTML for each repo without errors
3. `--serve` launches local preview
4. Build fails on broken docstring imports (catches API rot early)
5. `docs-manifest.yaml` at hub level with local URL per repo
6. Cross-review (Codex) passes

## Implementation Phases

### Phase 1 — Hub build script + manifest
- `scripts/docs/build-api-docs.sh` with `--repo <name>` and `--serve` flags
- Follows `scripts/quality/check-all.sh` pattern (per-repo loop, colored output, exit codes)
- `config/docs/docs-manifest.yaml` — repo name → local site URL map
- TDD: `tests/docs/test_build_api_docs.sh` — fixture repos, exit codes, site/ creation

### Phase 2 — mkdocs.yml per tier-1 repo
For each repo: assetutilities, digitalmodel, worldenergydata, assethold, ogmanufacturing:
- `uv add --dev mkdocs mkdocstrings[python]` (griffe backend)
- `mkdocs.yml` at repo root (site_name, docs_dir, plugins: mkdocstrings)
- `docs/api/index.md` auto-ref entry point
- Verify clean `mkdocs build` run; add `site/` to `.gitignore`

### Phase 3 — CI integration
- Extend existing workflows (digitalmodel, worldenergydata, assethold)
- New `docs.yml` for assetutilities + ogmanufacturing
- Job: `build-api-docs.sh --repo <name>` on push to main; fail on import errors

## Test Strategy
- Unit: bash fixture tests — mock mkdocs, verify flags, exit codes
- Integration: actual `mkdocs build` on assetutilities (123 files, smallest)
- AC matrix: 1 test case per AC

## Risks & Mitigations
- R1: Sphinx coexistence → MkDocs writes to `site/` only (gitignored), no conflict
- R2: digitalmodel build time → measure; `--no-strict` during dev if >60s
- R3: broken docstrings fail CI → desired; run WRK-1058 quality checks first

## Files to Create/Modify
- `scripts/docs/build-api-docs.sh` (new)
- `config/docs/docs-manifest.yaml` (new)
- `tests/docs/test_build_api_docs.sh` (new)
- `<repo>/mkdocs.yml` × 5 (new)
- `<repo>/docs/api/index.md` × 5 (new)
- `<repo>/.gitignore` × 5 (modify — add site/)
- `<repo>/pyproject.toml` × 5 (modify — add mkdocs dev deps)
- `.github/workflows/docs.yml` × 2 (new — assetutilities, ogmanufacturing)
- `.github/workflows/quality-gates.yml` × 3 (modify — digitalmodel, worldenergydata, assethold)
