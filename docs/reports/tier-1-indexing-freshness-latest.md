# Tier-1 Indexing Freshness Report

Generated: 2026-05-18T03:32:32-05:00
Working directory: `/mnt/local-analysis/workspace-hub`
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Mode: local scheduled freshness audit only; no cron jobs were created or modified.

## Overall Status

Portfolio status: **RED**

No material drift detected at the status level versus the latest corrected baseline. The timestamp and evidence were refreshed; the portfolio remains red because required canonical routing surfaces are still missing and trusted paths still contain runtime/cache noise.

## 2026-04-22 Scorecard Assumption Check

The 2026-04-22 tier-1 indexing scorecard assumptions **partially still hold and need detail-level revision**:

- Still holds: the portfolio is only partially ready for reliable code placement and canonical retrieval.
- `workspace-hub` remains the strongest control-plane repo but has missing current routing surfaces and root/index hygiene risk.
- `digitalmodel` remains the strongest engineering source/test structure.
- Still holds until remediated: machine-readable routing is incomplete because `workspace-hub` and `aceengineer-website` still lack `docs/registry/module-routing.yaml`.
- Needs revision / already changed: `digitalmodel`, `assetutilities`, and `aceengineer-website` now have several canonical docs/operator surfaces that were missing or weaker in the 2026-04-22 assumptions.

## Per-Repo Status Summary

| Repo | Status | Current reason |
| --- | --- | --- |
| `workspace-hub` | **RED** | Missing repo-wide operator map and registry; stale legacy references remain in `docs/README.md`; root/index noise remains high. |
| `digitalmodel` | **YELLOW** | Required canonical surfaces exist, but `README.md` still links missing `specs/data-needs.yaml`; historical OrcaWave/OrcaFlex map pointer remains workspace-level rather than repo-local. |
| `assetutilities` | **YELLOW** | Required canonical surfaces exist; no required canonical surface is missing; trusted source/test paths still contain runtime/cache/log noise. |
| `aceengineer-website` | **RED** | Required docs/operator surfaces exist, but `docs/registry/module-routing.yaml` is still missing. |

## workspace-hub — RED

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**

Exact missing surfaces:

- `workspace-hub/docs/maps/workspace-hub-operator-map.md`
- `workspace-hub/docs/registry/module-routing.yaml`

Exact broken or stale references:

- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md`
- `workspace-hub/docs/README.md:264` mentions stale legacy `.agent-os` reference: `├── .agent-os/              # Agent OS configuration`

Noise weakening routing trust:

- Root/runtime/build noise includes: `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Status:**`, `.cache`, `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.tmp-inspect-2348`, `.uv-cache`, `.venv`, `.venv-manim`, `.venv-test`, `dist`, `logs`, `node_modules`, `reports`, `tmp`
- Trusted source/test/docs path noise examples:
  - `docs/plans/agent-swarm-audits/2026-05-10/logs`
  - `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-1-codex.log`
  - `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-2-codex.log`
  - `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-3-codex.log`
  - `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-4-codex.log`
  - `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-5-codex.log`
  - `docs/plans/machine-prompts/2026-04-27/execution/orchestration-readiness-interactive-session.log`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/launch-summary.log`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-1-sesa.log`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-2-doris-university.log`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-3-doris-codes.log`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-4-woodfibre.log`
  - `docs/reports`
  - `src/__pycache__`
  - `src/__pycache__/__init__.cpython-311.pyc`
  - `src/__pycache__/__init__.cpython-312.pyc`
  - `src/__pycache__/__init__.cpython-313.pyc`
  - `src/ace/__pycache__`
  - `src/ace/__pycache__/__init__.cpython-311.pyc`
  - … 850 additional noise paths omitted from this summary.

Concise next actions:

1. Create `docs/maps/workspace-hub-operator-map.md` as the repo-wide operator map.
2. Create `docs/registry/module-routing.yaml` for machine-readable routing.
3. Remove or rewrite stale legacy references in `docs/README.md` using current canonical routing surfaces only.
4. Clean or quarantine root/runtime/cache/report noise from trusted source and index paths.

## digitalmodel — YELLOW

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/digitalmodel-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or stale references:

- `digitalmodel/README.md:73` -> `specs/data-needs.yaml`
- `digitalmodel/docs/maps/digitalmodel-operator-map.md:9` -> `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — repo-local target missing; workspace-level map exists

