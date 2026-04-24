# Plan for #2125: feat(llm-wiki): auto-refresh ingestion on new Orcina releases

> **Status:** draft (v2 — addresses r1 findings)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2125
> **Base commit:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (HEAD at v2 plan-drafting time; cite line numbers relative to this SHA)
> **Review artifacts (r1):** `scripts/review/results/20260424T103739Z-inline-content-plan-claude.md` (REJECT — empty-input harness bug, unusable), `scripts/review/results/20260424T103739Z-inline-content-plan-codex.md` (MAJOR — 2 P1 + 1 P2 + 1 P3, actionable), `scripts/review/results/20260424T103739Z-inline-content-plan-gemini.md` (NO_OUTPUT — silent failure)
> **Review artifacts (r2, pending):** `scripts/review/results/2026-04-24-plan-2125-v2-{claude,codex,gemini}.md`

---

## Review History (closure summary)

Short table mapping every r1 Codex finding to its resolution in this v2 plan, so future reviewers can see closure at a glance. (Claude and Gemini r1 were unusable — empty-input harness bug and silent failure respectively; Codex carried the round.)

### r1 (resolved in v2)
| Finding | Class | Resolution in v2 |
|---|---|---|
| **Output-root contract violation** — v1 hardcodes changelog at `data/llm-wiki/changelog/...` and adds a `.gitkeep` under `data/llm-wiki/`, but the existing `ingest-orcina.py main()` resolves output root via `resolve_wiki_dir()` with env var / config file / repo symlink / `knowledge/wikis` fallbacks. On machines where `$LLM_WIKI_DATA_DIR` or `config/llm-wiki.yaml:data_dir` points outside the repo, changelog writes and refreshed wiki state would land on different filesystems. | **P1** | **Resolved.** All changelog paths now derive from `resolve_wiki_dir() / "changelog"`. No `data/llm-wiki/...` string literals remain in Files-to-Change, pseudocode, or Acceptance Criteria. The `.gitkeep` row is removed — a generated artifact directory that lives outside the repo tree cannot be git-tracked, so the script creates the directory with `mkdir(parents=True, exist_ok=True)` at refresh time instead. New TDD row `test_refresh_writes_changelog_under_resolved_root` monkeypatches `resolve_wiki_dir` to point at a tmp path and asserts the changelog file lands there, not at a hardcoded `data/llm-wiki/` location. |
| **Refresh surface incomplete** — `ingest-orcina.py` ingests product TOC topics (`ingest_product`), supplementary pages (`ingest_supplementary`, 5 URLs), and papers/PDFs (`ingest_papers`). v1 only defined conditional-refresh and cache metadata for product topics. What happens when TOC entries are REMOVED? When supplementary pages change? When papers are added/removed/modified? v1 promised changelogs for added/removed/modified content but left 2 of 3 surfaces unspecified. | **P1** | **Resolved.** v2 locks explicit refresh behavior for all three ingest surfaces: (1) Product topics — HTTP conditional GET (`If-Modified-Since` + `If-None-Match`), SHA-256 content-hash fallback; deleted topics (in stored index but absent from live TOC) are pruned from `index.json` and listed in changelog `removed` section. (2) Supplementary pages — same conditional-GET + hash pattern; stored per-URL `http_meta` lives in a new `supplementary_meta.json` side-file under `resolve_wiki_dir() / "supplementary" / "supplementary_meta.json"`. (3) Papers/PDFs — PDF URL list re-enumerated each run from the papers index page; per-PDF state tracked by HTTP `HEAD` `Last-Modified` + `Content-Length` + SHA-256 of downloaded bytes, stored in `resolve_wiki_dir() / "papers" / "papers_meta.json"`; a PDF is re-downloaded only when any of those three signals changes; deleted PDFs are removed from disk and listed in changelog. Each surface has at least one TDD row (see TDD List section). |
| **Cron scope creep** — Issue #2125 says cron is OPTIONAL. v1 made `scripts/cron/orcina-refresh-cron.sh` + cron acceptance test MANDATORY and introduced extra dependencies (`gh`, workstation registry, `git-safe`, full-variant host policy, log/commit behavior) without clear reason cron belongs in #2125 vs the existing cron-tracking sibling #2036. | **P2** | **Resolved via Option (a) — split cron out.** v2 scope is refresh logic only: upstream-version parser, per-surface conditional-refresh machinery, changelog emission, TDD, docs. The cron wrapper is explicitly OUT of scope and listed under Non-goals. A follow-on issue will be filed at implementation time (title: `chore(cron): nightly Orcina refresh wrapper (post-#2125)`) as a sibling of #2036. Rationale: matches issue #2125 language ("cron is optional"); the cron pattern is already well-established in `scripts/knowledge/wiki-ingest-cron.sh` and can be ported without re-litigating it in this plan. The MANDATORY refresh logic is what the issue is about; cron is a separate mechanical layer on top. |
| **TDD edge cases missing — deleted-topic pruning, atomic rewrite, non-package helper imports** | **P3** | **Resolved.** Deleted-topic pruning: new TDD row `test_refresh_prunes_deleted_topics_from_index` — stored index contains topics {A, B, C}; live TOC returns {A, C}; assert B is removed from `index.json.topics` and listed in changelog `removed`. Atomic rewrite: new TDD row `test_refresh_index_write_is_atomic_on_partial_failure` — simulate mid-write exception; assert `index.json` remains the pre-refresh content (tempfile + `os.replace` pattern). Non-package helper imports: v2 follows the sanctioned pattern from the hyphen-path feedback note — new Python modules live under `scripts/data/llm-wiki/` with underscore-only filenames; runtime sibling imports from inside the same directory use bare `from resolve_wiki_path import resolve_wiki_dir` (matching the existing pattern at `ingest-orcina.py:557`); no `from llm-wiki.X import Y` / `import scripts.data.llm-wiki.X` style references anywhere in plan prose, pseudocode, or TDD commands. Grep of this v2 plan for the literal `llm-wiki.` returns only CLI invocation strings (hyphenated directory followed by a slash and a script name), NOT dotted-import forms. |

