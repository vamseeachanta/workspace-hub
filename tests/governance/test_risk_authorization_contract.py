"""Bounded source-contract regressions; provider trials establish separate behavior."""
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[2]
SHARED = "config/agents/SHARED_SOUL.md"
SURFACES = ["AGENTS.md", SHARED, "docs/standards/HARD-STOP-POLICY.md",
    "docs/plans/README.md", "docs/standards/PARALLEL_FIRST_EXECUTION.md",
    ".claude/skills/coordination/issue-planning-mode/SKILL.md",
    ".claude/skills/coordination/gh-work-planning/SKILL.md",
    ".claude/skills/coordination/engineering-issue-workflow/SKILL.md"]
RUNTIMES = ["config/agents/" + name for name in ["hermes/SOUL.runtime.md",
    "claude/SOUL.runtime.md", "codex/SOUL.runtime.md", "codex/AGENTS.runtime.md",
    "gemini/SOUL.runtime.md", "agy/SOUL.runtime.md"]]
OPERATION_CLASSES = {
    "read-only", "routine-reversible", "substantial", "irreversible", "owner-held", "unknown",
}


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def authorization_rows(text):
    section = text.split("# Authorization", 1)[1].split("\n# ", 1)[0]
    header = "| Operation class | Required authority | Route |"
    table = section.split(header, 1)[1].strip().split("\n\n", 1)[0]
    rows = {}
    for line in table.splitlines()[1:]:
        operation, authority, route = (cell.strip() for cell in line.strip("|").split("|"))
        assert operation not in rows
        rows[operation] = (authority, route)
    return rows


def test_shared_authority_routes_are_complete_and_do_not_mint_approval():
    rows = authorization_rows(read(SHARED))
    assert set(rows) == OPERATION_CLASSES
    assert "standing authorization" in rows["routine-reversible"][0].lower()
    assert "proceed" in rows["routine-reversible"][1].lower()
    assert "task request" in rows["substantial"][0].lower()
    authority, route = rows["irreversible"]
    assert authority == "The team decides"
    for safeguard in ("before running it", "Back up first", "Keep the machine reachable",
                      "Never put tokens or secrets anywhere", "stay in force"):
        assert safeguard in route
    authority, route = rows["owner-held"]
    assert authority.startswith("The owner") and authority.endswith("only")
    assert "Client-facing emails and messages" in route and "spending money" in route
    assert "context" in " ".join(rows["unknown"]).lower()


@pytest.mark.parametrize("path", SURFACES)
def test_primary_surfaces_route_to_shared_standing_authority(path):
    text = read(path)
    assert "SHARED_SOUL.md" in text
    assert "standing authorization" in text.lower()


@pytest.mark.parametrize("path", RUNTIMES)
def test_every_generated_runtime_contains_exact_shared_source(path):
    text = read(path)
    assert read(SHARED) in text
    assert set(authorization_rows(text)) == OPERATION_CLASSES


def test_agent_entry_fits_cap_without_losing_control_references():
    text = read("AGENTS.md")
    assert len(text.splitlines()) <= 20
    for reference in ["SHARED_SOUL.md", "HARD-STOP-POLICY.md", "AI_REVIEW_ROUTING_POLICY.md",
                      "PARALLEL_FIRST_EXECUTION.md", "agent-data-handling-contract.md",
                      "MODEL_RELEASE_READINESS_CONTRACT.md", "MODEL_RELEASE_UPGRADE_PLAYBOOK.md"]:
        assert reference in text
    assert "TDD" in text and "secrets" in text.lower()
    assert "task request authorizes implementation within scope" in text
    assert "no separate plan approval is required" in text


def test_shared_mandatory_controls_remain_explicit():
    text = read(SHARED)
    for invariant in ["TDD mandatory", "Adversarial review at BOTH stages",
                      "Never self-label", "docs/standards/FINAL_REPORT_VERIFICATION.md",
                      "Security baseline", "Pre-completion cleanup audit gate",
                      "Codes and standards we hold may be committed to private repositories"]:
        assert invariant in text


