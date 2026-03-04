#!/usr/bin/env bash
""":"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"
exec uv run --no-project --with markdown --with PyYAML python "$0" "$@"
":"""
from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path

import markdown
import yaml


def _split_frontmatter(text: str) -> tuple[dict, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except Exception:
        fm = {}
    body = text[match.end() :]
    return fm, body


def _extract_section(body: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)", re.DOTALL | re.MULTILINE)
    m = pattern.search(body)
    return m.group(1).strip() if m else ""


def _extract_first_section(body: str, headings: list[str]) -> str:
    for heading in headings:
        content = _extract_section(body, heading)
        if content:
            return content
    return ""


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def _html_md(md_text: str) -> str:
    if not md_text:
        return "<p><em>Not available.</em></p>"
    return markdown.markdown(md_text, extensions=["extra", "tables"])


def _collect_asset_files(assets_dir: Path) -> list[str]:
    if not assets_dir.exists():
        return []
    files = []
    for path in sorted(assets_dir.rglob("*")):
        if path.is_file():
            files.append(path.relative_to(assets_dir).as_posix())
    return files


def _discover_work_items(queue_dir: Path) -> list[str]:
    wrk_ids: set[str] = set()
    pattern = re.compile(r"^WRK-[A-Za-z0-9-]+$")
    for path in queue_dir.rglob("WRK-*.md"):
        if path.name == "WRK-TEMPLATE.md":
            continue
        wrk_id = path.stem
        if pattern.match(wrk_id):
            wrk_ids.add(wrk_id)
    return sorted(wrk_ids)


def _resolve_wrk_path(queue_dir: Path, wrk_id: str) -> Path:
    candidates = [
        queue_dir / f"{wrk_id}.md",
        queue_dir / "working" / f"{wrk_id}.md",
        queue_dir / "pending" / f"{wrk_id}.md",
        queue_dir / "done" / f"{wrk_id}.md",
        queue_dir / "blocked" / f"{wrk_id}.md",
        queue_dir / "archive" / f"{wrk_id}.md",
        queue_dir / "archived" / f"{wrk_id}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    nested_candidates = []
    for candidate in queue_dir.rglob(f"{wrk_id}.md"):
        rel_parts = candidate.relative_to(queue_dir).parts
        if "assets" in rel_parts:
            continue
        nested_candidates.append(candidate)
    if nested_candidates:
        nested_candidates.sort()
        return nested_candidates[0]
    raise FileNotFoundError(f"WRK not found: {wrk_id}")


def generate_final_review(wrk_id: str, output: Path) -> Path:
    workspace_root = Path(os.popen("git rev-parse --show-toplevel").read().strip() or ".").resolve()
    queue_dir = workspace_root / ".claude" / "work-queue"
    wrk_path = _resolve_wrk_path(queue_dir, wrk_id)

    fm, body = _split_frontmatter(wrk_path.read_text(encoding="utf-8"))
    assets_dir = queue_dir / "assets" / wrk_id
    evidence_dir = assets_dir / "evidence"

    title = str(fm.get("title") or wrk_id)
    status = str(fm.get("status") or "pending")
    route = str(fm.get("route") or "-")
    orchestrator = str(fm.get("orchestrator") or fm.get("provider") or "unknown")

    what = _extract_first_section(body, ["What", "Prompt", "Problem", "Context"])
    why = _extract_first_section(body, ["Why", "Objective", "Goals"])
    acceptance = _extract_first_section(body, ["Acceptance Criteria", "Success Criteria", "Definition of Done"])
    plan = _extract_first_section(body, ["Plan", "Implementation Plan", "Execution Plan"])
    execution_brief = _extract_first_section(body, ["Execution Brief", "Implementation Notes", "Execution"])

    plan_draft_ref = fm.get("plan_html_review_draft_ref")
    plan_final_ref = fm.get("plan_html_review_final_ref")
    draft_review = _load_text((workspace_root / str(plan_draft_ref))) if plan_draft_ref else _load_text(assets_dir / "plan-html-review-draft.md")
    final_review = _load_text((workspace_root / str(plan_final_ref))) if plan_final_ref else _load_text(assets_dir / "plan-html-review-final.md")

    execute = _load_yaml(evidence_dir / "execute.yaml")
    integrated_tests = execute.get("integrated_repo_tests") if isinstance(execute.get("integrated_repo_tests"), list) else []
    cross_review = _load_text(assets_dir / "cross-review-package.md") or _load_text(assets_dir / "cross-review-agent-synthesis.md")
    gate_summary = _load_text(evidence_dir / "gate-evidence-summary.md")
    resource_pack = _load_text(assets_dir / "resource-pack.md")
    resource_summary = _load_text(assets_dir / "resource-intelligence-summary.md")
    future_work = _load_text(evidence_dir / "future-work.yaml")
    skill_manifest = _load_text(evidence_dir / "skill-manifest.yaml")
    stage_evidence = _load_text(evidence_dir / "stage-evidence.yaml")

    test_rows = ""
    for idx, test in enumerate(integrated_tests, start=1):
        if not isinstance(test, dict):
            continue
        test_rows += (
            "<tr>"
            f"<td>{idx}</td>"
            f"<td>{html.escape(str(test.get('name', '')))}</td>"
            f"<td>{html.escape(str(test.get('scope', '')))}</td>"
            f"<td>{html.escape(str(test.get('result', '')))}</td>"
            f"<td><code>{html.escape(str(test.get('command', '')))}</code></td>"
            f"<td>{html.escape(str(test.get('artifact_ref', '')))}</td>"
            "</tr>"
        )
    if not test_rows:
        test_rows = '<tr><td colspan="6"><em>No integrated/repo tests recorded.</em></td></tr>'

    asset_links = _collect_asset_files(assets_dir)
    links_html = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in asset_links) or "<li><em>No assets found.</em></li>"

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(wrk_id)} - Final Review</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #111; }}
    h1, h2 {{ margin-top: 24px; }}
    .meta {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 8px; margin: 12px 0; }}
    .pill {{ background: #f5f5f5; border: 1px solid #ddd; padding: 8px; border-radius: 8px; }}
    .panel {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-top: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 8px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f5f5f5; }}
    code {{ background: #f3f3f3; padding: 1px 4px; }}
  </style>
</head>
<body>
  <h1>{html.escape(wrk_id)} Final Review</h1>
  <div class="meta">
    <div class="pill"><strong>Title</strong><br>{html.escape(title)}</div>
    <div class="pill"><strong>Status</strong><br>{html.escape(status)}</div>
    <div class="pill"><strong>Route</strong><br>{html.escape(route)}</div>
    <div class="pill"><strong>Orchestrator</strong><br>{html.escape(orchestrator)}</div>
  </div>

  <h2>Prompt Start Context</h2>
  <div class="panel">{_html_md(what or "Not available.")}</div>

  <h2>Why</h2>
  <div class="panel">{_html_md(why or "Not available.")}</div>

  <h2>Acceptance Criteria</h2>
  <div class="panel">{_html_md(acceptance or "Not available.")}</div>

  <h2>Plan</h2>
  <div class="panel">{_html_md(plan or "Not available.")}</div>
  <h3>Plan Review Artifacts</h3>
  <div class="panel">
    <h4>Draft</h4>
    {_html_md(draft_review)}
    <h4>Final</h4>
    {_html_md(final_review)}
  </div>

  <h2>Execution Brief</h2>
  <div class="panel">{_html_md(execution_brief or "Not available.")}</div>

  <h2>Cross-Review Summary</h2>
  <div class="panel">{_html_md(cross_review)}</div>

  <h2>Test Summary</h2>
  <table>
    <thead>
      <tr><th>#</th><th>Name</th><th>Scope</th><th>Result</th><th>Command</th><th>Artifact</th></tr>
    </thead>
    <tbody>
      {test_rows}
    </tbody>
  </table>

  <h2>Gate Evidence Summary</h2>
  <div class="panel">{_html_md(gate_summary)}</div>

  <h2>Resource Intelligence</h2>
  <div class="panel">
    <h4>Resource Summary</h4>
    {_html_md(resource_summary)}
    <h4>Resource Pack</h4>
    {_html_md(resource_pack)}
  </div>

  <h2>Skill Manifest</h2>
  <div class="panel">{_html_md(skill_manifest)}</div>

  <h2>Future Work</h2>
  <div class="panel">{_html_md(future_work)}</div>

  <h2>Stage Evidence Ledger</h2>
  <div class="panel">{_html_md(stage_evidence)}</div>

  <h2>Asset Index</h2>
  <div class="panel"><ul>{links_html}</ul></div>
</body>
</html>
"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_doc, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate comprehensive final HTML review for a WRK item.")
    parser.add_argument("wrk_id", nargs="?", help="Work item id, e.g., WRK-624")
    parser.add_argument("--all", action="store_true", help="Generate final review HTML for all WRK items.")
    parser.add_argument("--output", help="Output HTML path")
    args = parser.parse_args()

    workspace_root = Path(os.popen("git rev-parse --show-toplevel").read().strip() or ".").resolve()
    queue_dir = workspace_root / ".claude" / "work-queue"

    if args.all:
        wrk_ids = _discover_work_items(queue_dir)
        generated = 0
        for wrk_id in wrk_ids:
            out = workspace_root / ".claude" / "work-queue" / "assets" / wrk_id / "workflow-final-review.html"
            try:
                generate_final_review(wrk_id, out)
            except FileNotFoundError:
                continue
            generated += 1
        print(f"✔ Final reviews generated: {generated}")
        return 0

    if not args.wrk_id:
        parser.error("Provide WRK id or --all")

    default_output = workspace_root / ".claude" / "work-queue" / "assets" / args.wrk_id / "workflow-final-review.html"
    output = Path(args.output).resolve() if args.output else default_output
    try:
        path = generate_final_review(args.wrk_id, output)
    except FileNotFoundError as exc:
        print(f"✖ {exc}")
        return 2

    print(f"✔ Final review generated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