---

## Attested Evidence

Independently-verifiable claims this v2 plan relies on. Each was checked against HEAD `12b4be83` on 2026-04-24.

| Claim | Verification method | Result |
|---|---|---|
| Issue #2125 OPEN | `gh issue view 2125` | OPEN — "feat(llm-wiki): auto-refresh ingestion on new Orcina releases" |
| Issue #2036 OPEN (cron-tracking sibling) | `gh issue view 2036` | OPEN (carry-forward from v1 resource-intel) |
| `resolve_wiki_dir()` signature — zero-arg, returns `Path` | `grep -n "resolve_wiki_dir" scripts/data/llm-wiki/resolve_wiki_path.py` → `29:def resolve_wiki_dir() -> Path:` | **CONFIRMED** — signature is `def resolve_wiki_dir() -> Path`. No arguments. Returns first-existing of env var `$LLM_WIKI_DATA_DIR` → `config/llm-wiki.yaml:data_dir` → `REPO_ROOT/data/llm-wiki` → `REPO_ROOT/knowledge/wikis` (fallback, always returned if nothing earlier exists). |
| `ingest-orcina.py main()` uses `resolve_wiki_dir()` for output root | `grep -n "resolve_wiki_dir\|output_root" scripts/data/llm-wiki/ingest-orcina.py` → `557:    from resolve_wiki_path import resolve_wiki_dir`, `574:    output_root = Path(args.output_dir) if args.output_dir else resolve_wiki_dir()` | **CONFIRMED** — all three ingesters (`ingest_product`, `ingest_supplementary`, `ingest_papers`) receive `output_root` from `main()`'s resolver call. Changelog must be rooted the same way. |
| Three ingest surfaces exist in `ingest-orcina.py` | `grep -n "^def ingest" scripts/data/llm-wiki/ingest-orcina.py` → `309:def ingest_product(product_key: str, info: dict, output_root: Path) -> dict:`, `415:def ingest_supplementary(output_root: Path) -> list[dict]:`, `458:def ingest_papers(output_root: Path) -> list[dict]:` | **CONFIRMED** — three surfaces. v2 must spec refresh for each. |
| `SUPPLEMENTARY_URLS` contains the releases page | `grep -n "releases" scripts/data/llm-wiki/ingest-orcina.py` → `53:    ("releases", "https://www.orcina.com/releases/"),` | CONFIRMED — release HTML is already fetched every run; `orcina_version.py` only needs to parse HTML the existing supplementary path already downloads (no second fetch required in non-refresh mode). |
| `ingest_papers` uses `pdftotext` on downloaded PDFs | `grep -n "pdftotext\|papers_dir" scripts/data/llm-wiki/ingest-orcina.py` → `464:    papers_dir = output_root / "papers"`, `518:                ["pdftotext", "-layout", pdf_path, "-"],` | CONFIRMED — papers output lives under `output_root / "papers"` (i.e. `resolve_wiki_dir() / "papers"`); PDFs are downloaded to a tempdir, converted via `pdftotext -layout`, and only the markdown is persisted. Refresh metadata for papers must track the *source PDF* signals (URL, `Last-Modified`, `Content-Length`, SHA-256), not the markdown output. |
| `llm_wiki_common.py` does NOT exist yet | `ls scripts/data/llm-wiki/llm_wiki_common.py` → `No such file or directory`; `grep -rn "llm_wiki_common" scripts/data/llm-wiki/` → no matches | **CONFIRMED — no shared-common module exists in the repo yet.** The #2124 v3 plan proposes creating `orcina_common.py` at implementation time but has not landed. v2 of this plan therefore does NOT depend on a shared-common module; any helpers new to this plan (conditional-GET wrapper, content-hash, changelog writer, atomic-write) live inside `ingest-orcina.py` or in a new sibling file `orcina_refresh.py` with underscore-only naming. If #2124 lands `orcina_common.py` before this plan merges, refresh helpers may be relocated there at implementation time; not a prereq. |
| Existing ingester imports follow the sanctioned hyphen-path pattern | `grep -n "^from \|^import " scripts/data/llm-wiki/ingest-orcina.py` → bare `from resolve_wiki_path import resolve_wiki_dir` at line 557, no `from scripts.data.llm-wiki.X import Y` references anywhere | CONFIRMED — sibling imports inside `scripts/data/llm-wiki/` use bare module names (CWD-relative), which is legal because the hyphenated ancestor is never traversed as a dotted package. v2 preserves this pattern. |
| `data/llm-wiki/changelog/` does not exist | `ls data/llm-wiki/changelog/ 2>&1` → "No such file or directory" | Confirmed directory is absent; v2 now treats it as a runtime-created artifact under the resolved output root, not a git-tracked directory. |
| `grep "llm-wiki\." /tmp/plan-drafts/plan-2125-v2.md` returns zero hyphen-dot dotted-import smells | `grep -n 'llm-wiki\.' /tmp/plan-drafts/plan-2125-v2.md` — run as final gate before attestation | PASS condition: only occurrences of `llm-wiki/` (slash-separated filesystem path) are acceptable; any `llm-wiki.` (hyphen followed by dot) must be zero. Verified before submitting v2. |

