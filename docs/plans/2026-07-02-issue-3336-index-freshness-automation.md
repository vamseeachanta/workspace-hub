# Plan for #3336: Drive-index: freshness automation (incremental refresh crons) + recover lost .ace-knowledge builder

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3336
> **Client:** N/A
> **Project:** (none — repo-internal data infrastructure)
> **Lane:** lane:codex   <!-- matches the issue's lane:codex label; heavy programming per epic #3333 provider routing. Plan authored on lane:claude; implementation is lane:codex -->
> **Review artifacts:** scripts/review/results/2026-07-02-plan-3336-claude.md | scripts/review/results/2026-07-02-plan-3336-codex.md | scripts/review/results/2026-07-02-plan-3336-gemini.md

---

## Resource Intelligence Summary

<!-- Issue class: Data Pipeline / Harness-Infrastructure union.
     Consulted: issue body, epic body, sibling plans (#3334, #3335, #3339),
     live index artifacts on /mnt/ace, aceengineer-admin repo, workspace-hub git
     history, cron machinery (schedule-tasks.yaml, setup-cron.sh, notify.sh),
     live ssh probes of ace-linux-2. -->

### Existing repo code

- **HEADLINE FINDING — the ".ace-knowledge builder" is NOT lost.** It is the `aceengineer_admin.knowledge` subpackage in the **aceengineer-admin repo**: `/mnt/local-analysis/aceengineer-admin/src/aceengineer_admin/knowledge/` — full package (`index/sqlite_backend.py`, `index/unified_index.py` with `scan()`/`scan_all()`, 5 scanners, extractors, anonymizer), wired to a Click CLI group `knowledge` in `cli.py` (lines 71–130: `scan`, search, stats commands). It is **committed** (latest touch `402ba43` "fix(security): deterministic code review findings — SQLi + hardening", 2026-05-23). Its `CREATE TABLE assets` DDL matches the live DB's columns by NAME-SET (the 23 shared columns) but NOT by order — `language`/`page_count`/`word_count`/`last_extracted` were ALTER-appended post-creation, as were `status` and `canonical_path` (≥6 ALTER-added columns from later, unidentified migrations); the name-based refresh-owned-columns contract below is unaffected. The epic-level search missed it because it looked only in `workspace-hub/scripts` and on the drive — the builder lives in a *different repo*, exactly as its design spec says.
- Found (LIVE, archived): `.planning/archive/modules/ace-knowledge-index-system.md` (376 lines, git-tracked, present in the working tree) — the builder's design spec. States: "**Package home:** `aceengineer-admin` repo → `aceengineer_admin/knowledge/` subpackage; **Index location:** `/mnt/ace/.ace-knowledge/index.db`". Originally added at `specs/modules/ace-knowledge-index-system.md` in `963f20cde` (2026-02-24 — history citation only); auto-sync `2b1a8d779` (2026-03-26 — the same date as the DB's last mtime) **R100-RENAMED** it into `.planning/archive/modules/` — it was never deleted, and a plain repo grep for `ace-knowledge` finds it today (review r1 correction).
- Found: sibling plan `docs/plans/2026-07-02-issue-3334-dde-drive-index.md` (on this branch) — designs `scripts/data/drive-index/build_drive_index.py` as a **drive-agnostic, profile-driven** FTS5 builder (YAML drive profiles, deterministic ids, idempotent `ON CONFLICT(file_path) DO UPDATE` upserts, resume = re-walk, **separate hash stage**), and explicitly hands the "ace profile → recover lost builder" stretch to THIS issue (#3334 plan line 221). This plan REUSES that builder; it does not design a new one.
- Found: sibling plan `docs/plans/2026-07-02-issue-3335-drive-index-query-cli.md` — registry schema `config/drive-index-registry.yml`: per-entry `id, adapter, path, coverage, domains, freshness{built_at, staleness_days}, builder, adapter_params`; `builder: null # lost builder — see #3336` on the `ace_knowledge` entry. **No `row_count`/`as_of` fields exist** — #3339's plan filed that schema ask on #3335/#3336 (its lines 197, 369); THIS plan lands it.
- Found: cron machinery — `config/scheduled-tasks/schedule-tasks.yaml` is the **single source of truth** ("HARD RULE: all cron/task-scheduler entries must be declared here. Do NOT add entries directly to crontab"); `scripts/cron/setup-cron.sh` resolves machine → role via `config/workstations/registry.yaml` and renders/installs entries; `scripts/notify.sh <source> <job> <pass|fail> [details]` is the fail-loud JSONL notifier; `scripts/readiness/equality-matrix-cron.sh` is the fail-loud precedent (#2972: "ANY failure emits a JSONL notification (scripts/notify.sh) AND exits non-zero").
- Found: CAD builder `/mnt/ace/_cad-index/scripts/build_cad_index.py` (4,077 bytes, mtime 2026-06-26) — **NOT re-runnable as-is**: its inputs are hardcoded to a dead session scratchpad (`RAW = "/tmp/claude-1000/.../038b8b11-.../cad-raw.tsv"`, `DEDUP = ".../dedup"` — that session's scratchpad no longer exists). "Wrap only" therefore requires regenerating the raw-scan input and parameterizing the two paths.
- Gap: no refresh automation of any kind — no drive-index entries in `schedule-tasks.yaml`, no refresh wrapper, no staleness surfacing in any consumer.

### Standards

Not applicable — data-infrastructure issue; no engineering standard governs it.

| Standard | Status | Source |
|---|---|---|
| — | not applicable | `data/document-index/standards-transfer-ledger.yaml` not relevant to index-refresh tooling |

Repo conventions that DO apply: schedule-tasks.yaml HARD RULE (above); externalize-config-to-YAML rule; cron-PATH hazard (PR #3332, MERGED 2026-07-02T02:30Z, fixed cron-PATH provider probes in the equality collector — refresh commands must carry explicit `PATH=` prefixes and absolute interpreter fallbacks).

### LLM Wiki pages consulted

No relevant wiki pages — repo-internal data/ops infrastructure, no domain-engineering knowledge involved.

### Documents consulted

- Issue #3336 body — scope: recover/rewrite `.ace-knowledge` builder; per-index incremental refresh crons on owner machines; freshness metadata in the registry surfaced by the query CLI; follow cron conventions; failures loud.
- Epic #3333 body — inventory table (freshness column), architecture Layer 0 registry, "Freshness is unmanaged" gap #3, "builder is lost" gap #5 (now corrected by discovery above), sibling ordering "#3336/#3337 hardening" after #3334/#3335.
- `docs/plans/2026-07-02-issue-3334-dde-drive-index.md` — builder design reused wholesale (profiles, upsert semantics, hash-stage separation, ntfs/encoding hardening, ace-profile stretch handed here).
- `docs/plans/2026-07-02-issue-3335-drive-index-query-cli.md` — registry schema + `freshness{built_at, staleness_days}` + `defaults.staleness_days: 90`; CLI orchestrator this plan extends with staleness warnings.
- `docs/plans/2026-07-02-issue-3339-drive-file-nudge-hook.md` — OPEN SCHEMA ASK (its review F1 / Open item): "add an OPTIONAL per-index `row_count`/`as_of` field to the registry schema; the registry-read tier becomes a follow-on change once that field actually exists". This plan lands exactly that.
- `.planning/archive/modules/ace-knowledge-index-system.md` (live, archived by R100 rename `2b1a8d779`; added at `963f20cde` — history only) — builder provenance, package layout, scanner inventory.
- PR #3332 (MERGED 2026-07-02T02:30Z) — "fix(equality): … cron-PATH providers …" — the documented cron-PATH hazard precedent.
- Ops memory — ace-linux-2 crons "silent since 2026-06-30" (equality-matrix reconcile notes) → verified below: **alive again as of 2026-07-02 morning**; flagged as residual operational risk anyway.

### Gaps identified

- No refresh automation exists for ANY index: zero drive-index tasks in `config/scheduled-tasks/schedule-tasks.yaml`; no refresh wrapper script anywhere in `scripts/`.
- No staleness metadata schema: `config/drive-index-registry.yml` does not exist yet (created by #3335; verified missing), and #3335's planned schema has no `row_count`/`as_of`/live-state fields — must be added here (answers #3339's ask).
- No incremental mode in the #3334 builder design: it upserts every walked file each run and has no prune/deletion handling — `--incremental` (skip unchanged) and `--prune` (mark vanished rows) must be added as **additive** flags.
- No committed, runnable CAD index build path: the drive-local script's inputs are dead (scratchpad paths); a raw-scan generator + parameterized vendored copy must be created.
- No failure signal from any scheduled index job: `notify.sh` exists but nothing index-related calls it.
- `.ace-knowledge` refresh must not be a rebuild: the live DB contains 7 non-asset knowledge tables (`standards`, `formulas`, `methodologies`, `reference_data`, `code_patterns`, `cross_references`, `asset_tags`) populated by the aceengineer-admin extraction pipeline — a fresh-DB rebuild would destroy them; refresh must operate **in place on `assets` only**.

### Evidence (embedded verification)

**Issue/PR statuses** (verified 2026-07-02T14:44–14:52Z via `gh issue view` / `gh pr view`):
- `#3336` — OPEN — "Drive-index: freshness automation (incremental refresh crons) + recover lost .ace-knowledge builder" (labels: cat:data, enhancement, lane:codex, priority:medium, status:needs-plan)
- `#3333` — OPEN — "EPIC: Context-aware drive-file search — skill + unified query layer over /mnt/ace + /mnt/dde file indexes"
- PR `#3332` — MERGED 2026-07-02T02:30:00Z — "fix(equality): eliminate collector-artifact false DIVERGES (kanban collation, cron-PATH providers, skills SHA-skew)"

**Lost-builder search + discovery chain** (2026-07-02T14:44:46Z–14:50Z):
```
$ grep -rl "ace-knowledge\|ace_knowledge" /mnt/local-analysis/workspace-hub/scripts \
      /mnt/ace/.ace-knowledge 2>/dev/null | head
/mnt/local-analysis/workspace-hub/scripts/email/gmail-archive-extract.py
      # line 33: Path("/mnt/ace/.ace-knowledge/.legal-deny-list.yaml") — a CONSUMER, not a builder

$ ls -la --time-style=long-iso /mnt/ace/.ace-knowledge/
-rw-r--r--  1 vamsee vamsee  1213304832 2026-03-26 06:03 index.db
-rw-r--r--  1 vamsee vamsee  1211174912 2026-03-26 06:02 index.db.bak
-rw-r--r--  1 vamsee vamsee       32768 2026-07-02 04:39 index.db-shm    # touched TODAY → live reader exists
-rw-r--r--  1 vamsee vamsee           0 2026-06-16 10:20 index.db-wal
drwxrwxr-x  artifacts/ (empty)   backups/ (empty)
      # no scripts on the drive → confirms absence AT THE SEARCHED LOCATIONS

$ git -C /mnt/local-analysis/workspace-hub log --all --oneline --diff-filter=AD -- '*ace-knowledge*'
92f5ffc5b ... / 963f20cde chore(sync): auto-sync 2026-02-24  → adds specs/modules/ace-knowledge-index-system.md (376 lines)
2b1a8d779 chore(sync): auto-sync 2026-03-26
      # --diff-filter=AD reports a D here, but `git show --name-status 2b1a8d779` shows
      # R100 specs/modules/... → .planning/archive/modules/ace-knowledge-index-system.md
      # — a RENAME, not a deletion (review r1 correction); the file is git-tracked and
      # LIVE in the working tree today

$ head .planning/archive/modules/ace-knowledge-index-system.md      # live archived spec
"Package home: aceengineer-admin repo → aceengineer_admin/knowledge/ subpackage
 Index location: /mnt/ace/.ace-knowledge/index.db (SQLite, on NAS)"

$ ls /mnt/local-analysis/aceengineer-admin/src/aceengineer_admin/knowledge/
anonymizer/ artifacts/ config.py extractors/ index/ scanners/ schema.py __init__.py
$ ls .../knowledge/index/    → query_engine.py sqlite_backend.py unified_index.py
$ ls .../knowledge/scanners/ → base.py code_scanner.py project_scanner.py
                               simulation_scanner.py spreadsheet_scanner.py standards_scanner.py
$ git -C /mnt/local-analysis/aceengineer-admin log --oneline -1 -- src/aceengineer_admin/knowledge/
402ba43 fix(security): deterministic code review findings — SQLi + hardening (2026-05-23)
$ grep -n "def knowledge" .../cli.py → line 71: Click group "knowledge" (scan/search/stats commands)
```

**Schema-compat proof** (builder DDL vs live DB, 2026-07-02T14:50Z):
```
aceengineer_admin/knowledge/index/sqlite_backend.py:
  CREATE TABLE IF NOT EXISTS assets ( id TEXT PRIMARY KEY, asset_type, file_path UNIQUE,
    file_name, file_extension, file_size, content_hash, modified_date, source_root,
    discipline, project_code, folder_phase, title, description, language DEFAULT 'en',
    page_count, word_count, content_category, engineering_domain, scan_date,
    extraction_status DEFAULT 'pending', last_extracted, anonymized_title )   # 23 cols
  CREATE VIRTUAL TABLE IF NOT EXISTS assets_fts USING fts5(... content_rowid='rowid')
live /mnt/ace/.ace-knowledge/index.db (python3 stdlib sqlite3, mode=ro):
  same 23-column NAME-SET, but NOT the same order: language, page_count, word_count,
  last_extracted sit AFTER anonymized_title → they were ALTER-appended post-creation
  (the DB predates the current DDL generation), plus status TEXT DEFAULT 'active' and
  canonical_path — ≥6 ALTER-added columns in total (review r1 restatement)
  grep "canonical_path\|ALTER TABLE" sqlite_backend.py → NO MATCHES  # migration origin unknown
  # the refresh contract addresses columns BY NAME → name-set match is what matters; unaffected
```

**Live ace-DB builder-semantics probes** (python3 stdlib sqlite3, `mode=ro`, 2026-07-02T14:46Z):
```
tables: assets, standards, formulas, methodologies, reference_data, code_patterns,
        cross_references, asset_tags (+ assets_fts shadow tables)
extraction_status: extracted 29,091 | pending 1,159,800
scan_date min/max: 2026-02-01T18:43 .. 2026-02-03T16:40      # one 2-day full build, Feb 1–3
source_root: /mnt/ace/docs/disciplines 1,160,637 | /mnt/ace/O&G-Standards 27,343 | /mnt/ace/_ss_repo 911
      # coverage = THREE ROOTS, not the whole drive — refresh scope must match
content_hash NULL: 950 of 1,188,891                          # original builder hashed 99.92%
canonical_path NULL: 1,188,891 (all)   # later column, never populated — NO ACTION NEEDED:
      # ace file_path values are already canonical (/mnt/ace/...); canonical_path stays NULL
      # in v1. #3337 rewrites configs/catalogs only, never index contents — no owner exists
      # for populating this column, and none is required (review r1 clarification)
status: active 1,160,637 | removed 28,254                    # 'removed' tombstone convention ALREADY IN USE
id sample: '0d4919d6-1360-4d3d-ac97-ddbd3fb71c4e' (UUID4)    # ≠ #3334's sha256 ids; opaque, upsert-safe
```

**Freshness inventory** (`ls -la --time-style=long-iso`, 2026-07-02T14:44:52Z):
```
-rw-r--r-- 1213304832 2026-03-26 06:03  /mnt/ace/.ace-knowledge/index.db
-rw-r--r-- 6838796288 2025-12-28 14:25  /mnt/ace/O&G-Standards/_inventory.db
-rwxrwxrwx  623054407 2026-04-17 08:56  workspace-hub/data/document-index/index.jsonl
-rw-rw-r--  154109181 2026-06-26 06:05  /mnt/ace/_cad-index/cad-readability-index.tsv
-rw-rw-r--       4077 2026-06-26 15:49  /mnt/ace/_cad-index/scripts/build_cad_index.py
```

**CAD builder dead-input proof** (`head build_cad_index.py`, 2026-07-02T14:51Z):
```
RAW  = "/tmp/claude-1000/-mnt-local-analysis/038b8b11-fa15-43ae-b5c9-043769dced07/scratchpad/cad-raw.tsv"
DEDUP = "/tmp/claude-1000/-mnt-local-analysis/038b8b11-.../scratchpad/dedup"
      # different session's scratchpad — gone; script cannot re-run without a fresh raw scan
```

**Cron conventions + ace-linux-2 health** (2026-07-02T14:45Z–14:48Z):
```
config/scheduled-tasks/schedule-tasks.yaml header:
  "HARD RULE: all cron/task-scheduler entries must be declared here.
   Do NOT add entries directly to crontab or Windows Task Scheduler."
  fields: machines / roles / requires / prefer / schedule|schedules-per-machine / command / log
scripts/notify.sh: "Usage: bash scripts/notify.sh <source> <job> <status> [details]"
                   "  status: pass | fail"        # quoted verbatim (review r1)
  → appends JSONL to logs/notifications/YYYY-MM-DD.jsonl, always exits 0
scripts/readiness/equality-matrix-cron.sh line 2: "fail-loud weekly ... (#2972)"

$ ssh -o BatchMode=yes ace-linux-2 'crontab -l | head'      # ssh WORKS (BatchMode)
PATH=/home/vamsee/.npm-global/bin:/usr/local/bin:/usr/bin:/bin   # minimal cron PATH — the hazard
">>> workspace-hub managed (role: comms-dispatch+sim-worker) — generated by setup-cron.sh"
$ ssh ace-linux-2 'ls -lt /mnt/local-analysis/workspace-hub/logs/ | head'
repository-sync-2026-07-02.log 08:08 | ai-provider-dispatch 07:15 | monitoring 07:02
      # crons ALIVE as of this morning — the "silent since 06-30" ops note is (currently) cleared;
      # /tmp/workspace-hub-cron.log last write 2026-06-28 03:30 is the WEEKLY Sunday job, not silence
      # r1 note: these ssh probes were session-verified but NOT reproducible under the review
      # sandbox (remote read denied) — treat as a dated observation; setup-cron --dry-run
      # acceptance covers the real risk
```

**Gap proofs** (2026-07-02T14:45Z):
- `ls config/drive-index-registry.yml` → "No such file or directory" → #3335 not yet implemented (registry fields land there per the handshake below).
- `ls scripts/data/drive-index` → "No such file or directory" (from #3334 plan evidence, re-confirmed) → #3334 not yet implemented.
- `grep -n "drive-index" config/scheduled-tasks/schedule-tasks.yaml` → no matches → no refresh tasks exist.

**Reproduction proofs**: N/A — no runtime failure alleged; the issue alleges *absences* (no automation, no staleness signal, "lost" builder), each proven or corrected above. The one factual correction: the builder is not lost (discovery chain embedded above).

<!-- Source count: issue #3336 + epic #3333 + plans 3334/3335/3339 + archived spec (.planning/archive/modules/)
     + aceengineer-admin repo probes + live index.db probes + schedule-tasks.yaml + setup-cron.sh
     + notify.sh + equality-matrix-cron.sh + CAD builder + ssh ace-linux-2 probes + PR #3332
     = 14 distinct sources ≥ 3 required ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-02-issue-3336-index-freshness-automation.md |
| Refresh wrapper (cron entrypoint) | scripts/data/drive-index/refresh-drive-index.sh |
| Builder extensions (additive to #3334) | scripts/data/drive-index/build_drive_index.py (`--incremental`, `--prune`, multi-root profiles, state-file emission) |
| ace drive profile | scripts/data/drive-index/drive-index-config.yaml (`drives.ace` entry) |
| CAD raw scanner (new) | scripts/data/drive-index/cad/scan_cad_raw.py |
| CAD builder (vendored + parameterized) | scripts/data/drive-index/cad/build_cad_index.py |
| Builder provenance doc | scripts/data/drive-index/README.md (ace builder = aceengineer-admin `knowledge` pkg; spec = live `.planning/archive/modules/ace-knowledge-index-system.md`, added `963f20cde`) |
| Registry schema + entries | config/drive-index-registry.yml (freshness fields; builder pointers; static staleness rows) |
| CLI staleness surfacing | scripts/data/drive-index-search/registry.py + search.py (#3335 artifacts, extended) |
| Cron declarations | config/scheduled-tasks/schedule-tasks.yaml (3 tasks) |
| Live state sidecars (NOT committed) | `<index-dir>/refresh-state.json` (e.g., /mnt/ace/.ace-knowledge/refresh-state.json) |
| Tests | tests/data/drive_index_refresh/ (test_incremental_refresh.py, test_registry_freshness.py, test_staleness_cli.py, test_refresh_wrapper.py, test_cad_rebuild.py) |
| Plan review — Claude | scripts/review/results/2026-07-02-plan-3336-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-02-plan-3336-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-02-plan-3336-gemini.md |
| Wiki updates | none (N/A) |
| Docs updates | docs/plans/README.md index row (at implementation-PR time — NOT edited in this authoring pass) |

---

## Deliverable

Scheduled, fail-loud, mtime-based incremental refresh for the three v1 indexes (`.ace-knowledge` on ace-linux-1, `dde-knowledge` on ace-linux-2, CAD TSV on ace-linux-1) driven by `schedule-tasks.yaml` + a hardened cron wrapper that writes a drive-local `refresh-state.json` and emits `notify.sh` failures — **plus** the `.ace-knowledge` build path made reproducible (ace drive-profile of #3334's `build_drive_index.py` for metadata refresh; provenance of the FOUND original builder — aceengineer-admin `knowledge` package — documented and wired into the registry `builder:` field) — **plus** the registry freshness schema (`row_count`, `as_of`, `state_file`, per-index `staleness_days`) that answers #3339's open schema ask and is surfaced by #3335's CLI as "index N days stale" warnings; O&G-Standards `_inventory.db` and master `index.jsonl` explicitly excluded from v1 refresh with documented rationale but given registry staleness metadata so consumers see their age.

**Decision — builder "recovery":** the premise is corrected, not executed. The original builder EXISTS, committed, in aceengineer-admin (`aceengineer_admin.knowledge`; evidence above). Copying its 20+ modules into `scripts/data/drive-index/` would fork a maintained package across repos — rejected. Instead: (a) the registry's `ace_knowledge.builder` field changes from `null` to the cross-repo pointer + CLI invocation; (b) `scripts/data/drive-index/README.md` records the full provenance chain (spec LIVE at `.planning/archive/modules/ace-knowledge-index-system.md` — R100-archived by `2b1a8d779`, added `963f20cde`; package path; CLI group) so it can never be "lost" again; (c) the *reproducible refresh path committed under `scripts/data/drive-index/`* — which is what the acceptance actually needs — is the **ace drive-profile of #3334's `build_drive_index.py`** (metadata + prune only; the extraction/anonymizer stages remain aceengineer-admin's job). This satisfies "do NOT invent a new builder" twice over. Flag for owner at approval.

**Decision — v1 refresh scope:** `.ace-knowledge` + `dde-knowledge` + CAD only. OUT of v1: (1) `O&G-Standards/_inventory.db` — refresh means re-running a heavy text-extraction/chunking pipeline (1,043,616 chunks, 6.84 GB), not an mtime walk; days of compute, distinct pipeline (`phase-a-index.py` consumes, does not build, per #3334 evidence); (2) master `index.jsonl` — dde coverage formally deprecated by #3334 decision (b); ace coverage is superseded by the ace DB for file-level search; #3340 owns the long-term unified-index decision. Both still get registry `freshness` metadata (`as_of` from artifact mtimes: 2025-12-28 / 2026-04-17) so the CLI *warns* about their age instead of hiding it — staleness visibility without refresh automation.

---

## Pseudocode

### 1. Builder extensions (additive flags on #3334's `build_drive_index.py` — no behavior change to existing modes)

```
# profile schema gains: roots: [list]  (back-compat: root: str == [root])
# ace profile (drive-index-config.yaml):
drives:
  ace:
    roots: [/mnt/ace/docs/disciplines, "/mnt/ace/O&G-Standards", /mnt/ace/_ss_repo]
        # EXACTLY the live DB's three source_roots — preserves coverage semantics;
        # whole-drive expansion is a #3340 decision, not v1
    canonical_prefix: /mnt/ace            # paths already canonical on ace-linux-1
    db: /mnt/ace/.ace-knowledge/index.db  # REFRESH IN PLACE — never a fresh DB
    excludes: ['.ace-knowledge', '_cad-index', '$RECYCLE.BIN', 'System Volume Information']

--incremental mode (new):
    pre-load {file_path: (file_size, modified_date)} for rows under the walked roots
        (single indexed SELECT; ~1.2M rows ≈ 200–400 MB dict — acceptable on ace-linux-1;
         fall back to per-batch SELECT if RSS budget exceeded)
    for each walked file:
        if path known AND (size, mtime) unchanged AND status == 'active':
            mark seen, SKIP (no UPDATE → no row churn)
            # status gate (review r1 F2 — tombstone resurrection): a status='removed' row
            # whose file REAPPEARS (even byte-identical, e.g. restored from backup) must
            # NOT be skipped — it falls through to the UPDATE branch, which reactivates it
        if path known AND (changed OR status != 'active'): UPDATE ONLY the refresh-owned columns:
            file_size, modified_date, scan_date, status='active'
            # NEVER overwrite: title, description, discipline, project_code,
            # engineering_domain, extraction_status, content_hash, last_extracted,
            # anonymized_title — those belong to the aceengineer-admin extraction
            # pipeline; clobbering them with #3334's coarser heuristics is data loss
        if path new: INSERT full row via #3334 heuristics (sha256 id; UUID legacy ids
            coexist — id is opaque, file_path is the key)
--prune mode (new, only with --incremental):
    after walk: rows under walked roots with status='active' AND not seen this scan
        → UPDATE status='removed'   # matches the EXISTING tombstone convention
                                    # (28,254 rows already status='removed')
    never DELETE; never touch rows outside the walked roots
finalize: INSERT INTO assets_fts(assets_fts) VALUES('rebuild')
    # v1 keeps bulk rebuild (external-content FTS must be resynced after INSERTs);
    # if measured cost on 1.19M rows exceeds ~10 min, switch to per-row FTS
    # delete+insert for changed rows only (noted as tuning follow-on)
state-file emission (new, all modes): write <db-dir>/refresh-state.json atomically:
    { index_id, host, started_at, finished_at, status: ok|failed,
      row_count, rows_added, rows_updated, rows_pruned, duration_s, error: null|str }
foreign tables (standards, formulas, ...): NEVER touched — refresh opens the existing
    DB and issues statements against assets/assets_fts only (test-pinned)
hash stage: UNCHANGED from #3334 — separate `--hash incremental` invocation; refresh
    crons do NOT hash (950 NULL hashes on ace can be drained manually; dde hashing is
    a #3334 follow-on)
```

### 2. `refresh-drive-index.sh` — hardened cron wrapper (one wrapper, three jobs)

```
#!/usr/bin/env bash
# usage: refresh-drive-index.sh <ace|dde|cad>
set -euo pipefail
TARGET="$1"                                   # assigned up-front (review r1 F9); validate ∈ {ace,dde,cad} or usage-error
REPO_ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
fail() { bash "$REPO_ROOT/scripts/notify.sh" cron "drive-index-refresh-$1" fail "$2" || true
         write refresh-state.json {status: failed, error: $2} if possible
         exit 1 }                             # notify precedent: equality-matrix-cron.sh (#2972)
trap 'fail "$TARGET" "line $LINENO: $BASH_COMMAND"' ERR
PY=$(command -v python3 || echo /usr/bin/python3)   # cron PATH is minimal (PR #3332 hazard):
UV=$(command -v uv || echo "$HOME/.local/bin/uv")   # absolute fallbacks, never bare names
case $TARGET in
  ace)  [ -f /mnt/ace/.ace-knowledge/index.db ] || fail ace "index.db missing"
        run builder: --drive ace --incremental --prune ;;
  dde)  [ -f /mnt/dde/.dde-knowledge/index.db ] || fail dde "index.db missing — #3334 production run not landed?"
        run builder: --drive dde --incremental --prune ;;
  cad)  $PY scripts/data/drive-index/cad/scan_cad_raw.py --root /mnt/ace --out /mnt/ace/_cad-index/cad-raw.tsv
        $PY scripts/data/drive-index/cad/build_cad_index.py --raw ... --dedup /mnt/ace/_cad-index/dedup \
            --out ...tsv.tmp && mv tsv.tmp tsv    # atomic publish; consumers never see partial TSV
        write /mnt/ace/_cad-index/refresh-state.json ;;
esac
run builder = ($UV run --with pyyaml $PY | $PY) build_drive_index.py ...   # uv-first, bare-python fallback
              (uv known-broken on some boxes per ops memory)
on success: notify.sh cron drive-index-refresh-$TARGET pass "rows=N added=A updated=U pruned=P"
```

### 3. Cron declarations (`config/scheduled-tasks/schedule-tasks.yaml` — HARD RULE compliant)

```yaml
- id: drive-index-refresh-ace
  schedule: "30 2 * * 0"                    # weekly Sun 02:30, staggered vs existing jobs
  machines: [ace-linux-1]                   # index lives on ace-linux-1's local mount
  requires: [bash, python3, git]
  command: >-
    PATH=$HOME/.local/bin:$PATH; cd $WORKSPACE_HUB &&
    bash scripts/data/drive-index/refresh-drive-index.sh ace
    >> $WORKSPACE_HUB/logs/drive-index/refresh-ace-$(date +\%Y-\%m-\%d).log 2>&1
  log: logs/drive-index/refresh-ace-*.log
- id: drive-index-refresh-dde
  schedule: "30 3 * * 0"
  machines: [dev-secondary, ace-linux-2]    # dde is local ONLY on ace-linux-2 (never refresh over sshfs/NFS);
                                            # both registry-key + hostname forms listed defensively, matching
                                            # existing entries' style (review r1 F10); ssh health evidence was
                                            # session-verified only — not review-reproducible
  command: same shape, target dde           # DEPENDS on #3334's production DB existing;
                                            # wrapper fails LOUD (notify JSONL) until it does — intentional
- id: drive-index-refresh-cad
  schedule: "0 5 * * 0"
  machines: [ace-linux-1]
  command: same shape, target cad
# command shape mirrors existing entries (equality-report etc.): explicit PATH prefix,
# cd $WORKSPACE_HUB, mkdir'd log dir, per-day log files. Installed via
# `bash scripts/cron/setup-cron.sh` on each owner machine (operator/runbook step).
```

### 4. Registry freshness schema (lands in `config/drive-index-registry.yml`; answers #3339)

```yaml
# per-index `freshness` block gains three OPTIONAL fields (validated by #3335 registry.py):
freshness:
  built_at: "2026-03-26"          # existing (#3335)
  staleness_days: 14              # existing (#3335); per-index override of defaults.staleness_days
  row_count: 1188891              # NEW optional — static snapshot, updated at PR time
  as_of: "2026-07-02"             # NEW optional — date the static snapshot was taken
  state_file: /mnt/ace/.ace-knowledge/refresh-state.json   # NEW optional — LIVE truth
# consumers (CLI, #3339 nudge follow-on): prefer state_file when reachable
# (as_of := finished_at, row_count live, last status visible); fall back to the
# static row_count/as_of. NO git commits from cron — the static fields move only
# via PRs; the sidecar carries live truth. Entries updated/added:
#   ace_knowledge:  builder: aceengineer-admin repo → `aceengineer_admin.knowledge`
#                   (CLI: `aceengineer-admin knowledge scan-all`); refresh: this issue;
#                   staleness_days: 14; state_file as above;
#                   coverage: CORRECTED from #3335's whole-drive `/mnt/ace` claim to the
#                   three PROVEN source_roots (/mnt/ace/docs/disciplines, /mnt/ace/O&G-Standards,
#                   /mnt/ace/_ss_repo) so #3338/#3339 consumers don't over-claim (review r1 F6)
#   dde_knowledge:  (per #3334 handshake) + staleness_days: 14 + state_file
#   cad_readability: builder: scripts/data/drive-index/cad/; staleness_days: 14 + state_file
#   og_standards_inventory: as_of: "2025-12-28", staleness_days: 90, refresh: none
#       reason: "rebuild = full text-extraction pipeline (1.04M chunks); out of v1 — #3340"
#   master_document_index:  as_of: "2026-04-17", staleness_days: 60, refresh: none
#       # 60 not 90 (review r1 F3): as_of is 76 days old at plan date (2026-07-02) — 90 would
#       # not trip until ~07-16; a frozen, deprecated-coverage artifact SHOULD warn now
#       reason: "dde coverage deprecated per #3334(b); superseded for file search — #3340"
```

### 5. CLI staleness surfacing (small extension to #3335's `search.py`/`registry.py`)

```
compute_staleness(entry, now):
    state = read_json(entry.freshness.state_file) if reachable else None
    as_of = state.finished_at or entry.freshness.as_of or entry.freshness.built_at
    days = (now - as_of).days if as_of else None
    stale = days is not None and days > (entry.freshness.staleness_days or defaults)
    return {id, as_of, days_stale, threshold_days, stale, last_refresh_status: state.status or "unknown"}
emit: human mode → one stderr line per stale/failed index:
      "WARNING: index og_standards_inventory is 186 days stale (threshold 90)"
      # 186 = 2025-12-28 → 2026-07-02 (review r1 F3 arithmetic fix)
      "WARNING: index ace_knowledge last refresh FAILED at <ts> — results may be stale"
      --json envelope gains "index_status": [per-index staleness dicts]  (additive key;
      #3338/#3339 consume it later — non-breaking for #3335's schema test, which is
      updated in the same PR)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | scripts/data/drive-index/build_drive_index.py | additive: `roots:` list profiles, `--incremental`, `--prune`, refresh-state.json emission (artifact of #3334 — MUST exist first) |
| Modify | scripts/data/drive-index/drive-index-config.yaml | add `ace` drive profile (3 legacy roots, in-place DB) |
| Create | scripts/data/drive-index/refresh-drive-index.sh | hardened cron wrapper: PATH-safe, notify.sh fail-loud, state sidecar, per-target dispatch |
| Create | scripts/data/drive-index/cad/scan_cad_raw.py | regenerate the CAD raw TSV (replaces the dead scratchpad input) |
| Create | scripts/data/drive-index/cad/build_cad_index.py | vendored copy of `/mnt/ace/_cad-index/scripts/build_cad_index.py` with RAW/DEDUP/OUT parameterized (argv), output atomic; logic otherwise unchanged |
| Create | scripts/data/drive-index/README.md | builder provenance: ace = aceengineer-admin `knowledge` pkg (spec: `.planning/archive/modules/ace-knowledge-index-system.md`; history `963f20cde`), refresh = this profile system; never "lost" again |
| Modify | config/drive-index-registry.yml | freshness schema fields (`row_count`/`as_of`/`state_file`), builder pointers, `refresh: none` + reason on the two excluded indexes, AND correct `ace_knowledge.coverage` to the 3 proven source_roots — not whole-drive `/mnt/ace` (review r1 F6) (artifact of #3335 — MUST exist first; see handshake) |
| Modify | scripts/data/drive-index-search/registry.py | validate new optional freshness fields (reject wrong types; absent = fine) |
| Modify | scripts/data/drive-index-search/search.py | staleness computation + stderr warnings + `index_status` in `--json` |
| Modify | config/scheduled-tasks/schedule-tasks.yaml | 3 refresh task declarations (ace/dde/cad on owner machines) |
| Create | tests/data/drive_index_refresh/test_incremental_refresh.py | add/modify/delete/prune/preserve semantics over fixture trees |
| Create | tests/data/drive_index_refresh/test_registry_freshness.py | schema-field validation |
| Create | tests/data/drive_index_refresh/test_staleness_cli.py | staleness computation + warning + JSON key |
| Create | tests/data/drive_index_refresh/test_refresh_wrapper.py | wrapper failure-signal emission (stubbed notify.sh) |
| Create | tests/data/drive_index_refresh/test_cad_rebuild.py | raw-scan + vendored builder over fixture tree; header pin |
| Update (deferred) | docs/plans/README.md | add this plan to index — at implementation-PR time, NOT in this authoring pass |

Not committed: `refresh-state.json` sidecars, logs, and all drive-local artifacts.

**Sequencing / handshakes:** hard dependency on #3334 (builder + dde production DB) and #3335 (registry + CLI) landing first — epic ordering already says "#3336 hardening" after both. At implementation start, check `git show origin/main:config/drive-index-registry.yml` and `ls scripts/data/drive-index/`; if either sibling is unlanded, STOP and re-sequence (do not create parallel artifacts). The dde cron entry ships in this PR even if #3334's *production run* is pending — the wrapper fails loud ("index.db missing — #3334 production run not landed?"), which is the designed signal, not a bug. **Registry seam with #3337 (review r1 F7):** both this issue (freshness fields, builder pointers, staleness values) and #3337 (`canonical_aliases` extension) edit `config/drive-index-registry.yml` after #3335 — additive, different blocks; land sequentially, whichever merges second rebases (squash-merge stacking lesson).

---

## TDD Test List

Fixture pattern: tests build a tiny tree in `tmp_path`, run the builder to create a fixture DB, then mutate the tree (add/modify/delete) and re-run with `--incremental --prune`. A "legacy" fixture DB variant is created with UUID ids + populated extraction columns + a foreign `standards` table to pin preservation semantics. All: `uv run pytest tests/data/drive_index_refresh/ -v`.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_incremental_picks_up_added_file | new files indexed | add 1 file, re-run | row present, rows_added==1 in state file |
| test_incremental_updates_modified_file | mtime/size change detected | touch + append to 1 file | file_size/modified_date/scan_date updated; status active |
| test_incremental_skips_unchanged | no row churn on unchanged files | re-run with no tree changes | rows_updated==0; scan_date of untouched rows unchanged |
| test_prune_marks_removed_not_deleted | deletion handling matches live convention | delete 1 file, re-run --prune | row retained with status='removed'; count unchanged |
| test_removed_row_reactivated_on_reappearance | tombstone resurrection (review r1 F2) | delete file → --prune (status='removed') → restore byte-identical file → re-run --incremental | row status back to 'active'; visible to status='active' consumers |
| test_prune_scoped_to_walked_roots | prune never reaches other roots | DB row under un-walked root | untouched (still active) |
| test_update_preserves_extraction_columns | refresh never clobbers extraction pipeline output | legacy row with title/discipline/extraction_status='extracted'/content_hash set; modify file | those columns unchanged after refresh; only size/mtime/scan_date/status move |
| test_refresh_preserves_foreign_tables | in-place refresh, not rebuild | fixture DB with populated `standards` table | table + rows intact after refresh |
| test_refresh_preserves_legacy_uuid_ids | id stability across builder generations | legacy UUID-id row, modified file | id unchanged (upsert on file_path); new files get sha256 ids |
| test_multi_root_profile | `roots:` list walked, single-root back-compat | profile with 2 roots / with `root:` str | both roots' files indexed / str accepted |
| test_fts_synced_after_incremental | FTS sees new rows | add file `riser_vortex.dat`, refresh | `assets_fts MATCH 'vortex'` hits it |
| test_state_file_written_on_success | live freshness sidecar | successful run | refresh-state.json: status ok, row_count/added/updated/pruned/duration present, atomic (no .tmp left) |
| test_state_file_and_exit_on_failure | failure is recorded + propagated | builder pointed at nonexistent DB dir (or injected exception) | status failed + error string; process exit != 0 |
| test_wrapper_notify_on_failure | LOUD failure signal (the silent-cron hazard) | run refresh-drive-index.sh with stubbed `scripts/notify.sh` + failing target | notify stub called with (`cron`, `drive-index-refresh-<t>`, `fail`, msg); wrapper exit 1 |
| test_wrapper_notify_pass_summary | success is also visible | stubbed notify + passing target | notify called with `pass` + rows summary |
| test_registry_accepts_freshness_fields | #3339 schema ask landed | entry with row_count/as_of/state_file | registry loads; fields typed (int/date-str/path) |
| test_registry_rejects_bad_freshness_types | validation | row_count: "many" | RegistryError naming entry id |
| test_registry_freshness_fields_optional | back-compat with #3335 entries | entry without new fields | loads fine |
| test_cli_staleness_warning_stderr | consumer-visible staleness | fixture registry entry as_of 400 days old, threshold 90 | stderr WARNING "…days stale"; results still returned; exit 0 |
| test_cli_prefers_state_file | live sidecar beats static field | state_file with fresh finished_at + stale static as_of | not stale; last_refresh_status from sidecar |
| test_cli_state_file_unreachable_fallback | degradation | state_file path nonexistent | falls back to static as_of; no crash |
| test_cli_json_index_status_key | #3338/#3339 contract | --json on fixture registry | `index_status` list with id/as_of/days_stale/threshold_days/stale/last_refresh_status |
| test_cad_scan_raw_format | raw scanner output | fixture tree with .step/.dwg/.sldprt + non-CAD files | TSV rows `size\tmtime\tpath` for CAD extensions only |
| test_cad_builder_output_header_stable | vendored builder = drop-in producer | raw fixture TSV, no dedup dir | output header == `path format ecosystem readability read_tool glb name_description project size mtime`; atomic rename |
| test_schedule_tasks_valid | cron declarations well-formed | repo schedule-tasks.yaml after edit | `uv run python scripts/cron/validate-schedule.py` exits 0; 3 drive-index ids present, machines correct |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/data/drive_index_refresh/ -v`
- [ ] No regression: `uv run pytest tests/` passes (or matches pre-change failure baseline recorded at branch time); #3335's CLI test suite still green after the `index_status` extension
- [ ] `bash scripts/cron/setup-cron.sh --dry-run` on ace-linux-1 renders `drive-index-refresh-ace` + `-cad` (and NOT `-dde`); same on ace-linux-2 renders only `-dde` — machine targeting proven before install
- [ ] Live ace refresh run ON ace-linux-1: completes; `refresh-state.json` written with status ok + row counts; `SELECT count(*) FROM standards` identical before/after (foreign tables untouched); spot-check one pre-existing extracted row's title/extraction_status unchanged; runtime + FTS-rebuild time recorded in the PR AND compared against later Sunday ace-linux-1 job start times (e.g., the 03:30 slot) — schedule-overlap check; re-stagger if the first run exceeds the gap (review r1)
- [ ] One-time pre-refresh backup taken before the FIRST live ace run (`cp index.db index.db.pre-3336.bak` — runbook step; index.db.bak from 03-26 is stale)
- [ ] Live failure drill: run wrapper against a deliberately-missing DB path → `logs/notifications/<date>.jsonl` contains the `fail` event, refresh-state.json (if writable) says failed, wrapper exit != 0 captured in the cron-style log — refresh failures proven LOUD, not silent
- [ ] Live staleness smoke: `uv run python scripts/data/drive-index-search/search.py "mooring" --json` emits `index_status` with `og_standards_inventory` flagged stale (as_of 2025-12-28 → 186 days > threshold 90) and `master_document_index` flagged stale (as_of 2026-04-17 → 76 days > threshold 60 — threshold set to 60 for exactly this reason, review r1 F3), plus matching stderr warnings in human mode
- [ ] CAD rebuild reproduced END-TO-END on ace-linux-1 from the committed scripts (raw scan → vendored builder): output TSV header byte-identical to the live file's; row count within ±5% of 464,170 (drive has churned since 06-26); published atomically
- [ ] Registry entries updated: `ace_knowledge.builder` no longer `null` (points at aceengineer-admin `knowledge` package + CLI); excluded indexes carry `refresh: none` + reason; all freshness fields validate
- [ ] Crons installed on both owner machines via `setup-cron.sh` (operator-confirmable: `crontab -l | grep drive-index` on each box) — note: agent may need to hand this to the operator per permission constraints
- [ ] Review artifacts posted to scripts/review/results/ (3 providers)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MINOR** | Evidence base re-verified genuine; 3 MEDIUM defects (false "deleted spec" narrative — it was an R100 archive rename; tombstone-resurrection skip bug; staleness-smoke arithmetic false on plan's own dates) + 8 smaller nits — all addressed in r1 revisions below |
| Codex | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |
| Gemini | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |

**Overall result:** PASS after revisions (Claude r1)

Revisions made based on review:
- **F1** — spec provenance corrected: `2b1a8d779` was an R100 RENAME to `.planning/archive/modules/ace-knowledge-index-system.md` (git-tracked, live, 376 lines), not a deletion; README/registry provenance now points at the live archived path with `963f20cde` cited as history only; the "deleted, which is why repo searches came up empty" narrative removed (Resource Intel, Documents consulted, Evidence discovery chain, Artifact Map, Deliverable decision, Files to Change).
- **F2** — incremental skip branch now requires unchanged `(size, mtime)` AND `status=='active'`; a removed row whose file reappears (even unchanged) falls through to the UPDATE branch and is reactivated; `test_removed_row_reactivated_on_reappearance` added (Pseudocode §1, TDD list).
- **F3** — staleness arithmetic fixed: `master_document_index.staleness_days` set to 60 (its as_of 2026-04-17 is 76 days old, so the smoke actually trips); "552 days" example corrected to 186 for og_standards_inventory (Pseudocode §4/§5, Acceptance).
- **F4** — DDL evidence restated: live DB matches the builder DDL by NAME-SET, not order; `language/page_count/word_count/last_extracted` were ALTER-appended post-creation (≥6 ALTER-added columns total); name-based contract explicitly unaffected (Resource Intel, Evidence).
- **F5** — `canonical_path` NULL column: dangling "(→ #3337)" replaced with explicit "no action needed — file_path is already canonical; canonical_path stays NULL in v1" (Evidence).
- **F6** — registry edit list now also corrects #3335's `ace_knowledge.coverage` from whole-drive `/mnt/ace` to the 3 proven source_roots so #3338/#3339 consumers don't over-claim (Pseudocode §4, Files to Change).
- **F7** — registry-file seam with #3337 stated: sequential merges, second lander rebases (Sequencing).
- **F8** — notify.sh usage quoted verbatim (`<status>` arg, `status: pass | fail` line) (Evidence).
- **F9** — wrapper pseudocode assigns `TARGET="$1"` up-front with validation (Pseudocode §2).
- **F10** — dde schedule entry lists both `dev-secondary` and `ace-linux-2` forms defensively; ssh evidence flagged session-verified / not review-reproducible (Pseudocode §3, Evidence).
- **F11** — WAL-concurrency assumption documented: /mnt/ace is local ext4 on ace-linux-1 (no WAL-over-NFS hazard), flock guards wrapper-vs-wrapper only, aceengineer-admin extraction writes are uncoordinated-but-WAL-safe (Risks). Plus: first-run ace refresh runtime compared against later Sunday ace-linux-1 jobs for schedule overlap (Acceptance).

---

## Risks and Open Questions

- **Risk — issue premise corrected (needs owner ack):** the builder is not lost; it is `aceengineer_admin.knowledge` in aceengineer-admin (committed, security-hardened 2026-05-23). This plan documents + wires it and commits the *refresh* path in workspace-hub instead of copying ~20 modules cross-repo. If the owner insists on a workspace-hub-committed full builder, that becomes a vendoring decision with a real fork-maintenance cost — flag at approval.
- **Risk — hard dependency on unimplemented siblings:** #3334 (builder + dde DB) and #3335 (registry + CLI) are adversarial-reviewed plans, not landed code (`scripts/data/drive-index/` and `config/drive-index-registry.yml` both verified missing 2026-07-02). Implementation MUST start with a sibling-state check and stop if unlanded.
- **Risk — clobbering extraction metadata:** naive upsert would overwrite `title/discipline/extraction_status/content_hash` (populated by the aceengineer-admin pipeline: 29,091 extracted rows, 99.92% hashed) with #3334's coarser heuristics. Mitigated: refresh-owned-columns contract in pseudocode + `test_update_preserves_extraction_columns`.
- **Risk — live readers on the ace DB:** `index.db-shm` was touched 2026-07-02 04:39 — some process opens the DB currently (identity unknown; `gmail-archive-extract.py` reads a deny-list YAML in the same dir, and the CAD/knowledge skills may query it). Refresh runs under WAL with `busy_timeout`; readers are safe under WAL, but the writer must never run twice concurrently — the wrapper takes a flock on the state file. **Stated WAL-concurrency assumption (review r1 F11):** `/mnt/ace` is local ext4 on ace-linux-1 (verified `findmnt`: /dev/sda1 ext4) — no WAL-over-NFS hazard for the cron host; the flock guards wrapper-vs-wrapper ONLY; the aceengineer-admin extraction pipeline is an uncoordinated second writer on `assets` if ever re-run during a refresh window — under WAL + busy_timeout that is a corruption-safe race (write serialization), not a corrupting one. **Open:** identify the live reader (ops curiosity, not a blocker).
- **Risk — FTS rebuild cost:** bulk `rebuild` over 1.19M rows on every weekly refresh may be minutes-heavy; measured on the first live run (acceptance records it). Tuning fallback (per-row FTS sync for changed rows only) is pre-designed, not speculative.
- **Risk — silent-cron history on ace-linux-2:** ops memory says crons went silent 2026-06-30; verified ALIVE 2026-07-02 morning (logs 07:02–08:08). Residual risk is exactly why every refresh emits notify.sh events on BOTH pass and fail, and why the CLI surfaces `last_refresh_status` — a dead cron shows up as growing `days_stale` at query time even if no failure event was ever written.
- **Risk — cron PATH/env (PR #3332 precedent):** commands carry explicit `PATH=` prefixes; wrapper resolves `uv`/`python3` to absolute paths with fallbacks (uv known-broken on some boxes per ops memory).
- **Risk — dde cron fails weekly until #3334's production run lands:** intentional (loud > silent), but generates recurring fail JSONL. If the owner prefers quiet-until-built, flip the wrapper's missing-DB branch to a `skipped` state-file status + pass-with-note — decide at approval.
- **Risk — mixed-id DB (UUID legacy + sha256 new):** ids are opaque and never joined on; `file_path` is the key. Pinned by `test_refresh_preserves_legacy_uuid_ids`.
- **Open — whole-drive ace coverage:** v1 refresh preserves the legacy 3-root coverage (1.19M rows ≅ `/mnt/ace/docs/disciplines` + `O&G-Standards` + `_ss_repo`). Expanding to the full 7.3 TB drive is a coverage-policy decision → #3340.
- **Open — hash-stage cron:** content-hash refresh stays a separate manual/one-off `--hash incremental` invocation per #3334. A bounded weekly hash cron (e.g., 30-min budget) could drain new-file hashes — v2 candidate, not in this plan.
- **Open — `status`/`canonical_path` column provenance:** present in the live DB, absent from the aceengineer-admin DDL, no ALTER found; some later migration added them and something populated 28,254 `removed` tombstones. Refresh adopts the convention regardless; provenance hunt is optional archaeology.
- **Open — registry static `row_count`/`as_of` drift:** static fields move only via PRs (no commits from cron — by design); the live sidecar is authoritative when reachable. Consumers on machines that cannot reach the drive (e.g., #3339's hook on a box without `/mnt/ace`) fall back to static values — acceptable, dated, and exactly what #3339 asked for.

---

## Complexity: T2

**T2** — additive extensions to one existing module + one new wrapper + two vendored/new CAD scripts + registry/CLI/schedule config edits, ~24-test TDD suite over fixture trees, plus supervised live runs on two machines with a failure drill. No new architecture (builder, registry, CLI, cron machinery, and notify convention all exist or are designed by siblings); cross-repo provenance work and in-place-refresh safety semantics push it above T1.
