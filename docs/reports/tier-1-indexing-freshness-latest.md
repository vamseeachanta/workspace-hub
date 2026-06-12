# Tier-1 Indexing Freshness Report

Generated: 2026-06-11T03:33:52-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Working directory: `/mnt/local-analysis/workspace-hub`
Mode: scheduled freshness audit; local report refresh only; no new cron jobs scheduled.

## Overall Status

Portfolio status: **red**

Material drift: **no material drift detected at the status level** since the 2026-06-10 corrected RED/YELLOW baseline; timestamp and live evidence refreshed.

Reason:
- At least one tier-1 repo is still missing required canonical routing surfaces.
- Active broken/stale routing references remain in canonical surfaces where listed below.
- Cache/runtime noise remains inside trusted source/test paths and weakens retrieval trust.

## Required Canonical Routing Surfaces Checked

For each repo:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md`
- `docs/registry/module-routing.yaml`

Legacy `.agent-os` product/spec routing patterns are **not** treated as valid canonical surfaces.

## Per-Repo Status Summary

| Repo | Status | Broken or missing surfaces | Concise next action |
| --- | --- | --- | --- |
| `workspace-hub` | **red** | Missing `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`; 4 confirmed broken/stale Markdown reference(s); trusted-path/root noise present | Create current operator map + routing registry; replace active stale links with canonical current docs; segregate runtime/cache noise. |
| `digitalmodel` | **red** | 1 confirmed broken/stale Markdown reference(s); trusted-path/root noise present | Fix/remove stale `README.md` data-needs link if still intended; clean source cache noise. |
| `assetutilities` | **yellow** | trusted-path/root noise present | Clean source cache noise; keep operator map and registry aligned during module moves. |
| `aceengineer-website` | **red** | Missing `docs/registry/module-routing.yaml`; trusted-path/root noise present | Add routing registry; clean test cache noise. |

## Detailed Findings

### `workspace-hub` — red

Checked path: `/mnt/local-analysis/workspace-hub` (requested workspace root)

Present surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`

Missing surfaces:
- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

Confirmed broken/stale references:
- `docs/README.md:300` -> `../.agent-os/product/mission.md` (resolved missing: `/mnt/local-analysis/workspace-hub/.agent-os/product/mission.md`)
- `docs/README.md:301` -> `../.agent-os/product/tech-stack.md` (resolved missing: `/mnt/local-analysis/workspace-hub/.agent-os/product/tech-stack.md`)
- `docs/README.md:302` -> `../.agent-os/product/roadmap.md` (resolved missing: `/mnt/local-analysis/workspace-hub/.agent-os/product/roadmap.md`)
- `docs/README.md:303` -> `../.agent-os/product/decisions.md` (resolved missing: `/mnt/local-analysis/workspace-hub/.agent-os/product/decisions.md`)

Registry check:
- `docs/registry/module-routing.yaml` missing.

Noise affecting routing trust:
- root/runtime/cache marker `.coverage`.
- root/runtime/cache marker `.mypy_cache`.
- root/runtime/cache marker `.pytest_cache`.
- root/runtime/cache marker `.ruff_cache`.
- root/runtime/cache marker `claude_smoke.log`.
- root/runtime/cache marker `logs`.
- root/runtime/cache marker `tmp`.
- trusted `src/` contains Python cache noise (11 `__pycache__` dirs, 76 bytecode files, including `src/__pycache__`, `src/ace/__pycache__`, `src/config/__pycache__`, `src/digitalmodel/subsea/pipeline/free_span/__pycache__`).
- trusted `tests/` contains Python cache noise (53 `__pycache__` dirs, 682 bytecode files, including `tests/__pycache__`, `tests/quality/__pycache__`, `tests/subsea/pipeline/__pycache__`, `tests/analysis/__pycache__`).

Next actions:
1. Create `docs/maps/workspace-hub-operator-map.md` as the repo-local operator map.
2. Create `docs/registry/module-routing.yaml` for machine-readable routing.
3. Replace active stale/broken routing links with current canonical routing surfaces.
4. Keep root runtime/cache output out of trusted routing/index paths.

### `digitalmodel` — red

Checked path: `/mnt/local-analysis/digitalmodel` (sibling checkout fallback; no nested checkout under /mnt/local-analysis/workspace-hub/digitalmodel)

