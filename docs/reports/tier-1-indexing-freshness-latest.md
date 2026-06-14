# Tier-1 Indexing Freshness Audit — Latest

- **Generated:** 2026-06-14T03:32:51-05:00
- **Scope:** workspace-hub, digitalmodel, assetutilities, aceengineer-website
- **Mode:** scheduled freshness audit; no cron jobs created or modified
- **Drift summary:** No material drift detected at the status level relative to the latest known RED/YELLOW baseline.
- **2026-04-22 scorecard assumption verdict:** Portfolio-level 2026-04-22 assumption still holds: tier-1 routing/index readiness remains partial and needs curation. Repo-specific assumptions need revision where live evidence differs from the original scorecard: `assetutilities` is yellow when only trusted-path runtime/cache noise remains; `aceengineer-website` remains red until `docs/registry/module-routing.yaml` exists; `workspace-hub` remains red while canonical operator-map/registry gaps and active legacy links persist; `digitalmodel` remains red while the broken `README.md` specs link and trusted-path cache noise persist.

## Status Summary

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | **red** | Missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`<br>Broken links: `docs/README.md:300 -> ../.agent-os/product/mission.md`; `docs/README.md:301 -> ../.agent-os/product/tech-stack.md`; `docs/README.md:302 -> ../.agent-os/product/roadmap.md`; `docs/README.md:303 -> ../.agent-os/product/decisions.md`<br>Active legacy references: `docs/README.md:300 -> .agent-os/product/mission.md`; `docs/README.md:301 -> .agent-os/product/tech-stack.md`; `docs/README.md:302 -> .agent-os/product/roadmap.md`; `docs/README.md:303 -> .agent-os/product/decisions.md` | create/restore missing canonical routing surfaces: docs/maps/workspace-hub-operator-map.md, docs/registry/module-routing.yaml; repair broken canonical Markdown/registry path references; replace active legacy `.agent-os/product/*` routing links with current canonical surfaces; remove or explicitly quarantine cache/runtime/backup noise from trusted routing/source paths |
| `digitalmodel` | **red** | Broken links: `README.md:73 -> specs/data-needs.yaml` | repair broken canonical Markdown/registry path references; remove or explicitly quarantine cache/runtime/backup noise from trusted routing/source paths |
| `assetutilities` | **yellow** | None confirmed in canonical surfaces | remove or explicitly quarantine cache/runtime/backup noise from trusted routing/source paths |
| `aceengineer-website` | **red** | Missing: `docs/registry/module-routing.yaml` | create/restore missing canonical routing surfaces: docs/registry/module-routing.yaml; remove or explicitly quarantine cache/runtime/backup noise from trusted routing/source paths |

## Per-Repo Evidence

### workspace-hub — red

- **Checkout inspected:** `/mnt/local-analysis/workspace-hub`
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/workspace-hub-operator-map.md`: MISSING
  - `docs/registry/module-routing.yaml`: MISSING
- **Confirmed broken Markdown links in canonical surfaces:**
  - `docs/README.md:300` -> `../.agent-os/product/mission.md`
  - `docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
  - `docs/README.md:302` -> `../.agent-os/product/roadmap.md`
  - `docs/README.md:303` -> `../.agent-os/product/decisions.md`
- **Active stale legacy references in canonical surfaces:**
  - `docs/README.md:300` -> `.agent-os/product/mission.md`
  - `docs/README.md:301` -> `.agent-os/product/tech-stack.md`
  - `docs/README.md:302` -> `.agent-os/product/roadmap.md`
  - `docs/README.md:303` -> `.agent-os/product/decisions.md`
- **Confirmed stale registry literal paths:**
  - none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `src/ace/__pycache__`
  - `src/ace/__pycache__/cli.cpython-311.pyc`
  - `src/ace/__pycache__/cli.cpython-312.pyc`
  - `src/ace/__pycache__/completion.cpython-311.pyc`
  - `src/ace/__pycache__/completion.cpython-312.pyc`
  - `src/ace/__pycache__/router.cpython-311.pyc`
  - `src/ace/__pycache__/router.cpython-312.pyc`
  - `src/ace/__pycache__/__init__.cpython-311.pyc`
  - `src/ace/__pycache__/__init__.cpython-312.pyc`
  - `src/config/__pycache__`
  - `src/config/__pycache__/config_loader.cpython-311.pyc`
  - `src/config/__pycache__/config_loader.cpython-312.pyc`
- **workspace-hub root/index noise examples:**
  - `.cache`
  - `.coverage`
  - `.mypy_cache`
  - `.pytest_cache`
  - `.ruff_cache`
  - `claude_smoke.log`
  - `daily_gmail_action_digest_2026-04-09.md`
  - `draft_ace_api_cfp_note.md`
  - `draft_skestates_1099_followup_email.md`
  - `draft_skestates_hoa_transfer_email.md`
  - `draft_skestates_pest_exteriors_followup.md`
  - `draft_skestates_site_plan_variance_followup.md`
  - `final_skestates_1099_followup_email.md`
  - `final_skestates_hoa_transfer_email.md`
  - `final_skestates_pest_exteriors_followup.md`
  - `gmail_copy_paste_packet_2026-04-09.md`
  - `gmail_operator_packet_2026-04-09.md`
  - `gmail_presend_checklist_2026-04-09.md`
  - `gmail_sendready_status_2026-04-09.md`
  - `gmail_thread_reply_map_2026-04-09.md`
  - `issue-1839-gh-comment.md`
  - `issue-1839-impl.diff`
  - `issue-1839-next-slice-impl.diff`
  - `issue-1839-next-slice-review.md`
  - `issue-1839-review.md`
  - `issue-1858-impl.diff`
  - `issue-1858-review.md`
  - `sendready_skestates_1099_email.md`
  - `sendready_skestates_hoa_email.md`
  - `sendready_skestates_pest_email.md`
- **Git status summary:**
  - ` M .claude/README.md`
  - ` M .claude/memory/KNOWLEDGE.md`
  - ` M .claude/memory/claude-auto-memory.md`
  - ` M .claude/memory/improve-log.md`
  - `M  .claude/state/candidates/agent-candidates.md`
  - `M  .claude/state/candidates/hook-candidates.md`
  - `M  .claude/state/candidates/mcp-candidates.md`
  - `M  .claude/state/candidates/script-candidates.md`
  - `M  .claude/state/candidates/skill-candidates.md`
  - ` M .claude/state/cc-user-insights.yaml`
  - `M  .claude/state/correction-trend-meta.json`
  - `M  .claude/state/drift-summary.yaml`
  - `M  .claude/state/portfolio-signals.yaml`
  - `M  .claude/state/readiness-issues.md`
  - `M  .claude/state/session-health.yaml`
  - `M  .claude/state/session-signals/ai-readiness.jsonl`
  - `M  .claude/state/session-signals/drift-counts.jsonl`
  - `M  .claude/state/session-signals/smoke-tests.jsonl`
  - `M  .claude/state/session-signals/test-health.jsonl`
  - `A  .claude/state/skill-eval-results/2026-06-14.jsonl`

### digitalmodel — red

- **Checkout inspected:** `/mnt/local-analysis/digitalmodel`
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/digitalmodel-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: present
- **Confirmed broken Markdown links in canonical surfaces:**
  - `README.md:73` -> `specs/data-needs.yaml`
- **Active stale legacy references in canonical surfaces:**
  - none confirmed
- **Confirmed stale registry literal paths:**
  - none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/hydro_matrices.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/mean_drift.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/model_summary.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/multi_body.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/panel_pressures.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/qa_summary.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/qtf_heatmap.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/rao_plots.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/sections/__pycache__/__init__.cpython-311.pyc`
  - `src/digitalmodel/orcawave/reporting/__pycache__`
  - `src/digitalmodel/orcawave/reporting/__pycache__/builder.cpython-311.pyc`
- **Git status summary:**
  - `clean`

### assetutilities — yellow

- **Checkout inspected:** `/mnt/local-analysis/assetutilities`
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/assetutilities-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: present
- **Confirmed broken Markdown links in canonical surfaces:**
  - none confirmed
- **Active stale legacy references in canonical surfaces:**
  - none confirmed
- **Confirmed stale registry literal paths:**
  - none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `src/assetutilities/common/download_data/__pycache__`
  - `src/assetutilities/common/download_data/__pycache__/dwnld_from_zipurl.cpython-311.pyc`
  - `src/assetutilities/common/download_data/__pycache__/dwnld_from_zipurl.cpython-312.pyc`
  - `src/assetutilities/common/readers/__pycache__`
  - `src/assetutilities/common/readers/__pycache__/csv_reader.cpython-311.pyc`
  - `src/assetutilities/common/readers/__pycache__/csv_reader.cpython-312.pyc`
  - `src/assetutilities/common/readers/__pycache__/data_getter.cpython-311.pyc`
  - `src/assetutilities/common/readers/__pycache__/data_getter.cpython-312.pyc`
  - `src/assetutilities/common/readers/__pycache__/data_reader.cpython-311.pyc`
  - `src/assetutilities/common/readers/__pycache__/data_reader.cpython-312.pyc`
  - `src/assetutilities/common/readers/__pycache__/excel_reader.cpython-311.pyc`
  - `src/assetutilities/common/readers/__pycache__/excel_reader.cpython-312.pyc`
- **Git status summary:**
  - `clean`

### aceengineer-website — red

- **Checkout inspected:** `/mnt/local-analysis/aceengineer-website`
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/aceengineer-website-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: MISSING
- **Confirmed broken Markdown links in canonical surfaces:**
  - none confirmed
- **Active stale legacy references in canonical surfaces:**
  - none confirmed
- **Confirmed stale registry literal paths:**
  - none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `tests/docs/__pycache__`
  - `tests/docs/__pycache__/test_routing_surfaces.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__`
  - `tests/python/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_competitor_analysis.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_clean.cpython-311-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_sync.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/test_content_sync.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_wrk146_positioning.cpython-312-pytest-9.0.2.pyc`
- **Git status summary:**
  - `clean`

## 2026-04-22 Scorecard Assumptions

- **Still holds:** The tier-1 portfolio is not yet uniformly route-ready; future issue work still needs clearer canonical operator maps and machine-readable registries to avoid misplaced code and slow retrieval.
- **Needs revision:** Treat repo-specific risk based on current live surfaces rather than the original April labels. `assetutilities` should not be treated as red if no broken canonical links are confirmed; `aceengineer-website` stays red for the missing registry; `workspace-hub` and `digitalmodel` stay red for confirmed canonical-surface drift.

## Concise Next Actions

1. `workspace-hub`: add/restore `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace active `.agent-os/product/*` links in `docs/README.md`; clean root/index residue.
2. `digitalmodel`: repair `README.md:73 -> specs/data-needs.yaml`; remove or quarantine trusted `src/` cache noise.
3. `assetutilities`: clean trusted `src/` cache/runtime noise; keep canonical surfaces under freshness watch.
4. `aceengineer-website`: add `docs/registry/module-routing.yaml`; clean test cache noise.

## Cron Scope Confirmation

- No new cron jobs were scheduled.
