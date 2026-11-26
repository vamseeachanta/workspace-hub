"""Bounded canonical-record projections; no ingestion, app writes or auto-sync.

Reuse llm-wiki:docs/governance/client-home-design.md. PDF consumes dashboard.html
through the existing digitalmodel.reporting.pdf renderer, outside this adapter.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, urlparse

LIMIT = 262144
PDF_LIMIT = 32 * 1024 * 1024
SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")

def _exact(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("Unexpected or missing fields")

def _text(value, limit=4000):
    if not isinstance(value, str) or len(value) > limit or "\x00" in value:
        raise ValueError("Invalid text")
    return value

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result

def parse_record(text):
    if len(text.encode("utf-8")) > LIMIT:
        raise ValueError("Record exceeds bounded input limit")
    value = json.loads(text, object_pairs_hook=_pairs)
    validate_record(value)
    return value

def _link(link):
    _exact(link, ("label", "url"))
    if not _text(link["label"], 160).strip():
        raise ValueError("Link label is required")
    url = _text(link["url"], 4000)
    parsed = urlparse(url)
    if (any(ord(c) < 33 for c in url) or parsed.scheme not in ("https", "file")
            or parsed.username or parsed.password or not parsed.path
            or (parsed.scheme == "https" and not parsed.hostname)):
        raise ValueError("Unsafe or incomplete link")

def validate_record(data):
    _exact(data, ("schema", "client", "owner_repository", "title", "checked_at",
                  "coverage", "hold", "sections", "common_resources"))
    if type(data["schema"]) is not int or data["schema"] != 1:
        raise ValueError("Unsupported schema")
    if not isinstance(data["client"], str) or not SLUG.fullmatch(data["client"]):
        raise ValueError("Invalid client identity")
    if not isinstance(data["owner_repository"], str) or not REPOSITORY.fullmatch(data["owner_repository"]):
        raise ValueError("Invalid owner repository")
    if not _text(data["title"], 200).strip() or type(data["hold"]) is not bool:
        raise ValueError("Title and explicit hold state are required")
    checked = datetime.fromisoformat(_text(data["checked_at"], 60).replace("Z", "+00:00"))
    if checked.tzinfo is None:
        raise ValueError("Checked time must include timezone")
    if not isinstance(data["coverage"], list) or not 1 <= len(data["coverage"]) <= 12:
        raise ValueError("Explicit bounded coverage is required")
    for line in data["coverage"]:
        if not _text(line).strip():
            raise ValueError("Empty coverage")
    if not isinstance(data["sections"], list) or not 1 <= len(data["sections"]) <= 20:
        raise ValueError("At least one bounded work section is required")
    ids, total = set(), 0
    for section in data["sections"]:
        _exact(section, ("id", "title", "items"))
        ident = section["id"]
        if not isinstance(ident, str) or not SLUG.fullmatch(ident) or ident in ids or ident in ("common-resources", "coverage", "title", "provenance"):
            raise ValueError("Invalid or duplicate section identity")
        ids.add(ident)
        if not _text(section["title"], 200).strip():
            raise ValueError("Empty section title")
        if not isinstance(section["items"], list) or not 1 <= len(section["items"]) <= 50:
            raise ValueError("Empty or oversized section")
        total += len(section["items"])
        for item in section["items"]:
            _exact(item, ("text", "links"))
            if not _text(item["text"]).strip() or not isinstance(item["links"], list) or len(item["links"]) > 5:
                raise ValueError("Invalid work item")
            for link in item["links"]:
                _link(link)
    if total > 100:
        raise ValueError("Work-item limit exceeded")
    _link(data["common_resources"])

def _canonical(data):
    validate_record(data)
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def content_version(data):
    return "sha256:" + hashlib.sha256(_canonical(data)).hexdigest()

def _md(text):
    return re.sub(r"([\\\x60*_{}\[\]()#+!<>|~-])", r"\\\1", text.replace("\n", " "))

def _model(data):
    version = content_version(data)
    blocks = [("title", "title", data["title"], []),
              ("paragraph", "provenance", f"Checked: {data['checked_at']} · Content version: {version}", [])]
    for section in data["sections"]:
        blocks.append(("heading", section["id"], section["title"], []))
        blocks.extend(("bullet", section["id"], item["text"], item["links"]) for item in section["items"])
    blocks.append(("heading", "coverage", "Coverage", []))
    blocks.extend(("bullet", "coverage", text, []) for text in data["coverage"])
    blocks.append(("bullet", "common-resources", "Common engineering resources:", [data["common_resources"]]))
    return blocks

def render(data):
    blocks = _model(data)
    markdown, markup = [], []
    for kind, ident, text, links in blocks:
        mdlinks = " · ".join(f"[{_md(link['label'])}]({quote(link['url'], safe=':/?#@&=+;%~')})" for link in links)
        hlinks = " · ".join(f'<a href="{html.escape(link["url"], quote=True)}">{html.escape(link["label"])}</a>' for link in links)
        mdtext = _md(text) + (" " + mdlinks if links else "")
        htext = html.escape(text).replace("\n", " ") + (" " + hlinks if links else "")
        if kind == "title":
            markdown.append("# " + mdtext)
            markup.append("<h1>" + htext + "</h1>")
        elif kind == "heading":
            markdown.append("## " + mdtext)
            heading_id = ident if ident == "coverage" else f"section-{ident}"
            markup.append(f'<h2 id="{heading_id}">{htext}</h2>')
        elif kind == "bullet":
            markdown.append("- " + mdtext)
            markup.append(f'<div class="bullet">• {htext}</div>')
        else:
            markdown.append(mdtext)
            markup.append('<p class="meta">' + htext + "</p>")
    body = "\n".join(markup)
    options = "".join(f'<option value="{s["id"]}">{html.escape(s["title"])}</option>' for s in data["sections"])
    panel = f"""<section id="review-panel"><h2>Review comments and decisions</h2>
