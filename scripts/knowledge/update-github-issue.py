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
    lines = [f"- [{'x' if m.group(3).strip()=='done' else ' '}] **{m.group(1)}. {m.group(2).strip()}** — {m.group(4).strip()}"
             for m in re.finditer(r'-\s+order:\s*(\d+)\n\s+stage:\s*(.+)\n\s+status:\s*(\w+)\n(?:\s+.*\n)*?\s+comment:\s*["\']?(.+?)["\']?\s*$', p.read_text(), re.MULTILINE)]
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

def render_body(wrk_id, root):
    wrk = find_wrk_file(wrk_id, root)
    if not wrk: return f"WRK file not found for {wrk_id}"
    fm, _ = parse_frontmatter(wrk)
    cat = fm.get("category", "")
    sub = fm.get("subcategory", "")
    edir = root / ".claude/work-queue/assets" / wrk_id / "evidence"
    acs = extract_acceptance_criteria(wrk_id, root)
    return "\n\n".join([
        f"## {wrk_id}: {fm.get('title', wrk_id)}", "",
        f"**Status:** {fm.get('status','unknown')} | **Priority:** {fm.get('priority','unset')} | **Category:** {f'{cat}/{sub}' if sub else cat}",
        f"**Repo:** {fm.get('target_repos','workspace-hub')} | **Complexity:** {fm.get('complexity','unset')} | **Machine:** {fm.get('computer','unset')}",
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
    wrk_path.write_text(re.sub(r'\n---\n', f'\ngithub_issue_ref: {url}\n---\n', text, count=1))

def _gh_run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr); sys.exit(1)
    return r

def main(argv=None, repo_root=None):
    pa = argparse.ArgumentParser(description=__doc__)
    pa.add_argument("wrk_id")
    g = pa.add_mutually_exclusive_group(required=True)
    g.add_argument("--create", action="store_true")
    g.add_argument("--update", action="store_true")
    g.add_argument("--close", action="store_true")
    pa.add_argument("--dry-run", action="store_true")
    args = pa.parse_args(argv)
    root = Path(repo_root) if repo_root else _repo_root_default()
    body = render_body(args.wrk_id, root)
    if args.dry_run: print(body); return
    wrk = find_wrk_file(args.wrk_id, root)
    fm, _ = parse_frontmatter(wrk) if wrk else ({}, "")
    lbl = []
    for lb in generate_labels(args.wrk_id, root): lbl.extend(["--label", lb])
    if args.create:
        r = _gh_run(["gh", "issue", "create", "--title",
                      f"{args.wrk_id}: {fm.get('title', args.wrk_id)}", "--body", body] + lbl)
        url = r.stdout.strip(); print(f"Created: {url}")
        if wrk: _store_issue_ref(wrk, url)
    elif args.update:
        ref = fm.get("github_issue_ref", "")
        if not ref: print("No github_issue_ref in frontmatter", file=sys.stderr); sys.exit(1)
        _gh_run(["gh", "issue", "edit", ref.rstrip("/").split("/")[-1], "--body", body])
        print(f"Updated: {ref}")
    elif args.close:
        ref = fm.get("github_issue_ref", "")
        if not ref: print("No github_issue_ref in frontmatter", file=sys.stderr); sys.exit(1)
        _gh_run(["gh", "issue", "close", ref.rstrip("/").split("/")[-1]])
        print(f"Closed: {ref}")

if __name__ == "__main__":
    main()
