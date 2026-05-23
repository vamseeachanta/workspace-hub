# Canonical Anti-Repetition Surface (CARS) — Design

> **Status:** design-draft (awaiting user spec review)
> **Date:** 2026-05-22
> **Author:** Claude main session, in collaboration with vamseeachanta (brainstorming via superpowers:brainstorming skill)
> **Issue (to be filed after spec review):** TBD — placeholder for "feat(workflow): canonical anti-repetition surface across data/exec/output layers"
> **Related issues:** [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778), [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744), [#2775](https://github.com/vamseeachanta/workspace-hub/issues/2775), [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685), [#2400](https://github.com/vamseeachanta/workspace-hub/issues/2400)
> **Supersedes:** none (forward-only landing)

---

## TL;DR

Enhance the workspace-hub issue workflow so that every data ingest, execution result, and output artifact is canonicalized into the llm-wiki ecosystem (generic in `llm-wiki`; client-specific in `llm-wiki-<client>` per [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778)) under a three-tier structure: Concept (knowledge) → Method (technique) → Result (computation). Every issue's pre-flight queries the canonical store first; cache hits short-circuit re-derivation. Misses produce new canonical entries at close. The corpus compounds monotonically over time — work is never repeated, concepts never re-described, methods never re-designed.

Motivation in the user's words: *"not repeat work, not repeat concepts. We only improve and move forward. No wasted time, tokens, execution cycles."*

---

## Motivation

The workspace-hub ecosystem today produces durable knowledge artifacts in 6+ scattered locations per issue: `docs/plans/`, `scripts/review/results/`, `<sibling>/src/`, `<sibling>/tests/`, `knowledge/wikis/…` or `llm-wiki/…` or `llm-wiki-<client>/…`, `docs/reports/`, `docs/session-handoffs/`, `~/.claude/projects/.../memory/`. Each issue's workflow is action-centric (Issue → Plan → Approve → Implement → Close) but artifact-blind — there is no single manifest declaring where this issue's artifacts will land, no enforced anti-repetition lookup, and no provenance trail linking executable code to canonical wiki entries.

The downstream consequences are concrete and recurring:

- **Duplicate computation.** Engineering calcs (mooring MBL, wind coefficient lookup, fatigue analyses) are re-run across issues because no canonical record of prior runs exists.
- **Re-described concepts.** Methodology pages get authored multiple times because the existing version is in a different sibling, different domain, or different naming convention.
- **Drift unnoticed.** Code that produced a known canonical result evolves silently — the result becomes stale with no operational signal.
- **Cross-sibling fragility.** Wiki content that should reference generic concepts ends up re-derived locally per-project; client wiki content leaks ideas back into generic; routing decisions drift per-session per-agent.

[#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778) locks the *routing* layer (which sibling holds what); [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) pilots the first client sibling; [#2775](https://github.com/vamseeachanta/workspace-hub/issues/2775) locks the harness SSoT. CARS layers above all three — it makes the issue workflow itself enforce the anti-repetition contract.

---

## Design Decisions Locked

The following decisions were made through interactive brainstorming on 2026-05-22 and are LOCKED for the implementation plan that follows this design. Subsequent revisions require an explicit user re-approval cycle.

| # | Decision | Rationale |
|---|---|---|
| D1 | SSoT shape = **both layered** (per-issue Layer Manifest + workspace-wide registry) | Per-issue declares concrete artifacts; registry enforces type→location rules globally. Catches both manifest defects and routing defects in one gate. |
| D2 | Result scope = **all data/execution/output layer artifacts** | Excludes harness/infrastructure, source code, memory bridge. Includes engineering calcs, data ingests, methodology applications, report generations. |
| D3 | Tier model = **three tiers**: Concept → Method → Result | Anti-repetition for knowledge (T1), methodology (T2), computation (T3). Matches existing calc-citation pattern; generalizes it. |
| D4 | Lookup posture = **hard gate** | Plan cannot enter `status:plan-review` without canonical-store lookup output. Honors "no wasted cycles" motivation. |
| D5 | Build sequencing = **Approach A: Tier-3-first** | Highest-leverage waste eliminated first (computation dedup); builds on existing calc-citation pilot [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685); Tier-1/2 schemas emerge from real usage. |
| D6 | Tier-3 canonical key = **(method_id, inputs_fingerprint, params_fingerprint)** | `code_sha` is stored metadata for drift detection but NOT part of the lookup key — avoids corpus fragmentation on every commit. |
| D7 | Inline-vs-reference output threshold = **100 KB inline, larger by `output_reference`** | Keeps results grep-able; avoids wiki bloat. |
| D8 | Adversarial review depth = **scales with disposition** (cite-and-stop=T1, verification/improvement=T2, genuinely-new=T3) | Saves provider calls on cache hits; reviewers explicitly audit lookup section first to defend against false-negative attack surface. |
| D9 | Sidecar staging = **`docs/sessions/<issue>/results/`** then promoted at Close | Avoids phantom wiki entries from abandoned implementations; clean rollback by design. |
| D10 | Close-gate ratchet = **soft for weeks 1-4, hard at week 5+** | Lets schema and disposition flow stabilize before enforcing; retro at week 4 decides promotion vs extension. |
| D11 | Contract attachment = **`config/agents/SHARED_SOUL.md` must-fire bullet + `.claude/rules/canonical-store-contract.md`** | Matches calc-citation-contract precedent. AGENTS.md stays at 20-line cap. |
| D12 | Registry location = **`workspace-hub/config/canonical-store/`** | Sits next to `config/agents/`, `config/ai-tools/`, `config/data-flow/`. Inherits existing retrieval pattern. |
| D13 | Registry edits = **always T3 review** (path-based, overrides disposition) | Blast radius proportional to review depth; mis-routing risk is ecosystem-load-bearing. Allow-list for description/CHANGELOG formatting. |
| D14 | Bootstrap seed source = **#2685 pilot + 2026-05-20 OCIMF landing + BSEE production extracts** | Pre-validated work; highest-likelihood-of-hit seeds; populates 10-15 entries in weeks 1-2. |
| D15 | Drift detection = **nightly cron**, auto-template verification issues when DRIFTED > 20 | Drift report becomes operational backlog; matches existing daily-readiness-cron pattern. |

---

## Section 1 — Architecture Overview

### Working name

**CARS** — Canonical Anti-Repetition Surface.

### Three coupled artifacts

```
┌─────────────────────────────────────────────────────────────────┐
│  CANONICAL STORE  (Tier 1 / 2 / 3 wiki entries)                 │
│  ───────────────────────────────────────────────                 │
│  • llm-wiki/             ← generic (private since 2026-05-20)   │
│  • llm-wiki-<client>/    ← per-client (suffix form, #2778)      │
│    └─ projects/<project>/  ← project-folder nesting             │
└──────────────────────▲──────────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────────┐
│  WORKSPACE REGISTRY  (workspace-hub/config/canonical-store/)     │
│  ├─ layer-routing.yaml      ← kind → (tier, layer, sibling, path)│
│  ├─ method-registry.yaml     ← named methods → wiki + impls      │
│  ├─ tier-schema/             ← JSON schemas for tier frontmatter │
│  └─ domain-taxonomy.yaml     ← canonical domain slugs            │
└──────────────────────▲──────────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────────┐
│  PER-ISSUE PLAN  (docs/plans/YYYY-MM-DD-issue-NNN-slug.md)       │
│  ── new required sections ──                                     │
│  ├─ Canonical Store Lookup (Tier-1/2/3 query results)           │
│  ├─ Layer Manifest (data / exec / output rows)                  │
│  ├─ Disposition (cite-and-stop / verification / improvement /   │
│  │                genuinely-new)                                 │
│  └─ Code-Version Pin (sha at execution time)                    │
└──────────────────────▲──────────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────────┐
│  ENFORCEMENT (workspace-hub/scripts/enforcement/)                │
│  ├─ check-canonical-lookup.sh       ← blocks status:plan-review │
│  ├─ check-layer-manifest.sh         ← validates manifest rows   │
│  ├─ check-result-dedup.sh           ← Tier-3 hard gate          │
│  ├─ check-supersedes-lineage.sh     ← improvement-gate          │
│  └─ check-wiki-promotion-landed.sh  ← closure attestation       │
└──────────────────────────────────────────────────────────────────┘
```

### Two-axis data flow

```
                          LAYER →
                    data   exec   output
                   ┌─────┬─────┬──────┐
       CONCEPT     │ T1d │ T1e │ T1o  │   "what is it"
TIER ↓ METHOD      │ T2d │ T2e │ T2o  │   "how is it done"
       RESULT      │ T3d │ T3e │ T3o  │   "what came out"
                   └─────┴─────┴──────┘
```

Each cell is a valid canonical entry. The Layer Manifest in each plan declares which cells the issue touches.

### Workflow gate integration (overview — detailed in Section 3)

```
Issue → Resource Intel → [NEW] Canonical Store Lookup → [NEW] Layer Manifest
      → Plan body → Adversarial Review → status:plan-review → USER APPROVES
      → status:plan-approved → Implement (TDD) → [NEW] Emit result sidecar
      → Cross-review → Close → [NEW] Promote sidecar → wiki entry
```

Four `[NEW]` insertions; no existing gate phase is removed.

---

## Section 2 — Tier Schemas

### Common metadata footer (all three tiers)

```yaml
# Identity & routing (per #2778)
visibility: private-llm-wiki | private-client-llm-wiki | public-federal-data
client: <slug>              # required iff visibility=private-client-llm-wiki
project: <slug>             # optional; required if entry is project-scoped
source_sibling: llm-wiki | llm-wiki-<client>

# Lineage (anti-repetition)
supersedes: [<slug>, ...]
superseded_by: <slug> | null
related: [<slug>, ...]

# Promotion-ledger metadata (per #2744 pattern)
created: YYYY-MM-DDTHH:MM:SSZ
created_by: <agent or user>
last_reviewed: YYYY-MM-DDTHH:MM:SSZ
reviewer: <user>
revision: <integer>
confidence: 0.0–1.0
completion: 0.0–1.0

# Workflow provenance
authored_in_issue: <repo>#<NNNN>
authored_in_plan: docs/plans/YYYY-MM-DD-issue-NNNN-slug.md
```

### Tier 1 — CONCEPT page

**Purpose:** "What is this thing / concept?" Anti-repetition for *knowledge*.
**Canonical key:** the slug (filesystem path).
**Path:** `llm-wiki/<domain>/concepts/<concept-slug>.md`

```yaml
tier: concept
concept_slug: marine-engineering/concepts/vlcc-wind-coefficients
references:
  standards: [ocimf-meg3, ocimf-meg4, dnv-rp-c205]
  concepts: [marine-engineering/concepts/wind-loading-fundamentals]
  datasets: [marine-engineering/datasets/ocimf-meg4-annex-a]
applied_by_methods:
  - marine-engineering/methods/ocimf-meg4-wind-coeff-lookup
# [common footer]
```

### Tier 2 — METHOD page

**Purpose:** "How is the concept computed/applied?" Anti-repetition for *methodology*.
**Canonical key:** `method_id` registered in `method-registry.yaml`.
**Path:** `llm-wiki/<domain>/methods/<method-slug>.md`

```yaml
tier: method
method_id: ocimf-meg4-wind-coeff-lookup
method_version: 2.1.0
applies_to_concepts:
  - marine-engineering/concepts/vlcc-wind-coefficients
implementations:
  - sibling: digitalmodel
    module: digitalmodel.orcaflex.wind_loads
    function: lookup_meg4_coefficient
    entry_point: digitalmodel.orcaflex.wind_loads:lookup_meg4_coefficient
input_schema:
  vessel_class: {type: string, enum: [vlcc, suezmax, aframax, ...]}
  wind_heading_deg: {type: number, minimum: 0, maximum: 360}
  loading_condition: {type: string, enum: [ballast, loaded]}
parameters_schema:
  interpolation: {type: string, enum: [linear, cubic], default: linear}
output_schema:
  cx: {type: number}
  cy: {type: number}
  cn: {type: number}
data_dependencies:
  - marine-engineering/datasets/ocimf-meg4-annex-a
# [common footer]
```

### Tier 3 — RESULT entry

**Purpose:** "We ran this method on these inputs and got this output." Anti-repetition for *computation*.
**Canonical key:** `(method_id, inputs_fingerprint, params_fingerprint)` — `code_sha` is metadata.
**Path:** `llm-wiki/<domain>/results/<YYYY-MM-DD>-<method-slug>-<inputs-fp-short>.md`

```yaml
tier: result
result_id: 2026-05-22-ocimf-meg4-wind-coeff-lookup-7a3f8c

# Lookup key tuple
method_ref: ocimf-meg4-wind-coeff-lookup
method_version_at_run: 2.1.0
inputs_fingerprint: sha256:7a3f8c91e2b4d...
params_fingerprint: sha256:0a1b2c3d4e5f6...

# Verbatim inputs & params (so fingerprints are reproducible)
inputs:
  vessel_class: vlcc
  wind_heading_deg: 90
  loading_condition: loaded
parameters:
  interpolation: linear

# Result (inline if small; output_reference if >100KB)
output:
  cx: 0.42
  cy: 0.81
  cn: 0.05
output_fingerprint: sha256:f3e2d1c0b9a8...

# Code-version provenance (metadata; not part of key)
execution:
  sibling: digitalmodel
  code_sha: 9f3a2b1c8d7e6f5a4b3c2d1e0f9a8b7c
  code_version: 0.4.2
  entry_point: digitalmodel.orcaflex.wind_loads:lookup_meg4_coefficient
  ran_at: 2026-05-22T14:30:00Z
  ran_by: <agent-or-user>
  runtime_seconds: 0.034
  environment: uv-run; python 3.12.0; numpy 2.1.0

# Citations consumed
citations:
  - code_id: ocimf-meg4-annex-a
    source_sibling: llm-wiki
    source_path: marine-engineering/datasets/ocimf-meg4-annex-a/coeff-table-1.csv
    revision: meg4-2018

# QA (filled on verification disposition re-runs)
qa:
  reference_result: null
  matches_reference: null
  divergence: null

# [common footer]
```

### Fingerprinting algorithm

Both `inputs_fingerprint` and `params_fingerprint` are computed by RFC 8785 canonical JSON form + SHA-256:

```python
def fingerprint(obj: dict) -> str:
    import hashlib, json, unicodedata
    canonical = json.dumps(
        obj, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), default=str,
    )
    canonical = unicodedata.normalize("NFC", canonical)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

Float-precision normalization (round to 15 sig figs) is required for cross-platform stability; this is deferred to the implementation plan per §6 open question #1.

---

## Section 3 — Workflow Gate Integration

### Enhanced gate sequence

```
PHASE 1 — Issue intake          (unchanged)
PHASE 2 — Resource Intelligence
           existing: standards, prior plans, code search
           [NEW] Canonical Store Lookup (REQUIRED)
                  - query Tier-1, Tier-2, Tier-3
                  - declare DISPOSITION (one of four)
PHASE 3 — Draft Plan
           existing: pseudocode, files, TDD tests
           [NEW] Layer Manifest (REQUIRED)
           [NEW] Code-Version Pin
PHASE 4 — Adversarial Review
           [NEW] Depth scales with disposition (D8):
                  cite-and-stop → T1
                  verification  → T2
                  improvement   → T2
                  genuinely-new → T3
PHASE 5 — status:plan-review
           [GATE] check-canonical-lookup.sh
           [GATE] check-layer-manifest.sh
           [GATE] check-supersedes-lineage.sh
           HARD STOP — USER APPROVES → status:plan-approved
PHASE 6 — Implement (TDD)
           existing: tests first, code second
           [NEW] Calc code emits sidecar to docs/sessions/<issue>/results/
PHASE 7 — Cross-Review
           [NEW] Reviewers verify sidecar fingerprints match declared disposition
PHASE 8 — Close
           [NEW] Promote sidecar → wiki entry
                  cite-and-stop: no wiki write; close with citation
                  verification:  append qa.* to existing entry
                  improvement:   write new entry + flip prior's superseded_by
                  genuinely-new: write new entries as declared
           [GATE] check-wiki-promotion-landed.sh (SOFT weeks 1-4; HARD week 5+)
           [NEW] Comment on issue with wiki slug(s) + metric update
```

### Disposition decision tree

```
                    ┌────────────────────────────┐
                    │ Canonical Store Lookup     │
                    └────────────┬───────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
        NO HIT              MID HIT             TIER-3 HIT
       (all 3 tiers)     (Tier-1 or 2)        (full match)
            │                    │                    │
            ▼                    ▼                    ▼
       genuinely-new        improvement      Is code_sha drift?
       → full T3 review     → T2 review      YES → improvement
       → emit new T1/2/3    → emit new       NO  → cite-and-stop
         as needed            T2/3 entries   (or verification if QA)
```

### Enforcement scripts

| Script | Validates | Exit-1 effect |
|---|---|---|
| `check-canonical-lookup.sh` | Plan has Canonical Store Lookup section with valid Disposition; cited slugs exist | Blocks `status:plan-review` |
| `check-layer-manifest.sh` | Plan has Layer Manifest with ≥1 row; each row conforms to `layer-routing.yaml` | Blocks `status:plan-review` |
| `check-result-dedup.sh` | Staged sidecar's `(method_id, inputs_fp, params_fp)` is unique unless disposition ∈ {verification, improvement} | Blocks wiki-promotion commit |
| `check-supersedes-lineage.sh` | If disposition=improvement, supersedes link points to existing entry; prior `superseded_by` is null-or-update-target | Blocks `status:plan-review` |
| `check-wiki-promotion-landed.sh` | Declared wiki slug exists at expected path, frontmatter parses, schema valid | SOFT (weeks 1-4): warning comment. HARD (week 5+): blocks issue close. |

### Plan template additions

Three required sections inserted into `docs/plans/_template-issue-plan.md` between **Resource Intelligence Summary** and **Artifact Map**:

```markdown
## Canonical Store Lookup (REQUIRED)
Queried at: YYYY-MM-DDTHH:MM:SSZ
Query method: scripts/canonical-store/query.sh | manual grep | wiki-search MCP

### Tier 1 — Concept hit(s)
- [ ] No hit
- [ ] Hit: <concept_slug> — last_reviewed YYYY-MM-DD, confidence 0.XX

### Tier 2 — Method hit(s)
- [ ] No hit
- [ ] Hit: <method_id>@<version> — implementations: <sibling.module>

### Tier 3 — Result hit(s)
- [ ] No hit  (query key: method=<id>, inputs_fp=<sha256:...>, params_fp=<sha256:...>)
- [ ] Hit: <result_id>
       code_sha at run: <sha>  | current HEAD: <sha>  | drift: yes/no

### Disposition (REQUIRED — pick exactly one)
- [ ] cite-and-stop
- [ ] verification
- [ ] improvement
- [ ] genuinely-new

## Layer Manifest (REQUIRED)
| Tier | Layer  | Kind                  | Sibling           | Path           | Lifecycle |
|------|--------|-----------------------|-------------------|----------------|-----------|
| T3   | exec   | engineering-result    | llm-wiki          | <path>         | NEW       |
| ...  | ...    | ...                   | ...               | ...            | ...       |

## Code-Version Pin (REQUIRED if disposition ≠ cite-and-stop)
- <sibling> @ <branch>  → expected SHA at implementation start: <blank or sha>
- Recorded SHA at implementation completion: <filled at Close>
```

### Skill / Doc updates

| Skill / Doc | Change |
|---|---|
| `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Add Step 2.5 (Canonical Store Lookup), Step 3.1 (Layer Manifest), Step 8.1 (wiki promotion) |
| `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` | Update Step 6 (sidecar emission), Step 7 (promotion) |
| `docs/plans/_template-issue-plan.md` | Insert three new required sections |
| `docs/plans/README.md` | Document disposition decision tree |
| `.claude/rules/calc-citation-contract.md` | Note that #2685 pilot is a special case of canonical-store contract |
| `.claude/rules/codes-standards-data-routing.md` | Cross-ref to canonical-store contract for results |
| `config/agents/SHARED_SOUL.md` | Add must-fire rule (one bullet, per D11) |
| `.claude/rules/canonical-store-contract.md` | NEW — the full contract |

---

## Section 4 — Workspace Registry

### Directory layout

```
workspace-hub/config/canonical-store/
├── layer-routing.yaml              ← kind → (tier, layer, sibling, path) rules
├── method-registry.yaml             ← named methods → wiki + implementations
├── tier-schema/
│   ├── concept.schema.json
│   ├── method.schema.json
│   ├── result.schema.json
│   └── common-footer.schema.json
├── domain-taxonomy.yaml             ← canonical domain slugs
├── CHANGELOG.md
└── README.md
```

### layer-routing.yaml (excerpt)

```yaml
version: 1
last_updated: 2026-05-22
ref_documents:
  - .claude/rules/codes-standards-data-routing.md
  - .claude/rules/wiki-sibling-routing.md      # produced by #2778
  - issues: [2778, 2744, 2731]

tier_1_rules:
  - kind: concept-page-generic
    layer: any
    sibling: llm-wiki
    path_glob: "<domain>/concepts/<slug>.md"
    visibility_required: private-llm-wiki

  - kind: concept-page-client
    layer: any
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/concepts/<slug>.md"
    visibility_required: private-client-llm-wiki
    client_field_required: true

  - kind: standards-page
    layer: data
    sibling: llm-wiki
    path_glob: "<domain>/standards/<code-id>.md"
    visibility_required: private-llm-wiki

  - kind: dataset-page
    layer: data
    sibling: llm-wiki
    path_glob: "<domain>/datasets/<dataset-slug>/"

  - kind: public-federal-data
    layer: data
    sibling: worldenergydata-wiki
    path_glob: "<domain>/datasets/<dataset-slug>/"
    visibility_required: public-federal-data
    license_required: public-domain

tier_2_rules:
  - kind: engineering-method
    layer: exec
    sibling: llm-wiki
    path_glob: "<domain>/methods/<method-slug>.md"
    method_registry_required: true

  - kind: client-specific-method
    layer: exec
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/methods/<method-slug>.md"
    visibility_required: private-client-llm-wiki
    method_registry_required: true
    client_field_required: true

tier_3_rules:
  - kind: engineering-result
    layer: exec
    sibling: llm-wiki
    path_glob: "<domain>/results/<YYYY-MM-DD>-<method-slug>-<inputs-fp-short>.md"
    method_ref_required: true

  - kind: client-result
    layer: any
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/results/<YYYY-MM-DD>-<method-slug>-<inputs-fp-short>.md"
    visibility_required: private-client-llm-wiki
    method_ref_required: true
    client_field_required: true

  - kind: report-output
    layer: output
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/results/reports/<YYYY-MM-DD>-<report-slug>.md"

  - kind: generic-report-output
    layer: output
    sibling: llm-wiki
    path_glob: "<domain>/results/reports/<YYYY-MM-DD>-<report-slug>.md"

exclusions:
  - kind: harness-config
    matches: ["AGENTS.md", "CLAUDE.md", ".claude/rules/**", ".claude/skills/**", "config/agents/**"]
    reason: "Harness — covered by #2775."
  - kind: source-code
    matches: ["**/src/**", "**/tests/**", "**/*.py", "**/*.ts"]
    reason: "Source code is the implementation; canonical-store only governs results."
  - kind: memory-bridge
    matches: [".claude/memory/**", "~/.claude/projects/**/memory/**"]
    reason: "Memory-bridge surface (Hermes-managed)."
```

### method-registry.yaml (excerpt)

```yaml
version: 1
last_updated: 2026-05-22

methods:
  ocimf-meg4-wind-coeff-lookup:
    canonical_page: marine-engineering/methods/ocimf-meg4-wind-coeff-lookup
    canonical_sibling: llm-wiki
    current_version: 2.1.0
    implementations:
      - sibling: digitalmodel
        module: digitalmodel.orcaflex.wind_loads
        function: lookup_meg4_coefficient
    deprecated: false
    domain: marine-engineering
    standards_consumed: [ocimf-meg4-annex-a]

  dnv-os-e301-mooring-safety-factor:
    canonical_page: marine-engineering/methods/dnv-os-e301-mooring-safety-factor
    canonical_sibling: llm-wiki
    current_version: 1.0.0
    implementations:
      - sibling: digitalmodel
        module: digitalmodel.orcaflex.mooring_design
        function: check_mbl_with_safety_factor       # the #2685 pilot
    domain: marine-engineering
    standards_consumed: [dnv-os-e301]

  bsee-production-extract:
    canonical_page: data-pipeline/methods/bsee-production-extract
    canonical_sibling: worldenergydata-wiki
    current_version: 0.3.0
    implementations:
      - sibling: worldenergydata
        module: worldenergydata.bsee.production
        function: extract_production_yearly
    domain: energy-data-public

  # Client-method entries live in registry (visible) but point to
  # llm-wiki-<client> (gated by sibling's auth boundary)
  sirocco-mooring-fatigue-customization:
    canonical_page: projects/sirocco/methods/sirocco-mooring-fatigue-customization
    canonical_sibling: llm-wiki-acma
    current_version: 0.1.0
    client: acma
    project: sirocco
    references_generic_methods: [dnv-os-e301-mooring-safety-factor]
```

### Retrieval patterns

1. **Plan-time lookup** (Phase 2): `scripts/canonical-store/query.sh --tier 3 --method <id> --inputs '{...}' --params '{...}'` → emits plan-section-ready output
2. **Code-time method resolution**: `from canonical_store import resolve_method; meth = resolve_method("<method_id>")` reads `method-registry.yaml`
3. **Pre-commit validation**: enforcement scripts read `layer-routing.yaml` + `tier-schema/*.json`

### Registry edit lifecycle

| Change | Process |
|---|---|
| Add new `method_id` | Issue → Plan (disposition=genuinely-new for the method) → T3 review (per D13) → land Tier-2 wiki page + registry entry in same PR |
| Bump method version (breaking) | Issue with disposition=improvement → T3 review → bump `current_version` + new Tier-2 page + supersedes link from old |
| Deprecate a method | Issue → Plan → set `deprecated: true`, `superseded_by: <new_method_id>` |
| Add layer-routing rule | Issue → Plan with disposition=genuinely-new → T3 review |
| Tier-schema change | Plan with disposition=improvement → T3 review → migration script if breaking |

Registry has its own `CHANGELOG.md` audit trail. Every edit gets one line: date + issue + nature-of-change.

---

## Section 5 — Lifecycle: Bootstrap, Supersession, Drift

### 5.1 — Bootstrap

**Empty-corpus problem:** For the first ~2-4 weeks, every Tier-3 lookup returns NO_HIT. Without proactive seeding, the gate feels like ceremony.

**Seed-first principle:** Before turning on hard enforcement, seed the corpus with 10-15 highest-leverage entries from:

- Source 1: Existing calc-citation pilot ([#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685)) — DNV-OS-E301 mooring safety factor
- Source 2: OCIMF MEG3/MEG4 Annex A datasets (landed 2026-05-20)
- Source 3: BSEE production extracts (worldenergydata-wiki, public-domain)

**Phases:**

```
Week 0  — REGISTRY-FIRST
   Land config/canonical-store/ with empty registries
   Land tier-schema/*.json
   Land enforcement scripts in WARN-ONLY mode
   Land plan template + rule + SHARED_SOUL.md must-fire

Week 1-2 — SEED LANDING
   Open 10-15 seed issues; each runs full gate
   Targets: 3 Tier-1 + 5 Tier-2 + 7-10 Tier-3 entries

Week 3 — VALUE-CURVE EVALUATION
   docs/reports/canonical-store-hit-rate-weekly.md publishes weekly
   Target ≥30% hit rate; if <15% extend soft phase

Week 4 — RETRO + RATCHET
   Audit seed citations, frontmatter validity
   Promote close-gate from SOFT → HARD per D10
   Open follow-up issue for next 15-20 seed candidates
```

**Migration of existing scattered artifacts:** Forward-only via disposition=improvement. When an issue's lookup notices "I'd cite this if it were canonical but it isn't", the disposition includes a migration sub-flag. Frequently-referenced legacy artifacts migrate organically over ~3-6 months.

### 5.2 — Supersession & lineage

**Append-only with bi-directional pointers:**

```
Older entry            Newer entry
────────────           ────────────
result_id: A           result_id: B
supersedes: []         supersedes: [A]
superseded_by: B  ⇄    superseded_by: null
status: superseded     status: current
```

Tier-3 lookup returns the entry with `superseded_by: null` as the current canonical. Older entries remain queryable for historical context.

**Supersession reasons** (recorded in `supersedes_reason`):

- `code-fix` → other entries from the same buggy code SHA should be re-run
- `method-change` → all entries under the method need re-evaluation
- `input-correction` → only this entry; no fan-out
- `precision-upgrade` → existing consumers can keep using A; new prefer B

`scripts/canonical-store/find-impacted.sh` prints fan-out lists for any supersession event.

**Lineage chain:** `supersedes` lists only direct predecessor. Query script walks `superseded_by` to find current head.

**Concept/Method-tier supersession:** Same model. Tier-1 rare; Tier-2 is the typical version-bump path. `method-registry.yaml`'s `current_version` always points to chain head; older versions readable by `method_version_at_run` pin.

### 5.3 — Code-version drift detection

```
For each Tier-3 result:
    stored_sha = entry.execution.code_sha
    sibling    = entry.execution.sibling
    current_HEAD = git -C ../<sibling> rev-parse HEAD

    if stored_sha == current_HEAD:
        status: IN_SYNC
    elif git log --oneline {stored_sha}..{current_HEAD} -- {module_path}:
        status: DRIFTED            # specific module touched
    else:
        status: SIBLING_ADVANCED   # sibling moved; this module untouched
```

Path-aware check is essential — otherwise every commit floods the drift report.

**Drift surfacing:** Nightly cron (`scripts/canonical-store/drift-check.sh`) emits `docs/reports/canonical-store-drift-YYYY-MM-DD.md`:

```
## Summary
Total Tier-3 entries: 142
  ├─ IN_SYNC:          87
  ├─ SIBLING_ADVANCED: 43
  └─ DRIFTED:          12   (re-verification candidates)
```

DRIFTED entries can be auto-templated into verification-disposition issues per D15.

**Policy thresholds:**

- DRIFTED count > 20 → auto-issue to canonical-store-maintenance GitHub project
- IN_SYNC ratio < 60% → systemic signal; surface to `feedback_n_night_blocker_promote_to_replan` for replan
- Per-method drift > 50% → flag for version-bump consideration

### 5.4 — Hit-rate metric (value curve)

`docs/reports/canonical-store-hit-rate-weekly.md` (auto-generated):

```yaml
week_of: 2026-05-22
queries_fired: 47
hits_total: 18
hits_by_tier:
  tier_1: 8
  tier_2: 12
  tier_3: 5
dispositions_by_hit:
  cite_and_stop: 7
  verification: 4
  improvement: 7
genuinely_new: 29
estimated_cycles_saved:
  cite_and_stop_savings: 7 × 4.2 ≈ 29 cycles
  verification_savings: 4 × 2.1 ≈ 8 cycles
  improvement_savings: 7 × 1.8 ≈ 13 cycles
  total_this_week: ~50 cycles
corpus_size:
  tier_1: 23
  tier_2: 19
  tier_3: 142
```

---

## Section 6 — Acceptance Criteria, Open Questions, Risks

### 6.1 Acceptance criteria (design-level)

- [ ] `config/canonical-store/` directory exists with: `layer-routing.yaml`, `method-registry.yaml`, `tier-schema/{concept,method,result,common-footer}.schema.json`, `domain-taxonomy.yaml`, `CHANGELOG.md`, `README.md`
- [ ] Five enforcement scripts under `scripts/enforcement/`: `check-canonical-lookup.sh`, `check-layer-manifest.sh`, `check-result-dedup.sh`, `check-supersedes-lineage.sh`, `check-wiki-promotion-landed.sh`
- [ ] Helper scripts under `scripts/canonical-store/`: `fingerprint.py`, `query.sh`, `resolve-method.py`, `promote-to-wiki.sh`, `drift-check.sh`, `find-impacted.sh`
- [ ] Rule + skill updates: `.claude/rules/canonical-store-contract.md`, `SHARED_SOUL.md` must-fire bullet, `issue-planning-mode/SKILL.md` Steps 2.5/3.1/8.1, `engineering-issue-workflow/SKILL.md` Step-6/7, `docs/plans/_template-issue-plan.md`, `docs/plans/README.md`
- [ ] Bootstrap seeds landed: 3 Tier-1 + 5 Tier-2 + ≥7 Tier-3 entries from #2685 + OCIMF + BSEE
- [ ] Code-side citation integration: `digitalmodel.citations.schema.Citation` extended; #2685 pilot emits extended sidecar; sidecars stage to `docs/sessions/<issue>/results/`
- [ ] Memory entries: `feedback_canonical_store_lookup_at_resource_intel`, `project_canonical_store_v1`, `reference_canonical_store_paths`
- [ ] Dashboards: `canonical-store-hit-rate-weekly.md` (weekly), `canonical-store-drift-YYYY-MM-DD.md` (nightly), `canonical-store-close-compliance.md` (weeks 1-4)
- [ ] E2E pilot: one issue per disposition (genuinely-new, verification, improvement) runs full workflow successfully

### 6.2 Open questions (deferred to implementation plan)

1. **Float-fingerprint tolerance.** Pick a cross-platform rounding policy; add regression test.
2. **`query.sh` indexing strategy.** Brute-force grep vs commit-hook index vs future MCP `wiki_search` ([#2400](https://github.com/vamseeachanta/workspace-hub/issues/2400)).
3. **Tier-2 method deprecation lifecycle.** How long old `current_version` overlaps with new.
4. **Hermes/Codex/Gemini retrieval path for `config/canonical-store/`.** Verify each provider; add to per-provider deltas if needed.
5. **Client-wiki cross-reference auth boundary.** Verify GitHub repo-visibility actually provides discoverability-without-exfiltration.
6. **Multi-implementation methods.** When multiple siblings implement the same `method_id`, which `code_sha` goes into the sidecar.
7. **CHANGELOG.md grooming.** Define exactly which edits are "formatting" (T1 allowed) vs "content" (T3 required).

### 6.3 Out of scope

- Federated cross-sibling search (`llm-wiki` ∪ `llm-wiki-<client>` ∪ `worldenergydata-wiki` in one query)
- Automated bulk migration of legacy wiki content
- Schema migration tooling (shape only mentioned; not specified)
- Custom auth model for client-wiki access (uses GitHub repo-visibility as-is)
- Result entries for ad-hoc bash queries / status reports (excluded by D2)
- Memory-bridge integration (covered by [#2775](https://github.com/vamseeachanta/workspace-hub/issues/2775))
- CAD-DEVELOPMENTS / cad-tooling integration (PAUSED per `project_cad_tooling_review`)

### 6.4 Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Bootstrap value curve too slow | Medium | High | Front-load seeds; weekly hit-rate; extend soft phase if <15% by week 3 |
| Schema thrash | Medium | Medium | Strict semver; migration scripts mandated for breaking changes; T3 on edits |
| Float-fingerprint cross-platform flakiness | Medium | High | §6.2 #1; regression test in implementation plan; CI on all 3 platforms |
| Registry single-point-of-failure | Low (T3 gated) | Critical | T3 review on edits; CHANGELOG audit; documented rollback |
| Sidecar staging orphans | High | Low | `/gsd:cleanup` skill handles |
| Method-registry sprawl | Low | Medium | §6.2 #2; split per-domain at ~200 methods |
| Cross-provider compliance divergence | Medium | High | `SHARED_SOUL.md` must-fire via `SOUL.runtime.md` build; weekly per-provider retro |
| Subagent Write phantom on sidecar | Medium | Medium | Main session `ls`-verifies sidecar per `feedback_subagent_write_phantom` |
| Registry retrieval cost | Low | Low | Files small (<50KB); revisit at ~500KB |

### 6.5 Workflow gate for this design itself

```
Design Doc (this artifact)
   ▼
GitHub Issue (filed: "feat(workflow): canonical anti-repetition surface — v1")
   ▼
Resource Intel (verifies #2778, #2775, #2744, #2685 references)
   ▼
Implementation Plan (uses CURRENT template; DECLARES new sections it will add)
   ▼
Adversarial Review T3 (auto-triggered: touches config/canonical-store/, SHARED_SOUL.md)
   ▼
status:plan-review → USER APPROVES → status:plan-approved
   ▼
Implementation (TDD per engineering-issue-workflow skill)
   ▼
Cross-Review T3 → Close → Wiki entries land
   (this design becomes its own first canonical entries —
    Tier-1 for the contract concept, Tier-2 for the implementation
    method, Tier-3 for the v1 result)
```

### 6.6 Dependencies and ordering

```
BEFORE this design's implementation can start:
   #2778 (wiki-sibling routing) — provides layer-routing.yaml seed content
   #2744 (llm-wiki-acma) — first client sibling; tests private-client-llm-wiki tier

IN PARALLEL with this design:
   #2775 (harness SSoT) — orthogonal layer; coordinates via SHARED_SOUL.md

AFTER this design (consumes it):
   #2400 (MCP wiki_search) — Section 4 retrieval pattern 1 calls it out
   Future: per-client sibling onboarding
   Future: federated cross-sibling search (out of scope per §6.3)
```

---

## Next Steps

1. User reviews this design document.
2. If approved, transition to `superpowers:writing-plans` skill to produce the implementation plan.
3. Implementation plan will be filed against a new GitHub issue and follow the existing AGENTS.md gate (the current template, since the new template lands as part of this design's implementation).
4. Per D13, implementation plan is auto-T3 review because it touches `config/canonical-store/` + `SHARED_SOUL.md`.
5. Per `feedback_never_offer_to_self_label_plan_approved` — user-in-loop approval is load-bearing; no self-approval at any gate.

---

## Provenance

- **Brainstorming session:** 2026-05-22, ~2 hours, interactive multi-choice + free-form
- **Decisions locked:** D1-D15 above; each captured at the point of user selection
- **References consulted during design:**
  - [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778) (wiki-sibling routing lock)
  - [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) (ACMA epic; comment locking suffix-form naming)
  - [#2775](https://github.com/vamseeachanta/workspace-hub/issues/2775) (harness SSoT)
  - [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) (calc-citation pilot LIVE)
  - `AGENTS.md` (current 20-line Hard Gates)
  - `docs/plans/_template-issue-plan.md` (current template)
  - `.claude/skills/coordination/issue-planning-mode/SKILL.md`
  - `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
  - `.claude/rules/calc-citation-contract.md`
  - `.claude/rules/codes-standards-data-routing.md`
  - `.claude/rules/patterns.md` (enforcement gradient)
  - `.claude/rules/coding-style.md` (20-line cap on AGENTS.md/CLAUDE.md)
  - `config/agents/SHARED_SOUL.md` (must-fire rules surface)
  - `docs/governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md` (sibling design precedent)
  - Memory: `feedback_superpowers_specs_gitignored`, `feedback_html_default_artifact`, `feedback_subagent_write_phantom`, `feedback_codex_sustained_major_loop`, `feedback_n_night_blocker_promote_to_replan`, `feedback_attestation_enables_contradiction_detection`
- **User motivation captured verbatim:**
  > "every data, every execution result, every result should be added to the llm-wiki (except client info). this information should be stored in a canonical form such that it handles the data inputs, analysis type and result such that.. we can look up the same class of result without repeating work; This will help QA new result, also not unnecessarily repeat work etc. Potentially maintaining the used execution code version and current code version etc."
  > "The motivation is a grand plan to not repeat work if we did it in the past, not repeat concepts if we did them before etc. We only improve and move forward."
  > "no wasted time, tokens, execution cycles etc."