<p>Choose a section, then Save review JSON. Save locally and return it to the private repository workflow. No autosave or sending.</p>
<label>Section <select id="review-section">{options}</select></label>
<label>Comment <textarea id="review-comment" maxlength="4000" rows="3"></textarea></label>
<label>Decision or requested change <textarea id="review-decision" maxlength="800" rows="2"></textarea></label>
<button id="review-save">Save review JSON</button>
<label>Load saved review JSON <input type="file" id="review-load" accept=".json,application/json"></label>
<p id="review-message" role="status" aria-live="polite">Ready. Edits stay in this tab until saved.</p></section>"""
    js = Path(__file__).with_name("home_projection_review.js").read_text(encoding="utf-8")
    binding = json.dumps({"version": content_version(data), "sections": [s["id"] for s in data["sections"]]}).replace("<", "\\u003c")
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(data['title'])}</title><style>
:root{{color-scheme:light dark}}body{{font:14px/1.4 "Segoe UI",Arial,sans-serif;margin:24px auto;max-width:1000px;padding:20px;color:#1c2730;background:#fff}}
h1,h2{{color:#0d2438}}h1{{font-size:26px}}h2{{font-size:17px;margin:14px 0 6px}}a{{color:#0e7c7b}}.meta{{font-size:11px;overflow-wrap:anywhere}}.bullet{{margin:5px 0;padding-left:10px}}
#review-panel{{border:2px solid #0e7c7b;margin-top:20px;padding:15px}}label{{display:block;margin:10px 0}}textarea,select{{display:block;width:100%;font:inherit}}button{{padding:9px;font:inherit}}
@media(prefers-color-scheme:dark){{body{{background:#18212a;color:#edf3f5}}h1,h2{{color:#edf3f5}}a{{color:#8ddbd7}}}}
@page{{size:A4;margin:12mm}}@media print{{:root{{color-scheme:light}}body{{background:white;color:#1c2730;margin:0;padding:0;font-size:9pt;max-width:none}}h1,h2{{color:#0d2438}}h1{{font-size:18pt}}h2{{font-size:11pt}}#review-panel{{display:none}}.bullet{{break-inside:avoid}}}}
</style></head><body><main id="canonical-content">{body}</main>{panel}
<script>const reviewBinding={binding};</script><script>{js}</script></body></html>"""
    return {"space.md": "\n\n".join(markdown) + "\n", "dashboard.html": document,
            "index.html": document, "record.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n"}

def _no_links(path):
    for component in (path, *path.parents):
        if component.is_symlink() or getattr(component, "is_junction", lambda: False)():
            raise ValueError("Symbolic links or junctions are not accepted")

def write_bundle(data, destination, owner=None):
    artifacts = render(data)
    destination = Path(destination)
    _no_links(destination)
    destination.mkdir(parents=False, exist_ok=False)
    hashes = {}
    for name, text in artifacts.items():
        payload = text.encode("utf-8")
        with (destination / name).open("xb") as stream:
            stream.write(payload)
        hashes[name] = hashlib.sha256(payload).hexdigest()
    manifest = {"schema": 1, "content_version": content_version(data), "hold": data["hold"],
                "owner": owner, "artifacts": hashes, "pdf_status": "not_generated"}
    with (destination / "manifest.json").open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    return manifest

