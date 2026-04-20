# Standards/Codes Provenance + Reuse Contract

> **Issue:** [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207)
> **Parent:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — LLM-Wiki + Resource/Document Intelligence Operating Model
> **Status:** Normative — approved provenance and reuse contract for standards/codes
> **Date:** 2026-04-11 (revised 2026-04-19)
> **Scope:** Contract only. Implementation delegated to follow-on issues.
> **Revision 2026-04-19:** Realigns this contract with (a) the 2026-04-19 amendments to the parent operating model (Sections 2, 3, 8.1) and (b) the 11 findings from the 2026-04-17 cross-provider (Claude + Codex) adversarial review. See Section 12 (Revision history) for the full disposition table.

---

## 1. Purpose and Scope

### What this document defines

This is the **provenance and reuse contract** for standards/codes artifacts within the workspace-hub intelligence ecosystem. It establishes:

- The canonical identity model for source documents (`doc_key` definition and implementation mapping)
- Required provenance fields at each pyramid layer
- Decision rules for when existing document-intelligence outputs can be reused versus when raw documents must be reparsed
- The promotion path from document-intelligence outputs into LLM-wiki records
- Anti-patterns that create duplicate parsing, broken lineage, or identity conflicts
- Likely implementation surfaces for follow-on work

### What this document does NOT define

| Out of scope | Owner |
|---|---|
| The parent pyramid model, layer ownership, or information flow rules | #2205 (parent operating model) |
| Conformance validation scripts or linters | #2206 |
| Retrieval contract for issue workflows | #2208 |
| Durable-vs-transient boundary policy | #2209 |
| Unified registry file format or query interface | #2136 |
| L3 wiki-page frontmatter **binding** schema for any wiki domain | The per-wiki `CLAUDE.md` file (parent Section 8.1). This contract may *recommend* fields on top of the parent-mandated baseline floor; it may not bind. |

This contract specializes the parent model for provenance and reuse. It does not redefine it.

---

## 2. Relationship to Parent Operating Model (#2205)

