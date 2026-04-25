# Plan for #2125: feat(llm-wiki): auto-refresh ingestion on new Orcina releases

> **Status:** draft (v3 — addresses r2 Claude MAJOR + r2 Gemini APPROVE)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2125
> **Base commit:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (HEAD at v2 plan-drafting time; cite line numbers relative to this SHA)
> **Review artifacts (r1):** `scripts/review/results/20260424T103739Z-inline-content-plan-claude.md` (REJECT — empty-input harness bug, unusable), `scripts/review/results/20260424T103739Z-inline-content-plan-codex.md` (MAJOR — 2 P1 + 1 P2 + 1 P3, actionable), `scripts/review/results/20260424T103739Z-inline-content-plan-gemini.md` (NO_OUTPUT — silent failure)
> **Review artifacts (r2):** `scripts/review/results/20260424T205053Z-plan-2125-v2.md-plan-claude.md` (MAJOR — 4 P2 + 4 P3, actionable), `scripts/review/results/20260424T205325Z-plan-2125-v2.md-plan-gemini.md` (APPROVE with 2 P3)
> **Review artifacts (r3, pending):** `scripts/review/results/2026-04-24-plan-2125-v3-{claude,gemini}.md`

---

## Review History (closure summary)

Short table mapping every review finding to its resolution. Future reviewers can see closure at a glance.

### r1 (resolved in v2 — preserved here for traceability)
| Finding | Class | Resolution in v2 |
|---|---|---|
| **Output-root contract violation** — v1 hardcoded `data/llm-wiki/changelog/...` and added a `.gitkeep` under `data/llm-wiki/`, but `ingest-orcina.py main()` resolves output root via `resolve_wiki_dir()` with env-var / config / repo-symlink / fallback rules. | **P1** | Resolved in v2. All changelog paths derive from `resolve_wiki_dir() / "changelog"`. No `data/llm-wiki/...` string literals in Files-to-Change, pseudocode, or Acceptance Criteria. The `.gitkeep` row was removed. New TDD row `test_refresh_writes_changelog_under_resolved_root` monkeypatches `resolve_wiki_dir`. |
| **Refresh surface incomplete** — v1 only specced product topics; supplementary pages and papers/PDFs were unspecified. | **P1** | Resolved in v2. v3 preserves: explicit refresh behavior for all three ingest surfaces (product topics, supplementary, papers/PDFs), each with at least one TDD row. |
| **Cron scope creep** — v1 made cron MANDATORY; #2125 says cron is OPTIONAL. | **P2** | Resolved in v2 via Option (a) — cron split out to a follow-on sibling of #2036. v3 preserves the split. |
| **TDD edge cases missing** — deleted-topic pruning, atomic rewrite, non-package helper imports. | **P3** | Resolved in v2. v3 preserves all three TDD additions. |

### r2 (resolved in this v3)
| Finding | Class | Resolution in v3 |
|---|---|---|
| **`head_pdf` / caller contract mismatch** — caller in `ingest_papers` guards with `if (cached and head ...)` implying `head_pdf` returns `None` on failure, but the v2 pseudocode had no try/except. A single 405/403/timeout would crash the whole refresh. | **P2** | Resolved. v3 wraps `head_pdf` in `try: ... except (HTTPError, URLError, socket.timeout, OSError): return None` so the caller's `and head` guard is satisfied by construction. New TDD rows `test_head_pdf_network_failure_returns_none` and `test_refresh_falls_back_to_download_when_head_fails` exercise the fallback. The Risks-section claim about "falls back to download-and-hash-compare" is now expressed in the control flow, not just prose. See Pseudocode §`head_pdf` and TDD §Papers/PDF surface. |
| **pytest discovery mechanism for sibling-import tests is not documented** — v2 cited the existing `test_resolve_wiki_path.py` as precedent but did not state HOW discovery works. An implementer might reinvent and drift. | **P2** | Resolved. v3 documents the established mechanism inline: each new test module begins with the same `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` shim used at `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py:23-27` (verified at base SHA). No new `conftest.py` is introduced (none exists today; the per-test shim is the sanctioned pattern). The Pseudocode and TDD sections now show the shim header explicitly, and Acceptance Criteria binds invocation to `cd scripts/data/llm-wiki && uv run pytest tests/...` (CWD-relative — never traverses the hyphenated ancestor as a dotted package). |
| **`merge_of_per_product_changes` left as a placeholder** — three products feed the product-topics surface, but v2's changelog payload was a merged blob without product attribution. | **P2** | Resolved. v3 locks the schema explicitly inline. The `all_changes["product_topics"]` payload is now `{"orcaflex": {"added": [...], "removed": [...], "modified": [...]}, "orcawave": {...}, "orcfxapi": {...}}` — keyed by product, with each value carrying per-URL added/removed/modified lists. Changelog markdown emits one section per product (`### Product: OrcaFlex — Added (N) / Removed (M) / Modified (K)`). New TDD row `test_refresh_changelog_attributes_topic_changes_per_product` asserts per-product attribution. See Pseudocode §`assemble_product_topic_changes` and Schema-lock section below. |
| **PDF deletion path is fragile** — `entry['file'].split('/')[-1]` assumes a specific schema; legacy `papers_meta.json` missing `entry` key would raise `KeyError`. No test covers this branch. | **P2** | Resolved. v3 defines the `papers_meta.json` entry schema explicitly and inline (every required key listed), uses `Path(...).name` instead of `.split("/")[-1]` per Gemini's P3, and adds a defensive lookup helper `safe_get_papers_entry(stored_meta, url)` that returns `None` (not raises) for legacy / hand-edited / partial entries. New TDD row `test_refresh_prunes_legacy_papers_meta_without_entry_key` exercises a stored-meta blob missing the `entry` key. See Pseudocode §`papers_meta.json schema` and Schema-lock section below. |
| **Atomicity** — v2 said "`atomic_write_json-equivalent for markdown`"; introduce a named helper. | **P3** | Resolved. v3 defines `atomic_write_text(path: Path, text: str)` in `orcina_refresh.py` and refactors `atomic_write_json` to wrap it. The TDD row `test_refresh_changelog_write_is_atomic` binds to `atomic_write_text` for unambiguous mocking. |
| **Decision churn — same-day collision filename** | **P3** | Resolved. v3 locks the rule: when a target changelog filename already exists at write time, the new file is written as `<date>-<version>-T<HHMMSS>.md` unconditionally. No "decide at implementation". Acceptance Criteria adds a check. |
| **Timeout asymmetry** — `fetch_conditional` 30s vs `head_pdf` 15s. | **P3** | Resolved. v3 lifts both to module-top constants `FETCH_TIMEOUT_S = 30` and `HEAD_TIMEOUT_S = 15` in `orcina_refresh.py`, with a one-line justification: HEAD is a metadata round-trip and should fail fast; full GET may stream a multi-MB body and warrants a longer ceiling. |
| **Concurrency unmentioned** | **P3** | Resolved. Risks section now carries a single-writer-invariant line: two concurrent `--refresh` invocations on the same output root are unsupported; the follow-on cron wrapper will provide a `flock`. Interactive users must serialize manually. |
| **Gemini P3 — `atomic_write_text` helper** | **P3** | Resolved (same as Claude P3 above). |
| **Gemini P3 — `Path(...).name` over `.split("/")[-1]`** | **P3** | Resolved (folded into the P2 papers-deletion fix above). |

