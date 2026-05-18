# Data Layer Contract — Issue #2727

This contract defines how workspace-hub separates data inputs, wiki corpora, generated indexes, and publication targets. It implements the approved #2727 scope only; execution-layer routing and report-layer publication remain in their own issues unless explicitly referenced as downstream boundaries.

## Related policy references

- `docs/BUSINESS_BRAIN.md` — existing knowledge-promotion policy: raw/public data enters `llm-wiki` only through source, provenance, license, and legal sanity gates.
- `docs/DATA_RESIDENCE_POLICY.md` — existing data-residence policy: raw API downloads, ZIP archives, bulk source documents, and private/client data remain out of public git; scripts/configs/small license-safe reference data may be tracked.
- `.legal-deny-list.yaml` — centralized denylist for client/private identifiers and infrastructure strings; validation loads it dynamically rather than copying literals into issue artifacts.

## Layer definitions

| Level | Name | Purpose | Default residency | Publication posture |
|---|---|---|---|---|
| D-L1 | Raw data | Original public, mounted, client, standards, or repo-native sources. | raw-data | Never publish directly. |
| D-L2 | Readable raw data | Extracted text/metadata/views derived from D-L1 for review. | readable-raw-data | Private unless source/license/publication checks pass. |
| D-L3 | Curated derivative | Human/agent-reviewed summaries, facts, and learnings with provenance. | llm-wiki-private or repo-public depending on source class | Candidate for private/public wiki only after gates. |
| D-L4 | Publication/retrieval corpus | Public llm-wiki, private client llm-wiki, report/query/chatbot surfaces. | llm-wiki-private or llm-wiki-public | Must match source sensitivity and audience. |

## Data residence crosswalk

| Residence | Meaning | Allowed examples | Hard stop examples |
|---|---|---|---|
| raw-data | Untouched source files, mounted project directories, public API snapshots, vendor/reference PDFs. | `/mnt/ace/<client-or-project-root>`, external public source downloads outside git. | Committing raw PDFs or raw client files to public repos. |
| readable-raw-data | OCR/text/extracted rows, metadata ledgers, temporary review packs. | Private extraction caches, document index metadata. | Publishing extracted licensed/client text as public wiki content. |
| llm-wiki-private | Private/domain/client corpus for restricted learnings. | `/mnt/local-analysis/<client-private-wiki-root>`, private staging. | Treating private corpus as public llm-wiki. |
| llm-wiki-public | Public knowledge graph/wiki content. | `/mnt/local-analysis/llm-wiki` public-safe pages. | Raw private paths, client facts, licensed text, or unreviewed outputs. |

## Default routing rules

1. D-L1 never routes directly to D-L4 public llm-wiki.
2. Private/client data may route to `llm-wiki-private` or private report/chatbot runtime only.
3. Public-source data may route to `llm-wiki-public` only with provenance, license posture, and freshness.
4. Standards-derived constants require citations and legal/source posture; licensed text reproduction is forbidden.
5. Generated indexes and chatbots inherit the strictest source class in their corpus manifest.
6. Raw output, client-facing HTML, limited PDFs, and chatbots are report-layer surfaces; the data layer only supplies residency metadata and corpus boundaries.

## Repo-location decision

`/mnt/local-analysis` is treated as a multi-repo workspace. This issue records repo identity evidence and forbids silent moves of `workspace-hub`, `digitalmodel`, `worldenergydata`, or `llm-wiki`. Any move or canonical repo-placement change needs a follow-up GitHub issue and user approval.

## `/mnt/ace-data` alias decision

`/mnt/ace-data` is a symlink alias to `/mnt/ace` on this host. New durable architecture references should use canonical `/mnt/ace` path families or generalized private placeholders. Existing references are inventoried as cleanup candidates and must not be treated as canonical storage.