This document inherits from the [parent operating model](llm-wiki-resource-doc-intelligence-operating-model.md) (including the 2026-04-19 amendments to Sections 2, 3, and 8.1 — see [#2205 amendment comment](https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277238819)) and operates under its constraints:

| Parent rule | How this contract applies it |
|---|---|
| **Single-source-of-truth pyramid** (parent Section 2) | Provenance fields are owned by L2 (Registry/provenance). Wiki entries at L3 inherit provenance from L2; they do not create it. |
| **Most-durable-owner rule** (parent Section 2, amended 2026-04-19) | This contract itself is an L3 normative-architecture artifact per the worked-examples table. It does not describe itself as "L3-adjacent" or "between layers." |
| **`doc_key` rule** (parent Section 3, amended 2026-04-19) | This contract defines how live identity fields (`content_hash`, `sha`, `sha256`, `checksum`) map to the canonical `<algorithm>:<hex>` form, including `sha256:` (canonical) and `md5:` (legacy, read-only) namespaces. |
| **Status vocabulary** (parent Section 3, amended 2026-04-19) | This contract adopts the parent superset `gap | indexed | summarized | extracted | promoted | superseded | unreachable` verbatim. It may scope which values apply in this contract's decision tree; it may not redefine values or invent new ones. |
| **`merged_at` field** (parent Section 3, amended 2026-04-19) | This contract uses `merged_at` in all new references, treats `discovered` as a legacy read-time synonym, and does not redefine its semantic. |
| **L3 frontmatter schema authority** (parent Section 8.1, added 2026-04-19) | This contract recommends additional fields layered on top of the parent baseline floor (`title`, `last_updated`, `doc_key`). Binding happens in the relevant wiki `CLAUDE.md`, not here. |
| **Allowed information flows** (parent Section 4) | Reuse rules follow L2→L3 promotion flow. Reparsing falls back to L1→L2 indexing flow. |
| **Forbidden flows** (parent Section 5) | Reuse rules enforce the prohibition on L3 reparsing raw documents when L2 evidence is sufficient. |
| **Cross-machine access model** (parent Section 7) | Provenance fields must support multi-machine path aliasing. |
| **Unified artifact registry** (parent Section 8) | This contract defines provenance field requirements compatible with a `doc_key`-based registry. |
| **Child issue guardrails** (parent Section 10) | This contract does NOT redefine parent layer boundaries, ownership model, or workflow policy. |

### Conflict resolution

If this contract is found to conflict with the parent operating model, the parent takes precedence. Conflicts must be documented as comments on #2205 with a proposed amendment before any deviation.

---

## 3. Canonical Identity Model

### 3.1 The `doc_key` definition

The canonical identity of any source document is **content-based**. Per the parent operating model (Section 3, amended 2026-04-19), the `doc_key` has the form:

```
<algorithm>:<hex>
```

where `<algorithm>` is a hash-function identifier and `<hex>` is the hex-encoded digest.

**Permitted algorithm namespaces (normative, inherited from parent Section 3):**

| Namespace | Status | Permitted writers | Source of truth for behavior |
|---|---|---|---|
| `sha256:` | **Canonical** | All new writers | Required for any new `doc_key` written after 2026-04-19. |
| `md5:` | **Legacy, read-only** | `og_standards` legacy index entries only | Actively emitted by `scripts/data/document-index/phase-a-index.py:135-139` for 32-char inputs on that source. Permitted indefinitely for reads; no hard sunset. |

Bare-hex (no prefix) is a violation. When encountered, readers treat it as `sha256:` for compatibility **and emit a conformance warning** (check delegated to #2206).

**Mapping from existing codebase terms to the `<algorithm>:<hex>` form:**

| Existing term | Where used | Relationship to `doc_key` |
|---|---|---|
| `content_hash` | `index.jsonl` records, `config.yaml` (`primary_key: content_hash`), `provenance.py` dedup key | **The field carrying a `doc_key` value.** Live values are namespaced (`sha256:` or `md5:`) per `phase-a-index.py:135-139`. The field name `content_hash` is preserved for backward compatibility; semantically it is `doc_key`. |
| `sha` / `sha256` | Shard files (`"sha": "sha256:..."` prefix), summary file paths (`summaries/sha256:<hex>.json`) | A `doc_key` value in `sha256:<hex>` form. **Do not strip the prefix for identity comparison — strip only for display.** |
| `checksum` | `doc_intelligence/schema.py` (`DocumentMetadata.checksum`), `index_builder.py` manifest-index | SHA-256 of the source file. Equivalent to `doc_key` in `sha256:<hex>` form for that file. Used in extraction manifests for incremental-build change detection. |
| `content_hash()` function | `doc_intelligence/promoters/text_utils.py` | **NOT a `doc_key`.** This hashes the promoted *output content*, not the source document. It is a content-integrity stamp for promoted artifacts, not a document identity. See Section 8.3. |

### 3.2 Identity comparison rules

When comparing two identity values for equality:

1. **Namespaces must match.** A `sha256:` value and an `md5:` value for the same underlying document are **different identities** (different hash algorithms, different collision surfaces). They may be linked by provenance lineage, but they must not be joined by stripping prefixes and comparing bare hex.
2. **Bare-hex is not canonical.** Legacy code that stripped `sha256:` prefixes and compared bare hex is defect-prone under mixed-namespace data and must be reworked to compare the full `<algorithm>:<hex>` string.
3. **Case-insensitive hex is safe.** Hex digests are case-insensitive; normalize to lowercase for comparison.

### 3.3 Alias paths and machine-specific paths

File paths are **aliases**, not identity. The same document may appear at multiple locations:

```
doc_key: sha256:a1b2c3d4...
  paths:
    - /mnt/ace/0000 O&G/0000 Codes & Standards/Spare/API Stds/API/API RP 1111 (1999).pdf
    - /mnt/ace/0000 O&G/0000 Codes & Standards/unsorted/API RP 1111 4th Ed (2009)...pdf
    - /mnt/remote/dev-secondary/dde/0000 O&G/.../API RP 1111.pdf
```

This is already the behavior in `provenance.py`, which merges duplicate records by `content_hash` into a single entry with a `provenance` array tracking every location. The `standards-transfer-ledger.yaml` supports this via `doc_paths: [...]` arrays.

**Rules:**

- Path changes (rename, mount migration) do NOT change the `doc_key`.
- If a document's content is modified, it becomes a **new `doc_key`**. The old and new keys may be linked via provenance lineage (`absorbed_into`, `superseded_by`) but are distinct documents.
- Every known path for a document is recorded as an alias with machine/host metadata.

### 3.4 Revision / new-doc-key rule

When does a document get a new `doc_key`?

| Scenario | New `doc_key`? | Rationale |
|---|---|---|
| File copied to a different path or machine | No | Same content, same identity |
| File renamed without content change | No | Path is an alias |
| Document content updated (new edition, erratum) | **Yes** | Different content = different identity |
| OCR re-extraction emits a **sidecar** text artifact (source PDF untouched) | **No** | The source file bytes are unchanged. OCR output is a derived artifact. |
| OCR re-saves the PDF with an added text layer (e.g., `ocrmypdf --output-type pdf`) producing new file bytes | **Yes** | File bytes changed, so `doc_key` changes. Link the new `doc_key` to the prior one via `superseded_by` (or equivalent `ocr_derived_from`) in provenance lineage. |
| PDF re-saved with different metadata but identical visible content | **Yes** | The `doc_key` is computed from file bytes. A re-save that changes metadata changes the hash. Link via `superseded_by` if the visible content is equivalent. |

---

## 4. Required Provenance Fields

### 4.1 Minimum required fields

Every tracked document in the intelligence ecosystem must have these fields in its registry/index entry:

| Field | Type | Description | Owner layer |
|---|---|---|---|
| `doc_key` | string (`<algorithm>:<hex>` per Section 3.1) | Content-based canonical identity. Live records store this in the `content_hash` field; new writers emit the full `<algorithm>:<hex>` form verbatim. | L2 |
| `source` | string | Source bucket identifier (e.g., `og_standards`, `ace_standards`, `ace_project`). | L2 |
| `path` | string | A file path where this `doc_key` is reachable **on the recording host**. Machine-local by nature — see Section 4.1.1. | L2 |
| `host` | string | Machine/host where this `path` is valid. Binds `path` into a reachable pair. | L2 |
| `merged_at` | ISO 8601 UTC timestamp | When this provenance record was appended to the document's `provenance[]` array (per parent Section 3). Immutable per individual provenance record. See Section 4.1.2. | L2 |
| `processing_status` | enum (see Section 4.1.3) | Processing lifecycle state. **Field name `processing_status` is normative in this contract** to disambiguate from unrelated `status` fields elsewhere in the repo (e.g., classification status, ledger status). Live writers may keep emitting `status` for backward compatibility; readers must treat the field as processing-lifecycle only when the surface is one of those enumerated in Section 4.1.3. | L2 |

#### 4.1.1 Scope of the `path` field (resolves F5)

"Primary path" is not a global concept. When the same `doc_key` is reachable at different paths on different hosts:

- The `(path, host)` pair in the top-level entry is **machine-local**: it records the path preferred by whatever process wrote or last updated the entry.
- The authoritative cross-machine list lives in `provenance[]` (an array of `{source, path, host, merged_at, …}` entries).
- Cross-machine normalization (choosing a canonical path for display, resolving aliases) is delegated to #2136 (accessibility registry). This contract does not define a global "primary path" selection rule.

Readers that need a specific path for a given host should traverse `provenance[]` and filter by `host`; they must not assume the top-level `(path, host)` is the answer.

#### 4.1.2 `merged_at` semantic (resolves C4)

- `merged_at` is stamped by `provenance.py` when a provenance record is first appended to a document's `provenance[]` array.
- It is **not** a "first-indexed-anywhere" timestamp. `provenance.py` stamps `datetime.now(timezone.utc)` at merge time when no upstream value is present; since most Phase-A writers do not pre-populate this field, the effective value is merge-time (verified 2026-04-19 at `scripts/data/document-index/provenance.py:82`).
- Each individual provenance-array entry is immutable — once stamped, `merged_at` on that entry does not change even if the array is re-merged against new records.
- Readers MUST accept both `merged_at` (new) and `discovered` (legacy) field names. When both are present, prefer `merged_at`.
- Writers that require "true first-indexed-anywhere" semantics MUST add a new field `first_indexed_at` (not defined in this contract; parent Section 3 declines to require it at this time). Do not overload `merged_at`.

#### 4.1.3 `processing_status` enum (resolves F1 + C3)

Adopts the parent vocabulary verbatim (parent Section 3, amended 2026-04-19):

| Value | Meaning | Currently observed in live data |
|---|---|---|
| `gap` | Inventory entry with no extracted content yet (initial state for indexed-but-unprocessed sources) | **Yes — dominant in `index.jsonl` for standards/codes today (2000/2000 records sampled 2026-04-17).** |
| `indexed` | Document discovered and content-hashed; metadata captured | Yes |
| `summarized` | Summary content produced and persisted | Yes |
| `extracted` | Structured extraction (entities, fields) produced | Yes |
| `promoted` | Content has been promoted to L3 durable knowledge | Yes |
| `superseded` | Replaced by a newer `doc_key` for the same logical document | Rare — emitted by provenance-merge lineage workflows |
| `unreachable` | Source path or mount no longer accessible from any known machine | Not yet emitted by live writers; reserved |

**Surfaces bound by this enum (normative list for this contract):**

- `data/document-index/index.jsonl` records (field: `status`; treat as `processing_status`)
- `data/document-index/summaries/<algorithm>:<hex>.json` records that carry a processing-state field
- Promoted-artifact manifests under `knowledge/` that reference a `doc_key` with a processing-lifecycle field

The enum does **not** apply to: ledger row `status` (where that field, if present, carries transfer/migration state), classification `status` fields in subcategory taxonomies, or issue-workflow state. Those surfaces carry different `status` fields with different vocabularies and are out of scope for this contract.

### 4.2 Recommended extended fields

These fields are recommended for standards/codes documents and should be populated when available. They are layered on top of 4.1, not required for minimal conformance:

| Field | Type | Description | Owner layer |
|---|---|---|---|
| `id` | string | Human-readable standard identifier (e.g., `API-RP-1111`). Mutable — may be corrected. | L2 |
| `title` | string | Human-readable document title. | L2 |
| `org` | string | Standards organization (API, DNV, ISO, ASTM, etc.). | L2 |
| `domain` | string | Engineering domain from the taxonomy (pipeline, structural, marine, etc.). | L2 |
| `doc_paths` | list[string] | All known alias paths across machines and mounts. | L2 |
| `provenance` | list[object] | Array of `{source, path, host, merged_at, og_db_id?, old_path?}` entries (one per discovery location). Generated by `provenance.py`. Reader-compatibility: older entries may carry `discovered` in place of `merged_at`; readers accept both. | L2 |
| `size_mb` | float | File size in megabytes. | L2 |
| `ext` | string | File extension (`.pdf`, `.docx`, `.xlsx`, etc.). | L2 |
| `mtime` | ISO 8601 timestamp | File modification time at source. | L2 |
| `summary_ref` | string | Path to the summary JSON file. **Live filename pattern:** `data/document-index/summaries/<algorithm>:<hex>.json` — the `<algorithm>:<hex>` prefix is part of the filename (verified 2026-04-17; e.g., `summaries/sha256:3aa1fdc3e2c73e...json`). Readers must preserve the prefix when constructing the path. | L2 |
| `extraction_manifest_ref` | string | Path to the extraction manifest, if deep extraction was performed. | L2 |
| `promoted_artifacts` | list[string] | Paths to promoted outputs (equations, constants, tables, etc.) derived from this document. | L2 |
| `wiki_refs` | list[string] | Paths to LLM-wiki pages that cite this document as a source. Back-link field — see Section 4.3. | Materialized at L2; originates from L3 |

### 4.3 Field ownership by layer

Per parent Section 2, L3 must NOT own "source-of-truth provenance records." This contract refines what that means for back-link fields:

**Definition — back-link field:** A pointer from a higher-numbered layer to a lower-numbered layer, recorded at the lower layer for efficient reverse lookup. A back-link records *that a reference exists*; it does not record the *content* of the reference or establish provenance truth. The source-of-truth entity is the page at the higher layer; the back-link is a denormalized index.

`wiki_refs` is a back-link field — it is **populated from** L3 (wiki pages emit their `doc_key` citations) and **materialized at** L2 (the registry keeps the list for reverse lookup). L3 does not own `wiki_refs` as a provenance record; L3 *emits* the reference during ingest and the registry captures it.

| Layer | Owns | Must NOT own |
|---|---|---|
| **L1 Source documents** | The raw file bytes (and thus the `doc_key` implicitly). | Provenance metadata, processing status, summaries, wiki entries. |
| **L2 Registry/provenance** | All provenance fields in 4.1 and 4.2 (including the materialized `wiki_refs` back-link list), processing status, extraction lineage, path aliases. | Narrative synthesis, wiki content, issue execution state. |
| **L3 Durable knowledge** | Wiki-page content, the `doc_key` citations it makes, its own frontmatter. Emits `doc_key` references that L2 materializes into `wiki_refs`. | Source provenance fields, `doc_key` definition, processing status, the canonical list of wiki references (that lives at L2 as a denormalized index). |
| **L5 Execution state** | Issue references to `doc_key` for planning/review context. | Provenance fields, wiki content, source identity. |

---

## 5. Reuse-vs-Reparse Decision Rules

The central question: **when can existing document-intelligence outputs be reused, and when must raw documents be reparsed?**

### 5.1 Decision tree

Uses `processing_status` per Section 4.1.3. Because `gap` is the dominant value in live data (2000/2000 sampled `index.jsonl` records), the tree must branch on it explicitly:

```
Is there a registry entry for this doc_key?
├── NO → Fall through to L1: Index the raw document (Phase A).
│         Then summarize (Phase B). Then classify (Phase C). Continue pipeline.
└── YES → Check: what processing_status does it have?
          ├── processing_status: "gap"
          │     → Inventory-only — no downstream artifact exists.
          │       Needs at least summarization (Phase B+). Treat equivalently to a
          │       missing registry entry for reuse purposes.
          ├── processing_status: "indexed"
          │     → Metadata captured but no summary. Needs at least summarization
          │       (Phase B+). (Present in live data alongside `gap`; semantically
          │       "at least content-hashed.")
          ├── processing_status: "summarized"
          │     → Check: is the summary sufficient for the target use case?
          │       ├── YES (e.g., wiki page needs only domain + title + summary)
          │       │     → REUSE the summary. Do not reparse.
          │       └── NO (e.g., need tables, equations, constants)
          │             → Reparse: run deep extraction (doc_intelligence pipeline).
          ├── processing_status: "extracted"
          │     → Check: do extraction manifests contain the needed content types?
          │       ├── YES → REUSE extraction outputs. Do not reparse.
          │       └── NO (e.g., needed curves but only tables were extracted)
          │             → Targeted reparse: run additional extraction passes for missing types.
          ├── processing_status: "promoted"
          │     → REUSE promoted artifacts directly. These are the highest-fidelity outputs.
          │       Only reparse if the promoted artifact is suspected to be corrupt or outdated.
          ├── processing_status: "superseded"
          │     → Do NOT reuse this doc_key as authoritative. Follow the `superseded_by`
          │       lineage link to the current doc_key and restart the decision tree there.
          └── processing_status: "unreachable"
                → Source no longer accessible. Do not attempt reparse; rely on whatever
                  downstream artifacts (summary, extraction, promoted) already exist.
                  If none exist, this doc_key is not usable and must be flagged.
```

**Artifact-existence guard:** At every "REUSE" branch above, the referenced artifact (summary JSON, extraction manifest, promoted module) must be **present and non-empty**. Because summary filenames carry the `<algorithm>:<hex>` prefix (Section 4.2), the existence check MUST use the full prefixed filename. If the artifact is missing or zero-length despite the registry claiming that status, treat the document as if it were at the next-lower status level and fall through accordingly.

### 5.2 Sufficiency criteria

| Target use case | Minimum required `processing_status` | Reuse source |
|---|---|---|
| Wiki page creation (domain overview, entity page) | `summarized` | Summary JSON (`data/document-index/summaries/<algorithm>:<hex>.json`) |
| Wiki page with specific data (tables, constants) | `extracted` | Extraction manifest + content indexes |
| Code generation (equations, methods) | `promoted` | Promoted artifacts in digitalmodel modules |
| Conformance audit (does the registry know about this doc?) | `gap` or higher | Registry entry alone is sufficient |
| Cross-reference analysis | `indexed` or higher | Registry entry + `doc_paths` aliases |
| Full-text search | `summarized` or `extracted` | Summary text or extracted sections |

### 5.3 When OCR is required

OCR (or equivalent PDF-to-text extraction) is required only when:

1. The source document is a scanned PDF with no embedded text layer.
2. The existing extraction produced zero or negligible text (below `skip_below_words: 100` threshold from `config.yaml`).
3. A specific content type is needed (e.g., a figure caption or handwritten annotation) that text extraction cannot produce.

**OCR-and-`doc_key` rule (disambiguated per F3):**

- **Sidecar OCR** (produces a separate text artifact; leaves the source PDF untouched) does NOT change the `doc_key`. The source file bytes are unchanged. The extraction manifest records the OCR tool and parameters used.
- **Re-saving OCR** (e.g., `ocrmypdf --output-type pdf`, which writes a new PDF with an added text layer) DOES change the `doc_key`, because the file bytes change. The new PDF is a new document with a new `doc_key` linked to the original via `superseded_by` (or equivalent `ocr_derived_from`) lineage. See Section 3.4.

Pipelines that perform OCR must declare which mode they operate in and record the lineage link when they produce a new `doc_key`.

### 5.4 Staleness and re-extraction

An existing extraction may become stale if:

- The extraction tool is upgraded and produces materially better output.
- A known extraction bug is fixed (e.g., table parsing was broken for XLSX files).
- The document was previously extracted incompletely (e.g., timeout during overnight batch).

In these cases, **re-extraction is permitted** but must:
1. Produce a new extraction manifest (not overwrite the old one silently).
2. Record the re-extraction reason and timestamp.
3. Update the registry entry's `processing_status` and `extraction_manifest_ref`.

---

## 6. LLM-Wiki Promotion Path

### 6.1 From document-intelligence outputs into wiki-ready records

The promotion path uses existing document-intelligence outputs to populate wiki entries **without reparsing raw documents** when sufficient evidence exists.

```
L2 Registry + Summary ─→ Wiki source-summary page (wiki/sources/<slug>.md)
L2 Registry + Extraction ─→ Wiki entity/concept pages with specific data
L2 Registry + Promoted artifacts ─→ Wiki pages referencing live code modules
```

### 6.2 Promotion prerequisites

Before creating or updating a wiki page from a standards/codes document, the promotion process must verify:

| Prerequisite | Check | If missing |
|---|---|---|
| Document is registered | `doc_key` exists in registry | Index the document first (Phase A) |
| Summary exists | `summaries/<algorithm>:<hex>.json` is present and non-empty (full prefixed filename) | Summarize first (Phase B) |
| Domain is classified | Registry entry has a valid `domain` value | Classify first (Phase C) |
| No conflicting wiki page | No existing wiki page makes claims that contradict this source | Merge or flag for manual review |

### 6.3 Wiki page frontmatter — recommended fields

Per parent Section 8.1 (added 2026-04-19), **the per-wiki `CLAUDE.md` is the schema authority for L3 page frontmatter**. This contract does not and cannot bind frontmatter fields. What follows are *recommended* fields this contract proposes be **layered on top of the parent baseline floor** by the relevant wiki `CLAUDE.md`.

**Parent baseline floor (normative; restated from parent Section 8.1 for convenience):**

| Field | Type | Purpose |
|---|---|---|
| `title` | string | Human-readable page identity |
| `last_updated` | ISO-8601 date | Freshness signal for L3 promotion-decay tracking |
| `doc_key` | `<algorithm>:<hex>` per parent Section 3 | Canonical identity link to L1/L2 source(s); enables cross-layer reference |

**This contract's recommended additions for standards-promoted wiki pages:**

| Field | Type | Purpose | Binding |
|---|---|---|---|
| `source_ref` | string | Path to the underlying L2 summary (full prefixed form, e.g., `data/document-index/summaries/sha256:<hex>.json`) | Recommended; wiki `CLAUDE.md` decides |
| `domain` | string | Engineering domain classification, to support cross-wiki linking | Recommended; wiki `CLAUDE.md` decides |
| `promoted_from` | enum | Which `processing_status` the page was promoted from (`summarized`, `extracted`, or `promoted`) | Recommended; wiki `CLAUDE.md` decides |

**Which wikis this contract targets:** The primary wiki for standards-promoted pages is the **engineering wiki** (`knowledge/wikis/engineering/`). Its current `CLAUDE.md` declares `{title, tags, added, last_updated}` as required. This contract recommends that wiki's `CLAUDE.md` be updated by its maintainer to add `doc_key` (from the parent baseline floor) plus the three additions above for standards-promoted page classes. Other wikis (maritime-law, naval-architecture, marine-engineering) do not currently host standards-promoted pages; if they begin to, this contract's recommendations apply equivalently.

**Illustrative example (non-binding) of a conforming frontmatter block in the engineering wiki, assuming the engineering `CLAUDE.md` adopts the recommendations:**

```yaml
---
title: "API RP 1111 — Offshore Hydrocarbon Pipelines"
tags: [pipeline, api, offshore]
added: 2026-04-11
last_updated: 2026-04-19
doc_key: sha256:a1b2c3d4e5f6...
source_ref: data/document-index/summaries/sha256:a1b2c3d4e5f6....json
domain: pipeline
promoted_from: summarized
---
```

The block above is illustrative only. The binding schema is whatever `knowledge/wikis/engineering/CLAUDE.md` declares at the time of page creation.

### 6.4 When wiki promotion should NOT reparse

Wiki promotion should reuse existing outputs and NOT trigger reparsing when:

1. A summary exists and the wiki page only needs domain, title, organization, and narrative summary.
2. Extracted content indexes contain the needed tables, constants, or equations.
3. Promoted code artifacts already exist in digitalmodel modules.

Wiki promotion should trigger additional extraction (not full reparsing) only when:

1. The wiki page needs a specific content type not yet extracted.
2. The existing extraction is known to be incomplete or corrupt.

---

## 7. Unified Artifact-Registry Implications

### 7.1 Architecture-level compatibility with #2205

The parent operating model requires a "single lookup model" that can map any `doc_key` to its source references, registry entries, promoted artifacts, and execution references. This contract contributes the provenance layer of that model.

**What this contract requires of the unified registry:**

1. Every registry entry is keyed by `doc_key` (`<algorithm>:<hex>` per Section 3.1).
2. The registry supports the minimum required fields from Section 4.1, including `processing_status` and `merged_at`.
3. The registry can store multiple path aliases per `doc_key` (already supported by `provenance.py`).
4. The registry can link to summaries, extraction manifests, and promoted artifacts via reference paths, using the prefixed-filename convention for summary files.
5. The registry handles mixed-namespace identities (`sha256:` canonical, `md5:` legacy) without joining across namespaces. See Section 3.2.

### 7.2 What this contract recommends without fixing exact schema

This contract does NOT prescribe:
- Whether the unified registry is a single file or a federated set of files.
- The exact YAML/JSON schema for registry entries.
- The query interface for looking up documents by `doc_key`.
- Whether `registry.yaml` (aggregate stats) and `index.jsonl` (per-document records) should merge.

These are implementation decisions for #2136 (accessibility registry). This contract only requires that whatever implementation is chosen:
- Uses `doc_key` (`<algorithm>:<hex>` form) as the primary join key.
- Supports the provenance fields defined here.
- Does not invent a parallel identity system that competes with `doc_key`.
- Does not join `sha256:` and `md5:` values as if they were the same identity.

---

## 8. Anti-Patterns

### 8.1 Duplicate parsing

**Anti-pattern:** A wiki ingest pipeline reads a raw PDF, extracts text, and creates a wiki page — even though a summary and extraction already exist for that `doc_key`.

**Why it is forbidden:** Creates duplicate extraction work, risks inconsistency between wiki content and registry provenance, and wastes LLM budget.

**Correct approach:** Check the registry for existing outputs at the required sufficiency level (Section 5.2) before touching raw documents. Use the full prefixed filename when checking summary existence.

### 8.2 Path-only identity

**Anti-pattern:** Two systems each track the same document by path alone, creating separate records for `/mnt/ace/.../API RP 1111 (1999).pdf` and `/mnt/remote/.../API RP 1111.pdf` without recognizing they are the same `doc_key`.

**Why it is forbidden:** Violates the `doc_key` rule. Creates competing sources of truth.

**Correct approach:** Always resolve to `doc_key` first. Use `provenance.py`'s merge logic to unify path aliases under a single canonical record.

### 8.3 Broken lineage — promoted artifacts without a source `doc_key` back-link (rewritten per F2)

**Anti-pattern:** A promoted artifact (e.g., an equation module in digitalmodel) does not record which `doc_key` it was derived from, making it impossible to trace back to the source standard.

**Why it is forbidden:** Breaks auditability. If the source standard is revised, there is no way to identify which promoted artifacts need updating.

**Clarification of current state:** The existing promoter pattern emits a `# content-hash: <hash>` comment where the hash is computed from the **output body** via `scripts/data/doc_intelligence/promoters/text_utils.py::content_hash()` (verified across `constants.py`, `curves.py`, `definitions.py`, `equations.py`, `procedures.py`, `requirements.py`). That comment is an **output-integrity stamp**, NOT a source-traceability link. It does not satisfy the source `doc_key` back-link requirement.

**Correct approach:** Promoted artifacts must emit **two separate fields**:

1. A `# content-hash: <hash>` (or equivalent) **output-integrity stamp** computed from the promoted output body. This is the existing behavior; it detects corruption of the promoted file itself.
2. A `# source_doc_key: <algorithm>:<hex>` (or `# doc_key: <algorithm>:<hex>`) **source-traceability field** referencing the `doc_key` of the L1 document the artifact was derived from. This field does not currently exist in promoter outputs and must be added by follow-on work (see Section 9.3).

Existing output-integrity stamps alone are insufficient. An implementation that treats the existing `# content-hash:` as satisfying Section 8.3 has NOT closed this anti-pattern.

### 8.4 Wiki entries outranking provenance

**Anti-pattern:** A wiki page asserts facts about a standard (e.g., "API RP 1111 covers pipeline design for water depths up to 3000m") that contradict or extend what the L2 summary/extraction contains, without citing a source.

**Why it is forbidden:** L3 wiki content must be traceable to L2 provenance. Unsourced wiki claims create a parallel truth that cannot be verified or updated when the source changes.

**Correct approach:** Wiki pages cite their `doc_key` and source layer (via `promoted_from`). Claims beyond what the source evidence supports are flagged as "unverified" or "LLM-inferred" with a review tag.

### 8.5 Identity-namespace and prefix confusion

**Anti-pattern (stripping prefixes for comparison):** Legacy code strips `sha256:` prefixes and compares bare hex, then extends the same treatment to `md5:` values — silently joining MD5 and SHA-256 identities that happen to collide on 32 vs. 64 char substrings, or emitting bare-hex into storage.

**Why it is harmful:** Joins unrelated documents across hash algorithms. Creates silent dedup misses when writers disagree on whether to emit a prefix. Violates the parent Section 3 identity namespace rule.

**Correct approach:**

1. The canonical `doc_key` form is `<algorithm>:<hex>`. Both parts are load-bearing.
2. Comparison uses the full string. Namespace must match before hex comparison is meaningful.
3. `sha256:<hex>` and `md5:<hex>` are **different identities**, even if the underlying document is the same. They may be linked by provenance lineage; they must not be joined as if identical.
4. Bare-hex encountered in storage is a violation: upgrade the writer. Readers may treat bare-hex as `sha256:` for compatibility while emitting a conformance warning (check delegated to #2206).
5. Summary-file **paths** retain the full prefix in the filename (`summaries/sha256:<hex>.json`) per live behavior. Stripping the prefix for filename construction will produce paths that do not exist on disk.

---

## 9. Likely Implementation Surfaces

The following files and modules are likely to require changes when implementing the provenance and reuse contract. This section identifies them without implementing the changes. The parent operating model's rename of `discovered` → `merged_at` is delegated to a future code-side issue and is NOT part of this revision pass.

### 9.1 Identity convergence (namespace + field-name migration)

| File | Current state | Likely change |
|---|---|---|
| `scripts/data/document-index/config.yaml` | `primary_key: content_hash` | Document that `content_hash` carries `<algorithm>:<hex>`-form `doc_key` values. Optionally add `canonical_identity_field: doc_key` alias. |
| `scripts/data/document-index/provenance.py` | Dedup key is `content_hash`; stamps `discovered` at merge time (line 82) | Accept `doc_key` as a synonym for `content_hash` on input; rename `discovered` → `merged_at` in emitted records while continuing to read `discovered` from legacy input; preserve full `<algorithm>:<hex>` during dedup (no prefix stripping). |
| `scripts/data/document-index/phase-a-index.py` | Emits `md5:` for 32-char, `sha256:` for longer inputs (lines 135-139) | Keep existing namespacing; migration opportunity noted: when a record is touched for any other reason, upgrade `md5:` entries to `sha256:` by re-hashing accessible sources. No hard sunset. |
| `scripts/data/document-index/phase-b-claude-worker.py` | Uses `content_hash` field, emits `sha256:` in output | Normalize emitted field name reference; keep prefix. |
| `scripts/data/document-index/reclassify-audit.py` | Strips `sha256:` prefix for comparison | Replace prefix-strip-and-compare with full-string comparison (see Section 3.2). |
| `scripts/data/document-index/subcategory-classify.py` | Same prefix-strip pattern | Same fix. |
| `scripts/data/doc_intelligence/schema.py` | `DocumentMetadata.checksum` | Rename or alias to `doc_key`, treat as `<algorithm>:<hex>`. |
| `scripts/data/doc_intelligence/index_builder.py` | Manifest-index uses `checksum` field | Rename or alias to `doc_key`. |

### 9.2 Status-field disambiguation

| File | Current state | Likely change |
|---|---|---|
| `data/document-index/index.jsonl` | `status: gap` dominates live records | No data migration required; `gap` is now normative per Section 4.1.3. Writers may begin emitting `status` or `processing_status` — readers of this contract's surfaces accept either. |
| Surfaces carrying unrelated `status` fields (ledger, classification) | Overload possible | Audit for conflation; if any conformance check reads "the `status` field" generically, scope it to the surfaces in Section 4.1.3. |

### 9.3 Promotion path — adding source `doc_key` traceability

| File | Current state | Likely change |
|---|---|---|
| `scripts/data/doc_intelligence/promoters/*.py` (constants, curves, definitions, equations, procedures, requirements) | Emit only `# content-hash: <hash>` computed from output body | **Add a second comment line** `# source_doc_key: <algorithm>:<hex>` threading the source document's `doc_key` through the promotion pipeline. The existing output-integrity stamp stays as-is. See Section 8.3. |
| `scripts/knowledge/llm_wiki.py` | `ingest` reads raw files directly; no reuse check; no back-link materialization | Add (a) pre-ingest reuse check that queries the registry for existing summary/extraction using the full prefixed filename pattern, and (b) emission of `wiki_refs` back-links to the registry at ingest time. |
| `scripts/data/doc_intelligence/orchestrator.py` | Computes checksum and builds manifest | Add `processing_status` field to output; record whether extraction was incremental or full. |

### 9.4 Registry and ledger

| File | Current state | Likely change |
|---|---|---|
| `data/document-index/standards-transfer-ledger.yaml` | Uses `id` as primary key; `doc_path`/`doc_paths` for location; no `doc_key` field | Add `doc_key` field per standard where source is reachable. Entries without `doc_key` are **grandfathered as "legacy — no mount access"** until a Phase E back-population task (see Section 10) runs; #2206 conformance checks MUST NOT flag grandfathered legacy entries. |
| `data/document-index/registry.yaml` | Aggregate statistics only | Potentially extend or federate with per-document `doc_key` lookups (scope for #2136). |
| `data/document-index/mounted-source-registry.yaml` | Source-root level; no per-document `doc_key` | No change needed at this level; per-document identity lives in `index.jsonl`. |

---

## 10. Open Questions / Residual Risks

1. **Namespace migration strategy:** `md5:` entries for `og_standards` are permitted indefinitely per parent Section 3. An opportunistic-upgrade policy (re-hash to `sha256:` when a record is touched for any other reason) is the lowest-risk path. A hard migration would require mount access to the original sources; the standards-transfer ledger notes some sources are on unreachable mounts. Recommend: opportunistic upgrade only, documented in each writer.

2. **`processing_status` field name in live data:** Live `index.jsonl` writes `status`, not `processing_status`. This contract normalizes the **semantic name** to `processing_status` to avoid collision with unrelated `status` fields in other surfaces. The field-name rename in live data is delegated to a future code-side issue; until then, readers on the surfaces listed in Section 4.1.3 treat `status` as `processing_status`.

3. **`merged_at` vs. `discovered` rename in code:** Parent Section 3 mandates the semantic rename; the code-side implementation of the rename in `provenance.py` is delegated to a future code-side issue, not this revision. Readers must continue to accept `discovered` as a legacy synonym indefinitely — there is no hard sunset.

4. **Standards-transfer-ledger `doc_key` back-population:** The ledger identifies standards by human-readable `id` without a `doc_key`. Populating `doc_key` requires hashing source files, which requires mount access. This is a Phase E back-population task. **Until a concrete follow-on issue is filed and executed, pre-existing ledger entries without `doc_key` are explicitly grandfathered as legacy** — #2206 conformance checks must not flag them. Filing the follow-on issue is a prerequisite to ending the grandfather period.

5. **Promoted-artifact `source_doc_key` threading:** Adding a source `doc_key` back-link to promoter outputs (Section 8.3 / 9.3) requires threading the source hash through the promotion pipeline. This is a non-trivial plumbing change: the orchestrator must pass the source `doc_key` to each promoter and the promoter must emit it as a second comment field alongside the existing output-integrity stamp.

6. **Wiki ingest reuse gating:** The `llm_wiki.py` `ingest` command currently reads raw files directly. Adding a reuse check requires the wiki CLI to query the registry using full prefixed filenames, which couples two currently independent subsystems. This coupling is architecturally correct (L3 should read from L2) but needs careful API design.

7. **Cross-machine `doc_key` verification:** When a document exists on multiple machines, the `doc_key` should be identical. But if machines have subtly different file copies (e.g., different PDF metadata from re-downloads), the `doc_key` will differ. The `provenance.py` merge logic treats them as separate documents. This is correct behavior but may surprise users who expect "the same standard" to have one identity.

8. **Wiki `CLAUDE.md` updates required:** Per Section 6.3, the recommendations in this contract are *recommendations* — they are binding only if a wiki `CLAUDE.md` adopts them. For standards-promoted pages, the engineering wiki's `CLAUDE.md` would need to add `doc_key` (from the parent baseline floor) plus `source_ref`, `domain`, and `promoted_from`. That update is out of scope for this contract; it is the wiki maintainer's decision.

---

## 11. Recommended Follow-On Implementation Sequence

Based on the implementation surfaces identified in Section 9 and the dependency order from the parent operating model:

| Order | Work item | Scope | Depends on |
|---|---|---|---|
| 1 | Replace bare-hex comparisons with full-string `<algorithm>:<hex>` comparisons in `reclassify-audit.py`, `subcategory-classify.py`, and any downstream consumers | Small — targeted edits in two files | Nothing |
| 2 | Rename `discovered` → `merged_at` in `provenance.py` emitted records (reader continues to accept both) | Small — one file, one field name; this contract **does NOT implement this rename**; a separate code-side issue must be filed | Nothing |
| 3 | File and execute Phase E `doc_key` back-population task for `standards-transfer-ledger.yaml` | Medium — requires mount access; ends the grandfather period | #1 |
| 4 | Add `source_doc_key` threading through `doc_intelligence/orchestrator.py` and all six promoter modules | Medium — plumbing change | #1 |
| 5 | Add reuse-check to `llm_wiki.py` ingest using full prefixed filenames | Medium — query registry before reading raw files | #1, registry must be queryable |
| 6 | Build wiki-from-registry promotion mode in `llm_wiki.py` | Large — new ingest mode that reads from summaries/extractions | #5 |
| 7 | Update `knowledge/wikis/engineering/CLAUDE.md` to add `doc_key` (baseline floor) plus recommended `source_ref`, `domain`, `promoted_from` for standards-promoted pages | Small — one file; maintained by the engineering wiki owner, not this contract | #1 |

These items should be captured as implementation issues under #2207 or as sub-tasks of #2136 (accessibility registry), depending on whether they primarily affect provenance or accessibility.

---

## 12. Revision history

### 2026-04-19 — Cross-provider-review + parent-amendment realignment pass

Driven by (a) the 2026-04-19 amendments to parent operating model Sections 2, 3, and 8.1 ([#2205 amendment comment](https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277238819)), and (b) the 11 findings surfaced by the 2026-04-17 cross-provider adversarial review (7 Claude findings at `scripts/review/results/2026-04-17-plan-2207-claude-adversarial.md`; 4 Codex findings at `scripts/review/results/2026-04-17-plan-2207-codex-adversarial.md`).

**Amendments applied (A–E from the revision dispatch prompt):**

- **A. `<algorithm>:<hex>` identity form** (parent Section 3) — Section 3.1 rewritten to declare the `<algorithm>:<hex>` canonical form; `sha256:` (canonical) and `md5:` (legacy, read-only for `og_standards`) namespaces documented; bare-hex explicitly marked a violation with a reader-compatibility rule.
- **B. Status vocabulary adoption** (parent Section 3) — Section 4.1.3 adopts the parent superset (`gap | indexed | summarized | extracted | promoted | superseded | unreachable`); Section 5.1 decision tree extended with explicit `gap`, `superseded`, and `unreachable` branches.
- **C. `discovered` → `merged_at` rename** (parent Section 3) — Sections 4.1, 4.1.2, 4.2 use `merged_at`; semantic clarified as merge-time stamp; reader backward-compatibility documented; code-side rename in `provenance.py` explicitly deferred to a future issue.
- **D. Frontmatter reframed as additional-fields-on-baseline-floor** (parent Section 8.1) — Section 6.3 rewritten to restate the parent baseline floor, explicitly delegate binding authority to the per-wiki `CLAUDE.md`, and recommend (not require) `source_ref`, `domain`, `promoted_from` for engineering-wiki standards-promoted pages.
- **E. Cross-references updated** — Section 2 updates parent-section references to the amended sections; the parent amendment comment is linked.

**Finding dispositions:**

| ID | Severity | Source | Disposition | Where addressed |
|---|---|---|---|---|
| F1 | MAJOR | Claude | FIXED | Section 4.1.3 (enum adopts `gap` + full parent vocabulary); Section 5.1 (decision tree branches on all values) |
| F2 | MAJOR | Claude | FIXED | Section 8.3 rewritten; `# content-hash:` clarified as output-integrity stamp; `# source_doc_key:` documented as the required-but-not-yet-implemented traceability field; Section 9.3 captures the follow-on plumbing work |
| F3 | MINOR | Claude | FIXED | Section 3.4 table row updated to split sidecar OCR vs. re-saving OCR; Section 5.3 aligned |
| F4 | MINOR | Claude | FIXED | Section 4.3 adds explicit back-link-field definition; `wiki_refs` described as materialized at L2 from L3 emissions (not L3-owned as a provenance record) |
| F5 | MINOR | Claude | FIXED | Section 4.1.1 explicitly scopes `path` as machine-local; cross-machine normalization deferred to #2136; `provenance[]` is the authoritative multi-host list |
| F6 | MINOR | Claude | PARTIAL | Section 9.4 + Section 10 item 4 + Section 11 item 3: pre-existing ledger entries without `doc_key` are explicitly grandfathered as legacy; #2206 must not flag them; filing a concrete follow-on issue remains open (filing the issue is out of scope for this revision pass, which is documentation-only) |
| F7 | MAJOR (process) | Claude | FIXED (out-of-contract) | Cross-provider review was executed 2026-04-17 (Claude + Codex). This revision pass addresses the combined 11 findings from both reviewers. |
| C1 | MAJOR | Codex | FIXED | Section 3.1 + 3.2: `<algorithm>:<hex>` canonical form; namespaces documented; cross-namespace joins explicitly forbidden |
| C2 | MAJOR | Codex | FIXED | Section 4.2 (`summary_ref` row) + Section 6.3 example + Section 8.5: summary filenames carry the full `<algorithm>:<hex>` prefix; the 2026-04-11 bare-hex example was wrong and is corrected |
| C3 | MAJOR | Codex | FIXED | Section 4.1.3: field semantic normalized to `processing_status`; surfaces where this enum applies are enumerated; overload with unrelated `status` fields called out explicitly |
| C4 | MAJOR | Codex | FIXED | Section 4.1.2 + Open Question 3: `merged_at` semantic aligned with `provenance.py:82` live behavior (merge-time stamp, not first-indexed); contract no longer asserts "first-indexed" semantic |

**Preserved content (unchanged by this revision):**

- Section 1 purpose/scope, Section 2 relationship framing, Section 3.3 alias paths, Section 3.4 non-OCR rows, Section 4.2 non-affected fields, Section 5.2 sufficiency criteria structure (updated only for `gap` row), Section 5.4 staleness rules, Section 6.1 promotion-path diagram, Section 6.2 prerequisites, Section 6.4 reparse-avoidance rules, Section 7 registry implications structure, Section 8.1/8.2/8.4 anti-patterns, Appendix glossary structure.

**Explicitly NOT done in this pass (out of scope per revision dispatch):**

- Code changes in `scripts/data/document-index/*.py` (no writer edits).
- Data migrations in `data/document-index/*`.
- Edits to parent operating model (already amended upstream).
- Edits to sibling contracts #2206 or #2209.
- Creating or closing any related GitHub issues.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| `doc_key` | Content-based canonical identity of a source document, in `<algorithm>:<hex>` form (parent Section 3). `sha256:` canonical; `md5:` legacy, read-only for `og_standards`. |
| `content_hash` | Field name in `index.jsonl` and pipeline scripts that carries a `doc_key` value. Semantically identical to `doc_key`; preserved for backward compatibility. |
| `checksum` | Field name in `doc_intelligence/schema.py` that carries a `doc_key` value in `sha256:<hex>` form. |
| `processing_status` | Field semantic for the processing-lifecycle enum (`gap | indexed | summarized | extracted | promoted | superseded | unreachable`) inherited from parent Section 3. Live writers may emit `status`; readers on the surfaces in Section 4.1.3 treat the two as synonyms. |
| `merged_at` | ISO-8601 UTC timestamp recorded when a provenance record is first appended to a document's `provenance[]` array. Immutable per provenance entry. Legacy synonym: `discovered`. |
| `provenance` | Array of `{source, path, host, merged_at, …}` entries tracking where a document was found. |
| `promotion` | The act of converting document-intelligence outputs (summaries, extractions) into durable wiki entries at L3. |
| `reuse` | Using existing L2 outputs (summaries, extractions, promoted artifacts) instead of reparsing raw L1 documents. |
| `reparse` | Going back to the raw L1 document to produce new L2 outputs, when existing outputs are insufficient. |
| `back-link field` | A pointer from a higher-numbered layer to a lower-numbered layer, recorded at the lower layer for reverse lookup. Does not establish provenance truth (see Section 4.3). Example: `wiki_refs`. |
| `output-integrity stamp` | A hash of a promoted artifact's **output body**, used to detect corruption of the promoted file itself. Distinct from source traceability. Example: the existing `# content-hash:` comment in promoter outputs. |
| `source traceability field` | A field in a promoted artifact that references the `doc_key` of the L1 document the artifact was derived from. Example (proposed): `# source_doc_key:` — not yet implemented in promoters; see Section 8.3 and Section 9.3. |
