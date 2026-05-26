#!/usr/bin/env python3
"""Render a #2798 completeness record to an HTML artifact.

Output goes to ``docs/reports/<date>-<issue>-completeness.html`` per the repo's
HTML-artifact convention. The HTML embeds the EXACT persisted record as a
```completeness {json}``` block (the same marker the gate reads), so the
human-facing artifact can never drift from the score that gates closure.

All dynamic values are HTML-escaped.
"""
from __future__ import annotations

import datetime as _dt
import html
import json
import sys
from pathlib import Path

_CSS = """
body{margin:0;background:#0f1419;color:#e6edf3;font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:920px;margin:0 auto;padding:30px 20px}
h1{font-size:23px} .muted{color:#9aa7b2;font-size:13px}
.big{font-size:42px;font-weight:800}
.pass{color:#3fb950}.fail{color:#f85149}
table{width:100%;border-collapse:collapse;margin:14px 0}
td,th{border:1px solid #2d3742;padding:8px 10px;text-align:left}
code,pre{background:#0b0f14;border:1px solid #2d3742;border-radius:5px;padding:2px 6px;
 font:12.5px ui-monospace,Menlo,monospace;color:#c9d6e0}
pre{padding:12px;overflow-x:auto;white-space:pre-wrap}
"""


def render_html(result: dict, issue: int, title: str) -> str:
    pct = result.get("completeness_pct", 0)
    threshold = result.get("threshold", 0)
    passed = bool(result.get("passed", pct >= threshold))
    cls = result.get("cls", "?")
    verdict = "PASS" if passed else "FAIL — BLOCKED"
    vclass = "pass" if passed else "fail"
    rows = "".join(
        f"<tr><td>{html.escape(str(e))}</td></tr>" for e in result.get("evidence", [])
    )
    # Escape "<" as the JSON unicode escape so an evidence string can never break
    # out of HTML context (e.g. "</script>"/"<script>"); still valid + round-trippable JSON.
    record_json = json.dumps(result, sort_keys=False).replace("<", "\\u003c")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Completeness — #{int(issue)} {html.escape(title)}</title>
<style>{_CSS}</style></head><body><div class="wrap">
<h1>Completeness — #{int(issue)}: {html.escape(title)}</h1>
<div class="muted">class: {html.escape(cls)} · threshold: {int(threshold)} · generated {_dt.date.today().isoformat()}</div>
<p class="big {vclass}">{int(pct)}% — <span class="{vclass}">{verdict}</span></p>
<h2>Evidence</h2>
<table><thead><tr><th>Item</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Authoritative record (gate-read)</h2>
<pre>```completeness {record_json}```</pre>
<div class="muted">This block is the exact record persisted to the issue + kanban; the close gate reads it.</div>
</div></body></html>
"""


def write_html(result: dict, issue: int, title: str, repo_root: Path | None = None) -> Path:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    out = repo_root / "docs" / "reports" / f"{_dt.date.today().isoformat()}-{issue}-completeness.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(result, issue, title), encoding="utf-8")
    return out


if __name__ == "__main__":
    # Usage: render_completeness_html.py <issue> <title> < result.json
    rec = json.load(sys.stdin)
    path = write_html(rec, int(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "")
    print(path)
