# Plan for #3334: Drive-index: build full dde-drive SQLite FTS index + unfreeze master index dde coverage

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3334
> **Client:** N/A
> **Project:** (none — repo-internal data infrastructure)
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-02-plan-3334-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/document-index/phase-a-index.py` (13,807 bytes) — the master JSONL index builder. Config-driven (`config.yaml` `sources:` section), resume-safe (`load_existing_index()` keyed by path, atomic writes via `atomic_write_index`), already imports `sqlite3` (for the O&G-Standards `_inventory.db` source). Good pattern donor for resume/batching, but it emits JSONL, not SQLite FTS5, and walks dde over a network alias — it is NOT the deliverable.
- Found: `scripts/data/document-index/config.yaml` lines 32–45 — `dde_project` source with 9 roots under the **stale alias** `/mnt/remote/dev-secondary/dde/...` (documents, `0000 O&G`, Literature, Orcaflex, ABSG, g-drive, o-drive, dropbox_contents, `Temp - Oil&Gas`).
- Found: `/mnt/ace/.ace-knowledge/index.db` — the schema to be compatible with: `assets` table (25 columns incl. `asset_type`, `file_path` UNIQUE, `content_hash`, `source_root`, `discipline`, `project_code`, `engineering_domain`, `canonical_path`) + `assets_fts` = FTS5 **external-content** table (`content=assets, content_rowid=rowid`) over `title, description, anonymized_title`. 1,188,891 rows. Its builder script is LOST — recovery is issue #3336, not this issue; however this plan's builder is written drive-agnostic so it *could* rebuild ace too (stretch, handed to #3336).
- Gap: `scripts/data/drive-index/` does not exist. No SQLite index of any kind exists for dde (verified below).

### Standards
Not applicable — data-infrastructure issue, no engineering standard governs it. One repo convention applies:
| Standard | Status | Source |
|---|---|---|
| Canonical drive references (`/mnt/dde`) | in-flight — doc lands via PR #3341 | `docs/standards/canonical-drive-references.md` (in PR #3341; NOT yet on this branch — verified missing in worktree) |

### LLM Wiki pages consulted
No relevant wiki pages — this is repo-internal drive indexing, no domain-engineering knowledge involved.

### Documents consulted
- Issue #3334 body — scope: full-drive FTS5 index, drive-local DB at `/mnt/dde/.dde-knowledge/index.db`, builder under `scripts/data/drive-index/`, canonical paths, decide unfreeze-vs-deprecate for the JSONL layer.
- Epic #3333 body — inventory table confirms dde's only coverage is the frozen JSONL (495,487 `dde_project` rows, frozen 2026-04-17); architecture places this issue as Layer-0/Layer-1 feedstock for the #3335 unified query CLI (which reads BOTH sqlite-fts and jsonl adapters); #3337 will normalize canonical paths across indexes and rewrite `config.yaml` anyway.
- `data/document-index/registry.yaml` — `dde_project: 495487` documents (typed-doc subset, not all files); used as the runtime-estimate floor.
- PR #3341 (OPEN) — `docs/standards/canonical-drive-references.md`, `scripts/setup/nfs-dde-drive.sh`, `scripts/setup/canonical-drive-links.sh`: NFS mount of dde at canonical `/mnt/dde` on other machines is coming; today ace-linux-1 reaches dde via sshfs automount `/mnt/remote/ace-linux-2/dde`.
- `docs/plans/2026-04-20-inbox-drive-triage-session-design.md` — only prior drive-related plan; different scope (inbox triage), no index-builder overlap.

### Gaps identified
- No SQLite index for dde anywhere: 0 dde rows in `/mnt/ace/.ace-knowledge/index.db`, no `/mnt/dde/.dde-knowledge/` directory (both proven below). The builder, its YAML config, the output DB, and its tests must all be built from scratch.
- No `scripts/data/drive-index/` directory exists (proven below).
- `.ace-knowledge` builder lost — schema must be reverse-engineered from the live DB (done; embedded below), not copied from source.
- dde JSONL coverage frozen since 2026-04-17 under a dead path alias — must be either re-run or formally deprecated (decision in this plan: **deprecate**, see Deliverable/Pseudocode).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-02T09:30:31Z via `gh issue view` / `gh pr view`):
- `#3334` — OPEN — "Drive-index: build full dde-drive SQLite FTS index + unfreeze master index dde coverage" (labels: cat:data, lane:codex, status:needs-plan)
- `#3333` — OPEN — "EPIC: Context-aware drive-file search — skill + unified query layer over /mnt/ace + /mnt/dde file indexes"
- PR `#3341` — OPEN — "feat(setup): dde-drive NFS mount + canonical drive-reference convention" (files: `docs/standards/canonical-drive-references.md`, `scripts/setup/canonical-drive-links.sh`, `scripts/setup/nfs-dde-drive.sh`)

