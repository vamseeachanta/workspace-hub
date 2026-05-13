# Tier-1 Indexing Freshness Audit — Latest

**Run timestamp:** 2026-05-13T03:35:08-05:00

**Scope:** `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website` under `/mnt/local-analysis/workspace-hub` with sibling fallback only if nested checkout is absent.

**Canonical routing surfaces inspected:** `AGENTS.md`, `README.md`, `docs/README.md`, repo-local `docs/maps/<repo>-operator-map.md`, and machine-readable registry references where present/applicable. Legacy `.agent-os` reference patterns were not used.

**Material drift:** no material drift detected at the status level; timestamp refreshed and current evidence revalidated.

**2026-04-22 tier-1 indexing scorecard assumptions:** hold directionally but need current-state revision for point-in-time details. The latest status-level baseline remains `workspace-hub=red`, `digitalmodel=yellow`, `assetutilities=yellow`, `aceengineer-website=red`.

## Status table

| Repo | Status | Missing/broken surfaces | Concise next action |
|---|---:|---|---|
| `workspace-hub` | **red** | docs/maps/workspace-hub-operator-map.md; docs/registry/module-routing.yaml; 4 stale legacy Markdown links; 1 missing literal path mention; 836 trusted-path noise entries; 36 root/index noise entries | add current canonical operator map and module-routing registry; remove stale legacy references and reduce workspace root/index noise |
| `digitalmodel` | **yellow** | 1 broken markdown links; 1 missing literal path mentions; 3585 trusted-path noise entries | repair stale repo-local map references and maintain registry-backed module routing |
| `assetutilities` | **yellow** | 599 trusted-path noise entries | tighten module registry/operator map and clean stale canonical references/noise |
| `aceengineer-website` | **red** | no registry reference; 18 trusted-path noise entries | add/repair machine-readable routing registry and operator map coverage; remove stale/broken canonical references |

## Per-repo evidence

### workspace-hub — RED
- Path inspected: `/mnt/local-analysis/workspace-hub`
- Surface existence:
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/workspace-hub-operator-map.md`: MISSING
- Current canonical machine-readable registry references found: none found (`docs/registry/module-routing.yaml` is missing; `specs/module-registry.yaml` exists but is not the current tier-1 routing registry surface for this audit)
- Stale legacy Markdown links in canonical surfaces:
  - `docs/README.md` -> `../.agent-os/product/mission.md` (missing `/mnt/local-analysis/workspace-hub/.agent-os/product/mission.md`)
  - `docs/README.md` -> `../.agent-os/product/tech-stack.md` (missing `/mnt/local-analysis/workspace-hub/.agent-os/product/tech-stack.md`)
  - `docs/README.md` -> `../.agent-os/product/roadmap.md` (missing `/mnt/local-analysis/workspace-hub/.agent-os/product/roadmap.md`)
  - `docs/README.md` -> `../.agent-os/product/decisions.md` (missing `/mnt/local-analysis/workspace-hub/.agent-os/product/decisions.md`)
- Missing literal path mentions in canonical surfaces (conservative scan):
  - `docs/README.md` mentions `docs/plans/2026-04-22-issue-2464` (missing `/mnt/local-analysis/workspace-hub/docs/plans/2026-04-22-issue-2464`)
- Backup/cache/runtime noise in trusted source paths: 836 found; examples:
  - `src/__pycache__`
  - `src/ace/__pycache__`
  - `src/config/__pycache__`
  - `src/geometry/__pycache__`
  - `src/knowledge_graph/__pycache__`
  - `src/models/__pycache__`
  - `src/solvers/__pycache__`
  - `src/utilities/__pycache__`
  - `src/workspace_hub/math/__pycache__`
  - `src/workspace_hub/workstations/__pycache__`
- Workspace-hub root/index noise examples:
  - `GEMINI.md`
  - `MEMORY.md`
  - `ace_cfp_sending_kit_2026-04-09.md`
  - `ace_gmail_triage_2026-04-09.txt`
  - `claude_smoke.log`
  - `claude_smoke_prompt.txt`
  - `daily_gmail_action_digest_2026-04-09.md`
  - `dist/`
  - `docs-reorg-assessment.md`
  - `draft_ace_api_cfp_note.md`
- Classification drivers: missing operator map; missing current canonical `docs/registry/module-routing.yaml`; 4 stale legacy Markdown links in canonical surfaces; 1 missing literal path mention in canonical surfaces; 836 backup/cache/runtime noise entries in trusted paths; 36 root/index noise entries

### digitalmodel — YELLOW
- Path inspected: `/mnt/local-analysis/workspace-hub/digitalmodel`
- Surface existence:
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/digitalmodel-operator-map.md`: present
- Machine-readable registry references found: `docs/registry/module-routing.yaml`
- Broken Markdown links in canonical surfaces:
  - `README.md` -> `specs/data-needs.yaml` (missing `/mnt/local-analysis/workspace-hub/digitalmodel/specs/data-needs.yaml`)
