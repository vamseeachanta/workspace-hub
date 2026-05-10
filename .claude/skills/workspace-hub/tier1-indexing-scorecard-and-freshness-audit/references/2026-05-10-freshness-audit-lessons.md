# 2026-05-10 Tier-1 Freshness Audit Lessons

Use as a compact evidence reference for daily tier-1 indexing freshness audits after the 2026-05-10 scheduled/local run.

## Status-level result

The 2026-05-10 local audit refreshed `docs/reports/tier-1-indexing-freshness-latest.md` and kept the portfolio red:

- `workspace-hub`: RED
- `digitalmodel`: YELLOW
- `assetutilities`: YELLOW
- `aceengineer-website`: RED

Use **no status-level material drift detected** when these blockers remain unchanged, but do not claim a fully clean scan because runtime/cache noise remains in trusted paths.

## Evidence snapshot

- `workspace-hub` still lacks:
  - `docs/maps/workspace-hub-operator-map.md`
  - `docs/registry/module-routing.yaml`
- `workspace-hub/docs/README.md` still contains stale legacy `.agent-os/product/*` Markdown links. Report these only as stale legacy residue; do not recommend legacy `.agent-os` routing patterns.
- `workspace-hub` root/index trust is weakened by runtime/build/cache directories such as `dist/`, `reports/`, `tmp/`, `logs/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`.
- `digitalmodel` still has:
  - `README.md -> specs/data-needs.yaml` missing target
  - `docs/maps/digitalmodel-operator-map.md` referencing missing repo-local `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; the matching map exists at workspace level, not repo-local.
- `assetutilities` required canonical surfaces are present and no broken local Markdown links were confirmed after improved false-positive filtering; remaining material issue is trusted-path runtime/cache noise.
- `aceengineer-website` still lacks `docs/registry/module-routing.yaml`; no broken local Markdown links were confirmed in inspected canonical surfaces after filtering.

## Scanner refinement

The 2026-05-10 run refined prior `assetutilities` broken-link evidence as false positives. Future scanners should:

- Resolve Markdown links relative to the file containing the link.
- Treat code spans and routing-table entries such as `src/...`, `tests/...`, `docs/...`, `scripts/...`, `AGENTS.md`, and `MODULE_STRUCTURE.md` as repo-root routing descriptors unless they are actual Markdown links or explicitly described as local file targets.
- Do not mark wildcard patterns, placeholders, or example module names as missing paths.
- Separate **broken active references** from **trusted-path cache/runtime noise** so repo status explanations do not imply link breakage where only hygiene debt remains.

## Reporting pattern update

For freshness reports after this run:

- Keep `assetutilities` as YELLOW if cache/runtime noise remains, but do not list broken local links unless the scanner/manual review confirms actual Markdown target failures.
- Keep `aceengineer-website` RED while `docs/registry/module-routing.yaml` is missing, even if local links are clean.
- Include report file verification evidence when available: existence, size, mtime, and checksum.