Present surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing surfaces:
- None among the required surface set.

Confirmed broken/stale references:
- `README.md:73` -> `specs/data-needs.yaml` (resolved missing: `/mnt/local-analysis/digitalmodel/specs/data-needs.yaml`)

Registry check:
- `docs/registry/module-routing.yaml` exists.
- Path-like registry references scanned: no confirmed broken literal path references after wildcard/example filtering.

Noise affecting routing trust:
- trusted `src/` contains Python cache noise (114 `__pycache__` dirs, 628 bytecode files, including `src/digitalmodel/__pycache__`, `src/digitalmodel/orcawave/__pycache__`, `src/digitalmodel/orcawave/reporting/__pycache__`, `src/digitalmodel/orcawave/reporting/sections/__pycache__`).
- trusted `tests/` contains Python cache noise (50 `__pycache__` dirs, 291 bytecode files, including `tests/__pycache__`, `tests/ansys/__pycache__`, `tests/asset_integrity/__pycache__`, `tests/cathodic_protection/__pycache__`).

Next actions:
1. Fix or remove the stale `README.md` `specs/data-needs.yaml` reference if live docs still require it.
2. Clean Python cache artifacts from trusted source paths.
3. Preserve the repo-wide operator map and registry as canonical routing surfaces.

### `assetutilities` — yellow

Checked path: `/mnt/local-analysis/assetutilities` (sibling checkout fallback; no nested checkout under /mnt/local-analysis/workspace-hub/assetutilities)

Present surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing surfaces:
- None among the required surface set.

Confirmed broken/stale references:
- None in the checked canonical Markdown surface set.

Registry check:
- `docs/registry/module-routing.yaml` exists.
- Path-like registry references scanned: no confirmed broken literal path references after wildcard/example filtering.

Noise affecting routing trust:
- trusted `src/` contains Python cache noise (12 `__pycache__` dirs, 57 bytecode files, including `src/assetutilities/__pycache__`, `src/assetutilities/common/__pycache__`, `src/assetutilities/common/download_data/__pycache__`, `src/assetutilities/common/readers/__pycache__`).

Next actions:
1. Clean Python cache artifacts from trusted source paths.
2. Keep `docs/maps/assetutilities-operator-map.md` and `docs/registry/module-routing.yaml` aligned with module moves.
3. Keep status yellow until trusted-path noise is removed or explicitly excluded from routing scans.

### `aceengineer-website` — red

Checked path: `/mnt/local-analysis/aceengineer-website` (sibling checkout fallback; no nested checkout under /mnt/local-analysis/workspace-hub/aceengineer-website)

Present surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

Missing surfaces:
- `docs/registry/module-routing.yaml`

Confirmed broken/stale references:
- None in the checked canonical Markdown surface set.

Registry check:
- `docs/registry/module-routing.yaml` missing.

Noise affecting routing trust:
- trusted `tests/` contains Python cache noise (4 `__pycache__` dirs, 18 bytecode files, including `tests/__pycache__`, `tests/docs/__pycache__`, `tests/python/__pycache__`, `tests/repo_structure/__pycache__`).

Next actions:
1. Create `docs/registry/module-routing.yaml` for machine-readable routing.
2. Clean Python cache artifacts from trusted test paths.
3. Keep README/docs/operator map aligned with the new registry once added.

## 2026-04-22 Tier-1 Indexing Scorecard Assumption Check

Verdict: **portfolio-level assumptions still hold, with repo-specific revisions required.**

- The portfolio is still not fully green: missing routing surfaces, stale references, and trusted-path noise remain.
- `assetutilities` should remain revised from earlier red assumptions to **yellow** when live evidence only supports cache/runtime noise and all required canonical routing surfaces are present.
- `digitalmodel` has the required canonical surfaces in the sibling checkout, but remains **red** because a canonical README link is broken and source cache noise remains.
- `aceengineer-website` remains **red** until the machine-readable routing registry exists.
- `workspace-hub` remains **red** because current root/index surfaces are still missing repo-local routing surfaces and contain active stale legacy links/noise.

## No-Cron Confirmation

No new cron jobs were scheduled or modified by this audit.

