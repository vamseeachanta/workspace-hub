#!/usr/bin/env python3
"""Generate GitHub Issue body from WRK frontmatter + evidence, create/update/close via gh.

Usage: update-github-issue.py WRK-NNN [--create|--update|--close] [--dry-run]
"""
import argparse, re, subprocess, sys
from pathlib import Path

try:
    import yaml
    def _load_yaml(text): return yaml.safe_load(text) or {}
except ImportError:
    def _load_yaml(text):
        d = {}
        for m in re.finditer(r'^(\w[\w_]*):\s*(.+)$', text, re.MULTILINE):
            d[m.group(1)] = m.group(2).strip().strip('"').strip("'")
        return d

def _repo_root_default():
    try:
        return Path(subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip())
    except Exception: return Path.cwd()

def find_wrk_file(wrk_id, root):
    fname = f"{wrk_id}.md"
    for d in ("pending", "working", "done"):
        p = root / ".claude/work-queue" / d / fname
        if p.exists(): return p
    arc = root / ".claude/work-queue/archive"
    if arc.exists():
        for sub in sorted(arc.iterdir()):
            if (sub / fname).exists(): return sub / fname
    return None

def parse_frontmatter(wrk_path):
    text = wrk_path.read_text()
    m = re.match(r'^---\n(.*?)\n---\n?(.*)', text, re.DOTALL)
    if not m: return {}, text
    return _load_yaml(m.group(1)), m.group(2)

def extract_acceptance_criteria(wrk_id, root):
    wrk = find_wrk_file(wrk_id, root)
    if not wrk: return []
    _, body = parse_frontmatter(wrk)
    return [ln.strip() for ln in body.splitlines() if re.match(r'\s*- \[[ x]\]', ln)]

def _extract_sections(wrk_id, root, headings=("Mission", "What", "Why")):
    """Extract named ## sections from the WRK body markdown.

    If none of the priority headings match, falls back to all ## sections
    found in the body (preserving their original order).
    """
    wrk = find_wrk_file(wrk_id, root)
    if not wrk: return ""
    _, body = parse_frontmatter(wrk)
    ordered_keys = []
    sections = {}
    current, buf = None, []
    for line in body.splitlines():
        m = re.match(r'^##\s+(.+)$', line)
        if m:
            if current: sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
            ordered_keys.append(current)
        elif current is not None:
            buf.append(line)
    if current: sections[current] = "\n".join(buf).strip()
    # Try priority headings first; fall back to all sections
    keys = [h for h in headings if h in sections and sections[h]]
    if not keys:
        keys = [k for k in ordered_keys if k in sections and sections[k]]
    parts = []
    for h in keys:
        parts.append(f"### {h}\n\n{sections[h]}")
    return "\n\n".join(parts)

def _read_yaml(path):
    return _load_yaml(path.read_text()) if path.exists() else {}

def _detail(title, content):
    return f"<details><summary>{title}</summary>\n\n{content}\n\n</details>"

def _render_impl(edir):
    p = edir / "execute.yaml"
    if not p.exists(): return "Not yet available"
    raw, lines = p.read_text(), []
    for m in re.finditer(r'-\s+path:\s*(.+)\n\s+description:\s*["\']?(.+?)["\']?\s*$', raw, re.MULTILINE):
        lines.append(f"- `{m.group(1).strip()}` — {m.group(2).strip()}")
    if lines: lines.insert(0, "**Deliverables:**")
    data = _load_yaml(raw)
    tr = data.get("test_results")
    if isinstance(tr, dict):
        lines.append(f"\n**Tests:** Passed: {tr.get('passed','?')}, Failed: {tr.get('failed','?')}")
    elif not tr:
        pm, fm = re.search(r'passed:\s*(\d+)', raw), re.search(r'failed:\s*(\d+)', raw)
        if pm: lines.append(f"\n**Tests:** Passed: {pm.group(1)}" + (f", Failed: {fm.group(1)}" if fm else ""))
    return "\n".join(lines) if lines else "Not yet available"

