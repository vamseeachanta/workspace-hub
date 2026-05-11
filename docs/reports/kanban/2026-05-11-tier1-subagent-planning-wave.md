# Tier-1 Kanban Subagent Planning Wave — 2026-05-11

## Purpose

Planning-only wave over the tier-1 Kanban boards generated from live GitHub issues. The wave translated independent board slices into execution-ready planning packets with:

- issue URLs;
- provider + machine route;
- user-decision checkpoints;
- repo hygiene gates for file structure, tests, and CI/CD;
- cross-review expectations;
- blockers and first safe actions.

## Dispatch Summary

- Subagent attempts: 28 total.
- Completed planning packets: 23 subagents.
- Timed out / unusable: 5 subagents.
- No GitHub issues were mutated.
- No implementation work was performed.
- Default machine route: `ace-linux-1`.
- Overflow route: `ace-linux-2` only after readiness/auth/tool checks.

> Note: the user requested as many subagents as possible up to 25. Five initial dispatches timed out; replacement dispatches were launched to recover planning coverage. This resulted in 28 attempts total. No further dispatches were made after this was identified.

## Standard Operating Contract Applied

| Area | Planning rule |
|---|---|
| Machine routing | `ace-linux-1` is the control surface. `ace-linux-2` is overflow only after repo/tool/auth readiness checks. |
| Provider routing | Claude plans/reviews; Codex handles bounded implementation/tests after approval; Gemini performs research/adversarial review for high-risk domain, market, retrieval, or governance questions. |
| User decisions | Decision points are explicitly called out before implementation starts. |
| Repo hygiene | Every implementation packet requires file-structure, tests, CI/CD, docs, and artifact-location checks. |
| Cross-review | Plans/artifacts are cross-reviewed before closeout; higher-risk engineering/finance/GTM/retrieval items use Gemini adversarial review. |
| Implementation gate | Planning-only. No issue should move to implementation until its decision checkpoints are resolved and plan-approved state is verified. |

## Completed Planning Slices

### workspace-hub

1. **Orchestration / Kanban governance slice**
   - Focus: orchestration, governance, and planning-lifecycle issues from the workspace-hub Kanban board.
   - Output pattern: issue-level plan packets with user-decision gates, provider/machine route, hygiene gates, and review route.

2. **Operations / harness / AI orchestration hygiene slice**
   - Focus: harness, provider operations, quota/session, and automation hygiene.
   - Output pattern: hard-stop, state-machine, portability, and validation-first plans.

3. **Engineering / data-pipeline / standards slice**
   - Focus: engineering-critical and data-pipeline governance issues.
   - Output pattern: TDD-first, evidence-backed, cross-reviewed implementation plans.

