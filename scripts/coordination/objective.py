"""Objective intake dry-run command.

Reads a GitHub issue, extracts the objective brief, and renders lane contracts
without mutating GitHub or git state when --dry-run is used.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable


SECTION_ALIASES = {
    "Outcome": "outcome",
    "Done when": "done_when",
    "Constraints / must not": "constraints_must_not",
    "Out of scope": "out_of_scope",
    "Return format": "return_format",
    "Risk tier": "risk_tier",
}


@dataclass(frozen=True)
class IssueBrief:
    number: int
    title: str
    state: str
    outcome: str
    done_when: str
    constraints_must_not: str
    out_of_scope: str
    return_format: str
    risk_tier: str


@dataclass(frozen=True)
class LaneContract:
    role: str
    issue_number: int
    mode: str
    scope: str
    owned_paths: str
    read_only_paths: str
    forbidden_paths: str
    validators: tuple[str, ...]
    writes_allowed: bool
    dry_run: bool

    def to_markdown(self) -> str:
        writes = "yes, owned paths only" if self.writes_allowed else "no"
        lines = [
            f"### Role: {self.role}",
            f"- Issue: #{self.issue_number}",
            f"- Mode: {self.mode}",
            f"- Scope: {self.scope}",
            f"- Writes allowed: {writes}",
            f"- Owned paths: {self.owned_paths}",
            f"- Read-only paths: {self.read_only_paths}",
            f"- Forbidden paths: {self.forbidden_paths}",
            "- Validators:",
            *[f"  - `{validator}`" for validator in self.validators],
            "- Coordinator owns integration, push, PR, and issue closeout.",
        ]
        if self.dry_run:
            lines.append(
                "- DRY RUN: no labels, comments, branches, commits, or issues were changed."
            )
        return "\n".join(lines)


def extract_objective_brief(
    number: int, title: str, state: str, body: str
) -> IssueBrief:
    sections = _extract_sections(body)
    missing = [label for label in SECTION_ALIASES if not sections.get(label)]
    if missing:
        if len(missing) == len(SECTION_ALIASES):
            return _legacy_brief(number, title, state, body)
        return _partial_brief(number, title, state, body, sections)
    tier = sections["Risk tier"].strip().upper()[:1]
    if tier not in {"A", "B", "C"}:
        raise ValueError(f"issue #{number} has invalid risk tier: {sections['Risk tier']}")
    return IssueBrief(
        number=number,
        title=title,
        state=state,
        outcome=sections["Outcome"].strip(),
        done_when=sections["Done when"].strip(),
        constraints_must_not=sections["Constraints / must not"].strip(),
        out_of_scope=sections["Out of scope"].strip(),
        return_format=sections["Return format"].strip(),
        risk_tier=tier,
    )


def classify_execution_mode(brief: IssueBrief) -> str:
    done = brief.done_when.lower()
    if brief.risk_tier == "A":
        return "parallel-readonly"
    if any(token in done for token in ("role agent", "lane contract", "dry run")):
        return "parallel-readonly"
    if any(token in done for token in ("implement", "template", "script", "code")):
        return "single-lane"
    return "single-lane"


def render_lane_contracts(brief: IssueBrief, *, dry_run: bool) -> list[LaneContract]:
    mode = classify_execution_mode(brief)
    roles = _roles_for_mode(mode)
    return [
        LaneContract(
            role=role,
            issue_number=brief.number,
            mode=mode,
            scope=_scope_for_role(role, brief),
            owned_paths=_owned_paths(role, mode),
            read_only_paths="repository files, issue body, referenced plans, standards",
            forbidden_paths=(
                "secrets, licensed source documents, unrelated repos, "
                "owner-controlled labels"
            ),
            validators=_validators_for_role(role, mode),
            writes_allowed=role == "builder" and mode == "parallel-worktree",
            dry_run=dry_run,
        )
        for role in roles
    ]


def fetch_issue(issue: int, repo: str | None) -> dict:
    cmd = [
        "gh",
        "issue",
        "view",
        str(issue),
        "--json",
        "number,title,state,body,url,labels",
    ]
    if repo:
        cmd.extend(["--repo", repo])
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)


def render_dry_run(brief: IssueBrief) -> str:
    header = [
        f"# Objective dry run: #{brief.number} {brief.title}",
        "",
        f"- Issue state: {brief.state}",
        f"- Risk tier: {brief.risk_tier}",
        f"- Execution mode: {classify_execution_mode(brief)}",
        "",
        "## Lane contracts",
        "",
    ]
    contracts = [contract.to_markdown() for contract in render_lane_contracts(brief, dry_run=True)]
    return "\n\n".join(["\n".join(header), *contracts])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render objective lane contracts.")
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--repo", help="owner/repo override for gh issue view")
    parser.add_argument("--dry-run", action="store_true", required=True)
    args = parser.parse_args(argv)

    try:
        issue = fetch_issue(args.issue, args.repo)
        brief = extract_objective_brief(
            issue["number"], issue["title"], issue["state"], issue.get("body") or ""
        )
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as exc:
        print(f"objective: {exc}", file=sys.stderr)
        return 1
    print(render_dry_run(brief))
    return 0


def _extract_sections(body: str) -> dict[str, str]:
    matches = list(re.finditer(r"^\s*###\s+(.+?)\s*$", body, flags=re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        label = _canonical_label(match.group(1))
        if not label:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[label] = body[start:end].strip()
    sections.update({k: v for k, v in _extract_bold_sections(body).items() if k not in sections})
    return sections


def _extract_bold_sections(body: str) -> dict[str, str]:
    labels = "|".join(re.escape(label) for label in SECTION_ALIASES)
    pattern = re.compile(rf"^\s*\*\*({labels}):\*\*\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        label = match.group(1)
        inline = match.group(2).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        rest = body[start:end].strip()
        sections[label] = "\n".join(part for part in (inline, rest) if part).strip()
    return sections


def _legacy_brief(number: int, title: str, state: str, body: str) -> IssueBrief:
    return IssueBrief(
        number=number,
        title=title,
        state=state,
        outcome=title,
        done_when=(
            "Legacy issue lacks Objective template fields; dry-run contracts "
            "must preserve the existing issue scope and verify against its body."
        ),
        constraints_must_not=(
            "Dry run only. Do not change labels, comments, branches, commits, "
            "issues, or close state."
        ),
        out_of_scope="Changing historical issue content or reopening the issue.",
        return_format="Lane contracts for coordinator review.",
        risk_tier="B",
    )


def _partial_brief(
    number: int, title: str, state: str, body: str, sections: dict[str, str]
) -> IssueBrief:
    return IssueBrief(
        number=number,
        title=title,
        state=state,
        outcome=sections.get("Outcome", title).strip(),
        done_when=sections.get("Done when", body.strip() or title).strip(),
        constraints_must_not=sections.get(
            "Constraints / must not",
            "Dry-run partial Objective brief; do not mutate labels, comments, "
            "branches, commits, issues, or close state.",
        ).strip(),
        out_of_scope=sections.get(
            "Out of scope", "Changing issue scope during dry-run intake."
        ).strip(),
        return_format=sections.get(
            "Return format", "Lane contracts for coordinator review."
        ).strip(),
        risk_tier=_risk_tier_from_text(sections.get("Risk tier", body)),
    )


def _risk_tier_from_text(text: str) -> str:
    match = re.search(r"\b(?:risk\s+tier|tier)\s*[:\-]?\s*([ABC])\b", text, re.I)
    return match.group(1).upper() if match else "B"


def _canonical_label(raw: str) -> str | None:
    normalized = raw.strip().lower().replace(" / ", "/")
    for label in SECTION_ALIASES:
        candidate = label.lower().replace(" / ", "/")
        if normalized == candidate:
            return label
    return None


def _roles_for_mode(mode: str) -> tuple[str, ...]:
    if mode == "parallel-worktree":
        return ("scout", "builder", "gap-checker", "reporter", "verifier")
    if mode == "parallel-readonly":
        return ("scout", "explorer", "gap-checker", "verifier")
    return ("scout", "builder", "verifier")


def _scope_for_role(role: str, brief: IssueBrief) -> str:
    scopes = {
        "scout": "collect resource intelligence and risks for the objective",
        "explorer": "compare viable execution options before writes",
        "builder": "implement the assigned owned-path change set with TDD",
        "gap-checker": "check Done when and Constraints / must not coverage",
        "reporter": "draft the owner-facing status or PR summary",
        "verifier": "independently verify returned evidence and policy gates",
    }
    return f"{scopes[role]}: {brief.outcome}"


def _owned_paths(role: str, mode: str) -> str:
    if role == "builder" and mode == "parallel-worktree":
        return "assigned by coordinator before launch"
    return "none"


def _validators_for_role(role: str, mode: str) -> tuple[str, ...]:
    common = ("git status --short",)
    if role == "builder":
        return common + ("uv run pytest <assigned-tests>",)
    if role == "verifier":
        return common + ("uv run pytest <relevant-tests>",)
    if role == "gap-checker":
        return common + ("check every Done when item against evidence",)
    if role == "explorer":
        return common + ("compare 3-5 options with evidence paths",)
    return common + ("cite discovered files, issues, and risks",)


if __name__ == "__main__":
    raise SystemExit(main())
