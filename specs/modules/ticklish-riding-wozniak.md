# WRK-1126 Plan: Maritime Law Knowledge Data Layer

## Context

Offshore engineering work (OrcaFlex, ANSYS, CFD) operates within maritime legal and regulatory frameworks. The existing `engineering/maritime-legal/SKILL.md` (WRK-633) covers the engineering-analysis interface. WRK-1126 adds the **knowledge data layer**: machine-readable case law and liability convention data that agents can query to flag compliance risks in WRK items.

## Scope (Refined After Resource Intelligence)

Stage 2 found: maritime-legal SKILL.md already exists and covers admiralty law reference, liability framing, and regulatory framework. **No new skill directory needed.**

WRK-1126 delivers:
1. Two YAML seed files in `knowledge/seeds/`
2. A patch to `build-knowledge-index.sh` to auto-discover all `*.yaml` seeds (currently hardcoded to `career-learnings.yaml`)
3. Three pytest schema validation tests

## Critical Discovery: build-knowledge-index.sh Hardcoding

`scripts/knowledge/build-knowledge-index.sh` hardcodes `career-learnings.yaml` by filename. New seed files are silently ignored unless the script is updated to glob `knowledge/seeds/*.yaml`. This must be fixed as part of WRK-1126.

## Files to Create / Modify

| Action | Path | Purpose |
|--------|------|---------|
| CREATE | `knowledge/seeds/maritime-law-cases.yaml` | ≥10 landmark public cases |
| CREATE | `knowledge/seeds/maritime-liabilities.yaml` | ≥5 liability conventions with cap values |
| MODIFY | `scripts/knowledge/build-knowledge-index.sh` | Glob all `*.yaml` seeds (not just career-learnings) |
| CREATE | `tests/unit/test_maritime_seeds.py` | ≥3 schema validation tests |

## YAML Seed Schema (must match existing pattern)

```yaml
---
entries:
  - id: MARITIME-cases-<slug>        # unique, kebab-case
    type: career                      # use "career" for static seeds
    category: maritime-law            # must be "maritime-law" for AC5 query to work
    subcategory: case-law | liability-convention
    title: "Short title ≤100 chars"
    learned_at: "YYYY-MM-DDTHH:MM:SSZ"
    source: maritime-law-cases.yaml
    context: >
      Multi-line narrative: facts, jurisdiction, outcome, significance.
    patterns:
      - "Actionable pattern 1"
      - "Actionable pattern 2"
    follow_ons:
      - type: reference
        title: "Source document"
        url: "https://..."
        added_at: "YYYY-MM-DD"
        note: "Public record"
```

## `maritime-law-cases.yaml` — 10 Landmark Cases

| # | Case | Year | Jurisdiction | Liability Outcome |
|---|------|------|-------------|------------------|
| 1 | MV Prestige | 2002 | Spain/Int'l | €1B+ — broke CLC limits; Bahamas flag state liability |
| 2 | MV Erika | 1999 | France | Total fined; "prejudice écologique" introduced |
| 3 | MV Ever Given | 2021 | Egypt (Suez) | US$916M claim; settled ~US$200M; Shoei Kisen P&I |
| 4 | MSC Flaminia | 2012 | Germany/US | $200M+ cargo claims; COGSA applicability, shipper liability |
| 5 | MV Wakashio | 2020 | Mauritius | US$9.4M MARPOL fine; criminal prosecution; MLC crew welfare |
| 6 | The "Eurasian Dream" | 2002 | UK (LMAA) | Bill of lading carrier vs actual carrier; Hague-Visby Rules |
| 7 | The "Sea Empress" | 1996 | Wales | £60M cleanup; port authority liability; pollution duty of care |
| 8 | The "Amoco Cadiz" | 1978 | France/US | US$477M; established trans-boundary pollution damages |
| 9 | Deepwater Horizon | 2010 | US (BSEE) | US$20B+ settlement; OPA 90 liability caps overridden |
| 10 | The "Torrey Canyon" | 1967 | UK/France | Prompted MARPOL 73/78 and CLC 1969 creation |

## `maritime-liabilities.yaml` — 5+ Conventions

| # | Convention | Cap Formula | Applies To |
|---|-----------|-------------|-----------|
| 1 | CLC 1992 (Civil Liability Convention) | 89.77M SDR for ≥140,000 GT | Oil tanker spills |
| 2 | Bunker Convention 2001 | 3M SDR for ships >400 GT | Bunker fuel spills, non-tankers |
| 3 | HNS Convention 2010 | 250M SDR (ship); 250M SDR (fund) | Hazardous & noxious substances |
| 4 | Athens Convention 2002 | 400,000 SDR per passenger per incident | Passenger death/injury |
| 5 | LLMC 1976/1996 Protocol | Sliding scale by GT (e.g. 6.51M SDR for 70,000 GT) | General maritime claims |
| 6 | OPA 90 (US) | US$2,000/GT or US$17M (vessels) | US waters oil spills; no cap if gross negligence |

## build-knowledge-index.sh Patch

Current (hardcoded):
```python
with open(seeds_dir / "career-learnings.yaml") as f:
    data = yaml.safe_load(f)
```

Target (glob all YAML seeds):
```python
for seed_file in sorted(seeds_dir.glob("*.yaml")):
    with open(seed_file) as f:
        data = yaml.safe_load(f)
        if data and "entries" in data:
            for entry in data["entries"]:
                # existing dedup + append logic
```

The exact patch location will be confirmed during execution by reading the script.

## TDD Tests (`tests/unit/test_maritime_seeds.py`)

1. `test_maritime_cases_required_fields` — every case entry has id, category, subcategory, title, learned_at, source, context
2. `test_maritime_cases_minimum_count` — ≥10 entries in cases YAML
3. `test_maritime_liabilities_minimum_count` — ≥5 entries in liabilities YAML
4. `test_category_is_maritime_law` — all entries in both files have `category == "maritime-law"`
5. `test_cases_ids_are_unique` — no duplicate ids across both files

## Execution Sequence

```
Phase 1 (TDD — tests first, all fail):
  tests/unit/test_maritime_seeds.py — 5 tests

Phase 2 (Data files):
  knowledge/seeds/maritime-law-cases.yaml    (10 entries)
  knowledge/seeds/maritime-liabilities.yaml  (6 entries)

Phase 3 (Script patch):
  scripts/knowledge/build-knowledge-index.sh — glob *.yaml seeds

Phase 4 (Verify):
  uv run --no-project python -m pytest tests/unit/test_maritime_seeds.py -v
  bash scripts/knowledge/build-knowledge-index.sh
  bash scripts/knowledge/query-knowledge.sh --category maritime-law --limit 20
  bash scripts/legal/legal-sanity-scan.sh
```

## Acceptance Criteria (Revised)

1. `maritime-law-cases.yaml` ≥10 entries with full metadata — verified by test + query
2. `maritime-liabilities.yaml` ≥5 conventions with cap values — verified by test
3. `build-knowledge-index.sh` auto-discovers all `*.yaml` seeds — exits 0
4. `query-knowledge.sh --category maritime-law` returns ≥10 results
5. ≥5 pytest tests pass (0 fail)
6. Legal scan passes (no client identifiers)
7. No new skill file needed (existing maritime-legal SKILL.md sufficient)
