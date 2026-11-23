# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
#!/usr/bin/env python3
"""generate-skill-evals.py — Auto-generate eval YAML for SKILL.md files.

Reads a SKILL.md, extracts ## headings as required_sections candidates
and command patterns (uv run, bash scripts/, etc.) as required_commands candidates.
Generates eval YAML in the standard schema and writes to .planning/skills/evals/.

Usage:
    uv run --no-project python scripts/skills/generate-skill-evals.py <SKILL.md path>
    uv run --no-project python scripts/skills/generate-skill-evals.py --batch <file-with-paths>
    uv run --no-project python scripts/skills/generate-skill-evals.py --top50

All paths are relative to repo root.
"""
import argparse
import os
import re
import sys
from pathlib import Path

import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Generate eval YAML for skills")
    parser.add_argument("skill_path", nargs="?", help="Path to a single SKILL.md (relative to repo root)")
    parser.add_argument("--batch", help="File containing one SKILL.md path per line")
    parser.add_argument("--top50", action="store_true", help="Auto-discover and generate evals for top 50 skills")
    parser.add_argument("--evals-dir", default=".planning/skills/evals", help="Output directory for eval YAMLs")
    parser.add_argument("--wrk-id", default="WRK-1009", help="Work item ID")
    parser.add_argument("--dry-run", action="store_true", help="Print YAML to stdout instead of writing files")
    return parser.parse_args()


def find_repo_root():
    """Walk up from cwd to find repo root (has .git/)."""
    p = Path.cwd()
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    return Path.cwd()


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter. Returns (meta_dict, body_text)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 4:]
    try:
        meta = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, body


def extract_headings(body: str) -> list[str]:
    """Extract all ## headings from body text."""
    headings = []
    for line in body.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            headings.append(stripped)
    return headings


