# Plan: WRK-1153 — Extract doc-research-download patterns into reusable skill + lib

## Context

WRK-1151 (naval architecture doc research) produced three artifacts that will be needed
verbatim by WRK-1152 (electrical engineering) and all future domain download WRKs:
- A bash `download()` / `log()` function pair currently embedded in `download-naval-arch-docs.sh`
- A resource-catalog YAML schema currently implicit in `naval-architecture-resources.yaml`
- A repeatable 6-step workflow currently undocumented outside the WRK itself

Without extraction, each new domain WRK duplicates 30+ lines of bash and reinvents the schema.

## Deliverable 1 — `scripts/lib/download-helpers.sh`

**What to extract** from `scripts/data/naval-architecture/download-naval-arch-docs.sh`:
- Line 19: `log()` function — ISO-8601 timestamp + tee to `${LOG_FILE}`
- Lines 21–47: `download()` function — skip-if-exists, dry-run, wget (3 tries, 60s), cleanup on fail

**New file structure** (matches pattern of `scripts/lib/uv-env.sh` and `python-resolver.sh`):
```bash
#!/usr/bin/env bash
# ABOUTME: Shared download helpers — source this file; set LOG_FILE and DRY_RUN before sourcing
# Usage: source scripts/lib/download-helpers.sh
# Callers must export: LOG_FILE (path), DRY_RUN (true|false)

log() { ... }       # timestamp + tee to ${LOG_FILE}
download() { ... }  # download <url> <dest_dir> [filename]
```

**Refactor naval-arch script** — replace lines 19–47 with:
```bash
source "$(git rev-parse --show-toplevel)/scripts/lib/download-helpers.sh"
```
The `DEST`, `LOG_DIR`, `LOG_FILE`, `DRY_RUN` vars already set above this point — no other changes needed.

**Verify**: `bash scripts/data/naval-architecture/download-naval-arch-docs.sh --dry-run` must pass.

## Deliverable 2 — `knowledge/seeds/schema.md`

Documents the **resource-catalog** pattern (used by doc-research WRKs). The knowledge-entries
pattern (`career-learnings.yaml` style with `entries[]`) is a separate concern and out of scope.

**Structure of schema.md**:
```markdown
# Knowledge Seeds — Resource Catalog Schema

## When to use this schema
[doc-research WRKs that download and catalogue domain reference documents]

## Required top-level fields
category, subcategory, created_at

## Standard sections
- textbooks[]    — downloadable PDFs: title, author, year, local_path, source_url, size_mb, topics[], notes
- online_portals[] — non-downloadable resources: title, url, notes
- pending_manual[] — WAF-blocked / borrow-only: title, url, notes

## Bulk section variant
[For 10+ files of same type: use count + local_dir instead of per-file entries]

## Minimal example
[8-line YAML showing one textbook entry]
```

**File location**: `knowledge/seeds/schema.md` (alongside the seed YAML files)

## Deliverable 3 — `.claude/skills/data/doc-research-download/SKILL.md`

**Location**: `.claude/skills/data/doc-research-download/SKILL.md`
(top-level data skill, not nested under a domain subdir — it's cross-domain)

**Frontmatter**:
```yaml
name: doc-research-download
description: >
  Repeatable workflow for domain documentation research WRKs: search for freely-available
  references, download PDFs via shared bash lib, catalogue into knowledge/seeds/<domain>-resources.yaml.
  Use when starting any WRK that collects and indexes domain reference documents.
version: 1.0.0
category: data
related_skills: [workspace-hub/work-queue-workflow]
```

**Body sections**:
1. **Overview** — when to use (any domain doc-research WRK)
2. **6-step workflow** — verbatim from WRK-1151 execution:
   1. Fetch seed URLs, extract linked PDFs
   2. Web search for additional freely-available resources (OCW, archive.org, standards bodies)
   3. Create domain download script sourcing `scripts/lib/download-helpers.sh`
   4. Catalogue into `knowledge/seeds/<domain>-resources.yaml` per `schema.md`
   5. Regenerate document index
   6. Record WAF-blocked / borrow-only items in `pending_manual:` — never skip silently
3. **Script template stub** — 30-line bash template callers copy and fill in URLs
4. **Catalogue YAML template** — minimal 12-line YAML showing required fields
5. **AC checklist** — 6 items matching WRK-1151/1152 ACs
6. **Known WAF patterns** — eagle.org, archive.org borrow-only (from WRK-1151 findings)

## Deliverable 4 (bonus AC) — Update WRK-1152 entry_reads

Add to `knowledge/seeds/electrical-engineering-resources.yaml` path reference and update
`.claude/work-queue/pending/WRK-1152.md` to include in `entry_reads`:
```yaml
entry_reads:
  - .claude/skills/data/doc-research-download/SKILL.md
  - knowledge/seeds/schema.md
```

## Execution Order

1. Create `scripts/lib/download-helpers.sh`
2. Refactor `download-naval-arch-docs.sh` to source it
3. Run `--dry-run` to verify
4. Create `knowledge/seeds/schema.md`
5. Create `.claude/skills/data/doc-research-download/SKILL.md`
6. Update WRK-1152 frontmatter with `entry_reads`

## Files Modified

| File | Action |
|------|--------|
| `scripts/lib/download-helpers.sh` | CREATE |
| `scripts/data/naval-architecture/download-naval-arch-docs.sh` | EDIT (source lib, remove duplicated functions) |
| `knowledge/seeds/schema.md` | CREATE |
| `.claude/skills/data/doc-research-download/SKILL.md` | CREATE |
| `.claude/work-queue/pending/WRK-1152.md` | EDIT (add entry_reads) |

## Verification

```bash
# 1. Dry run — naval arch script still works
bash scripts/data/naval-architecture/download-naval-arch-docs.sh --dry-run

# 2. Lib is source-able standalone
LOG_FILE=/tmp/test.log DRY_RUN=true bash -c 'source scripts/lib/download-helpers.sh && download https://example.com /tmp test.txt && log "ok"'

# 3. Skill file valid YAML frontmatter
python3 -c "import yaml; yaml.safe_load(open('.claude/skills/data/doc-research-download/SKILL.md').read().split('---')[1])"
```

## Spec ref

`specs/modules/replicated-whistling-sparkle.md`