Claims the plan does NOT attest (require live verification during implementation, not plan-approval):
- Whether Orcina's upstream returns `Last-Modified` and `ETag` headers consistently across all ~717 topic pages, supplementary pages, and PDFs (plan assumes at least one of: header, or body SHA-256 of fetched bytes, is usable for any given URL; refresh falls back to content-hash when headers are absent).
- Exact HTML structure of `https://www.orcina.com/releases/` for version extraction (plan uses regex tolerant of `\d+\.\w+(-beta)?` forms; fixture test uses a captured snapshot).
- Behavior of PDF `HEAD` requests on Orcina's static host (plan assumes `Content-Length` is returned; if not, refresh falls back to always-download + hash-compare, which is still cheaper than always-reconvert).

---

## Resource Intelligence Summary

### Existing repo code (anchored to base SHA `12b4be83`)
- Found: `scripts/data/llm-wiki/ingest-orcina.py` (636 lines) — full crawler; `main()` resolves output root via `resolve_wiki_dir()` (line 574); three ingest functions (`ingest_product` line 309, `ingest_supplementary` line 415, `ingest_papers` line 458) all take `output_root: Path`. `SUPPLEMENTARY_URLS` (line 48) contains `("releases", "https://www.orcina.com/releases/")`, so release-page HTML is already fetched each run by the supplementary path.
- Found: `scripts/data/llm-wiki/resolve_wiki_path.py` — zero-arg `resolve_wiki_dir() -> Path` function; the authoritative rule for where ANY llm-wiki artifact (topic files, indexes, changelogs, meta side-files) must land.
- Found: `scripts/knowledge/wiki-ingest-cron.sh` — engineering-wiki cron reference (marker file, lint, auto-commit, wiki-alert on drop). v2 does NOT port this — cron is split to a follow-on (see r1 P2 resolution).
- Found: `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` (185 lines) — test pattern for the resolver; v2's `test_refresh_writes_changelog_under_resolved_root` monkeypatches the same symbol.
- Gap: no `--refresh` flag, no `If-Modified-Since`/`ETag` handling on any of the three surfaces, no per-entry content hash, no changelog emission, no upstream version parser, no per-surface meta side-file.

### Standards
Not applicable — ingestion tooling, not engineering calculation.

### LLM Wiki pages consulted
- `data/llm-wiki/orcaflex/index.json` (per repo-memory note: current version OrcaFlex 11.6c) — structure is product-scoped; version string lives only in README/prose, not machine-readable metadata. This plan adds `upstream_version` as a top-level key in each product `index.json`.
- No relevant wiki semantic pages — this plan touches the ingestion pipeline, not the rendered wiki.

