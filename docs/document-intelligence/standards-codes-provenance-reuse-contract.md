# Standards/Codes Provenance + Reuse Contract

> **Issue:** [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207)
> **Parent:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — LLM-Wiki + Resource/Document Intelligence Operating Model
> **Status:** Normative — approved provenance and reuse contract for standards/codes
> **Date:** 2026-04-11
> **Scope:** Contract only. Implementation delegated to follow-on issues.

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

This contract specializes the parent model for provenance and reuse. It does not redefine it.

---

## 2. Relationship to Parent Operating Model (#2205)

This document inherits from the [parent operating model](llm-wiki-resource-doc-intelligence-operating-model.md) and operates under its constraints:

| Parent rule | How this contract applies it |
|---|---|
| **Single-source-of-truth pyramid** (Section 2) | Provenance fields are owned by L2 (Registry/provenance). Wiki entries at L3 inherit provenance from L2; they do not create it. |
| **`doc_key` rule** (Section 3) | This contract defines the concrete mapping from existing `content_hash` fields to the canonical `doc_key`. |
| **Allowed information flows** (Section 4) | Reuse rules follow L2→L3 promotion flow. Reparsing falls back to L1→L2 indexing flow. |
| **Forbidden flows** (Section 5) | Reuse rules enforce the prohibition on L3 reparsing raw documents when L2 evidence is sufficient. |
| **Cross-machine access model** (Section 7) | Provenance fields must support multi-machine path aliasing. |
| **Unified artifact registry** (Section 8) | This contract defines provenance field requirements compatible with a `doc_key`-based registry. |
| **Child issue guardrails** (Section 10) | This contract does NOT redefine parent layer boundaries, ownership model, or workflow policy. |

### Conflict resolution

If this contract is found to conflict with the parent operating model, the parent takes precedence. Conflicts must be documented as comments on #2205 with a proposed amendment before any deviation.

---

## 3. Canonical Identity Model

### 3.1 The `doc_key` definition

The canonical identity of any source document is **content-based**. The `doc_key` is the SHA-256 hex digest of the document's binary content.

**Mapping from existing codebase terms:**

| Existing term | Where used | Relationship to `doc_key` |
|---|---|---|
| `content_hash` | `index.jsonl` records, `config.yaml` (`primary_key: content_hash`), `provenance.py` dedup key | **This IS the `doc_key`.** The field name `content_hash` is the current implementation of `doc_key`. Future implementations should accept both names during migration but converge on `doc_key` as the canonical field name. |
| `sha` / `sha256` | Shard files (`"sha": "sha256:..."` prefix), summary file lookups (`summaries/<sha256>.json`) | The hex digest value with optional `sha256:` prefix. Strip the prefix to obtain the `doc_key`. |
| `checksum` | `doc_intelligence/schema.py` (`DocumentMetadata.checksum`), `index_builder.py` manifest-index | SHA-256 of the source file, equivalent to `doc_key` for the same file. Used in extraction manifests for incremental-build change detection. |
| `content_hash()` function | `doc_intelligence/promoters/text_utils.py` | **NOT a `doc_key`.** This hashes the promoted *output content*, not the source document. It is a content-integrity stamp for promoted artifacts, not a document identity. |

### 3.2 The `doc_key` / content-identity convergence rule

All registry entries, summaries, promoted artifacts, and wiki-ready records **must** reference documents by `doc_key` (SHA-256 of file content). Implementation may retain legacy field names (`content_hash`, `sha`, `sha256`) during migration, but:

1. The semantic meaning is always "SHA-256 of the source document's binary content."
2. New code should use the field name `doc_key`.
3. When `sha256:` prefixes are present, they must be stripped for comparison. The canonical form is the bare 64-character hex digest.

### 3.3 Alias paths and machine-specific paths

File paths are **aliases**, not identity. The same document may appear at multiple locations:

