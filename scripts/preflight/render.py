"""Renderers and artifact writers for Hermes preflight reports."""

from __future__ import annotations

import json
from pathlib import Path
import re


def render_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_markdown(report: dict) -> str:
    target = report["target"]
    summary = report["summary"]
    lines = [
        f"# Hermes Preflight — {target['name']}",
        "",
        f"- Run: `{report['run_ts']}`",
        f"- From: `{report['from_host']}`",
        f"- Target: `{target['hostname']}` (`{target['role']}`)",
        f"- Workspace: `{target['workspace_root']}`",
        f"- Summary: pass={summary['pass']} warn={summary['warn']} block={summary['block']}",
        f"- Machine ready: `{str(summary['machine_ready']).lower()}`",
        f"- GitHub mutation allowed: `{str(summary['github_mutation_allowed']).lower()}`",
        "",
        "| Status | Check | Blocks | Detail |",
        "|---|---|---|---|",
    ]
    for check in report["checks"]:
        blocks = ", ".join(check.get("blocks") or []) or "-"
        detail = str(check.get("detail") or "").replace("|", "\\|")
        lines.append(f"| {check['status']} | `{check['name']}` | {blocks} | {detail} |")
    lines.append("")
    return "\n".join(lines)


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "target"


def write_artifacts(report: dict, artifacts_dir: str | Path) -> dict[str, Path]:
    out_dir = Path(artifacts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{report['run_ts'].replace(':', '').replace('-', '')}-{_safe_slug(report['target']['name'])}-hermes-preflight"
    json_path = out_dir / f"{stem}.json"
    markdown_path = out_dir / f"{stem}.md"
    json_path.write_text(render_json(report), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}

