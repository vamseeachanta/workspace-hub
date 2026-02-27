# Plan: Document Intelligence Agent Team (WRK-561..567, WRK-572..573)

## Context

The document index has 1,033,789 records but the linkage layer is thin:
- `digitalmodel.yaml` has 9 calc_examples entries covering pipeline/structural/marine/CP
- `doris.yaml`, `saipem.yaml`, `rock-oil-field.yaml` have **zero** calc_examples entries
- `calc-examples-mapper.py` does not exist (WRK-566 tooling missing)
- `specs/data-sources/script-audit.yaml` does not exist (WRK-573 missing)
- WRK-567 back-link pass is blocked until 561/562/563 complete

**Goal:** Close all 8 pending WRK items via a 3-agent parallel team, with a
final cleanup agent for WRK-567 after the parallel wave completes.

---

## File Conflict Analysis

| WRK items | Target files | Conflict? |
|-----------|-------------|-----------|
| WRK-561, 562, 563, 572 | `specs/data-sources/digitalmodel.yaml` | YES — same file |
| WRK-564 | `specs/data-sources/doris.yaml` | No |
| WRK-565 | `specs/data-sources/saipem.yaml`, `rock-oil-field.yaml` | No |
| WRK-566 | `scripts/readiness/query-docs.sh` (extend), new `calc-examples-mapper.py` | No |
| WRK-573 | new `specs/data-sources/script-audit.yaml` | No |
| WRK-567 | 78 WRK item `.md` files in `.claude/work-queue/` | No (after wave 1) |

---

## Team Structure

### Agent Alpha — digitalmodel.yaml enrichment
**WRK items:** WRK-561 → WRK-562 → WRK-563 → WRK-572 (sequential, same file)
**File:** `specs/data-sources/digitalmodel.yaml`
**Work:**
1. WRK-561: Add structural calc_examples — fatigue reports, S-N curve workbooks,
   stress-strain calcs (API-RP-2A-WSD-22nd section). 3 files from 31245/31279/611 projects.
2. WRK-562: Add marine calc_examples — wave scatter diagram (31245-CAL-0003),
   RAO data (31242-CAL-0007-1/2), BOP fatigue (31290-CAL-001-01), buoy calcs.
   Augment DNV-OS-E301 and API-RP-2P entries.
3. WRK-563: Add CP calc_examples — 2100 BLK31 SLOR CP design reports (DNV-RP-B401),
   corrosion FE workbooks (0143-CAL-0002/0005/0007), S-N with free corrosion.
   Augment DNV-RP-B401 and add ISO-15589-2 entries.
4. WRK-572: Add `fea_models:` section — 3 ANSYS model groups (VIV modal, SCF local,
   wave fatigue load cases) with path_pattern, domain, standards, host fields.
**Commit:** one commit per WRK item in digitalmodel + hub

### Agent Beta — other repo calc_examples
**WRK items:** WRK-564, WRK-565 (parallel, different files)
**Files:** `specs/data-sources/doris.yaml`, `specs/data-sources/saipem.yaml`,
           `specs/data-sources/rock-oil-field.yaml`
**Work:**
- WRK-564: Add `calc_examples:` section to doris.yaml — ≥10 pipeline calc files
  across DNV-OS-F101 (wall thickness), API-RP-1111 (propagation buckle),
  DNV-RP-F109 (on-bottom stability), DNV-RP-F110 (upheaval buckling), pipelay calcs.
  Query `index.jsonl` for matching files using `scripts/readiness/query-docs.sh`.
- WRK-565: Add `calc_examples:` section to saipem.yaml and rock-oil-field.yaml —
  pipelay analysis (0611-RES-0175-01), tensioner/FDAS calcs (0145-CAL series).
**Commit:** one per WRK item

### Agent Gamma — tooling + script audit
**WRK items:** WRK-566, WRK-573 (independent new files)
**Files:** `scripts/readiness/query-docs.sh` (extend), new
           `scripts/data/document-index/calc-examples-mapper.py`,
           new `specs/data-sources/script-audit.yaml`
**Work:**
- WRK-566:
  - Extend `query-docs.sh` with `--calc-only` flag (filter paths containing `/CAL/`
    or `-CAL-` or `-RPT-`) and `--standard <id>` flag (keyword match on id/org/keywords)
  - Create `scripts/data/document-index/calc-examples-mapper.py`:
    loads index.jsonl, scores records by keyword match to standard ID, outputs
    YAML block compatible with calc_examples schema. CLI: `--standard`, `--domain`,
    `--top N` (default 5).
  - Tests: 3 standard lookups (DNV-OS-F101, API-RP-2A-WSD, DNV-RP-B401)
- WRK-573:
  - Scan index.jsonl for `.py` files in project archive paths
  - Read representative scripts from 4 categories (OrcaFlex model builder,
    ANSYS Workbench, DeepScale surveillance, Blender ocean)
  - Run `scripts/legal/legal-sanity-scan.sh` on 1 script per category
  - Write `specs/data-sources/script-audit.yaml` with portability ratings,
    target_repo, legal_check status, and follow-up WRK suggestions
**Commit:** one per WRK item

---

## Wave 2: WRK-567 (after wave 1 completes)

Run as a single final agent (or in the main session):
- Match each WRK-482..559 standard ID against calc_examples entries in all 5 YAMLs
- Add `test_data:` block to matching WRK item front-matter
- Regenerate `INDEX.md` via `.claude/work-queue/scripts/generate-index.py`
- Legal scan pass

---

## Sequencing

```
Wave 1 (parallel):
  Agent Alpha:   WRK-561 → WRK-562 → WRK-563 → WRK-572   [~60 min, sequential internally]
  Agent Beta:    WRK-564, WRK-565                          [~30 min, parallel internally]
  Agent Gamma:   WRK-566, WRK-573                          [~45 min, parallel internally]

Wave 2 (after all Wave 1 agents complete):
  Main session:  WRK-567                                   [~20 min]
```

---

## Cross-Review Gate

Each agent must run before committing:
```bash
scripts/review/cross-review.sh <changed_file> all
```
Codex is a hard gate. If Codex quota is exhausted, manual review + note in commit.

---

## Acceptance Criteria (aggregate)

- [ ] digitalmodel.yaml `calc_examples` grows from 9 to ≥15 standard entries with files
- [ ] digitalmodel.yaml gains `fea_models:` section with 3 model groups
- [ ] doris.yaml has `calc_examples:` with ≥10 pipeline calc files
- [ ] saipem.yaml and rock-oil-field.yaml both have `calc_examples:` sections
- [ ] `calc-examples-mapper.py` exists and outputs valid YAML for 3 test standards
- [ ] `query-docs.sh --calc-only` and `--standard` flags work
- [ ] `specs/data-sources/script-audit.yaml` exists with 4 categories, legal scan run
- [ ] All WRK-482..559 items with matching calc files have `test_data:` field
- [ ] Legal scan passes on all committed files
- [ ] All 8 WRK items moved to done/