Noise weakening routing trust:

- Root/runtime/build noise includes: `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.venv`, `build`, `dist`, `logs`, `reports`
- Trusted source/test/docs path noise examples:
  - `docs/domains/orcaflex/examples/qa/__pycache__`
  - `docs/domains/orcaflex/examples/qa/__pycache__/orcaflex_example_qa.cpython-311.pyc`
  - `docs/domains/orcawave/L01_aqwa_benchmark/__pycache__`
  - `docs/domains/orcawave/L01_aqwa_benchmark/__pycache__/run_orcawave_api.cpython-311.pyc`
  - `docs/domains/reports`
  - `docs/guides/legacy/apirp2rd/COD/API-STD-2RD/Rev1/logs`
  - `docs/guides/legacy/apirp2rd/COD/API-STD-2RD/Rev2/logs`
  - `docs/legacy/apirp2rd/COD/API-STD-2RD/Rev1/logs`
  - `docs/legacy/apirp2rd/COD/API-STD-2RD/Rev2/logs`
  - `docs/reports`
  - `src/digitalmodel/__pycache__`
  - `src/digitalmodel/__pycache__/__init__.cpython-311.pyc`
  - `src/digitalmodel/__pycache__/__init__.cpython-312.pyc`
  - `src/digitalmodel/__pycache__/__init__.cpython-313.pyc`
  - `src/digitalmodel/__pycache__/__main__.cpython-311.pyc`
  - `src/digitalmodel/__pycache__/_compat.cpython-311.pyc`
  - `src/digitalmodel/__pycache__/_compat.cpython-312.pyc`
  - `src/digitalmodel/__pycache__/_compat.cpython-313.pyc`
  - `src/digitalmodel/__pycache__/engine.cpython-311.pyc`
  - `src/digitalmodel/__pycache__/sections.cpython-311.pyc`
  - … 3605 additional noise paths omitted from this summary.

Concise next actions:

1. Restore, relocate, or remove the `README.md` reference to `specs/data-needs.yaml`.
2. Clarify the historical OrcaWave/OrcaFlex map reference so it is explicitly workspace-level, or add a repo-local forwarding map.
3. Remove source-path log/cache noise from trusted package/test paths.

## assetutilities — YELLOW

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or stale references:

- None confirmed in inspected canonical surfaces after false-positive filtering.

Noise weakening routing trust:

