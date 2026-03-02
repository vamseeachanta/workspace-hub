#!/usr/bin/env bash
""":"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"
exec uv run --no-project --with markdown --with PyYAML python "$0" "$@"
":"""
import os
import re
import sys
import yaml
import html as html_lib
from pathlib import Path


def collect_test_evidence(assets_dir: str) -> dict:
    """Collect test artifacts for mandatory HTML Test Evidence section."""
    example_path = Path(assets_dir) / "example-pack.md"
    variation_path = Path(assets_dir) / "variation-test-results.md"

    example_present = example_path.exists()
    variation_present = variation_path.exists()
    summary = "No variation-test summary available."

    if variation_present:
        raw = variation_path.read_text(encoding="utf-8")
        for line in raw.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                summary = line
                break

    return {
        "example_pack_present": example_present,
        "variation_tests_present": variation_present,
        "example_pack_path": str(example_path),
        "variation_tests_path": str(variation_path),
        "variation_summary": summary,
    }


def generate_review(wrk_id, stage="draft", type="plan", output_file=None):
    workspace_root = os.popen("git rev-parse --show-toplevel").read().strip()
    queue_dir = os.path.join(workspace_root, ".claude/work-queue")
    
    # Find WRK file
    wrk_file = ""
    for folder in ["working", "pending", "done", "archived"]:
        path = os.path.join(queue_dir, folder, f"{wrk_id}.md")
        if os.path.exists(path):
            wrk_file = path
            break
    
    if not wrk_file:
        print(f"Error: Could not find {wrk_id}.md")
        return

    with open(wrk_file, 'r') as f:
        content = f.read()
    
    # Split frontmatter and body
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        print("Error: No frontmatter found")
        return
    
    try:
        fm = yaml.safe_load(fm_match.group(1))
    except Exception as e:
        print(f"Error parsing frontmatter: {e}")
        fm = {}

    body = content[fm_match.end():]
    
    # Metadata extraction
    title = fm.get('title', f"{wrk_id} Review")
    status = fm.get('status', 'pending').upper()
    status_class = "approve" if status == "DONE" else "pending"
    orchestrator = fm.get('orchestrator', 'unknown')
    priority = fm.get('priority', 'medium')
    route = fm.get('route', 'B')
    
    # lede extraction (first line of the body if it's not a header)
    lede_lines = [l for l in body.split('\n') if l.strip() and not l.startswith('#')][:1]
    lede = lede_lines[0] if lede_lines else "Review artifact for " + title
    
    # Executive summary extraction
    what_match = re.search(r"## (?:What|Objective)\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
    exec_summary = what_match.group(1).strip() if what_match else "No executive summary found."

    # Fast deterministic rendering for large WRK documents.
    exec_summary_html = f"<pre>{html_lib.escape(exec_summary)}</pre>"
    body_html = f"<pre>{html_lib.escape(body)}</pre>"
    
    # Check for reviewer artifacts
    reviewers = []
    assets_dir = os.path.join(queue_dir, "assets", wrk_id)
    if os.path.exists(assets_dir):
        for r_name in ["Claude", "Codex", "Gemini"]:
            r_path = os.path.join(assets_dir, f"review-{r_name.lower()}.md")
            if os.path.exists(r_path):
                with open(r_path, 'r') as rf:
                    r_content = rf.read()
                    verdict_match = re.search(r"## Verdict\n\s*\**([A-Z_]+)\**", r_content)
                    verdict = verdict_match.group(1) if verdict_match else "PENDING"
                    v_class = "approve" if verdict == "APPROVE" else "no-output" if verdict == "NO_OUTPUT" else "reject"
                    reviewers.append({
                        "name": r_name,
                        "verdict": verdict,
                        "verdict_class": v_class,
                        "note": f"Review artifact present at assets/{wrk_id}/review-{r_name.lower()}.md"
                    })
    test_evidence = collect_test_evidence(assets_dir)

    # Embedded CSS path logic
    css_rel_path = "../../assets/shared/orchestrator.css"

    # Template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{wrk_id} - {type.capitalize()} Review</title>
  <link rel="stylesheet" href="{css_rel_path}">
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <div class="eyebrow">{wrk_id} {type.capitalize()} Artifact</div>
      <h1>{title}</h1>
      <p class="lede">{lede}</p>
      <div class="meta">
        <div class="pill">Status: <span class="badge badge-{status_class}">{status}</span></div>
        <div class="pill">Route: {route}</div>
        <div class="pill">Priority: {priority}</div>
        <div class="pill">Orchestrator: {orchestrator}</div>
      </div>
    </div>
  </header>

  <main class="container">
    <div class="exec-summary">
      <h2>Executive Summary</h2>
      <div>{exec_summary_html}</div>
    </div>

    <div class="panel">
      {body_html}
    </div>

    <h2>Test Evidence</h2>
    <div class="panel">
      <p><strong>Example Pack:</strong> {"present" if test_evidence["example_pack_present"] else "missing"}</p>
      <p><strong>Variation Tests:</strong> {"present" if test_evidence["variation_tests_present"] else "missing"}</p>
      <p><strong>Example Pack Path:</strong> <code>{test_evidence["example_pack_path"]}</code></p>
      <p><strong>Variation Test Path:</strong> <code>{test_evidence["variation_tests_path"]}</code></p>
      <p><strong>Variation Test Summary:</strong> {test_evidence["variation_summary"]}</p>
    </div>
"""
    if reviewers:
        html += """
    <h2>Reviewer Synthesis</h2>
    <div class="reviewer-grid">
"""
        for r in reviewers:
            html += f"""
      <div class="reviewer-card">
        <span class="reviewer-name">{r['name']}</span>
        <p><strong>Verdict:</strong> <span class="badge badge-{r['verdict_class']}">{r['verdict']}</span></p>
        <p>{r['note']}</p>
      </div>
"""
        html += "    </div>"

    html += f"""
    <div class="action-footer">
      <p><strong>Required Action:</strong> Please provide your sign-off in the terminal.</p>
      <a href="#" class="btn btn-approve">APPROVE</a>
      <a href="#" class="btn btn-reject">REJECT</a>
    </div>
  </main>
</body>
</html>
"""
    
    if not output_file:
        name = f"{type}-review-{stage}.html"
        output_file = os.path.join(workspace_root, "assets", wrk_id, name)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html)
    
    # Internal artifact for validation
    internal_name = "review.html" if type == "plan" else "implementation-review.html"
    internal_path = os.path.join(queue_dir, "assets", wrk_id, internal_name)
    os.makedirs(os.path.dirname(internal_path), exist_ok=True)
    with open(internal_path, 'w') as f:
        f.write(html)

    print(f"✔ Standardized HTML generated: {output_file}")
    print(f"✔ Internal validation artifact: {internal_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("wrk_id")
    parser.add_argument("--stage", default="draft")
    parser.add_argument("--type", default="plan")
    parser.add_argument("--output")
    args = parser.parse_args()
    
    generate_review(args.wrk_id, args.stage, args.type, args.output)
