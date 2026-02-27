#!/usr/bin/env -S uv run --no-project --with markdown python
import os
import re
import markdown
import sys

def generate_review(wrk_id):
    workspace_root = os.popen("git rev-parse --show-toplevel").read().strip()
    queue_dir = os.path.join(workspace_root, ".claude/work-queue")
    
    # Find WRK file
    wrk_file = ""
    # Try working/ folder first as it's likely where the current item is
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
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        print("Error: No frontmatter found")
        return
    
    fm_str = match.group(1)
    body = content[match.end():]
    
    # Simple executive summary extraction (first paragraph of What)
    what_match = re.search(r"## What\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
    exec_summary = what_match.group(1).strip() if what_match else "No executive summary found."
    
    # Convert body to HTML
    body_html = markdown.markdown(body, extensions=['extra', 'codehilite', 'tables'])
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Review: {wrk_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 40px; background: #fafafa; color: #24292e; }}
        .card {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; border: 1px solid #e1e4e8; }}
        h1 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        h2 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; margin-top: 24px; }}
        .exec-summary {{ background: #f1f8ff; padding: 20px; border-left: 6px solid #0366d6; margin-bottom: 30px; border-radius: 4px; }}
        .exec-summary h2 {{ margin-top: 0; border: none; color: #0366d6; }}
        pre {{ background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; border: 1px solid #dfe1e4; }}
        code {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; background: rgba(27,31,35,0.05); padding: 0.2em 0.4em; border-radius: 3px; }}
        pre code {{ background: none; padding: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid #dfe1e8; padding: 12px; text-align: left; }}
        th {{ background-color: #f6f8fa; font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{wrk_id} Review</h1>
        <div class="exec-summary">
            <h2>Executive Summary</h2>
            <div>{markdown.markdown(exec_summary)}</div>
        </div>
        <div class="content">
            {body_html}
        </div>
    </div>
</body>
</html>
"""
    
    output_path = os.path.join(workspace_root, ".claude/work-queue/assets", wrk_id, "review.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
    print(f"✔ HTML review artifact generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_review(sys.argv[1])
    else:
        print("Usage: generate_review.py <WRK-ID>")
