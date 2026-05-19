# Tier-1 Indexing Freshness Audit — Latest

- **Run timestamp:** 2026-05-19T03:31:09-05:00 (Tue May 19 03:31:09 AM CDT 2026)
- **Workspace:** `/mnt/local-analysis/workspace-hub`
- **Repos in scope:** `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
- **Delivery/scheduling:** local report refresh only; no new cron jobs scheduled.
- **Portfolio status:** **RED**

## Summary

Material drift/blockers remain in tier-1 routing trust surfaces. Status-level baseline is unchanged from the latest known audit: workspace-hub and aceengineer-website remain red; digitalmodel and assetutilities remain yellow.

Previous stale-report corrections remain in force: do not carry forward raw broken-link counts for assetutilities without reproduction, and keep aceengineer-website red until `docs/registry/module-routing.yaml` exists.

## Per-repo status

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | **RED** | missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`<br>broken links: `docs/README.md:300` -> `../.agent-os/product/mission.md`; `docs/README.md:301` -> `../.agent-os/product/tech-stack.md`; `docs/README.md:302` -> `../.agent-os/product/roadmap.md`; `docs/README.md:303` -> `../.agent-os/product/decisions.md`<br>stale legacy references: `docs/README.md:264`; `docs/README.md:300`; `docs/README.md:301`; `docs/README.md:302`; `docs/README.md:303`<br>trusted-path noise: `src/__pycache__`, `src/ace/__pycache__`, `src/ace/__pycache__/cli.cpython-311.pyc`, `src/ace/__pycache__/cli.cpython-312.pyc`, `src/ace/__pycache__/completion.cpython-311.pyc`, `src/ace/__pycache__/completion.cpython-312.pyc`, `src/ace/__pycache__/router.cpython-311.pyc`, `src/ace/__pycache__/router.cpython-312.pyc` (+233 more) | Create current operator map and module-routing registry; remove stale legacy references from docs/README.md; reduce root/runtime index noise. |
| `digitalmodel` | **YELLOW** | broken links: `README.md:73` -> `specs/data-needs.yaml`<br>trusted-path noise: `src/digitalmodel/__pycache__`, `src/digitalmodel/infrastructure/__pycache__`, `src/digitalmodel/infrastructure/base_configs/__pycache__`, `src/digitalmodel/infrastructure/base_configs/__pycache__/__init__.cpython-311.pyc`, `src/digitalmodel/infrastructure/base_solvers/__pycache__`, `src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__`, `src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__/benchmark_suite.cpython-311.pyc`, `src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__/configuration_benchmarks.cpython-311.pyc` (+195 more) | Repair or remove README reference to missing specs/data-needs.yaml; clarify OrcaWave/OrcaFlex operator-map authority if still intended. |
| `assetutilities` | **YELLOW** | trusted-path noise: `src/assetutilities/__pycache__`, `src/assetutilities/agent_os/cli/__pycache__`, `src/assetutilities/agent_os/cli/__pycache__/interactive.cpython-311.pyc`, `src/assetutilities/agent_os/cli/__pycache__/main.cpython-311.pyc`, `src/assetutilities/agent_os/cli/__pycache__/progress.cpython-311.pyc`, `src/assetutilities/agent_os/cli/__pycache__/__init__.cpython-311.pyc`, `src/assetutilities/agent_os/commands/__pycache__`, `src/assetutilities/agent_os/commands/cli_components/__pycache__` (+201 more) | Keep canonical surfaces; clean generated cache/runtime/log/report noise from trusted source/test/docs paths or ignore it explicitly. |
| `aceengineer-website` | **RED** | missing: `docs/registry/module-routing.yaml`<br>trusted-path noise: `tests/__pycache__`, `tests/docs/__pycache__`, `tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__`, `tests/python/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc`, `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`, `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`, `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc` (+14 more) | Add docs/registry/module-routing.yaml; keep website operator map aligned with actual source/content paths. |

## Detailed evidence

### workspace-hub — RED

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — MISSING
- `docs/registry/module-routing.yaml` — MISSING

Confirmed broken/stale active references:
- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md`

Stale legacy reference evidence (do not use as current routing pattern):
- `docs/README.md:264` — `├── .agent-os/              # Agent OS configuration`
- `docs/README.md:300` — `- [Mission & Vision](../.agent-os/product/mission.md)`
- `docs/README.md:301` — `- [Technical Stack](../.agent-os/product/tech-stack.md)`
- `docs/README.md:302` — `- [Development Roadmap](../.agent-os/product/roadmap.md)`
- `docs/README.md:303` — `- [Product Decisions](../.agent-os/product/decisions.md)`

