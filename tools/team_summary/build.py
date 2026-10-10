"""Build the client team summary: YAML facts -> HTML -> PDF (workspace-hub#3967).

The generator is client-agnostic. Each client wiki holds its own facts file
(reports/team-summary/summary.yml) and the one canonical PDF beside it; git
history of that PDF is the change history.

Usage:
    uv run python tools/team_summary/build.py --data <summary.yml> --out <team-summary.pdf>
        [--html <path>] [--wiki-root <client wiki checkout>] [--check-sources]
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "team-summary.schema.json"

SECTION_ORDER = [
    "learn_or_solve",
    "priorities",
    "issues",
    "decisions",
    "areas",
    "deliverables",
    "sources",
]
SECTION_TITLES = {
    "learn_or_solve": "What are you here to learn or solve?",
    "priorities": "Top priorities",
    "issues": "Outstanding issues",
    "decisions": "Decisions and blockers",
    "areas": "By area",
    "deliverables": "Current deliverables",
    "sources": "Sources",
}
AREA_ORDER = ["marketing", "technical", "data", "projects"]
AREA_TITLES = {
    "marketing": "Marketing and business development",
    "technical": "Technical and engineering",
    "data": "Data and analytics",
    "projects": "Projects and delivery",
}
STATUS_LABELS = {
    "open": "Open",
    "investigating": "Investigating",
    "awaiting-review": "Awaiting review",
    "resolved": "Resolved",
}

escape = html.escape


def _normalise(value):
    """YAML parses ISO dates into date objects; the schema expects strings."""
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    return value


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return _normalise(yaml.safe_load(fh))


def validate(data: dict) -> list[str]:
    """Return schema errors as 'path: message' strings; empty means valid."""
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover - dev dependency
        raise SystemExit("jsonschema is required: uv sync (dev group)") from exc
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{where}: {err.message}")
    return errors


def collect_sources(data: dict) -> list[str]:
    """Unique sources in order of first appearance in the rendered sections."""
    seen: list[str] = []

    def add(items):
        for item in items or []:
            src = item.get("source")
            if src and src not in seen:
                seen.append(src)

    add(data.get("priorities"))
    add(data.get("issues"))
    add(data.get("decisions"))
    add(data.get("blockers"))
    for key in AREA_ORDER:
        add((data.get("areas") or {}).get(key))
    add(data.get("deliverables"))
    return seen


CSS = """
@page { size: Letter; margin: 16mm 16mm 18mm; }
:root { --ink:#1c2a33; --muted:#5a6a74; --rule:#cfd8dd; --band:#0f4c5c; --soft:#eef3f5;
        --open:#9a3b2f; --inv:#8a5a00; --rev:#2d5d8a; --res:#2f6b3a; }
* { box-sizing: border-box; }
body { margin:0; color:var(--ink); font: 10.5pt/1.45 "Segoe UI", "Liberation Sans", Arial, sans-serif; }
header { background:var(--band); color:#fff; padding:14px 18px; display:flex; justify-content:space-between; align-items:flex-end; gap:16px; }
header h1 { margin:0; font-size:20pt; font-weight:600; letter-spacing:.01em; }
header .kind { font-size:9pt; text-transform:uppercase; letter-spacing:.12em; opacity:.85; }
header .meta { text-align:right; font-size:9pt; opacity:.9; }
section { margin-top:14px; break-inside:avoid-page; }
h2 { font-size:12pt; margin:0 0 6px; padding-bottom:3px; border-bottom:1.5px solid var(--band); color:var(--band); }
h3 { font-size:10.5pt; margin:8px 0 3px; }
p { margin:0; }
.lead { background:var(--soft); padding:8px 12px; border-left:3px solid var(--band); font-size:11pt; }
table { width:100%; border-collapse:collapse; font-size:9.5pt; }
th { text-align:left; font-weight:600; color:var(--muted); font-size:8pt; text-transform:uppercase; letter-spacing:.06em; border-bottom:1px solid var(--rule); padding:4px 6px; }
td { border-bottom:1px solid var(--rule); padding:5px 6px; vertical-align:top; }
tr { break-inside:avoid; }
.num { font-variant-numeric: tabular-nums; white-space:nowrap; }
.chip { display:inline-block; padding:0 6px; border:1px solid currentColor; border-radius:9px; font-size:8pt; font-weight:600; white-space:nowrap; }
.s-open { color:var(--open); } .s-investigating { color:var(--inv); }
.s-awaiting-review { color:var(--rev); } .s-resolved { color:var(--res); }
ul { margin:2px 0 0; padding-left:16px; }
li { margin:2px 0; }
sup.ref { font-size:7pt; color:var(--muted); }
.empty { color:var(--muted); font-style:italic; }
ol.sources { font-size:8.5pt; color:var(--muted); padding-left:20px; margin:0; }
ol.sources li { word-break:break-all; }
footer { margin-top:16px; font-size:8pt; color:var(--muted); border-top:1px solid var(--rule); padding-top:6px; }
"""


def render_html(data: dict) -> str:
    sources = collect_sources(data)
    index = {src: i + 1 for i, src in enumerate(sources)}

    def ref(item) -> str:
        n = index.get(item.get("source"))
        return f'<sup class="ref">[{n}]</sup>' if n else ""

    e = escape
    out: list[str] = []
    out.append("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">")
    out.append(f"<title>{e(data['client'])} team summary {e(data['as_of'])}</title>")
    out.append(f"<style>{CSS}</style></head><body>")

    rev = data.get("wiki_revision")
    out.append(
        "<header><div><div class=\"kind\">Team summary</div>"
        f"<h1>{e(data['client'])}</h1></div>"
        f"<div class=\"meta\">As of {e(data['as_of'])}"
        + (f"<br>Wiki revision {e(rev)}" if rev else "")
        + "</div></header>"
    )

    out.append(f"<section><h2>{SECTION_TITLES['learn_or_solve']}</h2>")
    out.append(f"<p class=\"lead\">{e(data['learn_or_solve'])}</p></section>")

    out.append(f"<section><h2>{SECTION_TITLES['priorities']}</h2>")
    if data.get("priorities"):
        out.append("<table><tr><th>Priority</th><th>Owner</th><th>Next action</th><th>Due</th></tr>")
        for p in data["priorities"]:
            out.append(
                f"<tr><td>{e(p['title'])}{ref(p)}</td><td>{e(p['owner'])}</td>"
                f"<td>{e(p['next_action'])}</td><td class=\"num\">{e(p['due'])}</td></tr>"
            )
        out.append("</table>")
    else:
        out.append("<p class=\"empty\">No priorities recorded.</p>")
    out.append("</section>")

    out.append(f"<section><h2>{SECTION_TITLES['issues']}</h2>")
    if data.get("issues"):
        out.append("<table><tr><th>Issue</th><th>Status</th><th>Owner</th><th>Next action</th></tr>")
        for i in data["issues"]:
            status = i["status"]
            out.append(
                f"<tr><td>{e(i['title'])}{ref(i)}</td>"
                f"<td><span class=\"chip s-{e(status)}\">{e(STATUS_LABELS[status])}</span></td>"
                f"<td>{e(i['owner'])}</td><td>{e(i['next_action'])}</td></tr>"
            )
        out.append("</table>")
    else:
        out.append("<p class=\"empty\">No outstanding issues recorded.</p>")
    out.append("</section>")

    decisions, blockers = data.get("decisions") or [], data.get("blockers") or []
    if decisions or blockers:
        out.append(f"<section><h2>{SECTION_TITLES['decisions']}</h2>")
        if decisions:
            out.append("<h3>Decisions</h3><ul>")
            for d in decisions:
                out.append(f"<li><span class=\"num\">{e(d['date'])}</span> {e(d['text'])}{ref(d)}</li>")
            out.append("</ul>")
        if blockers:
            out.append("<h3>Blockers</h3><ul>")
            for b in blockers:
                out.append(f"<li>{e(b['text'])} <em>Owner: {e(b['owner'])}</em>{ref(b)}</li>")
            out.append("</ul>")
        out.append("</section>")

    areas = data.get("areas") or {}
    present = [k for k in AREA_ORDER if areas.get(k)]
    if present:
        out.append(f"<section><h2>{SECTION_TITLES['areas']}</h2>")
        for key in present:
            out.append(f"<h3>{AREA_TITLES[key]}</h3><ul>")
            for item in areas[key]:
                out.append(f"<li>{e(item['text'])}{ref(item)}</li>")
            out.append("</ul>")
        out.append("</section>")

    if data.get("deliverables"):
        out.append(f"<section><h2>{SECTION_TITLES['deliverables']}</h2>")
        out.append("<table><tr><th>Deliverable</th><th>Version</th><th>Status</th></tr>")
        for d in data["deliverables"]:
            out.append(
                f"<tr><td>{e(d['name'])}{ref(d)}</td><td class=\"num\">{e(d['version'])}</td>"
                f"<td>{e(d['status'])}</td></tr>"
            )
        out.append("</table></section>")

    out.append(f"<section><h2>{SECTION_TITLES['sources']}</h2><ol class=\"sources\">")
    for src in sources:
        out.append(f"<li>{e(src)}</li>")
    out.append("</ol></section>")

    out.append(
        "<footer>Generated from the client wiki, which is the single source of truth. "
        "Items marked awaiting review are not yet accepted conclusions.</footer>"
    )
    out.append("</body></html>")
    return "\n".join(out)


BROWSER_CANDIDATES = [
    "google-chrome",
    "chromium",
    "chromium-browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser() -> str | None:
    override = os.environ.get("TEAM_SUMMARY_BROWSER")
    for cand in ([override] if override else []) + BROWSER_CANDIDATES:
        found = shutil.which(cand) or (cand if Path(cand).is_file() else None)
        if found:
            return found
    return None


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    browser = find_browser()
    if browser is None:
        raise SystemExit("No headless Chrome or Edge found; set TEAM_SUMMARY_BROWSER.")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            browser,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            "--print-background",
            "--virtual-time-budget=3000",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    if not pdf_path.is_file() or pdf_path.read_bytes()[:5] != b"%PDF-":
        raise SystemExit(f"Renderer did not produce a PDF at {pdf_path}")


def wiki_revision(wiki_root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(wiki_root), "rev-parse", "--short", "HEAD"],
            check=True, capture_output=True, text=True,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def missing_sources(data: dict, wiki_root: Path) -> list[str]:
    """Wiki-relative sources that do not exist under wiki_root (URLs are skipped)."""
    return [
        src for src in collect_sources(data)
        if "://" not in src and not (wiki_root / src).exists()
    ]


def build(data_path: Path, pdf_path: Path, html_path: Path | None = None,
          wiki_root: Path | None = None, check_sources: bool = False) -> Path:
    data = load(data_path)
    if check_sources:
        if wiki_root is None:
            raise SystemExit("--check-sources needs --wiki-root")
        missing = missing_sources(data, wiki_root)
        if missing:
            raise SystemExit("Sources not found in the wiki:\n  " + "\n  ".join(missing))
    if wiki_root is not None:
        rev = wiki_revision(wiki_root)
        if rev:
            data["wiki_revision"] = rev
    errors = validate(data)
    if errors:
        raise SystemExit("Invalid team summary data:\n  " + "\n  ".join(errors))
    page = render_html(data)
    if html_path is not None:
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(page, encoding="utf-8")
        render_pdf(html_path, pdf_path)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_html = Path(tmp) / "team-summary.html"
            tmp_html.write_text(page, encoding="utf-8")
            render_pdf(tmp_html, pdf_path)
    return pdf_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check-only", action="store_true",
                    help="validate schema (and sources with --check-sources); do not render")
    ap.add_argument("--html", type=Path)
    ap.add_argument("--wiki-root", type=Path)
    ap.add_argument("--check-sources", action="store_true",
                    help="fail when a wiki-relative source does not exist under --wiki-root")
    args = ap.parse_args(argv)
    if args.check_only:
        data = load(args.data)
        problems = validate(data)
        if args.check_sources and args.wiki_root is not None:
            problems += [f"source not found: {s}" for s in missing_sources(data, args.wiki_root)]
        if problems:
            print("\n".join(problems))
            return 1
        print("OK: valid")
        return 0
    if args.out is None:
        ap.error("--out is required unless --check-only")
    pdf = build(args.data, args.out, args.html, args.wiki_root, args.check_sources)
    print(f"OK: {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
