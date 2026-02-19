#!/usr/bin/env python3
"""md-to-pdf: Convert Markdown with YAML frontmatter to styled PDF via Chrome headless."""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"
CHROME_BIN = "/usr/bin/google-chrome"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter between --- delimiters and return (metadata, body)."""
    match = re.match(r"\A---\s*\n(.*?\n)---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text

    raw_yaml = match.group(1)
    body = match.group(2)

    meta = {}
    for line in raw_yaml.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        colon_idx = line.find(":")
        if colon_idx == -1:
            continue
        key = line[:colon_idx].strip()
        value = line[colon_idx + 1:].strip().strip('"').strip("'")
        meta[key] = value

    return meta, body


def convert_md_to_html(body: str) -> str:
    """Convert markdown body to HTML using the markdown library."""
    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "toc",
            "attr_list",
            "meta",
            "sane_lists",
        ]
    )
    return md.convert(body)


def build_cover_page(meta: dict) -> str:
    """Build a cover page div from frontmatter metadata."""
    title = meta.get("title", "Untitled Document")
    subtitle = meta.get("subtitle", "")
    date = meta.get("date", "")
    confidentiality = meta.get("confidentiality", "")
    author = meta.get("author", "")
    version = meta.get("version", "")

    parts = ['<div class="cover-page">', '  <div class="accent-bar"></div>']
    parts.append(f'  <h1 class="cover-title">{_esc(title)}</h1>')

    if subtitle:
        parts.append(f'  <p class="cover-subtitle">{_esc(subtitle)}</p>')

    meta_lines = []
    if date:
        meta_lines.append(f'<span class="label">Date:</span> {_esc(date)}')
    if author:
        meta_lines.append(f'<span class="label">Author:</span> {_esc(author)}')
    if version:
        meta_lines.append(f'<span class="label">Version:</span> {_esc(version)}')

    if meta_lines:
        parts.append('  <div class="cover-meta">')
        for line in meta_lines:
            parts.append(f"    <div>{line}</div>")
        parts.append("  </div>")

    if confidentiality:
        parts.append(
            f'  <div class="confidentiality">{_esc(confidentiality)}</div>'
        )

    parts.append("</div>")
    return "\n".join(parts)


def _esc(text: str) -> str:
    """Minimal HTML escaping for metadata values."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def inject_into_template(
    cover_html: str,
    body_html: str,
    meta: dict,
    template_name: str = "base",
) -> str:
    """Load the HTML template and inject cover, body, CSS, and metadata."""
    template_path = TEMPLATES_DIR / f"{template_name}.html"
    css_path = TEMPLATES_DIR / "components.css"

    template = template_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")

    title = meta.get("title", "Document")
    accent = meta.get("accent_color", "#0066cc")
    footer = meta.get("footer", "")

    html = template
    html = html.replace("{{CSS}}", css)
    html = html.replace("{{COVER}}", cover_html)
    html = html.replace("{{BODY}}", body_html)
    html = html.replace("{{TITLE}}", _esc(title))
    html = html.replace("{{ACCENT_COLOR}}", accent)
    html = html.replace("{{FOOTER_TEXT}}", _esc(footer))

    return html


def screenshot(html_path: str, png_path: str) -> None:
    """Generate a screenshot PNG via Chrome headless."""
    cmd = [
        CHROME_BIN,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        f"--screenshot={png_path}",
        "--window-size=1200,1600",
        f"file://{html_path}",
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Screenshot: {png_path}")


def generate_pdf(html_path: str, pdf_path: str) -> None:
    """Generate a PDF via Chrome headless --print-to-pdf."""
    cmd = [
        CHROME_BIN,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        "--print-background",
        f"file://{html_path}",
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"PDF: {pdf_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to styled PDF via Chrome headless"
    )
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("-o", "--output", help="Output PDF path (default: <input>.pdf)")
    parser.add_argument(
        "--screenshot", action="store_true", help="Also generate a PNG screenshot"
    )
    parser.add_argument(
        "--no-cover", action="store_true", help="Skip cover page generation"
    )
    parser.add_argument(
        "--keep-html", action="store_true", help="Keep intermediate HTML file"
    )
    parser.add_argument(
        "--template",
        default="base",
        help="Template name from templates/ (default: base)",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    body_html = convert_md_to_html(body)

    cover_html = "" if args.no_cover else build_cover_page(meta)

    full_html = inject_into_template(cover_html, body_html, meta, args.template)

    # Determine output paths
    output_pdf = Path(args.output) if args.output else input_path.with_suffix(".pdf")
    output_pdf = output_pdf.resolve()

    # Write intermediate HTML
    if args.keep_html:
        html_path = str(output_pdf.with_suffix(".html"))
    else:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".html", delete=False, dir=str(output_pdf.parent)
        )
        html_path = tmp.name
        tmp.close()

    Path(html_path).write_text(full_html, encoding="utf-8")

    if args.keep_html:
        print(f"HTML: {html_path}")

    try:
        generate_pdf(html_path, str(output_pdf))

        if args.screenshot:
            png_path = str(output_pdf.with_suffix(".png"))
            screenshot(html_path, png_path)
    finally:
        if not args.keep_html:
            os.unlink(html_path)


if __name__ == "__main__":
    main()