- Root/runtime/build noise includes: `.coverage`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.venv`, `build`, `dist`, `logs`, `reports`
- Trusted source/test/docs path noise examples:
  - `src/assetutilities/__pycache__`
  - `src/assetutilities/__pycache__/__init__.cpython-311.pyc`
  - `src/assetutilities/__pycache__/__init__.cpython-312.pyc`
  - `src/assetutilities/__pycache__/__init__.cpython-313.pyc`
  - `src/assetutilities/__pycache__/engine.cpython-311.pyc`
  - `src/assetutilities/__pycache__/engine.cpython-312.pyc`
  - `src/assetutilities/__pycache__/math_helpers.cpython-311.pyc`
  - `src/assetutilities/agent_os/cli/__pycache__`
  - `src/assetutilities/agent_os/cli/__pycache__/__init__.cpython-311.pyc`
  - `src/assetutilities/agent_os/cli/__pycache__/interactive.cpython-311.pyc`
  - `src/assetutilities/agent_os/cli/__pycache__/main.cpython-311.pyc`
  - `src/assetutilities/agent_os/cli/__pycache__/progress.cpython-311.pyc`
  - `src/assetutilities/agent_os/commands/__pycache__`
  - `src/assetutilities/agent_os/commands/__pycache__/__init__.cpython-311.pyc`
  - `src/assetutilities/agent_os/commands/__pycache__/__init__.cpython-313.pyc`
  - `src/assetutilities/agent_os/commands/__pycache__/cli.cpython-311.pyc`
  - `src/assetutilities/agent_os/commands/__pycache__/context_optimization.cpython-311.pyc`
  - `src/assetutilities/agent_os/commands/__pycache__/context_optimization.cpython-313.pyc`
  - `src/assetutilities/agent_os/commands/__pycache__/create_module_agent.cpython-311.pyc`
  - `src/assetutilities/agent_os/commands/__pycache__/create_module_agent.cpython-313.pyc`
  - … 632 additional noise paths omitted from this summary.

Concise next actions:

1. Clean runtime/cache/log artifacts from trusted source/test paths.
2. Keep `docs/README.md`, `docs/maps/assetutilities-operator-map.md`, and `docs/registry/module-routing.yaml` aligned as the canonical routing trio.
3. Do not reintroduce stale broken-link counts unless revalidated with false-positive-filtered scanning.

## aceengineer-website — RED

Canonical surfaces inspected:

- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — **missing**

Exact missing surfaces:

- `aceengineer-website/docs/registry/module-routing.yaml`

Exact broken or stale references:

- None confirmed in inspected canonical surfaces after false-positive filtering.

Noise weakening routing trust:

- Root/runtime/build noise includes: `.coverage`, `.pytest_cache`, `.venv`, `dist`, `logs`, `node_modules`, `reports`
- Trusted source/test/docs path noise examples:
  - `tests/__pycache__`
  - `tests/__pycache__/__init__.cpython-311.pyc`
  - `tests/__pycache__/__init__.cpython-312.pyc`
  - `tests/__pycache__/__init__.cpython-313.pyc`
  - `tests/docs/__pycache__`
  - `tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__`
  - `tests/python/__pycache__/__init__.cpython-311.pyc`
  - `tests/python/__pycache__/__init__.cpython-312.pyc`
  - `tests/python/__pycache__/__init__.cpython-313.pyc`
  - `tests/python/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_competitor_analysis.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_clean.cpython-311-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_sync.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_sync.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_wrk146_positioning.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_wrk146_positioning.cpython-313.pyc`
  - … 2 additional noise paths omitted from this summary.

Concise next actions:

1. Create `docs/registry/module-routing.yaml` covering pages, content, demos, calculators, scripts, tests, and deployment/review surfaces.
2. Keep the registry aligned with `docs/maps/aceengineer-website-operator-map.md` and `docs/README.md`.
3. Clean runtime/build/cache artifacts from root and trusted test paths.

## Current Broken/Missing Surface Inventory

Required missing surfaces:

- `workspace-hub/docs/maps/workspace-hub-operator-map.md`
- `workspace-hub/docs/registry/module-routing.yaml`
- `aceengineer-website/docs/registry/module-routing.yaml`

Confirmed broken/stale active references:

- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md`
- `workspace-hub/docs/README.md:264` mentions stale legacy `.agent-os` residue
- `digitalmodel/README.md:73` -> `specs/data-needs.yaml`
- `digitalmodel/docs/maps/digitalmodel-operator-map.md:9` -> `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — repo-local target missing; workspace-level map exists

## Next Actions, Ranked

1. **workspace-hub:** add the missing repo-wide operator map and machine-readable registry; remove stale legacy references from `docs/README.md`.
2. **aceengineer-website:** add `docs/registry/module-routing.yaml`; keep repo status red until this exists.
3. **digitalmodel:** fix the missing `specs/data-needs.yaml` reference and clarify the workspace-level historical map reference.
4. **assetutilities:** clean runtime/cache/log noise from trusted source/test paths; do not chase stale broken-link false positives.
5. **Portfolio:** continue daily local freshness refreshes; no new cron jobs should be scheduled by this audit.

## Verification Notes

- Report refreshed at `docs/reports/tier-1-indexing-freshness-latest.md`.
- Current canonical routing surfaces only were used: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/*operator-map*.md`, and `docs/registry/module-routing.yaml` where present.
- Legacy references were reported only as stale residue, not as recommended routing patterns.