---

## Attested Evidence

Independently-verifiable claims this v3 plan relies on. Each was checked against HEAD `12b4be83` on 2026-04-24.

| Claim | Verification method | Result |
|---|---|---|
| Issue #2125 OPEN | `gh issue view 2125` | OPEN — "feat(llm-wiki): auto-refresh ingestion on new Orcina releases" |
| Issue #2036 OPEN (cron-tracking sibling) | `gh issue view 2036` | OPEN (carry-forward from v1 resource-intel) |
| `resolve_wiki_dir()` signature — zero-arg, returns `Path` | `grep -n "resolve_wiki_dir" scripts/data/llm-wiki/resolve_wiki_path.py` → `29:def resolve_wiki_dir() -> Path:` | **CONFIRMED** — signature is `def resolve_wiki_dir() -> Path`. No arguments. Returns first-existing of env var `$LLM_WIKI_DATA_DIR` → the llm-wiki YAML config under `config/` → `REPO_ROOT/data/llm-wiki` → `REPO_ROOT/knowledge/wikis` (fallback). |
| `ingest-orcina.py main()` uses `resolve_wiki_dir()` for output root | `grep -n "resolve_wiki_dir\|output_root" scripts/data/llm-wiki/ingest-orcina.py` → `557:    from resolve_wiki_path import resolve_wiki_dir`, `574:    output_root = Path(args.output_dir) if args.output_dir else resolve_wiki_dir()` | **CONFIRMED** |
| Three ingest surfaces exist | `grep -n "^def ingest" scripts/data/llm-wiki/ingest-orcina.py` → `309:def ingest_product`, `415:def ingest_supplementary`, `458:def ingest_papers` | **CONFIRMED** |
| `SUPPLEMENTARY_URLS` contains the releases page | `grep -n "releases" scripts/data/llm-wiki/ingest-orcina.py` → `53:    ("releases", "https://www.orcina.com/releases/"),` | CONFIRMED |
| `ingest_papers` uses `pdftotext` on downloaded PDFs | `grep -n "pdftotext\|papers_dir" scripts/data/llm-wiki/ingest-orcina.py` → `464:    papers_dir = output_root / "papers"`, `518:                ["pdftotext", "-layout", pdf_path, "-"],` | CONFIRMED |
| `llm_wiki_common.py` does NOT exist yet | `ls scripts/data/llm-wiki/llm_wiki_common.py` → "No such file or directory" | **CONFIRMED — no shared-common module exists.** v3 does NOT depend on a shared-common module. |
| Existing ingester imports follow the sanctioned hyphen-path pattern | `grep -n "^from \|^import " scripts/data/llm-wiki/ingest-orcina.py` → bare `from resolve_wiki_path import resolve_wiki_dir` at line 557, no dotted-path references through the hyphen | CONFIRMED |
| **Pytest sibling-import discovery mechanism (P2 #2 closure)** — established pattern is per-test `sys.path.insert(0, parent_dir)` shim | `sed -n '20,30p' scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` → lines 23-27 contain: `_SCRIPT_DIR = Path(__file__).resolve().parent.parent`, `if str(_SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(_SCRIPT_DIR))`, `import resolve_wiki_path as mod  # noqa: E402` | **CONFIRMED** — this is the load-bearing mechanism. No `conftest.py` exists under `scripts/data/llm-wiki/tests/`; `__init__.py` is present (empty). v3's new tests will replicate this header verbatim with the appropriate module name. |
| `data/llm-wiki/changelog/` does not exist | `ls data/llm-wiki/changelog/ 2>&1` → "No such file or directory" | Confirmed; treated as a runtime-created artifact. |
| Final-gate grep for `llm-wiki\.` (hyphen-dot dotted-path smell) returns zero hits | `grep -n 'llm-wiki\.' /tmp/plan-drafts/plan-2125-v3.md` | Run as final gate before write; expected: 0 matches. |

Claims the plan does NOT attest (require live verification during implementation, not plan-approval):
- Whether Orcina's upstream returns `Last-Modified` and `ETag` headers consistently across all ~717 topic pages, supplementary pages, and PDFs (plan assumes at least one of: header, or body SHA-256 of fetched bytes, is usable for any given URL).
- Exact HTML structure of `https://www.orcina.com/releases/` for version extraction (plan uses regex tolerant of `\d+\.\w+(-beta)?` forms; fixture test uses a captured snapshot).
- Behavior of PDF `HEAD` requests on Orcina's static host (plan assumes `Content-Length` and `Last-Modified` may or may not be returned; refresh falls back to download-and-hash-compare via the `head_pdf → None` path).

---

## Resource Intelligence Summary

### Existing repo code (anchored to base SHA `12b4be83`)
- Found: `scripts/data/llm-wiki/ingest-orcina.py` (636 lines) — full crawler; `main()` resolves output root via `resolve_wiki_dir()` (line 574); three ingest functions (`ingest_product` line 309, `ingest_supplementary` line 415, `ingest_papers` line 458) all take `output_root: Path`. `SUPPLEMENTARY_URLS` (line 48) contains `("releases", "https://www.orcina.com/releases/")`.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — zero-arg `resolve_wiki_dir() -> Path` function.
- Found: `scripts/knowledge/wiki-ingest-cron.sh` — engineering-wiki cron reference; v3 does NOT port this (cron split to a follow-on).
- Found: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` (185 lines) — load-bearing precedent for the sys.path-shim test header pattern (lines 23-27). v3's new tests will use the same idiom.
- Found: `scripts/data/llm-wiki/tests/__init__.py` — empty, present.
- Gap: no `conftest.py` under `scripts/data/llm-wiki/tests/`; v3 does NOT add one (per-test shim is the sanctioned pattern).
- Gap: no `--refresh` flag, no `If-Modified-Since`/`ETag` handling on any of the three surfaces, no per-entry content hash, no changelog emission, no upstream version parser, no per-surface meta side-file.

### Standards
Not applicable — ingestion tooling, not engineering calculation.

### LLM Wiki pages consulted
- `data/llm-wiki/orcaflex/index.json` — structure is product-scoped; version string lives only in README/prose, not machine-readable metadata. This plan adds `upstream_version` as a top-level key in each product `index.json`.
- No relevant wiki semantic pages — this plan touches the ingestion pipeline, not the rendered wiki.

### Documents consulted
- Parent issue #2088 (Orcina ingestion baseline) — referenced in the script docstring at `ingest-orcina.py:7`.
- Sibling #2126 (markdown-conversion QA) — landed in parallel Lane H2; shares the `html_to_markdown` surface. No overlap in files touched.
- Sibling #2124 (extend Orcina ingestion to resources/examples/training) — currently at v3 plan-review. v3 of #2125 does NOT depend on it.
- Sibling #2036 (cron-tracking) — the intended home for the nightly-wrapper follow-on.
- Upstream: `https://www.orcina.com/releases/` — only authoritative release-surface Orcina publishes; no public RSS/JSON feed.

### Gaps identified
- No machine-readable upstream version detector exists anywhere in the repo.
- No per-URL HTTP-cache layer.
- `index.json` schema has no `upstream_version` or `per_topic_hash` fields.
- No per-surface meta side-files (`supplementary_meta.json`, `papers_meta.json`).
- No Orcina-specific cron wrapper — intentionally left to a follow-on.

<!-- Source count: issue body + ingest-orcina.py + resolve_wiki_path.py + wiki-ingest-cron.sh + resolve_wiki_path tests + #2088/#2036 references + Orcina releases URL + feedback_llm_wiki_hyphen_module_path_pattern memory note + r1 Codex review artifact + r2 Claude review artifact + r2 Gemini review artifact = 11 distinct sources. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md |
| New module — version detector | scripts/data/llm-wiki/orcina_version.py |
| New module — refresh helpers | scripts/data/llm-wiki/orcina_refresh.py |
| New tests — version detector | scripts/data/llm-wiki/tests/test_orcina_version.py |
| New tests — refresh mode (all three surfaces) | scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py |
| Modify — ingest script | scripts/data/llm-wiki/ingest-orcina.py |
| Plan review — r3 Claude | scripts/review/results/2026-04-24-plan-2125-v3-claude.md |
| Plan review — r3 Gemini | scripts/review/results/2026-04-24-plan-2125-v3-gemini.md |

Pytest discovery: each new test module begins with the per-test sys.path-shim header (replicated verbatim from the precedent at `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` lines 23-27). No `conftest.py` row — none exists today and one is intentionally NOT added by this plan.

Note: no `data/llm-wiki/changelog/.gitkeep` row, no `scripts/cron/orcina-refresh-cron.sh` row. Changelog directory is a runtime artifact under the resolved output root (which may or may not be `data/llm-wiki/` depending on the machine); cron wrapper is split to a follow-on issue.

---

## Deliverable

An `ingest-orcina.py --refresh` mode that:
1. Parses the upstream Orcina releases page to detect the current `{orcaflex, orcawave, orcfxapi}` version triple.
2. For each of the three ingest surfaces (product topics, supplementary pages, papers/PDFs), skips work whose upstream signal (HTTP `Last-Modified`/`ETag` or body SHA-256; PDF `Last-Modified`+`Content-Length`+bytes-SHA-256) is unchanged since the last refresh.
3. Writes a machine-readable `upstream_version` to each product `index.json`.
4. Prunes entries absent from the live source (deleted topics, deleted supplementary pages, deleted PDFs) from their respective indexes.
5. Emits a per-product-attributed diff report to `resolve_wiki_dir() / "changelog" / "YYYY-MM-DD-<version>.md"` (or `...-T<HHMMSS>.md` on same-day+same-version collision) whenever any of the three surfaces has added/removed/modified content OR the detected version triple differs from the stored one.
6. All writes (indexes, meta side-files, changelog) use the tempfile + `os.replace` atomic-rewrite pattern via the named helpers `atomic_write_json` and `atomic_write_text`, so partial failures leave the previous state intact.

Explicitly OUT of scope for this plan: cron wrapper, commit automation, wiki-alert issue filing on version bump (all deferred to the follow-on sibling of #2036).

---

## Schema lock (P2 closure — pinned inline)

### `papers_meta.json` entry schema (per-URL value)

```
{
  "last_modified":   str | null,        // HTTP Last-Modified header from HEAD
  "content_length":  str | null,        // HTTP Content-Length header from HEAD
  "bytes_sha256":    str,               // hex digest of downloaded PDF body (always present after first successful download)
  "entry": {                            // per-PDF metadata mirror — required for prune + reconstruction
    "file":        str,                 // relative path under output_root, e.g. "papers/orcaflex_paper.md"
    "title":       str,
    "source_url":  str,                 // matches outer key
    "downloaded":  str                  // ISO8601 timestamp of last successful download
  }
}
```

Required keys: `last_modified`, `content_length`, `bytes_sha256`, `entry`. Within `entry`: `file`, `title`, `source_url`, `downloaded`. Defensive lookup `safe_get_papers_entry(stored_meta, url)` returns `None` if `url` absent OR if the value lacks an `entry` key OR if `entry.file` is missing — never raises. Pruning for legacy/partial entries logs a warning and skips disk-delete (the index is still pruned).

### `supplementary_meta.json` entry schema (per-URL value)

```
{
  "last_modified":  str | null,
  "etag":           str | null,
  "content_hash":   str | null          // sha256 hex of body, for header-fallback comparison
}
```

### Product-topics changelog payload (`all_changes["product_topics"]`)

Per-product attribution is the contract — never a flat merged blob.

```
{
  "orcaflex":  {"added": [url, ...], "removed": [url, ...], "modified": [url, ...]},
  "orcawave":  {"added": [url, ...], "removed": [url, ...], "modified": [url, ...]},
  "orcfxapi":  {"added": [url, ...], "removed": [url, ...], "modified": [url, ...]}
}
```

Changelog markdown rendering:

```
## Product topics

### Product: OrcaFlex — Added (N) / Removed (M) / Modified (K)
- Added:
  - <url>
- Removed:
  - <url>
- Modified:
  - <url>

### Product: OrcaWave — ...
### Product: OrcFxAPI — ...
```

Empty per-product sections (zero added/removed/modified) are omitted to keep the changelog concise.

---

## Pseudocode

```
# ── orcina_refresh.py (new) — module-top constants ───────────────────────────
FETCH_TIMEOUT_S = 30   # full-body GET — may stream multi-MB content
HEAD_TIMEOUT_S  = 15   # metadata-only round-trip — should fail fast

# ── orcina_version.py (new) ─────────────────────────────────────────────────
def detect_current_version(releases_html):
    # Input: already-fetched HTML of https://www.orcina.com/releases/
    # (fetched by the existing supplementary path; no second fetch).
    parse HTML, locate release rows (MadCap Flare release-table pattern)
    extract version strings matching r"OrcaFlex \d+\.\w+(-beta)?" (and OrcaWave/OrcFxAPI)
    return {
        "orcaflex": "11.6c" | None,
        "orcawave": "X.Y" | None,
        "orcfxapi": "X.Y" | None,
        "detected_at": utcnow_iso(),
        "source_url": "https://www.orcina.com/releases/",
    }

def load_stored_version(index_path: Path) -> str | None:
    if index.json has "upstream_version", return it; else return None

def diff_versions(stored_triple, current_triple):
    return {p: (stored.get(p), current[p])
            for p in current if stored.get(p) != current[p]}


# ── orcina_refresh.py (new — refresh helpers; sibling-import-safe) ──────────
# Imported from ingest-orcina.py via: from orcina_refresh import (...)
# Directory is scripts/data/llm-wiki/ — bare sibling import works because
# the hyphenated dir is never traversed as a dotted package.

import socket
from urllib.error import HTTPError, URLError

def fetch_conditional(url, cached_meta):
    # cached_meta: {"last_modified": str|None, "etag": str|None, "content_hash": str|None}
    build urllib.request.Request with If-Modified-Since / If-None-Match when present
    try:
        resp = urlopen(req, timeout=FETCH_TIMEOUT_S)
    except HTTPError as e:
        if e.code == 304: return ("unchanged", cached_meta, None)
        raise
    body = resp.read()
    new_meta = {
        "last_modified": resp.headers.get("Last-Modified"),
        "etag": resp.headers.get("ETag"),
        "content_hash": sha256_hex(body),
    }
    if cached_meta and new_meta["content_hash"] == cached_meta.get("content_hash"):
        return ("unchanged", new_meta, body)  # hash fallback — headers didn't cache but body identical
    return ("changed", new_meta, body)

def head_pdf(url):
    # HEAD for PDFs; returns {"last_modified", "content_length"} or None on ANY failure.
    # Defensive try/except per r2 P2 #1: a single 405/403/timeout on one PDF must NOT
    # crash the whole refresh — caller's `if cached and head ...` guard depends on this
    # contract. On None, caller falls back to download-and-hash-compare (slower but safe).
    req = urllib.request.Request(url, method="HEAD", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=HEAD_TIMEOUT_S) as resp:
            return {
                "last_modified": resp.headers.get("Last-Modified"),
                "content_length": resp.headers.get("Content-Length"),
            }
    except (HTTPError, URLError, socket.timeout, OSError) as e:
        log.warning("head_pdf failed for %s: %s — falling back to download", url, e)
        return None

def atomic_write_text(path: Path, text: str):
    # Single source of truth for atomic file writes. Wraps the tempfile + os.replace
    # pattern so all callers get the same semantics. Used by changelog markdown writes
    # AND by atomic_write_json (below).
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)  # atomic on POSIX; tempfile persists on failure, target unchanged

def atomic_write_json(path: Path, data: dict):
    # Wraps atomic_write_text — single atomic-write impl, JSON serialization on top.
    atomic_write_text(path, json.dumps(data, indent=2))

def safe_get_papers_entry(stored_meta: dict, url: str) -> dict | None:
    # Defensive lookup for legacy/partial papers_meta.json. Returns the
    # entry dict iff well-formed; None otherwise (caller logs + skips disk-delete).
    val = stored_meta.get(url)
    if not val: return None
    entry = val.get("entry")
    if not entry: return None
    if not entry.get("file"): return None
    return entry

def changelog_path(wiki_root: Path, version_label: str) -> Path:
    # Same-day+same-version collision rule (locked in v3): if the date+version
    # filename already exists, append a -T<HHMMSS> suffix unconditionally.
    # No "decide at implementation".
    base = wiki_root / "changelog" / f"{date.today().isoformat()}-{version_label}.md"
    if not base.exists():
        return base
    suffix = datetime.now(timezone.utc).strftime("T%H%M%S")
    return base.with_name(f"{base.stem}-{suffix}.md")

def write_changelog(wiki_root: Path, version_label: str, diffs: dict):
    # diffs schema (locked):
    #   "product_topics": {"orcaflex": {added, removed, modified}, "orcawave": {...}, "orcfxapi": {...}},
    #   "supplementary":  {added, removed, modified},
    #   "papers":         {added, removed, modified},
    #   "version_bump":   {orcaflex: (old, new), ...}
    changelog_dir = wiki_root / "changelog"         # ← resolve_wiki_dir() derived, NOT hardcoded
    changelog_dir.mkdir(parents=True, exist_ok=True)
    path = changelog_path(wiki_root, version_label)
    body = render_markdown_with_per_product_sections(diffs)
    atomic_write_text(path, body)


# ── ingest-orcina.py (modify) ────────────────────────────────────────────────
# Add:
#   parser.add_argument("--refresh", action="store_true")
#   parser.add_argument("--force-full", action="store_true")
#
# In main(): wiki_root = resolve_wiki_dir(); pass to all three ingesters +
#            to the changelog writer.

def ingest_product(product_key, info, output_root, refresh=False, force_full=False):
    index_path = output_root / product_key / "index.json"
    if refresh and not force_full and index_path.exists():
        stored = json.loads(index_path.read_text())
        stored_topics_by_url = {t["source_url"]: t for t in stored.get("topics", [])}
        live_entries = parse_toc_xml(info["toc_url"])
        live_urls = {e["link_url"] for e in live_entries}

        new_topics = []
        changes = {"added": [], "removed": [], "modified": []}
        for entry in live_entries:
            cached = stored_topics_by_url.get(entry["link_url"])
            cached_meta = cached.get("http_meta") if cached else None
            status, new_meta, body = fetch_conditional(entry["link_url"], cached_meta)
            if status == "unchanged" and cached:
                new_topics.append({**cached, "http_meta": new_meta})
            else:
                title, md = html_to_markdown(body.decode("utf-8", errors="replace"), entry["link_url"])
                write topic file via atomic_write_text
                new_topics.append({"file": ..., "title": title, "source_url": entry["link_url"],
                                   "http_meta": new_meta, ...})
                if cached: changes["modified"].append(entry["link_url"])
                else: changes["added"].append(entry["link_url"])

        # Deleted-topic pruning (resolves r1 P3)
        for url, cached in stored_topics_by_url.items():
            if url not in live_urls:
                changes["removed"].append(url)
                # v3 leaves the .md file on disk for audit trail; only the index is pruned.

        product_index = {
            "product": info["label"],
            "base_url": info["base_url"],
            "generated": utcnow_iso(),
            "topic_count": len(new_topics),
            "upstream_version": CURRENT_VERSION_TRIPLE[product_key],
            "topics": new_topics,
        }
        atomic_write_json(index_path, product_index)
        return {"entries": new_topics, "changes": changes, "product_key": product_key}
    else:
        # Existing full-crawl behavior (unchanged).
        ...

def ingest_supplementary(output_root, refresh=False, force_full=False):
    # Side-file: output_root / "supplementary" / "supplementary_meta.json"
    # Schema: see Schema-lock section above.
    meta_path = output_root / "supplementary" / "supplementary_meta.json"
    stored_meta = json.loads(meta_path.read_text()) if (refresh and not force_full and meta_path.exists()) else {}
    changes = {"added": [], "removed": [], "modified": []}

    entries = []
    new_meta = {}
    for name, url in SUPPLEMENTARY_URLS:
        cached = stored_meta.get(url)
        status, nm, body = fetch_conditional(url, cached)
        new_meta[url] = nm
        if status == "unchanged" and cached:
            entries.append(existing entry)
        else:
            title, md = html_to_markdown(body.decode(...), url)
            atomic_write_text(supp_dir / f"{name}.md", md)
            entries.append({...})
            if cached: changes["modified"].append(url)
            else: changes["added"].append(url)

    # Deleted-page pruning
    for url in stored_meta:
        if url not in new_meta:
            changes["removed"].append(url)

    atomic_write_json(meta_path, new_meta)
    return {"entries": entries, "changes": changes}

def ingest_papers(output_root, refresh=False, force_full=False):
    # Side-file: output_root / "papers" / "papers_meta.json"
    # Schema: see Schema-lock section above.
    meta_path = output_root / "papers" / "papers_meta.json"
    stored_meta = json.loads(meta_path.read_text()) if (refresh and not force_full and meta_path.exists()) else {}

    listing_html = fetch_page(PAPERS_PAGE)
    live_pdf_urls = extract pdf links from listing_html  # existing logic
    changes = {"added": [], "removed": [], "modified": []}

    entries = []
    new_meta = {}
    for pdf_info in live_pdf_urls:
        url = pdf_info["url"]
        cached = stored_meta.get(url)
        head = head_pdf(url)   # ← returns None on ANY HTTP/timeout failure (P2 #1 fix)
        if (cached and head
            and cached.get("last_modified") == head.get("last_modified")
            and cached.get("content_length") == head.get("content_length")):
            new_meta[url] = cached
            entries.append(cached["entry"])
            continue

        # head is None OR headers diverged — fall back to download-and-hash-compare.
        pdf_bytes = download(url)
        bytes_hash = sha256_hex(pdf_bytes)
        if cached and cached.get("bytes_sha256") == bytes_hash:
            # Bytes identical (HEAD failed or headers churned) — update headers only, skip reconvert.
            new_meta[url] = {**cached,
                             "last_modified": (head or {}).get("last_modified"),
                             "content_length": (head or {}).get("content_length")}
            entries.append(cached["entry"])
            continue

        # Actually changed (or new).
        markdown_text = pdftotext(pdf_bytes)
        atomic_write_text(papers_dir / f"{safe_filename}.md", markdown_text)
        entry = {"file": f"papers/{safe_filename}.md", "title": ...,
                 "source_url": url, "downloaded": utcnow_iso()}
        new_meta[url] = {"last_modified": (head or {}).get("last_modified"),
                         "content_length": (head or {}).get("content_length"),
                         "bytes_sha256": bytes_hash, "entry": entry}
        entries.append(entry)
        if cached: changes["modified"].append(url)
        else: changes["added"].append(url)

    # Deleted-PDF pruning — defensive against legacy/partial papers_meta.json (P2 #4 fix).
    for url in stored_meta:
        if url not in new_meta:
            changes["removed"].append(url)
            entry = safe_get_papers_entry(stored_meta, url)
            if entry is None:
                log.warning("legacy/partial papers_meta entry for %s — skipping disk-delete", url)
                continue
            try:
                (papers_dir / Path(entry["file"]).name).unlink()
            except FileNotFoundError:
                pass

    atomic_write_json(meta_path, new_meta)
    return {"entries": entries, "changes": changes}

# ── In main(), after all three ingesters return: per-product attribution ────
def assemble_product_topic_changes(product_results: list[dict]) -> dict:
    # Locks per-product attribution per the Schema-lock section.
    out = {}
    for r in product_results:   # one result per product
        out[r["product_key"]] = r["changes"]   # {"added": [...], "removed": [...], "modified": [...]}
    return out  # {"orcaflex": {...}, "orcawave": {...}, "orcfxapi": {...}}

all_changes = {
    "product_topics": assemble_product_topic_changes(product_results),
    "supplementary":  supp_changes,
    "papers":         paper_changes,
    "version_bump":   diff_versions(stored_triple, current_triple),
}
if any per-product or surface section has non-empty added/removed/modified
   OR version_bump is non-empty:
    write_changelog(wiki_root=output_root, version_label=current_triple_label(), diffs=all_changes)
```

Key discipline points:
- Every path that receives a write is derived from `output_root` (= `resolve_wiki_dir()`), including `changelog/`, `supplementary/supplementary_meta.json`, `papers/papers_meta.json`. No hardcoded `data/` literal anywhere.
- All Python-module references use underscore-only names (`orcina_version`, `orcina_refresh`); sibling imports from inside `scripts/data/llm-wiki/` use bare module names — no dotted-path traversal of the hyphenated ancestor.
- All index / meta / changelog writes use `atomic_write_json` or `atomic_write_text` (both backed by the same tempfile + `os.replace` pattern).
- All test modules carry the per-test sys.path-shim header (replicated from `tests/test_resolve_wiki_path.py:23-27`).

---

## Test discovery and invocation (P2 #2 closure)

The new test modules live at `scripts/data/llm-wiki/tests/test_orcina_version.py` and `.../test_ingest_orcina_refresh.py`. Each begins with this header (verbatim from the established precedent):

```python
import sys
from pathlib import Path

# scripts/data/llm-wiki/ lives at parent.parent — hyphenated ancestor blocks
# dotted-package traversal, so we insert the directory and import bare module
# names. Established pattern: scripts/data/llm-wiki/tests/test_resolve_wiki_path.py:23-27.
_SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import orcina_version    # noqa: E402
import orcina_refresh    # noqa: E402
```

Invocation: tests run via `cd scripts/data/llm-wiki && uv run pytest tests/test_orcina_version.py tests/test_ingest_orcina_refresh.py -v`. The `cd` keeps pytest's rootdir at `scripts/data/llm-wiki/` and avoids any path that traverses the hyphenated segment as a dotted package. Equivalent: `uv run pytest scripts/data/llm-wiki/tests/test_*.py` from repo root — pytest's collection is filesystem-path-driven, not dotted-import-driven, so this also works (collection traverses paths; the per-test sys.path shim handles the imports).

No `conftest.py` is added by this plan. The per-test shim is the load-bearing mechanism.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/orcina_version.py` | upstream-version parser (stateless HTML → dict); isolated for unit testability |
| Create | `scripts/data/llm-wiki/orcina_refresh.py` | refresh helpers (`fetch_conditional`, `head_pdf` with try/except, `atomic_write_text`, `atomic_write_json`, `safe_get_papers_entry`, `changelog_path`, `write_changelog`, SHA-256 wrapper); module-top constants `FETCH_TIMEOUT_S`, `HEAD_TIMEOUT_S` |
| Create | `scripts/data/llm-wiki/tests/test_orcina_version.py` | TDD — parse fixtures of the releases page; carries sys.path-shim header |
| Create | `scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py` | TDD — exercises `--refresh` across all three surfaces with mocked HTTP 304 / 200 / HEAD-failure responses, monkeypatched `resolve_wiki_dir` pointing at a tmp path, and per-product attribution assertions; carries sys.path-shim header |
| Modify | `scripts/data/llm-wiki/ingest-orcina.py` | add `--refresh` and `--force-full` flags; thread them through all three ingesters; add per-surface conditional-refresh, meta side-files, deleted-entry pruning, `upstream_version` in each product `index.json`, atomic writes, post-ingest per-product-attributed changelog assembly/emission |
| Update | `docs/plans/README.md` | index this plan |

Non-goals explicitly removed from Files to Change vs v1:
- `scripts/cron/orcina-refresh-cron.sh` — split to follow-on sibling of #2036.
- `data/llm-wiki/changelog/.gitkeep` — changelog directory lives under `resolve_wiki_dir()` and is a generated artifact; no git-tracked placeholder needed.
- `scripts/data/llm-wiki/tests/conftest.py` — none exists today and v3 does NOT add one. Per-test sys.path-shim header is the sanctioned mechanism.

---

## TDD Test List

### `test_orcina_version.py`

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_detect_current_version_from_fixture | Parses canned Orcina releases HTML | fixture `tests/fixtures/orcina_releases_11_6c.html` | `{"orcaflex": "11.6c", ...}` |
| test_detect_handles_multiple_products | All 3 products extracted when present | fixture with OrcaFlex+OrcaWave+OrcFxAPI rows | all 3 keys non-None |
| test_detect_returns_none_when_missing | Product absent from HTML yields None | fixture missing OrcaWave row | `current["orcawave"] is None` |
| test_detect_tolerates_unexpected_version_format | Regex tolerates `11.6c`, `12.0`, `13.0a-beta` | 3 synthetic rows | all parse, none raise |
| test_load_stored_version_missing_key | Old index.json without upstream_version | `{"product": "OrcaFlex"}` | returns None, does not raise |
| test_load_stored_version_present | New index.json with upstream_version | `{"upstream_version": "11.6c"}` | returns `"11.6c"` |
| test_diff_versions_identical | Same version both sides | stored==current | empty dict |
| test_diff_versions_bump | Version bump detected | stored="11.6b", current="11.6c" | `{"orcaflex": ("11.6b", "11.6c")}` |

### `test_ingest_orcina_refresh.py`

Output-root hygiene (resolves r1 P1 #1):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_writes_changelog_under_resolved_root | Changelog lands under `resolve_wiki_dir()`, not hardcoded `data/llm-wiki/` | monkeypatch `resolve_wiki_dir` to return `tmp_path`; force a version bump | changelog file exists at `tmp_path / "changelog" / "<date>-<ver>.md"` |
| test_refresh_meta_files_land_under_resolved_root | Per-surface meta side-files land under resolved root | monkeypatched resolver → tmp_path; refresh run | `tmp_path/supplementary/supplementary_meta.json` and `tmp_path/papers/papers_meta.json` exist |

Product-topics surface (resolves r1 P1 #2, topics):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_skips_unchanged_topic_on_304 | 304 response → topic .md not rewritten | mocked `urlopen` returns 304 for topic A | `write` not called for A; `index.json.topics[A].http_meta` preserved |
| test_refresh_skips_unchanged_topic_on_hash_match | headers missing but body-SHA identical → no rewrite | mocked 200 with same body, no `Last-Modified`/`ETag` | `write` not called for A; new `content_hash` recorded |
| test_refresh_rewrites_changed_topic | 200 + new body → topic re-converted | mocked 200 + different body-hash | A.md updated; `index.json` http_meta updated |
| test_refresh_prunes_deleted_topics_from_index | TOC entry removed upstream → index pruned, changelog lists removal (**r1 P3**) | stored index has {A, B, C}; live TOC returns {A, C} | `index.json.topics` contains only {A, C}; changelog `removed` lists B |
| test_refresh_without_stored_index_does_full_crawl | First-run `--refresh` falls back to full | no existing `index.json` | all topics fetched normally; meta recorded |
| test_force_full_overrides_refresh | `--force-full` ignores cache | `--refresh --force-full` with stored index | every topic re-fetched (no conditional headers set on outgoing requests) |
| test_version_persisted_in_each_product_index | `upstream_version` written to every product `index.json` | refresh run | `json.load(orcaflex/index.json)["upstream_version"] == "11.6c"` (and orcawave, orcfxapi) |
| **test_refresh_changelog_attributes_topic_changes_per_product** (**r2 P2 #3**) | Product-topic changelog payload is per-product, not flat-merged | mock orcaflex adds URL_X, orcawave removes URL_Y, orcfxapi modifies URL_Z | rendered changelog contains three sections (`### Product: OrcaFlex`, `### Product: OrcaWave`, `### Product: OrcFxAPI`) and `all_changes["product_topics"]` JSON shape matches the locked schema |

Supplementary surface (resolves r1 P1 #2, supplementary):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_skips_unchanged_supplementary_page | 304 on supplementary URL → no .md rewrite | mocked 304 for `releases` URL | `releases.md` mtime unchanged; `supplementary_meta.json` keeps cached entry |
| test_refresh_rewrites_changed_supplementary_page | 200 + new body → .md rewritten, meta updated | mocked 200 with different hash for `resources` URL | `resources.md` rewritten atomically; `supplementary_meta.json` reflects new `content_hash` |
| test_refresh_records_supplementary_changes_in_changelog | Added/modified supplementary pages listed in changelog | one new URL added to `SUPPLEMENTARY_URLS`, one changed | changelog `supplementary.added` and `supplementary.modified` populated |

Papers/PDF surface (resolves r1 P1 #2, papers; r2 P2 #1, P2 #4):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_skips_unchanged_pdf_via_head | PDF `Last-Modified` + `Content-Length` match cache → no download | mocked HEAD returns cached values | no GET issued; `pdftotext` not invoked; `papers_meta.json` keeps entry |
| test_refresh_re_downloads_pdf_on_head_change_but_skips_reconvert_on_hash_match | HEAD headers changed but bytes-SHA identical → no reconvert | mocked HEAD returns new `Last-Modified`; GET returns bytes with same SHA-256 | GET issued; `pdftotext` NOT invoked; `.md` unchanged; meta headers updated |
| test_refresh_reconverts_pdf_on_bytes_change | bytes-SHA differs → full reconvert | mocked HEAD+GET return new bytes with different SHA | `pdftotext` invoked; `.md` rewritten via `atomic_write_text`; `papers_meta.json` reflects new bytes-SHA |
| test_refresh_prunes_deleted_pdf_from_papers_index | PDF gone from listing → removed from index and disk | stored meta has URL X with full `entry`; listing no longer contains X | `papers_meta.json` lacks X; X's .md file deleted via `Path(entry["file"]).name`; changelog `papers.removed` lists X |
| **test_head_pdf_network_failure_returns_none** (**r2 P2 #1**) | `head_pdf` returns `None` on HTTPError/URLError/timeout/OSError, never raises | mocked `urlopen` raises `URLError("connection refused")` | `head_pdf(url)` returns `None`; warning logged; no exception propagates |
| **test_refresh_falls_back_to_download_when_head_fails** (**r2 P2 #1**) | When `head_pdf` returns `None`, refresh falls back to download-and-hash-compare instead of crashing | `head_pdf` mocked to return `None`; GET returns bytes matching cached `bytes_sha256` | refresh continues; no exception; cached entry preserved (or headers-only meta update); `.md` not rewritten |
| **test_refresh_prunes_legacy_papers_meta_without_entry_key** (**r2 P2 #4**) | Defensive lookup tolerates legacy/partial `papers_meta.json` (e.g. stored entry missing `entry` key from older runs) | stored meta = `{url: {"last_modified": "...", "content_length": "...", "bytes_sha256": "..."}}` (no `entry` key); listing no longer contains url | `papers_meta.json` lacks url after refresh; `safe_get_papers_entry` returns `None` for the row; warning logged; no `KeyError` raised; disk-delete skipped (no .md to remove) |

Atomic-write hygiene (resolves r1 P3 + r2 P3):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_index_write_is_atomic_on_partial_failure | Exception mid-write leaves prior `index.json` intact | monkeypatch `json.dumps` to raise after tempfile created but before `os.replace` | `index.json` still contains pre-refresh content; `.tmp` may persist but does not shadow target |
| **test_refresh_changelog_write_is_atomic** (**r2 P3 — bound to `atomic_write_text`**) | `atomic_write_text` semantics on changelog markdown | monkeypatch `os.replace` to raise inside `atomic_write_text` | pre-existing changelog (if any) intact; partial `.tmp` does not replace |

Filename collision (resolves r2 P3 — same-day+same-version):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| **test_changelog_path_appends_timestamp_on_collision** | `changelog_path` returns `-T<HHMMSS>.md` suffix when a file with the date+version name already exists | pre-create `tmp_path/changelog/2026-04-24-orcaflex-11.6c.md`; call `changelog_path(tmp_path, "orcaflex-11.6c")` | returned path matches regex `2026-04-24-orcaflex-11.6c-T\d{6}\.md` |

All tests use `unittest.mock.patch` on `urllib.request.urlopen` (no real network), monkeypatch `orcina_refresh.resolve_wiki_dir` to point at `tmp_path`, and carry the per-test sys.path-shim header. Fixture HTML files live under `scripts/data/llm-wiki/tests/fixtures/`.

---

## Acceptance Criteria

- [ ] `cd scripts/data/llm-wiki && uv run pytest tests/test_orcina_version.py -v` → all 8 tests pass.
- [ ] `cd scripts/data/llm-wiki && uv run pytest tests/test_ingest_orcina_refresh.py -v` → all TDD rows above pass (output-root hygiene, 3 surfaces incl. `head_pdf` failure path + legacy-meta pruning + per-product attribution, atomic-write, filename-collision).
- [ ] `cd scripts/data/llm-wiki && uv run pytest tests/` → existing `test_resolve_wiki_path.py` still passes (no regression).
- [ ] `python3 scripts/data/llm-wiki/ingest-orcina.py --refresh` against an existing index.json re-fetches zero product topics when the live upstream is byte-identical (observable: script prints `0 changed, 717 cached` or similar; wallclock < 60s for topics alone).
- [ ] `--refresh` writes `upstream_version` into every `<product>/index.json`.
- [ ] `--refresh` creates `supplementary_meta.json` under `resolve_wiki_dir() / "supplementary"` with one entry per URL in `SUPPLEMENTARY_URLS`.
- [ ] `--refresh` creates `papers_meta.json` under `resolve_wiki_dir() / "papers"` with one entry per live PDF, each carrying the locked schema (`last_modified`, `content_length`, `bytes_sha256`, `entry.{file,title,source_url,downloaded}`).
- [ ] When `stored.upstream_version != live.upstream_version` OR any of the three surfaces report non-empty added/removed/modified, a markdown changelog appears at `resolve_wiki_dir() / "changelog" / "<date>-<new-version>.md"` with per-product attribution sections for product topics.
- [ ] When versions are equal AND all surfaces are clean, no changelog file is created (verified in a live run).
- [ ] Running `--refresh` twice back-to-back on stable upstream produces zero `.md` rewrites and zero changelog entries on the second run (cache-effectiveness invariant).
- [ ] Same-day + same-version collision: when a changelog file already exists for today's date+version, the new file lands at `<date>-<version>-T<HHMMSS>.md` (verified by `test_changelog_path_appends_timestamp_on_collision`).
- [ ] Single PDF HEAD failure does NOT abort refresh — observable via `test_head_pdf_network_failure_returns_none` and `test_refresh_falls_back_to_download_when_head_fails`.
- [ ] Final plan-text gate: a hyphen-then-escaped-dot regex anchored on the project directory name (the standard hyphen-path smell pattern from `feedback_llm_wiki_hyphen_module_path_pattern`) returns zero hits when run against `docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md`. Hyphenated filesystem paths followed by `/` are fine; any hyphen-then-literal-dot in a Python dotted-import position is a defect.
- [ ] Review artifacts posted to `scripts/review/results/` for r3 Claude and Gemini.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | REJECT (unusable) | Input was empty file-path only (`cross-review.sh` inline-content bug); findings not actionable. |
| Codex (r1) | MAJOR | 2 P1 + 1 P2 + 1 P3 — all closed in v2. |
| Gemini (r1) | NO_OUTPUT | Silent failure during r1 run; not retried. |
| Claude (r2) | MAJOR | 4 P2 + 4 P3 — all closed in this v3 (head_pdf try/except, pytest discovery doc, per-product attribution schema, papers_meta defensive lookup; plus atomic_write_text helper, locked collision filename, timeout constants, single-writer invariant). |
| Gemini (r2) | APPROVE | 2 P3 — both closed (atomic_write_text helper folded with Claude P3; `Path(...).name` folded into the papers-deletion P2 fix). |
| Claude (r3) | (pending) | |
| Gemini (r3) | (pending) | |

**Overall result:** (pending r3)

---

## Risks and Open Questions

- **Risk:** Orcina releases page HTML structure may change without notice — the version parser must degrade gracefully (return `None` per product, not raise) so refresh doesn't go red on an upstream cosmetic change. Covered by `test_detect_returns_none_when_missing`.
- **Risk:** Upstream may not send `Last-Modified` or `ETag` headers consistently; `fetch_conditional` falls back to SHA-256 of the response body. Covered by `test_refresh_skips_unchanged_topic_on_hash_match`.
- **Risk:** PDF hosts sometimes drop `Content-Length` or fail HEAD entirely; `head_pdf` returns `None` (P2 #1 fix), and refresh falls back to download-and-hash-compare. Covered by `test_head_pdf_network_failure_returns_none` and `test_refresh_falls_back_to_download_when_head_fails`.
- **Risk:** Partial-crawl failure (network blip mid-run) could leave `index.json` inconsistent. Mitigation: tempfile + `os.replace` via `atomic_write_json` / `atomic_write_text`. Covered by `test_refresh_index_write_is_atomic_on_partial_failure` and `test_refresh_changelog_write_is_atomic`.
- **Risk:** `--refresh` against a very stale cache (months old, layout changes) may emit a changelog with hundreds of entries. Acceptable for the first post-upgrade run; not a blocker.
- **Risk:** If `resolve_wiki_dir()` returns a path outside the repo, the changelog is NOT git-tracked. By design — matches where topic/supplementary/paper markdown also lands. The follow-on cron issue will decide commit policy.
- **Risk — single-writer invariant (r2 P3 closure):** two concurrent `--refresh` invocations on the same output root are unsupported — they would race on `index.json` and the meta side-files. The follow-on cron wrapper will provide a `flock`. Interactive users must serialize manually.
- **Risk — legacy `papers_meta.json` schema drift (r2 P2 #4 closure):** older runs or hand-edited meta files may lack the `entry` key. `safe_get_papers_entry` returns `None` defensively; pruning logs a warning and still removes the row from the index but skips disk-delete. Covered by `test_refresh_prunes_legacy_papers_meta_without_entry_key`.
- **Risk — dependency interaction with #2124:** if #2124 lands `orcina_common.py` first, the refresh helpers in `orcina_refresh.py` may relocate into the shared module. Not a blocker; resolve at implementation time as a follow-up commit (one-line coordination note per Claude r2 question 6).
- **Open — audit-trail asymmetry (per Gemini r2 question 1 and Claude r2 question 2):** topics keep deleted `.md` on disk; PDFs delete the `.md`. Rationale: PDF outputs are large and frequently regenerated whole-file; topic outputs are small and may carry historical search context. The author may align both behaviors during implementation; v3 documents the asymmetry but does not require it.
- **Open — rate limiting (per Claude r2 question 5):** v3 does NOT introduce a politeness delay between fetches. If Orcina rate-limits the refresh tool, the follow-on cron wrapper is the right place to add a delay (single-writer + scheduled cadence is the natural enforcement point). Out-of-scope for this plan.
- **Open — version-detection total failure (per Claude r2 question 4):** if the regex returns `None` for all three products, `--refresh` will (a) log a warning, (b) keep the stored `upstream_version` values unchanged, (c) NOT emit a changelog from the version-bump trigger alone. Surface-level adds/removes/modifications still trigger a changelog independently. Exit code remains 0; the cron wrapper (follow-on) will be the place to add a non-zero exit on persistent version-detection failure if needed.

---

## Non-goals

- Cron wrapper for nightly refresh. Follow-on sibling of #2036.
- Auto-filing a GitHub "wiki-alert" issue on version bump. Follow-on with cron.
- Auto-commit of refreshed state. Follow-on with cron.
- Politeness delay / rate limiting in `--refresh` itself. Follow-on with cron.
- Any changes to `search-wiki.py` or the rendered wiki — `upstream_version` is a new forward-compatible key; existing readers ignore it.
- Renaming `ingest-orcina.py` to `ingest_orcina.py`. Not required — the existing file uses CLI invocation, hyphen-safe; its imports use bare sibling names that also work. Renaming would be a separate migration issue.
- Adding a `conftest.py` under `scripts/data/llm-wiki/tests/`. Per-test sys.path-shim header is the sanctioned mechanism (precedent at `test_resolve_wiki_path.py` lines 23-27).
- Retry logic for transient network errors in `fetch_conditional` / `head_pdf` (per Gemini r2 question 2). Out of scope — single-attempt + timeout is sufficient for this pipeline; transient failures will be caught on the next refresh run.

---

## Complexity: T2

**T2** — two new modules (`orcina_version.py`, `orcina_refresh.py`), one modified module (`ingest-orcina.py`), TDD required across three surfaces with explicit per-product attribution and HEAD-failure fallback, no cross-repo changes, no cron layer. Scope is bounded and all interfaces are local; upstream integration is read-only HTTP. Cron split to a follow-on keeps T2 honest; v3's deltas (try/except in `head_pdf`, sys.path-shim doc, per-product schema lock, defensive papers_meta lookup, atomic_write_text helper, locked collision filename, timeout constants, concurrency note) are spec tightening — no scope expansion.