def _render_tdd(edir):
    p = edir / "tdd.yaml"
    if not p.exists(): return "Not yet available"
    raw, data = p.read_text(), _load_yaml(p.read_text())
    lines = [f"**Approach:** {data.get('approach','TDD')} | **Results:** {data.get('tests_passed','?')}/{data.get('tests_total','?')} passed"]
    acs = [f"- [{'x' if m.group(2)=='pass' else ' '}] {m.group(1)}"
           for m in re.finditer(r'-\s+ac:\s*["\']?(.+?)["\']?\s*\n\s+result:\s*(\w+)', raw, re.MULTILINE)]
    if acs: lines.extend(["\n**AC Results:**"] + acs)
    return "\n".join(lines)

def _render_stages(edir):
    p = edir / "stage-evidence.yaml"
    if not p.exists(): return "Not yet available"
    raw = p.read_text()
    lines = []
    for m in re.finditer(
        r'-\s+order:\s*(\d+)\n\s+stage:\s*(.+)\n\s+status:\s*(\w+)'
        r'(?:\n\s+evidence:\s*["\']?(.*?)["\']?)?'
        r'(?:\n\s+comment:\s*["\']?(.*?)["\']?)?',
        raw, re.MULTILINE,
    ):
        order, name, status = m.group(1), m.group(2).strip(), m.group(3).strip()
        detail = (m.group(5) or m.group(4) or status).strip() or status
        check = "x" if status == "done" else " "
        lines.append(f"- [{check}] **{order}. {name}** — {detail}")
    return "\n".join(lines) if lines else "Not yet available"

def _render_cost(edir):
    parts = []
    cost = _read_yaml(edir / "cost-summary.yaml")
    if cost: parts.append(f"**Estimated cost:** ${cost.get('estimated_cost_usd','N/A')}")
    if (edir / "future-work.yaml").exists(): parts.append("**Future work:** see evidence file")
    return "\n".join(parts) if parts else "Not yet available"

def _render_plan(fm, root):
    ref = fm.get("spec_ref", "")
    if ref and (root / ref).exists(): return (root / ref).read_text().strip()
    return "Not yet available"

def _current_stage(edir):
    """Derive current stage from stage-evidence.yaml (first non-done stage)."""
    p = edir / "stage-evidence.yaml"
    if not p.exists(): return None
    raw = p.read_text()
    for m in re.finditer(
        r'-\s+order:\s*(\d+)\n\s+stage:\s*(.+)\n\s+status:\s*(\w+)', raw, re.MULTILINE
    ):
        status = m.group(3).strip()
        if status != "done":
            return f"Stage {m.group(1)}: {m.group(2).strip()} ({status})"
    return "All stages done"


def render_body(wrk_id, root):
    wrk = find_wrk_file(wrk_id, root)
    if not wrk: return f"WRK file not found for {wrk_id}"
    fm, _ = parse_frontmatter(wrk)
    cat = fm.get("category", "")
    sub = fm.get("subcategory", "")
    edir = root / ".claude/work-queue/assets" / wrk_id / "evidence"
    acs = extract_acceptance_criteria(wrk_id, root)
    stage_info = _current_stage(edir)
    status_str = stage_info if stage_info else fm.get('status', 'unknown')
    return "\n\n".join([
        f"## {wrk_id}: {fm.get('title', wrk_id)}", "",
        f"**Status:** {status_str} | **Priority:** {fm.get('priority','unset')} | **Category:** {cat}" + (f" | **Subcategory:** {sub}" if sub else ""),
        f"**Repo:** {fm.get('target_repos','workspace-hub')} | **Complexity:** {fm.get('complexity','unset')} | **Machine:** {fm.get('computer','unset')}",
        "", "---", "",
        _extract_sections(wrk_id, root),
        "", "---", "",
        _detail("Implementation Summary", _render_impl(edir)),
        _detail("Final Plan", _render_plan(fm, root)),
        _detail("Acceptance Criteria", "\n".join(acs) if acs else "Not yet available"),
        _detail("TDD Results", _render_tdd(edir)),
        _detail("Evidence and Cost", _render_cost(edir)),
        _detail("Stage Progress", _render_stages(edir)),
    ])

