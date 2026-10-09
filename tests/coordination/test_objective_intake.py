from __future__ import annotations

from pathlib import Path

import yaml

from scripts.coordination.objective import (
    IssueBrief,
    classify_execution_mode,
    extract_objective_brief,
    render_lane_contracts,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_objective_issue_template_contains_required_fields() -> None:
    template_path = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "objective.yml"

    raw = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    fields = {
        item["id"]: item
        for item in raw["body"]
        if isinstance(item, dict) and "id" in item
    }

    assert raw["name"] == "Objective"
    assert raw["labels"] == ["gate:completeness", "gate:completeness-v2"]
    assert {
        "outcome",
        "done_when",
        "constraints_must_not",
        "out_of_scope",
        "return_format",
        "risk_tier",
    } <= set(fields)
    assert fields["risk_tier"]["attributes"]["options"] == ["A", "B", "C"]


def test_objective_markdown_template_alias_contains_required_fields() -> None:
    template_path = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "objective.md"
    text = template_path.read_text(encoding="utf-8")

    for field in (
        "Outcome",
        "Done when",
        "Constraints / must not",
        "Out of scope",
        "Return format",
        "Risk tier",
    ):
        assert f"### {field}" in text

    assert "Canonical form template: objective.yml" in text


def test_standard_role_agents_exist_with_alias_models() -> None:
    expected = {
        "scout": "haiku",
        "builder": "sonnet",
        "gap-checker": "sonnet",
        "explorer": "sonnet",
        "reporter": "sonnet",
        "verifier": "opus",
    }

    for role, model in expected.items():
        path = REPO_ROOT / ".claude" / "agents" / f"{role}.md"
        text = path.read_text(encoding="utf-8")
        meta = yaml.safe_load(text.split("---", 2)[1])

        assert meta["name"] == role
        assert meta["model"] == model
        assert "claude-" not in meta["model"]
        assert "gpt-" not in meta["model"]


def test_builder_agent_can_run_tdd_validators() -> None:
    path = REPO_ROOT / ".claude" / "agents" / "builder.md"
    text = path.read_text(encoding="utf-8")
    meta = yaml.safe_load(text.split("---", 2)[1])

    assert "Bash" in {tool.strip() for tool in meta["tools"].split(",")}


def test_readonly_bash_agents_explicitly_forbid_writes() -> None:
    for role in ("scout", "gap-checker", "verifier"):
        path = REPO_ROOT / ".claude" / "agents" / f"{role}.md"
        text = path.read_text(encoding="utf-8")

        assert "no writes" in text.lower()


def test_explorer_key_locations_do_not_include_planning_dir() -> None:
    text = (REPO_ROOT / ".claude" / "agents" / "explorer.md").read_text(
        encoding="utf-8"
    )

    assert ".planning/" not in text


def test_extract_objective_brief_from_issue_form_markdown() -> None:
    body = """### Outcome

    Ship the intake path.

    ### Done when

    - Template exists
    - Dry run renders contracts

    ### Constraints / must not

    Do not close issues.

    ### Out of scope

    No auto-merge.

    ### Return format

    PR plus issue comment.

    ### Risk tier

    B
    """

    brief = extract_objective_brief(10, "Objective sample", "CLOSED", body)

    assert brief.outcome == "Ship the intake path."
    assert "Template exists" in brief.done_when
    assert brief.risk_tier == "B"


def test_extract_objective_brief_from_bold_issue_body_labels() -> None:
    body = """Plan: docs/plans/example.md.

**Outcome:** a new issue can be written as an objective and run by one coordinator.

**Done when:**
- `.github/ISSUE_TEMPLATE/objective.md` exists.
- `/objective <issue#>` exists.

**Constraints / must not:**
- Coordinator alone owns integration, push and issue closeout.

**Out of scope:** retiring old agents.

**Return format:** PR + dry-run lane contracts pasted as a comment.

**Risk tier:** B
"""

    brief = extract_objective_brief(3989, "Objective P2", "OPEN", body)

    assert brief.outcome.startswith("a new issue")
    assert "objective.md" in brief.done_when
    assert "Coordinator alone owns integration" in brief.constraints_must_not
    assert brief.risk_tier == "B"


def test_dry_run_contracts_for_closed_issue_are_rendered_without_writes() -> None:
    brief = IssueBrief(
        number=3989,
        title="Objective P2",
        state="CLOSED",
        outcome="A new issue can be written as an objective.",
        done_when=(
            "- objective template exists\n"
            "- role agents exist\n"
            "- dry run on a closed issue produces lane contracts"
        ),
        constraints_must_not="Coordinator alone owns integration, push and closeout.",
        out_of_scope="No tier-aware gate changes.",
        return_format="PR + dry-run lane contracts pasted as a comment.",
        risk_tier="B",
    )

    contracts = render_lane_contracts(brief, dry_run=True)
    rendered = "\n".join(contract.to_markdown() for contract in contracts)

    assert classify_execution_mode(brief) == "parallel-readonly"
    assert "DRY RUN: no labels, comments, branches, commits, or issues were changed." in rendered
    assert "Issue: #3989" in rendered
    assert "Role: scout" in rendered
    assert "Role: gap-checker" in rendered
    assert "Role: verifier" in rendered
    assert "Coordinator owns integration, push, PR, and issue closeout." in rendered


def test_legacy_closed_issue_without_objective_fields_gets_dry_run_brief() -> None:
    brief = extract_objective_brief(
        3955,
        "Preserve launch preference and session closeout",
        "CLOSED",
        "Historical issue body without objective headings.",
    )

    assert brief.outcome == "Preserve launch preference and session closeout"
    assert "Legacy issue lacks Objective template fields" in brief.done_when
    assert brief.risk_tier == "A"


def test_partial_objective_issue_body_gets_dry_run_brief() -> None:
    body = """Parent RFC: #3997 (layer L1). Epic: #3993. Tier B.

**Mechanism:** `.github/ISSUE_TEMPLATE/objective.yml` plus `/objective <issue#>`.

**Done when:** template live in workspace-hub and synced to canonical repos.
"""

    brief = extract_objective_brief(3998, "Rewire L1: objective intake", "OPEN", body)

    assert brief.outcome == "Rewire L1: objective intake"
    assert "template live" in brief.done_when
    assert "partial Objective brief" in brief.constraints_must_not
    assert brief.risk_tier == "B"


def test_partial_objective_without_tier_defaults_to_a() -> None:
    body = """**Done when:** template live in workspace-hub and synced.
"""

    brief = extract_objective_brief(3998, "Rewire L1: objective intake", "OPEN", body)

    assert brief.risk_tier == "A"
