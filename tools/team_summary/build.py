"""Build the client team summary: YAML facts -> HTML -> PDF (workspace-hub#3967)."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote
import yaml
HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "team-summary.schema.json"
SECTION_ORDER = ["learn_or_solve", "priorities", "issues", "decisions", "areas", "deliverables", "sources"]
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
AREA_TITLES = {"marketing": "Marketing and business development", "technical": "Technical and engineering", "data": "Data and analytics", "projects": "Projects and delivery"}
STATUS_LABELS = {"open": "Open", "investigating": "Investigating", "awaiting-review": "Awaiting review", "resolved": "Resolved"}
ASK_LABELS = {"input": "Input needed", "approval": "Approval needed", "conclusion": "Conclusion needed", "comments": "Comments requested"}
HTML_REVIEW_INSTRUCTION = "Open in Edge or Chrome from disk, select text, click Comment, then Save comments."
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
def review_records(data: dict) -> list[dict]:
    """Review document requests in display order, with duplicates removed."""
    seen, records = set(), []
    def add(items, owner_key="owner"):
        for item in items or []:
            review = item.get("review") or {}
            if not review:
                continue
            key = (review["doc"], review["ask"])
            if key in seen:
                continue
            seen.add(key)
            records.append({"review": review, "owner": item.get(owner_key, "")})
    add(data.get("priorities"))
    add(data.get("issues"))
    add(data.get("blockers"))
    for key in AREA_ORDER:
        add((data.get("areas") or {}).get(key))
    add(data.get("deliverables"), owner_key="")
    return records
def is_html_doc(path: str) -> bool:
    return Path(path).suffix.lower() in {".html", ".htm"}
def review_target(data: dict, doc: str) -> str:
    settings = data.get("review") or {}
    if is_html_doc(doc) and settings.get("copies_dir"):
        stem = Path(doc).stem
        return str(Path(settings["copies_dir"]) / f"{stem}-review.html").replace("\\", "/")
    return doc
def review_label(review: dict, target: str) -> str:
    if review.get("title"):
        return review["title"]
    path = Path(target)
    parent = path.parent.name
    return f"{parent}/{path.name}" if parent else path.name
def quote_url(value: str) -> str:
    return quote(value.replace("\\", "/"), safe="/:#?&=@[]!$&'()*+,;-%")
def review_link_or_path(data: dict, review: dict) -> str:
    doc = review["doc"]
    target = review_target(data, doc)
    label = review_label(review, target)
    base = (data.get("review") or {}).get("link_base")
    link_style = (data.get("review") or {}).get("link_style", "path")
    suffix = ""
    if link_style == "folder":
        suffix = f" (file {escape(Path(target).name)} in the shared folder)"
    if not base:
        return f"{escape(label)}{suffix}"
    if link_style == "folder":
        href = quote_url(base)
    else:
        target_path = target.lstrip("/").replace("\\", "/")
        href = f"{quote_url(base.rstrip('/'))}/{quote(target_path, safe='/')}"
    return f'<a href="{escape(href, quote=True)}">{escape(label)}</a>{suffix}'
def response_text(data: dict, review: dict) -> str:
    doc = review["doc"]
    target = review_target(data, doc)
    if not is_html_doc(doc):
        return "Record the response in the linked document."
    link_style = (data.get("review") or {}).get("link_style", "path")
    if link_style == "folder":
        instruction = (
            f"Download {Path(target).name} from the shared folder, open it in Edge or Chrome "
            "from disk, select text, click Comment, then Save comments."
        )
    else:
        instruction = HTML_REVIEW_INSTRUCTION
    parts = [instruction]
    ret = (data.get("review") or {}).get("return_to")
    if ret:
        parts.append(ret)
    return " ".join(parts)
def review_line(data: dict, item: dict) -> str:
    review = item.get("review")
    if not review:
        return ""
    return (
        '<div class="review-line">'
        f"{escape(ASK_LABELS[review['ask']])}: {review_link_or_path(data, review)}"
        f"{' ' + escape(response_text(data, review)) if is_html_doc(review['doc']) else ''}"
        "</div>"
    )
CSS = """
@page{size:Letter;margin:16mm 16mm 18mm}:root{--ink:#1c2a33;--muted:#5a6a74;--rule:#cfd8dd;--band:#0f4c5c;--soft:#eef3f5;--open:#9a3b2f;--inv:#8a5a00;--rev:#2d5d8a;--res:#2f6b3a}*{box-sizing:border-box}
body{margin:0;color:var(--ink);font:10.5pt/1.45 "Segoe UI","Liberation Sans",Arial,sans-serif}header{background:var(--band);color:#fff;padding:14px 18px;display:flex;justify-content:space-between;align-items:flex-end;gap:16px}header h1{margin:0;font-size:20pt;font-weight:600;letter-spacing:.01em}header .kind{font-size:9pt;text-transform:uppercase;letter-spacing:.12em;opacity:.85}header .meta{text-align:right;font-size:9pt;opacity:.9}
section{margin-top:14px;break-inside:avoid-page}h2{font-size:12pt;margin:0 0 6px;padding-bottom:3px;border-bottom:1.5px solid var(--band);color:var(--band)}h3{font-size:10.5pt;margin:8px 0 3px}p{margin:0}.lead{background:var(--soft);padding:8px 12px;border-left:3px solid var(--band);font-size:11pt}
table{width:100%;border-collapse:collapse;font-size:9.5pt}th{text-align:left;font-weight:600;color:var(--muted);font-size:8pt;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid var(--rule);padding:4px 6px}td{border-bottom:1px solid var(--rule);padding:5px 6px;vertical-align:top}a{color:var(--band);text-decoration:underline}tr{break-inside:avoid}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}.chip{display:inline-block;padding:0 6px;border:1px solid currentColor;border-radius:9px;font-size:8pt;font-weight:600;white-space:nowrap}.s-open{color:var(--open)}.s-investigating{color:var(--inv)}.s-awaiting-review{color:var(--rev)}.s-resolved{color:var(--res)}.review-line{margin-top:3px;color:var(--muted)}
ul{margin:2px 0 0;padding-left:16px}li{margin:2px 0}sup.ref{font-size:7pt;color:var(--muted)}.empty{color:var(--muted);font-style:italic}ol.sources{font-size:8.5pt;color:var(--muted);padding-left:20px;margin:0}ol.sources li{word-break:break-all}footer{margin-top:16px;font-size:8pt;color:var(--muted);border-top:1px solid var(--rule);padding-top:6px}@media print{a{color:var(--ink);text-decoration:underline}}
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
                f"<td>{e(p['next_action'])}{review_line(data, p)}</td>"
                f"<td class=\"num\">{e(p['due'])}</td></tr>"
            )
        out.append("</table>")
    else:
        out.append("<p class=\"empty\">No priorities recorded.</p>")
    out.append("</section>")
    records = review_records(data)
    if records:
        out.append("<section><h2>Documents awaiting your input</h2>")
        out.append("<table><tr><th>Document</th><th>Asked</th><th>Owner</th><th>How to respond</th></tr>")
        for rec in records:
            review = rec["review"]
            out.append(
                f"<tr><td>{review_link_or_path(data, review)}</td>"
                f"<td>{e(ASK_LABELS[review['ask']])}</td><td>{e(rec['owner'])}</td>"
                f"<td>{e(response_text(data, review))}</td></tr>"
            )
        out.append("</table></section>")
    out.append(f"<section><h2>{SECTION_TITLES['issues']}</h2>")
    if data.get("issues"):
        out.append("<table><tr><th>Issue</th><th>Status</th><th>Owner</th><th>Next action</th></tr>")
        for i in data["issues"]:
            status = i["status"]
            out.append(
                f"<tr><td>{e(i['title'])}{ref(i)}</td>"
                f"<td><span class=\"chip s-{e(status)}\">{e(STATUS_LABELS[status])}</span></td>"
                f"<td>{e(i['owner'])}</td><td>{e(i['next_action'])}{review_line(data, i)}</td></tr>"
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
                out.append(
                    f"<li>{e(b['text'])} <em>Owner: {e(b['owner'])}</em>{ref(b)}"
                    f"{review_line(data, b)}</li>"
                )
            out.append("</ul>")
        out.append("</section>")
    areas = data.get("areas") or {}
    present = [k for k in AREA_ORDER if areas.get(k)]
    if present:
        out.append(f"<section><h2>{SECTION_TITLES['areas']}</h2>")
        for key in present:
            out.append(f"<h3>{AREA_TITLES[key]}</h3><ul>")
            for item in areas[key]:
                out.append(f"<li>{e(item['text'])}{ref(item)}{review_line(data, item)}</li>")
            out.append("</ul>")
        out.append("</section>")
    if data.get("deliverables"):
        out.append(f"<section><h2>{SECTION_TITLES['deliverables']}</h2>")
        out.append("<table><tr><th>Deliverable</th><th>Version</th><th>Status</th></tr>")
        for d in data["deliverables"]:
            out.append(
                f"<tr><td>{e(d['name'])}{ref(d)}</td><td class=\"num\">{e(d['version'])}</td>"
                f"<td>{e(d['status'])}{review_line(data, d)}</td></tr>"
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
def review_docs(data: dict) -> list[str]:
    seen = []
    for rec in review_records(data):
        doc = rec["review"]["doc"]
        if doc not in seen:
            seen.append(doc)
    return seen
def missing_sources(data: dict, wiki_root: Path) -> list[str]:
    """Wiki-relative sources and review docs missing under wiki_root; URLs are skipped."""
    paths = collect_sources(data) + [d for d in review_docs(data) if d not in collect_sources(data)]
    return [src for src in paths if "://" not in src and not (wiki_root / src).exists()]
def client_slug(data: dict) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", data["client"].lower()).strip("-")
    return slug or "client"
def make_review_copies(data: dict, wiki_root: Path) -> list[Path]:
    settings = data.get("review") or {}
    copies_dir = settings.get("copies_dir")
    html_docs = [doc for doc in review_docs(data) if is_html_doc(doc)]
    if not html_docs:
        return []
    if not copies_dir:
        raise SystemExit("--make-review-copies needs review.copies_dir in summary.yml")
    made = []
    out_dir = wiki_root / copies_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    for doc in html_docs:
        src = wiki_root / doc
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        out = wiki_root / review_target(data, doc)
        if out.exists() and digest[:12] in out.read_text(encoding="utf-8", errors="ignore"):
            made.append(out)
            continue
        key = f"{client_slug(data)}-{Path(doc).stem}-{digest[:12]}"
        tool = HERE.parent / "html-review" / "make_review_copy.py"
        subprocess.run([sys.executable, str(tool), str(src), str(out), key], check=True)
        made.append(out)
    return made
def publish_review_requests(data: dict, wiki_root: Path, publish_dir: Path) -> list[Path]:
    settings = data.get("review") or {}
    link_style = settings.get("link_style", "path")
    requests: list[tuple[str, str]] = []
    for rec in review_records(data):
        doc = rec["review"]["doc"]
        target = review_target(data, doc)
        requests.append((doc, target))
    if link_style == "folder":
        seen: dict[str, str] = {}
        for doc, target in requests:
            name = Path(target).name
            previous = seen.get(name)
            if previous and previous != doc:
                raise SystemExit(
                    f"publish file-name collision for {name}: {previous} and {doc}"
                )
            seen[name] = doc
    published: list[Path] = []
    for _doc, target in requests:
        rel = Path(target)
        src = wiki_root / rel
        if not src.is_file():
            raise SystemExit(f"Review file to publish not found: {target}")
        dest = publish_dir / (Path(rel.name) if link_style == "folder" else rel)
        if dest.suffix.lower() == ".json":
            raise SystemExit(f"Refusing to overwrite review comments JSON: {dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() == src.read_bytes():
            continue
        shutil.copy2(src, dest)
        print(f"published review file: {dest}")
        published.append(dest)
    return published
def build(data_path: Path, pdf_path: Path, html_path: Path | None = None,
          wiki_root: Path | None = None, check_sources: bool = False,
          make_copies: bool = False, publish_dir: Path | None = None) -> Path:
    data = load(data_path)
    errors = validate(data)
    if errors:
        raise SystemExit("Invalid team summary data:\n  " + "\n  ".join(errors))
    if check_sources:
        if wiki_root is None:
            raise SystemExit("--check-sources needs --wiki-root")
        missing = missing_sources(data, wiki_root)
        if missing:
            raise SystemExit("Sources not found in the wiki:\n  " + "\n  ".join(missing))
    if make_copies:
        if wiki_root is None:
            raise SystemExit("--make-review-copies needs --wiki-root")
        make_review_copies(data, wiki_root)
    if publish_dir is not None:
        if wiki_root is None:
            raise SystemExit("--publish-dir needs --wiki-root")
        publish_review_requests(data, wiki_root, publish_dir)
    if wiki_root is not None:
        rev = wiki_revision(wiki_root)
        if rev:
            data["wiki_revision"] = rev
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
    ap.add_argument("--make-review-copies", action="store_true",
                    help="create HTML review copies for reviewed HTML documents")
    ap.add_argument("--publish-dir", type=Path,
                    help="copy linked review files into this publication directory")
    args = ap.parse_args(argv)
    if args.check_only:
        data = load(args.data)
        problems = validate(data)
        if args.check_sources:
            if args.wiki_root is None:
                problems.append("--check-sources needs --wiki-root")
            else:
                problems += [f"source not found: {s}" for s in missing_sources(data, args.wiki_root)]
        if args.make_review_copies and not problems:
            if args.wiki_root is None:
                problems.append("--make-review-copies needs --wiki-root")
            else:
                make_review_copies(data, args.wiki_root)
        if args.publish_dir is not None and not problems:
            if args.wiki_root is None:
                problems.append("--publish-dir needs --wiki-root")
            else:
                publish_review_requests(data, args.wiki_root, args.publish_dir)
        if problems:
            print("\n".join(problems))
            return 1
        print("OK: valid")
        return 0
    if args.out is None:
        ap.error("--out is required unless --check-only")
    pdf = build(args.data, args.out, args.html, args.wiki_root, args.check_sources,
                args.make_review_copies, args.publish_dir)
    print(f"OK: {pdf}")
    return 0
if __name__ == "__main__":
    sys.exit(main())