**File existence** (`ls -la`, 2026-07-02T09:30:37Z, worktree + mounts):
- EXISTS: `scripts/data/document-index/phase-a-index.py` (13,807 bytes)
- EXISTS: `scripts/data/document-index/config.yaml` (dde roots at lines 35–43)
- EXISTS: `/mnt/local-analysis/workspace-hub/data/document-index/index.jsonl` — 623,054,407 bytes, mtime **2026-04-17** (frozen)
- MISSING (new — this plan creates): `scripts/data/drive-index/build_drive_index.py`, `scripts/data/drive-index/drive-index-config.yaml`, `tests/data/drive-index/test_build_drive_index.py`
- MISSING: `docs/standards/canonical-drive-references.md` in this worktree (arrives via PR #3341)
- MISSING: `/mnt/dde` on ace-linux-1 (`ls: cannot access '/mnt/dde'`) — NFS mount pending PR #3341; sshfs path works today

**ace index.db schema** (python `sqlite3`, read-only URI `mode=ro`, 2026-07-02T09:30:50Z):
```
CREATE TABLE assets (
    id TEXT PRIMARY KEY,
    asset_type TEXT NOT NULL,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    file_extension TEXT,
    file_size INTEGER DEFAULT 0,
    content_hash TEXT,
    modified_date TEXT,
    source_root TEXT,
    discipline TEXT,
    project_code TEXT,
    folder_phase TEXT,
    title TEXT,
    description TEXT,
    content_category TEXT,
    engineering_domain TEXT,
    scan_date TEXT,
    extraction_status TEXT DEFAULT 'pending',
    anonymized_title TEXT
, language TEXT DEFAULT 'en', page_count INTEGER, word_count INTEGER, last_extracted TEXT, status TEXT DEFAULT 'active', canonical_path TEXT)

CREATE VIRTUAL TABLE assets_fts USING fts5(
    title,
    description,
    anonymized_title,
    content=assets,
    content_rowid=rowid
)
-- assets: 1188891 rows
```
Note: `sqlite3` CLI is NOT installed on ace-linux-1 (`command not found`, 2026-07-02T09:30:30Z) — all DB work uses Python stdlib `sqlite3` (module present, library 3.45.1 on ace-linux-2).

**Gap proofs** (2026-07-02T09:30:52Z–09:31:04Z):
- `SELECT count(*) FROM assets WHERE file_path LIKE '%/dde/%' OR source_root LIKE '%dde%'` → **0** → confirms zero dde rows in the ace DB.
- `ls /mnt/remote/ace-linux-2/dde/.dde-knowledge` → "No such file or directory" → confirms no drive-local dde index exists.
- `ls scripts/data/drive-index` (worktree) → "No such file or directory" → confirms builder dir does not exist.

**dde drive + execution host** (`ssh -o BatchMode=yes ace-linux-2`, 2026-07-02T09:30:36Z–09:31:35Z):
```
$ ssh ace-linux-2 'df -h /mnt/dde; mount | grep dde'
/dev/sdc2       2.8T  2.0T  848G  70% /mnt/dde
/dev/sdc2 on /mnt/dde type ntfs3 (rw,relatime,uid=1000,gid=1000,iocharset=utf8)
$ ssh ace-linux-2 'ls /mnt/dde'   # top level (excerpt)
$RECYCLE.BIN / 0000 O&G / ABSG / deckhand / documents / dropbox_contents / g-drive /
Literature / o-drive / Orcaflex / Personal / System Volume Information / Temp - Oil&Gas
+ ~8 loose files at root (PDFs, .doc)
$ ssh ace-linux-2 'ls /mnt/workspace-hub/scripts | head'   # checkout EXISTS
ace / agents / ai / ...
$ ssh ace-linux-2 'cd /mnt/workspace-hub && git log -1 --format="%h %cd"'
2f5eb972f Tue Jun 30 05:09:34 2026 -0500      # 2 days stale → git pull needed before run
$ ssh ace-linux-2 'python3 --version; command -v uv; command -v tmux'
Python 3.12.3 / /snap/bin/uv / /usr/bin/tmux   # sqlite library 3.45.1 (FTS5 available)
```

**Reproduction proofs**: N/A — no runtime failure alleged; this is a build-from-scratch data-infrastructure issue. The "failure mode" is an absence (no dde index), proven under Gap proofs above.

<!-- Source count: issue #3334 + epic #3333 + phase-a-index.py + config.yaml + registry.yaml + ace index.db + PR #3341 + live ssh probes = 8 ≥ 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-02-issue-3334-dde-drive-index.md |
| Builder | scripts/data/drive-index/build_drive_index.py |
| Builder config (YAML, per externalize-config rule) | scripts/data/drive-index/drive-index-config.yaml |
| Tests | tests/data/drive-index/test_build_drive_index.py |
| Output DB (NOT committed — drive-local artifact) | /mnt/dde/.dde-knowledge/index.db (+ build.log, scan_state inside DB) |
| Master-index deprecation edits | scripts/data/document-index/config.yaml, data/document-index/registry.yaml |
| Registry entry (coordination with #3335) | config/drive-index-registry.yml (if landed by then; else registry.yaml note only) |
| Plan review — Claude | scripts/review/results/2026-07-02-plan-3334-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-02-plan-3334-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-02-plan-3334-gemini.md |
| Wiki updates | none (N/A) |
| Docs updates | docs/plans/README.md index row (deferred to implementation PR; not edited in this authoring pass per task scope) |

---

## Deliverable

A committed, drive-agnostic, resume-safe SQLite FTS5 index builder (`scripts/data/drive-index/build_drive_index.py` + YAML config) that, run ON ace-linux-2, produces `/mnt/dde/.dde-knowledge/index.db` — schema-compatible with `/mnt/ace/.ace-knowledge/index.db`, all paths canonical `/mnt/dde/...`, row count reconciled against a fresh `find` — **plus** formal deprecation of the frozen dde JSONL coverage in the master index (decision (b), rationale below), with full TDD coverage over a fixture tree.

**Decision — unfreeze (a) vs deprecate (b): recommend (b) deprecate.** Rationale: (1) #3335's unified CLI reads sqlite-fts and jsonl adapters side by side, so consumers lose nothing; (2) re-running `phase-a-index.py` over dde means re-walking ~half a million docs over sshfs/NFS from ace-linux-1 — the exact NFS-latency trap the issue warns about — to refresh a format that is strictly weaker than the new DB (no FTS, 623 MB flat file); (3) #3337 will rewrite `config.yaml` path aliases anyway, so fixing the alias now just to re-run once is churn; (4) the new DB is drive-local and rebuildable on the owning machine, which is the durable convention (mirrors `.ace-knowledge`). **Deprecation retention semantics (corrected in review — NOT unconditionally non-destructive):** the frozen dde rows survive **resume runs only**. `phase-a-index.py` resume mode merges from existing rows, but `--force` merges from `{}` + enabled sources only — so with `dde_project` disabled, a `--force` rebuild **silently drops all 495,487 dde rows** from `index.jsonl`. Mitigations baked into this plan: (1) the `enabled: false` edit in `config.yaml` carries a loud warning comment beside it ("WARNING: dde rows in index.jsonl survive RESUME runs only — a --force rebuild DROPS all 495,487 dde rows; superseded by /mnt/dde/.dde-knowledge/index.db (#3334)"); (2) the `registry.yaml` coverage annotation for the JSONL reads `frozen 2026-04-17, dde rows lost on --force rebuild`; (3) a retention-semantics test is in the TDD list (`test_force_rebuild_retention_semantics`). Flag for user at approval (epic text says "or deprecate — decide in plan"; this is the plan's decision).

---

## Pseudocode

```
# build_drive_index.py — drive-agnostic; stdlib sqlite3 + pyyaml only
main(argv):
    args: --config drive-index-config.yaml --drive dde   # selects a drive profile
          [--db PATH] [--hash {none,incremental}] [--batch-size 2000]
          [--reconcile] [--limit N (tests)]
    profile = yaml[drives][args.drive]:
        root: /mnt/dde            # physical walk root (on owning machine they coincide)
        canonical_prefix: /mnt/dde
        db: /mnt/dde/.dde-knowledge/index.db
        excludes: ['$RECYCLE.BIN', 'System Volume Information', '.dde-knowledge']
        classify: {topdir→discipline/engineering_domain map, ext→asset_type map}
    open_db(db):                                  # mkdir -p parent
        create assets + assets_fts (external-content FTS5) + scan_state
          — DDL verbatim from .ace-knowledge schema (embedded above) so the two
            drives are column-identical; PRAGMA journal_mode=WAL, synchronous=NORMAL
    scan(root):
        walk via os.scandir, recursive, children sorted (deterministic order);
        prune excluded dir names at any depth; skip symlinks; follow_symlinks=False
        encoding policy (ntfs3 can yield undecodable names): walk with os.fsdecode
            semantics (errors='surrogateescape'); before storage, sanitize every TEXT
            column via .encode('utf-8','backslashreplace').decode('utf-8') — stdlib
            sqlite3 REJECTS surrogate-escaped TEXT, so surrogates never reach the DB
        for each file: stat → row:
            canonical = canonical_prefix + relpath(path, root)
            file_path = canonical_path = canonical   # BOTH columns get the canonical
                # value: file_path is the UPSERT conflict column AND the column the
                # #3335 sqlite_fts adapter reads; canonical_path kept for ace parity
            id = sha256(canonical)[:32]           # deterministic → idempotent upserts
            asset_type/discipline/engineering_domain from classify maps
            title = filename stem; description = parent-dir breadcrumb (FTS fodder)
            anonymized_title = NULL in v1 (assets_fts indexes it; NULL is valid —
                column kept only for ace-schema parity)
            content_hash = NULL (metadata-first pass)
        buffer rows; every batch_size: UPSERT ON CONFLICT(file_path) DO UPDATE,
            update scan_state (progress counters), COMMIT
        batch-failure fallback: if executemany raises (e.g., one poison filename in a
            2000-row batch), retry that batch row-by-row; log + quarantine the failing
            row(s) into the errors counter, keep the rest — one bad name never
            discards a batch
        on restart (resume): re-walk from the START — upserts are idempotent
            (deterministic ids + ON CONFLICT DO UPDATE), so resume == re-run; committed
            batches survive, the redundant re-walk is minutes-cheap and always correct.
            NO "skip until past last-committed path" logic: sorted-DFS preorder is NOT
            lexicographic order, and a deleted last-path breaks any comparator —
            rejected in review as unsound.
        per-entry errors: unreadable entry → log + errors counter, continue (never abort walk)
    finalize():
        INSERT INTO assets_fts(assets_fts) VALUES('rebuild')   # bulk FTS after load
        write scan summary row (scan_date, files, errors, duration)
    reconcile mode (--reconcile):
        n_find = count via same walk, no DB; compare to SELECT count(*);
        print both + delta; exit nonzero if |delta| > 0.1%
    hash stage (SEPARATE invocation, --hash incremental):
        SELECT files WHERE content_hash IS NULL ORDER BY file_size ASC;
        sha256 in 64 KiB chunks; commit per batch; safe to kill/resume anytime
        (2.0 TB used @ ~120–180 MB/s sequential ⇒ ≥4 h ideal, realistically a
         multi-day background job with small-file overhead — hence deferrable)

# master-index deprecation (small, config-only)
config.yaml: dde_project source → enabled: false  (phase-a-index.py already skips
    disabled sources; if no 'enabled' knob exists, comment the source out) +
    LOUD warning comment beside the flag:
    "WARNING: dde rows in index.jsonl survive RESUME runs only — a --force rebuild
     merges from {} + enabled sources and DROPS all 495,487 dde rows.
     Superseded 2026-07 by /mnt/dde/.dde-knowledge/index.db (#3334)"
registry.yaml: annotate dde_project count as
    "frozen 2026-04-17, dde rows lost on --force rebuild" + pointer to new DB
```

Stretch (noted, not in scope — belongs to #3336): `--drive ace` profile with `root/canonical_prefix: /mnt/ace`, `db: /mnt/ace/.ace-knowledge/index.db` would let this same builder regenerate the ace index, recovering the lost builder. The drive-profile design above is what makes that possible; do not run it against the live ace DB in this issue.

**Execution runbook (ON ace-linux-2 — local disk, never NFS/sshfs):**
```
ssh ace-linux-2 'cd /mnt/workspace-hub && git pull'         # checkout is 2 days stale (2f5eb972f)
ssh ace-linux-2 'mkdir -p /mnt/dde/.dde-knowledge'          # MUST precede first run: the nohup
                                                            # log redirect below fails if the
                                                            # directory does not exist yet
ssh ace-linux-2 'cd /mnt/workspace-hub && nohup uv run python \
    scripts/data/drive-index/build_drive_index.py --drive dde \
    > /mnt/dde/.dde-knowledge/build.log 2>&1 &'             # or tmux session; both present
# monitor:  ssh ace-linux-2 'tail -5 /mnt/dde/.dde-knowledge/build.log'
# reconcile: ssh ace-linux-2 'cd /mnt/workspace-hub && uv run python ...build_drive_index.py --drive dde --reconcile'
```
Runtime estimate (metadata pass): registry floor 495,487 typed docs ⇒ total files likely 0.7–1.5 M. Local ntfs3 stat throughput ~1–3 k files/s cold ⇒ walk 6–25 min; with batched SQLite upserts + final FTS rebuild, budget **30–120 min** total. Fallback if `uv` misbehaves (known flaky on some boxes per ops memory): script is stdlib+pyyaml only ⇒ `uv run --with pyyaml` or bare `python3` with pyyaml present.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/data/drive-index/build_drive_index.py | drive-agnostic FTS5 index builder (main implementation) |
| Create | scripts/data/drive-index/drive-index-config.yaml | drive profiles, excludes, classification maps — externalized per YAML-config rule |
| Create | tests/data/drive-index/test_build_drive_index.py | TDD suite over fixture tree (fixtures built in tmp_path by tests) |
| Modify | scripts/data/document-index/config.yaml | disable `dde_project` source + supersession comment (decision (b)) |
| Modify | data/document-index/registry.yaml | annotate dde_project as frozen/superseded → pointer to /mnt/dde/.dde-knowledge/index.db |
| Modify (conditional) | config/drive-index-registry.yml | add dde index entry IF #3335 has landed the registry; else covered by registry.yaml note (see handshake below) |
| Update (deferred) | docs/plans/README.md | add this plan to index — at implementation-PR time, not in this authoring pass |

Not committed: `/mnt/dde/.dde-knowledge/index.db` and build.log (drive-local artifacts, like `.ace-knowledge`).

**Registry-entry handshake with #3335 (explicit ordering):** exactly ONE of the two issues adds the `dde_knowledge` entry to `config/drive-index-registry.yml`. At implementation time, check `git show origin/main:config/drive-index-registry.yml`:
- If #3335 has landed the registry → **THIS plan (#3334) adds the entry** (incl. `adapter_params`).
- If #3335 has NOT landed → this plan only records the ready-to-paste entry (below) and **#3335 adds it** when it creates the registry.

Ready-to-paste entry:
```yaml
  - id: dde_knowledge
    adapter: sqlite_fts
    path: /mnt/dde/.dde-knowledge/index.db
    coverage: {drives: [/mnt/dde], subtree: /mnt/dde}
    freshness: {built_at: "<build date>"}
    builder: scripts/data/drive-index/build_drive_index.py
    adapter_params:
      fts_table: assets_fts
      base_table: assets
      path_column: file_path        # == canonical_path by construction (this builder)
      select_columns: [file_name, file_size, modified_date, engineering_domain]
```

---

## TDD Test List

All tests run against a tiny fixture tree built in `tmp_path` (≈12 files: nested dirs, a `$RECYCLE.BIN` dir with a decoy file, a `System Volume Information` dir, filenames with spaces/`&`/unicode, one 0-byte file, one symlink). `uv run pytest tests/data/drive-index/ -v`.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_schema_matches_ace_columns | schema compatibility contract | fresh DB from builder | `assets` column set == the 25-column list embedded in this plan; `assets_fts` exists with content=assets |
| test_index_row_count_matches_fixture | full walk, correct count | fixture tree (9 indexable files) | `SELECT count(*) FROM assets` == 9 |
| test_excludes_recycle_bin_and_svi | exclusion pruning at any depth | decoy files inside `$RECYCLE.BIN`, `System Volume Information` | those paths absent from DB |
| test_canonical_path_prefix | alias→canonical rewrite | root=tmp fixture, canonical_prefix=/mnt/dde | every `canonical_path` startswith `/mnt/dde/`; no tmp_path leakage |
| test_fts_query_hits | FTS5 actually searchable | file named `riser_fatigue_report.pdf` | `assets_fts MATCH 'riser fatigue'` returns its rowid |
| test_idempotent_rerun | re-run = upsert not duplicate | run builder twice | count unchanged; ids stable (sha256 canonical) |
| test_resume_after_interrupt | resume safety (re-walk-from-start model) | kill after batch 1 (batch-size=3, simulate via --limit / injected exception), rerun | rerun re-walks from start; final count == 9, no dupes (idempotent upserts), scan_state summary updated |
| test_hash_stage_separate_and_incremental | hash pass deferred + resumable | metadata pass then `--hash incremental` | pass 1: all content_hash NULL; pass 2: all populated with correct sha256; partial kill + rerun completes |
| test_unreadable_file_does_not_abort | error tolerance | chmod 000 one file | walk completes, errors counter == 1, other rows present |
| test_symlink_skipped | no symlink traversal | symlink to sibling dir | target not double-indexed |
| test_reconcile_mode | acceptance tooling works | fixture DB + tree | `--reconcile` exit 0, prints matching counts; exit ≠0 after deleting a row |
| test_config_dde_source_disabled | deprecation edit is real | repo `scripts/data/document-index/config.yaml` | dde_project source disabled/absent from active sources parse |
| test_force_rebuild_retention_semantics | F1 retention contract: dde rows survive resume ONLY | tiny JSONL index with fake dde rows + config with dde disabled; run phase-a logic in resume mode, then --force mode | resume: dde rows retained; --force: dde rows gone — pins the documented loss semantics so a future "why did rows vanish" has a test to point at |
| test_surrogate_filename_batch_fallback | undecodable NTFS name doesn't poison a batch | fixture file created with a raw-bytes (non-UTF-8) name (os.fsencode), batch containing it + good rows | batch retried row-by-row; good rows land; poison row stored with backslashreplace-escaped path (or quarantined+counted); no surrogates in any TEXT column |
| test_classification_map_applied | topdir→discipline/domain YAML map drives columns | fixture tree with dirs mapped in config (e.g., `Orcaflex/` → engineering_domain) | rows under mapped dirs carry mapped `discipline`/`engineering_domain`/`asset_type`; unmapped dirs get the declared defaults |

Note (v1 scope): `anonymized_title` stays **NULL in v1** even though `assets_fts` indexes it — NULL is valid FTS input; the column exists purely for ace-schema parity (asserted in test_schema_matches_ace_columns).

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/data/drive-index/test_build_drive_index.py -v`
- [ ] No regression: existing document-index tests still pass (`uv run pytest tests/data/document-index/` — directory selection; `-k` selects by test NAME, not directory, and would silently select nothing)
- [ ] Production run completed ON ace-linux-2 (not over NFS/sshfs): `/mnt/dde/.dde-knowledge/index.db` exists, WAL-checkpointed, openable read-only
- [ ] Row count reconciled: `--reconcile` (same-walk `find`-equivalent count vs `SELECT count(*)`) within ±0.1%; both numbers recorded in build.log and pasted into the PR
- [ ] Zero rows with non-canonical prefixes: `SELECT count(*) FROM assets WHERE canonical_path NOT LIKE '/mnt/dde/%'` == 0; zero rows under `$RECYCLE.BIN` / `System Volume Information`
- [ ] FTS smoke query on production DB returns hits (e.g., `assets_fts MATCH 'orcaflex'`)
- [ ] Kill-and-resume demonstrated once on the production run (or batch-commit evidence in log) — resume-safety proven at scale, not only in tests
- [ ] `config.yaml` dde source disabled + `registry.yaml` supersession note landed (decision (b)); registry entry in `config/drive-index-registry.yml` if #3335 landed
- [ ] Hash stage explicitly NOT required for acceptance (documented as follow-on incremental job); `content_hash` column present and NULL
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | 1 HIGH ("non-destructive deprecation" false under `--force` — 495,487 dde rows silently dropped), 2 MEDIUM (resume skip-until-last-path unsound; surrogate NTFS filenames poison executemany batches), 5 MINOR + 1 INFO (runbook mkdir, file_path=canonical_path, #3335 registry handshake ordering, `pytest -k` mis-selection, #3341 sequencing, TDD gaps) |
| Codex | PENDING — dispatch deferred | codex runtime CPU-constrained on this host; see epic #3333 routing note |
| Gemini | PENDING — dispatch deferred | codex runtime CPU-constrained on this host; see epic #3333 routing note |

**Overall result:** PASS after revisions

Revisions made based on review:
- F1 (HIGH): Deliverable + pseudocode rewritten — retention is resume-only; loud warning comment mandated beside `enabled: false`; registry.yaml annotation fixed to "frozen 2026-04-17, dde rows lost on --force rebuild"; added `test_force_rebuild_retention_semantics`.
- F2 (MEDIUM): dropped skip-until-last-path resume logic; resume = re-walk from start over idempotent upserts (pseudocode + `test_resume_after_interrupt` updated).
- F3 (MEDIUM): added encoding policy (surrogateescape walk + backslashreplace storage), per-row retry fallback on batch failure, and `test_surrogate_filename_batch_fallback`.
- F4 (MINOR): runbook now creates `/mnt/dde/.dde-knowledge` before the nohup log redirect.
- F5 (MINOR): pseudocode states `file_path = canonical_path = /mnt/dde/...` explicitly (upsert conflict column + #3335 adapter column).
- F6 (MINOR): registry-entry handshake with #3335 pinned (who adds `dde_knowledge`, in which order) + ready-to-paste entry embedded.
- F7 (MINOR): acceptance criterion now uses `pytest tests/data/document-index/` instead of `-k document_index`.
- F8 (MINOR): sequencing note added — build independent of PR #3341, consumption from ace-linux-1 is not.
- F9 (INFO): added `test_classification_map_applied`; documented `anonymized_title` stays NULL in v1.

---

## Risks and Open Questions

- **Risk — decision (b) needs owner sign-off:** issue title says "unfreeze"; this plan recommends deprecate-in-favor-of-DB instead. Non-destructive (frozen rows retained), but confirm at plan approval. If owner insists on (a), the alias fix should wait for #3337's canonical rewrite to avoid double churn.
- **Risk — ntfs3 quirks:** NTFS under Linux `ntfs3` can surface invalid-encoding filenames, reparse points, and permission oddities. Builder must treat every per-entry error as log-and-continue (test covers this); use `os.fsdecode` defensively.
- **Risk — 2.0 TB hash pass mis-scoped as blocking:** hashing everything is a multi-day job; plan explicitly stages it as a separate incremental invocation. Do not let review re-couple it to acceptance.
- **Risk — stale checkout on ace-linux-2:** `/mnt/workspace-hub` is at `2f5eb972f` (Jun 30) — `git pull` is a mandatory runbook step; also confirm the implementation PR is merged (or fetch the branch) before the production run.
- **Risk — `uv` flakiness on some machines** (ops memory: uv broken for several repos): mitigated — builder is stdlib+pyyaml; bare `python3` fallback documented.
- **Risk — concurrent writes to the drive during scan:** files created/deleted mid-walk make find-vs-DB reconciliation drift slightly; hence ±0.1% tolerance rather than exact equality, and reconcile runs immediately after build.
- **Risk — FTS external-content pitfall:** with `content=assets`, updating `assets` without syncing FTS desyncs the index. Bulk `rebuild` after each metadata/hash pass (hash pass touches no FTS-indexed columns, so it's actually safe — note in code comment).
- **Open — classification depth:** ace rows carry `discipline/project_code/engineering_domain` populated by the lost builder's heuristics. This plan populates them from a top-dir YAML map (coarse) and leaves refinement to #3336/#3337. Acceptable for the #3335 CLI's ranked search? (Assumed yes — FTS over title/breadcrumb is the primary signal.)
- **Open — NFS mount timing (PR #3341):** canonical `/mnt/dde` does not exist on ace-linux-1 yet. All plan paths are canonical because the builder runs on ace-linux-2 where `/mnt/dde` is the real local mount — no dependency on #3341 merging first, but reviewers should not "fix" paths to sshfs aliases. **Sequencing note:** the BUILD has no dependency on PR #3341, but CONSUMPTION from ace-linux-1 does — until the NFS mount lands, `/mnt/dde` is absent on ace-linux-1, the #3335 CLI will report the dde index as an unreachable coverage gap, and dde queries fall back to the (frozen) JSONL layer.

---

## Complexity: T2

**T2** — one new module + YAML config + 12-test TDD suite, two config-file edits, a supervised long-running production run on a remote host with reconciliation evidence. No new architecture (schema is copied from an existing DB; patterns from phase-a-index.py), so not T3; production-run choreography and resume/idempotency semantics push it above T1.
