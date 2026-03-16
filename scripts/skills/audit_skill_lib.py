#!/usr/bin/env python3
"""Shared library for audit-skills.py — parsing, checks, and formatters."""

from __future__ import annotations

import io
import re
from pathlib import Path

import yaml

HTML_WHITELIST = {
    "details", "summary", "br", "hr", "sub", "sup", "kbd", "img", "a", "em",
    "strong", "code", "pre", "p", "ul", "ol", "li", "table", "tr", "td", "th",
    "thead", "tbody", "div", "span", "b", "i", "h1", "h2", "h3", "h4", "h5",
    "h6", "blockquote", "dl", "dt", "dd", "head", "body", "html", "meta",
    "style", "script", "header", "footer", "main", "section", "nav", "aside",
    "article", "figure", "figcaption", "button", "input", "form", "label",
    "select", "option", "textarea", "svg", "path", "canvas", "video", "audio",
    "source", "link", "title",
}

EXEC_PATTERN = re.compile(r"(bash scripts/|uv run|bash \.claude/skills/)")
TAG_RE = re.compile(
    r"<[a-zA-Z][a-zA-Z0-9_:-]*(?:\s[^>]*)?>|</[a-zA-Z][a-zA-Z0-9_:-]*>"
)
TAG_NAME_RE = re.compile(r"</?([a-zA-Z][a-zA-Z0-9_:-]*)")
PLACEHOLDER_RE = re.compile(r"^[a-z][a-z0-9_-]*$")


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter and return (meta, body)."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return None, content
    end = stripped.find("---", 3)
    if end == -1:
        return None, content
    raw = stripped[3:end].strip()
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, content
    if not isinstance(meta, dict):
        return None, content
    return meta, stripped[end + 3:]


def strip_code_blocks(text: str) -> str:
    return re.sub(r"```[^`]*```", "", text, flags=re.DOTALL)


def _count_non_whitelisted_tags(body: str) -> int:
    body_clean = strip_code_blocks(body)
    count = 0
    for tag in TAG_RE.findall(body_clean):
        m = TAG_NAME_RE.match(tag)
        if not m:
            continue
        name = m.group(1)
        if name.lower() in HTML_WHITELIST:
            continue
        if PLACEHOLDER_RE.match(name) and len(name) <= 20:
            continue
        count += 1
    return count


def _append_violation(violations: list[dict], path: str, check: str, detail: str) -> None:
    violations.append({"file": path, "check": check, "severity": "warn", "detail": detail})


def run_violations_audit(skill_dir: Path) -> list[dict]:
    """Check all SKILL.md files for structural violations."""
    violations: list[dict] = []
    for skill_file in sorted(skill_dir.rglob("SKILL.md")):
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_frontmatter(content)
        p = str(skill_file)
        if (skill_file.parent / "README.md").exists():
            _append_violation(violations, p, "readme_present",
                              "README.md found in skill dir (v2 anti-pattern)")
        wc = len(content.split())
        if wc > 5000:
            _append_violation(violations, p, "word_count_exceeded",
                              f"SKILL.md has {wc} words (limit: 5000)")
        if meta:
            desc_len = len(str(meta.get("description", "")))
            if desc_len > 1024:
                _append_violation(violations, p, "description_too_long",
                                  f"description field is {desc_len} chars (limit: 1024)")
        tag_count = _count_non_whitelisted_tags(body)
        if tag_count > 0:
            _append_violation(violations, p, "xml_html_tags_in_body",
                              f"{tag_count} XML/HTML tag(s) found in SKILL.md body")
    return violations


def run_coverage_audit(skill_dir: Path) -> list[dict]:
    """Check all SKILL.md files for script-wiring gaps."""
    gaps: list[dict] = []
    for skill_file in sorted(skill_dir.rglob("SKILL.md")):
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        meta, _ = parse_frontmatter(content)
        if meta and meta.get("scripts_exempt") is True:
            continue
        has_fm = (meta and isinstance(meta.get("scripts"), list)
                  and len(meta["scripts"]) > 0)
        has_body = bool(EXEC_PATTERN.search(content))
        if not has_fm and not has_body:
            gaps.append({
                "path": str(skill_file), "has_script_ref": False,
                "gaps": ["no_frontmatter_scripts", "no_exec_pattern"],
            })
    return gaps


def format_violations_yaml(violations: list[dict]) -> str:
    if not violations:
        return "violations: []\n"
    buf = io.StringIO()
    buf.write("violations:\n")
    for v in violations:
        buf.write(f"  - file: {v['file']}\n    check: {v['check']}\n")
        buf.write(f"    severity: {v['severity']}\n    detail: \"{v['detail']}\"\n")
    return buf.getvalue()


def format_coverage_yaml(gaps: list[dict]) -> str:
    if not gaps:
        return ""
    buf = io.StringIO()
    buf.write("skills:\n")
    for g in gaps:
        buf.write(f"  - path: {g['path']}\n    has_script_ref: false\n    gaps:\n")
        for gap in g["gaps"]:
            buf.write(f"      - {gap}\n")
    buf.write(f"gaps_total: {len(gaps)}\n")
    return buf.getvalue()


def format_all_yaml(violations: list[dict], gaps: list[dict]) -> str:
    data = {
        "violations": violations or [],
        "coverage": {"skills": gaps, "gaps_total": len(gaps)},
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False, width=120)
