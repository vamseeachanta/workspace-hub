# Report Layer Contract (#2729)

The report layer converts execution evidence into bounded human-facing surfaces. It is not a dumping ground for raw outputs and it must not silently promote private/client data into public corpora.

## Levels

| Level | Working name | Contents | Boundary rule |
|---|---|---|---|
| R-L1 | Raw output | logs, CSV/JSON extracts, intermediate figures, model outputs, generated screenshots | Not a deliverable by default; preserve only when evidence or regeneration requires it |
| R-L2 | Evidence bundle | source manifest references, command manifests, validation results, legal scan, checksums, review verdicts | Required for every published claim and client/public handoff |
| R-L3 | Internal report | investigation notes, review packs, operator-only markdown/HTML | May include private context; not public/client-safe without gates |
| R-L4 | Client-facing HTML | sanitized interactive reports, dashboards, demos, HTML-first deliverables | Preferred client deliverable format; requires evidence bundle and sanitization gate |
| R-L5 | Limited PDF | static exports for filing, signature, contractual attachment, or offline delivery | Exception path only; HTML-first remains default; exception reason required |
| R-L6 | Chatbot/query surface | public or private chatbot corpora, query indexes, embeddings, retrieval metadata | Inherits corpus posture and freshness/scope disclosure; cannot be more public than its source corpus without promotion gates |

## Required output residency

Every report artifact declares `output_residency`:

- `public_llm_wiki` — public reusable learning pages or public chatbot corpus.
- `domain_private_corpus` — private/local llm-wiki raw data or internal domain corpus.
- `registered_client_private_corpus` — client/project-private deliverables or source-derived artifacts.
- `ignored_internal_run_artifact` — transient raw output that should not be durable or deliverable by default.
- `no_preserve` — disposable scratch output.

## Published claim contract

Every report-published claim must bind to:

`source_manifest`, `command_manifest`, `validation_result`, `legal_scan`, `checksum`, `review_verdict`, `output_residency`, and `promotion_decision`.

## Report-derived learning

Keyword: report-derived learning.

Report-derived learning is allowed only when routed by output residency. Private/client report observations can become public only after provenance, license, legal, sanitization, and owner-review promotion gates. Otherwise they stay in a private/local corpus or are not preserved.

## HTML-first and PDF-limited policy

Client-facing HTML is the default because it supports interaction, provenance disclosure, and regeneration links. PDF is limited to specific business/legal/offline needs and must carry an exception reason plus the same evidence bundle as HTML.