Trusted-path/root noise examples (241 detected, capped examples):
- `workspace-hub/src/__pycache__`
- `workspace-hub/src/ace/__pycache__`
- `workspace-hub/src/ace/__pycache__/cli.cpython-311.pyc`
- `workspace-hub/src/ace/__pycache__/cli.cpython-312.pyc`
- `workspace-hub/src/ace/__pycache__/completion.cpython-311.pyc`
- `workspace-hub/src/ace/__pycache__/completion.cpython-312.pyc`
- `workspace-hub/src/ace/__pycache__/router.cpython-311.pyc`
- `workspace-hub/src/ace/__pycache__/router.cpython-312.pyc`
- `workspace-hub/src/ace/__pycache__/__init__.cpython-311.pyc`
- `workspace-hub/src/ace/__pycache__/__init__.cpython-312.pyc`
- `workspace-hub/src/config/__pycache__`
- `workspace-hub/src/config/__pycache__/config_loader.cpython-311.pyc`
- `workspace-hub/src/config/__pycache__/config_loader.cpython-312.pyc`
- `workspace-hub/src/config/__pycache__/config_manager.cpython-311.pyc`
- `workspace-hub/src/config/__pycache__/config_manager.cpython-312.pyc`
- `workspace-hub/src/config/__pycache__/schema_validator.cpython-311.pyc`
- `workspace-hub/src/config/__pycache__/schema_validator.cpython-312.pyc`
- `workspace-hub/src/config/__pycache__/__init__.cpython-311.pyc`
- `workspace-hub/src/config/__pycache__/__init__.cpython-312.pyc`
- `workspace-hub/src/digitalmodel/subsea/pipeline/free_span/__pycache__`
- `workspace-hub/src/digitalmodel/subsea/pipeline/free_span/__pycache__/models.cpython-311.pyc`
- `workspace-hub/src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_allowable_length.cpython-311.pyc`
- `workspace-hub/src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_fatigue_damage.cpython-311.pyc`
- `workspace-hub/src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_natural_frequency.cpython-311.pyc`
- `workspace-hub/src/digitalmodel/subsea/pipeline/free_span/__pycache__/span_natural_frequency.cpython-313.pyc`

### digitalmodel — YELLOW

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/digitalmodel-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Confirmed broken/stale active references:
- `digitalmodel/README.md:73` -> `specs/data-needs.yaml`

Trusted-path/root noise examples (203 detected, capped examples):
- `digitalmodel/src/digitalmodel/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_configs/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_configs/__pycache__/__init__.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__/benchmark_suite.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__/configuration_benchmarks.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__/report_generator.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__/solver_benchmarks.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__/__init__.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/config/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/config/__pycache__/solver_config.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/config/__pycache__/__init__.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/fatigue/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/fatigue/__pycache__/fatigue_analysis.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/fatigue/__pycache__/fatigue_analysis.cpython-313.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/fatigue/__pycache__/__init__.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__/cathodic_protection.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__/code_dnvrph103_hydrodynamics_circular.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__/code_dnvrph103_hydrodynamics_rectangular.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__/cp_DNV_RP_B401_2021.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__/cp_DNV_RP_F103_2010.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__/cp_sacrificial_anode_b401.cpython-311.pyc`

### assetutilities — YELLOW

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Trusted-path/root noise examples (209 detected, capped examples):
- `assetutilities/src/assetutilities/__pycache__`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/interactive.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/main.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/progress.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/__init__.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/error_handler.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/help_system.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/interactive.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/interface.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/manager.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/models.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/progress.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__/__init__.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/context/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/context/__pycache__/chunking.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/context/__pycache__/embedding.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/context/__pycache__/optimizer.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/context/__pycache__/processor.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/context/__pycache__/__init__.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/docs/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/docs/__pycache__/linker.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/docs/__pycache__/parser.cpython-311.pyc`

### aceengineer-website — RED

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — MISSING

Trusted-path/root noise examples (22 detected, capped examples):
- `aceengineer-website/tests/__pycache__`
- `aceengineer-website/tests/docs/__pycache__`
- `aceengineer-website/tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__`
- `aceengineer-website/tests/python/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`
- `aceengineer-website/tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/test_competitor_analysis.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/test_content_clean.cpython-311-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/test_content_sync.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/test_content_sync.cpython-313-pytest-9.0.3.pyc`
- `aceengineer-website/tests/python/__pycache__/test_wrk146_positioning.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/test_wrk146_positioning.cpython-313.pyc`
- `aceengineer-website/tests/python/__pycache__/__init__.cpython-311.pyc`
- `aceengineer-website/tests/python/__pycache__/__init__.cpython-312.pyc`
- `aceengineer-website/tests/python/__pycache__/__init__.cpython-313.pyc`
- `aceengineer-website/tests/repo_structure/__pycache__`
- `aceengineer-website/tests/repo_structure/__pycache__/test_repo_structure_contract.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/__pycache__/__init__.cpython-311.pyc`
- `aceengineer-website/tests/__pycache__/__init__.cpython-312.pyc`
- `aceengineer-website/tests/__pycache__/__init__.cpython-313.pyc`

## 2026-04-22 tier-1 indexing scorecard assumption check

**Partially still holds; detail-level revision is required.**

- Still holds: the portfolio is not yet fully reliable for code placement and canonical retrieval because required machine-readable routing remains incomplete.
- Still holds: `workspace-hub` remains the strongest control-plane repo, but root/index hygiene and missing current routing surfaces weaken routing trust.
- Still holds: `digitalmodel` remains the strongest engineering source/test structure, but has at least one stale README reference that should be resolved.
- Still holds until remediated: `workspace-hub` and `aceengineer-website` lack `docs/registry/module-routing.yaml`.
- Needs revision: `digitalmodel`, `assetutilities`, and `aceengineer-website` now have stronger canonical docs/operator surfaces than the original 2026-04-22 assumptions, so future scorecards should not describe those surfaces as absent if they exist.

## Next actions

1. `workspace-hub`: create `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; remove stale legacy references from `docs/README.md`.
2. `aceengineer-website`: create `docs/registry/module-routing.yaml` to make website source/content routing machine-readable.
3. `digitalmodel`: fix `README.md` link to `specs/data-needs.yaml` or restore the referenced registry/spec file if it is canonical.
4. `assetutilities`: clean or explicitly exclude runtime/cache/log/report outputs under trusted paths; keep false-positive filtered link scanning.
5. Re-run this freshness audit after any routing-surface changes; do not schedule additional cron jobs from this report.

## Material-change note

No material status-level drift detected relative to the latest known baseline. The report timestamp and evidence were refreshed; confirmed blockers remain open.
