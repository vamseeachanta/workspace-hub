# Tier-1 Indexing Freshness Report

Generated: 2026-06-01T03:30:48-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Working directory: `/mnt/local-analysis/workspace-hub`
Report path: `/mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md`

## Overall Status

Portfolio status: **red**

Reason:
- Two tier-1 repos still miss required canonical routing/index surfaces.
- One tier-1 repo still has a broken active canonical README reference.
- Trusted source/test/docs paths still contain runtime/cache noise that weakens routing trust.
- The previous `latest` report had stale all-red sibling-checkout evidence for `digitalmodel`, `assetutilities`, and `aceengineer-website`; this refresh corrects that from live filesystem evidence.

No new cron jobs were scheduled.

## Repo Status Summary

| Repo | Status | Live checkout used | Exact broken or missing surfaces | Concise next action |
|---|---|---|---|---|
| `workspace-hub` | **red** | `/mnt/local-analysis/workspace-hub` | Missing `docs/maps/workspace-hub-operator-map.md`; missing `docs/registry/module-routing.yaml`; broken/stale active links in `docs/README.md:300-303` to retired `.agent-os/product/*`; stale legacy tree reference at `docs/README.md:264`; root/runtime noise: `.cache`, `dist`, `.mypy_cache`, `claude_smoke.log`, `.pytest_cache`, `.ruff_cache`, `node_modules`; source/test cache noise present. | Create the repo-local operator map and module-routing registry; replace stale legacy links with current canonical routing surfaces; clean or ignore runtime/cache noise from trusted paths. |
| `digitalmodel` | **yellow** | `/mnt/local-analysis/digitalmodel` sibling fallback | Required surfaces present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, `docs/registry/module-routing.yaml`; broken active link `README.md:73 -> specs/data-needs.yaml`; operator map lines 8-12 intentionally point to a historical workspace-level slice at `/mnt/local-analysis/workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; source/test cache noise present. | Fix or remove the broken `specs/data-needs.yaml` README target; clarify historical slice path as cross-repo/workspace-level if retained; clean trusted-path cache noise. |
| `assetutilities` | **yellow** | `/mnt/local-analysis/assetutilities` sibling fallback | Required surfaces present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, `docs/registry/module-routing.yaml`; no broken canonical markdown links detected after false-positive filtering; trusted source cache noise remains under `src/assetutilities/**/__pycache__`. | Clean runtime/cache noise from trusted source paths and keep registry/operator-map alignment under daily scan. |
| `aceengineer-website` | **red** | `/mnt/local-analysis/aceengineer-website` sibling fallback | Missing `docs/registry/module-routing.yaml`; required `AGENTS.md`, `README.md`, `docs/README.md`, and `docs/maps/aceengineer-website-operator-map.md` are present; root/runtime noise: `.pytest_cache`, `node_modules`, `dist`; test cache noise present. | Add `docs/registry/module-routing.yaml`; clean or ignore generated/runtime paths so static-site routing remains low-noise. |

## Per-Repo Evidence

### workspace-hub — red

Canonical surfaces inspected:
- Present: `AGENTS.md`, `README.md`, `docs/README.md`
- Missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`

Confirmed broken/stale canonical references:
- `docs/README.md:300 -> ../.agent-os/product/mission.md`
- `docs/README.md:301 -> ../.agent-os/product/tech-stack.md`
- `docs/README.md:302 -> ../.agent-os/product/roadmap.md`
- `docs/README.md:303 -> ../.agent-os/product/decisions.md`
- `docs/README.md:264` still lists `.agent-os/` as a configuration tree entry.

Noise evidence:
- Root/runtime noise observed: `.cache`, `dist`, `.mypy_cache`, `claude_smoke.log`, `.pytest_cache`, `.ruff_cache`, `node_modules`.
- Trusted source/test cache noise observed under `src/**/__pycache__` and `tests/**/__pycache__`.
- The worktree has substantial unrelated generated state churn; this report only refreshed the requested local report file.

Status rationale: red until the repo-local operator map, module-routing registry, and stale legacy references are fixed.

### digitalmodel — yellow

Canonical surfaces inspected:
- Present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, `docs/registry/module-routing.yaml`
- Missing: none

