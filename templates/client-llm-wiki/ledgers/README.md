# Ledgers — usage rules

Ledgers are the audit-trail surface for this private wiki. Every promotion of a raw source into a readable derivative, a private wiki page, or a sanitized public-derivative MUST have a ledger entry.

## When to copy the example

`promotion-ledger.example.yml` is a static schema reference. **Do not edit it.** Instead:

1. When you start a new working ledger, copy it to a dated file:
   ```bash
   cp ledgers/promotion-ledger.example.yml ledgers/promotion-ledger-YYYY-MM-DD.yml
   ```
2. Append entries to that dated file as sources are processed.
3. Multiple dated ledgers may coexist (e.g., one per ingestion campaign). Keep them all; do not consolidate retroactively.

## Field meanings

| Field | Meaning |
|---|---|
| `ledger_version` | Schema version. Bump if entries change shape. |
| `client` | Short client identifier (matches `<CLIENT_SHORT_NAME>`). |
| `entries[].source_id` | Stable identifier for the source. Convention: `<CLIENT_SHORT_NAME_UPPER>-SOURCE-NNNN`. |
| `entries[].source_doc_key` | Stable doc-intel key (shared with #2389). Required for cross-system join. |
| `entries[].source_path` | Absolute path under `/mnt/ace/<CLIENT_RAW_ROOT>/`. |
| `entries[].source_class` | One of: `raw-data`, `readable-raw-data`, `private-wiki`, `public-derivative`. |
| `entries[].input_residency` | One of: `private-client`, `private-internal`, `public-eligible`. |
| `entries[].output_residency` | One of: `readable-local`, `private-wiki`, `public-llm-wiki`. |
| `entries[].readable_derivative_path` | Path to OCR/text/markdown extract. `null` if not yet produced. |
| `entries[].private_wiki_page` | Path to the curated page under `pages/`. `null` if not yet promoted. |
| `entries[].extraction` | How the readable derivative was produced (`version`, `method`, `tool_version`, `extracted_at`). |
| `entries[].confidence` | Per-dimension confidence scores 0.0–1.0 plus operator-set `overall`; see "Confidence sub-fields" below. |
| `entries[].score_metadata` | Who/what produced the score (`scored_by`, `scored_with`, `scored_at`, `rationale_bucket`). |
| `entries[].promotion` | Promotion gate state: `status`, private/public allowances, rationale, `gates`. |
| `entries[].promotion.gates` | `reviewer_clearance`, `legal_clearance`, `sanitization_review`, `public_release_clearance`, `private_release_clearance`. |
| `entries[].revision_lineage` | `current_extraction_version`, `previous_extraction_versions[]`, `supersedes`, `superseded_by`, `revision_trigger`. |

## Confidence sub-fields

The `confidence` block records eight per-dimension scores (range 0.0–1.0) plus an `overall` score:

| Sub-field | What it measures |
|---|---|
| `raw_source_presence` | Is the raw source actually accessible at `source_path`? |
| `readability_or_ocr_quality` | How cleanly does the source render to text? |
| `extraction_completeness` | Did the extraction capture all relevant content? |
| `metadata_completeness` | Are source metadata (author, date, project) populated? |
| `citation_quality` | Are downstream citations to this source unambiguous? |
| `privacy_redaction_classification` | How confident is the privacy classification? |
| `engineering_domain_confidence` | Does the domain classification (mooring, drilling, etc.) hold up? |
| `report_readiness` | Is the extraction suitable to feed into client-facing reports? |

### Combining sub-fields into `overall`

`overall` is **not** automatically computed. The operator sets it deliberately based on the eight sub-fields. Recommended convention:

- If any sub-field is below 0.3, `overall` should not exceed 0.5 regardless of other sub-fields (a single weak dimension caps the whole).
- If all sub-fields are 0.7 or above, `overall` may equal the unweighted mean.
- Otherwise, `overall` should reflect the operator's judgment, biased toward the lowest two sub-fields.

The point is operator judgment, not arithmetic — the sub-fields exist so the rationale is inspectable.

## Readiness classification (derived)

`scripts/client_llm_wiki/promotion_ledger.py` exposes `classify_readiness(entry)`, which returns one of five labels independent of the operator's `promotion.status`:

| Label | Condition |
|---|---|
| `not-started` | No extraction recorded and all confidence sub-fields are 0.0. |
| `partial` | `overall ≤ 0.5` and no release clearance gate is set. |
| `usable-with-caveats` | `overall` in `(0.5, 0.75]` and no release clearance gate is set. |
| `client-ready` | `overall ≥ 0.75` AND all private-release gates cleared (`reviewer_clearance` + `private_release_clearance`). |
| `needs-human-review` | Any single sub-field below 0.3 (caps), OR a release gate cleared but `overall < 0.75`, OR `overall ≥ 0.75` with no clearance recorded. |

**Score is not approval.** A score above 0.75 with no clearance lands in `needs-human-review`, not `client-ready`. Dashboards/reports must use `classify_readiness`, never raw `confidence.overall`, when deciding whether knowledge is client-usable.

## Validation

Every ledger file must:

- be valid YAML (parses without error)
- have `ledger_version`, `client`, and `entries` at the root
- have every entry carry a unique `source_id` plus `source_doc_key`
- declare `source_class`, `input_residency`, `output_residency`
- carry full `extraction` provenance (`version`, `method`, `tool_version`, `extracted_at`)
- carry all eight confidence sub-fields plus `overall`
- carry `score_metadata` (actor, tool, timestamp, rationale bucket)
- carry `promotion.gates` with all five gate keys present
- have `promotion.public_llm_wiki_allowed: true` (or `output_residency: public-llm-wiki`) ONLY when sanitization review, legal clearance, reviewer clearance, and public release clearance are recorded with a non-empty rationale
- carry `revision_lineage` with `current_extraction_version` matching `extraction.version` and a `previous_extraction_versions` list (may be empty)
- never carry credentials, raw-extract bodies, or client-private bulk content — ledgers point to artifacts, they don't embed them

A ledger that violates these rules is invalid and must be corrected before further entries are appended. Programmatic validation is performed by `scripts/client_llm_wiki/promotion_ledger.py::validate()` and fails closed on the first defect.
