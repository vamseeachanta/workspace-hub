# Tier-1 Indexing Freshness Report

Generated: 2026-06-03T08:32:11Z
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Working directory: `/mnt/local-analysis/workspace-hub`
Mode: scheduled freshness audit; no new cron jobs scheduled.
Source baseline: 2026-04-22 tier-1 indexing scorecard plus current canonical routing surfaces only.

## Overall Status

Portfolio status: **red**

Material drift since the prior correct baseline: **no status-level material drift detected**. The stale 2026-06-02 latest report incorrectly treated sibling tier-1 checkouts as missing; this refresh corrected the scan by using sibling fallbacks under `/mnt/local-analysis/` when nested checkouts were absent.

Reason portfolio remains red:
- `workspace-hub` is still missing required repo-local routing surfaces and has active broken legacy `.agent-os` links in `docs/README.md`.
- `digitalmodel` has all required canonical routing surfaces, but still has an active broken routing/reference link in `README.md`.
- `aceengineer-website` is still missing the machine-readable module-routing registry.
- trusted source/test/docs paths still contain cache/runtime/report noise in multiple repos.

## Per-Repo Status Summary

| Repo | Status | Current evidence | Concise next action |
| --- | --- | --- | --- |
| `workspace-hub` | **red** | Missing `docs/maps/workspace-hub-operator-map.md`; missing `docs/registry/module-routing.yaml`; active broken `.agent-os` product-doc links in `docs/README.md`; root/docs/runtime noise remains. | Create repo-local operator map + module-routing registry; replace active legacy `.agent-os` links with current canonical routing surfaces; clean or quarantine root/runtime noise. |
| `digitalmodel` | **red** | `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, and `docs/registry/module-routing.yaml` exist; active broken link remains: `README.md:73 -> specs/data-needs.yaml`. Source-path cache/package noise remains. | Fix or remove the broken `specs/data-needs.yaml` link; purge/cache-ignore generated `__pycache__` and egg-info noise from trusted paths. |
| `assetutilities` | **yellow** | Required canonical surfaces exist; no broken links detected in inspected surfaces; source-path cache/package noise remains under `src/assetutilities...`. | Clean/package-ignore `src/assetutilities.egg-info/` and `__pycache__/` noise; keep registry/operator-map current as code moves. |
| `aceengineer-website` | **red** | `AGENTS.md`, `README.md`, `docs/README.md`, and `docs/maps/aceengineer-website-operator-map.md` exist; missing `docs/registry/module-routing.yaml`; test/script cache noise remains. | Add machine-readable `docs/registry/module-routing.yaml`; clean/cache-ignore test/script `__pycache__` noise. |

## Exact Broken or Missing Surfaces

### `workspace-hub` — red

Missing canonical routing surfaces:
- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

Active broken/stale legacy references in inspected canonical docs:
- `docs/README.md:300 -> ../.agent-os/product/mission.md` resolves to missing `.agent-os/product/mission.md`
- `docs/README.md:301 -> ../.agent-os/product/tech-stack.md` resolves to missing `.agent-os/product/tech-stack.md`
- `docs/README.md:302 -> ../.agent-os/product/roadmap.md` resolves to missing `.agent-os/product/roadmap.md`
- `docs/README.md:303 -> ../.agent-os/product/decisions.md` resolves to missing `.agent-os/product/decisions.md`

Other routing trust concerns:
- `docs/README.md:264` still presents `.agent-os/` as part of the documented repository structure.
- Root/index noise remains visible in the workspace root, including operational scratch artifacts such as `claude_smoke.log`, issue payload/review/diff files, `node_modules/`, `nohup.out`, `tmp/`, `output/`, `reports/`, and generated email/triage packets.
- Runtime/cache/log noise remains in trusted docs/agent paths, including examples under `docs/plans/.../logs/*.log`, `docs/sessions/*.log`, `.claude/reports/*.log`, `.claude/state/**/*.log`, and `.claude/**/__pycache__/`.

### `digitalmodel` — red

Canonical surfaces present:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

Active broken references:
- `README.md:73 -> specs/data-needs.yaml` resolves to missing `specs/data-needs.yaml`

Other routing trust concerns:
- Source-path cache/package noise remains, including `src/digitalmodel.egg-info/`, `src/digitalmodel/__pycache__/`, and nested `src/digitalmodel/**/__pycache__/` artifacts.

### `assetutilities` — yellow

Canonical surfaces present:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

Broken references in inspected surfaces:
- none detected

Other routing trust concerns:
- Source-path cache/package noise remains, including `src/assetutilities.egg-info/`, `src/assetutilities/__pycache__/`, and nested `src/assetutilities/**/__pycache__/` artifacts.

### `aceengineer-website` — red

Missing canonical routing surfaces:
- `docs/registry/module-routing.yaml`

Canonical surfaces present:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

Broken references in inspected surfaces:
- none detected

Other routing trust concerns:
- Test/script cache noise remains, including `tests/**/__pycache__/` and `scripts/**/__pycache__/` artifacts.

## 2026-04-22 Scorecard Assumption Check

Overall assumption: **still holds, with repo-specific revisions required**.

The 2026-04-22 scorecard conclusion that the tier-1 portfolio is only partially ready still holds. Future GitHub issue work still cannot rely on a uniformly green set of trusted routing/index surfaces.

Required revisions to the 2026-04-22 assumptions:
- `digitalmodel`: revise upward for surface completeness. It now has a repo-local `docs/README.md`, repo-wide `docs/maps/digitalmodel-operator-map.md`, and `docs/registry/module-routing.yaml`. Keep red only because of the active broken `README.md:73 -> specs/data-needs.yaml` reference and source cache noise.
- `assetutilities`: revise upward from highest misplacement risk. It now has the expected canonical docs entry point, operator map, and registry. Current status is yellow, not red, because remaining evidence is primarily source-path cache/package noise.
- `aceengineer-website`: revise upward for docs/operator-map completeness but keep red until `docs/registry/module-routing.yaml` exists.
- `workspace-hub`: original concern still holds. It remains the richest control plane but has weak routing trust because the repo-local operator map and registry are absent, legacy `.agent-os` links remain active in `docs/README.md`, and root/index/runtime noise remains high.

## Next Actions

1. `workspace-hub`: create `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`, then remove/replace active `.agent-os` product-doc links from `docs/README.md`.
2. `digitalmodel`: fix `README.md:73 -> specs/data-needs.yaml` by restoring the target or replacing the link with a current canonical registry/data-needs surface.
3. `aceengineer-website`: add `docs/registry/module-routing.yaml` aligned to the existing `docs/maps/aceengineer-website-operator-map.md`.
4. `assetutilities`, `digitalmodel`, `aceengineer-website`: purge generated `__pycache__/` and package metadata noise from trusted paths and ensure ignore rules prevent recurrence.
5. `workspace-hub`: quarantine root-level scratch/generated artifacts so the repository root and curated docs remain trusted routing surfaces.

## Notes

- This report intentionally does not use or recommend legacy `.agent-os` reference patterns.
- No new cron jobs were scheduled.
- No material drift detected at the status level; this refresh corrected stale prior-report path evidence and refreshed the timestamp.