@pytest.mark.parametrize("path,forbidden", [
    ("docs/standards/HARD-STOP-POLICY.md", "Implementation starts only after the plan comment is posted"),
    ("docs/standards/HARD-STOP-POLICY.md", "Cross-review can be waived for trivial changes"),
    ("docs/standards/HARD-STOP-POLICY.md", "**Pure configuration change**: no engineering logic changes (auto-detected)"),
    ("docs/standards/HARD-STOP-POLICY.md", "Agent MUST use the `clarify` tool"),
    (".claude/skills/coordination/issue-planning-mode/SKILL.md", "Only after `status:plan-approved` label AND"),
    (".claude/skills/coordination/issue-planning-mode/SKILL.md", "remove or downgrade the stale approval label unless"),
    (".claude/skills/coordination/gh-work-planning/SKILL.md", "on approve: remove `status:plan-review`, add `status:plan-approved`"),
    (".claude/skills/coordination/gh-work-planning/SKILL.md", "approve -> set `status:plan-approved`, then execution may begin"),
    (".claude/skills/coordination/engineering-issue-workflow/SKILL.md", "brief plan, still requires approval"),
])
def test_reproduced_unsafe_or_blanket_instructions_do_not_return(path, forbidden):
    assert forbidden not in read(path)


def test_handoffs_and_optional_assessment_do_not_become_authority():
    text = read(SHARED)
    assert "handoff" in text.lower() and "provenance" in text.lower()
    assert "workflow_decision.py" in text
    assert "not a mandatory per-tool" in text
    assert "Legacy enforcement" in text
    normalized = " ".join(text.split())
    for clause in [
        "A reference in agent-written JSON, a local marker, a label alone, a review verdict or a handoff does not authenticate that authority.",
        "Cross-session handoffs carry context to verify, not independent approval.",
        "Reuse established approval within its unchanged scope.",
        "Material scope changes require matching task authority; ask only when the new scope is not already authorized.",
        "Never infer approval from elapsed time, overnight scheduling or posting a plan.",
    ]:
        assert clause in normalized


def test_historical_plan_index_rows_are_retained():
    text = read("docs/plans/README.md")
    rows = [line for line in text.splitlines() if line.startswith("|") and re.search(r"20\d\d-\d\d-\d\d", line)]
    assert rows, "Historical plan index must remain present"
    assert any("2026-09-12-issue-3615-shared-risk-workflow.html" in row for row in rows)


def test_engineering_step_numbers_match_headings_and_delegation():
    text = read(SURFACES[-1])
    box = re.findall(r"^STEP (\d+):", text, re.M)
    headings = re.findall(r"^### STEP (\d+):", text, re.M)
    assert box == headings == [str(n) for n in range(1, 8)]
    assert "Steps 1-4" in text and "STEP 5 (Implement, TDD)" in text


def test_onboarding_step_numbers_match_headings():
    text = read("docs/plans/README.md")
    box = text.split("## The Workflow (Step by Step)", 1)[1].split("```", 2)[1]
    assert re.findall(r"^(\d+)\.", box, re.M) == re.findall(r"^### Step (\d+):", text, re.M)


def test_entry_retains_concurrent_claim_and_handoff_requirements():
    text = read("AGENTS.md")
    for literal in ["claim.py", "BLOCKED if held", "handoff before stopping"]:
        assert literal in text


def test_entry_reference_targets_exist():
    text = read("AGENTS.md")
    owner = "fleet-ops"
    playbook = "docs/newsletter-playbook.md"
    external = f"{owner} {playbook}"
    assert external in text
    owner_checkout = ROOT.parent / owner
    if owner_checkout.is_dir():
        assert (owner_checkout / playbook).is_file(), external
    for relative in re.findall(r"(?:config|docs)/[A-Za-z0-9_./-]+\.md", text.replace(external, "")):
        assert (ROOT / relative).is_file(), relative
