# 2026-05-11 Tier-1 Freshness Audit Lessons

Use as a compact evidence reference for daily tier-1 indexing freshness audits after the 2026-05-11 scheduled/local run.

## Status-level result

The 2026-05-11 local audit refreshed `docs/reports/tier-1-indexing-freshness-latest.md` and kept the portfolio red:

- `workspace-hub`: RED
- `digitalmodel`: YELLOW
- `assetutilities`: YELLOW
- `aceengineer-website`: RED

Use **no status-level material drift detected** when these blockers remain unchanged, but still refresh the timestamp and current evidence.

## Current evidence snapshot

- `workspace-hub` still lacks:
  - `docs/maps/workspace-hub-operator-map.md`
  - `docs/registry/module-routing.yaml`
- `workspace-hub/docs/README.md` still contains active stale legacy `.agent-os/product/*` Markdown links:
  - `../.agent-os/product/mission.md`
  - `../.agent-os/product/tech-stack.md`
  - `../.agent-os/product/roadmap.md`
  - `../.agent-os/product/decisions.md`
- `workspace-hub/docs/README.md` also includes `.agent-os/` tree residue. Report it only as stale legacy residue; do not recommend legacy `.agent-os` routing patterns.
- `workspace-hub` root/index trust is weakened by runtime/build/cache directories such as `.cache/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `dist/`, `reports/`, `tmp/`, and `logs/`.
- `digitalmodel` required canonical surfaces are present, but still has:
  - `README.md -> specs/data-needs.yaml` missing target
  - `docs/maps/digitalmodel-operator-map.md` line 9 references missing repo-local `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; the matching map exists at workspace level, not repo-local.
- `assetutilities` required canonical surfaces are present and no broken active local Markdown links were confirmed after false-positive filtering; remaining material issue is trusted-path runtime/cache noise.
- `aceengineer-website` required docs/operator surfaces are present, but `docs/registry/module-routing.yaml` is still missing; no broken active local Markdown links were confirmed in inspected canonical surfaces after filtering.

## Repo location guardrail

For this scheduled audit, prefer the nested tier-1 repo paths under `/mnt/local-analysis/workspace-hub/`:

- `/mnt/local-analysis/workspace-hub/digitalmodel`
- `/mnt/local-analysis/workspace-hub/assetutilities`
- `/mnt/local-analysis/workspace-hub/aceengineer-website`

Sibling paths under `/mnt/local-analysis/` may exist for some repos, but the requested working tree and report target are workspace-hub-local. Use sibling paths only as fallback if the nested repo is absent.

## Reporting pattern update

For freshness reports after this run:

- State that the 2026-04-22 scorecard assumptions still hold **directionally**, but its point-in-time evidence needs current-state revision.
- Specifically note that `assetutilities` now has required canonical surfaces; do not repeat the old scorecard claim that `docs/README.md` or operator/registry surfaces are missing unless revalidated missing.
- Specifically note that `aceengineer-website` now has `docs/README.md` and an operator map, but remains RED until `docs/registry/module-routing.yaml` exists.
- Include report file verification evidence when available: existence, size, mtime, and checksum.

## Verification evidence from the run

The 2026-05-11 report verification used:

```bash
stat -c 'path=%n size=%s mtime=%y' /mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md
sha256sum /mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md
```

Observed after refresh:

- size: `8822` bytes
- mtime: `2026-05-11 03:33:13.658313000 -0500`
- sha256: `cf2b0f335ed6b245a3bbc66862f9969ebd12a3238a2aca58d0297140ef3596a6`
