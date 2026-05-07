# Tier-1 Approval-State Audit — 2026-05-06

Generated: `2026-05-06T20:59:30` local time

## Scope

Scoped tier-1 repos audited for live open GitHub issues carrying `status:plan-approved`:

- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `worldenergydata`
- `assethold`
- `aceengineer-website`

Evidence surfaces checked per approved issue:

1. Live GitHub labels from `gh issue list --label status:plan-approved`.
2. Conflicting live `status:plan-review` label.
3. Canonical local plan file under `docs/plans/` using issue-number filename matching.
4. Local approval marker under `.planning/plan-approved/<issue>.md`.
5. Repo branch and dirty worktree state for execution-readiness risk.

## Executive summary

- Live `status:plan-approved` open issues found: **212**.
- Fully evidenced approved issues with plan + marker and no conflict: **135**.
- Fully evidenced and not already `status:working`: **129** execution-candidate issues before additional issue-specific worktree checks.
- Missing canonical plan evidence: **25** issues.
- Missing `.planning/plan-approved` marker: **73** issues.
- Remaining plan-review/approved label conflicts: **0**.
- Already marked `status:working`: **15** issues; these should not be launched as new worker lanes without implementation-state audit.
- Dirty local repo clones: **4** of 6; use isolated clean worktrees before execution waves.

Decision: treat the approved pool as **partially executable, partially governance-drifted**. Launch only from the fully evidenced, non-working subset after issue-specific worktree/branch ownership is assigned.

## Repo-level approval evidence matrix

| Repo | Branch | Worktree | Live approved | Fully evidenced | Missing plan | Missing marker | Label conflicts | Already working |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `workspace-hub` | `chore/llm-wiki-spinout-cleanup` | `dirty:20` | 22 | 8 | 8 | 10 | 0 | 14 |
| `digitalmodel` | `fix/issue-555-chain-database-diameters-slice` | `dirty:80` | 85 | 78 | 7 | 7 | 0 | 1 |
| `assetutilities` | `main` | `dirty:2` | 21 | 21 | 0 | 0 | 0 | 0 |
| `worldenergydata` | `main` | `clean` | 57 | 1 | 10 | 56 | 0 | 0 |
| `assethold` | `main` | `dirty:28` | 27 | 27 | 0 | 0 | 0 | 0 |
| `aceengineer-website` | `main` | `clean` | 0 | 0 | 0 | 0 | 0 | 0 |

## Drift classification

### P0 — Label conflicts

No live issue currently has both `status:plan-approved` and `status:plan-review`. The earlier `assetutilities#72` and `assethold#7` conflicts remain resolved in the live label state.

### P1 — Approved label without canonical planning evidence

Issues in this category are not safe for immediate execution. Repair by adding or locating the canonical `docs/plans/` artifact, adding/verifying `.planning/plan-approved/<issue>.md`, and posting a concise GitHub evidence comment before worker launch.

### Missing canonical plan file examples