```
doc_key: a1b2c3d4...  (SHA-256 of file content)
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
| OCR re-extraction produces different text | No — the source file hasn't changed | OCR output is a derived artifact, not the source identity. The source `doc_key` remains stable. |
| PDF re-saved with different metadata but identical visible content | **Yes** — the binary differs | The `doc_key` is computed from file bytes. A re-save that changes metadata changes the hash. Link via `superseded_by` if the visible content is equivalent. |

---

## 4. Required Provenance Fields

### 4.1 Minimum required fields

Every tracked document in the intelligence ecosystem must have these fields in its registry/index entry:

| Field | Type | Description | Owner layer |
|---|---|---|---|
| `doc_key` | string (64-char hex) | SHA-256 of source file content. The canonical identity. | L2 |
| `source` | string | Source bucket identifier (e.g., `og_standards`, `ace_standards`, `ace_project`). | L2 |
| `path` | string | Primary file path (the highest-priority alias). | L2 |
| `host` | string | Machine/host where this path is valid. | L2 |
| `discovered` | ISO 8601 timestamp | When this document was first indexed. | L2 |
| `status` | enum | Processing status: `indexed`, `summarized`, `extracted`, `promoted`. | L2 |

### 4.2 Recommended extended fields

These fields are recommended for standards/codes documents and should be populated when available:

| Field | Type | Description | Owner layer |
|---|---|---|---|
| `id` | string | Human-readable standard identifier (e.g., `API-RP-1111`). Mutable — may be corrected. | L2 |
| `title` | string | Human-readable document title. | L2 |
| `org` | string | Standards organization (API, DNV, ISO, ASTM, etc.). | L2 |
| `domain` | string | Engineering domain from the taxonomy (pipeline, structural, marine, etc.). | L2 |
| `doc_paths` | list[string] | All known alias paths across machines and mounts. | L2 |
| `provenance` | list[object] | Array of `{source, path, host, discovered, og_db_id?, old_path?}` entries (one per discovery location). Generated by `provenance.py`. | L2 |
| `size_mb` | float | File size in megabytes. | L2 |
| `ext` | string | File extension (`.pdf`, `.docx`, `.xlsx`, etc.). | L2 |
| `mtime` | ISO 8601 timestamp | File modification time at source. | L2 |
| `summary_ref` | string | Path to the summary JSON file (`summaries/<doc_key>.json`). | L2 |
| `extraction_manifest_ref` | string | Path to the extraction manifest, if deep extraction was performed. | L2 |
| `promoted_artifacts` | list[string] | Paths to promoted outputs (equations, constants, tables, etc.) derived from this document. | L2 |
| `wiki_refs` | list[string] | Paths to LLM-wiki pages that cite this document as a source. | L3 (back-link) |

### 4.3 Field ownership by layer

| Layer | Owns | Must NOT own |
|---|---|---|
| **L1 Source documents** | The raw file bytes (and thus the `doc_key` implicitly). | Provenance metadata, processing status, summaries, wiki entries. |
| **L2 Registry/provenance** | All provenance fields (4.1 and 4.2 above), processing status, extraction lineage, path aliases. | Narrative synthesis, wiki content, issue execution state. |
| **L3 Durable knowledge** | `wiki_refs` (back-links from wiki pages to their source `doc_key`). Wiki pages may cite `doc_key` but do not own provenance truth. | Source provenance fields, `doc_key` definition, processing status. |
| **L5 Execution state** | Issue references to `doc_key` for planning/review context. | Provenance fields, wiki content, source identity. |

---

## 5. Reuse-vs-Reparse Decision Rules

The central question: **when can existing document-intelligence outputs be reused, and when must raw documents be reparsed?**

### 5.1 Decision tree

```
Is there a registry entry for this doc_key?
├── NO → Fall through to L1: Index the raw document (Phase A).
│         Then summarize (Phase B). Then classify (Phase C). Continue pipeline.
└── YES → Check: what processing status does it have?
          ├── status: "indexed" only
          │     → Reparse: needs at least summarization (Phase B+).
          ├── status: "summarized"
          │     → Check: is the summary sufficient for the target use case?
          │       ├── YES (e.g., wiki page needs only domain + title + summary)
          │       │     → REUSE the summary. Do not reparse.
          │       └── NO (e.g., need tables, equations, constants)
          │             → Reparse: run deep extraction (doc_intelligence pipeline).
          ├── status: "extracted"
          │     → Check: do extraction manifests contain the needed content types?
          │       ├── YES → REUSE extraction outputs. Do not reparse.
          │       └── NO (e.g., needed curves but only tables were extracted)
          │             → Targeted reparse: run additional extraction passes for missing types.
          └── status: "promoted"
                → REUSE promoted artifacts directly. These are the highest-fidelity outputs.
                  Only reparse if the promoted artifact is suspected to be corrupt or outdated.
