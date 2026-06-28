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
:root{--fg:#1a2230;--muted:#5b6675;--bg:#f7f8fa;--card:#fff;--line:#e2e6ec;--brand:#5b3fd6;--ok:#1a7f4b;--warn:#b06a00;--hold:#9a3412}
*{box-sizing:border-box}
body{margin:0;font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg)}
header{padding:22px;background:var(--card);border-bottom:1px solid var(--line)}
header h1{font-size:22px;margin:0 0 4px}
header .meta{color:var(--muted);font-size:14px}
header .home{color:var(--brand);text-decoration:none;font-size:13px}
main{max-width:920px;margin:0 auto;padding:24px 22px}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:0 0 18px}
section h2{font-size:16px;margin:0 0 12px;border-bottom:1px solid var(--line);padding-bottom:8px}
.kpis{display:flex;gap:10px;flex-wrap:wrap}
.kpi{flex:1 1 120px;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.kpi .n{font-size:26px;font-weight:700}
.kpi .l{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#f0f3f7}
a{color:var(--brand)}
ul{margin:6px 0;padding-left:20px}li{margin:3px 0}
footer{color:var(--muted);font-size:13px;text-align:center;padding:18px}
.idx{list-style:none;padding:0}.idx li{margin:0 0 10px;padding:0}
.idx a{font-weight:600;font-size:16px}.idx .d{color:var(--muted);font-size:13px}
"""


def _esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _issue_link(num) -> str:
    return f'<a href="{REPO}/issues/{_esc(num)}">#{_esc(num)}</a>'


def _pr_link(num) -> str:
    return f'<a href="{REPO}/pull/{_esc(num)}">#{_esc(num)}</a>'


def _shell(title: str, body: str, home: str = "../index.html") -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_esc(title)}</title>\n<style>{_STYLE}</style></head>\n<body>\n"
        + body
        + "\n</body></html>\n"
    )


def render_session_html(payload: dict) -> str:
    """Render a self-contained session-review page. Assumes payload is already
    sanitized (call `build` for the sanitize-then-render path)."""
    slug = _esc(payload.get("slug", "session"))
    date = _esc(payload.get("date", ""))
    title = _esc(payload.get("title", "Session Review"))
    lane = _esc(payload.get("lane", ""))
    parts: list[str] = []
    parts.append(
        f'<header><a class="home" href="../index.html">← workspace-hub</a>'
        f"<h1>Session Review — {title}</h1>"
        f'<div class="meta">{date} · workspace-hub'
        + (f" · lane:{lane}" if lane else "")
        + " · public-safe (issue/PR numbers + verdicts only)</div></header>\n<main>"
    )

    kpis = payload.get("kpis") or []
    if kpis:
        cells = "".join(
            f'<div class="kpi"><div class="n">{_esc(k.get("n"))}</div>'
            f'<div class="l">{_esc(k.get("l"))}</div></div>'
            for k in kpis
        )
        parts.append(f'<section><h2>At a glance</h2><div class="kpis">{cells}</div>'
                     + (f"<p>{_esc(payload['summary'])}</p>" if payload.get("summary") else "")
                     + "</section>")
    elif payload.get("summary"):
        parts.append(f"<section><h2>At a glance</h2><p>{_esc(payload['summary'])}</p></section>")

    prs = payload.get("prs") or []
    if prs:
        rows = "".join(
            f"<tr><td>{_pr_link(p.get('num'))}</td><td>{_esc(p.get('what'))}</td>"
            f"<td>{_esc(p.get('status'))}</td></tr>"
            for p in prs
        )
        parts.append("<section><h2>Pull requests</h2><table><thead><tr>"
                     "<th>PR</th><th>What</th><th>Status</th></tr></thead><tbody>"
                     + rows + "</tbody></table></section>")

    issues = payload.get("issues") or []
    if issues:
        rows = "".join(
            f"<tr><td>{_issue_link(i.get('num'))}</td><td>{_esc(i.get('state'))}</td>"
            f"<td>{_esc(i.get('note'))}</td></tr>"
            for i in issues
        )
        parts.append("<section><h2>Issues &amp; plans</h2><table><thead><tr>"
                     "<th>Issue</th><th>State</th><th>Note</th></tr></thead><tbody>"
                     + rows + "</tbody></table></section>")

    for key, heading in (("decisions", "Decisions"), ("artifacts", "Artifacts"),
                         ("next_steps", "Next steps")):
        items = payload.get(key) or []
        if items:
            lis = "".join(f"<li>{_esc(x)}</li>" for x in items)
            parts.append(f"<section><h2>{heading}</h2><ul>{lis}</ul></section>")

    parts.append("</main><footer>workspace-hub · session review · "
                 f"generated by build_session_review.py · {slug}</footer>")
    return _shell(f"Session Review · {date} · {title}", "".join(parts))


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
          public: bool = True) -> dict:
    """Sanitize (if public), render the page + index, update the manifest.

    Returns the manifest entry. Raises SanitizationError if a denied client
    pattern survives into the public page (fail-closed)."""
    if public:
        payload = sani.sanitize_payload(payload, patterns)
    slug = payload.get("slug") or "session"
    date = payload.get("date") or "0000-00-00"
    file_name = f"{date}-{slug}.html"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    page = render_session_html(payload)
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
    entry = build(payload, sessions_dir, patterns, public=True)
    print(f"Wrote {sessions_dir / entry['file']} and refreshed index ({entry['slug']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
