# Plan for #2136: Build Intelligence Accessibility Registry with Machine Reachability Metadata

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2136
> **Review artifacts:** scripts/review/results/2026-04-11-plan-2136-claude.md | scripts/review/results/2026-04-11-plan-2136-final.md

---

## Resource Intelligence Summary

### Existing registry/provenance assets consulted

| Asset | Path | What it tracks | Why it does NOT solve #2136 |
|---|---|---|---|
| Registry stats | `data/document-index/registry.yaml` | Aggregate document counts by source/domain/repo | Aggregate stats — no per-asset accessibility or reachability metadata |
| Standards transfer ledger | `data/document-index/standards-transfer-ledger.yaml` | 425 individual standards with id, org, domain, paths, status | Tracks documents within the intelligence ecosystem, not the intelligence assets themselves |
| Mounted source registry | `data/document-index/mounted-source-registry.yaml` | 8 source roots with mount paths and availability checks | Source-root level only — no per-asset query commands, agent entry points, or freshness indicators |
| Design code registry | `data/design-codes/code-registry.yaml` | ~30 design codes with edition tracking | Domain-specific (design codes only) — not a general intelligence asset registry |
| Corpus index | `data/document-index/index.jsonl` | 1,033,933 per-document records (path, SHA-256, size, ext, source) | Per-document L2 inventory — does not map intelligence surfaces like wikis, maps, or architecture docs |
| Online resource registry | `data/document-index/online-resource-registry.yaml` | 247 tracked online data sources | Tracks online sources, not the repo's own intelligence asset surfaces |
| Enhancement plan | `data/document-index/enhancement-plan.yaml` | 34,099 lines of domain classification + gap analysis output | Pipeline output — not an asset registry |