def _git(root, *args):
    run = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=15)
    if run.returncode:
        raise ValueError("Owner Git verification failed")
    return run.stdout

def owner_receipt(source, root, data):
    validate_record(data)
    source, root = Path(source).absolute(), Path(root).absolute()
    _no_links(source)
    _no_links(root)
    if Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() != root.resolve():
        raise ValueError("Expected root is not the owning repository")
    try:
        relative = source.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("Canonical record is outside its owner") from exc
    if any(part in (".git", "..") for part in Path(relative).parts) or not source.is_file() or source.stat().st_size > LIMIT:
        raise ValueError("Invalid bounded canonical record path")
    origin = _git(root, "remote", "get-url", "origin").decode().strip()
    if origin.startswith("git@github.com:"):
        repo = origin.removeprefix("git@github.com:").removesuffix(".git")
    else:
        parsed = urlparse(origin)
        if parsed.scheme not in ("https", "ssh") or parsed.hostname != "github.com":
            raise ValueError("Owner origin must be a verified GitHub repository")
        repo = parsed.path.lstrip("/").removesuffix(".git")
    if repo != data["owner_repository"]:
        raise ValueError("Owner repository binding differs")
    commit = _git(root, "rev-parse", "HEAD").decode().strip()
    ref = commit + ":" + relative
    if int(_git(root, "cat-file", "-s", ref)) > LIMIT:
        raise ValueError("Committed record exceeds bounded limit")
    current = source.read_bytes()
    if _git(root, "show", ref) != current or parse_record(current.decode("utf-8")) != data:
        raise ValueError("Canonical record is dirty or differs from selected content")
    if _git(root, "rev-parse", "HEAD").decode().strip() != commit:
        raise ValueError("Owner HEAD changed during verification")
    return {"repository": repo, "commit": commit,
            "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD").decode().strip(),
            "record_path": relative, "disposition": "committed",
            "record_sha256": hashlib.sha256(current).hexdigest()}

def owner_destination(destination, root):
    """Return proposals/generated work to the verified owner, never shared code."""
    destination, root = Path(destination).absolute(), Path(root).absolute()
    _no_links(destination)
    _no_links(root)
    try:
        relative = destination.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("Output must remain inside the verified owner repository") from exc
    if ".git" in relative.parts or not relative.parts:
        raise ValueError("Output cannot be Git metadata or the owner root")
    return destination

