# <CLIENT_SHORT_NAME> Data Cycle Contract

This repository is the private <CLIENT_SHORT_NAME> LLM-wiki target. It is for readable, curated, source-grounded knowledge and evidence ledgers. It is not the raw-data dumping ground.

## Layers

### 1. Data layer

| Level | Residency | Purpose | Public eligible? |
| --- | --- | --- | --- |
| Raw project data | `/mnt/ace/<CLIENT_RAW_ROOT>/` | Original client/project inputs, large engineering files, PDFs, models, spreadsheets, solver archives | No |
| Readable source derivatives | private/local only, promoted into this repo only when safe | OCR/text/markdown/table extracts with source IDs and privacy class | No, unless explicitly sanitized |
| Private <CLIENT_SHORT_NAME> wiki | `<CLIENT_PRIVATE_REPO>` | Curated pages, extraction ledgers, report provenance, chatbot knowledge base inputs | No |
| Public llm-wiki derivatives | public `llm-wiki` only after promotion | Generic sanitized engineering knowledge with client identifiers removed | Yes, after explicit promotion gate |

### 2. Execution layer

Execution must declare:

- input data path and source class
- tool/code path and version
- compute host/environment
- generated raw outputs
- evidence manifest path
- promotion decision and confidence score

No execution output becomes client-facing until it has a traceable evidence manifest.

### 3. Report layer

Report outputs include:

- raw analysis output
- internal HTML reports
- client-facing HTML reports
- limited PDFs generated from approved HTML/report sources
- chatbot knowledge packs and retrieval indexes

Report residency must mirror source-data residency unless an explicit promotion gate says otherwise. Client/private inputs cannot flow into public reports, public wiki pages, or public chatbot packs without sanitization review.

## Gate rule

Raw data never moves directly to public `llm-wiki`. Promotion path is:

```text
raw source -> readable derivative -> private <CLIENT_SHORT_NAME> wiki -> reviewed/sanitized derivative -> public llm-wiki, if appropriate
```

Each transition needs a ledger entry.
