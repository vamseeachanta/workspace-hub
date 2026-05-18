# Data-Governance Usage-Level Matrix for Architecture Review Issues

Use with layered architecture review issues when the user asks about AI-agent raw data, readable raw data, private/public llm-wiki routing, data layers, execution layers, or report/output layers.

## Core rule

Do not treat parseability as publishability. A source can move from native/raw form into readable text/chunks without becoming public. Public llm-wiki receives only public-source material or explicitly sanitized/approved derivatives.

Canonical routing:

```text
raw-data
  -> readable-raw-data
      -> llm-wiki-private
          -> private/client report or private chatbot
          -> sanitized derivative candidate -> llm-wiki-public
      -> sanitized/public-source candidate -> llm-wiki-public
```

## Usage levels

| Level | Definition | Default visibility | Typical locations | Agent default |
|---|---|---|---|---|
| `raw-data` | Native/original source material: PDFs, spreadsheets, emails, exports, solver files, scans, images, proprietary datasets, vendor docs, project archives. Often unparsed and unredacted. | Private/local unless explicitly public-source. | `/mnt/ace/<domain-or-source>/`, `/mnt/ace/client_projects/<client-or-project>/`, raw exports, external-drive ingests. | Read only for inventory/extraction; no public citation/promotion without classification. |
| `readable-raw-data` | Derived text/OCR/markdown/CSV/JSON/chunks/source cards produced from raw data for agent consumption. | Inherits source restrictions from `raw-data`. | extraction output dirs, chunk stores, local/private staging, normalized source cards. | Searchable for agents, but still private/restricted when parent source is private. |
| `llm-wiki-private` | Curated private/client/domain wiki or RAG corpus with normalized, cited, searchable knowledge that is not public-safe. | Private. | private llm-wiki repo, client-private wiki/corpus targets, internal-only RAG indexes. | Allowed for private reports/chatbots; public derivative requires sanitization and approval. |
| `llm-wiki-public` | Public-safe curated wiki content suitable for broad reuse, public GitHub, public docs, public chatbot context, and public reports. | Public. | `/mnt/local-analysis/workspace-hub/llm-wiki/` (nested under workspace-hub since 2026-05-18) or public llm-wiki repo checkout. | Broad agent use allowed, with citations/source provenance. |

## Issue/body requirements

When creating or updating GitHub issues for this class of work, include:

1. A matrix row for each usage level above.
2. Example path classes, using redacted patterns for client-sensitive paths.
3. Allowed/forbidden agent actions per level: read, extract, index, cite, summarize, publish, expose in chatbot, expose in report.
4. Promotion gates between levels: extraction gate, curation gate, sanitization gate, public-publication gate.
5. Source-class/citation requirements so reports and chatbots can combine private and public retrieval without collapsing provenance.
6. Checker/test expectations, such as config schema validation and fail-closed checks for public outputs containing private source classes.

## Anti-patterns

- Do not say `readable-raw-data` is public because it is markdown/text/OCR.
- Do not route client-private data directly into public `llm-wiki`.
- Do not store real client/project names in public issue bodies or public docs when redacted path patterns are sufficient.
- Do not let report generation collapse `llm-wiki-private` and `llm-wiki-public` citations into a single undifferentiated source list.
- Do not treat a GitHub issue/comment matrix as implementation approval; keep normal plan/adversarial-review/user-approval gates.

## Verification checklist

Before reporting success on an issue/comment update:

- Re-query the GitHub issue/comment and capture the URL.
- Confirm the matrix explicitly includes `raw-data`, `readable-raw-data`, `llm-wiki-private`, and `llm-wiki-public`.
- Confirm private-to-public promotion requires sanitization/approval.
- Confirm public summaries use redacted path patterns for client-sensitive roots.
