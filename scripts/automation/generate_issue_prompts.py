#!/usr/bin/env python3
"""
Generate Claude-ready prompt files from approved GitHub issues.

Queries GitHub for issues with a target label (default: plan-approved issues
with an agent label), classifies each into one of 10 prompt types based on
its `cat:` and `domain:` labels, extracts paths and test commands from the
issue's plan file if it exists, and writes a fully-populated prompt file.

Usage:
    uv run scripts/automation/generate_issue_prompts.py                   # all approved agent:claude issues
    uv run scripts/automation/generate_issue_prompts.py --issue 1234      # single issue
    uv run scripts/automation/generate_issue_prompts.py --label "cat:bugfix"  # custom label filter
    uv run scripts/automation/generate_issue_prompts.py --dry-run         # preview to stdout
    uv run scripts/automation/generate_issue_prompts.py --list-types      # show prompt type catalog
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "prompts" / "pending"
PLANS_DIR = REPO_ROOT / "docs" / "plans"
REPO_SLUG = "vamseeachanta/workspace-hub"

# ---------------------------------------------------------------------------
# Prompt type catalog
# ---------------------------------------------------------------------------
# Each entry maps a type key to its metadata.  `cat_labels` and
# `domain_labels` are checked in priority order — first match wins.
# Priority is the list order of PROMPT_TYPES itself (first = highest).

PROMPT_TYPES: list[dict[str, Any]] = [
    {
        "key": "tdd-bugfix",
        "number": 3,
        "name": "TDD-first bugfix",
        "cat_labels": ["cat:bugfix"],
        "domain_labels": ["domain:workflow-fix"],
        "title_hints": ["bug", "fix", "broken", "regression", "fails", "crash"],
    },
    {
        "key": "data-pipeline",
        "number": 8,
        "name": "Data-pipeline issue",
        "cat_labels": ["cat:data-pipeline", "cat:data"],
        "domain_labels": [
            "domain:data-pipeline",
            "domain:extraction-pipeline",
            "domain:pipeline",
            "domain:data-fixtures",
        ],
        "title_hints": ["pipeline", "etl", "export", "ingest", "extract", "schema"],
    },
    {
        "key": "cli-tooling",
        "number": 7,
        "name": "CLI / tooling issue",
        "cat_labels": ["cat:tooling", "cat:developer-experience"],
        "domain_labels": [
            "domain:tooling",
            "domain:cli-ux",
            "domain:terminal",
        ],
        "title_hints": ["cli", "command", "flag", "argparse", "script"],
    },
    {
        "key": "refactor-with-guards",
        "number": 4,
        "name": "Refactor with guards",
        "cat_labels": [],
        "domain_labels": ["domain:refactor", "domain:refactoring"],
        "title_hints": ["refactor", "restructure", "reorganize", "consolidate"],
    },
    {
        "key": "test-coverage",
        "number": 5,
        "name": "Test coverage uplift",
        "cat_labels": [],
        "domain_labels": ["domain:test-coverage", "domain:testing"],
        "title_hints": ["test coverage", "add tests", "missing tests", "untested"],
    },
    {
        "key": "doc-sync",
        "number": 6,
        "name": "Documentation + implementation sync",
        "cat_labels": ["cat:documentation"],
        "domain_labels": ["domain:docs", "domain:doc-generation"],
        "title_hints": ["docs", "documentation", "readme", "out of date"],
    },
    {
        "key": "cleanup-hardening",
        "number": 9,
        "name": "Cleanup / hardening",
        "cat_labels": ["cat:maintenance"],
        "domain_labels": [
            "domain:cleanup",
            "domain:repo-cleanup",
            "domain:repo-health",
            "domain:code-quality",
            "domain:maintenance",
        ],
        "title_hints": ["cleanup", "harden", "lint", "deprecat", "dead code"],
    },
    {
        "key": "verify-and-close",
        "number": 2,
        "name": "Verify and close",
        "cat_labels": [],
        "domain_labels": [],
        "title_hints": ["verify", "already done", "close if"],
    },
    {
        "key": "planning-checkpoint",
        "number": 10,
        "name": "Planning-to-execution checkpoint",
        "cat_labels": ["cat:strategy", "cat:research"],
        "domain_labels": ["domain:research", "domain:strategy"],
        "title_hints": ["plan", "investigate", "spike", "explore options"],
    },
    {
        "key": "single-issue",
        "number": 1,
        "name": "Single-issue implementation (default)",
        "cat_labels": [],
        "domain_labels": [],
        "title_hints": [],
    },
]


# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------

def gh_issue_view(number: int) -> dict:
    """Fetch a single issue with all metadata."""
    result = subprocess.run(
        [
            "gh", "-R", REPO_SLUG, "issue", "view", str(number),
            "--json", "number,title,body,labels,comments,assignees,state",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"ERROR: gh issue view {number} failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def gh_query_issues(labels: str) -> list[dict]:
    """Query GitHub for open issues matching comma-separated labels."""
    result = subprocess.run(
        [
            "gh", "-R", REPO_SLUG, "issue", "list",
            "-L", "200",
            "--state", "open",
            "--label", labels,
            "--json", "number,title,labels",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"Warning: gh query failed for {labels}: {result.stderr}", file=sys.stderr)
        return []
    return json.loads(result.stdout) if result.stdout.strip() else []


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_issue(issue: dict) -> dict:
    """Classify an issue into one of the 10 prompt types.

    Priority order:
    1. Exact `cat:` label match
    2. Exact `domain:` label match
    3. Title keyword hint
    4. Default → single-issue implementation (#1)
    """
    label_names = {lbl["name"] for lbl in issue.get("labels", [])}
    title_lower = issue.get("title", "").lower()

    for ptype in PROMPT_TYPES:
        # Check cat: labels
        if any(cl in label_names for cl in ptype["cat_labels"]):
            return ptype
        # Check domain: labels
        if any(dl in label_names for dl in ptype["domain_labels"]):
            return ptype

    # Fallback: title hints (looser match, checked after all label passes)
    for ptype in PROMPT_TYPES:
        if any(hint in title_lower for hint in ptype["title_hints"]):
            return ptype

    # Default
    return PROMPT_TYPES[-1]


# ---------------------------------------------------------------------------
# Plan file extraction
# ---------------------------------------------------------------------------

def find_plan_file(issue_number: int) -> Path | None:
    """Find the plan file for an issue, if it exists."""
    pattern = f"*-issue-{issue_number}-*"
    matches = sorted(PLANS_DIR.glob(pattern))
    if matches:
        return matches[-1]  # most recent by date prefix
    # Also try without 'issue-' prefix
    pattern2 = f"*-{issue_number}-*"
    matches2 = [m for m in sorted(PLANS_DIR.glob(pattern2)) if m.name != "_template-issue-plan.md"]
    return matches2[-1] if matches2 else None


def extract_allowed_paths(plan_text: str) -> str:
    """Extract file paths from the 'Files to Change' section."""
    paths: list[str] = []
    in_section = False
    for line in plan_text.splitlines():
        if re.match(r"^##\s+Files to Change", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and "|" in line:
            # Parse table rows: | Action | Path | Reason |
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 3:
                path_cell = cells[2].strip("`").strip()
                if path_cell and path_cell != "Path" and not path_cell.startswith("---"):
                    paths.append(path_cell)
    if not paths:
        return "# (no plan file found — inspect issue body for target files)"
    return "\n".join(f"  - {p}" for p in paths)


def extract_test_commands(plan_text: str) -> str:
    """Extract test commands from the 'Acceptance Criteria' section."""
    commands: list[str] = []
    in_section = False
    for line in plan_text.splitlines():
        if re.match(r"^##\s+Acceptance Criteria", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            # Look for uv run pytest or similar test commands
            match = re.search(r"`(uv run pytest[^`]+|pytest[^`]+|python -m pytest[^`]+)`", line)
            if match:
                commands.append(match.group(1))
    if not commands:
        return "uv run pytest tests/ -v --tb=short"
    return "\n".join(commands)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

TEMPLATES: dict[int, str] = {
    1: """\
You are Claude operating as a 5-role internal agent team in a single terminal:
1. Planner
2. Implementer
3. Reviewer
4. Tester
5. Synthesizer

Repository: {repo}
GitHub issue: #{number}
Issue title: {title}

Mission:
Execute this GitHub issue end-to-end in this single terminal only. Do not use multiple worktrees or multiple terminals. Work only within the approved issue scope.

Execution rules:
- First inspect the issue using gh
- Summarize scope, acceptance criteria, and target files
- If the issue is already done, prove it with evidence and prepare a closeout comment instead of changing code
- If code changes are needed, use TDD: create or tighten a failing test first, then implement the minimum fix
- Run targeted validation before any broader validation
- Perform an adversarial self-review after implementation
- Commit and push only if validation passes
- Post a concise GitHub progress comment and final closeout comment

Path contract:
- Owned paths:
{allowed_paths}

Required commands:
  gh issue view {number} --repo {repo}
  git status
{test_commands}

Output requirements:
- Show:
  1. scope summary
  2. already-done vs not-done decision
  3. failing proof
  4. implementation summary
  5. validation results
  6. adversarial review verdict: PASS | MINOR | MAJOR
  7. exact GitHub comment text before posting
  8. exact commit message

Do not ask the user questions. Make reasonable decisions and execute.
""",

    2: """\
You are Claude acting as an internal agent team in one terminal:
Planner, Verifier, Reviewer, Synthesizer.

Repository: {repo}
GitHub issue: #{number}
Issue title: {title}

Goal:
Determine whether this issue is already satisfied. Prefer verification and closure over unnecessary implementation.

Required workflow:
- Read the full issue and recent comments with gh
- Inspect current repo state for direct evidence
- Run the narrowest relevant validation commands
- Compare actual repo behavior against issue acceptance criteria
- Decide exactly one:
  1. already done
  2. not done
  3. uncertain

If already done:
- Draft and post a GitHub comment with evidence
- Close the issue

If not done:
- Stop after producing a precise execution plan, failing proof target, owned paths, and next implementation step
- Do not implement

If uncertain:
- Produce the exact missing evidence needed to decide

Constraints:
- Single terminal only
- No broad refactors
- No speculative fixes
- No branch creation unless repo policy requires it

Validation commands:
{test_commands}

Deliverable format:
- Decision
- Evidence
- Exact gh commands/comments used
- Close/no-close outcome

Do not ask the user questions. Make reasonable decisions and execute.
""",

    3: """\
You are Claude operating as a single-terminal internal agent team.

Repo: {repo}
Issue: #{number}
Title: {title}

Primary objective:
Fix this bug with strict TDD in a single terminal.

Mandatory sequence:
1. Read the issue
2. Identify the smallest failing test or validator proving the bug
3. Write or tighten that test first
4. Run it and capture the failure
5. Implement the minimum fix
6. Re-run the same test
7. Run nearby regression checks
8. Perform adversarial self-review
9. Commit, push, and post GitHub update if green

Write boundaries:
- Only modify:
{allowed_paths}

Testing:
- Use only these validation commands unless required otherwise:
{test_commands}

Adversarial review checklist:
- Did the test really fail before the fix?
- Does the fix actually satisfy the issue?
- Did we accidentally expand scope?
- Could edge cases still fail?
- Are docs/comments/tests now aligned?

Required outputs:
- failing test evidence
- minimal diff summary
- validation matrix
- review verdict
- final issue comment
- commit hash after push

Do not ask the user questions. Make reasonable decisions and execute.
""",

    4: """\
You are Claude in one terminal, simulating an internal team:
Architect, Refactorer, Tester, Reviewer, Reporter.

Repo: {repo}
Issue: #{number}
Title: {title}

Goal:
Execute this refactor safely without changing intended behavior.

Rules:
- Single terminal only
- Behavior-preserving unless the issue explicitly requires behavior changes
- Add or tighten tests before structural edits
- Keep changes inside:
{allowed_paths}

Process:
1. Inspect issue + target module(s)
2. Identify invariants and current behavior
3. Add safety tests first
4. Refactor in small steps
5. Run targeted tests after each step
6. Run final regression checks
7. Perform adversarial review focused on hidden behavior drift
8. Commit/push if safe
9. Post GitHub update

Required final report:
- before/after structure summary
- tests added
- invariants preserved
- risks found
- final recommendation
- gh comment text
- commit message

Do not ask the user questions. Make reasonable decisions and execute.
""",

    5: """\
You are Claude acting as a single-terminal internal QA team:
Planner, Test Author, Reviewer, Synthesizer.

Repo: {repo}
Issue: #{number}
Title: {title}

Goal:
Increase meaningful test coverage for this issue without speculative product changes.

Constraints:
- Do not modify production code unless required to enable valid tests
- If production code is defective, prove it with failing tests before changing it
- Stay within:
{allowed_paths}

Workflow:
1. Read issue and inspect current tests
2. Find the most important uncovered scenarios
3. Add tests that reflect real issue acceptance criteria
4. Run targeted tests
5. If tests expose a bug, implement only the minimum required fix
6. Re-run tests
7. Perform adversarial review on test quality:
   - are tests meaningful?
   - do they fail for the right reason?
   - are mocks excessive?
   - are edge cases covered?

Validation:
{test_commands}

Required output:
- gaps identified
- tests added
- any source fixes made
- pass/fail evidence
- final GitHub comment draft
- exact commit message

Do not ask the user questions. Make reasonable decisions and execute.
""",

    6: """\
You are Claude in a single terminal with internal roles:
Planner, Implementer, Doc Editor, Reviewer, Tester.

Repo: {repo}
Issue: #{number}
Title: {title}

Goal:
Resolve this issue while keeping code, tests, and documentation synchronized.

Rules:
- Update docs only if they are directly impacted by the issue
- Do not let documentation drift from implementation
- Use TDD for behavior changes
- Restrict edits to:
{allowed_paths}

Process:
1. Read issue and inspect relevant code/docs/tests
2. Determine whether the issue is code-only, doc-only, or both
3. If behavior changes, create failing proof first
4. Implement minimum fix
5. Update affected docs/examples/help text
6. Validate code and documentation consistency
7. Run adversarial review

Validation:
{test_commands}

Final deliverable:
- issue status: already done / fixed / blocked
- changed files grouped by code/tests/docs
- validation evidence
- doc consistency notes
- exact final gh comment text

Do not ask the user questions. Make reasonable decisions and execute.
""",

    7: """\
You are Claude operating as a one-terminal internal tooling team:
CLI Analyst, Implementer, Tester, Reviewer, Reporter.

Repo: {repo}
Issue: #{number}
Title: {title}

Objective:
Fix or enhance the CLI/tooling behavior described in the issue.

Rules:
- Reproduce via real CLI invocation where possible
- Favor deterministic smoke tests
- Avoid broad unrelated cleanup
- Only touch:
{allowed_paths}

Execution:
1. Read issue and inspect the CLI entrypoint + related tests
2. Reproduce the issue with the smallest command possible
3. Add or tighten a failing CLI-focused test
4. Implement minimum fix
5. Re-run the exact repro command
6. Run targeted regression tests
7. Perform adversarial review focused on:
   - UX regressions
   - error handling
   - exit codes
   - argument parsing
   - help text drift

Validation commands:
{test_commands}

Required report:
- repro command
- failing evidence
- fix summary
- final smoke test output
- review verdict
- commit and GitHub comment

Do not ask the user questions. Make reasonable decisions and execute.
""",

    8: """\
You are Claude in one terminal acting as:
Data Analyst, Implementer, Validator, Reviewer, Synthesizer.

Repo: {repo}
Issue: #{number}
Title: {title}

Goal:
Implement or fix this data-pipeline issue safely and with strong validation.

Constraints:
- Single terminal only
- No silent schema changes
- No hidden breaking changes
- Only edit:
{allowed_paths}

Workflow:
1. Read issue and inspect pipeline entrypoints, schemas, fixtures, and tests
2. Identify input/output contract
3. Add failing proof for the exact broken behavior
4. Implement minimal change
5. Validate output shape, content, and edge cases
6. Run adversarial review focused on:
   - null handling
   - ordering assumptions
   - schema drift
   - join explosion / duplication
   - backward compatibility

Validation:
{test_commands}

Output:
- contract summary
- failing proof
- change summary
- validation evidence
- backward compatibility note
- final gh comment draft
- exact commit message

Do not ask the user questions. Make reasonable decisions and execute.
""",

    9: """\
You are Claude acting as an internal quality team in a single terminal:
Planner, Hardener, Tester, Reviewer, Reporter.

Repo: {repo}
Issue: #{number}
Title: {title}

Goal:
Execute this cleanup/hardening issue without turning it into an uncontrolled refactor.

Rules:
- Stay tightly inside issue scope
- If you find adjacent problems, list them as future-issue candidates instead of absorbing them
- Restrict edits to:
{allowed_paths}

Required process:
1. Read issue
2. Inspect current state
3. Identify exact hardening target
4. Add tests/checks if applicable
5. Apply minimal cleanup/hardening change
6. Validate
7. Perform adversarial review
8. Produce future-issue candidates for anything intentionally deferred

Validation:
{test_commands}

Final output format:
- scope executed
- changes made
- validation results
- residual risks
- future issue candidates
- final GitHub comment text

Do not ask the user questions. Make reasonable decisions and execute.
""",

    10: """\
You are Claude as a single-terminal internal agent team:
Planner, Scope Auditor, Tester, Reviewer, Synthesizer.

Repo: {repo}
Issue: #{number}
Title: {title}

Goal:
Determine whether this issue is directly executable now in a single terminal, and if yes, execute it. If not, stop with a high-quality operator-ready dossier.

Decision workflow:
1. Read issue and comments
2. Confirm whether acceptance criteria are concrete enough
3. Confirm target files are identifiable
4. Confirm validation path exists
5. Confirm scope fits a single-terminal execution
6. Decide:
   - executable now
   - executable with minor clarification inferred from repo state
   - not safely executable now

If executable now:
- proceed with TDD implementation
- validate
- review
- commit/push
- post GitHub updates

If not safely executable now:
Produce:
- missing context
- inferred target files
- proposed acceptance criteria
- proposed tests
- owned/read-only/forbidden paths
- recommended next operator action

Allowed paths:
{allowed_paths}

Validation:
{test_commands}

Required deliverable:
- execution decision
- evidence
- action taken
- exact GitHub comment text

Do not ask the user questions. Make reasonable decisions and execute.
""",
}


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

def build_prompt(issue: dict, ptype: dict, plan_text: str | None) -> str:
    """Fill a prompt template with real issue data."""
    allowed = extract_allowed_paths(plan_text) if plan_text else \
        "  # (no plan file found — inspect issue body for target files)"
    tests = extract_test_commands(plan_text) if plan_text else \
        "  uv run pytest tests/ -v --tb=short"

    template = TEMPLATES[ptype["number"]]
    return template.format(
        repo=REPO_SLUG,
        number=issue["number"],
        title=issue["title"],
        allowed_paths=allowed,
        test_commands=tests,
    )


def prompt_filename(issue: dict, ptype: dict) -> str:
    """Generate a deterministic filename for a prompt."""
    slug = re.sub(r"[^a-z0-9]+", "-", issue["title"].lower()).strip("-")[:60]
    return f"{issue['number']:04d}-{ptype['key']}-{slug}.md"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Claude-ready prompt files from approved GitHub issues.",
    )
    parser.add_argument("--issue", "-i", type=int, help="Generate for a single issue number")
    parser.add_argument("--label", "-l", default="agent:claude",
                        help="Label filter for issue queries (default: agent:claude)")
    parser.add_argument("--status-label", default="",
                        help="Additional status label to require (e.g. status:plan-approved)")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Print prompts to stdout instead of writing files")
    parser.add_argument("--output-dir", "-o", type=Path, default=OUTPUT_DIR,
                        help=f"Output directory (default: {OUTPUT_DIR.relative_to(REPO_ROOT)})")
    parser.add_argument("--list-types", action="store_true",
                        help="Print the prompt type catalog and exit")
    parser.add_argument("--force-type", type=int, choices=range(1, 11), metavar="N",
                        help="Override auto-classification with prompt type 1-10")
    args = parser.parse_args()

    if args.list_types:
        print("Prompt Type Catalog")
        print("=" * 50)
        for pt in PROMPT_TYPES:
            cat_hint = ", ".join(pt["cat_labels"][:2]) if pt["cat_labels"] else "-"
            domain_hint = ", ".join(pt["domain_labels"][:2]) if pt["domain_labels"] else "-"
            print(f"  #{pt['number']:2d}  {pt['name']}")
            print(f"       cat: {cat_hint}")
            print(f"       domain: {domain_hint}")
            print()
        return

    # Collect issues
    issues: list[dict] = []
    if args.issue:
        issue_data = gh_issue_view(args.issue)
        issues.append(issue_data)
    else:
        labels = args.label
        if args.status_label:
            labels = f"{labels},{args.status_label}"
        raw = gh_query_issues(labels)
        if not raw:
            print(f"No open issues found with labels: {labels}", file=sys.stderr)
            sys.exit(0)
        # Fetch full data for each (we need body + comments for plan extraction)
        for stub in raw:
            issues.append(gh_issue_view(stub["number"]))

    # Process each issue
    now = datetime.now(timezone.utc)
    generated: list[str] = []

    for issue in sorted(issues, key=lambda i: i["number"]):
        num = issue["number"]

        # Classify
        if args.force_type:
            ptype = next(pt for pt in PROMPT_TYPES if pt["number"] == args.force_type)
        else:
            ptype = classify_issue(issue)

        # Find plan file
        plan_path = find_plan_file(num)
        plan_text = plan_path.read_text() if plan_path else None

        # Build prompt
        prompt = build_prompt(issue, ptype, plan_text)

        # Add metadata header
        header = (
            f"<!-- generated: {now.strftime('%Y-%m-%dT%H:%M:%SZ')} -->\n"
            f"<!-- issue: #{num} -->\n"
            f"<!-- type: {ptype['number']} — {ptype['name']} -->\n"
            f"<!-- plan: {plan_path.relative_to(REPO_ROOT) if plan_path else 'none'} -->\n"
            f"<!-- classifier: {'forced' if args.force_type else 'auto'} -->\n"
            "\n"
        )
        full_prompt = header + prompt

        fname = prompt_filename(issue, ptype)

        if args.dry_run:
            sep = "=" * 70
            print(f"\n{sep}")
            print(f"FILE: {fname}")
            print(f"TYPE: #{ptype['number']} — {ptype['name']}")
            print(f"PLAN: {plan_path.relative_to(REPO_ROOT) if plan_path else 'none'}")
            print(sep)
            print(full_prompt)
        else:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            out_path = args.output_dir / fname
            out_path.write_text(full_prompt)
            generated.append(str(out_path.relative_to(REPO_ROOT)))
            print(f"  OK  #{num:4d}  type={ptype['number']:2d}  {fname}")

    if not args.dry_run and generated:
        print(f"\n{len(generated)} prompt(s) written to {args.output_dir.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
