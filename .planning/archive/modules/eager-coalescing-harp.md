# WRK-1357: LLM-classify va-hdd-2 remaining content into digitalmodel domains

## Context

va-hdd-2 (`/mnt/ace/data/va-hdd-2`) is a 727 GB legacy HDD dump containing mostly personal/educational literature (GRE, MBA, Finance, Photography, etc.) with minimal engineering content. WRK-1288 completed classification of ace_standards and workspace_spec sources but did not cover va-hdd-2. This task classifies the remaining va-hdd-2 content using the existing document-index pipeline.

**Key insight:** Most content will classify as "other" — the value is confirming what (if any) engineering-relevant material exists in this dump.

## Plan

### Step 1: Add va-hdd-2 source to config.yaml
- **File:** `scripts/data/document-index/config.yaml`
- Add new source entry `va_hdd_2` with path `/mnt/ace/data/va-hdd-2`
- Extensions: `.pdf, .docx, .xlsx, .pptx, .txt`
- Add to `deduplication.source_priority` list (lowest priority)

### Step 2: Run Phase A indexing (dry-run first)
- **Script:** `scripts/data/document-index/phase-a-index.py --source va_hdd_2 --dry-run`
- Review file count and size distribution
- Then run without `--dry-run` to build index entries

### Step 3: Review Phase A manifest
- Check `data/document-index/index.jsonl` for va_hdd_2 entries
- Assess file count — if >1000 files, consider cost before proceeding to Phase B/C
- Report manifest summary to user for approval before LLM classification

### Step 4: Run Phase C classification
- **Script:** `scripts/data/document-index/phase-c-classify.py --source va_hdd_2`
- Uses existing domain keyword routing + LLM fallback
- Budget: haiku model, within daily $20 budget

### Step 5: Generate classification report
- Summarize domain distribution (expect >90% "other")
- Flag any engineering-relevant files for manual review
- Write results to `data/document-index/summaries/va-hdd-2-classification-report.yaml`

## Acceptance Criteria

1. va_hdd_2 source added to config.yaml with correct path and extensions
2. Phase A index contains all eligible files from va-hdd-2
3. All indexed files have a domain classification (Phase C)
4. Classification report generated showing domain distribution
5. Any engineering-relevant files (non-"other") flagged for review

## Pseudocode

1. Edit config.yaml → add va_hdd_2 source block
2. Run `phase-a-index.py --source va_hdd_2 --dry-run` → review count
3. Run `phase-a-index.py --source va_hdd_2` → build index
4. Run `phase-c-classify.py --source va_hdd_2` → classify all entries
5. Query index.jsonl → count by domain → write report YAML
6. Filter non-"other" entries → flag for review

## Test Plan

1. **Config validation:** Parse config.yaml after edit, verify va_hdd_2 source has correct path, host, extensions
2. **Phase A dry-run:** Confirm file discovery works, count > 0, no errors
3. **Phase A output:** Verify index.jsonl contains va_hdd_2 entries with content_hash
4. **Phase C output:** Verify all va_hdd_2 entries have domain field populated
5. **Report accuracy:** Spot-check 5 random "other" and 5 random non-"other" classifications manually

## Files to Modify

- `scripts/data/document-index/config.yaml` — add source
- `data/document-index/index.jsonl` — new entries (pipeline output)
- `data/document-index/summaries/va-hdd-2-classification-report.yaml` — new file (output)

## Verification

```bash
# After Step 1
python scripts/data/document-index/phase-a-index.py --source va_hdd_2 --dry-run

# After Step 3
grep -c '"source_type":"va_hdd_2"' data/document-index/index.jsonl

# After Step 4
python -c "
import json
from collections import Counter
c = Counter()
for line in open('data/document-index/index.jsonl'):
    r = json.loads(line)
    if r.get('source_type') == 'va_hdd_2':
        c[r.get('domain','unclassified')] += 1
print(dict(c))
"
```
