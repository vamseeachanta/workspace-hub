# Tier-1 Indexing Freshness Audit — Latest

Generated: 2026-05-01T03:37:37-05:00 / 2026-05-01T08:37:37+00:00

Working directory: `/mnt/local-analysis/workspace-hub`

Baseline authority: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`

Required canonical routing surfaces per tier-1 repo:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md`
- `docs/registry/module-routing.yaml`

Raw/generated inventory such as `docs/CONTENT_INDEX.md` remains discovery-only and is not treated as trusted routing authority.

## Executive Summary

Portfolio status: **red**

No material drift detected in the portfolio-level conclusion: tier-1 routing/index readiness is still partial, not green. The 2026-04-22 scorecard assumptions still hold directionally: `digitalmodel` remains structurally strong but under-routed; `workspace-hub` remains the control-plane source but noisy/incomplete as a trusted routing index; `assetutilities` is improved but still carries legacy routing-reference residue; `aceengineer-website` is mostly understandable for direct edits but is still missing the canonical registry.

Revision note: the active contract now fixes the canonical machine-readable registry path as `docs/registry/module-routing.yaml`. Missing that registry is treated as a required-surface gap in this report.

## Per-Repo Status

| Repo | Status | Summary |
| --- | --- | --- |
| `workspace-hub` | **red** | Missing required operator map and registry; active `docs/README.md` has broken stale legacy links; root contains tracked report-fragment noise. |
| `digitalmodel` | **red** | Missing docs entry point, operator map, and registry; README has a broken registry/data-needs link; tracked temp artifact exists under tests. |
| `assetutilities` | **yellow** | Required canonical surfaces are present and no trusted-path backup/temp noise was detected; residual legacy `.agent-os/product/` references remain in tracked `.agent-os/` instruction/standards files. |
| `aceengineer-website` | **red** | `AGENTS.md`, `README.md`, docs entry point, and operator map are present, but required canonical registry is missing; blog content still contains legacy product-doc references. |

## Exact Findings

### `workspace-hub` — red

Present canonical surfaces:

- `AGENTS.md`
- `README.md`
- `docs/README.md`

Missing canonical surfaces:

- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

Broken/stale references in canonical surfaces:

- `docs/README.md:299 -> ../.agent-os/product/mission.md`
- `docs/README.md:300 -> ../.agent-os/product/tech-stack.md`
- `docs/README.md:301 -> ../.agent-os/product/roadmap.md`
- `docs/README.md:302 -> ../.agent-os/product/decisions.md`

Noise/hygiene drift:

- No tracked backup/temp artifacts detected under trusted source paths.
- Workspace root has tracked report-fragment files that weaken root/index trust:
  - `**Status:**`
  - `**Date:**`
  - `**Complexity:**`
  - `**Review`
  - `**Issue:**`
- `docs/CONTENT_INDEX.md` is large raw inventory and must remain non-authoritative for routing.

Concise next actions:

1. Add `docs/maps/workspace-hub-operator-map.md`.
2. Add `docs/registry/module-routing.yaml`.
3. Replace or retire the broken active links in `docs/README.md:299-302` with current canonical routing surfaces.
4. Remove or quarantine the tracked root report-fragment files.

### `digitalmodel` — red

Present canonical surfaces:

- `AGENTS.md`
- `README.md`

Missing canonical surfaces:

- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

Broken/stale references in canonical surfaces:

- `README.md:61 -> specs/data-needs.yaml`

Noise/hygiene drift:

- Tracked temp artifact in trusted test path:
  - `tests/workflows/integration/conftest.py.tmp.142657.1759122346612`

Legacy reference residue:

- Several tracked `.claude/` docs/instructions still reference legacy product-doc paths. These are not accepted as current routing authority and should be cleaned or explicitly archived when #2462 is remediated.

Concise next actions:

1. Add `docs/README.md` as the repo docs entry point.
2. Add `docs/maps/digitalmodel-operator-map.md` for repo-wide code/test/docs routing.
3. Add `docs/registry/module-routing.yaml`.
4. Repair or retire `README.md:61` link to `specs/data-needs.yaml`.
5. Remove the tracked `.tmp` test artifact.

### `assetutilities` — yellow

Present canonical surfaces:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing canonical surfaces:

- None detected.

Broken/stale references in canonical surfaces:

- None detected.

Noise/hygiene drift:

- No tracked backup/temp artifacts detected under trusted source paths.

Legacy reference residue:

- Residual legacy product-doc references exist in tracked `.agent-os/` instruction/standards files, including:
  - `.agent-os/standards/code-style.md:8`
  - `.agent-os/instructions/enhanced-create-spec.md:44`
  - `.agent-os/instructions/enhanced-create-spec.md:46`
  - `.agent-os/instructions/enhanced-create-spec.md:47`
  - `.agent-os/instructions/enhanced-create-spec.md:48`
  - `.agent-os/instructions/analyze-product.md:163`

Concise next actions:

1. Keep routing through the canonical surface set listed above.
2. Clean or archive the tracked legacy `.agent-os/` references so they cannot be mistaken for current routing authority.
3. Keep `docs/registry/module-routing.yaml` aligned with source/test/docs changes.

### `aceengineer-website` — red

Present canonical surfaces:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

Missing canonical surfaces:

- `docs/registry/module-routing.yaml`

Broken/stale references in canonical surfaces:

- None detected in the audited canonical surfaces.

Noise/hygiene drift:

- No tracked backup/temp artifacts detected under trusted source paths.

Legacy reference residue:

- `content/blog/PHASE_2_TIER_1_COVERAGE_EXPANSION.md:433`
- `content/blog/PHASE_2_TIER_1_COVERAGE_EXPANSION.md:434`
- `content/blog/PHASE_2_TIER_1_COVERAGE_EXPANSION.md:435`

Concise next actions:

1. Add `docs/registry/module-routing.yaml`.
2. Decide whether the blog references are historical archive context or should be qualified/cleaned so they do not look like current routing instructions.
3. Keep the operator map and docs entry point synchronized with site source paths.

## 2026-04-22 Scorecard Assumptions

Status: **still hold, with minor interpretation updates**

- **Still holds:** overall readiness is partial; portfolio cannot be treated as green for deterministic code placement/retrieval.
- **Still holds:** `digitalmodel` has strong source/test engineering structure but lacks complete repo-wide routing surfaces.
- **Still holds:** `workspace-hub` is the control-plane repo but needs curated routing-map/registry completion and noise cleanup.
- **Needs positive revision:** `assetutilities` has improved materially since the 2026-04-22 scorecard because all five required canonical surfaces are now present.
- **Needs stricter registry interpretation:** `aceengineer-website` remains incomplete until `docs/registry/module-routing.yaml` exists, even though other human-readable routing surfaces are present.

## Next Actions by Priority

1. **P0 — `workspace-hub`:** add missing operator map and registry; remove broken active legacy links and root report-fragment noise.
2. **P0 — `digitalmodel`:** add docs entry point, operator map, registry; fix broken README reference; remove tracked temp test artifact.
3. **P1 — `aceengineer-website`:** add `docs/registry/module-routing.yaml`; qualify or clean legacy references in blog content.
4. **P1 — `assetutilities`:** clean/retire tracked legacy `.agent-os/` reference residue while preserving canonical routing surfaces.

## Freshness Result

The report timestamp was refreshed. No material portfolio-level drift was detected: the tier-1 set still requires remediation before the routing/index surfaces can be considered fully current and trustworthy.
