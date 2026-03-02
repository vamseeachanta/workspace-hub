#!/usr/bin/env bash
""":"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"
exec uv run --no-project --with markdown --with PyYAML python "$0" "$@"
":"""
import os
import re
import markdown
import sys
import yaml
from pathlib import Path

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
    
    # Executive summary extraction
    what_match = re.search(r"## (?:What|Objective)\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
    exec_summary = what_match.group(1).strip() if what_match else "No executive summary found."
    
    # Convert body to HTML
    body_html = markdown.markdown(body, extensions=['extra', 'codehilite', 'tables'])
    
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

    # Template (embedded for zero-dep simplicity)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{wrk_id} - {type.capitalize()} Review</title>
  <style>
    :root {{ --primary: #0366d6; --success: #28a745; --warning: #f1e05a; --danger: #d73a49; --gray-light: #f6f8fa; --gray-dark: #24292e; --border: #e1e4e8; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 40px; background: var(--gray-light); color: var(--gray-dark); }}
    .card {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 24px; border: 1px solid var(--border); }}
    h1 {{ border-bottom: 2px solid var(--border); padding-bottom: 0.3em; margin-bottom: 20px; }}
    h2 {{ border-bottom: 1px solid var(--border); padding-bottom: 0.3em; margin-top: 32px; color: var(--primary); }}
    .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-weight: bold; color: white; text-transform: uppercase; font-size: 0.8em; vertical-align: middle; }}
    .badge-approve {{ background: var(--success); }} .badge-reject {{ background: var(--danger); }} .badge-no-output {{ background: #6a737d; }} .badge-pending {{ background: var(--warning); color: black; }}
    .exec-summary {{ background: #f1f8ff; border-left: 6px solid var(--primary); padding: 20px; border-radius: 4px; margin-bottom: 30px; }}
    .reviewer-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
    .reviewer-card {{ background: #fff; border: 1px solid var(--border); padding: 16px; border-radius: 6px; }}
    .reviewer-name {{ font-weight: bold; color: #586069; border-bottom: 1px solid #eee; margin-bottom: 10px; display: block; }}
    .action-footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid var(--border); text-align: center; }}
    .btn {{ padding: 10px 24px; border-radius: 6px; font-weight: bold; text-decoration: none; margin: 0 10px; display: inline-block; }}
    .btn-approve {{ background: var(--success); color: white; border: 1px solid #22863a; }} .btn-reject {{ background: white; color: var(--danger); border: 1px solid var(--danger); }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{wrk_id}: {type.capitalize()} Review ({stage.capitalize()}) <span class="badge badge-{status_class}">{status}</span></h1>
    
    <div class="exec-summary">
      <h2>Executive Summary</h2>
      <div>{markdown.markdown(exec_summary)}</div>
    </div>

    <div class="content">
      {body_html}
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
  </div>
</body>
</html>
"""
    
    # Determine output path based on standardized naming
    if not output_file:
        name = f"{type}-review-{stage}.html"
        output_file = os.path.join(workspace_root, "assets", wrk_id, name)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html)
    
    # Also save to internal assets for validation
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