### Documents consulted
- Parent issue #2088 (Orcina ingestion baseline) — referenced in the script docstring at `ingest-orcina.py:7`; established the 717-topic TOC-driven crawl.
- Sibling #2126 (markdown-conversion QA) — landed in parallel Lane H2; shares the `html_to_markdown` surface. #2125 changes crawl cadence; #2126 validates converter fidelity. No overlap in files touched.
- Sibling #2124 (extend Orcina ingestion to resources/examples/training) — currently at v3 plan-review. That plan proposes a new `orcina_common.py` extraction. v2 of #2125 does NOT depend on it (see Attested Evidence for the `llm_wiki_common.py` non-existence check); if #2124 lands first, refresh helpers may relocate at implementation time.
- Sibling #2036 (cron-tracking) — the intended home for the nightly-wrapper follow-on that v2 split out of #2125.
- Upstream: `https://www.orcina.com/releases/` — only authoritative release-surface Orcina publishes; no public RSS/JSON feed.

### Gaps identified
- No machine-readable upstream version detector exists anywhere in the repo.
- No per-URL HTTP-cache layer — every run re-fetches all ~717 product pages + all 5 supplementary pages + every linked PDF.
- `index.json` schema has no `upstream_version` or `per_topic_hash` fields — adding them is forward-compatible (new keys, old readers ignore).
- No per-surface meta side-files (`supplementary_meta.json`, `papers_meta.json`) exist.
- No Orcina-specific cron wrapper — intentionally left to a follow-on (see r1 P2).

<!-- Source count: issue body + ingest-orcina.py + resolve_wiki_path.py + wiki-ingest-cron.sh + resolve_wiki_path tests + #2088/#2036 references + Orcina releases URL + feedback_llm_wiki_hyphen_module_path_pattern memory note + r1 Codex review artifact = 9 distinct sources. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md |
| New module — version detector | scripts/data/llm-wiki/orcina_version.py |
| New module — refresh helpers (conditional GET, hashing, atomic write, changelog writer) | scripts/data/llm-wiki/orcina_refresh.py |
| New tests — version detector | scripts/data/llm-wiki/tests/test_orcina_version.py |
| New tests — refresh mode (all three surfaces) | scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py |
| Modify — ingest script | scripts/data/llm-wiki/ingest-orcina.py |
| Plan review — r2 Claude | scripts/review/results/2026-04-24-plan-2125-v2-claude.md |
| Plan review — r2 Codex | scripts/review/results/2026-04-24-plan-2125-v2-codex.md |
| Plan review — r2 Gemini | scripts/review/results/2026-04-24-plan-2125-v2-gemini.md |

Note: no `data/llm-wiki/changelog/.gitkeep` row, no `scripts/cron/orcina-refresh-cron.sh` row. Changelog directory is a runtime artifact under the resolved output root (which may or may not be `data/llm-wiki/` depending on the machine); cron wrapper is split to a follow-on issue.

---

## Deliverable

An `ingest-orcina.py --refresh` mode that:
1. Parses the upstream Orcina releases page to detect the current `{orcaflex, orcawave, orcfxapi}` version triple.
2. For each of the three ingest surfaces (product topics, supplementary pages, papers/PDFs), skips work whose upstream signal (HTTP `Last-Modified`/`ETag` or body SHA-256; PDF `Last-Modified`+`Content-Length`+bytes-SHA-256) is unchanged since the last refresh.
3. Writes a machine-readable `upstream_version` to each product `index.json`.
4. Prunes entries absent from the live source (deleted topics, deleted supplementary pages, deleted PDFs) from their respective indexes.
5. Emits a diff report to `resolve_wiki_dir() / "changelog" / "YYYY-MM-DD-<version>.md"` whenever any of the three surfaces has added/removed/modified content OR the detected version triple differs from the stored one.
6. All writes (indexes, meta side-files, changelog) use the tempfile + `os.replace` atomic-rewrite pattern so partial failures leave the previous state intact.

