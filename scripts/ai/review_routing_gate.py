#!/usr/bin/env python3
"""AI Review Routing Gate — enforces docs/standards/AI_REVIEW_ROUTING_POLICY.md.

Analyzes a PR diff and recommends which AI reviewer(s) should review the change.

Usage:
  # From stdin (pipe a diff):
  git diff main...HEAD | uv run python scripts/ai/review_routing_gate.py --stdin

  # From a PR number (requires gh CLI):
  uv run python scripts/ai/review_routing_gate.py --pr 42

  # From a local diff file:
  uv run python scripts/ai/review_routing_gate.py --diff-file changes.diff

Output: JSON with reviewers, reason, priority, and triggers_matched.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Constants — mirror docs/standards/AI_REVIEW_ROUTING_POLICY.md
# ---------------------------------------------------------------------------

GEMINI_TRIGGERS = {
    "architecture-heavy": {
        "rationale": (
            "Cross-module or cross-repo structural change that benefits "
            "from an independent architectural perspective"
        ),
    },
    "research-heavy": {
        "rationale": (
            "Task requires synthesizing multiple external sources, standards, "
            "or large documents where Gemini's context window adds material value"
        ),
    },
    "ambiguous-requirements": {
        "rationale": (
            "Requirements are underspecified or contested — a third independent "
            "interpretation reduces risk"
        ),
    },
    "high-stakes": {
        "rationale": (
            "Change affects production systems, security boundaries, data "
            "integrity, or compliance — cost of error justifies extra review"
        ),
    },
    "context-saturation": {
        "rationale": (
            "Claude's context is already saturated with task material — "
            "Gemini can process overflow without losing fidelity"
        ),
    },
}

# Thresholds
CROSS_MODULE_DIR_THRESHOLD = 4  # directories touched to count as architecture-heavy
URL_THRESHOLD = 5  # added URLs to count as research-heavy
LARGE_DIFF_LINES = 500  # added lines to count as context-saturation
AMBIGUOUS_MARKER_THRESHOLD = 4  # TODO/FIXME/TBD markers to count as ambiguous

# Architecture-sensitive files
ARCHITECTURE_FILES = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    ".claude/rules/patterns.md",
    "AGENTS.md",
    ".claude/settings.json",
}

# High-stakes path patterns
HIGH_STAKES_PATTERNS = [
    r"(auth|security|encrypt|secret|token|credential|password|api.key)",
    r"(deploy|production|prod[.-]|release|migration)",
    r"(compliance|audit|gdpr|hipaa|pci)",
]

# Research indicators (URL patterns in added lines)
URL_PATTERN = re.compile(r"https?://[^\s\"'>\]]+")

# Ambiguity markers
AMBIGUITY_MARKERS = re.compile(r"\b(TODO|FIXME|TBD|HACK|XXX|UNCLEAR|UNDECIDED)\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class RoutingRecommendation:
    """Structured review routing recommendation."""

    orchestrator: str = "claude"
    reviewers: list = field(default_factory=lambda: ["codex"])
    reason: str = ""
    priority: str = "normal"  # low, normal, high
    triggers_matched: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "orchestrator": self.orchestrator,
            "reviewers": self.reviewers,
            "reason": self.reason,
            "priority": self.priority,
            "triggers_matched": self.triggers_matched,
        }


# ---------------------------------------------------------------------------
# Diff analysis
# ---------------------------------------------------------------------------

def _extract_files_from_diff(diff: str) -> list[str]:
    """Extract file paths from a unified diff."""
    return re.findall(r"^diff --git a/(.+?) b/", diff, re.MULTILINE)


def _extract_top_dirs(files: list[str]) -> set[str]:
    """Extract unique top-level directories from file paths."""
    dirs = set()
    for f in files:
        parts = f.split("/")
        if len(parts) > 1:
            dirs.add(parts[0])
        else:
            dirs.add(".")  # root-level file
    return dirs


def _count_added_lines(diff: str) -> int:
    """Count lines added (starting with + but not +++)."""
    return sum(1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))


def _extract_added_content(diff: str) -> str:
    """Extract only the added lines from a diff."""
    return "\n".join(
        line[1:] for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def analyze_diff_for_triggers(diff: str) -> list[str]:
    """Analyze a diff and return list of Gemini trigger names that fire.

    Implements the five trigger rules from AI_REVIEW_ROUTING_POLICY.md.
    """
    triggers = []
    files = _extract_files_from_diff(diff)
    added_content = _extract_added_content(diff)
    added_line_count = _count_added_lines(diff)

    # 1. Architecture-heavy: cross-module changes or architecture-sensitive files
    top_dirs = _extract_top_dirs(files)
    arch_files_touched = any(f in ARCHITECTURE_FILES for f in files)
    if len(top_dirs) >= CROSS_MODULE_DIR_THRESHOLD or (
        arch_files_touched and len(top_dirs) >= 2
    ):
        triggers.append("architecture-heavy")

    # 2. Research-heavy: many external URLs in added content
    urls = URL_PATTERN.findall(added_content)
    if len(urls) >= URL_THRESHOLD:
        triggers.append("research-heavy")

    # 3. Ambiguous-requirements: many TODO/FIXME/TBD markers in added content
    markers = AMBIGUITY_MARKERS.findall(added_content)
    if len(markers) >= AMBIGUOUS_MARKER_THRESHOLD:
        triggers.append("ambiguous-requirements")

    # 4. High-stakes: security/production/compliance paths or content
    high_stakes_hit = False
    for pattern in HIGH_STAKES_PATTERNS:
        # Check file paths
        for f in files:
            if re.search(pattern, f, re.IGNORECASE):
                high_stakes_hit = True
                break
        # Check added content
        if re.search(pattern, added_content, re.IGNORECASE):
            high_stakes_hit = True
        if high_stakes_hit:
            break
    if high_stakes_hit:
        triggers.append("high-stakes")

    # 5. Context-saturation: very large diffs
    if added_line_count >= LARGE_DIFF_LINES:
        triggers.append("context-saturation")

    return triggers


def classify_change_scope(diff: str) -> str:
    """Classify the scope of a change for priority assignment.

    Returns one of: docs-only, tests-only, code, mixed.
    """
    files = _extract_files_from_diff(diff)
    if not files:
        # Fall back to line-level heuristic
        return "code"

    has_docs = False
    has_tests = False
    has_code = False

    for f in files:
        lower = f.lower()
        if lower.startswith("docs/") or lower.endswith((".md", ".rst", ".txt")):
            has_docs = True
        elif "test" in lower or lower.startswith("tests/"):
            has_tests = True
        else:
            has_code = True

    if has_code and (has_docs or has_tests):
        return "mixed"
    if has_docs and not has_tests and not has_code:
        return "docs-only"
    if has_tests and not has_docs and not has_code:
        return "tests-only"
    return "code"


# ---------------------------------------------------------------------------
# Recommendation builder
# ---------------------------------------------------------------------------

def build_recommendation(triggers: list[str], scope: str) -> RoutingRecommendation:
    """Build a routing recommendation from triggers and scope.

    Per AI_REVIEW_ROUTING_POLICY.md:
    - Default: two-provider (Claude orchestrates, Codex reviews)
    - If any trigger fires: three-provider (add Gemini)
    """
    rec = RoutingRecommendation()
    rec.triggers_matched = list(triggers)

    if triggers:
        rec.reviewers = ["codex", "gemini"]
        rec.priority = "high"
        trigger_str = ", ".join(triggers)
        rec.reason = (
            f"Three-provider review: Gemini triggered by [{trigger_str}]. "
            f"Per AI_REVIEW_ROUTING_POLICY.md, these conditions justify "
            f"an independent third-lane review."
        )
    else:
        rec.reviewers = ["codex"]
        rec.reason = (
            "Default two-provider review: Claude orchestrates, Codex reviews. "
            "No Gemini trigger conditions detected."
        )
        if scope in ("docs-only", "tests-only"):
            rec.priority = "low"
        else:
            rec.priority = "normal"

    return rec


# ---------------------------------------------------------------------------
# Diff retrieval
# ---------------------------------------------------------------------------

def get_pr_diff(pr_number: int) -> str:
    """Get the diff for a PR using the gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "pr", "diff", str(pr_number)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"Error: gh pr diff failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        return result.stdout
    except FileNotFoundError:
        print("Error: gh CLI not found. Install it: https://cli.github.com/", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: gh pr diff timed out after 30s", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(args: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="AI Review Routing Gate — determines which AI reviewers should review a change.",
        epilog="Policy: docs/standards/AI_REVIEW_ROUTING_POLICY.md",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr", type=int, help="PR number (uses gh CLI to fetch diff)")
    group.add_argument("--stdin", action="store_true", help="Read diff from stdin")
    group.add_argument("--diff-file", type=str, help="Path to a diff file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    parsed = parser.parse_args(args)

    # Get the diff
    if parsed.pr:
        diff = get_pr_diff(parsed.pr)
    elif parsed.stdin:
        diff = sys.stdin.read()
    elif parsed.diff_file:
        with open(parsed.diff_file) as f:
            diff = f.read()
    else:
        parser.print_help()
        return 1

    if not diff.strip():
        print("Error: empty diff provided", file=sys.stderr)
        return 1

    # Analyze
    triggers = analyze_diff_for_triggers(diff)
    scope = classify_change_scope(diff)
    rec = build_recommendation(triggers, scope)

    # Output
    indent = 2 if parsed.pretty else None
    print(json.dumps(rec.to_dict(), indent=indent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
