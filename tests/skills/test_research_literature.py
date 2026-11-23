# ABOUTME: Validates research-literature skill file structure and frontmatter
# ABOUTME: Part of WRK-1181 — research and literature gathering skill

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
import yaml


SKILL_PATH = ".claude/skills/data/research-literature/SKILL.md"

# Contract basis: docs/plans/2026-04-20-issue-2419-skill-markdown-contract-drift.md,
# Resource Intelligence Summary; SKILL.md, "8-Step Workflow"; and
# references/workflow-steps.md, "Step 1" through "Step 8".
WORKFLOW_STEPS = (
    "Query the Standards Ledger",
    "Query the Document Index",
    "Cross-Reference Capability Map",
    "Produce the Research Brief",
    "Search University & Academic Resources",
    "Document Download Tasks",
    "Deep Online Research",
    "Download Script Generation",
)


def _resolve_reference(document, name, skill_root):
    match = re.search(rf"\[{re.escape(name)}\]\(([^)\n]+)\)", document.read_text())
    assert match, f"Missing reference link: {name}"
    target = (document.parent / match.group(1)).resolve()
    assert target.is_relative_to(skill_root.resolve()), (
        f"Reference escapes skill tree: {name}"
    )
    assert target.is_file(), f"Missing reference file: {name}"
    return target


def _validate_sections(skill_path):
    content = skill_path.read_text()
    # The plan records the retired layout; SKILL.md now owns the overview and AC.
    for section in ("## Inputs", "## 8-Step Workflow", "## AC Checklist"):
        assert section in content.splitlines(), f"Missing section: {section}"
    workflow = content.split("## 8-Step Workflow\n", 1)[1].split("\n## ", 1)[0]
    steps = re.findall(r"^\d+\. .+$", workflow, re.MULTILINE)
    assert steps == [
        f"{number}. {name}"
        for number, name in enumerate(WORKFLOW_STEPS, start=1)
    ], "Missing or reordered workflow step"
    checklist = content.split("## AC Checklist\n", 1)[1].split("\n## ", 1)[0]
    assert re.search(r"^- \[ \] \S", checklist, re.MULTILINE), "Empty AC checklist"

    # Detailed headings and the brief template moved into the linked references.
    workflow_path = _resolve_reference(skill_path, "workflow-steps.md", skill_path.parent)
    template_path = _resolve_reference(skill_path, "templates.md", skill_path.parent)
    headings = re.findall(r"^## Step .+$", workflow_path.read_text(), re.MULTILINE)
    assert headings == [
        f"## Step {number} — {name}"
        for number, name in enumerate(WORKFLOW_STEPS, start=1)
    ], "Missing or reordered detailed workflow step"
    assert "## Research Brief Template" in template_path.read_text().splitlines()


def _validate_references(skill_path):
    # Plan #2419 and SKILL.md's links replace top-level script-string checks.
    workflow_path = _resolve_reference(skill_path, "workflow-steps.md", skill_path.parent)
    template_path = _resolve_reference(skill_path, "templates.md", skill_path.parent)
    # references/workflow-steps.md, Step 4, also links the shared template.
    assert (
        _resolve_reference(workflow_path, "templates.md", skill_path.parent)
        == template_path
    )
    # Preserve the data-source checks at their new home: detailed Steps 1–3.
    workflow = workflow_path.read_text()
    for reference in ("query-ledger.py", "index.jsonl", "capability-map"):
        assert reference in workflow, f"Missing workflow reference: {reference}"


@pytest.fixture
def skill_tree(tmp_path):
    """Copy only contract documents; all mutations stay in temporary storage."""
    source = Path(SKILL_PATH)
    skill_path = tmp_path / "skill" / source.name
    skill_path.parent.mkdir()
    skill_path.write_text(source.read_text())
    for name in ("workflow-steps.md", "templates.md"):
        reference = _resolve_reference(source, name, source.parent)
        target = skill_path.parent / "references" / name
        target.parent.mkdir(exist_ok=True)
        target.write_text(reference.read_text())
    return skill_path


def test_skill_file_exists():
    assert os.path.exists(SKILL_PATH), f"Skill file missing: {SKILL_PATH}"


def test_skill_frontmatter():
    with open(SKILL_PATH) as f:
        content = f.read()
    parts = content.split("---", 2)
    assert len(parts) >= 3, "Missing YAML frontmatter delimiters"
    meta = yaml.safe_load(parts[1])
    assert meta["name"] == "research-literature"
    assert "triggers" in meta
    assert len(meta["triggers"]) >= 3


def test_skill_has_required_sections():
    _validate_sections(Path(SKILL_PATH))


def test_skill_references_existing_scripts():
    _validate_references(Path(SKILL_PATH))


@pytest.mark.parametrize("step", WORKFLOW_STEPS)
@pytest.mark.parametrize("document", ("SKILL.md", "references/workflow-steps.md"))
def test_missing_workflow_step_is_rejected(skill_tree, step, document):
    _validate_sections(skill_tree)
    target = skill_tree.parent / document
    content = target.read_text()
    target.write_text("\n".join(
        line for line in content.splitlines() if not line.endswith(step)
    ))
    with pytest.raises(AssertionError, match="workflow step"):
        _validate_sections(skill_tree)


@pytest.mark.parametrize(
    "document, reference",
    (
        ("SKILL.md", "references/workflow-steps.md"),
        ("SKILL.md", "references/templates.md"),
        ("references/workflow-steps.md", "templates.md"),
    ),
)
def test_broken_reference_is_rejected(skill_tree, document, reference):
    _validate_references(skill_tree)
    target = skill_tree.parent / document
    content = target.read_text()
    target.write_text(content.replace(f"]({reference})", "](missing.md)"))
    with pytest.raises(AssertionError, match="Missing reference file"):
        _validate_references(skill_tree)


def test_reference_outside_skill_tree_is_rejected(skill_tree, tmp_path):
    _validate_references(skill_tree)
    outside = tmp_path / "outside.md"
    outside.write_text("Existing file outside the skill tree")
    content = skill_tree.read_text()
    skill_tree.write_text(content.replace(
        "](references/workflow-steps.md)", f"]({outside})"
    ))
    with pytest.raises(AssertionError, match="Reference escapes skill tree"):
        _validate_references(skill_tree)


def test_skill_version():
    with open(SKILL_PATH) as f:
        content = f.read()
    parts = content.split("---", 2)
    meta = yaml.safe_load(parts[1])
    assert "version" in meta
    assert meta["version"] == "1.0.0"
