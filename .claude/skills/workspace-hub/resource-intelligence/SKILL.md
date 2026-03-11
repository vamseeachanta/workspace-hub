---
name: resource-intelligence
description: Execute the Resource Intelligence stage for a WRK item using a standard artifact pack, P1/P2/P3 gap ranking, source-registry awareness, and a user pause/continue decision.
version: 1.1.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - wrk_resource_pack_generation
  - gap_ranking
  - source_registry_awareness
  - document_intelligence_linking
  - legal_scan_evidence
  - user_pause_gate
  - mining_checklist
  - category_mining_map
tools: [Read, Write, Edit, Bash, Grep, Glob]
related_skills:
  - work-queue
  - engineering-context-loader
  - document-inventory
  - document-rag-pipeline
  - knowledge-manager
  - legal-sanity
  - agent-router
  - agent-usage-optimizer
  - comprehensive-learning
requires: []
see_also:
  - references/source-registry.md
  - templates/resource-intelligence-summary.md
  - templates/resource-intelligence-template.yaml
  - scripts/init-resource-pack.sh
tags: []
---

# Resource Intelligence

Use this skill to execute Resource Intelligence stages for a WRK item:

- Stage 2: `Resource Intelligence` → exit artifact: `evidence/resource-intelligence.yaml`
- Stage 16: `Resource Intelligence Update` → exit artifact: `evidence/resource-intelligence-update.yaml`

---

## Stage 2 — Resource Intelligence

### Required Outputs

Create or update these files under `.claude/work-queue/assets/WRK-<id>/`:

**Gate-passing (machine-checked by `verify-gate-evidence.py`):**
- `evidence/resource-intelligence.yaml` — primary exit artifact

**Required companions (consumed by downstream scripts):**
- `resource-intelligence-summary.md`
- `resource-pack.md`
- `sources.md`
- `constraints.md`
- `domain-notes.md`
- `open-questions.md`
- `resources.yaml`

### evidence/resource-intelligence.yaml Schema

```yaml
wrk_id: WRK-NNN
generated_at: "YYYY-MM-DDTHH:MM:SSZ"
generated_by: claude          # or codex | gemini
stage: 2

target_repos:
  - repo-name

# Gate-verified fields (verify-gate-evidence.py enforces these):
skills:
  core_used:                  # minimum 3 entries required
    - coordination/workspace/work-queue
    - workspace-hub/work-queue-workflow
    - workspace-hub/resource-intelligence
  related: []
completion_status: continue_to_planning   # or pause_and_revise
top_p1_gaps: []               # non-empty → completion_status must be pause_and_revise

# Recommended fields (WARN if missing — will become FAIL after 3 production runs):
domain:
  problem: >
    One sentence: what is broken or missing that this WRK fixes?
  architecture_decision: >
    One sentence: what approach was chosen and why?

# Documentation fields (not gate-checked today):
existing_files:
  - path: path/to/file.py
    status: existing          # existing | new | modified | reference
    notes: "brief description"
constraints:
  - constraint description
top_p2_gaps: []
top_p3_gaps: []
```

### Stage 2 Micro-Skill Checklist

1. Read `## Mission` from `working/WRK-NNN.md` — internalize scope boundary
2. Read `category`, `subcategory`, `target_repos` from WRK frontmatter
3. Create `assets/WRK-NNN/evidence/` directory if it does not exist
4. Mine resources using the **Resource Mining Checklist** below, guided by the **Category→Mining Map**
5. Assess complexity and determine `completion_status` (`continue_to_planning` | `pause_and_revise`)
6. Record `skills.core_used` (minimum 3), `constraints`, `top_p1_gaps`, and recommended `domain.*` fields
7. Write `evidence/resource-intelligence.yaml` and required companion artifacts
8. Write `resource-intelligence-summary.md` using `templates/resource-intelligence-summary.md`

> **⛔ STOP — Stage 2 exit point.**
> Write `evidence/resource-intelligence.yaml` and halt.
> Do NOT create or edit plan, spec, implementation, or review artifacts.
> Do NOT begin Stage 3 (Triage) or later stages. The next stage starts fresh from this file.

