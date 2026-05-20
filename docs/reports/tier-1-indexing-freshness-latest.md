# Tier-1 Indexing Freshness Audit — Latest

- **Run timestamp:** 2026-05-20T03:32:34-05:00 (Wed May 20 03:32:34 AM CDT 2026)
- **Workspace:** `/mnt/local-analysis/workspace-hub`
- **Repos in scope:** `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
- **Delivery/scheduling:** local report refresh only; no new cron jobs scheduled.
- **Portfolio status:** **RED**

## Summary

No material drift detected at the status level versus the latest corrected baseline; timestamp and evidence were refreshed. Existing blockers remain material until remediated.

Previous stale-report corrections remain in force: do not carry forward raw broken-link counts for `assetutilities` without reproduction, and keep `aceengineer-website` red until `docs/registry/module-routing.yaml` exists.

## Per-repo status

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | **RED** | missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`<br>broken/stale refs: `docs/README.md:300` -> `../.agent-os/product/mission.md`; `docs/README.md:301` -> `../.agent-os/product/tech-stack.md`; `docs/README.md:302` -> `../.agent-os/product/roadmap.md`; `docs/README.md:303` -> `../.agent-os/product/decisions.md`<br>stale legacy references: `docs/README.md:264`; `docs/README.md:300`; `docs/README.md:301`; `docs/README.md:302`; `docs/README.md:303`<br>trusted-path noise: `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-1-codex.log`, `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-2-codex.log`, `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-3-codex.log`, `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-4-codex.log`, `docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-5-codex.log`, `docs/plans/machine-prompts/2026-04-27/execution/orchestration-readiness-interactive-session.log`, `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/launch-summary.log`, `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-1-sesa.log` (+1427 more) | Create current operator map and module-routing registry; remove stale legacy references from docs/README.md; reduce root/runtime index noise. |
| `digitalmodel` | **YELLOW** | broken/stale refs: `README.md:73` -> `specs/data-needs.yaml`<br>operator-map authority notes: `docs/maps/digitalmodel-operator-map.md:9` -> `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` (repo-local target missing; workspace-level map exists)<br>trusted-path noise: `docs/domains/orcaflex/examples/qa/__pycache__`, `docs/domains/orcaflex/examples/qa/__pycache__/orcaflex_example_qa.cpython-311.pyc`, `docs/domains/orcawave/L01_aqwa_benchmark/__pycache__`, `docs/domains/orcawave/L01_aqwa_benchmark/__pycache__/run_orcawave_api.cpython-311.pyc`, `scripts/__pycache__`, `scripts/__pycache__/audit_spec_library.cpython-311.pyc`, `scripts/__pycache__/extract_property_inventory.cpython-311.pyc`, `scripts/__pycache__/semantic_validate.cpython-311.pyc` (+3618 more) | Repair or remove README reference to missing specs/data-needs.yaml; clarify OrcaWave/OrcaFlex operator-map authority if still intended; clean cache noise. |
| `assetutilities` | **YELLOW** | trusted-path noise: `src/assetutilities/__pycache__`, `src/assetutilities/__pycache__/__init__.cpython-311.pyc`, `src/assetutilities/__pycache__/__init__.cpython-312.pyc`, `src/assetutilities/__pycache__/__init__.cpython-313.pyc`, `src/assetutilities/__pycache__/engine.cpython-311.pyc`, `src/assetutilities/__pycache__/engine.cpython-312.pyc`, `src/assetutilities/__pycache__/math_helpers.cpython-311.pyc`, `src/assetutilities/agent_os/cli/__pycache__` (+629 more) | Keep canonical surfaces; clean generated cache/runtime/log/report noise from trusted source/test/docs paths or exclude it explicitly. |
| `aceengineer-website` | **RED** | missing: `docs/registry/module-routing.yaml`<br>trusted-path noise: `scripts/__pycache__`, `scripts/__pycache__/__init__.cpython-311.pyc`, `scripts/__pycache__/__init__.cpython-312.pyc`, `scripts/__pycache__/competitor_analysis.cpython-312.pyc`, `scripts/__pycache__/content_sync.cpython-312.pyc`, `scripts/__pycache__/content_sync.cpython-313.pyc`, `scripts/maintenance/__pycache__`, `scripts/maintenance/__pycache__/__init__.cpython-311.pyc` (+25 more) | Add docs/registry/module-routing.yaml; keep website operator map aligned with actual source/content paths; clean cache noise. |

## Detailed evidence

### workspace-hub — RED

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — MISSING
- `docs/registry/module-routing.yaml` — MISSING

Missing required/current surfaces:
- `workspace-hub/docs/maps/workspace-hub-operator-map.md`
- `workspace-hub/docs/registry/module-routing.yaml`

Confirmed broken/stale active references:
- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md` — `- [Mission & Vision](../.agent-os/product/mission.md)`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md` — `- [Technical Stack](../.agent-os/product/tech-stack.md)`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md` — `- [Development Roadmap](../.agent-os/product/roadmap.md)`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md` — `- [Product Decisions](../.agent-os/product/decisions.md)`

