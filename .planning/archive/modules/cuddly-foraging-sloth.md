# WRK-1181: Research & Literature Gathering Skill

## Context

Every calculation implementation starts with literature research — finding applicable standards, gathering reference documents, and identifying worked examples for TDD. Currently this is ad-hoc; each agent re-discovers the same steps. The doc index has 1M records and the standards ledger tracks 425 standards (55% gaps), but no systematic workflow connects research → download → organize → implement.

The skill skeleton already exists at `.claude/skills/data/research-literature/SKILL.md` with a 6-step workflow. This WRK enhances it with:
- Deep online research per domain (WebSearch + WebFetch)
- Automated download scripts per domain → `/mnt/ace/<repo>/docs/domains/<domain>/literature/`
- Research brief generation for priority domains across all repos

## Deliverables

### 1. Enhanced SKILL.md (update existing)
**File:** `.claude/skills/data/research-literature/SKILL.md`
- Add Step 7: Deep online research (WebSearch for standards, papers, technical references)
- Add Step 8: Download script generation (curl-based, following hydrodynamics pattern)
- Add domain-to-repo mapping table
- Add priority domain list for batch research

### 2. Domain Research Driver Script
**File:** `scripts/data/research-literature/research-domain.py`
- Accepts `--category <domain> --repo <repo>` arguments
- Queries standards ledger for domain gaps
- Queries doc index for existing documents
- Cross-references capability map
- Outputs research brief YAML to `specs/capability-map/research-briefs/`
- Generates download script skeleton at `/mnt/ace/<repo>/docs/domains/<domain>/literature/download-literature.sh`

### 3. Download Script Template
**File:** `scripts/data/research-literature/download-template.sh`
- Curl-based, follows `/mnt/ace/digitalmodel/docs/domains/hydrodynamics/literature/download-literature.sh` pattern
- Sources `scripts/lib/download-helpers.sh`
- Names files as `<author>-<year>-<short-title>.pdf`

### 4. Domain-Repo Mapping Config
**File:** `config/research-literature/domain-repo-map.yaml`
- Maps each engineering domain → target repo + `/mnt/ace/` path
- Priority tier (1=immediate, 2=next, 3=future)

### 5. TDD Tests
**File:** `tests/data/test_research_domain.py`
- Test research brief YAML generation (valid schema)
- Test download script generation (valid bash)
- Test domain-repo mapping lookup
- Test ledger query integration

### 6. Deep Research + Downloads (execution phase)

Priority domains for deep research (Tier 1 — immediate):

| Domain | Repo | Why |
|--------|------|-----|
| geotechnical | digitalmodel | WRK-1179 blocked; pile capacity research brief exists |
| cathodic_protection | digitalmodel | Most mature domain; 128 tests; standards-inventory exists |
| structural/fatigue | digitalmodel | 117 standards mapped; DNV RP C203 done |
| hydrodynamics | digitalmodel | Existing literature folder; extend coverage |
| drilling | OGManufacturing + worldenergydata | Core domain; surveillance + pressure mgmt |
| pipeline | digitalmodel + worldenergydata | Largest ledger domain; pipeline_safety module |
| bsee | worldenergydata | 6,813 standards mapped; regulatory data |
| metocean | worldenergydata | Environmental loading; supports structural/hydro |
| subsea | digitalmodel | Subsea engineering; umbilicals, risers |
| naval_architecture | digitalmodel | Ship design; hull models |

For each Tier 1 domain:
1. Run `research-domain.py` to generate research brief from existing data
2. Use WebSearch to find freely available PDFs, papers, technical references
3. Generate `download-literature.sh` at `/mnt/ace/<repo>/docs/domains/<domain>/literature/`
4. Execute download scripts to gather documents
5. Validate PDFs with `file <path>` (reject HTML/WAF responses)

## Execution Order

1. **Create domain-repo mapping** (`config/research-literature/domain-repo-map.yaml`)
2. **Write TDD tests** (`tests/data/test_research_domain.py`) — RED
3. **Build driver script** (`scripts/data/research-literature/research-domain.py`) — GREEN
4. **Create download template** (`scripts/data/research-literature/download-template.sh`)
5. **Update SKILL.md** with new steps 7-8
6. **Execute Tier 1 research** — spawn parallel agents per domain:
   - Each agent: WebSearch → compile URLs → generate download script → run downloads
   - Save research briefs to `specs/capability-map/research-briefs/<domain>.yaml`
   - Save literature to `/mnt/ace/<repo>/docs/domains/<domain>/literature/`

## Files Changed (5 files — within chunk limit)

| Action | File |
|--------|------|
| Edit | `.claude/skills/data/research-literature/SKILL.md` |
| Create | `scripts/data/research-literature/research-domain.py` |
| Create | `scripts/data/research-literature/download-template.sh` |
| Create | `config/research-literature/domain-repo-map.yaml` |
| Create | `tests/data/test_research_domain.py` |

Plus per-domain artifacts (not counted as code changes):
- ~10 research briefs in `specs/capability-map/research-briefs/`
- ~10 download scripts in `/mnt/ace/<repo>/docs/domains/<domain>/literature/`
- Downloaded PDFs (external storage, not in git)

## Verification

1. `uv run --no-project python -m pytest tests/data/test_research_domain.py` — all pass
2. `uv run --no-project python scripts/data/research-literature/research-domain.py --category geotechnical --repo digitalmodel` — produces valid YAML brief
3. `bash /mnt/ace/digitalmodel/docs/domains/geotechnical/literature/download-literature.sh --dry-run` — shows curl commands
4. `file /mnt/ace/digitalmodel/docs/domains/geotechnical/literature/*.pdf` — confirms real PDFs
5. Research briefs validated against template schema