def generate_labels(wrk_id, root):
    wrk = find_wrk_file(wrk_id, root)
    if not wrk: return ["enhancement"]
    fm, _ = parse_frontmatter(wrk)
    labels = ["enhancement"]
    if fm.get("priority"): labels.append(f"priority:{fm['priority']}")
    if fm.get("category"): labels.append(f"cat:{fm['category']}")
    return labels

def _store_issue_ref(wrk_path, url):
    text = wrk_path.read_text()
    if re.search(r'^github_issue_ref:', text, re.MULTILINE):
        text = re.sub(r'^github_issue_ref:.*$', f'github_issue_ref: {url}', text, count=1, flags=re.MULTILINE)
    else:
        text = re.sub(r'\n---\n', f'\ngithub_issue_ref: {url}\n---\n', text, count=1)
    wrk_path.write_text(text)

def _gh_run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr); sys.exit(1)
    return r

def _get_issue_number(fm):
    """Extract issue number from github_issue_ref in frontmatter."""
    ref = fm.get("github_issue_ref", "")
    if not ref:
        print("No github_issue_ref in frontmatter", file=sys.stderr); sys.exit(1)
    return ref.rstrip("/").split("/")[-1]


def main(argv=None, repo_root=None):
    pa = argparse.ArgumentParser(description=__doc__)
    pa.add_argument("wrk_id")
    g = pa.add_mutually_exclusive_group(required=True)
    g.add_argument("--create", action="store_true")
    g.add_argument("--update", action="store_true")
    g.add_argument("--close", action="store_true")
    g.add_argument("--comment", type=str, help="Post a comment on the issue")
    g.add_argument("--read-comments", action="store_true", help="Read issue comments as JSON")
    pa.add_argument("--dry-run", action="store_true")
    pa.add_argument("--repo", type=str, default=None, help="GitHub repo (owner/name) for gh commands")
    args = pa.parse_args(argv)
    root = Path(repo_root) if repo_root else _repo_root_default()
    wrk = find_wrk_file(args.wrk_id, root)
    fm, _ = parse_frontmatter(wrk) if wrk else ({}, "")

    # Build --repo flag if specified, or infer from github_issue_ref
    repo_flag = []
    if args.repo:
        repo_flag = ["--repo", args.repo]
    elif fm.get("github_issue_ref"):
        import urllib.parse
        ref = fm["github_issue_ref"].rstrip("/")
        parts = ref.replace("https://github.com/", "").split("/")
        if len(parts) >= 3:
            repo_flag = ["--repo", f"{parts[0]}/{parts[1]}"]

    if args.comment:
        num = _get_issue_number(fm)
        if args.dry_run: print(f"Would comment on #{num}: {args.comment}"); return
        _gh_run(["gh", "issue", "comment", num, "--body", args.comment] + repo_flag)
        print(f"Commented on #{num}")
        return

    if args.read_comments:
        num = _get_issue_number(fm)
        r = _gh_run(["gh", "issue", "view", num, "--comments", "--json", "comments"] + repo_flag)
        print(r.stdout)
        return

    body = render_body(args.wrk_id, root)
    if args.dry_run: print(body); return
    lbl = []
    for lb in generate_labels(args.wrk_id, root): lbl.extend(["--label", lb])
    if args.create:
        r = _gh_run(["gh", "issue", "create", "--title",
                      f"{args.wrk_id}: {fm.get('title', args.wrk_id)}", "--body", body] + lbl + repo_flag)
        url = r.stdout.strip(); print(f"Created: {url}")
        if wrk: _store_issue_ref(wrk, url)
    elif args.update:
        num = _get_issue_number(fm)
        _gh_run(["gh", "issue", "edit", num, "--body", body] + repo_flag)
        print(f"Updated: {fm.get('github_issue_ref', '')}")
    elif args.close:
        num = _get_issue_number(fm)
        _gh_run(["gh", "issue", "close", num] + repo_flag)
        print(f"Closed: {fm.get('github_issue_ref', '')}")

if __name__ == "__main__":
    main()
