# Tier-1 Indexing Freshness Audit — Latest

- **Generated:** 2026-06-13T03:33:26-05:00
- **Scope:** workspace-hub, digitalmodel, assetutilities, aceengineer-website
- **Mode:** scheduled freshness audit; no cron jobs created or modified
- **Drift summary:** No material drift detected at the status level relative to the latest known RED/YELLOW baseline.
- **2026-04-22 scorecard assumption verdict:** Portfolio-level 2026-04-22 assumption still holds: tier-1 routing/index readiness remains partial and needs curation. Repo-specific details need revision where live surfaces have changed (notably assetutilities is no longer red if only trusted-path noise remains; aceengineer-website remains red until module-routing registry exists).

## Status Summary

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | **red** | Missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`<br>Broken links: `docs/README.md:300 -> ../.agent-os/product/mission.md`; `docs/README.md:301 -> ../.agent-os/product/tech-stack.md`; `docs/README.md:302 -> ../.agent-os/product/roadmap.md`; `docs/README.md:303 -> ../.agent-os/product/decisions.md`<br>Active legacy references: `docs/README.md:300 -> .agent-os/product/mission.md`; `docs/README.md:301 -> .agent-os/product/tech-stack.md`; `docs/README.md:302 -> .agent-os/product/roadmap.md`; `docs/README.md:303 -> .agent-os/product/decisions.md` | create/restore missing canonical routing surfaces: docs/maps/workspace-hub-operator-map.md, docs/registry/module-routing.yaml; repair broken Markdown links in canonical surfaces; replace active legacy .agent-os routing links with current canonical surfaces; remove or ignore trusted-path cache/runtime/backup noise; clean workspace-hub root/index residue so routing surfaces remain trustworthy |
| `digitalmodel` | **red** | Broken links: `README.md:73 -> specs/data-needs.yaml` | repair broken Markdown links in canonical surfaces; remove or ignore trusted-path cache/runtime/backup noise |
| `assetutilities` | **yellow** | None confirmed in canonical surfaces | remove or ignore trusted-path cache/runtime/backup noise |
| `aceengineer-website` | **red** | Missing: `docs/registry/module-routing.yaml` | create/restore missing canonical routing surfaces: docs/registry/module-routing.yaml; remove or ignore trusted-path cache/runtime/backup noise |

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
- **Confirmed stale registry literal paths:** none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `src/__pycache__`
  - `src/ace/__pycache__`
  - `src/config/__pycache__`
  - `src/geometry/__pycache__`
  - `src/knowledge_graph/__pycache__`
  - `src/models/__pycache__`
  - `src/solvers/__pycache__`
  - `src/utilities/__pycache__`
  - `src/__pycache__/__init__.cpython-311.pyc`
  - `src/__pycache__/__init__.cpython-312.pyc`
  - `src/__pycache__/__init__.cpython-313.pyc`
  - `src/workspace_hub/math/__pycache__`
- **workspace-hub root/index noise examples:**
  - `.coverage`
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
  - `daily_gmail_action_digest_2026-04-09.md`
  - `sendready_skestates_1099_email.md`
  - `sendready_skestates_hoa_email.md`
  - `sendready_skestates_pest_email.md`
  - `skestates_gmail_triage_2026-04-09.md`
  - `draft_ace_api_cfp_note.md`
  - `issue-1839-gh-comment.md`
  - `terminal-2-impl.diff`
  - `terminal-2-review.md`
  - `transcript_raw.json`
  - `video_summary.txt`
  - `youtube_summary.txt`
  - `issue-1839-impl.diff`
  - `issue-1839-next-slice-impl.diff`
  - `issue-1839-next-slice-review.md`
  - `issue-1839-review.md`
  - `issue-1858-impl.diff`
- **Git status summary:**
  - clean

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
- **Active stale legacy references in canonical surfaces:** none confirmed
- **Confirmed stale registry literal paths:** none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `src/digitalmodel/__pycache__`
  - `src/digitalmodel/orcawave/__pycache__`
  - `src/digitalmodel/ansys/__pycache__`
  - `src/digitalmodel/asset_integrity/__pycache__`
  - `src/digitalmodel/benchmarks/__pycache__`
  - `src/digitalmodel/cathodic_protection/__pycache__`
  - `src/digitalmodel/citations/__pycache__`
  - `src/digitalmodel/drilling_riser/__pycache__`
  - `src/digitalmodel/fatigue/__pycache__`
  - `src/digitalmodel/field_development/__pycache__`
  - `src/digitalmodel/geotechnical/__pycache__`
  - `src/digitalmodel/gis/__pycache__`
- **Git status summary:**
  - clean

### assetutilities — yellow

- **Checkout inspected:** `/mnt/local-analysis/assetutilities`
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/assetutilities-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: present
- **Confirmed broken Markdown links in canonical surfaces:** none
- **Active stale legacy references in canonical surfaces:** none confirmed
- **Confirmed stale registry literal paths:** none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `src/assetutilities/__pycache__`
  - `src/assetutilities/common/__pycache__`
  - `src/assetutilities/modules/__pycache__`
  - `src/assetutilities/__pycache__/engine.cpython-311.pyc`
  - `src/assetutilities/__pycache__/engine.cpython-312.pyc`
  - `src/assetutilities/__pycache__/__init__.cpython-311.pyc`
  - `src/assetutilities/__pycache__/__init__.cpython-312.pyc`
  - `src/assetutilities/modules/csv_utilities/__pycache__`
  - `src/assetutilities/modules/data_exploration/__pycache__`
  - `src/assetutilities/modules/test_utilities/__pycache__`
  - `src/assetutilities/modules/yml_utilities/__pycache__`
  - `src/assetutilities/modules/zip_utilities/__pycache__`
- **Git status summary:**
  - clean

### aceengineer-website — red

- **Checkout inspected:** `/mnt/local-analysis/aceengineer-website`
- **Canonical surfaces:**
  - `AGENTS.md`: present
  - `README.md`: present
  - `docs/README.md`: present
  - `docs/maps/aceengineer-website-operator-map.md`: present
  - `docs/registry/module-routing.yaml`: MISSING
- **Confirmed broken Markdown links in canonical surfaces:** none
- **Active stale legacy references in canonical surfaces:** none confirmed
- **Confirmed stale registry literal paths:** none confirmed or registry absent
- **Trusted source/test path noise examples:**
  - `tests/__pycache__`
  - `tests/docs/__pycache__`
  - `tests/python/__pycache__`
  - `tests/repo_structure/__pycache__`
  - `tests/__pycache__/__init__.cpython-311.pyc`
  - `tests/__pycache__/__init__.cpython-312.pyc`
  - `tests/__pycache__/__init__.cpython-313.pyc`
  - `tests/repo_structure/__pycache__/test_repo_structure_contract.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-311-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc`
  - `tests/python/__pycache__/conftest.cpython-313-pytest-9.0.3.pyc`
  - `tests/python/__pycache__/test_brand_identity_assets.cpython-312-pytest-9.0.2.pyc`
- **Git status summary:**
  - clean

## 2026-04-22 Tier-1 Indexing Scorecard Assumptions

Portfolio-level 2026-04-22 assumption still holds: tier-1 routing/index readiness remains partial and needs curation. Repo-specific details need revision where live surfaces have changed (notably assetutilities is no longer red if only trusted-path noise remains; aceengineer-website remains red until module-routing registry exists).

Current repo-specific assumption status:
- `workspace-hub`: Still needs revision/remediation: control-plane routing remains red due missing operator map/registry and root/index noise.
- `digitalmodel`: Still needs revision/remediation if broken README data-needs reference or trusted src cache noise persists.
- `assetutilities`: Needs repo-specific revision from older red baseline: required canonical surfaces are present; current blocker is trusted-path noise, so status is yellow unless new broken references appear.
- `aceengineer-website`: Still holds as red for durable issue-routing until docs/registry/module-routing.yaml exists.

## Concise Next Actions

- `workspace-hub`: create/restore missing canonical routing surfaces: docs/maps/workspace-hub-operator-map.md, docs/registry/module-routing.yaml; repair broken Markdown links in canonical surfaces; replace active legacy .agent-os routing links with current canonical surfaces; remove or ignore trusted-path cache/runtime/backup noise; clean workspace-hub root/index residue so routing surfaces remain trustworthy
- `digitalmodel`: repair broken Markdown links in canonical surfaces; remove or ignore trusted-path cache/runtime/backup noise
- `assetutilities`: remove or ignore trusted-path cache/runtime/backup noise
- `aceengineer-website`: create/restore missing canonical routing surfaces: docs/registry/module-routing.yaml; remove or ignore trusted-path cache/runtime/backup noise

## Notes

- Legacy `.agent-os` reference patterns were not used as canonical routing surfaces in this audit.
- Wildcard/example path references were filtered out; only confirmed literal missing links/paths are reported.
- No new cron jobs were scheduled.