| Repo | Issue | Approval marker | Labels | Worktree |
| --- | --- | --- | --- | --- |
| workspace-hub | [workspace-hub#2327](https://github.com/vamseeachanta/workspace-hub/issues/2327) — digitalmodel: CadQuery spike for parametric offshore geometry generation | — | `priority:low`, `cat:engineering`, `cat:research`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2152](https://github.com/vamseeachanta/workspace-hub/issues/2152) — test(reporting): add golden fixture corpus for weekly review run artifacts and validator coverage | `.planning/plan-approved/2152.md` | `enhancement`, `priority:medium`, `cat:operations`, `cat:harness`, `status:blocked`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2112](https://github.com/vamseeachanta/workspace-hub/issues/2112) — data(field-dev): backfill SubseaIQ equipment counts to unblock cost benchmarking | `.planning/plan-approved/2112.md` | `enhancement`, `priority:high`, `cat:engineering`, `agent:claude`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2055](https://github.com/vamseeachanta/workspace-hub/issues/2055) — feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts | `.planning/plan-approved/2055.md` | `enhancement`, `priority:high`, `cat:engineering`, `status:working`, `wip:ace-linux-1`, `dark-intelligence`, `agent:claude`, `agent:codex`, `status:plan-approved`, `status:needs-data`, `scope:v1` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1962](https://github.com/vamseeachanta/workspace-hub/issues/1962) — FEATURE: Tier-1 Repo Ecosystem Refactoring — audit, plan, execute with Claude Code plan mode | `.planning/plan-approved/1962.md` | `enhancement`, `priority:high`, `cat:engineering`, `cat:harness`, `status:working`, `agent:gemini`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1782](https://github.com/vamseeachanta/workspace-hub/issues/1782) — epic: zero-loss agent learnings — git-track ALL AI agent memories, corrections, patterns, and insights | — | `enhancement`, `priority:high`, `cat:ai-orchestration`, `cat:harness`, `status:working`, `machine:multi`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1583](https://github.com/vamseeachanta/workspace-hub/issues/1583) — Hermes config parity via repo ecosystem templates | — | `enhancement`, `priority:medium`, `cat:ai-orchestration`, `cat:harness`, `status:working`, `machine:multi`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1264](https://github.com/vamseeachanta/workspace-hub/issues/1264) — WRK-1365: OrcaFlex frame analysis | — | `enhancement`, `priority:high`, `cat:engineering-calculations`, `wrk-item`, `status:working`, `machine:licensed-win-1`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| digitalmodel | [digitalmodel#515](https://github.com/vamseeachanta/digitalmodel/issues/515) — Clarify and close semantic-equivalence gaps between spec/LLM-friendly YAML and OrcaFlex strict YAML | — | `enhancement`, `cat:engineering`, `priority:high`, `route:B`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#503](https://github.com/vamseeachanta/digitalmodel/issues/503) — Ingest OrcaFlex/OrcaWave online help into LLM-accessible format | — | `enhancement`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#501](https://github.com/vamseeachanta/digitalmodel/issues/501) — OrcaWave: expand QTF config + field points + irregular frequency method | — | `enhancement`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#500](https://github.com/vamseeachanta/digitalmodel/issues/500) — OrcaWave: mesh file pre-flight validation + auto-copy in runner | — | `enhancement`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#486](https://github.com/vamseeachanta/digitalmodel/issues/486) — Implement subsea connectors and jumpers module (API 17R) | — | `enhancement`, `cat:engineering`, `priority:medium`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#282](https://github.com/vamseeachanta/digitalmodel/issues/282) — WRK-130: Standardize analysis reporting for each OrcaWave structure type | — | `enhancement`, `cat:engineering`, `priority:high`, `wrk-item`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#279](https://github.com/vamseeachanta/digitalmodel/issues/279) — WRK-129: Standardize analysis reporting for each OrcaFlex structure type | — | `enhancement`, `cat:engineering`, `priority:high`, `wrk-item`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| … | 10 additional rows omitted from this report; full JSON: `/tmp/tier1_approval_state_audit.json` | | | |

### Missing approval marker examples

| Repo | Issue | Plan evidence | Labels | Worktree |
| --- | --- | --- | --- | --- |
| workspace-hub | [workspace-hub#2628](https://github.com/vamseeachanta/workspace-hub/issues/2628) — epic(digitalmodel-ci): domain-divided CI architecture replacing maxfail-masking pattern | `docs/plans/2026-05-03-issue-2628-digitalmodel-domain-divided-ci.md` | `enhancement`, `priority:high`, `cat:engineering`, `cat:harness`, `domain:testing`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) — docs(security): external contributor and unsolicited paid-help response runbook | `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` | `documentation`, `priority:medium`, `cat:documentation`, `domain:security`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) — chore(security): codify public repo interaction-limit renewal in scheduled tasks | `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` | `enhancement`, `priority:medium`, `cat:operations`, `domain:automation`, `domain:security`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2327](https://github.com/vamseeachanta/workspace-hub/issues/2327) — digitalmodel: CadQuery spike for parametric offshore geometry generation | — | `priority:low`, `cat:engineering`, `cat:research`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2124](https://github.com/vamseeachanta/workspace-hub/issues/2124) — feat(llm-wiki): extend ingestion to Orcina resources, examples, and training materials | `docs/plans/2026-04-24-issue-2124-orcina-resources-examples-training.md` | `enhancement`, `priority:medium`, `cat:data-pipeline`, `domain:marine`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2125](https://github.com/vamseeachanta/workspace-hub/issues/2125) — feat(llm-wiki): auto-refresh ingestion on new Orcina releases | `docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md` | `enhancement`, `priority:medium`, `cat:data-pipeline`, `domain:marine`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2046](https://github.com/vamseeachanta/workspace-hub/issues/2046) — Audit compliance of strict issue planning workflow after rollout | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | `priority:medium`, `cat:ai-orchestration`, `cat:operations`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1782](https://github.com/vamseeachanta/workspace-hub/issues/1782) — epic: zero-loss agent learnings — git-track ALL AI agent memories, corrections, patterns, and insights | — | `enhancement`, `priority:high`, `cat:ai-orchestration`, `cat:harness`, `status:working`, `machine:multi`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1583](https://github.com/vamseeachanta/workspace-hub/issues/1583) — Hermes config parity via repo ecosystem templates | — | `enhancement`, `priority:medium`, `cat:ai-orchestration`, `cat:harness`, `status:working`, `machine:multi`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1264](https://github.com/vamseeachanta/workspace-hub/issues/1264) — WRK-1365: OrcaFlex frame analysis | — | `enhancement`, `priority:high`, `cat:engineering-calculations`, `wrk-item`, `status:working`, `machine:licensed-win-1`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| digitalmodel | [digitalmodel#515](https://github.com/vamseeachanta/digitalmodel/issues/515) — Clarify and close semantic-equivalence gaps between spec/LLM-friendly YAML and OrcaFlex strict YAML | — | `enhancement`, `cat:engineering`, `priority:high`, `route:B`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#503](https://github.com/vamseeachanta/digitalmodel/issues/503) — Ingest OrcaFlex/OrcaWave online help into LLM-accessible format | — | `enhancement`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#501](https://github.com/vamseeachanta/digitalmodel/issues/501) — OrcaWave: expand QTF config + field points + irregular frequency method | — | `enhancement`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#500](https://github.com/vamseeachanta/digitalmodel/issues/500) — OrcaWave: mesh file pre-flight validation + auto-copy in runner | — | `enhancement`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#486](https://github.com/vamseeachanta/digitalmodel/issues/486) — Implement subsea connectors and jumpers module (API 17R) | — | `enhancement`, `cat:engineering`, `priority:medium`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| … | 58 additional rows omitted from this report; full JSON: `/tmp/tier1_approval_state_audit.json` | | | |

## Execution-candidate pool

These issues have both a canonical plan match and an approval marker, no label conflict, and are not already marked `status:working`. They still require a clean issue-specific worktree and branch before execution.

### Top fully evidenced, non-working candidates

| Repo | Issue | Plan evidence | Approval marker | Worktree |
| --- | --- | --- | --- | --- |
| workspace-hub | [workspace-hub#2563](https://github.com/vamseeachanta/workspace-hub/issues/2563) — Set up Telegram mobile access for Hermes AI control | `docs/plans/2026-05-02-issue-2563-telegram-hermes.md` | `.planning/plan-approved/2563.md` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2533](https://github.com/vamseeachanta/workspace-hub/issues/2533) — feat(repo-portfolio): review and revise mission/objective statements across active repos | `docs/plans/2026-04-27-issue-2533-repo-portfolio-mission-objective-review.md` | `.planning/plan-approved/2533.md` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2523](https://github.com/vamseeachanta/workspace-hub/issues/2523) — feat(workstations): add reusable Hermes preflight readiness checker | `docs/plans/2026-05-02-issue-2523-hermes-preflight.md` | `.planning/plan-approved/2523.md` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| digitalmodel | [digitalmodel#578](https://github.com/vamseeachanta/digitalmodel/issues/578) — W2W motion-compensated gangway operability module (DNV-ST-0358) | `docs/plans/2026-05-05-issue-578-w2w-gangway-operability.md` | `.planning/plan-approved/578.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#577](https://github.com/vamseeachanta/digitalmodel/issues/577) — Safety Case / MAH ALARP framework module (NORSOK Z-013, UK HSE SCR-2015) | `docs/plans/2026-05-05-issue-577-safety-case-mah-alarp.md` | `.planning/plan-approved/577.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#576](https://github.com/vamseeachanta/digitalmodel/issues/576) — FOWT watch-circle envelope check vs dynamic-cable curvature (DNV-RP-0360) | `docs/plans/2026-05-05-issue-576-fowt-watch-circle-cable-curvature.md` | `.planning/plan-approved/576.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#575](https://github.com/vamseeachanta/digitalmodel/issues/575) — FOWT coupled aero-hydro response Python facade (IEC 61400-3-2, DNV-RP-0286) | `docs/plans/2026-05-05-issue-575-fowt-coupled-aero-hydro-facade.md` | `.planning/plan-approved/575.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#574](https://github.com/vamseeachanta/digitalmodel/issues/574) — Wiki standards-page family for FOWT (IEC 61400-3-2, DNV-ST-0119, DNV-RP-0286, DNV-ST-0126, DNV-ST-0358, DNV-RP-0360, API RP 2SIM) | `docs/plans/2026-05-05-issue-574-fowt-wiki-standards-pages.md` | `.planning/plan-approved/574.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#573](https://github.com/vamseeachanta/digitalmodel/issues/573) — fix(marine_ops): DNV-RP-F103 calibration drift in test_cathodic_protection_dnv.py — clears 16 of 77 marine_ops failures | `docs/plans/2026-05-05-issue-573-dnv-rp-f103-cathodic-protection-calibration.md` | `.planning/plan-approved/573.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) — fix(marine_ops): batched residue clusters R1+R5+R7+R8 — clears ~10 of 77 marine_ops failures | `docs/plans/2026-05-05-issue-566-marine-ops-r1-r5-r7-r8-batched.md` | `.planning/plan-approved/566.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#565](https://github.com/vamseeachanta/digitalmodel/issues/565) — fix(marine_ops): test_hydro_coefficients.py::TestIntegration::test_csv_to_visualization_workflow — needs investigation | `docs/plans/2026-05-05-issue-565-hydro-coefficients-csv-to-visualization.md` | `.planning/plan-approved/565.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#564](https://github.com/vamseeachanta/digitalmodel/issues/564) — fix(marine_ops): test_ocimf_mooring_integration.py::test_environmental_forces_to_mooring_tension — needs investigation | `docs/plans/2026-05-05-issue-564-ocimf-mooring-environmental-forces-total.md` | `.planning/plan-approved/564.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#563](https://github.com/vamseeachanta/digitalmodel/issues/563) — fix(marine_ops): test_marine_eng_performance.py::test_ocimf_database_performance — needs investigation | `docs/plans/2026-05-05-issue-563-marine-eng-perf-ocimf-database.md` | `.planning/plan-approved/563.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#562](https://github.com/vamseeachanta/digitalmodel/issues/562) — fix(marine_ops): test_marine_eng_performance.py::test_complete_workflow_performance — numpy.bool_ not JSON serializable | `docs/plans/2026-05-05-issue-562-marine-eng-perf-numpy-bool-json.md` | `.planning/plan-approved/562.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#561](https://github.com/vamseeachanta/digitalmodel/issues/561) — fix(marine_ops): test_ocimf_mooring_integration.py::test_combined_environmental_forces — wrong test premise (current dominates) | `docs/plans/2026-05-05-issue-561-ocimf-mooring-combined-environmental.md` | `.planning/plan-approved/561.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#560](https://github.com/vamseeachanta/digitalmodel/issues/560) — fix(marine_ops): test_hydro_rao_integration.py::test_coupling_terms_affect_response — needs investigation | `docs/plans/2026-05-05-issue-560-rao-coupling-terms-affect-response.md` | `.planning/plan-approved/560.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#559](https://github.com/vamseeachanta/digitalmodel/issues/559) — fix(marine_ops): test_hydro_rao_integration.py::test_full_matrix_interpolation — strict-greater on equal floats (use >=) | `docs/plans/2026-05-05-issue-559-rao-full-matrix-interpolation.md` | `.planning/plan-approved/559.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#558](https://github.com/vamseeachanta/digitalmodel/issues/558) — fix(marine_ops): test_hydro_rao_integration.py::test_damping_affects_phase — phase 138° not near -90° (sign convention) | `docs/plans/2026-05-05-issue-558-rao-damping-affects-phase.md` | `.planning/plan-approved/558.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#557](https://github.com/vamseeachanta/digitalmodel/issues/557) — fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_boundary_warnings — DID NOT WARN on out-of-range query | `docs/plans/2026-05-05-issue-557-ocimf-boundary-warnings.md` | `.planning/plan-approved/557.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#556](https://github.com/vamseeachanta/digitalmodel/issues/556) — fix(marine_ops): test_ocimf.py::TestOCIMFDatabase::test_get_coefficients_interpolation — CYw=-3.56 not in [0,1.5] | `docs/plans/2026-05-05-issue-556-ocimf-coefficients-interpolation.md` | `.planning/plan-approved/556.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#554](https://github.com/vamseeachanta/digitalmodel/issues/554) — fix(marine_ops): catenary solver bracketing + sinh overflow — clears 21 of 77 marine_ops failures | `docs/plans/2026-05-05-issue-554-catenary-solver-bracketing-sinh-overflow.md` | `.planning/plan-approved/554.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#537](https://github.com/vamseeachanta/digitalmodel/issues/537) — OrcaFlex: manifest.yml not written when all runs skipped — clarify docstring + behavior | `docs/plans/2026-05-05-issue-537-manifest-empty-runs.md` | `.planning/plan-approved/537.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#536](https://github.com/vamseeachanta/digitalmodel/issues/536) — OrcaFlex: per-iteration model_validate perf for large sweep matrices | `docs/plans/2026-05-05-issue-536-per-iteration-validate-perf.md` | `.planning/plan-approved/536.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#535](https://github.com/vamseeachanta/digitalmodel/issues/535) — OrcaFlex: apply_dotted_override should chain ValidationError with dotted-path context | `docs/plans/2026-05-05-issue-535-apply-dotted-override-error-chain.md` | `.planning/plan-approved/535.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#534](https://github.com/vamseeachanta/digitalmodel/issues/534) — OrcaFlex: _apply_overrides direct-call StopIteration guard | `docs/plans/2026-05-05-issue-534-apply-overrides-stopiteration-guard.md` | `.planning/plan-approved/534.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#531](https://github.com/vamseeachanta/digitalmodel/issues/531) — OrcaFlex: follow-up — 9 pre-existing test failures across 5 files not covered by #510 plan scope | `docs/plans/2026-05-05-issue-531-9-pre-existing-test-failures.md` | `.planning/plan-approved/531.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#530](https://github.com/vamseeachanta/digitalmodel/issues/530) — OrcaFlex tests: hoist class-scoped fixtures in test_orcaflex_converter_enhanced.py to module level | `docs/plans/2026-05-05-issue-530-hoist-class-fixtures.md` | `.planning/plan-approved/530.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#529](https://github.com/vamseeachanta/digitalmodel/issues/529) — OrcaFlex: convert_batch() parallel path doesn't aggregate success counts into self.stats | `docs/plans/2026-05-05-issue-529-convert-batch-parallel-stats.md` | `.planning/plan-approved/529.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#523](https://github.com/vamseeachanta/digitalmodel/issues/523) — Harvest #517 subprocess review into actionable implementation tasks for #515 program | `docs/plans/2026-05-05-issue-523-harvest-517-subprocess-review.md` | `.planning/plan-approved/523.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| digitalmodel | [digitalmodel#522](https://github.com/vamseeachanta/digitalmodel/issues/522) — Codify ultra-constrained Claude subprocess prompt patterns for issue-scope reviews | `docs/plans/2026-05-05-issue-522-claude-subprocess-prompt-patterns.md` | `.planning/plan-approved/522.md` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |
| … | 99 additional rows omitted from this report; full JSON: `/tmp/tier1_approval_state_audit.json` | | | |

## Already-working approved issues

Do not launch duplicate workers for these. First run post-approval implementation-state audit: issue comments, PRs, branches, planned files on main, and CI state.

### Approved + status:working issues

| Repo | Issue | Plan evidence | Approval marker | Labels | Worktree |
| --- | --- | --- | --- | --- | --- |
| workspace-hub | [workspace-hub#2403](https://github.com/vamseeachanta/workspace-hub/issues/2403) — feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large | `docs/plans/2026-04-20-issue-2403-embeddings-model-selection-spike.md` | `.planning/plan-approved/2403.md` | `enhancement`, `priority:medium`, `cat:data-pipeline`, `cat:research`, `domain:document-intelligence`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2402](https://github.com/vamseeachanta/workspace-hub/issues/2402) — feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | `docs/plans/2026-04-20-issue-2402-embeddings-build-index.md` | `.planning/plan-approved/2402.md` | `enhancement`, `priority:high`, `cat:data-pipeline`, `domain:document-intelligence`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2327](https://github.com/vamseeachanta/workspace-hub/issues/2327) — digitalmodel: CadQuery spike for parametric offshore geometry generation | — | — | `priority:low`, `cat:engineering`, `cat:research`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2269](https://github.com/vamseeachanta/workspace-hub/issues/2269) — feat(openfoam): standardize ESI v2312 baseline workflow and validation | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` | `.planning/plan-approved/2269.md` | `enhancement`, `priority:high`, `cat:engineering`, `cat:documentation`, `status:working`, `machine:dev-secondary`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2229](https://github.com/vamseeachanta/workspace-hub/issues/2229) — feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live | `docs/plans/2026-04-13-issue-2229-licensed-win-1-live-validation.md` | `.planning/plan-approved/2229.md` | `enhancement`, `priority:medium`, `cat:harness`, `status:working`, `machine:licensed-win-1`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2129](https://github.com/vamseeachanta/workspace-hub/issues/2129) — chore(harness): automate issue-state drift and redundancy audit across GitHub + analysis artifacts | `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md` | `.planning/plan-approved/2129.md` | `enhancement`, `priority:medium`, `cat:ai-orchestration`, `cat:harness`, `status:working`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2124](https://github.com/vamseeachanta/workspace-hub/issues/2124) — feat(llm-wiki): extend ingestion to Orcina resources, examples, and training materials | `docs/plans/2026-04-24-issue-2124-orcina-resources-examples-training.md` | — | `enhancement`, `priority:medium`, `cat:data-pipeline`, `domain:marine`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2125](https://github.com/vamseeachanta/workspace-hub/issues/2125) — feat(llm-wiki): auto-refresh ingestion on new Orcina releases | `docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md` | — | `enhancement`, `priority:medium`, `cat:data-pipeline`, `domain:marine`, `domain:knowledge-management`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2055](https://github.com/vamseeachanta/workspace-hub/issues/2055) — feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts | — | `.planning/plan-approved/2055.md` | `enhancement`, `priority:high`, `cat:engineering`, `status:working`, `wip:ace-linux-1`, `dark-intelligence`, `agent:claude`, `agent:codex`, `status:plan-approved`, `status:needs-data`, `scope:v1` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#2046](https://github.com/vamseeachanta/workspace-hub/issues/2046) — Audit compliance of strict issue planning workflow after rollout | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | — | `priority:medium`, `cat:ai-orchestration`, `cat:operations`, `status:working`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1962](https://github.com/vamseeachanta/workspace-hub/issues/1962) — FEATURE: Tier-1 Repo Ecosystem Refactoring — audit, plan, execute with Claude Code plan mode | — | `.planning/plan-approved/1962.md` | `enhancement`, `priority:high`, `cat:engineering`, `cat:harness`, `status:working`, `agent:gemini`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1782](https://github.com/vamseeachanta/workspace-hub/issues/1782) — epic: zero-loss agent learnings — git-track ALL AI agent memories, corrections, patterns, and insights | — | — | `enhancement`, `priority:high`, `cat:ai-orchestration`, `cat:harness`, `status:working`, `machine:multi`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1583](https://github.com/vamseeachanta/workspace-hub/issues/1583) — Hermes config parity via repo ecosystem templates | — | — | `enhancement`, `priority:medium`, `cat:ai-orchestration`, `cat:harness`, `status:working`, `machine:multi`, `agent:claude`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| workspace-hub | [workspace-hub#1264](https://github.com/vamseeachanta/workspace-hub/issues/1264) — WRK-1365: OrcaFlex frame analysis | — | — | `enhancement`, `priority:high`, `cat:engineering-calculations`, `wrk-item`, `status:working`, `machine:licensed-win-1`, `agent:codex`, `status:plan-approved` | `chore/llm-wiki-spinout-cleanup` / `dirty:20` |
| digitalmodel | [digitalmodel#504](https://github.com/vamseeachanta/digitalmodel/issues/504) — OrcaFlex buoys builder refactor: split 611-line mega-builder into focused builders | `docs/plans/2026-05-05-issue-504-buoys-builder-refactor.md` | `.planning/plan-approved/504.md` | `enhancement`, `status:working`, `status:plan-approved` | `fix/issue-555-chain-database-diameters-slice` / `dirty:80` |

## Repo worktree risk

| Repo | Branch | Dirty entries | Risk |
| --- | --- | ---: | --- |
| `workspace-hub` | `chore/llm-wiki-spinout-cleanup` | 20 | dirty local clone; execution must use a fresh isolated worktree or first preserve/triage dirt |
| `digitalmodel` | `fix/issue-555-chain-database-diameters-slice` | 80 | dirty local clone; execution must use a fresh isolated worktree or first preserve/triage dirt |
| `assetutilities` | `main` | 2 | dirty local clone; execution must use a fresh isolated worktree or first preserve/triage dirt |
| `worldenergydata` | `main` | 0 | clean for inspection; still create isolated branch/worktree for execution |
| `assethold` | `main` | 28 | dirty local clone; execution must use a fresh isolated worktree or first preserve/triage dirt |
| `aceengineer-website` | `main` | 0 | clean for inspection; still create isolated branch/worktree for execution |

## Multiagent orchestration recommendations

1. **Do not launch from label-only approval.** Require `status:plan-approved` + `docs/plans/...` + `.planning/plan-approved/<issue>.md` + no `status:working` + assigned clean worktree.
2. **Start with low-drift repos.** `assetutilities` and `assethold` have complete plan+marker evidence for all approved issues, but both local clones are dirty; use fresh worktrees. `digitalmodel` has a large mostly-evidenced pool but is dirty and on an issue branch, so isolate carefully.
3. **Treat `worldenergydata` as governance repair first.** It has many canonical plans but almost no approval markers; create a marker backfill/audit issue or perform marker reconciliation before broad execution.
4. **Treat old `workspace-hub` approved+working issues as implementation-state audits, not new execution starts.** Several are already `status:working` and/or missing marker evidence.
5. **WIP cap:** at most 4 execution lanes after this audit: 2 implementation, 1 verification, 1 governance-repair/planning lane.

## Recommended next gates

| Gate | Action | Owner | Exit evidence |
| --- | --- | --- | --- |
| G1 | Pick 3–5 fully evidenced, non-working candidates from `assetutilities`, `assethold`, or `digitalmodel`. | Orchestrator | Candidate shortlist with issue URLs and plan/marker paths. |
| G2 | For each selected issue, create/verify fresh isolated worktree and branch ownership. | Orchestrator | `git worktree list`, branch name, clean `git status --short`. |
| G3 | For `worldenergydata`, reconcile missing approval markers before execution. | Governance lane | Marker files or label rollback/evidence comments. |
| G4 | For `status:working` items, audit PR/branch/main/CI state before assigning workers. | Verification lane | Implementation-state audit notes per issue. |

## Source evidence

- Live issue JSON snapshots: `/tmp/*_plan_approved_live.json`.
- Consolidated audit JSON: `/tmp/tier1_approval_state_audit.json`.
- Commands used: `gh issue list --repo vamseeachanta/<repo> --state open --label status:plan-approved --limit 1000 --json number,title,url,labels,updatedAt`; local `git status --short`; filesystem checks under `docs/plans/` and `.planning/plan-approved/`.