Stale legacy reference evidence (do not use as current routing pattern):
- `docs/README.md:264` — `├── .agent-os/              # Agent OS configuration`
- `docs/README.md:300` — `- [Mission & Vision](../.agent-os/product/mission.md)`
- `docs/README.md:301` — `- [Technical Stack](../.agent-os/product/tech-stack.md)`
- `docs/README.md:302` — `- [Development Roadmap](../.agent-os/product/roadmap.md)`
- `docs/README.md:303` — `- [Product Decisions](../.agent-os/product/decisions.md)`

Trusted-path/root noise examples (1435 detected, capped examples):
- `workspace-hub/docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-1-codex.log`
- `workspace-hub/docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-2-codex.log`
- `workspace-hub/docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-3-codex.log`
- `workspace-hub/docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-4-codex.log`
- `workspace-hub/docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-5-codex.log`
- `workspace-hub/docs/plans/machine-prompts/2026-04-27/execution/orchestration-readiness-interactive-session.log`
- `workspace-hub/docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/launch-summary.log`
- `workspace-hub/docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-1-sesa.log`
- `workspace-hub/docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-2-doris-university.log`
- `workspace-hub/docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-3-doris-codes.log`
- `workspace-hub/docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-4-woodfibre.log`
- `workspace-hub/docs/sessions/bulk-comment-2026-05-18T193334Z.log`
- `workspace-hub/docs/sessions/bulk-comment-retry-2026-05-18T212122Z.log`
- `workspace-hub/scripts/__pycache__`
- `workspace-hub/scripts/__pycache__/__init__.cpython-311.pyc`
- `workspace-hub/scripts/__pycache__/__init__.cpython-312.pyc`
- `workspace-hub/scripts/__pycache__/__init__.cpython-313.pyc`
- `workspace-hub/scripts/__pycache__/bash_command_prefixes.cpython-311.pyc`
- `workspace-hub/scripts/__pycache__/bash_command_prefixes.cpython-312.pyc`
- `workspace-hub/scripts/__pycache__/bash_command_prefixes.cpython-313.pyc`
- `workspace-hub/scripts/__pycache__/curate_worked_examples.cpython-313.pyc`
- `workspace-hub/scripts/__pycache__/refresh-agent-work-queue.cpython-311.pyc`
- `workspace-hub/scripts/__pycache__/refresh-agent-work-queue.cpython-312.pyc`
- `workspace-hub/scripts/__pycache__/skill-extractor.cpython-313.pyc`

Workspace root/index git status noise sample (5 lines shown):
```text
M .claude/skills/coordination/issue-planning-mode/SKILL.md
 M .claude/skills/github/github-issues/SKILL.md
 M config/ai-tools/agent-capability-radar.html
 M logs/orchestrator/hermes/skill-patches.jsonl
?? .claude/skills/coordination/issue-planning-mode/references/per-machine-repo-placement-outcome-contract.md
```

### digitalmodel — YELLOW

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/digitalmodel-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Missing required/current surfaces:
- none detected

Confirmed broken/stale active references:
- `digitalmodel/README.md:73` -> `specs/data-needs.yaml` — `- [specs/data-needs.yaml](specs/data-needs.yaml) -- Data dependency lifecycle tracker`

Operator-map authority notes:
- `digitalmodel/docs/maps/digitalmodel-operator-map.md:9` -> `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — repo-local target missing; workspace-level map exists; line: ``docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` remains useful for`

Trusted-path/root noise examples (3626 detected, capped examples):
- `digitalmodel/docs/domains/orcaflex/examples/qa/__pycache__`
- `digitalmodel/docs/domains/orcaflex/examples/qa/__pycache__/orcaflex_example_qa.cpython-311.pyc`
- `digitalmodel/docs/domains/orcawave/L01_aqwa_benchmark/__pycache__`
- `digitalmodel/docs/domains/orcawave/L01_aqwa_benchmark/__pycache__/run_orcawave_api.cpython-311.pyc`
- `digitalmodel/scripts/__pycache__`
- `digitalmodel/scripts/__pycache__/audit_spec_library.cpython-311.pyc`
- `digitalmodel/scripts/__pycache__/extract_property_inventory.cpython-311.pyc`
- `digitalmodel/scripts/__pycache__/semantic_validate.cpython-311.pyc`
- `digitalmodel/scripts/benchmark/__pycache__`
- `digitalmodel/scripts/benchmark/__pycache__/validate_owd_vs_spec.cpython-311.pyc`
- `digitalmodel/scripts/examples/__pycache__`
- `digitalmodel/scripts/examples/__pycache__/pyvista_3d_evaluation.cpython-313.pyc`
- `digitalmodel/src/digitalmodel/__pycache__`
- `digitalmodel/src/digitalmodel/__pycache__/__init__.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/__init__.cpython-312.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/__init__.cpython-313.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/__main__.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/_compat.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/_compat.cpython-312.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/_compat.cpython-313.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/engine.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/sections.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/units.cpython-311.pyc`
- `digitalmodel/src/digitalmodel/__pycache__/units.cpython-312.pyc`

### assetutilities — YELLOW

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Missing required/current surfaces:
- none detected

Confirmed broken/stale active references:
- none confirmed after false-positive filtering

Trusted-path/root noise examples (637 detected, capped examples):
- `assetutilities/src/assetutilities/__pycache__`
- `assetutilities/src/assetutilities/__pycache__/__init__.cpython-311.pyc`
- `assetutilities/src/assetutilities/__pycache__/__init__.cpython-312.pyc`
- `assetutilities/src/assetutilities/__pycache__/__init__.cpython-313.pyc`
- `assetutilities/src/assetutilities/__pycache__/engine.cpython-311.pyc`
- `assetutilities/src/assetutilities/__pycache__/engine.cpython-312.pyc`
- `assetutilities/src/assetutilities/__pycache__/math_helpers.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/__init__.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/interactive.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/main.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__/progress.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/__init__.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/__init__.cpython-313.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/cli.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/context_optimization.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/context_optimization.cpython-313.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/create_module_agent.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/create_module_agent.cpython-313.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/documentation_integration.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/documentation_integration.cpython-313.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/specs_integration.cpython-311.pyc`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__/template_management.cpython-311.pyc`