```

**Artifact-existence guard:** At every "REUSE" branch above, the referenced artifact (summary JSON, extraction manifest, promoted module) must be **present and non-empty**. If the artifact is missing or zero-length despite the registry claiming that status, treat the document as if it were at the next-lower status level and fall through accordingly. This prevents silent failures when artifacts are deleted, moved, or corrupted after registration.

### 5.2 Sufficiency criteria

| Target use case | Minimum required status | Reuse source |
|---|---|---|
| Wiki page creation (domain overview, entity page) | `summarized` | Summary JSON (`summaries/<doc_key>.json`) |
| Wiki page with specific data (tables, constants) | `extracted` | Extraction manifest + content indexes |
| Code generation (equations, methods) | `promoted` | Promoted artifacts in digitalmodel modules |
| Conformance audit (does the registry know about this doc?) | `indexed` | Registry entry alone is sufficient |
| Cross-reference analysis | `indexed` | Registry entry + `doc_paths` aliases |
| Full-text search | `summarized` or `extracted` | Summary text or extracted sections |

### 5.3 When OCR is required

OCR (or equivalent PDF-to-text extraction) is required only when:

1. The source document is a scanned PDF with no embedded text layer.
2. The existing extraction produced zero or negligible text (below `skip_below_words: 100` threshold from `config.yaml`).
3. A specific content type is needed (e.g., a figure caption or handwritten annotation) that text extraction cannot produce.

**OCR does NOT change the `doc_key`.** The source file is unchanged; OCR produces a derived text artifact. The extraction manifest records the OCR tool and parameters used.

### 5.4 Staleness and re-extraction

An existing extraction may become stale if:

- The extraction tool is upgraded and produces materially better output.
- A known extraction bug is fixed (e.g., table parsing was broken for XLSX files).
- The document was previously extracted incompletely (e.g., timeout during overnight batch).

In these cases, **re-extraction is permitted** but must:
1. Produce a new extraction manifest (not overwrite the old one silently).
2. Record the re-extraction reason and timestamp.
3. Update the registry entry's processing status and `extraction_manifest_ref`.

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
| Summary exists | `summaries/<doc_key>.json` is present and non-empty | Summarize first (Phase B) |
| Domain is classified | Registry entry has a valid `domain` value | Classify first (Phase C) |
| No conflicting wiki page | No existing wiki page makes claims that contradict this source | Merge or flag for manual review |

### 6.3 Wiki page provenance back-link

Every wiki page created from a standards/codes document must include:

```yaml
---
title: "API RP 1111 — Offshore Hydrocarbon Pipelines"
doc_key: a1b2c3d4e5f6...
source_ref: data/document-index/summaries/a1b2c3d4e5f6....json
domain: pipeline
promoted_from: summarized  # or "extracted" or "promoted"
last_updated: 2026-04-11
---
```

This ensures traceability from wiki content back to its source `doc_key` and the specific intelligence layer that produced it.

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

1. Every registry entry is keyed by `doc_key` (SHA-256 of source content).
2. The registry supports the minimum required fields from Section 4.1.
3. The registry can store multiple path aliases per `doc_key` (already supported by `provenance.py`).
4. The registry can link to summaries, extraction manifests, and promoted artifacts via reference paths.

### 7.2 What this contract recommends without fixing exact schema

This contract does NOT prescribe:
- Whether the unified registry is a single file or a federated set of files.
- The exact YAML/JSON schema for registry entries.
- The query interface for looking up documents by `doc_key`.
- Whether `registry.yaml` (aggregate stats) and `index.jsonl` (per-document records) should merge.

These are implementation decisions for #2136 (accessibility registry). This contract only requires that whatever implementation is chosen:
- Uses `doc_key` as the primary join key.
- Supports the provenance fields defined here.
- Does not invent a parallel identity system that competes with `doc_key`.

---

## 8. Anti-Patterns

### 8.1 Duplicate parsing

**Anti-pattern:** A wiki ingest pipeline reads a raw PDF, extracts text, and creates a wiki page — even though a summary and extraction already exist for that `doc_key`.

**Why it is forbidden:** Creates duplicate extraction work, risks inconsistency between wiki content and registry provenance, and wastes LLM budget.

**Correct approach:** Check the registry for existing outputs at the required sufficiency level (Section 5.2) before touching raw documents.

### 8.2 Path-only identity

**Anti-pattern:** Two systems each track the same document by path alone, creating separate records for `/mnt/ace/.../API RP 1111 (1999).pdf` and `/mnt/remote/.../API RP 1111.pdf` without recognizing they are the same `doc_key`.

**Why it is forbidden:** Violates the `doc_key` rule. Creates competing sources of truth.

**Correct approach:** Always resolve to `doc_key` first. Use `provenance.py`'s merge logic to unify path aliases under a single canonical record.

### 8.3 Broken lineage

**Anti-pattern:** A promoted artifact (e.g., an equation module in digitalmodel) does not record which `doc_key` it was derived from, making it impossible to trace back to the source standard.

**Why it is forbidden:** Breaks auditability. If the source standard is revised, there is no way to identify which promoted artifacts need updating.

**Correct approach:** Promoted artifacts must include a `content_hash` or `doc_key` comment/metadata field linking back to the source document. The current promoter pattern (`# content-hash: <hash>` or `# content_hash: <hash>`) satisfies this, but should converge on `# doc_key: <hash>` for consistency.