**Key finding:** No existing registry provides a unified machine-readable view of the intelligence assets themselves (wiki domains, architecture docs, maps, registries, seeds, entry points) with machine reachability, query commands, and freshness metadata. The closest human-readable equivalent is the accessibility map (#2096), which inventories 26+ assets across 3 discoverability tiers but is a markdown document, not a queryable data surface.

### Parent/sibling artifacts consulted

| Artifact | Issue | Status | Key takeaways for #2136 |
|---|---|---|---|
| Parent operating model | #2205 | Normative | L2 owns registry/provenance; L4 owns entry-point surfaces. #2136 sits at the L2/L4 boundary: structured registry data (L2) that feeds entry-point surfaces (L4). Section 7.4: "Machine reachability is explicit metadata, not an assumption. Each registry entry should record which machines/mounts can access the underlying source document (implementation details delegated to #2136)." Section 8: requires convergence on `doc_key`-based lookup but leaves file format/storage to #2136. |
| Provenance contract | #2207 | Normative | Defines `doc_key` (SHA-256 of source content) as canonical identity. #2136 must use `doc_key` where applicable (i.e., for assets that are individual files with computable hashes). For directory-level assets (wiki domains, `data/document-index/` directory), `doc_key` does not apply — these need an `asset_key` that complements but does not conflict with `doc_key`. Section 7.2: "whatever implementation is chosen: uses `doc_key` as the primary join key, supports the provenance fields, does not invent a parallel identity system." |
| Boundary policy | #2209 | Normative | Section 4.3: Registries at L2 are durable — entries persist as long as underlying source exists. The intelligence accessibility registry is itself a durable L2 artifact. |
| Accessibility map | #2096 | Normative | Section 5: inventories 26+ assets with discoverability ratings (Discoverable / Partially discoverable / Hard to discover). Section 9: explicitly delegates machine-readable registry to #2136. This map is the primary evidence source for seeding the registry. |
| Canonical entry points plan | #2104 | Plan-review | Designs three-tier L4 navigation. Section on boundaries: "Machine-readable registry schema, `doc_key` lookup interface, machine-reachability metadata, programmatic access API" is #2136 scope. The entry-point pages will link to the registry but do not define its schema. |
| Workflow retrieval contract | #2208 | Not yet planned | Defines how L5 execution state (issues, plans) programmatically consumes L2/L3 intelligence. #2136 provides the lookup surface; #2208 defines the consumption protocol. |
| Weekly review template | #2089 | Draft | Section D (Intelligence Accessibility) needs a machine-queryable surface for automated checks. The #2136 registry is the data source that Section D queries will consume. |

### LLM Wiki pages consulted

- No existing wiki pages directly address the intelligence accessibility registry concept.
- `knowledge/wikis/engineering/wiki/index.md` — verified as one of the assets to be registered.

### Gaps identified

1. **No meta-registry exists.** The repo has registries for documents, standards, design codes, and source mounts — but no registry of the intelligence assets themselves (wiki domains, architecture docs, maps, registries, entry points, seeds).
2. **Machine reachability is implicit.** The mounted-source-registry records source roots with mount paths but does not indicate which machines can access which intelligence assets. The parent model (#2205 Section 7.4) explicitly requires this as metadata.
3. **No query entry points recorded.** There is no machine-readable surface recording how to programmatically access each intelligence asset (e.g., `yq '.codes[]' data/design-codes/code-registry.yaml` or `grep -c '' knowledge/wikis/engineering/wiki/index.md`).
4. **No freshness source recorded.** The `resource-intelligence-maturity.yaml` tracks maturity metrics but there is no per-asset freshness indicator or mechanism.
5. **Accessibility map is human-readable only.** The #2096 map contains the inventory but in markdown table format — not queryable by scripts or agents.
6. **No `asset_key` convention.** The `doc_key` (SHA-256) is defined for individual documents but there is no identity convention for intelligence assets that are directories, YAML files, or collections.

---

## Proposed Registry Role and Scope Boundaries

### What the intelligence accessibility registry IS

A **single machine-readable YAML file** that inventories the major intelligence assets in the workspace-hub ecosystem. Each entry records:

- What the asset is (identity, type, layer)
- Where it lives (canonical path)
- How to access it (human entry point, agent entry point, query command)
- Who can reach it (machine reachability)
- How to check if it is current (freshness source)
- Who owns it (responsible issue or role)

The registry operates at the **meta level**: it registers intelligence surfaces (wiki domains, registries, maps, architecture docs, seeds), not individual documents within those surfaces. Individual documents are tracked by `index.jsonl` and `standards-transfer-ledger.yaml`.

### What the registry is NOT

| NOT this | Why | Owner |
|---|---|---|
| A replacement for `index.jsonl` or `standards-transfer-ledger.yaml` | Those track individual documents at L2; this tracks intelligence surfaces | Existing L2 infrastructure |
| A navigation page or entry-point design | Navigation is L4 markdown surfaces; this is L2 structured data | #2104 |
| A workflow retrieval contract | How issues consume intelligence is a protocol, not a registry | #2208 |
| A conformance checker | Validation scripts that check registry health are a separate concern | #2206 |
| A `doc_key` lookup service | The registry may reference `doc_key` values but does not implement document-level identity resolution | #2207 |
| A per-document reachability tracker | Per-document path aliasing is handled by `provenance.py` and `index.jsonl` | #2207 |

### Layer classification

The registry file lives at **L2 (Registry/provenance)**: it is structured, durable, machine-readable inventory data. It feeds L4 entry-point surfaces (the markdown navigation pages designed by #2104) and L5 weekly review checks (Section D of #2089).

### Relationship to existing registries

| Existing registry | Relationship to #2136 registry |
|---|---|
| `data/document-index/registry.yaml` | The #2136 registry will have a row pointing to `registry.yaml` as an intelligence asset. The two are at different abstraction levels: `registry.yaml` tracks document aggregates; #2136 tracks the asset surfaces. |
| `standards-transfer-ledger.yaml` | Same: the ledger is one of the intelligence assets registered in the #2136 registry. |
| `mounted-source-registry.yaml` | The mounted-source-registry tracks source roots. The #2136 registry tracks intelligence assets. Source roots are one input to machine-reachability metadata, but the two serve different purposes. |
| `code-registry.yaml` | Same as ledger: a domain-specific intelligence asset that gets a row in the #2136 registry. |

### Scope boundary with `doc_key`

The `doc_key` (SHA-256 of file content) is the canonical identity for individual source documents (#2207). The intelligence accessibility registry tracks assets at a higher abstraction level — directories, collections, YAML files that are regularly updated. For these:

- **Single-file assets** (e.g., `code-registry.yaml`): may optionally record a `doc_key` for content verification, but the `doc_key` changes every time the file is updated, so it is not a stable identity. The `asset_key` is the stable identity.
- **Directory assets** (e.g., `knowledge/wikis/engineering/wiki/`): `doc_key` does not apply. Identity is by `asset_key` (a human-readable slug).
- **No conflict with #2207**: the `asset_key` is a registry-internal identifier for intelligence surfaces. It complements `doc_key` (which identifies individual source documents) without creating a parallel document identity system.

---

## Proposed Minimum Field Set and Validation Expectations

### Required fields (every row must have these)

| Field | Type | Description | Source today |
|---|---|---|---|
| `asset_key` | string (slug) | Unique identifier for the intelligence asset. Human-readable slug (e.g., `wiki-engineering`, `registry-standards-transfer-ledger`). Convention: `<type>-<short-name>`. | New — must be defined per asset |
| `title` | string | Human-readable display name | From existing docs / file headers |
| `asset_type` | enum | One of: `wiki`, `registry`, `ledger`, `map`, `architecture-doc`, `entry-point`, `seed`, `governance-doc`, `operational-template` | New — classification per #2205 layer model |
| `layer` | enum | Pyramid layer: `L1`, `L2`, `L3`, `L3-adjacent`, `L4`, `L5`, `L6`, `recurring-operational` | From #2205 / #2096 classification |
| `canonical_path` | string | Primary file or directory path relative to repo root | From existing file locations |
| `human_entry_point` | string or null | How a human discovers this asset (e.g., `docs/README.md > Quick Links`, `docs/document-intelligence/README.md`) | From #2096 accessibility map |
| `agent_entry_point` | string or null | How an agent discovers this asset (e.g., `knowledge/wikis/engineering/CLAUDE.md`, `AGENTS.md > docs/README.md`) | From existing CLAUDE.md files / control-plane contract |
| `machine_scope` | list[string] | Machines where this asset is accessible. Values: `all-git-clones` (git-tracked, always available), `ace-linux-1`, `ace-linux-2`, `dev-secondary`, etc. | From `mounted-source-registry.yaml` + knowledge of mount points |
| `source_of_truth_tier` | enum | One of: `git-tracked`, `shared-mount`, `local-cache` (per #2205 Section 7) | From file location and tracking method |
| `durability` | enum | One of: `durable`, `transient`, `recurring-operational` (per #2209) | From #2209 classification |

### Recommended extended fields (populated when available)

| Field | Type | Description | Source today |
|---|---|---|---|
| `query_command` | string or null | Programmatic query to extract key content (e.g., `yq '.codes[]' data/design-codes/code-registry.yaml`) | New — must be defined per asset |
| `freshness_source` | string or null | How to check if the asset is current (e.g., `generated` field in YAML header, `git log -1 --format=%ci <path>`, file mtime) | From file format / existing `generated` fields |
| `freshness_cadence` | string or null | Expected update frequency (e.g., `weekly`, `monthly`, `on-demand`, `continuous`) | From known pipeline/process schedules |
| `record_count` | integer or null | Number of records/pages/entries (for inventoried assets) | From #2096 inventory or file headers |
| `owner_issue` | string or null | GitHub issue responsible for this asset's lifecycle | From #2205 issue tree |
| `discoverability` | enum or null | Current rating: `discoverable`, `partially-discoverable`, `hard-to-discover` | From #2096 Section 5 |
| `gaps` | string or null | Known accessibility gaps (free text, from #2096 Section 6) | From #2096 gap analysis |
| `depends_on` | list[string] or null | Other `asset_key` values this asset depends on | From dependency analysis |

### Validation expectations

| Check | Rule | Enforcement |
|---|---|---|
| `asset_key` uniqueness | No duplicate `asset_key` values in the registry | Schema validation script (future #2206) |
| Required fields present | Every row has all required fields non-null (except `human_entry_point` and `agent_entry_point` which may be null if not yet established) | Schema validation script |
| `canonical_path` exists | The path points to an existing file or directory in the repo | File-existence check (future #2206 or weekly review) |
| `layer` consistency | Layer values match #2205 pyramid definitions | Manual review + conformance check |
| `machine_scope` validity | Machine names come from a controlled vocabulary matching `mounted-source-registry.yaml` source_ids or known machine hostnames | Schema validation |
| `asset_type` validity | Only recognized enum values | Schema validation |
| No orphan entries | Every registered asset still exists; every major asset from #2096 inventory is registered | Bidirectional coverage check |

---

## Seeding Strategy for Major Intelligence Assets

### Phase 1: Seed from #2096 accessibility map (initial population)

The #2096 accessibility map (Section 5) inventories 26+ assets across 6 classes. These are the first entries:

**Wiki assets (L3):**
- `wiki-engineering` — `knowledge/wikis/engineering/wiki/` (~78 pages)
- `wiki-marine-engineering` — `knowledge/wikis/marine-engineering/wiki/` (~19,168 pages)
- `wiki-maritime-law` — `knowledge/wikis/maritime-law/wiki/` (~22 pages)
- `wiki-naval-architecture` — `knowledge/wikis/naval-architecture/wiki/` (~45 pages)
- `wiki-personal` — `knowledge/wikis/personal/wiki/` (~5 pages)
- `wiki-cross-links` — `knowledge/wikis/cross-links.md` (25 links)
- `seeds-knowledge` — `knowledge/seeds/` (6 seed files)

**Registry / provenance assets (L2):**
- `registry-corpus-index` — `data/document-index/index.jsonl` (~1,033,933 records)
- `registry-aggregate-stats` — `data/document-index/registry.yaml`
- `ledger-standards-transfer` — `data/document-index/standards-transfer-ledger.yaml` (425 standards)
- `registry-mounted-sources` — `data/document-index/mounted-source-registry.yaml` (8 sources)
- `registry-design-codes` — `data/design-codes/code-registry.yaml` (~30 codes)
- `registry-online-resources` — `data/document-index/online-resource-registry.yaml` (247 resources)
- `registry-summaries` — `data/document-index/summaries/` (~639,585 files)
- `registry-enhancement-plan` — `data/document-index/enhancement-plan.yaml` (34,099 lines)
- `registry-conference` — `data/document-index/conference-*.yaml` (multiple files)
- `registry-resource-maturity` — `data/document-index/resource-intelligence-maturity.yaml`

**Architecture docs (L3-adjacent normative):**
- `arch-operating-model` — `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `arch-provenance-contract` — `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `arch-boundary-policy` — `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`

**Maps and inventories (L4):**
- `map-accessibility` — `docs/document-intelligence/intelligence-accessibility-map.md`
- `map-data-intelligence` — `docs/document-intelligence/data-intelligence-map.md`
- `map-engineering-docs` — `docs/document-intelligence/engineering-documentation-map.md`
- `map-domain-coverage` — `docs/document-intelligence/domain-coverage.md`
- `map-mount-drive` — `docs/document-intelligence/mount-drive-knowledge-map.md`

**Operational / governance (recurring-operational / governance):**
- `template-weekly-review` — `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`

### Phase 2: Extend as new assets are created

As #2104 implementation creates new entry-point pages (e.g., `docs/document-intelligence/README.md`), they are added to the registry. Same for future wiki domains, new registries, or promoted intelligence surfaces.

### Seeding method

The initial seed is a manual YAML file authored from the #2096 inventory with machine-reachability metadata added by consulting `mounted-source-registry.yaml` and known machine configurations. Future entries are added manually or by a registration script (out of scope for initial implementation).

---

## What Should Remain Out of Scope

| Concern | Why out of scope | Owner |
|---|---|---|
| Individual document lookup by `doc_key` | The registry tracks intelligence surfaces, not individual documents. `doc_key` lookup is the concern of `index.jsonl` and `provenance.py`. | #2207, existing infrastructure |
| Entry-point page design and creation | The registry provides data; the navigation pages are #2104's deliverable | #2104 |
| Workflow retrieval hooks | How issue planning/execution consumes the registry is a protocol definition | #2208 |
| Conformance validation scripts | Scripts that validate registry schema completeness and file-existence are a #2206 deliverable | #2206 |
| Automated freshness checking | Scripts that query `freshness_source` and report staleness belong to weekly review automation | #2089 |
| Per-document reachability tracking | Per-document path aliasing across machines is `provenance.py`'s concern | #2207 |
| Registry query CLI or API | A programmatic query interface (beyond `yq` on the YAML file) is future work if warranted by scale | Future issue |

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md` |
| Plan review — Claude | `scripts/review/results/2026-04-11-plan-2136-claude.md` |
| Plan review — Final | `scripts/review/results/2026-04-11-plan-2136-final.md` |
| **Implementation targets (deferred):** | |
| Intelligence accessibility registry | `data/document-index/intelligence-accessibility-registry.yaml` — new file |
| Registry schema validation script | `scripts/data/document-index/validate-accessibility-registry.py` — new file |
| Weekly review integration | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — add registry-based checks to Section D |
| Plan index update | `docs/plans/README.md` — add this plan to index |

---

## Deliverable

A machine-readable intelligence accessibility registry (`data/document-index/intelligence-accessibility-registry.yaml`) that inventories the major intelligence assets in the workspace-hub ecosystem, including canonical paths, human and agent entry points, query commands, machine reachability metadata, and freshness indicators — seeded from the #2096 accessibility map inventory and validated by a schema-completeness script.

---

## Pseudocode / Registry-Assembly Logic Sketch

### Registry file structure

```yaml
# intelligence-accessibility-registry.yaml
generated: '2026-MM-DD'
schema_version: '1.0.0'
description: >
  Machine-readable inventory of intelligence assets in the workspace-hub
  ecosystem. Each entry records what the asset is, where it lives, how to
  access it, which machines can reach it, and how to check if it is current.
  Governed by #2205 (parent operating model). Identity for individual
  documents uses doc_key per #2207; this registry uses asset_key for
  intelligence surfaces.

assets:
  - asset_key: wiki-engineering
    title: Engineering LLM Wiki
    asset_type: wiki
    layer: L3
    canonical_path: knowledge/wikis/engineering/wiki/
    human_entry_point: knowledge/wikis/engineering/wiki/index.md
    agent_entry_point: knowledge/wikis/engineering/CLAUDE.md
    query_command: null  # directory-level; use wiki/index.md for navigation
    machine_scope: [all-git-clones]
    source_of_truth_tier: git-tracked
    durability: durable
    freshness_source: "git log -1 --format=%ci knowledge/wikis/engineering/wiki/"
    freshness_cadence: on-demand
    record_count: 78
    owner_issue: null
    discoverability: discoverable
    gaps: "Not linked from docs/README.md; no mention in capabilities summary"

  - asset_key: ledger-standards-transfer
    title: Standards Transfer Ledger
    asset_type: ledger
    layer: L2
    canonical_path: data/document-index/standards-transfer-ledger.yaml
    human_entry_point: docs/document-intelligence/data-intelligence-map.md
    agent_entry_point: null  # no agent-specific entry point
    query_command: "yq '.standards[] | select(.status == \"gap\")' data/document-index/standards-transfer-ledger.yaml"
    machine_scope: [all-git-clones]
    source_of_truth_tier: git-tracked
    durability: durable
    freshness_source: ".generated field in YAML header"
    freshness_cadence: monthly
    record_count: 425
    owner_issue: null
    discoverability: partially-discoverable
    gaps: "Referenced in data-intelligence-map but not from docs/README.md"

  # ... ~25 more entries seeded from #2096 inventory
```

### Schema validation logic sketch

```
function validate_registry(registry_path):
    load registry YAML
    for each asset in registry.assets:
        assert asset_key is unique
        assert asset_key matches pattern: lowercase-alphanumeric-with-hyphens
        assert title is non-empty string
        assert asset_type in VALID_ASSET_TYPES
        assert layer in VALID_LAYERS
        assert canonical_path is non-empty string
        assert machine_scope is non-empty list
        assert source_of_truth_tier in VALID_TIERS
        assert durability in VALID_DURABILITIES
        if canonical_path is file:
            assert file exists at canonical_path
        elif canonical_path is directory:
            assert directory exists at canonical_path
    report: total assets, missing optional fields, file-existence failures
```

### Weekly review integration sketch

```
# Section D enhancement: query registry for automated accessibility checks
function weekly_accessibility_check():
    load intelligence-accessibility-registry.yaml
    for each asset where machine_scope includes current_machine:
        check canonical_path exists
        if freshness_source is not null:
            check freshness within expected cadence
        report: asset_key, status (ok / missing / stale)
    for each asset where discoverability != 'discoverable':
        flag: asset_key still has known accessibility gaps
```

---

## Files to Change (Planning Scope Only)

These are the implementation targets. **None of these changes should be made during planning.**

| Action | Path | Reason |
|---|---|---|
| **Create** | `data/document-index/intelligence-accessibility-registry.yaml` | The registry itself — seeded with ~26 entries from #2096 inventory |
| **Create** | `scripts/data/document-index/validate-accessibility-registry.py` | Schema validation script for registry health |
| **Modify** | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Add registry-based checks to Section D |
| **Update** | `docs/plans/README.md` | Add this plan to index |

### Likely future implementation surfaces (separate from this issue)

| Surface | Owner issue | Relationship |
|---|---|---|
| Entry-point pages that link to the registry | #2104 | Navigation pages reference registry entries |
| Conformance checks against registry | #2206 | Validation scripts query registry for completeness |
| Workflow retrieval hooks consuming registry | #2208 | Issue workflows look up intelligence assets via registry |
| Weekly review automation using registry | #2089 | Section D checks become automated against registry data |
| Registry query CLI (if warranted by scale) | Future issue | Programmatic access beyond `yq` on YAML |

---

## TDD / Verification List for Future Implementation

| Test name | What it verifies | Method |
|---|---|---|
| `test_registry_file_exists` | Registry file is present at expected path | File existence check |
| `test_registry_yaml_valid` | Registry file parses as valid YAML | `yq` or Python `yaml.safe_load()` |
| `test_asset_keys_unique` | No duplicate `asset_key` values | Collect keys, check set length == list length |
| `test_required_fields_present` | Every entry has all required fields non-null | Iterate entries, check field presence |
| `test_canonical_paths_exist` | Every `canonical_path` resolves to an existing file or directory | `os.path.exists()` for each |
| `test_asset_type_valid` | Every `asset_type` is in the controlled vocabulary | Set membership check |
| `test_layer_valid` | Every `layer` is in the controlled vocabulary | Set membership check |
| `test_machine_scope_valid` | Every `machine_scope` list contains valid machine identifiers | Set membership against controlled vocabulary |
| `test_source_of_truth_tier_valid` | Every `source_of_truth_tier` is valid | Enum check |
| `test_durability_valid` | Every `durability` is valid | Enum check |
| `test_coverage_vs_2096_inventory` | Major assets from #2096 accessibility map are represented | Compare asset list against #2096 Section 5 inventory |
| `test_no_provenance_invention` | Registry entries do not invent `doc_key` values or provenance claims not backed by L2 | Manual review / automated check for `doc_key` field absence unless backed by `index.jsonl` |

---

## Acceptance Criteria

- [ ] `data/document-index/intelligence-accessibility-registry.yaml` exists with ≥25 entries seeded from #2096 inventory
- [ ] Every entry has all required fields: `asset_key`, `title`, `asset_type`, `layer`, `canonical_path`, `machine_scope`, `source_of_truth_tier`, `durability`
- [ ] `asset_key` values are unique, human-readable slugs following `<type>-<short-name>` convention
- [ ] `machine_scope` accurately reflects which machines can access each asset (based on `mounted-source-registry.yaml` and known configurations)
- [ ] `canonical_path` values resolve to existing files/directories in the repo
- [ ] Schema validation script (`validate-accessibility-registry.py`) passes with zero errors
- [ ] No `doc_key` values are invented by the registry — `doc_key` references only appear if backed by existing `index.jsonl` or `standards-transfer-ledger.yaml` entries
- [ ] Registry does not duplicate the concerns of `registry.yaml`, `standards-transfer-ledger.yaml`, or `mounted-source-registry.yaml`
- [ ] Weekly review template Section D references the registry as a data source for automated checks
- [ ] `docs/plans/README.md` updated with this plan's index entry
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-review) | APPROVE with MINOR notes | See `scripts/review/results/2026-04-11-plan-2136-claude.md` |

**Overall result:** PASS — plan is review-ready

Revisions made based on review:
- Strengthened `asset_key` vs `doc_key` boundary explanation to prevent identity system confusion
- Added explicit "what should remain out of scope" section to prevent scope creep into #2104/#2208
- Clarified that `machine_scope: [all-git-clones]` is the default for git-tracked assets
- Added `test_no_provenance_invention` to TDD list
- Clarified seeding strategy is from #2096 inventory, not from scratch enumeration

---

## Risks and Open Questions

1. **Risk: Registry staleness.** The registry is a manually maintained YAML file. If assets are added or removed without updating the registry, it drifts. Mitigation: the validation script checks `canonical_path` existence, and the weekly review Section D will flag missing files.

2. **Risk: `asset_key` naming convention may not be immediately obvious.** The `<type>-<short-name>` convention is ad-hoc. Mitigation: document the convention in the registry file header; keep names consistent with existing file naming patterns.

3. **Risk: Machine reachability data may be incomplete.** The current `mounted-source-registry.yaml` has 8 sources but doesn't exhaustively map machine-to-asset availability. Mitigation: start with `all-git-clones` as the default for git-tracked assets (which covers ~80% of entries) and incrementally add machine-specific entries for mounted sources.

4. **Open: Should the registry file live at `data/document-index/intelligence-accessibility-registry.yaml` or elsewhere?** Rationale for `data/document-index/`: this is the existing home for registry/ledger YAML files. Alternative: `data/intelligence-registry.yaml` at the top level. Recommendation: `data/document-index/` for consistency with existing registries.

5. **Open: Should `query_command` be a shell command string or a structured object?** A string is simpler but less portable. A structured object `{tool: yq, args: [...]}` is more robust but more complex. Recommendation: start with string for simplicity; migrate to structured if multi-tool queries become common.

6. **Open: Unified registry convergence (#2205 Section 12, question 1).** The parent model asks whether #2207 and #2136 converge on a single file or federated lookup. This plan recommends **federation**: the intelligence accessibility registry is a separate file that complements (not merges with) existing registries. Each registry serves a distinct purpose at a distinct abstraction level. Convergence happens via `doc_key` as the join key for document-level lookups, and `asset_key` for surface-level lookups.

7. **Boundary: #2104 and #2208.** This plan does NOT design the navigation pages (#2104) or the issue-workflow retrieval protocol (#2208). The registry is the data source; those issues are the consumers. This boundary is explicit and should remain so.

8. **Boundary: Conformance checks (#2206).** The validation script in this plan is a basic schema-completeness checker. Full conformance validation (checking that the registry's claims match the parent model, provenance contract, and boundary policy) is #2206's scope.

---

## Complexity: T2

**T2** — New registry YAML file, one validation script, one template modification. Multiple files but straightforward schema design with clear precedent from existing registries. Not T1 because it requires careful field design grounded in 5+ upstream artifacts. Not T3 because it does not involve multi-module code architecture or complex data flows.
