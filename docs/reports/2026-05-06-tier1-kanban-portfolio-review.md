# Tier-1 Repo Kanban Portfolio Review — 2026-05-06

> Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`, `aceengineer-website`. Data pulled live with `gh issue list` on 2026-05-06; local repo state checked with `git status --short`. This is a repo-tracked review board, not an implementation authorization.

## Executive summary

- The tier-1 issue surface is dominated by **workspace-hub (815 open)** and **digitalmodel (262 open)**; the remaining four active tier-1 repos add 114 open issues.
- The immediate execution-ready backlog is large: **216 open issues carry `status:plan-approved`**, but several repos have substantial dirty/untracked local state, so batch execution should start with worktree/branch hygiene and issue-state reconciliation.
- Planning gaps remain material: **967 open issues have no `status:plan-*` label**, primarily workspace-hub and digitalmodel. These need triage/decomposition before execution under the hard gate.
- Agent routing is only partially applied: workspace-hub has `agent:*` labels, but digitalmodel / assetutilities / worldenergydata / assethold / aceengineer-website currently show no agent labels on the scoped open issue sets.
- Post-snapshot update: the two conflicting `status:plan-review` + `status:plan-approved` labels identified in the initial board (`assetutilities#72`, `assethold#7`) were audited and reconciled on 2026-05-06; both now retain `status:plan-approved` only.
- 2026-05-08 live approval-state audit completed: see [`2026-05-08-tier1-approval-state-audit.md`](2026-05-08-tier1-approval-state-audit.md). The repo-structure execution wave should start with `assetutilities#78`; `digitalmodel#596` remains plan-review, and `workspace-hub#2656`, `worldenergydata#394`, `assethold#49`, `aceengineer-website#13`, and `aceengineer-strategy#19` need approval-marker/plan reconciliation before implementation workers launch.

## Repo-level board metrics

| Repo | Branch | Dirty paths | Open | Recent closed sample | Plan review | Plan approved | Conflicting plan labels | Planning needed | Agent labels present |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `workspace-hub` | `chore/llm-wiki-spinout-cleanup` | 6 | 815 | 30 | 7 | 22 | 0 | 786 | C:66 / X:81 / G:4 / Any:0 |
| `digitalmodel` | `main` | 80 | 262 | 30 | 0 | 86 | 0 | 176 | C:0 / X:0 / G:0 / Any:0 |
| `assetutilities` | `main` | 71 | 21 | 30 | 0 | 21 | 0 | 0 | C:0 / X:0 / G:0 / Any:0 |
| `worldenergydata` | `docs/handoff-2026-05-03-lt-epic-closed` | 67 | 61 | 30 | 1 | 60 | 0 | 0 | C:0 / X:0 / G:0 / Any:0 |
| `assethold` | `main` | 28 | 27 | 15 | 0 | 27 | 0 | 0 | C:0 / X:0 / G:0 / Any:0 |
| `aceengineer-website` | `main` | 0 | 5 | 2 | 0 | 0 | 0 | 5 | C:0 / X:0 / G:0 / Any:0 |

## Kanban columns

### Done / recently closed review sample

Use this column to audit whether recently closed work was transactionally completed: pushed, branch/worktree disposed, issue close evidence present, and no stale artifacts left behind.