def verify_bundle(destination, for_publication=False, owner_root=None):
    destination = Path(destination)
    _no_links(destination)
    manifest_path = destination / "manifest.json"
    _no_links(manifest_path)
    if manifest_path.stat().st_size > LIMIT:
        raise ValueError("Oversized manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    _exact(manifest, ("schema", "content_version", "hold", "owner", "artifacts", "pdf_status"))
    if (type(manifest["schema"]) is not int or manifest["schema"] != 1
            or type(manifest["hold"]) is not bool or not isinstance(manifest["artifacts"], dict)
            or manifest["pdf_status"] != "not_generated"):
        raise ValueError("Invalid manifest")
    if set(manifest["artifacts"]) != {"space.md", "dashboard.html", "index.html", "record.json"}:
        raise ValueError("Incomplete bundle")
    for name, digest in manifest["artifacts"].items():
        path = destination / name
        _no_links(path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Artifact readback mismatch")
    data = parse_record((destination / "record.json").read_text(encoding="utf-8"))
    if manifest["content_version"] != content_version(data) or manifest["hold"] != data["hold"]:
        raise ValueError("Canonical version or hold mismatch")
    expected = render(data)
    if any((destination / name).read_text(encoding="utf-8") != text for name, text in expected.items()):
        raise ValueError("Projections differ from canonical content")
    receipt_path = destination / "pdf-receipt.json"
    pdf_path = destination / "dashboard.pdf"
    _no_links(receipt_path)
    _no_links(pdf_path)
    if receipt_path.exists():
        _check_pdf_file(pdf_path, PDF_LIMIT)
        _check_pdf_file(receipt_path, LIMIT)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
        _exact(receipt, ("content_version", "html_sha256", "pdf_sha256", "pages", "content_checked", "links_checked"))
        if (receipt["content_version"] != manifest["content_version"]
                or receipt["html_sha256"] != manifest["artifacts"]["dashboard.html"]
                or receipt["pdf_sha256"] != hashlib.sha256(pdf_path.read_bytes()).hexdigest()
                or type(receipt["pages"]) is not int or receipt["pages"] < 1
                or receipt["content_checked"] is not True or receipt["links_checked"] is not True):
            raise ValueError("PDF receipt/source mismatch")
        if _pdf_content_receipt(destination, manifest, data, receipt["pages"]) != receipt:
            raise ValueError("PDF content differs from its receipt")
        manifest = {**manifest, "pdf_status": "generated_and_checked", "pdf_receipt": receipt}
    elif for_publication and pdf_path.exists():
        raise ValueError("PDF receipt required for publication")
    if for_publication:
        if data["hold"] or not manifest["owner"] or owner_root is None:
            raise ValueError("Hold or unverified private owner prevents publication acceptance")
        receipt = owner_receipt(Path(owner_root) / manifest["owner"]["record_path"], owner_root, data)
        if receipt != manifest["owner"]:
            raise ValueError("Owner revision changed; regenerate")
    return manifest

def _check_pdf_file(path, limit):
    if not path.is_file() or not 1 <= path.stat().st_size <= limit:
        raise ValueError(f"Expected a nonempty regular file within {limit} bytes: {path.name}")

def _pdf_content_receipt(destination, manifest, data, expected_pages):
    pdf_path = destination / "dashboard.pdf"
    _no_links(pdf_path)
    _check_pdf_file(pdf_path, PDF_LIMIT)
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    if len(reader.pages) != expected_pages:
        raise ValueError("PDF page-count acceptance failed")
    text = "".join("".join((page.extract_text() or "").split()) for page in reader.pages)
    for _, _, line, links in _model(data):
        if "".join(line.split()) not in text:
            raise ValueError("PDF omits canonical content")
        if any("".join(link["label"].split()) not in text for link in links):
            raise ValueError("PDF omits a canonical link label")
    actual_links = {str(annotation.get_object().get("/A", {}).get("/URI", ""))
                    for page in reader.pages for annotation in page.get("/Annots", [])}
    expected_links = {link["url"] for _, _, _, links in _model(data) for link in links}
    if not expected_links.issubset(actual_links):
        raise ValueError("PDF omits or changes canonical hyperlink targets")
    receipt = {"content_version": manifest["content_version"],
               "html_sha256": manifest["artifacts"]["dashboard.html"],
               "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
               "pages": len(reader.pages), "content_checked": True, "links_checked": True}
    return receipt

def record_pdf(destination, expected_pages=1):
    """Verify the actual existing-renderer derivative, then write a new receipt."""
    destination = Path(destination)
    manifest = verify_bundle(destination)
    data = parse_record((destination / "record.json").read_text(encoding="utf-8"))
    receipt = _pdf_content_receipt(destination, manifest, data, expected_pages)
    with (destination / "pdf-receipt.json").open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    return receipt

def feedback_proposal(data, feedback):
    validate_record(data)
    _exact(feedback, ("schema", "content_version", "section_id", "comment", "decision"))
    if type(feedback["schema"]) is not int or feedback["schema"] != 1:
        raise ValueError("Invalid feedback schema")
    if feedback["content_version"] != content_version(data):
        raise ValueError("Stale or mismatched feedback version")
    if feedback["section_id"] not in [s["id"] for s in data["sections"]]:
        raise ValueError("Unknown feedback section")
    _text(feedback["comment"], 4000)
    _text(feedback["decision"], 800)
    if not feedback["comment"].strip() and not feedback["decision"].strip():
        raise ValueError("Empty feedback")
    return {**feedback, "owner_repository": data["owner_repository"], "status": "proposed",
            "canonical_change_applied": False, "hold": data["hold"]}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "feedback"):
        command = sub.add_parser(name)
        command.add_argument("record", type=Path)
        command.add_argument("--owner-root", type=Path, required=True)
        command.add_argument("--out", type=Path, required=True)
        if name == "feedback":
            command.add_argument("feedback_file", type=Path)
    args = parser.parse_args(argv)
    _no_links(args.record)
    if args.record.stat().st_size > LIMIT:
        raise ValueError("Oversized record")
    data = parse_record(args.record.read_text(encoding="utf-8"))
    owner = owner_receipt(args.record, args.owner_root, data)
    args.out = owner_destination(args.out, args.owner_root)
    if args.command == "build":
        write_bundle(data, args.out, owner)
        verify_bundle(args.out)
    else:
        _no_links(args.feedback_file)
        if args.feedback_file.stat().st_size > 16384:
            raise ValueError("Oversized feedback file")
        feedback = json.loads(args.feedback_file.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
        result = feedback_proposal(data, feedback)
        _no_links(args.out)
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"content_version": content_version(data), "output": str(args.out),
                      "owner": owner, "publication_performed": False}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