### 8.4 Wiki entries outranking provenance

**Anti-pattern:** A wiki page asserts facts about a standard (e.g., "API RP 1111 covers pipeline design for water depths up to 3000m") that contradict or extend what the L2 summary/extraction contains, without citing a source.

**Why it is forbidden:** L3 wiki content must be traceable to L2 provenance. Unsourced wiki claims create a parallel truth that cannot be verified or updated when the source changes.

**Correct approach:** Wiki pages cite their `doc_key` and source layer. Claims beyond what the source evidence supports are flagged as "unverified" or "LLM-inferred" with a review tag.

### 8.5 Prefix inconsistency in hash values

**Anti-pattern:** Some records store `sha256:a1b2c3...` (with prefix), others store `a1b2c3...` (bare hex), others store `sha256` as a nested field name. Code must strip/add prefixes inconsistently.

**Why it is harmful:** Creates join failures, silent dedup misses, and brittle string manipulation.

**Correct approach:** The canonical `doc_key` is the bare 64-character hex digest. The `sha256:` prefix is a storage/display convention only. All comparison and lookup operations must normalize to bare hex before matching. New code should store bare hex; legacy code should strip prefixes at read boundaries.

---

## 9. Likely Implementation Surfaces

The following files and modules are likely to require changes when implementing the provenance and reuse contract. This section identifies them without implementing the changes.

### 9.1 Identity convergence (field name migration)

| File | Current state | Likely change |
|---|---|---|
| `scripts/data/document-index/config.yaml` | `primary_key: content_hash` | Add `canonical_identity_field: doc_key` or rename. |
| `scripts/data/document-index/provenance.py` | Dedup key is `content_hash` | Accept `doc_key` as synonym; emit `doc_key` in merged output. |
| `scripts/data/document-index/phase-b-claude-worker.py` | Uses `content_hash` field, emits `sha256` in output | Normalize output field name to `doc_key`. |
| `scripts/data/document-index/reclassify-audit.py` | Strips `sha256:` prefix manually | Centralize prefix-stripping into a shared utility. |
| `scripts/data/document-index/subcategory-classify.py` | Same `sha256:` prefix stripping | Same centralization. |
| `scripts/data/doc_intelligence/schema.py` | `DocumentMetadata.checksum` | Rename or alias to `doc_key` for consistency. |
| `scripts/data/doc_intelligence/index_builder.py` | Manifest-index uses `checksum` field | Rename or alias to `doc_key`. |

### 9.2 Reuse decision logic

| File | Current state | Likely change |
|---|---|---|
| `scripts/knowledge/llm_wiki.py` | `ingest` reads raw files directly; no reuse check | Add pre-ingest check: query registry for existing summary/extraction before reading raw. |
| `scripts/data/doc_intelligence/orchestrator.py` | Computes checksum and builds manifest | Add `status` field to output; record whether extraction was incremental or full. |

### 9.3 Promotion path

| File | Current state | Likely change |
|---|---|---|
| `scripts/data/doc_intelligence/promoters/*.py` | Emit `content_hash(body)` for promoted-artifact integrity | Add source `doc_key` as a separate comment/metadata field for traceability. |
| `scripts/knowledge/llm_wiki.py` | `batch-ingest` takes metadata files | Add mode that ingests from registry+summaries rather than raw files. |

