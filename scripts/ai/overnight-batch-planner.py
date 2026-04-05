#!/usr/bin/env python3
"""Overnight Batch Planner — builds a multi-terminal execution plan for tagged GitHub issues.

Reads open GitHub issues that carry overnight-execution labels, matches each to the
optimal AI agent, and generates a git-contention-safe terminal assignment map with
self-contained prompts for unattended overnight runs.

Usage:
  uv run scripts/ai/overnight-batch-planner.py
  uv run scripts/ai/overnight-batch-planner.py --dry-run
  uv run scripts/ai/overnight-batch-planner.py --repo owner/repo --terminals 3
  uv run scripts/ai/overnight-batch-planner.py --output-file plan.json

Label conventions:
  agent:claude   — route to Claude
  agent:codex    — route to Codex CLI
  agent:gemini   — route to Gemini (via Copilot pool)
  agent:hermes   — route to Hermes
  overnight      — mark issue for overnight execution
  overnight-batch — same as overnight

Output: structured JSON plan with terminal assignments, file ownership, and prompts.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Dependency bootstrap — works with uv run
# ---------------------------------------------------------------------------
try:
    import yaml
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT     = Path(__file__).resolve().parents[2]
ROUTING_CONFIG = REPO_ROOT / "config" / "agents" / "routing-config.yaml"
PROVIDER_CAPS  = REPO_ROOT / "config" / "agents" / "provider-capabilities.yaml"

NUM_TERMINALS = 3

# ---------------------------------------------------------------------------
# Label → agent mapping
# ---------------------------------------------------------------------------
LABEL_AGENT_MAP: dict[str, str] = {
    "agent:claude":  "claude",
    "agent:codex":   "codex",
    "agent:gemini":  "gemini",
    "agent:hermes":  "hermes",
}

OVERNIGHT_LABELS = {"overnight", "overnight-batch", "batch"}

AGENT_MODEL_MAP: dict[str, dict[str, str]] = {
    "claude":  {"model": "claude-opus-4-6",       "provider": "anthropic"},
    "codex":   {"model": "codex-cli",              "provider": "openai-codex"},
    "gemini":  {"model": "gemini-2.5-pro",         "provider": "copilot"},
    "hermes":  {"model": "claude-sonnet-4.6",      "provider": "copilot"},
}

AGENT_COMMAND: dict[str, str] = {
    "claude":  "claude",
    "codex":   "codex",
    "gemini":  "hermes --provider copilot --model gemini-2.5-pro",
    "hermes":  "hermes",
}

# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


# ---------------------------------------------------------------------------
# GitHub issue fetcher
# ---------------------------------------------------------------------------

def fetch_overnight_issues(repo: str | None, dry_run: bool) -> list[dict]:
    """Fetch open GitHub issues tagged for overnight execution via gh CLI."""
    if dry_run:
        # Return synthetic issues for testing/preview without needing gh auth
        return _synthetic_issues()

    gh_args = [
        "gh", "issue", "list",
        "--state", "open",
        "--label", "overnight",
        "--json", "number,title,labels,body,assignees",
        "--limit", "50",
    ]
    if repo:
        gh_args += ["--repo", repo]

    try:
        result = subprocess.run(gh_args, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            # Try overnight-batch label as fallback
            gh_args_b = gh_args[:]
            gh_args_b[gh_args_b.index("overnight")] = "overnight-batch"
            result = subprocess.run(gh_args_b, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"[warn] gh CLI failed: {result.stderr.strip()}", file=sys.stderr)
            print("[warn] Falling back to dry-run synthetic issues.", file=sys.stderr)
            return _synthetic_issues()

        issues = json.loads(result.stdout or "[]")
        if not issues:
            print("[info] No overnight-labelled issues found; using synthetic set for demo.", file=sys.stderr)
            return _synthetic_issues()
        return issues

    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"[warn] gh CLI unavailable ({exc}); using synthetic dry-run data.", file=sys.stderr)
        return _synthetic_issues()


def _synthetic_issues() -> list[dict]:
    """Synthetic issue set for dry-run / offline testing."""
    return [
        {
            "number": 1801,
            "title": "Generate skills inventory report from all sub-repos",
            "labels": [{"name": "agent:hermes"}, {"name": "overnight"}, {"name": "docs"}],
            "body": "Walk all .claude/skills directories and produce a consolidated Markdown report.",
            "assignees": [],
        },
        {
            "number": 1823,
            "title": "Refactor authentication module with full test coverage",
            "labels": [{"name": "agent:claude"}, {"name": "overnight"}, {"name": "refactor"}],
            "body": "Rewrite auth.py to use JWT; add pytest suite with >=90% coverage.",
            "assignees": [],
        },
        {
            "number": 1834,
            "title": "Cross-review all open PRs against coding standards",
            "labels": [{"name": "agent:codex"}, {"name": "overnight"}, {"name": "review"}],
            "body": "Run Codex cross-review gate on PRs #45 #46 #47 and output verdict JSON.",
            "assignees": [],
        },
        {
            "number": 1845,
            "title": "Analyze worldenergydata CSV exports and produce trend report",
            "labels": [{"name": "agent:gemini"}, {"name": "overnight"}, {"name": "data-analysis"}],
            "body": "Load the 2026 CSV exports, run trend analysis, export charts + summary PDF.",
            "assignees": [],
        },
        {
            "number": 1852,
            "title": "Update all README files with latest API changes",
            "labels": [{"name": "agent:hermes"}, {"name": "overnight"}, {"name": "docs"}],
            "body": "Scan each sub-repo README and patch it to reflect the new v3 API surface.",
            "assignees": [],
        },
        {
            "number": 1855,
            "title": "Write integration tests for the new routing gate",
            "labels": [{"name": "agent:codex"}, {"name": "overnight"}, {"name": "testing"}],
            "body": "Add pytest integration tests for review_routing_gate.py covering all trigger paths.",
            "assignees": [],
        },
    ]


# ---------------------------------------------------------------------------
# Issue → agent resolution
# ---------------------------------------------------------------------------

def resolve_agent(issue: dict) -> str:
    """Pick the best agent for an issue based on its labels."""
    label_names = {lbl["name"] for lbl in issue.get("labels", [])}

    # Explicit agent label wins
    for lbl, agent in LABEL_AGENT_MAP.items():
        if lbl in label_names:
            return agent

    # Heuristic fallback from title/body keywords
    text = (issue.get("title", "") + " " + (issue.get("body") or "")).lower()
    if any(kw in text for kw in ["pdf", "csv", "data", "report", "skill", "doc", "readme"]):
        return "hermes"
    if any(kw in text for kw in ["test", "refactor", "cleanup", "implement", "fix"]):
        return "codex"
    if any(kw in text for kw in ["architecture", "design", "complex", "review"]):
        return "claude"
    return "claude"  # safe default


# ---------------------------------------------------------------------------
# File ownership / git contention avoidance
# ---------------------------------------------------------------------------

def infer_file_scope(issue: dict) -> list[str]:
    """Heuristically derive which files/dirs an issue is likely to touch."""
    text = (issue.get("title", "") + " " + (issue.get("body") or "")).lower()
    scopes = []
    if any(kw in text for kw in ["readme", "doc", "report", "skill"]):
        scopes.append("docs/")
        scopes.append(".claude/skills/")
    if any(kw in text for kw in ["auth", "authentication"]):
        scopes.append("src/auth/")
    if any(kw in text for kw in ["routing", "route", "gate"]):
        scopes.append("scripts/ai/")
        scopes.append("config/agents/")
    if any(kw in text for kw in ["csv", "data", "analysis", "chart", "trend"]):
        scopes.append("worldenergydata/")
        scopes.append("data/")
    if any(kw in text for kw in ["test", "pytest", "coverage"]):
        scopes.append("tests/")
    if not scopes:
        scopes.append("(repo root)")
    return scopes


def check_scope_conflict(scope_a: list[str], scope_b: list[str]) -> bool:
    """Return True if two scope lists share overlapping paths."""
    return bool(set(scope_a) & set(scope_b))


def assign_terminals(
    issues_with_agents: list[dict],
    num_terminals: int,
) -> list[list[dict]]:
    """
    Distribute issues across terminals minimising git contention.

    Strategy:
    - Group same-agent issues together when possible (they share context / credentials).
    - Avoid putting two issues with overlapping file scopes in the same terminal.
    - Round-robin across terminals as tiebreaker.
    """
    terminals: list[list[dict]] = [[] for _ in range(num_terminals)]
    terminal_scopes: list[list[str]] = [[] for _ in range(num_terminals)]

    # Sort: group by agent first so same-agent issues cluster
    issues_sorted = sorted(issues_with_agents, key=lambda x: x["agent"])

    for issue in issues_sorted:
        scope = issue["file_scope"]
        # Find best terminal: prefer same agent, no scope conflict, least loaded
        best_t = None
        best_score = -1
        for t_idx, t_issues in enumerate(terminals):
            conflict = check_scope_conflict(scope, terminal_scopes[t_idx])
            if conflict:
                continue  # skip — would cause git contention
            # Score: same-agent bonus + inverse load
            agent_match = sum(1 for i in t_issues if i["agent"] == issue["agent"])
            load_penalty = len(t_issues)
            score = agent_match * 2 - load_penalty
            if score > best_score:
                best_score = score
                best_t = t_idx

        if best_t is None:
            # All terminals have a conflict — pick least-loaded regardless
            best_t = min(range(num_terminals), key=lambda i: len(terminals[i]))

        terminals[best_t].append(issue)
        terminal_scopes[best_t].extend(scope)

    return terminals


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

def build_prompt(issue: dict) -> str:
    """Build a self-contained prompt for the assigned agent."""
    agent  = issue["agent"]
    num    = issue["number"]
    title  = issue["title"]
    body   = (issue.get("body") or "").strip()
    scopes = ", ".join(issue["file_scope"])
    model_info = AGENT_MODEL_MAP.get(agent, {})

    prompt = (
        f"# Overnight Task — Issue #{num}: {title}\n\n"
        f"**Agent**: {agent}  |  **Model**: {model_info.get('model', 'auto')}\n\n"
        f"## Objective\n{body or title}\n\n"
        f"## Scope\nFocus changes in: {scopes}\n\n"
        f"## Instructions\n"
        f"1. Implement the objective fully and autonomously.\n"
        f"2. Commit your changes with a conventional commit message referencing #{num}.\n"
        f"3. Run any relevant tests and fix failures before committing.\n"
        f"4. Append a brief summary of changes to /tmp/overnight-log-{num}.txt\n"
        f"5. Do NOT open PRs automatically — leave a draft diff summary instead.\n"
    )
    return prompt


def build_terminal_command(issue: dict) -> str:
    """Build the shell command to launch the agent for this issue."""
    agent   = issue["agent"]
    cmd_base = AGENT_COMMAND.get(agent, agent)
    prompt   = issue["prompt"].replace('"', '\\"').replace('\n', '\\n')
    num      = issue["number"]
    return (
        f'# Issue #{num}\n'
        f'{cmd_base} -e "{prompt}"'
    )


# ---------------------------------------------------------------------------
# Plan assembly
# ---------------------------------------------------------------------------

def assemble_plan(
    terminals: list[list[dict]],
    routing_cfg: dict,
    repo: str | None,
    dry_run: bool,
) -> dict:
    terminal_plans = []
    for t_idx, issues in enumerate(terminals):
        agents_in_terminal = sorted({i["agent"] for i in issues})
        issue_entries = []
        for issue in issues:
            issue_entries.append({
                "issue_number": issue["number"],
                "title": issue["title"],
                "agent": issue["agent"],
                "model": AGENT_MODEL_MAP.get(issue["agent"], {}).get("model", "auto"),
                "provider": AGENT_MODEL_MAP.get(issue["agent"], {}).get("provider", "auto"),
                "file_scope": issue["file_scope"],
                "prompt": issue["prompt"],
                "launch_command": issue["launch_command"],
            })
        terminal_plans.append({
            "terminal": t_idx + 1,
            "label": f"Terminal {t_idx + 1}",
            "agents": agents_in_terminal,
            "issue_count": len(issues),
            "file_ownership": sorted({s for i in issues for s in i["file_scope"]}),
            "issues": issue_entries,
        })

    total_issues = sum(len(t) for t in terminals)

    return {
        "plan_version": "1.0.0",
        "generated_by": "overnight-batch-planner.py",
        "repo": repo or "(current)",
        "dry_run": dry_run,
        "total_issues": total_issues,
        "num_terminals": len(terminals),
        "contention_strategy": "scope-based partition with agent clustering",
        "routing_config": str(ROUTING_CONFIG),
        "terminals": terminal_plans,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an overnight batch execution plan from GitHub issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Use synthetic issues instead of calling gh CLI (offline testing).",
    )
    parser.add_argument(
        "--repo",
        help="GitHub repo in owner/repo format (uses current repo if omitted).",
    )
    parser.add_argument(
        "--terminals", type=int, default=NUM_TERMINALS,
        help=f"Number of parallel terminals to plan for (default: {NUM_TERMINALS}).",
    )
    parser.add_argument(
        "--output-file",
        help="Write plan JSON to this file in addition to stdout.",
    )
    parser.add_argument(
        "--compact", action="store_true",
        help="Output compact (non-indented) JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    routing_cfg   = load_yaml(ROUTING_CONFIG)
    provider_caps = load_yaml(PROVIDER_CAPS)

    # 1. Fetch issues
    raw_issues = fetch_overnight_issues(args.repo, args.dry_run)
    print(f"[info] Fetched {len(raw_issues)} overnight issue(s).", file=sys.stderr)

    # 2. Enrich each issue
    enriched = []
    for issue in raw_issues:
        agent  = resolve_agent(issue)
        scope  = infer_file_scope(issue)
        issue_data = dict(issue)
        issue_data["agent"]      = agent
        issue_data["file_scope"] = scope
        issue_data["prompt"]     = build_prompt(issue_data)
        issue_data["launch_command"] = build_terminal_command(issue_data)
        enriched.append(issue_data)

    # 3. Assign to terminals
    terminals = assign_terminals(enriched, args.terminals)

    # 4. Assemble plan
    plan = assemble_plan(terminals, routing_cfg, args.repo, args.dry_run)

    # 5. Output
    indent = None if args.compact else 2
    plan_json = json.dumps(plan, indent=indent)

    print(plan_json)

    if args.output_file:
        out_path = Path(args.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(plan_json)
        print(f"[info] Plan written to {args.output_file}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