---

## Stage 16 — Resource Intelligence Update

### Required Outputs

Record incremental additions discovered during execution:

**Gate-passing:**
- `evidence/resource-intelligence-update.yaml`

**Also update:**
- `evidence/stage-evidence.yaml` — stage 16 entry

### evidence/resource-intelligence-update.yaml Schema

```yaml
wrk_id: WRK-NNN
stage: 16
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_by: claude

additions:                    # new sources, constraints, or findings discovered during execution
  - type: source              # source | constraint | finding | skill
    description: "what was discovered"
    path: optional/file/path
no_additions_rationale: ""    # populate if additions is empty — explain why nothing new was found
```

## Micro-Skill Checklist (Stage 16)

1. Re-read the WRK `## Mission` boundary — only record additions in scope
2. Review `evidence/execute.yaml` and `evidence/future-work.yaml` for new sources/constraints
3. Identify any new sources, constraints, findings, or skills discovered during execution
4. Write `evidence/resource-intelligence-update.yaml` with `additions[]` OR `no_additions_rationale`
5. Update `evidence/stage-evidence.yaml` — set stage 16 entry to `status: done`

> **⛔ STOP — Stage 16 exit point.**
> Write `evidence/resource-intelligence-update.yaml` and halt.
> Do NOT reopen planning, spec, or implementation artifacts.
> Do NOT begin Stage 17. The next stage starts fresh from this file.

---

## Resource Mining Checklist

Mine in this order (cheapest lookup first). Stop a category when no relevant results found after a reasonable scan.

| # | Category | Where to look | When relevant |
|---|----------|--------------|---------------|
| 1 | **Skills** | `.claude/skills/**` — scan for domain keywords | Always — load domain skills before planning |
| 2 | **Prior WRKs** | `work-queue/archive/`, `related:` + `blocked_by:` fields | Always — avoid re-deriving solved problems |
| 3 | **Memory** | `MEMORY.md`, `memory/*.md` | Always — institutional knowledge |
| 4 | **Existing code / scripts** | `src/`, `scripts/` in each `target_repo` | Implementation WRKs |
| 5 | **Specs / plans** | `specs/wrk/`, `specs/modules/` | Route B/C — prior design decisions |
| 6 | **Workspace docs** | `.claude/docs/` | Architecture, orchestration, legal decisions |
| 7 | **Document index** | `data/document-index/registry.yaml`, `index.jsonl`, `standards-transfer-ledger.yaml` | Engineering / standards WRKs |
| 8 | **Mounted sources** | `/mnt/ace/`, `/mnt/remote/ace-linux-2/dde` | Engineering domain WRKs |
| 9 | **Online / additive** | External URLs | Only when repo sources are insufficient |

---

## Category→Mining Map

Read `category` and `subcategory` from WRK frontmatter. Use this table to select which mining categories to prioritise.

| WRK `category` | High-priority mining | Low-priority (skip unless relevant) |
|----------------|---------------------|--------------------------------------|
| `harness` | 1 Skills, 2 Prior WRKs, 3 Memory, 6 Workspace docs | 7 Document index, 8 Mounted sources |
| `engineering` | 4 Existing code, 7 Document index, 8 Mounted sources | 9 Online (check index first) |
| `data` | 4 Existing code, 5 Specs, 7 Document index | 8 Mounted sources |
| `platform` | 1 Skills, 4 Existing code, 6 Workspace docs | 7 Document index |
| `business` | 3 Memory, 5 Specs, 6 Workspace docs | 7 Document index, 8 Mounted sources |
| `maintenance` | 2 Prior WRKs, 4 Existing code, 6 Workspace docs | 8 Mounted sources, 9 Online |
| `personal` | 3 Memory | all others |
| `uncategorised` | 1 Skills, 2 Prior WRKs, 3 Memory | decide per subcategory |

For any `subcategory` containing `pipeline`, `viv`, `dnv`, `api rp`, `iso`, `fea`, `cfd`, `ansys`, `orcaflex` → always include categories 7 and 8 regardless of `category`.

---

## target_repos→Paths

For each repo in `target_repos`, inventory these paths during mining category 4 (Existing code / scripts):