### 9.4 Registry and ledger

| File | Current state | Likely change |
|---|---|---|
| `data/document-index/standards-transfer-ledger.yaml` | Uses `id` as primary key; `doc_path`/`doc_paths` for location; no `doc_key` field | Add `doc_key` field per standard. |
| `data/document-index/registry.yaml` | Aggregate statistics only | Potentially extend or federate with per-document `doc_key` lookups (scope for #2136). |
| `data/document-index/mounted-source-registry.yaml` | Source-root level; no per-document `doc_key` | No change needed at this level; per-document identity lives in `index.jsonl`. |

---

## 10. Open Questions / Residual Risks

1. **Field name migration strategy:** Should the codebase migrate from `content_hash` to `doc_key` all at once, or support both names during a transition period? A dual-name period reduces breakage risk but adds complexity. Recommend: support both at read boundaries, emit `doc_key` in new code, migrate legacy files in a single coordinated PR.

2. **`sha256:` prefix normalization:** The prefix appears in shard files and some summary lookups. Should a shared utility function be added to `provenance.py` or a new `identity.py` module? Recommend: add to `provenance.py` as `normalize_doc_key(raw: str) -> str`.

3. **Standards-transfer-ledger `doc_key` population:** The ledger currently identifies standards by human-readable `id` (e.g., `API-RP-1111`) without a `doc_key`. Populating `doc_key` requires hashing source files, which requires mount access. This should be a Phase E back-population task.

4. **Promoted-artifact `doc_key` back-links:** Current promoters emit `content_hash(body)` (hash of the output). Adding a `doc_key` back-link to the source requires threading the source document's hash through the promotion pipeline. This is a non-trivial plumbing change.

5. **Wiki ingest reuse gating:** The `llm_wiki.py` `ingest` command currently reads raw files directly. Adding a reuse check requires the wiki CLI to query the registry, which couples two currently independent subsystems. This coupling is architecturally correct (L3 should read from L2) but needs careful API design.

6. **Cross-machine `doc_key` verification:** When a document exists on multiple machines, the `doc_key` should be identical. But if machines have subtly different file copies (e.g., different PDF metadata from re-downloads), the `doc_key` will differ. The `provenance.py` merge logic handles this by treating them as separate documents. This is correct behavior but may surprise users who expect "the same standard" to have one identity.

---

## 11. Recommended Follow-On Implementation Sequence

Based on the implementation surfaces identified in Section 9 and the dependency order from the parent operating model:

| Order | Work item | Scope | Depends on |
|---|---|---|---|
| 1 | Add `normalize_doc_key()` utility to `provenance.py` | Small — one function, strips `sha256:` prefix, validates hex length | Nothing |
| 2 | Add `doc_key` field to `standards-transfer-ledger.yaml` | Medium — Phase E back-population script, requires mount access | #1 |
| 3 | Normalize identity field names in pipeline scripts | Medium — coordinated rename across Phase B/C/E scripts | #1 |
| 4 | Add reuse-check to `llm_wiki.py` ingest | Medium — query registry before reading raw files | #1, registry must be queryable |
| 5 | Add source `doc_key` back-link to promoter outputs | Medium — thread source hash through promotion pipeline | #1, #3 |
| 6 | Build wiki-from-registry promotion mode in `llm_wiki.py` | Large — new ingest mode that reads from summaries/extractions | #4 |

These items should be captured as implementation issues under #2207 or as sub-tasks of #2136 (accessibility registry), depending on whether they primarily affect provenance or accessibility.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| `doc_key` | SHA-256 hex digest of a source document's binary content. The canonical identity. |
| `content_hash` | Legacy field name for `doc_key` in `index.jsonl` and pipeline scripts. |
| `checksum` | Legacy field name for `doc_key` in `doc_intelligence/schema.py`. |
| `provenance` | Array of `{source, path, host, discovered}` entries tracking where a document was found. |
| `promotion` | The act of converting document-intelligence outputs (summaries, extractions) into durable wiki entries at L3. |
| `reuse` | Using existing L2 outputs (summaries, extractions, promoted artifacts) instead of reparsing raw L1 documents. |
| `reparse` | Going back to the raw L1 document to produce new L2 outputs, when existing outputs are insufficient. |
