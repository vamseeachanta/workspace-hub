# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Render a per-session live-link HTML work-review doc (#3298).

Companion to #2110 (machine-readable session-close report): #2110 emits the
structured payload, this renders the human-facing reviewable page and maintains
a rolling index. Pages are self-contained (inline CSS, no external asset refs)
and PUBLIC-SAFE — sanitized at render time via `session_review_sanitize` before
being written, so `scripts/build_pages.py` can copy them verbatim into the
public GitHub Pages site (stdlib-only there).

Outputs under `docs/reports/sessions/`:
  <date>-<slug>.html   one page per session
  index.html           rolling, newest-first index with live links
  manifest.json        enumerated list the Pages builder copies (no glob)

CLI:  uv run python scripts/workflow/build_session_review.py <payload.json>
Payload schema (all fields optional except slug+date+title):
  {slug, date, title, lane, summary,
   kpis:[{n,l}], issues:[{num,state,note}], prs:[{num,what,status}],
   decisions:[str], artifacts:[str], next_steps:[str]}
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_review_sanitize as sani  # noqa: E402

REPO = "https://github.com/vamseeachanta/workspace-hub"

_STYLE = """
:root{--fg:#1a2230;--muted:#5b6675;--bg:#f7f8fa;--card:#fff;--line:#e2e6ec;--brand:#5b3fd6;--warn:#b06a00}
*{box-sizing:border-box}
body{margin:0;font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg)}
header{padding:20px 22px;background:var(--card);border-bottom:1px solid var(--line)}
header h1{font-size:20px;margin:0 0 4px}
header .meta{color:var(--muted);font-size:13px}
header .home{color:var(--brand);text-decoration:none;font-size:13px}
header .headline{margin:8px 0 0;font-size:15px}
main{max-width:860px;margin:0 auto;padding:20px 22px}
.refs{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:4px 18px}
.row{display:flex;gap:14px;padding:9px 0;border-bottom:1px solid var(--line);align-items:baseline}
.row:last-child{border-bottom:0}
.k{flex:0 0 92px;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.v{flex:1;font-size:14px}
.v a{color:var(--brand);text-decoration:none}.v a:hover{text-decoration:underline}
.sep{color:var(--line);margin:0 3px}
.warn{color:var(--warn)}
footer{color:var(--muted);font-size:12px;text-align:center;padding:16px}
.idx{list-style:none;padding:0}.idx li{margin:0 0 10px;padding:0}
.idx a{font-weight:600;font-size:16px}.idx .d{color:var(--muted);font-size:13px}
"""

# Ordered reference groups: (payload type, plural heading). The page is a lean
# index of pointers — substance lives in each ref's canonical home.
_REF_GROUPS = [
    ("issue", "Issues"), ("pr", "PRs"), ("commit", "Commits"),
    ("plan", "Plans"), ("decision", "Decisions"), ("handoff", "Record"),
    ("report", "Reports"), ("link", "Links"),
]
_REPO_PATH_FOR = {"issue": "issues", "pr": "pull", "commit": "commit"}


def _esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _ref_href(ref: dict, repo_root=None):
    """Resolve a reference to (href, missing). Substance is NOT inlined — the
    href points at the artifact's canonical home (GitHub issue/PR/commit, or a
    repo blob path). `missing` flags a `path` ref absent from disk at build."""
    if ref.get("href"):
        return str(ref["href"]), False
    t = ref.get("type")
    if t in _REPO_PATH_FOR and ref.get("num") not in (None, ""):
        return f"{REPO}/{_REPO_PATH_FOR[t]}/{ref['num']}", False
    if ref.get("path"):
        path = str(ref["path"])
        missing = repo_root is not None and not (Path(repo_root) / path).exists()
        return f"{REPO}/blob/main/{path}", missing
    if t == "decision" and ref.get("num") not in (None, ""):
        return f"{REPO}/issues/{ref['num']}", False  # decided in an issue/PR thread
    return "", False


def _ref_label(ref: dict) -> str:
    if ref.get("label"):
        return _esc(ref["label"])
    if ref.get("num") not in (None, ""):
        return f"#{_esc(ref['num'])}"
    if ref.get("path"):
        return _esc(ref["path"])
    return _esc(ref.get("href", "?"))


def _ref_anchor(ref: dict, repo_root=None) -> str:
    href, missing = _ref_href(ref, repo_root)
    label = _ref_label(ref)
    warn = '<span class="warn" title="path not found at build">⚠ </span>' if missing else ""
    return f'{warn}<a href="{_esc(href)}">{label}</a>' if href else f"{warn}{label}"


def _normalize_refs(payload: dict) -> list[dict]:
    """Return the v2 `refs` list. v2 payloads pass through; v1 payloads
    (issues[]/prs[]) are shimmed into refs so older payloads still render lean."""
    if payload.get("refs"):
        return list(payload["refs"])
    refs: list[dict] = []
    for i in payload.get("issues") or []:
        refs.append({"type": "issue", "num": i.get("num"), "label": i.get("note")})
    for p in payload.get("prs") or []:
        refs.append({"type": "pr", "num": p.get("num"), "label": p.get("what")})
    return refs


def _shell(title: str, body: str, home: str = "../index.html") -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_esc(title)}</title>\n<style>{_STYLE}</style></head>\n<body>\n"
        + body
        + "\n</body></html>\n"
    )


