# 2026-05-15 Freshness Audit Lessons

## Context

Scheduled local Tier-1 routing/index freshness audit for `/mnt/local-analysis/workspace-hub` covering:

- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `aceengineer-website`

Target report refreshed:

- `/mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md`

## Durable workflow lessons

1. **Re-read or otherwise verify the report after writing it.** A freshness audit is not complete at file-write time. Verify at least `stat`/checksum and, when practical, a diff or targeted readback before final delivery.
2. **Treat historical scorecards as context, not authority.** For Tier-1 routing audits, use `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` and current canonical surfaces as the baseline; `docs/reports/*scorecard*.md` files can be stale.
3. **Call out stale prior-report corrections explicitly.** If `tier-1-indexing-freshness-latest.md` contains stale status or stale broken-link counts, the refreshed report should name the correction so future audits do not preserve old generator errors.
4. **Keep status and evidence drift separate.** It is valid to say `no material drift detected at the status level` when portfolio/repo colors did not change, but still list newly verified or corrected evidence.
5. **Use false-positive-filtered broken-link checks.** Do not carry forward raw broken-link counts without resolving links relative to the containing file and filtering examples, wildcard patterns, and non-canonical illustrative file names.

## Current evidence snapshot from the 2026-05-15 audit

Portfolio status remained **RED**.

Per-repo statuses:

- `workspace-hub` — **RED**: missing `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; stale legacy references remain in `docs/README.md`; root/index noise remains high.
- `digitalmodel` — **YELLOW**: required canonical surfaces exist; `README.md` still references missing `specs/data-needs.yaml`; `docs/maps/digitalmodel-operator-map.md` still references the OrcaWave/OrcaFlex historical map as if repo-local even though the matching map exists at workspace level.
- `assetutilities` — **YELLOW**: required canonical surfaces exist; no confirmed broken active canonical Markdown links after false-positive filtering; trusted source/test paths still contain runtime/cache/log noise.
- `aceengineer-website` — **RED**: required docs/operator surfaces exist; required `docs/registry/module-routing.yaml` is missing.

Confirmed stale or broken references from this run:

- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md`
- `digitalmodel/README.md:73` -> `specs/data-needs.yaml`
- `digitalmodel/docs/maps/digitalmodel-operator-map.md:9` -> repo-local historical map assumption for `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

## 2026-04-22 scorecard assumption handling

The 2026-04-22 scorecard should be reported as **partially still holding but requiring detail-level revision**:

- Still holds: portfolio is only partially ready for reliable code placement and canonical retrieval.
- Still holds: `workspace-hub` is the strongest control-plane repo but has root/index hygiene risk.
- Still holds: `digitalmodel` is the strongest engineering source/test structure.
- Needs revision: `digitalmodel/docs/README.md`, repo-wide `digitalmodel` operator map, `assetutilities/docs/README.md`, `assetutilities` operator map/registry, and `aceengineer-website` docs/operator map now exist.
- Still holds until remediated: machine-readable routing is incomplete because `workspace-hub` and `aceengineer-website` still lack `docs/registry/module-routing.yaml`.

## Final-response verification pattern

For scheduled jobs where the final response is delivered automatically, include compact verification evidence in the final response rather than bloating the report:

```text
path=docs/reports/tier-1-indexing-freshness-latest.md size=<bytes> mtime=<timestamp>
sha256=<sha256>
```

This keeps the canonical report readable while giving the user evidence that the latest file was refreshed and verified.
