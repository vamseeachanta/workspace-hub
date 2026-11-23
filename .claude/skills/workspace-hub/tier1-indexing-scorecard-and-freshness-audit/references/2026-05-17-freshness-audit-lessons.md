# 2026-05-17 Freshness Audit Lessons

## Context

Scheduled local Tier-1 routing/index freshness audit for `/mnt/local-analysis/workspace-hub` covering:

- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `aceengineer-website`

Target report refreshed:

- `/mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md`

## Current evidence snapshot from the 2026-05-17 audit

Portfolio status remained **RED**.

Per-repo statuses:

- `workspace-hub` — **RED**: `AGENTS.md`, `README.md`, and `docs/README.md` exist; `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml` are still missing; stale legacy references remain in `docs/README.md`; root/runtime noise remains high.
- `digitalmodel` — **YELLOW**: all required canonical surfaces exist; `README.md` still references missing `specs/data-needs.yaml`; the operator-map note for the OrcaWave/OrcaFlex historical map now resolves as workspace-level context rather than a literal Markdown link, but should be clarified if it is intended authority.
- `assetutilities` — **YELLOW**: all required canonical surfaces exist; no confirmed broken active canonical Markdown links after false-positive filtering; trusted source/test/docs paths still contain runtime/cache noise. Do not carry forward prior raw broken-link counts unless reproduced.
- `aceengineer-website` — **RED**: `AGENTS.md`, `README.md`, `docs/README.md`, and `docs/maps/aceengineer-website-operator-map.md` exist; required `docs/registry/module-routing.yaml` is still missing; no confirmed broken active canonical Markdown links after false-positive filtering.

Confirmed stale or broken references from this run:

- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md`
- `workspace-hub/docs/README.md:264` mentions `.agent-os/` in the documented tree.
- `digitalmodel/README.md:73` -> `specs/data-needs.yaml`

## Report correction pattern reinforced

The pre-existing latest report had stale status/counts:

- It over-reported `assetutilities` as having 6 broken active references.
- It under-reported `aceengineer-website` as yellow even though the required registry is missing.

When refreshing the report, explicitly state these corrections so future agents do not preserve stale generator output.

## 2026-04-22 scorecard assumption handling

Report as **partially still holding but requiring detail-level revision**:

- Still holds: portfolio remains only partially ready for reliable code placement and canonical retrieval.
- Still holds: `workspace-hub` is strongest control-plane repo but has root/index hygiene risk and missing current routing surfaces.
- Still holds: `digitalmodel` is strongest engineering source/test structure.
- Still holds until remediated: machine-readable routing is incomplete because `workspace-hub` and `aceengineer-website` still lack `docs/registry/module-routing.yaml`.
- Needs revision / already changed: `digitalmodel`, `assetutilities`, and `aceengineer-website` now have several canonical docs/operator surfaces that were missing or weaker in the 2026-04-22 assumptions.

## Verification evidence from this run

After writing the report, read it back and verify with `stat` and `sha256sum`.

Observed final evidence:

```text
path=docs/reports/tier-1-indexing-freshness-latest.md size=7841 mtime=2026-05-17 03:32:59.729465500 -0500
sha256=6e486cff69c7e7771a028f8b2abba68d9a64f85f3649afa7905ae11b493a5fee
```
