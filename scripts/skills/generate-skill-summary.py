#!/usr/bin/env python3
"""Generate or verify full skills summary markdown + html from .claude/skills."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from pathlib import Path


def _extract_indexes(readme_text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(
        r"^\|\s*\[(?P<label>[^\]]+)\]\((?P<link>[^)]+)\)\s*\|\s*(?P<summary>[^|]+)\|",
        re.MULTILINE,
    )
    for match in pattern.finditer(readme_text):
        rows.append(
            {
                "label": match.group("label").strip(),
                "link": match.group("link").strip(),
                "summary": match.group("summary").strip(),
            }
        )
    return rows


def _extract_frontmatter_description(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    if end == -1:
        return ""
    frontmatter = text[4:end]
    match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip().strip('"').strip("'")


def _extract_objective(text: str) -> str:
    lines = text.splitlines()
    # Prefer first blockquote text.
    for raw in lines:
        s = raw.strip()
        if s.startswith(">"):
            return s.lstrip(">").strip()
    # Otherwise first regular line that is not structural markdown.
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith(("---", "#", "|", "<!--", "```", "- ", "* ")):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*", s):
            continue
        return s
    return "No objective text found."


def _scope_for(path_rel: str) -> str:
    if path_rel.startswith("_archive/"):
        return "archive"
    if path_rel.startswith("_diverged/"):
        return "diverged"
    return "active"


def _build_rows(skills_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for skill_path in sorted(skills_root.rglob("SKILL.md")):
        rel = skill_path.relative_to(skills_root).as_posix()
        text = skill_path.read_text(encoding="utf-8", errors="replace")
        description = _extract_frontmatter_description(text)
        objective = _extract_objective(text)
        skill_name = skill_path.parent.name
        rows.append(
            {
                "skill": skill_name,
                "path": rel,
                "scope": _scope_for(rel),
                "summary": description or "No description in frontmatter.",
                "objective": objective,
            }
        )
    return rows


def _render_md(
    rows: list[dict[str, str]],
    indexes: list[dict[str, str]],
    generated_at: str,
) -> str:
    active = sum(1 for r in rows if r["scope"] == "active")
    archive = sum(1 for r in rows if r["scope"] == "archive")
    diverged = sum(1 for r in rows if r["scope"] == "diverged")
    lines = [
        "# Skills Summary",
        "",
        f"Generated: {generated_at}",
        "",
        "> AUTO-GENERATED. Do not edit manually.",
        "> Sync command: `uv run --no-project python scripts/skills/generate-skill-summary.py`",
        "",
        "## Totals",
        "",
        f"- Total skills: **{len(rows)}**",
        f"- Active: **{active}**",
        f"- Archive: **{archive}**",
        f"- Diverged: **{diverged}**",
        "",
        "## Skill Summary",
        "",
        "| # | Skill | Scope | Path | Summary | Objective |",
        "|---|---|---|---|---|---|",
    ]
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | [{row['skill']}]({row['path']}) | {row['scope']} | "
            f"[{row['path']}]({row['path']}) | {row['summary']} | {row['objective']} |"
        )
    lines.extend(["", "## Key Source Indexes Used", ""])
    for idx in indexes:
        lines.append(f"- [{idx['label']}]({idx['link']})")
    lines.append("")
    return "\n".join(lines)


def _render_html(rows: list[dict[str, str]], generated_at: str, md_ref: str) -> str:
    body_rows = []
    for idx, row in enumerate(rows, start=1):
        body_rows.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td><a href=\"{html.escape(row['path'])}\">{html.escape(row['skill'])}</a></td>"
            f"<td>{html.escape(row['scope'])}</td>"
            f"<td><a href=\"{html.escape(row['path'])}\">{html.escape(row['path'])}</a></td>"
            f"<td>{html.escape(row['summary'])}</td>"
            f"<td>{html.escape(row['objective'])}</td>"
            "</tr>"
        )
    rows_html = "\n".join(body_rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skills Summary</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #111; }}
    h1, h2 {{ margin: 0 0 12px; }}
    p {{ margin: 8px 0; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
    th {{ background: #f5f5f5; text-align: left; }}
    code {{ background: #f2f2f2; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>Skills Summary</h1>
  <p><strong>Generated:</strong> {html.escape(generated_at)}</p>
  <p><strong>Sync rule:</strong> regenerate from markdown source with
  <code>uv run --no-project python scripts/skills/generate-skill-summary.py</code>.</p>
  <p><strong>Markdown source:</strong> <a href="{html.escape(md_ref)}">{html.escape(md_ref)}</a></p>
  <table>
    <thead>
      <tr><th>#</th><th>Skill</th><th>Scope</th><th>Path</th><th>Summary</th><th>Objective</th></tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
</body>
</html>
"""


def _normalize_for_compare(text: str, *, html_mode: bool) -> str:
    if html_mode:
        return re.sub(
            r"(<strong>Generated:</strong>) [^<]+",
            r"\1 <normalized>",
            text,
        )
    return re.sub(r"^Generated: .+$", "Generated: <normalized>", text, flags=re.MULTILINE)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate or verify .claude/skills/SKILLS_SUMMARY.md and "
            ".claude/skills/SKILLS_SUMMARY.html"
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify generated outputs are in sync (non-zero exit on drift).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    root = Path(__file__).resolve().parents[2]
    skills_root = root / ".claude" / "skills"
    readme_path = skills_root / "README.md"
    if not readme_path.exists():
        raise FileNotFoundError(f"Missing: {readme_path}")

    indexes = _extract_indexes(readme_path.read_text(encoding="utf-8", errors="replace"))
    rows = _build_rows(skills_root)
    generated_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    md_out = skills_root / "SKILLS_SUMMARY.md"
    html_out = skills_root / "SKILLS_SUMMARY.html"
    md_content = _render_md(rows, indexes, generated_at)
    html_content = _render_html(rows, generated_at, "SKILLS_SUMMARY.md")

    if args.check:
        if not md_out.exists() or not html_out.exists():
            print("Missing generated files. Run generator without --check.", file=sys.stderr)
            return 1
        current_md = md_out.read_text(encoding="utf-8", errors="replace")
        current_html = html_out.read_text(encoding="utf-8", errors="replace")
        if _normalize_for_compare(md_content, html_mode=False) != _normalize_for_compare(
            current_md, html_mode=False
        ) or _normalize_for_compare(html_content, html_mode=True) != _normalize_for_compare(
            current_html, html_mode=True
        ):
            print(
                "Skills summary is out of sync. Regenerate with:\n"
                "  uv run --no-project python scripts/skills/generate-skill-summary.py",
                file=sys.stderr,
            )
            return 1
        print("Skills summary is in sync.")
        return 0

    md_out.write_text(md_content, encoding="utf-8")
    html_out.write_text(html_content, encoding="utf-8")
    print(f"Wrote {md_out}")
    print(f"Wrote {html_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