def render_session_html(payload: dict, repo_root=None) -> str:
    """Render a LEAN reference-layer session page: a grouped index of links to
    each artifact's canonical home (code→PRs/commits, plans→docs/plans,
    decisions→issue/PR, log→handoff doc). Restates nothing beyond an optional
    one-line headline. Assumes payload is already sanitized (use `build`)."""
    slug = _esc(payload.get("slug", "session"))
    date = _esc(payload.get("date", ""))
    title = _esc(payload.get("title", "Session Review"))
    lane = _esc(payload.get("lane", ""))
    headline = payload.get("headline") or payload.get("summary") or ""
    refs = _normalize_refs(payload)

    body = (
        f'<header><a class="home" href="../index.html">← workspace-hub</a>'
        f"<h1>{title}</h1>"
        f'<div class="meta">{date} · session record'
        + (f" · lane:{lane}" if lane else "")
        + " · public-safe (references only)</div>"
        + (f'<p class="headline">{_esc(headline)}</p>' if headline else "")
        + '</header>\n<main><div class="refs">'
    )

    known = {g[0] for g in _REF_GROUPS}
    rows: list[str] = []
    for t, heading in _REF_GROUPS:
        group = [r for r in refs if r.get("type") == t]
        if group:
            anchors = ' <span class="sep">·</span> '.join(_ref_anchor(r, repo_root) for r in group)
            rows.append(f'<div class="row"><span class="k">{heading}</span><span class="v">{anchors}</span></div>')
    other = [r for r in refs if r.get("type") not in known]  # never silently drop a ref
    if other:
        anchors = ' <span class="sep">·</span> '.join(_ref_anchor(r, repo_root) for r in other)
        rows.append(f'<div class="row"><span class="k">Other</span><span class="v">{anchors}</span></div>')

    body += ("".join(rows) or '<div class="row"><span class="v">No artifacts referenced.</span></div>')
    body += ("</div></main><footer>workspace-hub · session record · references canonical homes "
             "(code→PRs · plans→docs/plans · decisions→issue/PR · log→handoff) · " + slug + "</footer>")
    return _shell(f"Session · {date} · {title}", body)


def render_index_html(entries: list[dict]) -> str:
    """Rolling index of session reviews, newest-first, with live links."""
    rows = "".join(
        f'<li><a href="{_esc(e["file"])}">{_esc(e.get("title", e["slug"]))}</a>'
        f'<div class="d">{_esc(e.get("date", ""))}'
        + (f" · lane:{_esc(e['lane'])}" if e.get("lane") else "")
        + "</div></li>"
        for e in entries
    )
    body = (
        '<header><a class="home" href="../index.html">← workspace-hub</a>'
        "<h1>Session Reviews</h1>"
        '<div class="meta">Per-session work-review docs (#3298) · newest first · public-safe</div>'
        "</header>\n<main><section><ul class=\"idx\">" + (rows or "<li>No sessions yet.</li>")
        + "</ul></section></main><footer>workspace-hub · session reviews</footer>"
    )
    return _shell("Session Reviews · workspace-hub", body)


def update_manifest(manifest_path: Path, entry: dict) -> list[dict]:
    """Insert/replace `entry` (keyed by slug) and persist newest-first."""
    entries: list[dict] = []
    if manifest_path.exists():
        entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = [e for e in entries if e.get("slug") != entry["slug"]]
    entries.append(entry)
    entries.sort(key=lambda e: (e.get("date", ""), e.get("slug", "")), reverse=True)
    manifest_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    return entries


def build(payload: dict, sessions_dir: Path, patterns: list[tuple[str, bool]],
          public: bool = True, repo_root=None) -> dict:
    """Sanitize (if public), render the page + index, update the manifest.

    `repo_root` (when given) lets the renderer verify `path` refs exist on disk
    and flag missing ones; pass None to skip verification (e.g. in unit tests).
    Returns the manifest entry. Raises SanitizationError if a denied client
    pattern survives into the public page (fail-closed)."""
    if public:
        payload = sani.sanitize_payload(payload, patterns)
    slug = payload.get("slug") or "session"
    date = payload.get("date") or "0000-00-00"
    file_name = f"{date}-{slug}.html"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    page = render_session_html(payload, repo_root=repo_root)
    if public:
        sani.assert_clean(page, patterns)  # last-line fail-closed gate
    (sessions_dir / file_name).write_text(page, encoding="utf-8")

    entry = {"slug": slug, "date": date, "title": payload.get("title", slug),
             "lane": payload.get("lane", ""), "file": file_name}
    entries = update_manifest(sessions_dir / "manifest.json", entry)
    (sessions_dir / "index.html").write_text(render_index_html(entries), encoding="utf-8")
    return entry


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: build_session_review.py <payload.json>", file=sys.stderr)
        return 2
    repo_root = Path(__file__).resolve().parents[2]
    payload = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    patterns = sani.load_deny_patterns(repo_root / ".legal-deny-list.yaml")
    sessions_dir = repo_root / "docs" / "reports" / "sessions"
    entry = build(payload, sessions_dir, patterns, public=True, repo_root=repo_root)
    print(f"Wrote {sessions_dir / entry['file']} and refreshed index ({entry['slug']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