def extract_commands(body: str) -> list[str]:
    """Extract command patterns from code blocks."""
    commands = []
    # Look for common command patterns
    patterns = [
        r'(uv run\s+[^\\\n]+)',
        r'(bash\s+scripts/[^\\\n]+)',
        r'(python\s+scripts/[^\\\n]+)',
        r'(/work\s+\w+)',
        r'(/gsd[\w-]*)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, body):
            cmd = match.group(1).strip()
            # Clean up: remove trailing backticks, pipes, backslash continuations
            cmd = cmd.split('|')[0].strip().rstrip('`\\').strip()
            # Skip if the command ends with a backslash (multi-line)
            if cmd and len(cmd) < 120 and cmd not in commands:
                commands.append(cmd)
    return commands


def select_eval_sections(headings: list[str]) -> list[str]:
    """Select the most important headings for eval checks.
    
    We pick up to 5 sections that are most indicative of skill quality.
    Priority: Quick Start, Core Concepts, When to Use, process/procedure headings.
    """
    if not headings:
        return []
    
    # Priority keywords for capability checks
    priority_keywords = [
        "Quick Start", "Core Concepts", "When to Use", "Usage", 
        "Overview", "Purpose", "Process", "Pipeline", "Architecture",
        "Workflow", "Configuration", "Setup", "API", "Commands",
        "Examples", "Implementation", "Reference", "Output",
        "Scheduling", "Integration", "Reusable Scripts",
    ]
    
    selected = []
    remaining = list(headings)
    
    # First pass: pick priority headings
    for keyword in priority_keywords:
        for h in remaining:
            if keyword.lower() in h.lower() and h not in selected:
                selected.append(h)
                remaining.remove(h)
                break
        if len(selected) >= 5:
            break
    
    # If we still need more, take the first remaining ones (up to 5 total)
    for h in remaining:
        if h not in selected and len(selected) < 5:
            selected.append(h)
    
    # Always return at least 1 section if headings exist
    return selected[:5]


def select_eval_commands(commands: list[str]) -> list[str]:
    """Select up to 3 most important commands for eval checks."""
    if not commands:
        return []
    # Prefer uv run commands, then bash scripts/, then others
    prioritized = sorted(commands, key=lambda c: (
        0 if c.startswith("uv run") else
        1 if c.startswith("bash ") else
        2 if c.startswith("python ") else
        3
    ))
    return prioritized[:3]


def make_skill_prefix(skill_name: str) -> str:
    """Generate a short prefix for eval IDs from skill name."""
    # Take first letters of each word, max 4 chars
    parts = skill_name.replace("-", " ").split()
    if len(parts) == 1:
        return parts[0][:4]
    prefix = "".join(p[0] for p in parts[:4])
    return prefix


def generate_eval_yaml(
    skill_path: str,
    repo_root: Path,
    wrk_id: str = "WRK-1009",
) -> tuple[str, dict]:
    """Generate eval YAML dict for a single skill.
    
    Returns (skill_name, yaml_dict).
    """
    full_path = repo_root / skill_path
    if not full_path.exists():
        raise FileNotFoundError(f"SKILL.md not found: {full_path}")
    
    text = full_path.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_frontmatter(text)
    
    # Determine skill name
    skill_name = meta.get("name", full_path.parent.name)
    # Clean skill name  
    skill_name = str(skill_name).strip().strip("'\"")
    
    # Extract candidates
    headings = extract_headings(body)
    commands = extract_commands(body)
    
    # Select for evals
    eval_sections = select_eval_sections(headings)
    eval_commands = select_eval_commands(commands)
    
    # Build prefix for eval IDs
    prefix = make_skill_prefix(skill_name)
    
    # Build evals list
    evals = []
    
    # Capability eval: required sections
    if eval_sections:
        cap_eval = {
            "eval_id": f"{prefix}-cap-01",
            "eval_type": "capability",
            "description": f"Core sections documented for {skill_name}",
            "checks": {
                "required_sections": eval_sections,
            },
        }
        evals.append(cap_eval)
    
    # Procedural eval: required commands (if any found)
    if eval_commands:
        proc_eval = {
            "eval_id": f"{prefix}-proc-01",
            "eval_type": "procedural",
            "description": f"Key commands documented for {skill_name}",
            "checks": {
                "required_commands": eval_commands,
            },
        }
        evals.append(proc_eval)
    
    # If no commands but we have extra sections, create a procedural eval with more sections
    if not eval_commands and len(headings) > len(eval_sections):
        extra_sections = [h for h in headings if h not in eval_sections][:3]
        if extra_sections:
            proc_eval = {
                "eval_id": f"{prefix}-proc-01",
                "eval_type": "procedural",
                "description": f"Additional documentation sections for {skill_name}",
                "checks": {
                    "required_sections": extra_sections,
                },
            }
            evals.append(proc_eval)
    
    # Fallback: if no evals at all, create a minimal one with at least one heading
    if not evals:
        # Use the first heading from the full text
        all_h2 = re.findall(r'^(## .+)$', body, re.MULTILINE)
        if all_h2:
            evals.append({
                "eval_id": f"{prefix}-cap-01",
                "eval_type": "capability",
                "description": f"Minimal documentation check for {skill_name}",
                "checks": {
                    "required_sections": all_h2[:2],
                },
            })
    
    yaml_dict = {
        "version": 1,
        "wrk_id": wrk_id,
        "skill_name": skill_name,
        "skill_path": skill_path,
        "evals": evals,
    }
    
    return skill_name, yaml_dict


# ── Top 50 skill discovery ──────────────────────────────────────────

DOMAIN_WEIGHTS = {
    "workspace-hub": 10,
    "coordination": 10,
    "engineering": 7,
    "_core": 6,
    "operations": 8,
    "_internal": 7,
    "_runtime": 7,
    "development": 6,
    "data": 5,
    "eng": 6,
    "science": 4,
    "digitalmodel": 5,
}

GSD_WEIGHT = 9

ALREADY_HAVE_EVALS = {"workflow-gatepass", "work-queue", "comprehensive-learning"}


def discover_top50(repo_root: Path) -> list[str]:
    """Discover and rank the top 50 skills by importance."""
    skills_dir = repo_root / ".claude" / "skills"
    scored = []
    
    for skill_path in skills_dir.rglob("SKILL.md"):
        if "/_archive/" in str(skill_path):
            continue
        
        rel_path = str(skill_path.relative_to(repo_root))
        skill_name = skill_path.parent.name
        
        # Skip existing evals
        if skill_name in ALREADY_HAVE_EVALS:
            continue
        
        text = skill_path.read_text(encoding="utf-8", errors="replace")
        heading_count = len(re.findall(r'^## ', text, re.MULTILINE))
        
        # Parse frontmatter for scripts
        has_scripts = "scripts:" in text[:2000]
        has_related = "related_skills" in text[:2000]
        
        score = 0
        
        # Domain weight
        parts = rel_path.split("/")
        domain = parts[2] if len(parts) > 2 else ""
        
        if domain.startswith("gsd-"):
            score += GSD_WEIGHT
        
        score += DOMAIN_WEIGHTS.get(domain, 2)
        
        if has_scripts:
            score += 15
        
        if has_related:
            score += 3
        
        score += min(heading_count, 8)
        score += min(len(text) // 1000, 5)
        
        scored.append((score, domain, skill_name, rel_path))
    
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    
    return [item[3] for item in scored[:50]]


def dump_yaml_clean(data: dict) -> str:
    """Dump YAML with clean formatting."""
    return yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )


def main():
    args = parse_args()
    repo_root = find_repo_root()
    evals_dir = repo_root / args.evals_dir
    evals_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which skills to process
    skill_paths = []
    
    if args.top50:
        skill_paths = discover_top50(repo_root)
        print(f"Discovered top 50 skills for eval generation")
    elif args.batch:
        batch_file = Path(args.batch)
        skill_paths = [line.strip() for line in batch_file.read_text().splitlines() if line.strip() and not line.startswith("#")]
    elif args.skill_path:
        skill_paths = [args.skill_path]
    else:
        print("ERROR: provide a skill path, --batch file, or --top50", file=sys.stderr)
        return 1
    
    generated = 0
    errors = 0
    
    for skill_path in skill_paths:
        try:
            skill_name, yaml_dict = generate_eval_yaml(
                skill_path=skill_path,
                repo_root=repo_root,
                wrk_id=args.wrk_id,
            )
            
            if args.dry_run:
                print(f"--- {skill_name} ---")
                print(dump_yaml_clean(yaml_dict))
            else:
                # Use skill_name for filename, sanitized
                safe_name = re.sub(r'[^a-z0-9_-]', '-', skill_name.lower())
                out_path = evals_dir / f"{safe_name}.yaml"
                out_path.write_text(dump_yaml_clean(yaml_dict), encoding="utf-8")
                print(f"  ✓ {safe_name}.yaml ({len(yaml_dict.get('evals', []))} evals)")
            
            generated += 1
            
        except Exception as e:
            print(f"  ✗ {skill_path}: {e}", file=sys.stderr)
            errors += 1
    
    print(f"\nGenerated: {generated} eval files, Errors: {errors}")
    
    if errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