| Repo | Issue | Title | Labels | Closed/updated |
|---|---:|---|---|---:|
| `digitalmodel` | [#552](https://github.com/vamseeachanta/digitalmodel/issues/552) | fix(aqwa-backend): align CRLF/LF line endings between generate_single and generate_modular | enhancement, priority:low, status:plan-approved | 2026-05-06 |
| `workspace-hub` | [#2642](https://github.com/vamseeachanta/workspace-hub/issues/2642) | feat(naval-arch): B1528 SIROCCO moored-current rudder force component report | enhancement, priority:high, cat:engineering-calculations, domain:hydrodynamics, domain:visualization | 2026-05-05 |
| `worldenergydata` | [#384](https://github.com/vamseeachanta/worldenergydata/issues/384) | fix(bsee): lazy-load module-level singletons in bsee_data.py — unblocks import and GTM demos | bug, priority:high, cat:engineering | 2026-05-05 |
| `workspace-hub` | [#2627](https://github.com/vamseeachanta/workspace-hub/issues/2627) | wiki(engineering-standards): create DNV-RP-F103 page (unblocks #2609 R3 fix) | cat:engineering, status:plan-approved, llm-wiki, tracker, domain:digitalmodel | 2026-05-04 |
| `digitalmodel` | [#571](https://github.com/vamseeachanta/digitalmodel/issues/571) | fix(tests/orcaflex): test_cli_commands_from_module assertion drift — separate from S1 PATH cluster | bug, domain:naval-architecture, status:plan-approved | 2026-05-04 |
| `digitalmodel` | [#570](https://github.com/vamseeachanta/digitalmodel/issues/570) | fix(tests/orcaflex): replace bare CLI invocations with sys.executable -m — clears ~22 of 42 solvers/orcaflex failures | bug, cat:engineering, domain:naval-architecture, status:plan-approved | 2026-05-04 |
| `worldenergydata` | [#377](https://github.com/vamseeachanta/worldenergydata/issues/377) | feat(lt): comprehensive report assembly — HTML + PDF + executive summary + citations (Phase 4 of #373) | documentation, enhancement, priority:high, cat:engineering, status:plan-approved | 2026-05-03 |
| `worldenergydata` | [#376](https://github.com/vamseeachanta/worldenergydata/issues/376) | feat(lt): cross-field analytics — technology, operator, HSE, cost benchmarking (Phase 3 of #373) | enhancement, cat:engineering, priority:medium, cat:data, status:plan-approved | 2026-05-03 |
| `workspace-hub` | [#2622](https://github.com/vamseeachanta/workspace-hub/issues/2622) | fix(digitalmodel-tests): Cluster C — drop -p no:capture from QG command or refactor capsys tests (~17 errors) | priority:medium, cat:engineering, domain:testing, status:done | 2026-05-03 |
| `workspace-hub` | [#2621](https://github.com/vamseeachanta/workspace-hub/issues/2621) | fix(digitalmodel-tests): Cluster B — extend _HAS_WED_DCF skipif to 4 sibling test classes (14 failures) | priority:medium, cat:engineering, domain:testing, status:done | 2026-05-03 |
| `worldenergydata` | [#375](https://github.com/vamseeachanta/worldenergydata/issues/375) | feat(lt): per-field economic analysis for all 10 fields — NPV/IRR/payback + sensitivities (Phase 2 of #373) | enhancement, priority:high, cat:engineering, status:plan-approved | 2026-05-03 |
| `workspace-hub` | [#2618](https://github.com/vamseeachanta/workspace-hub/issues/2618) | fix(hooks): pre-push config-drift check fails with ModuleNotFoundError: yaml under uv ephemeral env | priority:medium, status:plan-approved | 2026-05-03 |
| `worldenergydata` | [#374](https://github.com/vamseeachanta/worldenergydata/issues/374) | feat(lt): backfill field configs for Big Foot + North Platte (Phase 1 of #373) | enhancement, priority:high, cat:data, status:plan-approved | 2026-05-03 |
| `digitalmodel` | [#546](https://github.com/vamseeachanta/digitalmodel/issues/546) | ci: Quality Gates artifact truncates pytest log to 8.6 KB JSON tail — upload full log instead | cat:ci, status:plan-approved | 2026-05-03 |
| `assethold` | [#48](https://github.com/vamseeachanta/assethold/issues/48) | fix(ci): resolve coverage and Python 3.9 market-hours failures blocking PR #47 | bug, priority:high | 2026-04-29 |
| `assethold` | [#38](https://github.com/vamseeachanta/assethold/issues/38) | Phase 1 follow-ups — code polish and test hygiene | enhancement, cat:engineering, priority:low, status:done, status:plan-approved | 2026-04-17 |
| `assethold` | [#39](https://github.com/vamseeachanta/assethold/issues/39) | Extend market_hours_aware to signals consumers (alert_engine, trend_detector, dashboard) | enhancement, priority:medium, cat:engineering, status:done, status:plan-approved | 2026-04-17 |
| `assethold` | [#35](https://github.com/vamseeachanta/assethold/issues/35) | Realtime feeds Phase 1 — market-hours awareness + intraday TTL | enhancement, priority:medium, cat:engineering | 2026-04-17 |
| `assethold` | [#30](https://github.com/vamseeachanta/assethold/issues/30) | Remove legacy code and consolidate duplicate module hierarchy | enhancement, priority:high, status:plan-approval | 2026-04-16 |
| `digitalmodel` | [#525](https://github.com/vamseeachanta/digitalmodel/issues/525) | Remove silent defaults in OrcaWaveInputParser for semantic-equivalence hardening | enhancement, project, priority:high, cat:engineering-models, cat:development | 2026-04-15 |
| `assetutilities` | [#74](https://github.com/vamseeachanta/assetutilities/issues/74) | Missing pytest-asyncio in test dependencies causes 23 async test failures |  | 2026-04-11 |
| `assetutilities` | [#73](https://github.com/vamseeachanta/assetutilities/issues/73) | Fix and document the supported uv/pytest workflow after pytest dependency cleanup |  | 2026-04-11 |
| `aceengineer-website` | [#2](https://github.com/vamseeachanta/aceengineer-website/issues/2) | Add SEO principles to the website | wrk-item | 2025-07-24 |
| `aceengineer-website` | [#1](https://github.com/vamseeachanta/aceengineer-website/issues/1) | Convert to static website in Github | wrk-item | 2025-07-24 |
| `assetutilities` | [#57](https://github.com/vamseeachanta/assetutilities/issues/57) | tech debt \| Add Plotly capability into Visualization Module |  | 2025-06-12 |

### In review / needs approval decision (`status:plan-review`)

These are planning-board items. They are not executable until explicit user approval and clean `status:plan-approved` state.

| Repo | Issue | Title | Labels | Updated |
|---|---:|---|---|---:|
| `workspace-hub` | [#2643](https://github.com/vamseeachanta/workspace-hub/issues/2643) | feat(llm-wiki): plan metadata-only /mnt/ace-data raw-like source coverage triage | priority:high, cat:data-pipeline, cat:documentation, domain:document-intelligence, domain:knowledge-management | 2026-05-05 |
| `workspace-hub` | [#2510](https://github.com/vamseeachanta/workspace-hub/issues/2510) | feat(cad): build Python layout/CAD automation demo for chip/package geometries | priority:medium, cat:engineering, cat:tooling, status:plan-review, domain:semiconductor | 2026-05-04 |
| `workspace-hub` | [#2551](https://github.com/vamseeachanta/workspace-hub/issues/2551) | audit(security): verify branch/ruleset protections across public repos after collaborator-only lockdown | enhancement, priority:medium, cat:operations, domain:security, domain:repo-health | 2026-05-06 |
| `worldenergydata` | [#387](https://github.com/vamseeachanta/worldenergydata/issues/387) | WRK-688: eval(worldenergydata): evaluate pyWAsP for wind resource assessment integration | enhancement, cat:engineering, priority:medium, wrk-item, status:plan-review | 2026-05-06 |
| `workspace-hub` | [#2653](https://github.com/vamseeachanta/workspace-hub/issues/2653) | WRK-694: Per-session log files in session-logger.sh | enhancement, priority:medium, cat:engineering, wrk-item, status:plan-review | 2026-05-06 |
| `workspace-hub` | [#2626](https://github.com/vamseeachanta/workspace-hub/issues/2626) | fix(security): narrow #2552 external-contributor runbook tests + scenario 3 — drop privacy-leaking test, define ingestion vector, resolve interaction-limit contradiction | priority:medium, cat:documentation, domain:security, status:plan-review | 2026-05-04 |
| `workspace-hub` | [#2632](https://github.com/vamseeachanta/workspace-hub/issues/2632) | META: rebind 3 llm-wiki plan-approved issues stuck on missing approval markers (#2368/#2124/#2125) | priority:medium, cat:knowledge-domain, domain:knowledge-management, status:plan-review | 2026-05-05 |
| `workspace-hub` | [#2528](https://github.com/vamseeachanta/workspace-hub/issues/2528) | chore(skills): retire 6 deprecated email skills + update gmail-triage to queue model | enhancement, priority:medium, cat:infrastructure, domain:skill-curation, maintenance | 2026-05-06 |

### Ready / pending execution (`status:plan-approved`)

This is the largest near-term execution pool. Before launching agents, revalidate each issue's plan artifact, approval marker, local dirty state, and file ownership boundaries.

| Repo | Issue | Title | Labels | Updated |
|---|---:|---|---|---:|
| `worldenergydata` | [#334](https://github.com/vamseeachanta/worldenergydata/issues/334) | feat(cost): annual operator disclosures dataset for year-over-year project cost tracking | enhancement, priority:high, cat:engineering, cat:data, status:plan-approved | 2026-04-22 |
| `digitalmodel` | [#515](https://github.com/vamseeachanta/digitalmodel/issues/515) | Clarify and close semantic-equivalence gaps between spec/LLM-friendly YAML and OrcaFlex strict YAML | enhancement, cat:engineering, priority:high, route:B, status:plan-approved | 2026-04-24 |
| `digitalmodel` | [#282](https://github.com/vamseeachanta/digitalmodel/issues/282) | WRK-130: Standardize analysis reporting for each OrcaWave structure type | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-04-24 |
| `digitalmodel` | [#279](https://github.com/vamseeachanta/digitalmodel/issues/279) | WRK-129: Standardize analysis reporting for each OrcaFlex structure type | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-04-24 |
| `workspace-hub` | [#1782](https://github.com/vamseeachanta/workspace-hub/issues/1782) | epic: zero-loss agent learnings — git-track ALL AI agent memories, corrections, patterns, and insights | enhancement, priority:high, cat:ai-orchestration, cat:harness, status:working | 2026-04-28 |
| `workspace-hub` | [#2269](https://github.com/vamseeachanta/workspace-hub/issues/2269) | feat(openfoam): standardize ESI v2312 baseline workflow and validation | enhancement, priority:high, cat:engineering, cat:documentation, status:working | 2026-04-28 |
| `workspace-hub` | [#2402](https://github.com/vamseeachanta/workspace-hub/issues/2402) | feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working | 2026-04-28 |
| `workspace-hub` | [#2055](https://github.com/vamseeachanta/workspace-hub/issues/2055) | feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts | enhancement, priority:high, cat:engineering, status:working, wip:ace-linux-1 | 2026-04-29 |
| `workspace-hub` | [#2112](https://github.com/vamseeachanta/workspace-hub/issues/2112) | data(field-dev): backfill SubseaIQ equipment counts to unblock cost benchmarking | enhancement, priority:high, cat:engineering, agent:claude, status:plan-approved | 2026-05-01 |
| `workspace-hub` | [#2563](https://github.com/vamseeachanta/workspace-hub/issues/2563) | Set up Telegram mobile access for Hermes AI control | enhancement, priority:high, cat:ai-orchestration, cat:operations, domain:integrations | 2026-05-03 |
| `workspace-hub` | [#2523](https://github.com/vamseeachanta/workspace-hub/issues/2523) | feat(workstations): add reusable Hermes preflight readiness checker | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:ai-orchestration | 2026-05-03 |
| `workspace-hub` | [#2628](https://github.com/vamseeachanta/workspace-hub/issues/2628) | epic(digitalmodel-ci): domain-divided CI architecture replacing maxfail-masking pattern | enhancement, priority:high, cat:engineering, cat:harness, domain:testing | 2026-05-04 |
| `worldenergydata` | [#124](https://github.com/vamseeachanta/worldenergydata/issues/124) | WRK-1189: Ingest BOEM lease data | enhancement, priority:high, cat:engineering, wrk-item, status:plan-approved | 2026-05-05 |
| `worldenergydata` | [#128](https://github.com/vamseeachanta/worldenergydata/issues/128) | WRK-1231: Implement CompanyLoader for BOEM company/operator hierarchy | enhancement, priority:high, cat:engineering, wrk-item, status:plan-approved | 2026-05-05 |
| `worldenergydata` | [#361](https://github.com/vamseeachanta/worldenergydata/issues/361) | feat(provenance): adopt calc-citation-contract for worldenergydata calc outputs | enhancement, priority:high, cat:engineering, cat:data, status:plan-approved | 2026-05-05 |
| `worldenergydata` | [#350](https://github.com/vamseeachanta/worldenergydata/issues/350) | audit(data): build data completeness and freshness scorecard | enhancement, priority:high, cat:engineering, cat:data, status:plan-approved | 2026-05-05 |
| `worldenergydata` | [#343](https://github.com/vamseeachanta/worldenergydata/issues/343) | feat(cost): build major-operator annual statement source registry and yearly coverage tracker | enhancement, priority:high, cat:engineering, cat:data, status:plan-approved | 2026-05-05 |
| `worldenergydata` | [#349](https://github.com/vamseeachanta/worldenergydata/issues/349) | audit(repo): build capability inventory and module readiness matrix | documentation, priority:high, cat:engineering, cat:data, status:plan-approved | 2026-05-05 |
| `worldenergydata` | [#362](https://github.com/vamseeachanta/worldenergydata/issues/362) | feat(report): operator cost benchmarking from annual disclosures (HTML + notebook) | enhancement, priority:high, cat:engineering, cat:data, status:plan-approved | 2026-05-05 |
| `digitalmodel` | [#554](https://github.com/vamseeachanta/digitalmodel/issues/554) | fix(marine_ops): catenary solver bracketing + sinh overflow — clears 21 of 77 marine_ops failures | bug, cat:engineering, priority:high, domain:naval-architecture, status:plan-approved | 2026-05-06 |
| `digitalmodel` | [#519](https://github.com/vamseeachanta/digitalmodel/issues/519) | Classify and fix General/Environment/Groups fidelity gaps in OrcaFlex generation | enhancement, cat:engineering, priority:high, status:pending, route:B | 2026-05-06 |
| `digitalmodel` | [#518](https://github.com/vamseeachanta/digitalmodel/issues/518) | Add model-library regression tests for strict-vs-generated OrcaFlex semantic diffs | enhancement, cat:engineering, priority:high, status:pending, route:B | 2026-05-06 |
| `digitalmodel` | [#580](https://github.com/vamseeachanta/digitalmodel/issues/580) | WRK-5066: Production engineering study — literature, methods and implementation | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-05-06 |
| `digitalmodel` | [#574](https://github.com/vamseeachanta/digitalmodel/issues/574) | Wiki standards-page family for FOWT (IEC 61400-3-2, DNV-ST-0119, DNV-RP-0286, DNV-ST-0126, DNV-ST-0358, DNV-RP-0360, API RP 2SIM) | enhancement, cat:engineering, priority:high, status:plan-approved | 2026-05-06 |
| `workspace-hub` | [#1962](https://github.com/vamseeachanta/workspace-hub/issues/1962) | FEATURE: Tier-1 Repo Ecosystem Refactoring — audit, plan, execute with Claude Code plan mode | enhancement, priority:high, cat:engineering, cat:harness, status:working | 2026-05-06 |
| `digitalmodel` | [#483](https://github.com/vamseeachanta/digitalmodel/issues/483) | sub: curves.py decomposition -- break up 29,666-line monolith | cat:engineering, priority:high, status:plan-approved | 2026-05-06 |
| `digitalmodel` | [#269](https://github.com/vamseeachanta/digitalmodel/issues/269) | WRK-629: feat(client2): engineering AI demo — diffraction + plate FFS + GoA + maritime legal system prompts + knowledge base | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-05-06 |
| `digitalmodel` | [#270](https://github.com/vamseeachanta/digitalmodel/issues/270) | WRK-630: feat(client2): engineering AI demo — diffraction + plate FFS + GoA + maritime legal workflows + demo package | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-05-06 |
| `digitalmodel` | [#283](https://github.com/vamseeachanta/digitalmodel/issues/283) | WRK-131: Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-05-06 |
| `digitalmodel` | [#284](https://github.com/vamseeachanta/digitalmodel/issues/284) | WRK-133: Update OrcaFlex license agreement with addresses and 3rd-party terms | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-05-06 |
| `digitalmodel` | [#281](https://github.com/vamseeachanta/digitalmodel/issues/281) | WRK-121: Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | enhancement, cat:engineering, priority:high, wrk-item, status:plan-approved | 2026-05-06 |
| `worldenergydata` | [#353](https://github.com/vamseeachanta/worldenergydata/issues/353) | fix(scheduler): diagnose uv/scheduler no-op command timeouts | bug, ci, priority:high, cat:data, cat:automation | 2026-04-27 |
| `workspace-hub` | [#1264](https://github.com/vamseeachanta/workspace-hub/issues/1264) | WRK-1365: OrcaFlex frame analysis | enhancement, priority:high, cat:engineering-calculations, wrk-item, status:working | 2026-04-28 |
| `workspace-hub` | [#2533](https://github.com/vamseeachanta/workspace-hub/issues/2533) | feat(repo-portfolio): review and revise mission/objective statements across active repos | enhancement, priority:high, cat:documentation, domain:repo-organization, status:plan-approved | 2026-05-03 |
| `worldenergydata` | [#266](https://github.com/vamseeachanta/worldenergydata/issues/266) | Operationalize EIA scheduler job — config, API key, first successful data write | enhancement, priority:high, cat:data, status:plan-approved | 2026-05-05 |

### Needs planning / triage before execution

These lack a `status:plan-*` label in the live issue list. They should enter the GitHub planning route before implementation.

| Repo | Issue | Title | Labels | Updated |
|---|---:|---|---|---:|
| `workspace-hub` | [#2517](https://github.com/vamseeachanta/workspace-hub/issues/2517) | Compliance alert: W18 — 42% (high) | priority:high, priority:medium, priority:critical, compliance-alert | 2026-05-03 |
| `digitalmodel` | [#268](https://github.com/vamseeachanta/digitalmodel/issues/268) | WRK-628: feat(frontierdeepwater): client AI roadshow — phased engineering AI adoption programme | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#267](https://github.com/vamseeachanta/digitalmodel/issues/267) | WRK-625: feat(frontierdeepwater): engineering AI demo — system prompts + knowledge base (Day 1) | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#261](https://github.com/vamseeachanta/digitalmodel/issues/261) | WRK-618: feat(geotechnical): soil profile models, CPT correlation, shared types | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#256](https://github.com/vamseeachanta/digitalmodel/issues/256) | WRK-598: feat(product): build engineering chatbot for oil & gas clients | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#255](https://github.com/vamseeachanta/digitalmodel/issues/255) | WRK-595: feat(orcaflex): rewrite enrichment pipeline — worldenergydata-first, all stages on acma-ansys05 | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#254](https://github.com/vamseeachanta/digitalmodel/issues/254) | WRK-589: feat(orcaflex): dat-to-yaml pipeline — extract, legal-scan, import to digitalmodel | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#249](https://github.com/vamseeachanta/digitalmodel/issues/249) | WRK-559: feat(digitalmodel/marine): Implement API RP 2P — API RP 2P 2nd Ed (1987) Analysis of Spread Mooring | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#248](https://github.com/vamseeachanta/digitalmodel/issues/248) | WRK-555: feat(digitalmodel/marine): Implement DNV E301 — DNV OS E301 (2010) Position Mooring | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#247](https://github.com/vamseeachanta/digitalmodel/issues/247) | WRK-544: feat(OGManufacturing/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#246](https://github.com/vamseeachanta/digitalmodel/issues/246) | WRK-543: feat(digitalmodel/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#245](https://github.com/vamseeachanta/digitalmodel/issues/245) | WRK-538: feat(doris/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#244](https://github.com/vamseeachanta/digitalmodel/issues/244) | WRK-537: feat(digitalmodel/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#243](https://github.com/vamseeachanta/digitalmodel/issues/243) | WRK-536: feat(doris/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#242](https://github.com/vamseeachanta/digitalmodel/issues/242) | WRK-535: feat(digitalmodel/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#241](https://github.com/vamseeachanta/digitalmodel/issues/241) | WRK-534: feat(doris/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#240](https://github.com/vamseeachanta/digitalmodel/issues/240) | WRK-533: feat(digitalmodel/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#239](https://github.com/vamseeachanta/digitalmodel/issues/239) | WRK-532: feat(doris/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#238](https://github.com/vamseeachanta/digitalmodel/issues/238) | WRK-531: feat(digitalmodel/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#237](https://github.com/vamseeachanta/digitalmodel/issues/237) | WRK-530: feat(doris/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#236](https://github.com/vamseeachanta/digitalmodel/issues/236) | WRK-529: feat(digitalmodel/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#235](https://github.com/vamseeachanta/digitalmodel/issues/235) | WRK-528: feat(doris/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#234](https://github.com/vamseeachanta/digitalmodel/issues/234) | WRK-527: feat(digitalmodel/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#233](https://github.com/vamseeachanta/digitalmodel/issues/233) | WRK-526: feat(doris/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#232](https://github.com/vamseeachanta/digitalmodel/issues/232) | WRK-525: feat(digitalmodel/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#231](https://github.com/vamseeachanta/digitalmodel/issues/231) | WRK-524: feat(doris/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#230](https://github.com/vamseeachanta/digitalmodel/issues/230) | WRK-523: feat(digitalmodel/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#229](https://github.com/vamseeachanta/digitalmodel/issues/229) | WRK-522: feat(doris/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#228](https://github.com/vamseeachanta/digitalmodel/issues/228) | WRK-521: feat(digitalmodel/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#227](https://github.com/vamseeachanta/digitalmodel/issues/227) | WRK-520: feat(doris/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#226](https://github.com/vamseeachanta/digitalmodel/issues/226) | WRK-519: feat(digitalmodel/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#225](https://github.com/vamseeachanta/digitalmodel/issues/225) | WRK-518: feat(doris/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#224](https://github.com/vamseeachanta/digitalmodel/issues/224) | WRK-517: feat(digitalmodel/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#223](https://github.com/vamseeachanta/digitalmodel/issues/223) | WRK-516: feat(doris/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |
| `digitalmodel` | [#222](https://github.com/vamseeachanta/digitalmodel/issues/222) | WRK-515: feat(digitalmodel/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | enhancement, cat:engineering, priority:high, wrk-item | 2026-03-24 |

### State conflicts reconciled after initial snapshot

| Repo | Issue | Title | Resolution | Evidence comment |
|---|---:|---|---|---|
| `assetutilities` | [#72](https://github.com/vamseeachanta/assetutilities/issues/72) | Cleanup: resolve merge markers blocking editable install and downstream pytest | Removed stale `status:plan-review`; retained `status:plan-approved` after verifying `docs/plans/2026-05-05-issue-72-merge-markers-cleanup.md` and `.planning/plan-approved/72.md`. | [comment](https://github.com/vamseeachanta/assetutilities/issues/72#issuecomment-4393231306) |
| `assethold` | [#7](https://github.com/vamseeachanta/assethold/issues/7) | Portfolio value | Removed stale `status:plan-review`; retained `status:plan-approved` after verifying `docs/plans/2026-05-05-issue-7-portfolio-value.md` and `.planning/plan-approved/7.md`. | [comment](https://github.com/vamseeachanta/assethold/issues/7#issuecomment-4393231526) |

## Additional planning needed

1. **Portfolio triage pass:** workspace-hub and digitalmodel together contain 962 planning-needed issues. Create/prioritize a smaller execution spine rather than treating the backlog as one flat queue.
2. **Approval-state audit:** completed 2026-05-06 in `docs/reports/2026-05-06-tier1-approval-state-audit.md`. Result: 212 live approved issues, 129 fully evidenced and not already `status:working`, 25 missing canonical plan evidence, 73 missing approval markers, and 0 remaining plan-review/approved label conflicts.
3. **Agent-label backfill:** apply `agent:claude`, `agent:codex`, `agent:gemini`, or `agent:any` labels across non-workspace repos after heuristic/manual review.
4. **Dirty-state isolation:** several child repos have dirty/untracked state. Use isolated worktrees and preserve/attribute existing state before worker execution.
5. **Tier-1 readiness fixes:** latest freshness audit still reports workspace-hub and aceengineer-website as RED, digitalmodel and assetutilities as YELLOW. Route readiness fixes before broad implementation waves.

## Multiagent orchestration execution items

| Priority | Work item | Primary agent | Why | Suggested gate |
|---:|---|---|---|---|
| P0 | Create a live portfolio spine issue/board that groups tier-1 work into P0/P1/P2 lanes and links this report | Claude orchestrator | The open issue surface is too large for ad-hoc execution. | Planning-only issue; no implementation until approved. |
| P0 | Reconcile conflicting labels on assetutilities #72 and assethold #7 | Claude/Codex ops lane | **Completed 2026-05-06:** both issues audited, commented, and normalized to `status:plan-approved` only. | Evidence comments: assetutilities [#72](https://github.com/vamseeachanta/assetutilities/issues/72#issuecomment-4393231306), assethold [#7](https://github.com/vamseeachanta/assethold/issues/7#issuecomment-4393231526). |
| P0 | Audit `status:plan-approved` issues for missing plan files/approval markers in digitalmodel/worldenergydata/assethold/assetutilities | Codex verifier lane | **Completed 2026-05-06:** wrote `docs/reports/2026-05-06-tier1-approval-state-audit.md`; found 192 approved, 129 fully evidenced non-working candidates, 25 missing plan evidence, 73 missing markers, 0 label conflicts. | Use audit gates before worker launch; create drift-repair/follow-up issues before broad execution. |
| P1 | Backfill `agent:*` labels in digitalmodel/worldenergydata/assethold/assetutilities/aceengineer-website | Gemini classifier + Claude reviewer | Non-workspace repos currently have no agent routing labels in scoped query. | Dry-run classification artifact, then batch-label after review. |
| P1 | Execute bounded RED/YELLOW readiness fixes: website `docs/registry/module-routing.yaml`, digitalmodel broken README link, workspace-hub routing surfaces | Codex implementation lanes | Small, verifiable repo-readiness improvements unblock future agents. | Each fix needs issue/plan approval or an existing approved issue. |
| P1 | Build overnight prompt pack for 3 lanes: governance/approval audit, engineering fixes, data/GTM docs | Claude orchestrator | Creates zero-contention workstreams with explicit ownership. | Only from approved issues; one branch/worktree per lane. |
| P2 | Recent-closure transactional audit across sampled closed issues | Codex verifier + Claude synthesis | Closeout hygiene proof is required; closed work can hide stale branches/files. | Report discrepancies; reopen/create blocker issues if needed. |

## Recommended WIP caps

- Keep **4 active execution items max**: 2 implementation, 1 verification, 1 planning/governance.
- Do not let plan-review items enter execution queues.
- For parallel execution, prefer **one issue per worktree per agent**; orchestrator owns final integration, comments, labels, and closeout.

## Source evidence

- `docs/reports/tier-1-indexing-freshness-latest.md` reported workspace-hub RED, digitalmodel YELLOW, assetutilities YELLOW, aceengineer-website RED on 2026-05-06.
- `docs/vision/VISION.md` identifies active tier-1 mission repos: digitalmodel, assetutilities, worldenergydata, assethold, aceengineer-website, workspace-hub.
- Live GitHub issue data collected via `gh issue list --repo <owner/repo> --state open/closed --json ...`.
