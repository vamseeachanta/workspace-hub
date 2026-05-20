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
| `entries[].source_path` | Absolute path under `/mnt/ace/<CLIENT_RAW_ROOT>/`. |
| `entries[].source_class` | One of: `raw-data`, `readable-raw-data`, `private-wiki`, `public-derivative`. |
| `entries[].readable_derivative_path` | Path to OCR/text/markdown extract. `null` if not yet produced. |
| `entries[].private_wiki_page` | Path to the curated page under `pages/`. `null` if not yet promoted. |
| `entries[].extraction` | How the readable derivative was produced (method, tool version, timestamp). |
| `entries[].confidence` | Per-dimension confidence scores 0.0–1.0; see "Confidence sub-fields" below. |
| `entries[].promotion` | Promotion gate state: status, private/public allowances, rationale. |
| `entries[].revision_trigger` | When to revisit (e.g., when better OCR models exist). |

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

## Validation

Every ledger file must:

- be valid YAML (parses without error)
- have `ledger_version`, `client`, and `entries` at the root
- have every entry carry a unique `source_id`
- have `promotion.public_llm_wiki_allowed: true` ONLY when a sanitization review is recorded in `promotion.rationale` and `REDACTION-POSTURE.md` defaults have been applied
- never carry credentials, raw-extract bodies, or client-private bulk content — ledgers point to artifacts, they don't embed them

A ledger that violates these rules is invalid and must be corrected before further entries are appended.