### aceengineer-website — RED

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — MISSING

Missing required/current surfaces:
- `aceengineer-website/docs/registry/module-routing.yaml`

Confirmed broken/stale active references:
- none confirmed after false-positive filtering

Trusted-path/root noise examples (33 detected, capped examples):
- `aceengineer-website/scripts/__pycache__`
- `aceengineer-website/scripts/__pycache__/__init__.cpython-311.pyc`
- `aceengineer-website/scripts/__pycache__/__init__.cpython-312.pyc`
- `aceengineer-website/scripts/__pycache__/competitor_analysis.cpython-312.pyc`
- `aceengineer-website/scripts/__pycache__/content_sync.cpython-312.pyc`
- `aceengineer-website/scripts/__pycache__/content_sync.cpython-313.pyc`
- `aceengineer-website/scripts/maintenance/__pycache__`
- `aceengineer-website/scripts/maintenance/__pycache__/__init__.cpython-311.pyc`
- `aceengineer-website/scripts/maintenance/__pycache__/__init__.cpython-312.pyc`
- `aceengineer-website/scripts/maintenance/__pycache__/verify_repo_structure.cpython-311.pyc`
- `aceengineer-website/scripts/maintenance/__pycache__/verify_repo_structure.cpython-312.pyc`
- `aceengineer-website/tests/__pycache__`
- `aceengineer-website/tests/__pycache__/__init__.cpython-311.pyc`
- `aceengineer-website/tests/__pycache__/__init__.cpython-312.pyc`
- `aceengineer-website/tests/__pycache__/__init__.cpython-313.pyc`
- `aceengineer-website/tests/docs/__pycache__`
- `aceengineer-website/tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__`
- `aceengineer-website/tests/python/__pycache__/__init__.cpython-311.pyc`
- `aceengineer-website/tests/python/__pycache__/__init__.cpython-312.pyc`
- `aceengineer-website/tests/python/__pycache__/__init__.cpython-313.pyc`
- `aceengineer-website/tests/python/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`
- `aceengineer-website/tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`

## 2026-04-22 tier-1 indexing scorecard assumption check

**Partially still holds; detail-level revision is still required.**

Still holds:
- Portfolio remains only partially ready for reliable code placement and canonical retrieval.
- `workspace-hub` remains the strongest control-plane repo, but missing current routing surfaces plus root/index hygiene risk weaken trust.
- `digitalmodel` remains the strongest engineering source/test structure.
- Machine-readable routing remains incomplete until `workspace-hub` and `aceengineer-website` both expose `docs/registry/module-routing.yaml`.

Needs revision / already changed:
- `digitalmodel`, `assetutilities`, and `aceengineer-website` now have stronger canonical docs/operator surfaces than the original 2026-04-22 assumptions. Future scorecards should not describe those surfaces as absent where they now exist.
- The `assetutilities` broken-link concern remains corrected: no confirmed broken active canonical Markdown links were reproduced by this false-positive-filtered scan.

## Concise next actions

1. `workspace-hub`: add `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; remove stale legacy references from `docs/README.md`; clean or exclude root/runtime/cache noise from trusted index paths.
2. `aceengineer-website`: add `docs/registry/module-routing.yaml`.
3. `digitalmodel`: fix/remove the missing `specs/data-needs.yaml` reference and clarify whether the OrcaWave/OrcaFlex historical map is repo-local authority or workspace-level context.
4. `assetutilities`: clean generated cache/runtime/log/report noise from trusted source/test/docs paths or explicitly exclude it from routing/index scans.
5. Re-run this freshness audit after routing-surface remediation; do not schedule new cron jobs from this task.

## Scanner notes

- Checked only current canonical routing surfaces: `AGENTS.md`, `README.md`, `docs/README.md`, repo-local operator maps under `docs/maps/`, and `docs/registry/module-routing.yaml`.
- Did not use or recommend legacy product-doc paths as current routing surfaces.
- Markdown-link checks used relative resolution from the containing file and skipped wildcard/example patterns to avoid known false positives.
