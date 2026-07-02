# Plan for #3337: Drive-index: canonical-path normalization across indexes (retire dev-secondary/transport aliases)

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3337
> **Client:** N/A
> **Project:** (none — repo-internal data infrastructure)
> **Lane:** lane:codex   <!-- matches the issue's lane:codex label; heavy programming per epic #3333 provider routing. Plan authored on lane:claude; implementation is lane:codex -->
> **Review artifacts:** scripts/review/results/2026-07-02-plan-3337-claude.md | scripts/review/results/2026-07-02-plan-3337-codex.md | scripts/review/results/2026-07-02-plan-3337-gemini.md

---

## Resource Intelligence Summary

<!-- Issue class: Data Pipeline / Harness-Infrastructure union.
     Consulted: issue #3337 body, epic #3333 body, sibling plans #3334/#3335,
     docs/standards/canonical-drive-references.md (merged via PR #3341),
     scripts/setup/canonical-drive-links.sh, scripts/data/document-index/*
     (config.yaml, cross-drive-dedup-audit.py, phase-b-claude-worker.py),
     data/document-index/* artifacts (index.jsonl live probe, registry.yaml,
     mounted-source-registry.yaml, dde catalogs, cross-drive-dedup-report.json,
     shards/), scripts/enforcement/check-no-abs-paths.sh (lint precedent),
     config/workstations/registry.yaml (hostname-alias ground truth). -->

### Existing repo code
- Found: `scripts/data/document-index/config.yaml` — dde source roots at lines 35–43 use the **retired-hostname alias** `/mnt/remote/dev-secondary/dde/...` (9 roots); line 44 `host: dev-secondary`; line 163 `summaries_dir: /mnt/remote/ace-linux-1/ace/data/document-index/summaries` — a **third alias form** (ace transport path) not mentioned in the issue body. All three violate `docs/standards/canonical-drive-references.md` ("transport path is plumbing — never hardcode it").
- Found: `scripts/data/document-index/phase-b-claude-worker.py` lines 289–292 — a **hardcoded, private duplicate alias map** already exists: `PATH_REMAPS = [("/mnt/remote/ace-linux-2/dde/", "/mnt/dde/"), ("/mnt/remote/dev-secondary/dde/", "/mnt/dde/")]`, plus line 36 `_DEFAULT_SUMMARIES = "/mnt/remote/ace-linux-1/ace/..."`. This is exactly the scattered-alias-knowledge problem #3337 consolidates: the map must become an import from the single shared authority, not a second copy.
- Found: `scripts/data/document-index/cross-drive-dedup-audit.py` lines 32, 37 — hardcoded `"dde_path": "/mnt/remote/ace-linux-2/dde/..."` comparison roots (the ace↔dde dedup joiner the issue says "breaks on aliases").
- Found: `scripts/enforcement/check-no-abs-paths.sh` (#2322) — the enforcement precedent to copy: standalone bash, regex scan, **baseline ratchet** (`config/quality/no-abs-paths-baseline.txt`, `<repo-relative-path>:<line>` keys, only NEW offenses fail), line-level sentinel comment (`# abs-path-allowed`), `--update-baseline`, logged env-var bypass. `tests/enforcement/test_check_no_conflict_markers.py` etc. show the pytest-subprocess test pattern for such scripts.
- Found: `config/workstations/registry.yaml` lines 173–174 — `dev-secondary: hostname: ace-linux-2` — proves `dev-secondary` is the retired workstation name for the dde owner host; both stale forms denote the same drive.
- Found: `data/document-index/mounted-source-registry.yaml` lines 48–49 — `mount_root: /mnt/ace-data/...` with `symlink_note: /mnt/ace-data is a symlink to /mnt/ace` — a **fourth alias form** (local symlink) to fold into the alias map.
- Gap: `scripts/data/drive-index-search/pathnorm.py` and `config/drive-index-registry.yml` do **not exist yet** — they are #3335 deliverables (gap proof below). #3337 extends them; hard dependency.
- Gap: no enforcement script rejects non-canonical drive roots anywhere (`ls scripts/enforcement/*canonical*` → nothing).

### Standards
Not applicable as engineering standards — one repo convention governs this issue:

| Standard | Status | Source |
|---|---|---|
| Canonical drive references (`/mnt/<drive>` only; transport never hardcoded) | **done — merged to main 2026-07-02T14:41:59Z via PR #3341** | `docs/standards/canonical-drive-references.md` + `scripts/setup/canonical-drive-links.sh` (DRIVE_OWNER: ace→ace-linux-1, dde→ace-linux-2) |
| Engineering-standards ledger | not applicable | `data/document-index/standards-transfer-ledger.yaml` not relevant to path plumbing |

### LLM Wiki pages consulted
No relevant wiki pages — repo-internal data/harness infrastructure, no domain-engineering knowledge involved.

### Documents consulted
- Issue #3337 body — scope items 1–4 (adopt convention, one-time migration, shared helper, registry lint); acceptance: one canonical path per file from any machine; `config.yaml` carries no host-alias roots.
- Epic #3333 body — gap 4 "Path aliasing breaks canonical references"; suggested order puts #3337 in the hardening phase after #3335 (registry+CLI) and #3334 (dde index).
- `docs/plans/2026-07-02-issue-3335-drive-index-query-cli.md` — **the critical scope boundary**: #3335 normalizes *output rows* via the registry `canonical_aliases` map applied in `scripts/data/drive-index-search/pathnorm.py`; its Risks section states "#3337 normalizes canonical paths *inside index contents*; keep `canonical_aliases` in the registry so #3337 can later shrink it to a no-op without CLI changes". It also fixed the helper name to `pathnorm.py` specifically to match this issue.
- `docs/plans/2026-07-02-issue-3334-dde-drive-index.md` — decision (b): the frozen dde JSONL coverage is **deprecated** in favor of a new drive-local `/mnt/dde/.dde-knowledge/index.db` whose rows are canonical **from birth** (`file_path = canonical_path = /mnt/dde/...`). Direct consequence for #3337: the 623 MB `index.jsonl` dde rows are a deprecated artifact — rewriting them is churn, alias-map coverage at read time suffices. #3334 also edits the same `config.yaml` dde block (`enabled: false` + retention warning) — coordination note in Risks.
- `data/document-index/registry.yaml` — `dde_project: 495487` (the issue's row count); no `/mnt/` path strings inside (`grep -n 'mnt'` → empty), so it needs only the #3334 supersession annotation, not path rewriting.
- Ops memory `reference_digitalmodel_python_env_venv.md` / repo convention: `uv run` is the workspace-hub Python convention; enforcement scripts are bash + pytest-subprocess tested.

### Gaps identified
- No shared alias→canonical authority exists today (only the private `PATH_REMAPS` copy in phase-b-claude-worker.py, which is missing the ace-transport and ace-data forms).
- No canonical-path lint exists; nothing stops a new index config from hardcoding `/mnt/remote/...`.
- The registry `canonical_aliases` map (per #3335's design) will ship with only 2 dde entries; the ace-transport (`/mnt/remote/ace-linux-1/ace`) and `/mnt/ace-data` forms found in this research are not covered anywhere.
- No migration tool exists to rewrite the small live configs/catalogs; 8 tracked YAML/JSON files under `data/document-index/` plus `scripts/data/document-index/config.yaml` carry alias roots (enumeration in Evidence).
- No pre/post migration-equivalence verification harness exists (needs #3335's CLI as the probe).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-02T14:45:17Z–14:49:02Z via `gh issue view` / `gh pr view`):
- `#3337` — OPEN — "Drive-index: canonical-path normalization across indexes (retire dev-secondary/transport aliases)" (labels: cat:data, enhancement, lane:codex, priority:medium, status:needs-plan)
- `#3333` — OPEN — "EPIC: Context-aware drive-file search — skill + unified query layer over /mnt/ace + /mnt/dde file indexes"
- `#3334` — OPEN — "Drive-index: build full dde-drive SQLite FTS index + unfreeze master index dde coverage"
- `#3335` — OPEN — "Drive-index: unified query CLI + index registry over heterogeneous catalogs (SQLite/JSONL/TSV/YAML)"
- PR `#3341` — **MERGED 2026-07-02T14:41:59Z** — "feat(setup): dde-drive NFS mount + canonical drive-reference convention" (the convention this issue consumes is on main; present in this worktree)

**File existence** (`ls` / `git ls-files`, 2026-07-02T14:45:17Z–14:49:46Z):
- EXISTS: `docs/standards/canonical-drive-references.md`, `scripts/setup/canonical-drive-links.sh` (DRIVE_OWNER registry lines 24–27: ace→ace-linux-1, dde→ace-linux-2)
- EXISTS: `scripts/data/document-index/config.yaml`, `scripts/data/document-index/cross-drive-dedup-audit.py`, `scripts/data/document-index/phase-b-claude-worker.py`, `scripts/enforcement/check-no-abs-paths.sh`, `config/quality/no-abs-paths-baseline.txt`, `tests/enforcement/` (pytest suite for enforcement scripts)
- EXISTS (live, untracked): `/mnt/local-analysis/workspace-hub/data/document-index/index.jsonl` — 623,054,407 bytes, mtime 2026-04-17 (frozen); `git ls-files data/document-index/index.jsonl` → empty → **not git-tracked** (its rewrite would not even produce a reviewable diff)
- MISSING (created by #3335 — dependency): `scripts/data/drive-index-search/pathnorm.py`, `config/drive-index-registry.yml` (`ls` → "No such file or directory", 2026-07-02T14:45:58Z)
- MISSING (new — this plan creates): `scripts/enforcement/check-canonical-drive-paths.sh`, `config/quality/canonical-drive-paths-baseline.txt`, `scripts/data/document-index/migrate-canonical-paths.py`, `tests/enforcement/test_check_canonical_drive_paths.py`, `tests/data/document-index/test_canonical_migration.py`

**Line excerpts** (`grep -n`, 2026-07-02T14:45:17Z / 14:51:13Z):
```
$ grep -n "dev-secondary\|/mnt/" scripts/data/document-index/config.yaml | head
35:      - /mnt/remote/dev-secondary/dde/documents
36:      - /mnt/remote/dev-secondary/dde/0000 O&G
...  (9 roots, lines 35–43)
44:    host: dev-secondary
163:  summaries_dir: /mnt/remote/ace-linux-1/ace/data/document-index/summaries

$ sed -n 289,292p scripts/data/document-index/phase-b-claude-worker.py
PATH_REMAPS = [
    ("/mnt/remote/ace-linux-2/dde/", "/mnt/dde/"),
    ("/mnt/remote/dev-secondary/dde/", "/mnt/dde/"),
]
$ grep -n 'mnt/remote' scripts/data/document-index/cross-drive-dedup-audit.py | head -3
6:(/mnt/remote/ace-linux-2/dde/) to identify duplicates and unique files.
32:        "dde_path": "/mnt/remote/ace-linux-2/dde/documents/",
37:        "dde_path": "/mnt/remote/ace-linux-2/dde/0000 O&G/0000 Codes & Standards/",
```

**Ground-truth alias probes** (2026-07-02T14:45:58Z–14:48:42Z, against the live 623 MB artifact — all `grep` bounded with `-m`/`-c`, never full reads):
```
$ grep -m3 -o '"/mnt/remote/[^"]*"' /mnt/local-analysis/workspace-hub/data/document-index/index.jsonl
"/mnt/remote/ace-linux-2/dde/documents/simulation/OrcaFlex/611 Mecor S Lay Installation/..."
$ head -1 index.jsonl | cut -c1-200
{"path": "/mnt/ace/O&G-Standards/Unknown/Codes_&_Standards_Database.xls", "host": "ace-linux-1", ...}
$ grep -c '/mnt/remote/ace-linux-2/dde' index.jsonl        →  260496   (0.163 s warm)
$ grep -c '/mnt/remote/dev-secondary'   index.jsonl        →  0
$ grep -F -c 'dev-secondary'            index.jsonl        →  1        (a FILENAME row:
  specs/modules/hardware-inventory/manifests/dev-secondary.yml — NOT a path alias)
```
Findings: (1) `/mnt/ace` rows already canonical (first row shown); (2) **all** dde rows inside `index.jsonl` use the `ace-linux-2` transport alias (260,496 alias-bearing lines of 649,564 total) — the `dev-secondary` form exists only in the *builder config*, never in index contents; (3) the JSONL line count with the alias (260,496) is well below registry's `dde_project: 495487` — the registry counts include shard/carryover layers (hypothesis carried over from #3335 plan).

**Alias census across tracked artifacts** (`git grep -l 'remote/ace-linux-2/dde' -- '*.yaml' '*.yml' '*.py' '*.sh' '*.json'` + per-file greps, 2026-07-02T14:49:46Z):
- Index configs/catalogs IN SCOPE (rewrite): `scripts/data/document-index/config.yaml`; `data/document-index/{mounted-source-registry.yaml, dde-literature-catalog.yaml, dde-oil-gas-codes-scan.yaml, dde-standards-inventory.yaml, coverage-audit.yaml, llm-wiki-external-source-priority-queue.yaml, summary-extraction-plan.yaml, cross-drive-dedup-report.json}` (dedup report samples: `"/mnt/ace/docs/"` vs `"/mnt/remote/ace-linux-2/dde/documents/"` — the alias-broken join pair named by the issue)
- Index scripts IN SCOPE (repoint): `scripts/data/document-index/cross-drive-dedup-audit.py`, `scripts/data/document-index/phase-b-claude-worker.py`
- Plumbing OUT OF SCOPE (transport paths are their job): `scripts/setup/nfs-dde-drive.sh`, `docs/ops/mount-map.yaml`, `config/workstations/registry.yaml`, `scripts/readiness/check-network-mounts.sh`
- Historical/inert (leave; baseline if lint-visible): `.planning/archive/**`, `.claude/state/**`, `analysis/**`, `data/open-issues-2026-04-08.json`, `tests/data/document-index/test_phase_e2_rules.py` (fixture strings)

**Gap proofs** (2026-07-02T14:45:58Z–14:51:48Z):
- `ls scripts/data/drive-index-search config/drive-index-registry.yml` → "No such file or directory" (both) → #3335 deliverables not landed; dependency is real.
- `grep -n 'mnt' data/document-index/registry.yaml` → empty → registry.yaml carries counts, not paths — no rewrite needed there.
- `grep -F -l 'mnt/remote' data/document-index/shards/*.json` → no files (exit 1), sample row `"path": "/mnt/local-analysis/workspace-hub/specs/..."` → **all 20 tracked shards are already alias-free**; shards need no migration.
- `ls tests/enforcement/` → exists with `test_check_no_conflict_markers.py`, `test_check_model_id_sourcing.py`, fixtures/ → pytest-subprocess pattern for bash lint scripts confirmed.

**Reproduction proofs**: the issue alleges a data-consistency defect, not a runtime failure. Reproduced as data: the same drive is referenced three ways across live artifacts — `config.yaml:35` (`/mnt/remote/dev-secondary/dde/documents`), `index.jsonl` contents (`/mnt/remote/ace-linux-2/dde/documents/...`, 260,496 lines), and the canonical form `/mnt/dde` (convention doc + #3334's new DB). A join between `cross-drive-dedup-report.json`'s dde keys and any canonical-path index misses on every row without normalization.
- Reproduced at: 2026-07-02T14:45:58Z
- Failure mode observed matches issue claim: YES — three alias forms live simultaneously (plus a 4th, `/mnt/ace-data`, found during research).

<!-- Source count: issue #3337 + epic #3333 + plan 3335 + plan 3334 + canonical-drive-references.md
     + canonical-drive-links.sh + config.yaml + phase-b-claude-worker.py + cross-drive-dedup-audit.py
     + index.jsonl live probes + mounted-source-registry.yaml + dde catalogs + dedup report + shards
     + registry.yaml + check-no-abs-paths.sh + workstations registry + tests/enforcement
     = 18 distinct sources ≥ 3 required. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-02-issue-3337-canonical-path-normalization.md |
| Shared alias authority (extended, not duplicated) | scripts/data/drive-index-search/pathnorm.py (created by #3335; this issue extends) + `canonical_aliases` in config/drive-index-registry.yml (the data) |
| One-time migration tool | scripts/data/document-index/migrate-canonical-paths.py |
| Enforcement lint | scripts/enforcement/check-canonical-drive-paths.sh + config/quality/canonical-drive-paths-baseline.txt |
| Tests — pathnorm alias table | tests/data/drive_index_search/test_pathnorm_canonical.py |
| Tests — migration | tests/data/document-index/test_canonical_migration.py |
| Tests — lint | tests/enforcement/test_check_canonical_drive_paths.py |
| Migrated configs | scripts/data/document-index/config.yaml + 8 data/document-index/ artifacts (list in Files to Change) |
| Plan review — Claude | scripts/review/results/2026-07-02-plan-3337-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-02-plan-3337-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-02-plan-3337-gemini.md |
| Wiki updates | none (no domain knowledge added) |
| Docs updates | docs/standards/canonical-drive-references.md (add "index artifacts + lint" section); docs/plans/README.md index row (at implementation/PR time — NOT edited in this authoring pass) |

---

## Deliverable

Every live drive-index config and small catalog in the repo stores canonical `/mnt/<drive>/...` paths only (one-time migration, idempotent tool), all historical alias forms (`/mnt/remote/dev-secondary/dde`, `/mnt/remote/ace-linux-2/dde`, `/mnt/remote/ace-linux-1/ace`, `/mnt/ace-data`) resolve through the single shared `pathnorm.py` + registry `canonical_aliases` authority so frozen artifacts stay queryable without regeneration, and a new `check-canonical-drive-paths.sh` lint (sentinel + baseline-ratchet, per the check-no-abs-paths.sh precedent) rejects non-canonical drive roots in new index configs — with full TDD coverage.

### Design decisions (weighed; recommendations)

**D1 — `index.jsonl` dde rows (260,496 alias-bearing lines in a 623 MB, frozen, untracked, #3334-deprecated artifact): LEAVE FROZEN + alias-map coverage.**

| Option | Cost | Benefit | Verdict |
|---|---|---|---|
| a. Rewrite in place | streaming rewrite of 623 MB; artifact is untracked (no reviewable diff), frozen since 2026-04-17, and formally deprecated by #3334 decision (b); a `--force` rebuild would drop the rows anyway | contents match convention | churn on a dead artifact — rejected |
| b. Leave frozen + alias map (`canonical_aliases` applied by #3335's `pathnorm.py` on every output row) | one YAML map entry (already shipped by #3335 for this exact alias) | historical artifact stays queryable, zero risk, zero I/O | **recommended** |
| c. Regenerate over NFS | re-walk ~half a million dde docs from ace-linux-1 — the NFS-latency trap #3334 explicitly rejected | fresh data | superseded by #3334's drive-local DB — rejected |

BUT the **small, live, tracked** configs and catalogs DO get rewritten (they are inputs to future builds and joins, they are reviewable diffs, and the issue's acceptance names `config.yaml` explicitly): `config.yaml`, `mounted-source-registry.yaml`, the dde-*.yaml catalogs, `coverage-audit.yaml`, `llm-wiki-external-source-priority-queue.yaml`, `summary-extraction-plan.yaml`, `cross-drive-dedup-report.json` (123 KB — small enough to rewrite, and it is the alias-broken join artifact the issue names).

**D2 — shared helper: EXTEND #3335's `pathnorm.py` as the single authority; registry `canonical_aliases` stays the data.** A second copy (e.g., keeping phase-b-claude-worker's private `PATH_REMAPS`) recreates the defect this issue retires — the research found that exact drift already: `PATH_REMAPS` is missing the ace-transport and ace-data forms. `pathnorm.py` gains a `load_alias_map()` that reads `config/drive-index-registry.yml`, and document-index scripts import it (import shim below, since `drive-index-search/` is a hyphenated non-package dir). The alias map SHRINKS toward no-op as artifacts churn out, exactly as #3335's risk note planned — but it does not reach zero while the frozen `index.jsonl` remains registered (end-state documented in the standard).

**D3 — enforcement: NEW standalone `scripts/enforcement/check-canonical-drive-paths.sh` following check-no-abs-paths.sh's sentinel + baseline-ratchet pattern — not an extension of check-no-abs-paths.sh.** Rationale: check-no-abs-paths targets `.sh`/`.py` *scripts* and treats ANY `/mnt/` as a violation — the opposite polarity of this rule, where canonical `/mnt/<drive>` is REQUIRED and only `/mnt/remote/` + legacy alias roots are violations, and the target set is *configs* (YAML/JSON), which check-no-abs-paths never scans (a scope gap its own cross-provider memory snapshot records). Scan set: `scripts/data/**/*.y*ml`, `config/drive-index-registry.yml`, `data/document-index/*.yaml` + `*.json` (tracked only) — NOT the huge/untracked artifacts, NOT the plumbing allowlist (nfs-*.sh, canonical-drive-links.sh, mount-map.yaml, workstations registry, readiness checks). The registry's own `canonical_aliases` keys legitimately contain alias strings — exempted structurally (see Pseudocode).

**D4 — migration verification: pre/post equivalence via the #3335 CLI + dedup-join check.** Before migration, record the CLI's canonical output for N known dde files (the CLI already normalizes output rows via the alias map); after migration, the same queries must return byte-identical canonical paths — proving the migration changed representation, not meaning. At least ONE of the queries must target a dde row in a NON-alias form, if any exist beyond the 260,496 counted alias-bearing lines (review r1 F6) — proving alias-map coverage is complete rather than assumed; the 260,496-vs-495,487 count gap stays a labeled hypothesis either way. Plus: every dde key in the rewritten `cross-drive-dedup-report.json` now shares the `/mnt/dde/` prefix with #3334's DB rows, so cross-drive joins are prefix-compatible without remapping.

---

## Pseudocode

### 1. `pathnorm.py` extension (modifies #3335's module — the only shared-helper change)

```
# scripts/data/drive-index-search/pathnorm.py  (exists after #3335; ADD:)

function load_alias_map(registry_path=config/drive-index-registry.yml) -> dict:
    yaml.safe_load(registry_path)["canonical_aliases"]      # data lives in YAML, not code
    validate: every value startswith "/mnt/" and has no "/remote/" segment
    return dict sorted longest-key-first                    # longest-prefix-wins, per #3335

function canonicalize(path, alias_map) -> str:              # #3335's normalize, exposed standalone
    for alias, canonical in alias_map:                      # longest-prefix-first
        if path == alias or path.startswith(alias + "/"):
            return canonical + path[len(alias):]
    return path                                             # canonical passthrough

function is_canonical(path, alias_map) -> bool:
    return canonicalize(path, alias_map) == path and not path.startswith("/mnt/remote/")
```

Registry data change (`config/drive-index-registry.yml` — extends #3335's map with the two forms research found):

```yaml
canonical_aliases:
  /mnt/remote/ace-linux-2/dde: /mnt/dde        # transport (present in index.jsonl contents, 260,496 lines)
  /mnt/remote/dev-secondary/dde: /mnt/dde      # retired hostname (present in config.yaml)
  /mnt/remote/ace-linux-1/ace: /mnt/ace        # ace transport (config.yaml summaries_dir, phase-b default)  [NEW]
  /mnt/ace-data: /mnt/ace                      # local symlink (mounted-source-registry) — verify ls -la first  [NEW]
```

Import shim for document-index scripts (hyphenated dir is not a package):

```
# scripts/data/document-index/_pathnorm_shim.py (~7 lines)
REPO_ROOT = Path(__file__).resolve().parents[3]
assert (REPO_ROOT / "config").is_dir(), "_pathnorm_shim moved? repo-root resolution broke"   # review r1 F7
sys.path.insert(0, str(REPO_ROOT / "scripts/data/drive-index-search"))
from pathnorm import canonicalize, load_alias_map, is_canonical   # re-export
```

### 2. `migrate-canonical-paths.py` — one-time, idempotent config rewriter

```
# scripts/data/document-index/migrate-canonical-paths.py
main(argv):
    args: [--check] (dry-run: report would-change counts, exit 1 if any)
          [--targets FILE...] (default: the 9 tracked files listed in Files to Change)
    alias_map = load_alias_map()                       # via shim — single authority, no local copy
    for file in targets:
        text = read(file)
        # TEXT-LEVEL prefix substitution, NOT yaml round-trip: preserves comments,
        # key order, quoting, and formatting; alias prefixes are unique literal
        # strings so substitution is unambiguous. Replace longest-alias-first.
        new = text; for alias, canonical in alias_map: new = new.replace(alias + "/", canonical + "/")
        also replace bare-alias occurrences followed by quote/EOL (catalog `source:` keys quote the bare root)
        if file is YAML/JSON: STRUCTURAL SAFETY CHECK —
            parse(text) and parse(new) must both succeed, and
            walk both trees: they must be identical after mapping every string
            through canonicalize()                      # proves rewrite = pure path renaming
        if new != text: atomic write (tmp + rename)
    special-case config.yaml — dde-source SAFETY GATE (review r1 F1):
        the migration REQUIRES #3334's `enabled: false` + retention-warning comment to be
        present on origin/main config.yaml BEFORE running; if ABSENT, the migration itself
        applies `enabled: false` + the retention warning to the dde source block DEFENSIVELY
        — it must NEVER leave canonical /mnt/dde roots live with `enabled: true`, which
        would arm the ~0.5M-file NFS walk from ace-linux-1 that #3334 exists to avoid
    special-case config.yaml: `host: dev-secondary` → `host: ace-linux-2`
        (host field is metadata, not a path — regex-targeted edit + comment)
    print per-file changed/unchanged summary
    idempotency: second run finds zero alias prefixes → zero writes → exit 0
    NEVER touches: data/document-index/index.jsonl (frozen, untracked — D1),
        checkpoints/, shards/ (proven alias-free), plumbing allowlist files
```

### 3. `check-canonical-drive-paths.sh` — lint (mirrors check-no-abs-paths.sh)

```
# scripts/enforcement/check-canonical-drive-paths.sh
Usage: [--baseline=<file>] [--update-baseline] [--no-baseline] [<file-or-dir>...]
DEFAULT_BASELINE=config/quality/canonical-drive-paths-baseline.txt
SENTINEL: line ending "# transport-path-allowed" is skipped   (mirrors # abs-path-allowed)
BYPASS: ALLOW_TRANSPORT_PATHS=1 (logged to stderr)

target set (no positional args):
    git ls-files 'scripts/data/**/*.yml' 'scripts/data/**/*.yaml' \
                 'config/drive-index-registry.yml' \
                 'data/document-index/*.yaml' 'data/document-index/*.json'
    minus PLUMBING_ALLOWLIST (docs/ops/mount-map.yaml is not matched; keep list anyway):
        scripts/setup/*, scripts/readiness/*, config/workstations/registry.yaml
    structural exemption: in config/drive-index-registry.yml, lines inside the
        `canonical_aliases:` block are skipped (awk block-range: from the key to
        the next top-level key) — alias strings are that block's PAYLOAD

violation regex:  (/mnt/remote/|/mnt/ace-data(/|["'[:space:]]|$))
    # transport prefix + known symlink alias; the ace-data alternative matches the BARE
    # form too (review r1 F2) — `mount_root: /mnt/ace-data` with no trailing slash must
    # not evade the lint (catalog `source:` keys quote the bare root)
    # consequence: the preserved `symlink_note` history lines in mounted-source-registry.yaml
    # now match — sentinel-comment (`# transport-path-allowed`) or baseline them (they are
    # YAML; sentinel works there)
    (deliberately NOT a full canonical-whitelist check: unknown /mnt/<x> roots are
     the abs-path lint's business; this lint only retires ALIASES per #3337 scope)
JSON targets (review r1 F3): JSON carries no comments, so the `# transport-path-allowed`
    sentinel is UNUSABLE inside `data/document-index/*.json` — baseline entries are the
    ONLY escape hatch for JSON files (the dedup report is rewritten clean, so in practice
    the baseline stays empty)

baseline ratchet: identical semantics to check-no-abs-paths.sh —
    known entries `<repo-relative-path>:<line>` skipped; NEW offenses fail (exit 1);
    --update-baseline regenerates sorted file and exits 0
post-migration expectation: baseline is EMPTY or near-empty (historical/inert files
    only if any later enter the target set) — the ratchet exists for the pattern's
    sake and future expansion, not to grandfather the files this issue fixes
```

### 4. Migration-equivalence verification (D4 — runbook, executed at implementation)

```
PRE  (before rewriting anything):
    uv run python scripts/data/drive-index-search/search.py "mecor s lay" --json > /tmp/pre.json
    plus 2 more queries hitting known dde rows + 1 hitting /mnt/ace rows
    + 1 query targeting a dde row in a NON-alias path form, if any exist (probe:
      grep -m1 -v '/mnt/remote/' over dde-host rows in index.jsonl) — proves alias-map
      coverage is complete, not just the 260,496 counted lines (review r1 F6); the
      260,496-vs-495,487 registry count gap remains a labeled hypothesis regardless
POST (after migration + registry alias-map extension):
    same queries > /tmp/post.json
    assert: results[].canonical_path sets are IDENTICAL pre/post (jq -S compare)
    assert: zero '/mnt/remote/' occurrences in post.json
DEDUP JOIN:
    python: every dde-side key in cross-drive-dedup-report.json startswith '/mnt/dde/'
            and canonicalize(key) == key   (join-ready against #3334 DB rows)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | scripts/data/drive-index-search/pathnorm.py | add `load_alias_map()`, `canonicalize()`, `is_canonical()` public API (exists after #3335 — dependency gate) |
| Modify | config/drive-index-registry.yml | extend `canonical_aliases` with `/mnt/remote/ace-linux-1/ace → /mnt/ace` and `/mnt/ace-data → /mnt/ace` (exists after #3335) |
| Create | scripts/data/document-index/_pathnorm_shim.py | import bridge into the hyphenated drive-index-search dir (single authority, no copy) |
| Create | scripts/data/document-index/migrate-canonical-paths.py | one-time idempotent migration tool (+ `--check` dry-run mode) |
| Create | scripts/enforcement/check-canonical-drive-paths.sh | registry lint — sentinel + baseline ratchet per check-no-abs-paths.sh precedent |
| Create | config/quality/canonical-drive-paths-baseline.txt | ratchet baseline (expected empty/near-empty post-migration) |
| Modify | scripts/data/document-index/config.yaml | 9 dde roots → `/mnt/dde/...`; `host: dev-secondary` → `ace-linux-2`; `summaries_dir` → `/mnt/ace/...` (GATE, review r1 F1: require #3334's `enabled: false` + retention warning present, else apply them defensively — never leave canonical /mnt/dde roots live with `enabled: true`) |
| Modify | data/document-index/mounted-source-registry.yaml | mount_root aliases → canonical (incl. `/mnt/ace-data` rows); keep `symlink_note` lines as history — sentinel-comment or baseline them, since the F2-widened lint matches the bare `/mnt/ace-data` form |
| Modify | data/document-index/dde-literature-catalog.yaml | source_dirs + per-item paths → `/mnt/dde/...` |
| Modify | data/document-index/dde-oil-gas-codes-scan.yaml | source_path + header comments → canonical |
| Modify | data/document-index/dde-standards-inventory.yaml | source root → canonical |
| Modify | data/document-index/coverage-audit.yaml | summaries canonical_location + dde prerequisites → canonical |
| Modify | data/document-index/llm-wiki-external-source-priority-queue.yaml | mount_dependency → canonical |
| Modify | data/document-index/summary-extraction-plan.yaml | SUMMARIES_DIR narrative path → canonical |
| Modify | data/document-index/cross-drive-dedup-report.json | dde keys → `/mnt/dde/...` (D4 join artifact; 123 KB) |
| Modify | scripts/data/document-index/cross-drive-dedup-audit.py | hardcoded `dde_path` roots → canonical; module docstring |
| Modify | scripts/data/document-index/phase-b-claude-worker.py | delete private `PATH_REMAPS` → import via `_pathnorm_shim`; `_DEFAULT_SUMMARIES` → `/mnt/ace/...` |
| Modify | docs/standards/canonical-drive-references.md | add "Index artifacts & enforcement" section: alias-map end-state (frozen artifacts only), lint pointer |
| Create | tests/data/drive_index_search/test_pathnorm_canonical.py | alias-table TDD (all historical forms + passthrough) |
| Create | tests/data/document-index/test_canonical_migration.py | migration rewrite/idempotency/structure-safety TDD (fixture copies, never live files) |
| Create | tests/enforcement/test_check_canonical_drive_paths.py | lint accept/reject/baseline/sentinel TDD (pytest-subprocess, fixtures in tests/enforcement/fixtures/) |
| Update (deferred) | docs/plans/README.md | add this plan to index — at implementation-PR time, NOT in this authoring pass |

NOT changed: `data/document-index/index.jsonl` (D1 — frozen, untracked, deprecated), `data/document-index/shards/*` (proven alias-free), `data/document-index/registry.yaml` (no paths; #3334 owns its annotation), plumbing (`scripts/setup/*`, `docs/ops/mount-map.yaml`, `config/workstations/registry.yaml`, `scripts/readiness/check-network-mounts.sh`), historical archives (`.planning/`, `.claude/state/`, `analysis/`).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_canonicalize_dev_secondary_alias | historical form 1 | `/mnt/remote/dev-secondary/dde/Literature/x.pdf` | `/mnt/dde/Literature/x.pdf` |
| test_canonicalize_ace_linux2_transport | historical form 2 (index.jsonl contents) | `/mnt/remote/ace-linux-2/dde/documents/y.xlsx` | `/mnt/dde/documents/y.xlsx` |
| test_canonicalize_canonical_passthrough | historical form 3: already canonical | `/mnt/dde/documents/y.xlsx`, `/mnt/ace/docs/a.pdf` | unchanged |
| test_canonicalize_ace_transport_alias | new-found form: ace transport | `/mnt/remote/ace-linux-1/ace/data/document-index/summaries` | `/mnt/ace/data/document-index/summaries` |
| test_canonicalize_ace_data_symlink_alias | new-found form: local symlink | `/mnt/ace-data/digitalmodel/docs/z.md` | `/mnt/ace/digitalmodel/docs/z.md` |
| test_canonicalize_no_partial_segment_match | prefix safety | `/mnt/remote/ace-linux-2/dde-extra/z` | unchanged |
| test_load_alias_map_from_registry | YAML is the data authority | fixture registry with 4 aliases | dict, longest-prefix-first order, values validated canonical |
| test_load_alias_map_rejects_noncanonical_value | map self-consistency | fixture with value `/mnt/remote/x/y` | error naming the bad entry |
| test_is_canonical | lint/verify primitive | canonical vs alias vs `/mnt/remote/unknown/q` | True / False / False |
| test_phase_b_worker_uses_shared_map | no second copy survives (D2) | load `phase-b-claude-worker.py` via `importlib.util.spec_from_file_location` (hyphenated filename — not importable by module name; review r1 F5), with `_pathnorm_shim`'s `sys.path` insert in effect for that load | module has no local `PATH_REMAPS` literal; remap fn delegates to pathnorm |
| test_migration_rewrites_dde_roots | config rewrite | fixture copy of config.yaml (alias roots) | all 9 roots `/mnt/dde/...`; `host: ace-linux-2`; summaries_dir `/mnt/ace/...` |
| test_migration_enforces_dde_disabled | F1 safety gate — never canonical+enabled | fixture config.yaml with alias roots, `enabled: true`, NO retention comment | migrated file has `/mnt/dde` roots AND `enabled: false` AND the retention-warning comment (defensively applied); fixture already carrying #3334's edit is preserved verbatim |
| test_migration_idempotent | second run is a no-op | run tool twice on fixture set | run 2: zero files written; byte-identical to run 1 output |
| test_migration_preserves_structure | text-level rewrite = pure renaming | YAML fixture with comments + quoting | parses pre/post; trees identical after canonicalize() mapping; comments intact |
| test_migration_check_mode | dry-run contract | `--check` on dirty fixture / clean fixture | exit 1 + would-change report / exit 0 |
| test_migration_never_touches_frozen_artifacts | D1 guard | fixture tree containing an `index.jsonl` | file mtime/content untouched; not in targets |
| test_migration_rewrites_dedup_report_keys | D4 join artifact | fixture dedup JSON with alias keys | all dde keys `/mnt/dde/...`; JSON still parses; non-path values untouched |
| test_lint_rejects_transport_path | core reject case | fixture YAML with `/mnt/remote/ace-linux-2/dde/x` | exit 1, names file:line |
| test_lint_accepts_canonical | core accept case | fixture YAML with only `/mnt/dde/`, `/mnt/ace/` | exit 0 |
| test_lint_sentinel_allows_line | escape hatch | violating line ending `# transport-path-allowed` | exit 0 |
| test_lint_baseline_ratchet | only NEW offenses fail | baselined violation + one new one | exit 1 listing only the new offense |
| test_lint_update_baseline | ratchet refresh | `--update-baseline` on fixtures | baseline file written sorted; exit 0 |
| test_lint_exempts_registry_alias_block | structural exemption (D3) | fixture drive-index-registry.yml with `canonical_aliases` containing alias strings | exit 0; same strings OUTSIDE the block still fail |
| test_lint_skips_plumbing_allowlist | plumbing stays legal | fixture named as scripts/setup/nfs-x.sh with transport path | not scanned / exit 0 |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/data/drive_index_search/test_pathnorm_canonical.py tests/data/document-index/test_canonical_migration.py tests/enforcement/test_check_canonical_drive_paths.py -v`
- [ ] No regression: `uv run pytest tests/data/ tests/enforcement/` passes (or matches pre-change failure baseline recorded at branch time); #3335's existing pathnorm/CLI tests still green after the pathnorm extension
- [ ] Issue acceptance 1 — same file, one canonical path from any machine: pre/post CLI equivalence harness (D4) passes — identical `canonical_path` sets, zero `/mnt/remote/` in post-migration output (commands + jq diff pasted into the PR)
- [ ] Issue acceptance 2 — `git grep -c '/mnt/remote/' scripts/data/document-index/config.yaml` → 0 and no `dev-secondary` host-alias remains in it; alias map in `config/drive-index-registry.yml` covers all four forms (dev-secondary, ace-linux-2 transport, ace-linux-1 transport, ace-data)
- [ ] Migration idempotency proven live: running `migrate-canonical-paths.py` a second time on the repo → "0 files changed" and `git status --porcelain` unchanged
- [ ] Lint green on the migrated repo: `scripts/enforcement/check-canonical-drive-paths.sh` exit 0 with an empty (or documented) baseline; injecting a `/mnt/remote/...` line into a scanned config makes it exit 1
- [ ] Cross-drive dedup join check: every dde key in `cross-drive-dedup-report.json` starts with `/mnt/dde/` and `canonicalize(key) == key`
- [ ] `data/document-index/index.jsonl` untouched (mtime still 2026-04-17) — D1 honored
- [ ] Docs: `docs/standards/canonical-drive-references.md` gains the index-artifacts/enforcement section; plan indexed in docs/plans/README.md at PR time
- [ ] Review artifacts posted to scripts/review/results/ (3 providers)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MINOR** | Every load-bearing evidence claim re-verified exact; 1 MEDIUM (unenforced #3334-lands-first assumption → canonical dde roots could go live with `enabled: true`, arming the NFS-walk trap) + 6 lint/coordination/mechanism nits — all addressed in r1 revisions below |
| Codex | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |
| Gemini | PENDING — dispatch deferred (codex runtime CPU-constrained on this host; see epic #3333 routing note) | — |

**Overall result:** PASS after revisions (Claude r1)

Revisions made based on review:
- **F1** — sequencing gate hardened: the migration now REQUIRES #3334's `enabled: false` + retention comment present on origin/main config.yaml before running, and applies them itself defensively if absent — never leaving canonical `/mnt/dde` roots live with `enabled: true` (the ~0.5M-file NFS-walk trap #3334 exists to avoid). Stated in Risks + Pseudocode §2 + Files to Change + new `test_migration_enforces_dde_disabled` (TDD list).
- **F2** — lint violation regex widened to `(/mnt/remote/|/mnt/ace-data(/|["'[:space:]]|$))` so the bare `/mnt/ace-data` form is matched; the preserved `symlink_note` history lines are sentinel-commented or baselined (Pseudocode §3, Files to Change).
- **F3** — stated explicitly that `# transport-path-allowed` sentinels are unusable inside JSON targets; baseline entries are the only escape hatch for JSON files (Pseudocode §3).
- **F4** — mutual-ordering note with #3336 on `config/drive-index-registry.yml` added: sequential merges, second lander rebases — mirroring the config.yaml/#3334 note (Risks).
- **F5** — `test_phase_b_worker_uses_shared_map` now specifies `importlib.util.spec_from_file_location` loading for the hyphenated `phase-b-claude-worker.py`, with the shim's `sys.path` insert in effect for that load (TDD list).
- **F6** — D4 verification gains one query targeting a non-alias dde row form (proving alias-map coverage is complete, not just the 260,496 counted lines); the count gap stays a labeled hypothesis (Design D4, Pseudocode §4).
- **F7** — shim robustness: `assert (REPO_ROOT / "config").is_dir()` added after the `parents[3]` resolution (Pseudocode §1).

---

## Risks and Open Questions

- **Risk — hard dependency on #3335 (OPEN, not implemented):** `pathnorm.py` and `config/drive-index-registry.yml` do not exist yet (gap-proven above). Safe to plan now; implementation MUST gate on `git show origin/main:config/drive-index-registry.yml` succeeding. If #3337 is dispatched first by mistake, the fallback is to create pathnorm.py per #3335's spec — but that inverts ownership; prefer waiting.
- **Risk — same-file collision with #3334, HARDENED to a gate (review r1 F1):** #3334 edits `scripts/data/document-index/config.yaml` (dde source `enabled: false` + loud retention warning); today the dde block has `enabled: true`. If #3337 migrated first WITHOUT the gate, config.yaml would carry live canonical `/mnt/dde` roots with `enabled: true` — the next `phase-a-index.py` run would walk ~0.5M dde files over NFS from ace-linux-1 (the exact trap #3334 rejects) and mutate the "frozen" index.jsonl. Therefore: the migration REQUIRES #3334's `enabled: false` + retention comment present on origin/main config.yaml before running; if absent it applies them itself, defensively (pseudocode §2 + `test_migration_enforces_dde_disabled`). When #3334 has landed, the rewrite preserves its flag and warning comment verbatim (only path strings change). Sequential merges, never parallel branches on this file (squash-merge stacking lesson).
- **Risk — same-file seam with #3336 on `config/drive-index-registry.yml` (review r1 F4):** this issue extends `canonical_aliases`; #3336 adds freshness fields/builder pointers to the same registry file — additive edits in different blocks, both landing after #3335. Sequential merges only; whichever lands second rebases (mirror of the config.yaml/#3334 note above).
- **Risk — `/mnt/ace-data → /mnt/ace` alias is registry-hearsay:** the symlink claim comes from `mounted-source-registry.yaml`'s own `symlink_note`, not a live probe (this worktree box cannot see ace-linux-1's `/mnt/ace-data`). Implementation must verify `ls -la /mnt/ace-data` on ace-linux-1 before adding the alias-map entry; if it is NOT a symlink to /mnt/ace, drop that entry and leave those registry rows baselined.
- **Risk — text-level rewrite corrupting a value that merely *contains* an alias substring:** mitigated by the structural safety check (parse pre/post + tree-equality-modulo-canonicalize) and by fixtures copying the real files. The dedup report's VOB-file keys include spaces/`&` — substitution is prefix-anchored on literal strings, immune to shell-quoting issues since it runs in Python.
- **Risk — alias map can never fully reach no-op:** the frozen `index.jsonl` keeps its transport-alias contents by design (D1), so `canonical_aliases` must survive as long as that artifact is registered. Not a defect — the end-state is "aliases exist ONLY in the map + frozen artifacts, never in live configs" — but reviewers should not "simplify" the map away. When #3334's DB fully supersedes the JSONL layer and its registry entry is retired, the dde alias entries can be dropped (flag to #3340's long-term unified-index decision).
- **Risk — lint scope creep:** the violation regex intentionally covers only known alias forms (`/mnt/remote/`, `/mnt/ace-data/`), not a full "must-be-canonical-whitelist" check; widening it to all `/mnt/<x>` roots would collide with check-no-abs-paths.sh's remit and false-positive on `/mnt/local-analysis` (explicitly canonical-exempt per the standard: not a shared drive).
- **Open — should `coverage-audit.yaml`/`summary-extraction-plan.yaml` (analysis narratives, not configs) be rewritten or baselined?** Plan says rewrite (cheap, keeps the lint baseline empty); if the owner prefers audit artifacts stay historically verbatim, move them to the baseline instead — zero code change either way. Flag at approval.
- **Open — `host:` field convention:** `config.yaml` `host: dev-secondary` → `ace-linux-2` treats hostnames like paths (retire the stale name). Confirm nothing keys on the literal string `dev-secondary` in phase-a-index.py resume logic before renaming (one grep at implementation time).

---

## Complexity: T2

**T2** — one shared-module extension + two new tools (migration, lint) + ~11 config/script edits + three TDD suites (~24 tests) across two existing test trees; cross-issue coordination with #3334/#3335 on shared files. No new architecture (alias map and helper are #3335's design; lint pattern is copied from #2322), no schema migration of live databases, frozen 623 MB artifact deliberately untouched — so not T3; multi-artifact migration + enforcement + equivalence harness push it above T1.