| Repo | Paths to inventory |
|------|--------------------|
| `workspace-hub` | `scripts/`, `.claude/skills/`, `.claude/docs/`, `specs/` |
| `digitalmodel` | `src/digitalmodel/`, `tests/`, `specs/wrk/` |
| `assetutilities` | `src/assetutilities/`, `tests/` |
| `worldenergydata` | `src/worldenergydata/`, `tests/` |
| `assethold` | `src/assethold/`, `tests/` |
| `ogmanufacturing` | `src/ogmanufacturing/`, `tests/` |
| `aceengineer-website` | `content/`, `src/` |
| `aceengineer-admin` | `src/` |
| any other repo | `src/`, `tests/`, `scripts/` (if they exist) |

---

## Gap Ranking

- `P1`: blocks stage pass
- `P2`: weakens planning materially
- `P3`: enhancement only

Rubric:

- `P1`: the stage cannot safely continue — a required artifact, source, legal gate, or core context is missing or contradictory
- `P2`: the stage can continue, but planning quality or repeatability is materially weakened
- `P3`: the stage remains valid; the gap only improves ergonomics, automation depth, or future scale

If any unresolved `P1` gaps remain → `completion_status: pause_and_revise`.
If no unresolved `P1` gaps remain → `completion_status: continue_to_planning`.

---

## First-Pass Routing Rule

- `agent-router` is advisory for agent fit only
- `agent-usage-optimizer` is advisory for quota and capacity only
- the orchestrator retains final routing authority
- quota/capacity risk from `agent-usage-optimizer` takes precedence over fit preference from `agent-router` when they conflict
- overrides must be recorded in `resources.yaml` under `routing_overrides[]` with `decision`, `reason`, `recorded_at`, `recorded_by`

---

## Source Rules

- Prefer repo-native and already-indexed sources first.
- Every downloaded source must record: `source_type`, `origin`, `license/access`, `retrieval_date`, `canonical_storage_path`, `duplicate/superseded`, `status` (`available` | `source_unavailable`), fallback evidence when unavailable.

Read `references/source-registry.md` before adding or changing source-root mappings.

---

## Templates and Scripts

- Gate artifact template: `templates/resource-intelligence-template.yaml`
- Summary template: `templates/resource-intelligence-summary.md`
- Resource-pack scaffolder: `scripts/init-resource-pack.sh`
- Resource-pack validator: `scripts/validate-resource-pack.sh`
- Maturity sync/check: `scripts/sync-maturity-summary.py`

Run `init-resource-pack.sh WRK-NNN` to scaffold companion files.
Run `validate-resource-pack.sh` before treating Stage 2 as passable.

---

## Version History

- **1.1.1** (2026-03-07): Codex review fixes (WRK-1029)
  - stage-02 changed from chained_agent → task_agent (stop guard was contradicted by chained_stages)
  - Category→Mining Map: added `uncategorised` row
  - Stage 16 Micro-Skill Checklist added (was missing, only Stage 2 had one)
  - stage-16 blocking_condition: `lessons[]` → `additions[] and no_additions_rationale`
- **1.1.0** (2026-03-07): Stage 2/16 alignment with WRK-1028 stage isolation contract (WRK-1029)
  - `evidence/resource-intelligence.yaml` added as primary gate-passing exit artifact for Stage 2
  - `evidence/resource-intelligence-update.yaml` confirmed as Stage 16 gate artifact
  - `resource-intelligence-summary.md` retained as required companion (consumers unchanged)
  - Separate Stage 2 / Stage 16 sections with distinct checklists and stop guards
  - Stage 2 micro-skill checklist: 8 items including path setup and hard stop on artifacts
  - Resource Mining Checklist: 9 ordered categories (Skills → Online/additive)
  - Category→Mining Map: WRK `category` values mapped to mining priorities
  - target_repos→Paths: per-repo inventory path table
  - Schema: gate-verified fields distinguished from recommended/WARN fields
  - `domain.problem` and `domain.architecture_decision`: required in schema, WARN in gatepass
- **1.0.0** (2026-02-xx): Initial release