4. **Document intelligence / documentation / GTM slice**
   - Issues:
     - [#2402 embeddings index L2+L3 query CLI](https://github.com/vamseeachanta/workspace-hub/issues/2402)
     - [#2643 metadata-only raw-like source coverage triage](https://github.com/vamseeachanta/workspace-hub/issues/2643)
     - [#2657 Hermes llm-wiki spinout path drift](https://github.com/vamseeachanta/workspace-hub/issues/2657)
     - [#2640 worldenergydata production decline forecast GTM notebook](https://github.com/vamseeachanta/workspace-hub/issues/2640)
   - Highest-value first actions:
     - freeze L2/L3 CLI mini-spec;
     - define metadata-only source triage rubric;
     - build old-path → new-path mapping table;
     - lock notebook outline and one baseline forecast method.

5. **Marine / knowledge / canonical-spec slice**
   - Issues:
     - [#2641 solver-queue multi-machine inbox ingestion](https://github.com/vamseeachanta/workspace-hub/issues/2641)
     - [#2474 OrcaFlex native reverse-parser equivalence proof](https://github.com/vamseeachanta/workspace-hub/issues/2474)
     - [#2473 OrcaWave-to-OrcaFlex hydrodynamic handoff semantics](https://github.com/vamseeachanta/workspace-hub/issues/2473)
     - [#2472 CALM/SPM buoy OrcaFlex semantic proof](https://github.com/vamseeachanta/workspace-hub/issues/2472)
   - Highest-value first actions:
     - draft ingestion contract note;
     - create equivalence claim table;
     - draft OrcaWave→OrcaFlex handoff matrix;
     - create CALM/SPM semantic decomposition table.

6. **Governance / compliance follow-ups slice**
   - Issues:
     - [#1839 workflow hard-stops/session governance](https://github.com/vamseeachanta/workspace-hub/issues/1839)
     - [#2142 tracked skill-link handling across repos](https://github.com/vamseeachanta/workspace-hub/issues/2142)
     - [#2255 reconcile plan-approved labels with local markers](https://github.com/vamseeachanta/workspace-hub/issues/2255)
     - [#2291 cron-health failure detection](https://github.com/vamseeachanta/workspace-hub/issues/2291)
   - Highest-value first actions:
     - governance matrix for hard-stop triggers;
     - normalize skill-link reference contract;
     - truth table for label/local-marker reconciliation;
     - cron-health signal taxonomy and incident thresholds.

7. **Provider/session/AI utilization slice**
   - Issues:
     - [#2660 compliance alert W20](https://github.com/vamseeachanta/workspace-hub/issues/2660)
     - [#2332 provider-audit bare-python3 debt](https://github.com/vamseeachanta/workspace-hub/issues/2332)
     - [#2203 pre-push tier-1 checks worktree-aware](https://github.com/vamseeachanta/workspace-hub/issues/2203)
     - [#2217 issue-hygiene repo-reality path extraction](https://github.com/vamseeachanta/workspace-hub/issues/2217)
   - Highest-value first actions:
     - pin W20 alert source and trigger path;
     - inventory bare `python3` call sites;
     - document worktree-aware root discovery;
     - define path-reference extraction schema.

### digitalmodel

8. **Repo-structure / engineering hygiene slice**
   - Issues:
     - [#596 normalize digitalmodel folder/file structure](https://github.com/vamseeachanta/digitalmodel/issues/596)
     - [#597 classify and relocate B1528 generated evidence](https://github.com/vamseeachanta/digitalmodel/issues/597)
     - [#509 OrcaFlex YAML strict validation hook](https://github.com/vamseeachanta/digitalmodel/issues/509)
     - [#514 async checkpoint ignore policy](https://github.com/vamseeachanta/digitalmodel/issues/514)
   - Recommended sequence:
     1. define folder/file taxonomy;
     2. classify B1528 evidence;
     3. align async checkpoint policy;
     4. add YAML strict hook once globs are stable.

9. **Hydrodynamics / OrcaWave-OrcaFlex proof and tests slice**
   - Issues:
     - [#595 client PDF packaging GTM material](https://github.com/vamseeachanta/digitalmodel/issues/595)
     - [#509 YAML-strict pre-commit hook](https://github.com/vamseeachanta/digitalmodel/issues/509)
     - [#514 async checkpoint ignore policy](https://github.com/vamseeachanta/digitalmodel/issues/514)
     - [#596 normalize folder/file structure](https://github.com/vamseeachanta/digitalmodel/issues/596)
   - Highest-value first actions:
     - current-state directory taxonomy;
     - classify checkpoint artifacts;
     - enumerate OrcaFlex spec YAML globs;
     - define packaged PDF output contract.

10. **Engineering-models / data domain slice**
    - Issues:
      - [#597 B1528 generated evidence classification](https://github.com/vamseeachanta/digitalmodel/issues/597)
      - [#595 client PDF packaging](https://github.com/vamseeachanta/digitalmodel/issues/595)
      - [#596 folder/file normalization](https://github.com/vamseeachanta/digitalmodel/issues/596)
      - [#509 OrcaFlex YAML strict hook](https://github.com/vamseeachanta/digitalmodel/issues/509)
    - Recommended decision bundle:
      - evidence taxonomy;
      - client PDF package contract;
      - normalization policy;
      - strict validation contract.

### assetutilities

11. **Shared-utilities package / YAML / clean-code slice**
    - Issues:
      - [#60 package development](https://github.com/vamseeachanta/assetutilities/issues/60)
      - [#58 YAML Plotting](https://github.com/vamseeachanta/assetutilities/issues/58)
      - [#41 Clean code](https://github.com/vamseeachanta/assetutilities/issues/41)
    - Recommended sequence:
      1. clarify clean-code categories;
      2. define package audience/release mode;
      3. write YAML plotting v1 contract.

12. **YAML / productivity utilities slice**
    - Issues:
      - [#59 yaml_utilities Variable Definition](https://github.com/vamseeachanta/assetutilities/issues/59)
      - [#52 YAML file split](https://github.com/vamseeachanta/assetutilities/issues/52)
      - [#56 productivity Meetings](https://github.com/vamseeachanta/assetutilities/issues/56)
      - [#42 PB Hardware and Utility Readiness](https://github.com/vamseeachanta/assetutilities/issues/42)
    - Highest-value first actions:
      - variable-resolution contract;
      - YAML split behavior matrix;
      - meeting utility v1 deliverable definition;
      - PB readiness rubric.

### worldenergydata

13. **Engineering / energy-data slice**
    - Issues:
      - [#392 public well-log datasets ingest](https://github.com/vamseeachanta/worldenergydata/issues/392)
      - [#387 pyWAsP evaluation](https://github.com/vamseeachanta/worldenergydata/issues/387)
      - [#367 ProductionAPI12 NPV FDAS migration](https://github.com/vamseeachanta/worldenergydata/issues/367)
      - [#361 calc-citation-contract](https://github.com/vamseeachanta/worldenergydata/issues/361)
    - Recommended sequence:
      1. citation contract;
      2. well-log schema + fixture matrix;
      3. pyWAsP evaluation rubric;
      4. NPV migration mapping + golden cases.

14. **Data / automation slice**
    - Issues:
      - [#368 recently-closed issue verifier](https://github.com/vamseeachanta/worldenergydata/issues/368)
      - [#366 HSE bulk dedup ingest](https://github.com/vamseeachanta/worldenergydata/issues/366)
      - [#365 BSEE binary decompression ingest](https://github.com/vamseeachanta/worldenergydata/issues/365)
      - [#360 scheduler refresh health](https://github.com/vamseeachanta/worldenergydata/issues/360)
    - Highest-value first actions:
      - classify issue closeout states;
      - rank HSE dedup keys;
      - magic-byte sample classification;
      - scheduler health contract.

15. **Capability / readiness slice**
    - Issues:
      - [#349 capability inventory and module readiness matrix](https://github.com/vamseeachanta/worldenergydata/issues/349)
      - [#350 data completeness/freshness scorecard](https://github.com/vamseeachanta/worldenergydata/issues/350)
      - [#351 source refresh runtime readiness matrix](https://github.com/vamseeachanta/worldenergydata/issues/351)
      - [#273 SODIR scheduler endpoint contract](https://github.com/vamseeachanta/worldenergydata/issues/273)
    - Highest-value first actions:
      - module boundary rubric;
      - per-source cadence/coverage contract;
      - refresh entrypoint inventory;
      - one-page SODIR endpoint contract.

### llm-wiki

16. **Knowledge-management decisions / review slice**
    - Issues:
      - [#26 Batch Pack 4 promotion](https://github.com/vamseeachanta/llm-wiki/issues/26)
      - [#25 Batch Pack 1 promotion](https://github.com/vamseeachanta/llm-wiki/issues/25)
      - [#42 LNG-projects standards routing](https://github.com/vamseeachanta/llm-wiki/issues/42)
      - [#40 reservoir literature ingest](https://github.com/vamseeachanta/llm-wiki/issues/40)
    - Recommended sequence:
      1. LNG-projects standards routing rule;
      2. reservoir literature ingest template;
      3. Batch Pack 4 promotion checklist;
      4. Batch Pack 1 legacy normalization.

17. **Engineering / extraction execution slice**
    - Issues:
      - [#11 OCR ace-linux-1 scanned PDFs](https://github.com/vamseeachanta/llm-wiki/issues/11)
      - [#10 OCR ace-linux-2 scanned PDFs](https://github.com/vamseeachanta/llm-wiki/issues/10)
      - [#9 deep extraction ace-linux-2 machine-readable PDFs](https://github.com/vamseeachanta/llm-wiki/issues/9)
      - [#8 deep extraction ace-linux-1 machine-readable PDFs](https://github.com/vamseeachanta/llm-wiki/issues/8)
    - Recommended sequence:
      1. machine-readable extraction contract on ace-linux-1;
      2. OCR contract on ace-linux-1;
      3. ace-linux-2 readiness checks;
      4. ace-linux-2 extraction/OCR only after readiness.

18. **Standards / source acquisition slice**
    - Issues:
      - [#12 ABS CP Guidance Notes acquisition](https://github.com/vamseeachanta/llm-wiki/issues/12)
      - [#7 batch LLM summaries](https://github.com/vamseeachanta/llm-wiki/issues/7)
      - [#6 research briefs equations/examples enrichment](https://github.com/vamseeachanta/llm-wiki/issues/6)
      - [#5 chart image extraction from PDFs](https://github.com/vamseeachanta/llm-wiki/issues/5)
    - Highest-value first actions:
      - official source target list;
      - summary contract and 3-document pilot;
      - enrichment value rubric;
      - chart taxonomy and benchmark set.

### assethold

19. **Finance-portfolio slice**
    - Issues:
      - [#46 duplicate path_utils helper](https://github.com/vamseeachanta/assethold/issues/46)
      - [#45 auxiliary agent-os lint cleanup](https://github.com/vamseeachanta/assethold/issues/45)
      - [#33 architecture documentation](https://github.com/vamseeachanta/assethold/issues/33)
      - [#27 portfolio benchmark vs SPY](https://github.com/vamseeachanta/assethold/issues/27)
    - Highest-value first actions:
      - inventory all `path_utils` definitions/references;
      - capture lint failures by pattern;
      - outline current modules/data flow;
      - write benchmark assumptions spec.

20. **Engineering slice**
    - Issues:
      - [#44 render-charts default dir decision](https://github.com/vamseeachanta/assethold/issues/44)
      - [#43 insider_tracker wiring](https://github.com/vamseeachanta/assethold/issues/43)
      - [#42 cache_ttl_hours config](https://github.com/vamseeachanta/assethold/issues/42)
      - [#40 pre-market/after-hours support](https://github.com/vamseeachanta/assethold/issues/40)
    - Recommended sequence:
      1. cache TTL config;
      2. render chart default dir;
      3. insider tracker integration;
      4. pre-market/after-hours support.

### aceengineer-website

21. **Website GTM pages / copy slice**
    - Issues:
      - [#9 canonical firm-copy home](https://github.com/vamseeachanta/aceengineer-website/issues/9)
      - [#8 engineering.html CAP heading renames](https://github.com/vamseeachanta/aceengineer-website/issues/8)
      - [#7 About hero FPSO/panel-mesh imagery](https://github.com/vamseeachanta/aceengineer-website/issues/7)
      - [#5 GTM Demo 4 Subsea Jumper Installation Analysis](https://github.com/vamseeachanta/aceengineer-website/issues/5)
    - Recommended sequence:
      1. canonical homepage copy brief;
      2. engineering heading rename table;
      3. Demo 4 content skeleton;
      4. imagery direction brief.

### aceengineer-strategy

22. **GTM core decisions slice**
    - Issues:
      - [#2 wedge confirmation](https://github.com/vamseeachanta/aceengineer-strategy/issues/2)
      - [#3 ICP confirmation](https://github.com/vamseeachanta/aceengineer-strategy/issues/3)
      - [#4 standards LLM-wiki industrialization](https://github.com/vamseeachanta/aceengineer-strategy/issues/4)
      - [#5 mooring quick-screen calculator](https://github.com/vamseeachanta/aceengineer-strategy/issues/5)
    - Recommended sequence:
      1. wedge thesis;
      2. primary ICP card;
      3. standards industrialization framing note;
      4. calculator concept brief.

23. **Shell/offshore outreach cluster slice**
    - Issues:
      - [#20 Shell interventions outreach cluster](https://github.com/vamseeachanta/aceengineer-strategy/issues/20)
      - [#18 offshore intervention/riser automation outreach](https://github.com/vamseeachanta/aceengineer-strategy/issues/18)
      - [#17 outreach issue](https://github.com/vamseeachanta/aceengineer-strategy/issues/17)
      - [#16 outreach issue](https://github.com/vamseeachanta/aceengineer-strategy/issues/16)
    - Planning rule: keep #20 as cluster anchor; only draft contact-level outreach after shared message spine, proof points, objection set, and CTA ladder are approved.

## Failed / Timed-Out Dispatches

Five subagent attempts timed out or produced no usable summary:

- two digitalmodel specialization attempts in the early wave;
- three no-tool planning attempts that never reached their first LLM request.

Replacement planning slices were dispatched with shorter prompts and explicit `terminal` toolset access while instructing the subagents not to call tools. Those replacement dispatches completed successfully.

## Cross-Repo Action Priorities

1. **Decision packets first**
   - `aceengineer-strategy` wedge/ICP.
   - `llm-wiki` routing/promotion rules.
   - `workspace-hub` governance/approval-state truth tables.

2. **Readiness matrices before implementation**
   - `worldenergydata` module/runtime/data scorecards.
   - `workspace-hub` provider/session/worktree path assumptions.

3. **Semantic contracts before code**
   - `digitalmodel` OrcaFlex/OrcaWave/CALM semantic proof tables.
   - `llm-wiki` OCR/extraction/summary schemas.
   - `assetutilities` YAML variable/split contracts.

4. **Artifact hygiene before client-facing delivery**
   - `digitalmodel` PDF package contract and generated-evidence taxonomy.
   - `aceengineer-website` copy/asset/CTA terminology sheet.
   - `assethold` benchmark assumptions and data-validity labels.

## Next Recommended Step

Pick 3–5 completed planning packets and promote them to formal GitHub issue plans using the existing issue-planning gate:

1. open the target issue;
2. write/update the issue plan using `docs/plans/_template-issue-plan.md`;
3. attach first-safe-action, decision checklist, hygiene gates, and cross-review route;
4. move only to `status:plan-review` after the plan is complete;
5. wait for user approval before implementation.