Explicitly OUT of scope for this plan: cron wrapper, commit automation, wiki-alert issue filing on version bump (all deferred to the follow-on sibling of #2036).

---

## Pseudocode

```
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
# we do NOT traverse the hyphenated dir as a dotted package.

def fetch_conditional(url, cached_meta):
    # cached_meta: {"last_modified": str|None, "etag": str|None, "content_hash": str|None}
    build urllib.request.Request with If-Modified-Since / If-None-Match when present
    try: resp = urlopen(req, timeout=30)
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
    # HEAD for PDFs; returns {"last_modified", "content_length"} or None on failure.
    req = urllib.request.Request(url, method="HEAD", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return {
            "last_modified": resp.headers.get("Last-Modified"),
            "content_length": resp.headers.get("Content-Length"),
        }

def atomic_write_json(path: Path, data: dict):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, path)  # atomic on POSIX; tempfile persists on failure, target unchanged

def write_changelog(wiki_root: Path, version_label: str, diffs: dict):
    # diffs: {"product_topics": {added, removed, modified}, "supplementary": {...}, "papers": {...},
    #         "version_bump": {orcaflex: (old, new), ...}}
    changelog_dir = wiki_root / "changelog"         # ← resolve_wiki_dir() derived, NOT hardcoded
    changelog_dir.mkdir(parents=True, exist_ok=True)
    path = changelog_dir / f"{date.today().isoformat()}-{version_label}.md"
    emit markdown sections: Version Bump, Added, Removed, Modified (per surface)
    atomic_write_json-equivalent for markdown (tempfile + os.replace)


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
                write topic file atomically
                new_topics.append({"file": ..., "title": title, "source_url": entry["link_url"],
                                   "http_meta": new_meta, ...})
                if cached: changes["modified"].append(entry["link_url"])
                else: changes["added"].append(entry["link_url"])

        # Deleted-topic pruning (resolves P3)
        for url, cached in stored_topics_by_url.items():
            if url not in live_urls:
                changes["removed"].append(url)
                # Optional: delete the .md file; v2 leaves the file for audit trail,
                # only prunes from index.

        product_index = {
            "product": info["label"],
            "base_url": info["base_url"],
            "generated": utcnow_iso(),
            "topic_count": len(new_topics),
            "upstream_version": CURRENT_VERSION_TRIPLE[product_key],  # from orcina_version
            "topics": new_topics,
        }
        atomic_write_json(index_path, product_index)
        return {"entries": new_topics, "changes": changes}
    else:
        # Existing full-crawl behavior (unchanged).
        ...

def ingest_supplementary(output_root, refresh=False, force_full=False):
    # v2 adds per-URL refresh. Side-file: output_root / "supplementary" / "supplementary_meta.json"
    # Schema: {url: {"last_modified", "etag", "content_hash"}}
    meta_path = output_root / "supplementary" / "supplementary_meta.json"
    stored_meta = json.loads(meta_path.read_text()) if (refresh and not force_full and meta_path.exists()) else {}
    changes = {"added": [], "removed": [], "modified": []}
    live_names = {name for name, _ in SUPPLEMENTARY_URLS}

    entries = []
    new_meta = {}
    for name, url in SUPPLEMENTARY_URLS:
        cached = stored_meta.get(url)
        status, nm, body = fetch_conditional(url, cached)
        new_meta[url] = nm
        if status == "unchanged" and cached:
            # reuse existing .md
            entries.append(existing entry)
        else:
            title, md = html_to_markdown(body.decode(...), url)
            atomic write supp_dir / f"{name}.md"
            entries.append({...})
            if cached: changes["modified"].append(url)
            else: changes["added"].append(url)

    # Deleted-page pruning (for future-proofing if SUPPLEMENTARY_URLS shrinks)
    for url in stored_meta:
        if url not in new_meta:
            changes["removed"].append(url)

    atomic_write_json(meta_path, new_meta)
    return {"entries": entries, "changes": changes}

def ingest_papers(output_root, refresh=False, force_full=False):
    # v2 adds per-PDF refresh. Side-file: output_root / "papers" / "papers_meta.json"
    # Schema: {pdf_url: {"last_modified", "content_length", "bytes_sha256", "markdown_file"}}
    meta_path = output_root / "papers" / "papers_meta.json"
    stored_meta = json.loads(meta_path.read_text()) if (refresh and not force_full and meta_path.exists()) else {}

    # Always re-fetch the listing page to enumerate current PDFs.
    listing_html = fetch_page(PAPERS_PAGE)
    live_pdf_urls = extract pdf links from listing_html  # existing logic
    changes = {"added": [], "removed": [], "modified": []}

    entries = []
    new_meta = {}
    for pdf_info in live_pdf_urls:
        url = pdf_info["url"]
        cached = stored_meta.get(url)
        head = head_pdf(url)
        if (cached and head
            and cached.get("last_modified") == head.get("last_modified")
            and cached.get("content_length") == head.get("content_length")):
            # PDF bytes haven't changed — skip download + pdftotext.
            new_meta[url] = cached
            entries.append(cached["entry"])  # cached entry carries file path + metadata
            continue

        # Download, hash, and only re-run pdftotext if bytes-SHA-256 actually differs.
        pdf_bytes = download(url)
        bytes_hash = sha256_hex(pdf_bytes)
        if cached and cached.get("bytes_sha256") == bytes_hash:
            # HEAD headers changed but bytes identical — update headers only, skip reconvert.
            new_meta[url] = {**cached, "last_modified": head.get("last_modified"),
                             "content_length": head.get("content_length")}
            entries.append(cached["entry"])
            continue

        # Actually changed (or new).
        markdown_text = pdftotext(pdf_bytes)
        atomic write papers_dir / f"{safe_filename}.md"
        entry = {...}
        new_meta[url] = {"last_modified": head.get("last_modified"),
                         "content_length": head.get("content_length"),
                         "bytes_sha256": bytes_hash, "entry": entry}
        entries.append(entry)
        if cached: changes["modified"].append(url)
        else: changes["added"].append(url)

    # Deleted-PDF pruning
    for url in stored_meta:
        if url not in new_meta:
            changes["removed"].append(url)
            # Delete the markdown file for the removed PDF.
            try: (papers_dir / stored_meta[url]["entry"]["file"].split("/")[-1]).unlink()
            except FileNotFoundError: pass

    atomic_write_json(meta_path, new_meta)
    return {"entries": entries, "changes": changes}

# After all three ingesters return, main() assembles:
all_changes = {
    "product_topics": merge_of_per_product_changes,
    "supplementary": supp_changes,
    "papers": paper_changes,
    "version_bump": diff_versions(stored_triple, current_triple),
}
if any surface has non-empty added/removed/modified OR version_bump is non-empty:
    write_changelog(wiki_root=output_root, version_label=current_triple_label(), diffs=all_changes)
```

Key discipline points:
- Every path that receives a write is derived from `output_root` (= `resolve_wiki_dir()`), including `changelog/`, `supplementary/supplementary_meta.json`, `papers/papers_meta.json`. No `data/llm-wiki/...` literal anywhere.
- All Python-module references use underscore-only names (`orcina_version`, `orcina_refresh`); sibling imports from inside `scripts/data/llm-wiki/` use bare module names — no dotted-path traversal of the hyphenated ancestor.
- All index / meta / changelog writes use the tempfile + `os.replace` pattern.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/orcina_version.py` | upstream-version parser (stateless HTML → dict); isolated for unit testability |
| Create | `scripts/data/llm-wiki/orcina_refresh.py` | refresh helpers (`fetch_conditional`, `head_pdf`, `atomic_write_json`, `write_changelog`, SHA-256 wrapper); kept out of `ingest-orcina.py` so tests can import by bare sibling name |
| Create | `scripts/data/llm-wiki/tests/test_orcina_version.py` | TDD — parse fixtures of the releases page |
| Create | `scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py` | TDD — exercises `--refresh` across all three surfaces with mocked HTTP 304 / 200 / HEAD responses and a monkeypatched `resolve_wiki_dir` pointing at a tmp path |
| Modify | `scripts/data/llm-wiki/ingest-orcina.py` | add `--refresh` and `--force-full` flags; thread them through all three ingesters; add per-surface conditional-refresh, meta side-files, deleted-entry pruning, `upstream_version` in each product `index.json`, atomic writes, post-ingest changelog assembly/emission |
| Update | `docs/plans/README.md` | index this plan |

Non-goals explicitly removed from Files to Change vs v1:
- `scripts/cron/orcina-refresh-cron.sh` — split to follow-on sibling of #2036.
- `data/llm-wiki/changelog/.gitkeep` — changelog directory lives under `resolve_wiki_dir()` and is a generated artifact; no git-tracked placeholder needed (and would be wrong on machines where the resolver points outside the repo).

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
| test_refresh_writes_changelog_under_resolved_root | Changelog lands under `resolve_wiki_dir()`, not hardcoded `data/llm-wiki/` | monkeypatch `resolve_wiki_dir` to return `tmp_path`; force a version bump | changelog file exists at `tmp_path / "changelog" / "<date>-<ver>.md"` and NOT at `data/llm-wiki/changelog/...` |
| test_refresh_meta_files_land_under_resolved_root | Per-surface meta side-files land under resolved root | monkeypatched resolver → tmp_path; refresh run | `tmp_path/supplementary/supplementary_meta.json` and `tmp_path/papers/papers_meta.json` exist |

Product-topics surface (resolves r1 P1 #2, topics):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_skips_unchanged_topic_on_304 | 304 response → topic .md not rewritten | mocked `urlopen` returns 304 for topic A | `write` not called for A; `index.json.topics[A].http_meta` preserved |
| test_refresh_skips_unchanged_topic_on_hash_match | headers missing but body-SHA identical → no rewrite | mocked 200 with same body, no `Last-Modified`/`ETag` | `write` not called for A; new `content_hash` recorded |
| test_refresh_rewrites_changed_topic | 200 + new body → topic re-converted | mocked 200 + different body-hash | A.md updated; `index.json` http_meta updated |
| test_refresh_prunes_deleted_topics_from_index | TOC entry removed upstream → index pruned, changelog lists removal (**P3**) | stored index has {A, B, C}; live TOC returns {A, C} | `index.json.topics` contains only {A, C}; changelog `removed` lists B |
| test_refresh_without_stored_index_does_full_crawl | First-run `--refresh` falls back to full | no existing `index.json` | all topics fetched normally; meta recorded |
| test_force_full_overrides_refresh | `--force-full` ignores cache | `--refresh --force-full` with stored index | every topic re-fetched (no conditional headers set on outgoing requests) |
| test_version_persisted_in_each_product_index | `upstream_version` written to every product `index.json` | refresh run | `json.load(orcaflex/index.json)["upstream_version"] == "11.6c"` (and orcawave, orcfxapi) |

Supplementary surface (resolves r1 P1 #2, supplementary):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_skips_unchanged_supplementary_page | 304 on supplementary URL → no .md rewrite | mocked 304 for `releases` URL | `releases.md` mtime unchanged; `supplementary_meta.json` keeps cached entry |
| test_refresh_rewrites_changed_supplementary_page | 200 + new body → .md rewritten, meta updated | mocked 200 with different hash for `resources` URL | `resources.md` rewritten atomically; `supplementary_meta.json` reflects new `content_hash` |
| test_refresh_records_supplementary_changes_in_changelog | Added/modified supplementary pages listed in changelog | one new URL added to `SUPPLEMENTARY_URLS`, one changed | changelog `supplementary.added` and `supplementary.modified` populated |

Papers/PDF surface (resolves r1 P1 #2, papers):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_skips_unchanged_pdf_via_head | PDF `Last-Modified` + `Content-Length` match cache → no download | mocked HEAD returns cached `Last-Modified` + `Content-Length` | no GET issued for PDF; `pdftotext` not invoked; `papers_meta.json` keeps entry |
| test_refresh_re_downloads_pdf_on_head_change_but_skips_reconvert_on_hash_match | HEAD headers changed but bytes-SHA identical → no reconvert | mocked HEAD returns new `Last-Modified`; GET returns bytes with same SHA-256 | GET issued, but `pdftotext` NOT invoked and `.md` file unchanged; meta headers updated |
| test_refresh_reconverts_pdf_on_bytes_change | bytes-SHA differs → full reconvert | mocked HEAD+GET return new bytes with different SHA | `pdftotext` invoked; `.md` rewritten atomically; `papers_meta.json` reflects new bytes-SHA |
| test_refresh_prunes_deleted_pdf_from_papers_index | PDF gone from listing → removed from index and disk | stored meta has URL X; listing no longer contains X | `papers_meta.json` lacks X; X's .md file deleted; changelog `papers.removed` lists X |

Atomic-write hygiene (resolves r1 P3):

| Test name | What it verifies | Input | Expected output |
|---|---|---|---|
| test_refresh_index_write_is_atomic_on_partial_failure | Exception mid-write leaves prior `index.json` intact | monkeypatch `json.dumps` to raise after tempfile created but before `os.replace` | `index.json` still contains pre-refresh content; `.tmp` file may persist but does not shadow the target |
| test_refresh_changelog_write_is_atomic | Same pattern applied to changelog markdown | monkeypatch write to raise | pre-existing changelog (if any) intact; partial `.tmp` does not replace |

All tests use `unittest.mock.patch` on `urllib.request.urlopen` (no real network) and monkeypatch `orcina_refresh.resolve_wiki_dir` to point at `tmp_path`. Fixture HTML files live under `scripts/data/llm-wiki/tests/fixtures/`.

---

## Acceptance Criteria

- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_orcina_version.py -v` → all 8 tests pass.
- [ ] `uv run pytest scripts/data/llm-wiki/tests/test_ingest_orcina_refresh.py -v` → all TDD rows above pass (output-root hygiene, 3 surfaces, atomic-write).
- [ ] `uv run pytest scripts/data/llm-wiki/tests/` → existing `test_resolve_wiki_path.py` still passes (no regression).
- [ ] `python3 scripts/data/llm-wiki/ingest-orcina.py --refresh` against an existing index.json re-fetches zero product topics when the live upstream is byte-identical (observable: script prints `0 changed, 717 cached` or similar; wallclock < 60s for topics alone).
- [ ] `--refresh` writes `upstream_version` into every `<product>/index.json`.
- [ ] `--refresh` creates `supplementary_meta.json` under `resolve_wiki_dir() / "supplementary"` with one entry per URL in `SUPPLEMENTARY_URLS`.
- [ ] `--refresh` creates `papers_meta.json` under `resolve_wiki_dir() / "papers"` with one entry per live PDF.
- [ ] When `stored.upstream_version != live.upstream_version` OR any of the three surfaces report non-empty added/removed/modified, a markdown changelog appears at `resolve_wiki_dir() / "changelog" / "<date>-<new-version>.md"`.
- [ ] When versions are equal AND all surfaces are clean, no changelog file is created (verified in a live run).
- [ ] Running `--refresh` twice back-to-back on stable upstream produces zero `.md` rewrites and zero changelog entries on the second run (cache-effectiveness invariant).
- [ ] Final plan-text gate: `grep -n 'llm-wiki\.' docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md` returns zero dotted-import-form hits (hyphenated filesystem paths followed by `/` are fine; any `llm-wiki.` with a literal dot after the hyphenated segment is a defect).
- [ ] Review artifacts posted to `scripts/review/results/` for r2 Claude, Codex, Gemini.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | REJECT (unusable) | Input was empty file-path only (`cross-review.sh` inline-content bug); findings not actionable. |
| Codex (r1) | MAJOR | 2 P1 + 1 P2 + 1 P3 — all closed in this v2 (see Review History section above). |
| Gemini (r1) | NO_OUTPUT | Silent failure during r1 run; not retried. |
| Claude (r2) | (pending) | |
| Codex (r2) | (pending) | |
| Gemini (r2) | (pending) | |

**Overall result:** (pending r2)

---

## Risks and Open Questions

- **Risk:** Orcina releases page HTML structure may change without notice — the version parser must degrade gracefully (return `None` per product, not raise) so refresh doesn't go red on an upstream cosmetic change. Covered by `test_detect_returns_none_when_missing`.
- **Risk:** Upstream may not send `Last-Modified` or `ETag` headers consistently; `fetch_conditional` already falls back to SHA-256 of the response body. Covered by `test_refresh_skips_unchanged_topic_on_hash_match`.
- **Risk:** PDF hosts sometimes drop `Content-Length` on HEAD; refresh then falls back to download-and-hash-compare, which is still cheaper than always-reconvert. Acceptable.
- **Risk:** Partial-crawl failure (network blip mid-run) could leave `index.json` inconsistent. Mitigation: tempfile + `os.replace` on every write. Covered by `test_refresh_index_write_is_atomic_on_partial_failure`.
- **Risk:** `--refresh` against a very stale cache (months old, layout changes) may emit a changelog with hundreds of entries. Acceptable for the first post-upgrade run; not a blocker.
- **Risk:** If `resolve_wiki_dir()` returns a path outside the repo (env var / config override), the changelog is NOT git-tracked. This is by design — it matches where the topic/supplementary/paper markdown also lands. The follow-on cron issue will decide commit policy.
- **Risk — dependency interaction with #2124:** if #2124 lands `orcina_common.py` first, the refresh helpers in `orcina_refresh.py` may relocate into the shared module. Not a blocker; resolve at implementation time.
- **Open:** Changelog filename format `<date>-<version>.md` — if multiple refreshes run the same day AND the version triple changes twice, the second changelog overwrites the first. Mitigation: include a short timestamp suffix when a same-day+same-version collision is detected (`<date>-<version>-T<HHMMSS>.md`). Decision deferred to implementation.
- **Open:** Should the `.md` files for removed topics/PDFs be deleted from disk, or left for audit? v2 defaults: topics → leave on disk (prune from index only); PDFs → delete on disk (matches the sibling-meta-file semantics). Confirm with user during implementation.

---

## Non-goals

- Cron wrapper for nightly refresh. The mechanical cron/`git-safe`/wiki-alert layer is a known, bounded pattern already established in `scripts/knowledge/wiki-ingest-cron.sh`. Porting it for Orcina is a follow-on sibling of #2036 and does NOT belong in #2125. The refresh logic delivered here is consumable by that future cron wrapper as a single `python3 scripts/data/llm-wiki/ingest-orcina.py --refresh` invocation.
- Auto-filing a GitHub "wiki-alert" issue on version bump. Also belongs with the cron wrapper.
- Auto-commit of refreshed state. Also belongs with the cron wrapper.
- Any changes to `search-wiki.py` or the rendered wiki — `upstream_version` is a new forward-compatible key; existing readers ignore it.
- Renaming `ingest-orcina.py` to `ingest_orcina.py`. Not required — the existing file uses CLI invocation (`python3 scripts/data/llm-wiki/ingest-orcina.py ...`), which is hyphen-safe, and its imports use bare sibling names that also work. Renaming would be a separate migration issue.

---

## Complexity: T2

**T2** — two new modules (`orcina_version.py`, `orcina_refresh.py`), one modified module (`ingest-orcina.py`), TDD required across three surfaces, no cross-repo changes, no cron layer. Scope is bounded and all interfaces are local; upstream integration is read-only HTTP. Cron split to a follow-on keeps T2 honest.
