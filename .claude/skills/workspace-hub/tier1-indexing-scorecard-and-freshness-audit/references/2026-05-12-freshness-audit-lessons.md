# 2026-05-12 Tier-1 Freshness Audit Lessons

Use as a compact evidence reference for daily tier-1 indexing freshness audits after the 2026-05-12 scheduled/local run.

## Status-level result

The 2026-05-12 local audit refreshed `docs/reports/tier-1-indexing-freshness-latest.md` and kept the portfolio red:

- `workspace-hub`: RED
- `digitalmodel`: YELLOW
- `assetutilities`: YELLOW
- `aceengineer-website`: RED

Use **no material drift detected at the status level** when these statuses remain unchanged, while still listing any current evidence revalidated during the run.

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
- `workspace-hub` root/index trust remains weakened by runtime/build/cache directories such as `.cache/`, `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `logs/`, `node_modules/`, `reports/`, and `tmp/`.
- `digitalmodel` required canonical surfaces are present, but still has:
  - `README.md -> specs/data-needs.yaml` missing target
  - `docs/maps/digitalmodel-operator-map.md` line 9 references missing repo-local `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; the matching map exists at workspace level, not repo-local.
- `assetutilities` required canonical surfaces are present and no broken active local Markdown links were confirmed after false-positive filtering; remaining material issue is trusted-path runtime/cache noise.
- `aceengineer-website` required docs/operator surfaces are present, but `docs/registry/module-routing.yaml` is still missing.

## Report verification pitfall

Do not embed exact `stat` size/mtime/checksum values inside the report before the report is final. Any later patch to the report invalidates the embedded checksum and creates self-referential stale evidence. Preferred pattern:

1. Write the complete report body, including a generic verification note if desired.
2. Make all content patches.
3. Run final `stat` and `sha256sum`.
4. Put exact verification evidence in the final cron response, or append it only after deciding no further report edits will occur.

## Reporting pattern update

For freshness reports after this run:

- Phrase unchanged status as **no material drift detected at the status level**.
- Keep exact broken/missing surfaces in the report, even when status is unchanged.
- Continue stating that the 2026-04-22 scorecard assumptions still hold directionally but need current-state revision for point-in-time details.

## Verification evidence from the run

The 2026-05-12 report verification used:

```bash
stat -c 'path=%n size=%s mtime=%y' /mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md
sha256sum /mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md
```

Observed after final report refresh:

- size: `12827` bytes
- mtime: `2026-05-12 03:34:52.919715500 -0500`
- sha256: `4d535fb35db987cbf7f83379a330ab90d07cbeca33a59585c319e29fdc0b8d77`