Confirmed broken/stale canonical references:
- `README.md:73 -> specs/data-needs.yaml` is broken; no matching `data-needs.yaml` exists in `/mnt/local-analysis/digitalmodel`.
- `docs/maps/digitalmodel-operator-map.md:8-12` describes the OrcaWave/OrcaFlex historical narrow slice as a workspace-level map. The referenced file exists at `/mnt/local-analysis/workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`, not repo-local.

Noise evidence:
- Trusted source/test cache noise observed under `src/digitalmodel/**/__pycache__` and root `.pytest_cache`.

Status rationale: yellow because all required routing surfaces exist, but one active README target is broken and trusted-path cache noise remains.

### assetutilities — yellow

Canonical surfaces inspected:
- Present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, `docs/registry/module-routing.yaml`
- Missing: none

Confirmed broken/stale canonical references:
- None detected in the inspected canonical markdown surfaces after false-positive filtering.

Noise evidence:
- Trusted source cache noise observed under `src/assetutilities/**/__pycache__`.

Status rationale: yellow because the previously missing routing surfaces are now present, but trusted-path runtime/cache noise remains and should stay on the remediation watchlist.

### aceengineer-website — red

Canonical surfaces inspected:
- Present: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/aceengineer-website-operator-map.md`
- Missing: `docs/registry/module-routing.yaml`

Confirmed broken/stale canonical references:
- None detected in the inspected canonical markdown surfaces after false-positive filtering.

Noise evidence:
- Root/runtime noise observed: `.pytest_cache`, `node_modules`, `dist`.
- Test cache noise observed under `tests/**/__pycache__`.

Status rationale: red until `docs/registry/module-routing.yaml` exists.

## 2026-04-22 Scorecard Assumption Check

Source assumption file inspected: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`.

Verdict: **the top-level 2026-04-22 portfolio assumption still holds, but repo-specific assumptions need revision.**

Still holds:
- The tier-1 portfolio remains only partially ready for reliable code placement and retrieval.
- `workspace-hub` is still the richest control-plane repo but has weak curation/index hygiene.
- `digitalmodel` remains the strongest engineering source/test structure.
- `aceengineer-website` remains understandable for direct edits but not fully durable for issue-routing until the registry exists.

Needs revision:
- `digitalmodel` no longer lacks `docs/README.md`, a repo-wide operator map, or `docs/registry/module-routing.yaml`; those surfaces are now present. Its current blocker is narrower: broken `README.md:73 -> specs/data-needs.yaml`, cross-repo historical map wording, and cache noise.
- `assetutilities` no longer lacks `docs/README.md`, an operator map, or `docs/registry/module-routing.yaml`; those surfaces are now present. Its current issue is trusted-path runtime/cache noise rather than missing routing surfaces.
- `aceengineer-website` no longer lacks `docs/README.md` or an operator map; its remaining required missing surface is `docs/registry/module-routing.yaml`.
- Prior root-clutter examples in the 2026-04-22 scorecard should not be reused as current evidence without rechecking; today’s live root issue is runtime/generated noise and large unrelated state churn, not the old weird tracked root filenames.

## Drift Assessment

Material status-level drift since the corrected late-May baseline: **no material drift detected at the status level**.

Report-content drift corrected in this refresh:
- The previous `latest` report incorrectly marked `digitalmodel`, `assetutilities`, and `aceengineer-website` as missing all canonical surfaces because it did not use sibling fallback evidence.
- This report uses live sibling checkouts under `/mnt/local-analysis/<repo>` where nested checkouts under `/mnt/local-analysis/workspace-hub/<repo>` are absent.

## Next Actions

1. `workspace-hub`: create `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; remove stale active `.agent-os/product/*` links from `docs/README.md`.
2. `digitalmodel`: fix or delete `README.md:73 -> specs/data-needs.yaml`; clarify cross-repo historical operator-map wording; clean cache noise.
3. `assetutilities`: clean `src/assetutilities/**/__pycache__` and keep the current registry/operator map aligned.
4. `aceengineer-website`: add `docs/registry/module-routing.yaml`; clean generated/cache noise from routing-trusted paths.
5. Portfolio: continue daily timestamp refresh and status audit only; no additional cron scheduling is needed from this run.

## Notes

This report intentionally uses current canonical routing surfaces only: `AGENTS.md`, `README.md`, `docs/README.md`, repo-local `docs/maps/<repo>-operator-map.md`, and `docs/registry/module-routing.yaml` where applicable. Legacy product-doc reference patterns are reported only as stale/broken evidence, not as recommended routing surfaces.