- Missing literal path mentions in canonical surfaces (conservative scan):
  - `docs/maps/digitalmodel-operator-map.md` mentions `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` (missing `/mnt/local-analysis/workspace-hub/digitalmodel/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`)
- Backup/cache/runtime noise in trusted source paths: 3585 found; examples:
  - `src/digitalmodel/__pycache__`
  - `src/digitalmodel/infrastructure/__pycache__`
  - `src/digitalmodel/marine_ops/__pycache__`
  - `src/digitalmodel/naval_architecture/__pycache__`
  - `src/digitalmodel/nde/__pycache__`
  - `src/digitalmodel/orcaflex/__pycache__`
  - `src/digitalmodel/orcawave/__pycache__`
  - `src/digitalmodel/power/__pycache__`
  - `src/digitalmodel/production_engineering/__pycache__`
  - `src/digitalmodel/reservoir/__pycache__`
- Classification drivers: 1 broken markdown links in canonical surfaces; 1 missing literal path mentions in canonical surfaces; 3585 backup/cache/runtime noise entries in trusted paths

### assetutilities — YELLOW
- Path inspected: `/mnt/local-analysis/workspace-hub/assetutilities`
- Surface existence:
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/assetutilities-operator-map.md`: present
- Machine-readable registry references found: `docs/registry/module-routing.yaml`
- Broken Markdown links in canonical surfaces: none detected
- Missing literal path mentions in canonical surfaces: none detected
- Backup/cache/runtime noise in trusted source paths: 599 found; examples:
  - `src/assetutilities/__pycache__`
  - `src/modules/web-contextualization/__pycache__`
  - `src/modules/agent_os/enhanced_create_specs/__pycache__`
  - `src/assetutilities/calculations/__pycache__`
  - `src/assetutilities/common/__pycache__`
  - `src/assetutilities/constants/__pycache__`
  - `src/assetutilities/devtools/__pycache__`
  - `src/assetutilities/modules/__pycache__`
  - `src/assetutilities/units/__pycache__`
  - `src/assetutilities/units/domains/__pycache__`
- Classification drivers: 599 backup/cache/runtime noise entries in trusted paths

### aceengineer-website — RED
- Path inspected: `/mnt/local-analysis/workspace-hub/aceengineer-website`
- Surface existence:
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/aceengineer-website-operator-map.md`: present
- Machine-readable registry references found: none found
- Broken Markdown links in canonical surfaces: none detected
- Missing literal path mentions in canonical surfaces: none detected
- Backup/cache/runtime noise in trusted source paths: 18 found; examples:
  - `tests/__pycache__`
  - `tests/docs/__pycache__`
  - `tests/python/__pycache__`
  - `tests/repo_structure/__pycache__`
  - `tests/__pycache__/__init__.cpython-312.pyc`
  - `tests/__pycache__/__init__.cpython-313.pyc`
  - `tests/repo_structure/__pycache__/test_repo_structure_contract.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`
- Classification drivers: missing machine-readable registry reference; missing machine-readable registry reference; 18 backup/cache/runtime noise entries in trusted paths

## Next actions

1. Keep the 2026-04-22 scorecard assumptions directionally, but use this refreshed current-state baseline for point-in-time routing risk: `workspace-hub=red`, `digitalmodel=yellow`, `assetutilities=yellow`, `aceengineer-website=red`.
2. Prioritize `workspace-hub` and `aceengineer-website` registry/operator-map remediation because they are the RED tier-1 repos in the current baseline.
3. For YELLOW repos, repair exact stale references listed above before adding new routing surfaces; avoid creating broad noisy indexes as a substitute for operator maps/registries.
4. Do not introduce or recommend legacy `.agent-os` reference patterns.
5. No new cron jobs were scheduled by this run.

## Verification

- Report refreshed locally at `docs/reports/tier-1-indexing-freshness-latest.md`.
- Scan mode: local filesystem inspection only; no GitHub issues or cron jobs created.
