"""Tests for convert-agent-to-skill.py."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path, PureWindowsPath

import pytest

# Add parent dir to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import as module (hyphenated filename)
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "convert_agent_to_skill",
    Path(__file__).parent.parent / "convert-agent-to-skill.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

parse_frontmatter = _mod.parse_frontmatter
infer_category = _mod.infer_category
extract_description = _mod.extract_description
derive_skill_name = _mod.derive_skill_name
build_skill_content = _mod.build_skill_content
convert_single_file = _mod.convert_single_file
convert_directory = _mod.convert_directory
convert_agent = _mod.convert_agent
batch_convert = _mod.batch_convert
SKIP_FILES = _mod.SKIP_FILES
SKIP_DIRS = _mod.SKIP_DIRS


# ─── Frontmatter parsing ─────────────────────────────────────────────


class TestParseFrontmatter:
    def test_with_frontmatter(self):
        content = """---
name: test-agent
description: A test agent
model: sonnet
---
# Agent content
Body text here.
"""
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "test-agent"
        assert meta["description"] == "A test agent"
        assert meta["model"] == "sonnet"
        assert "# Agent content" in body
        assert "Body text here." in body

    def test_without_frontmatter(self):
        content = """# Just markdown
No frontmatter here.
"""
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert content == body

    def test_empty_content(self):
        meta, body = parse_frontmatter("")
        assert meta == {}
        assert body == ""

    def test_frontmatter_with_quoted_values(self):
        content = """---
name: "quoted-name"
description: 'single-quoted'
---
Body"""
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "quoted-name"
        assert meta["description"] == "single-quoted"

    def test_frontmatter_missing_closing(self):
        content = """---
name: broken
No closing marker.
"""
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == content


# ─── Category inference ───────────────────────────────────────────────


class TestInferCategory:
    @pytest.mark.parametrize(
        "path,expected",
        [
            ("agents/orcaflex/README.md", "engineering"),
            ("agents/orcawave/damping.md", "engineering"),
            ("agents/aqwa/README.md", "engineering"),
            ("agents/freecad/README.md", "engineering"),
            ("agents/cad-engineering/README.md", "engineering"),
            ("agents/gmsh/README.md", "engineering"),
            ("agents/cathodic-protection.md", "engineering"),
            ("agents/github/pr-workflow.md", "development"),
            ("agents/testing/unit/runner.md", "development"),
            ("agents/sparc/design.md", "development"),
            ("agents/data/ml/model.md", "data"),
            ("agents/documentation/api.md", "documentation"),
            ("agents/unknown/thing.md", "general"),
        ],
    )
    def test_category_inference(self, path: str, expected: str):
        assert infer_category(path) == expected


# ─── Description extraction ──────────────────────────────────────────


class TestExtractDescription:
    def test_from_metadata(self):
        meta = {"description": "Agent for CP systems"}
        body = "Some body text"
        assert extract_description(meta, body) == "Agent for CP systems"

    def test_from_body_first_paragraph(self):
        meta = {}
        body = """# Title

You are an expert in engineering.
More details here."""
        assert extract_description(meta, body) == "You are an expert in engineering."

    def test_long_description_truncated(self):
        meta = {"description": "x" * 250}
        body = ""
        desc = extract_description(meta, body)
        assert len(desc) <= 200
        assert desc.endswith("...")

    def test_fallback_default(self):
        meta = {}
        body = "# Only headings\n```code```"
        desc = extract_description(meta, body)
        assert desc == "Converted from Claude agent file"


# ─── Skill name derivation ───────────────────────────────────────────


class TestDeriveSkillName:
    def test_from_metadata(self):
        meta = {"name": "my-agent"}
        assert derive_skill_name(Path("foo.md"), meta) == "my-agent"

    def test_from_file_path(self):
        meta = {}
        assert derive_skill_name(Path("agents/cool-agent.md"), meta) == "cool-agent"

    def test_from_directory_path(self, tmp_path):
        d = tmp_path / "orcaflex"
        d.mkdir()
        meta = {}
        assert derive_skill_name(d, meta) == "orcaflex"


# ─── Build skill content ─────────────────────────────────────────────


class TestBuildSkillContent:
    def test_basic_build(self):
        content = build_skill_content(
            "test-agent", "engineering", "A test skill", "Body here."
        )
        assert "name: test-agent" in content
        assert "category: engineering" in content
        assert "description: A test skill" in content
        assert "type: reference" in content
        assert "scripts_exempt: true" in content
        assert "# Test Agent" in content
        assert "Body here." in content

    def test_with_tags(self):
        content = build_skill_content(
            "tagged", "data", "Tagged skill", "Body.", tags=["tag1", "tag2"]
        )
        assert "tags: [tag1, tag2]" in content


# ─── Single file conversion ──────────────────────────────────────────


class TestConvertSingleFile:
    def test_converts_agent_file(self, tmp_path):
        agent = tmp_path / "test-agent.md"
        agent.write_text("""---
name: test-agent
description: Test agent description
---
# Test Agent

You are a test agent.""", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        result = convert_single_file(agent, output_dir)

        assert result is not None
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "name: test-agent" in content
        assert "You are a test agent." in content

    def test_dry_run_creates_no_files(self, tmp_path):
        agent = tmp_path / "test-agent.md"
        agent.write_text("# Simple agent\nBody text.", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        result = convert_single_file(agent, output_dir, dry_run=True)

        assert result is not None  # Returns path
        assert not result.exists()  # But doesn't create it

    def test_skip_existing(self, tmp_path):
        agent = tmp_path / "test-agent.md"
        agent.write_text("# Agent\nBody.", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        skill_dir = output_dir / "test-agent"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("existing content", encoding="utf-8", newline="\n")

        result = convert_single_file(agent, output_dir)
        assert result is None
        assert skill_file.read_text(encoding="utf-8") == "existing content"

    def test_skip_excluded_files(self, tmp_path):
        agent = tmp_path / "todo.md"
        agent.write_text("# Todo\nSome tasks.", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        result = convert_single_file(agent, output_dir)
        assert result is None


# ─── Directory conversion ────────────────────────────────────────────


class TestConvertDirectory:
    def test_concatenates_md_files(self, tmp_path):
        agent_dir = tmp_path / "orcaflex-agent"
        agent_dir.mkdir()
        (agent_dir / "README.md").write_text("""---
name: orcaflex-agent
description: OrcaFlex agent
---
# OrcaFlex Agent

Main content here.""", encoding="utf-8", newline="\n")
        (agent_dir / "BATCH_PROCESSING.md").write_text("""# Batch Processing

Batch notes here.""", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        results = convert_directory(agent_dir, output_dir)

        assert len(results) == 1
        content = results[0].read_text(encoding="utf-8")
        assert "name: orcaflex-agent" in content
        assert "Main content here." in content
        assert "Batch notes here." in content

    def test_empty_directory(self, tmp_path):
        agent_dir = tmp_path / "empty-agent"
        agent_dir.mkdir()

        output_dir = tmp_path / "skills"
        results = convert_directory(agent_dir, output_dir)
        assert results == []

    def test_skips_todo_files(self, tmp_path):
        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        (agent_dir / "README.md").write_text("# Agent\nMain.", encoding="utf-8", newline="\n")
        (agent_dir / "todo.md").write_text("# Todo\nSkip this.", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        results = convert_directory(agent_dir, output_dir)

        assert len(results) == 1
        content = results[0].read_text(encoding="utf-8")
        assert "Skip this." not in content


# ─── Batch conversion ────────────────────────────────────────────────


class TestBatchConvert:
    def test_batch_with_include_filter(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Create dirs
        for name in ["orcaflex", "testing", "swarm"]:
            d = agents_dir / name
            d.mkdir()
            (d / "README.md").write_text(f"# {name}\nContent for {name}.", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        include = {"orcaflex", "testing"}
        results = batch_convert(agents_dir, output_dir, include=include)

        assert len(results) == 2
        names = {r.parent.name for r in results}
        assert "orcaflex" in names
        assert "testing" in names
        assert "swarm" not in names

    def test_batch_skips_excluded_dirs(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        for name in ["core", "swarm", "hive-mind", "github"]:
            d = agents_dir / name
            d.mkdir()
            (d / "README.md").write_text(f"# {name}\nContent.", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        results = batch_convert(agents_dir, output_dir)

        names = {r.parent.name for r in results}
        assert "core" in names
        assert "github" in names
        assert "swarm" not in names
        assert "hive-mind" not in names

    def test_batch_handles_top_level_md_files(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        (agents_dir / "cathodic-protection.md").write_text("""---
name: cathodic-protection
description: CP expert
---
# CP Agent
Body.""", encoding="utf-8", newline="\n")

        output_dir = tmp_path / "skills"
        results = batch_convert(agents_dir, output_dir)

        assert len(results) == 1
        assert results[0].parent.name == "cathodic-protection"

    def test_batch_nonexistent_dir(self, tmp_path):
        results = batch_convert(tmp_path / "nope", tmp_path / "out")
        assert results == []


# Hand-authored example: the frontmatter fields and version follow the existing
# build_skill_content format; the title and body are transcribed independently.
PENDING_SOURCE = """---
name: sample-agent
description: A checklist example
---
# Checklist

Follow the checklist.
"""
EXPECTED_DRAFT = """---
name: sample-agent
version: 1.0.0
category: general
description: A checklist example
type: reference
tags: []
scripts_exempt: true
---
# Sample Agent

# Checklist

Follow the checklist.
"""


@pytest.fixture
def pending_example(tmp_path, monkeypatch):
    # Relative inputs keep category inference independent of the temporary root.
    monkeypatch.chdir(tmp_path)
    agents = Path("agents")
    agents.mkdir()
    source = agents / "sample-agent.md"
    source.write_text(PENDING_SOURCE, encoding="utf-8", newline="\n")
    output = Path("skills")
    draft = output / "sample-agent" / "SKILL.md"
    return agents, source, output, draft


def test_pending_agents_detects_missing_and_changed(pending_example):
    agents, source, output, draft = pending_example
    assert batch_convert(agents, output, dry_run=True, pending_only=True) == [draft]
    assert not output.exists()

    draft.parent.mkdir(parents=True)
    draft.write_text(EXPECTED_DRAFT, encoding="utf-8", newline="\n")
    # Different timestamps do not make identical rendered content pending.
    os.utime(source, None)
    assert batch_convert(agents, output, dry_run=True, pending_only=True) == []

    source.write_text(PENDING_SOURCE.replace("Follow", "Review"), encoding="utf-8", newline="\n")
    # Equal timestamps do not hide a changed source (use the existing draft time).
    stamp = draft.stat()
    os.utime(source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert batch_convert(agents, output, dry_run=True, pending_only=True) == [draft]
    assert draft.read_text(encoding="utf-8") == EXPECTED_DRAFT


@pytest.mark.parametrize("existing", [False, True])
def test_pending_preview_is_read_only(pending_example, tmp_path, monkeypatch, existing):
    agents, source, output, draft = pending_example
    if existing:
        draft.parent.mkdir(parents=True)
        draft.write_text("Draft awaiting review\n", encoding="utf-8", newline="\n")

    def snapshot():
        return {
            path.relative_to(tmp_path): (
                path.read_bytes() if path.is_file() else None,
                path.stat().st_mtime_ns,
            )
            for path in tmp_path.rglob("*")
        }

    before = snapshot()
    monkeypatch.setattr(sys, "argv", [
        "convert-agent-to-skill.py", "--batch", str(agents), "--output", str(output),
        "--pending-only", "--dry-run",
    ])
    assert _mod.main() == 0  # argparse success exit convention.
    assert snapshot() == before


def test_pending_scan_is_deterministic(pending_example, caplog):
    agents, source, output, draft = pending_example
    # Deliberately create entries in reverse lexical order.
    (agents / "zeta.md").write_text("# Zeta\nZeta body.", encoding="utf-8", newline="\n")
    (agents / "alpha.md").write_text("# Alpha\nAlpha body.", encoding="utf-8", newline="\n")
    expected = [output / "alpha" / "SKILL.md", draft, output / "zeta" / "SKILL.md"]
    with caplog.at_level(logging.INFO):
        assert batch_convert(agents, output, dry_run=True, pending_only=True) == expected
        first_log = caplog.text
        caplog.clear()
        assert batch_convert(agents, output, dry_run=True, pending_only=True) == expected
        assert caplog.text == first_log


def test_pending_scan_preserves_exclusions(pending_example):
    agents, source, output, draft = pending_example
    for name in sorted(SKIP_FILES):
        (agents / name).write_text("Excluded content", encoding="utf-8", newline="\n")
    for name in sorted(SKIP_DIRS):
        excluded = agents / name
        excluded.mkdir()
        (excluded / "README.md").write_text("Excluded content", encoding="utf-8", newline="\n")
    (agents / "notes.txt").write_text("Not markdown", encoding="utf-8", newline="\n")
    empty = agents / "empty"
    empty.mkdir()
    (empty / "notes.txt").write_text("Not markdown", encoding="utf-8", newline="\n")
    assert batch_convert(agents, output, dry_run=True, pending_only=True) == [draft]
    assert batch_convert(agents, output, include={"notes"},
                         dry_run=True, pending_only=True) == []


def test_pending_conversion_writes_only_selected_output(pending_example, monkeypatch):
    agents, source, output, draft = pending_example
    draft.parent.mkdir(parents=True)
    draft.write_text("Draft awaiting review\n", encoding="utf-8", newline="\n")
    other_source = agents / "other.md"
    other_source.write_text("# Other\nOther body.", encoding="utf-8", newline="\n")
    other_draft = output / "other" / "SKILL.md"
    other_draft.parent.mkdir(parents=True)
    other_draft.write_text("Preserved draft\n", encoding="utf-8", newline="\n")
    (agents / "unselected.md").write_text("# New\nNew body.", encoding="utf-8", newline="\n")
    before = {path: path.read_bytes() for path in agents.rglob("*") if path.is_file()}
    monkeypatch.setattr(sys, "argv", [
        "convert-agent-to-skill.py", "--batch", str(agents), "--output", str(output),
        "--include", "sample-agent", "--pending-only",
    ])
    assert _mod.main() == 0  # argparse success exit convention.
    assert draft.read_text(encoding="utf-8") == EXPECTED_DRAFT
    assert other_draft.read_text(encoding="utf-8") == "Preserved draft\n"
    assert sorted(output.rglob("SKILL.md")) == sorted([draft, other_draft])
    assert {path: path.read_bytes() for path in before} == before
    # The selected draft is now current and a second conversion skips it.
    assert batch_convert(agents, output, include={"sample-agent"}, pending_only=True) == []


def test_existing_conversion_defaults_are_preserved(pending_example):
    agents, source, output, draft = pending_example
    assert batch_convert(agents, output) == [draft]
    assert draft.read_text(encoding="utf-8") == EXPECTED_DRAFT
    source.write_text(PENDING_SOURCE.replace("Follow", "Review"), encoding="utf-8", newline="\n")
    assert batch_convert(agents, output) == []
    assert draft.read_text(encoding="utf-8") == EXPECTED_DRAFT
    assert batch_convert(agents, output, dry_run=True) == [draft]


def test_pending_directory_uses_existing_rendering(pending_example):
    agents, source, output, draft = pending_example
    bundle = agents / "bundle"
    bundle.mkdir()
    (bundle / "README.md").write_text(PENDING_SOURCE, encoding="utf-8", newline="\n")
    notes = bundle / "notes.md"
    notes.write_text("# Notes\nExtra guidance.", encoding="utf-8", newline="\n")
    (bundle / "todo.md").write_text("Excluded content", encoding="utf-8", newline="\n")
    # Hand-concatenated from the example above and the documented source separator.
    expected = EXPECTED_DRAFT + "\n\n---\n\n## Source: notes.md\n\n# Notes\nExtra guidance.\n"
    assert convert_agent(bundle, output, pending_only=True) == [draft]
    assert draft.read_text(encoding="utf-8") == expected
    assert convert_agent(bundle, output, dry_run=True, pending_only=True) == []
    notes.write_text("# Notes\nRevised guidance.", encoding="utf-8", newline="\n")
    assert convert_agent(bundle, output, dry_run=True, pending_only=True) == [draft]
    assert draft.read_text(encoding="utf-8") == expected


def test_pending_single_input_cli(pending_example, monkeypatch, caplog):
    agents, source, output, draft = pending_example
    monkeypatch.setattr(sys, "argv", [
        "convert-agent-to-skill.py", "--input", str(source), "--output", str(output),
        "--pending-only", "--dry-run",
    ])
    with caplog.at_level(logging.INFO):
        assert _mod.main() == 0  # argparse success exit convention.
    assert "MISSING" in caplog.text
    assert draft.as_posix() in caplog.text
    assert not output.exists()


def test_pending_reports_changed_draft(pending_example, caplog):
    agents, source, output, draft = pending_example
    draft.parent.mkdir(parents=True)
    # CRLF is a byte-level content difference even with the same rendered text.
    draft.write_bytes(EXPECTED_DRAFT.replace("\n", "\r\n").encode("utf-8"))
    with caplog.at_level(logging.INFO):
        assert batch_convert(agents, output, dry_run=True, pending_only=True) == [draft]
    assert "CHANGED" in caplog.text
    assert draft.as_posix() in caplog.text


@pytest.mark.parametrize("directory", [False, True], ids=["file", "directory"])
@pytest.mark.parametrize("pending_only", [False, True], ids=["default", "pending"])
def test_conversion_is_current_with_windows_newlines(
    pending_example, monkeypatch, directory, pending_only,
):
    agents, source, output, draft = pending_example
    if directory:
        bundle = agents / "bundle"
        bundle.mkdir()
        (bundle / "README.md").write_text(
            PENDING_SOURCE, encoding="utf-8", newline="\n",
        )
        source = bundle

    original_open = Path.open

    def windows_open(path, mode="r", buffering=-1, encoding=None,
                     errors=None, newline=None):
        # Model Windows' default text translation on any operating system.
        if "w" in mode and "b" not in mode and newline is None:
            newline = "\r\n"
        return original_open(
            path, mode, buffering, encoding=encoding, errors=errors, newline=newline,
        )

    monkeypatch.setattr(Path, "open", windows_open)
    assert convert_agent(source, output, pending_only=pending_only) == [draft]
    assert draft.read_bytes() == EXPECTED_DRAFT.encode("utf-8")
    assert convert_agent(source, output, dry_run=True, pending_only=True) == []


def test_pending_diagnostics_use_forward_slashes(monkeypatch, caplog):
    draft = PureWindowsPath("skills/sample/SKILL.md")
    monkeypatch.setattr(PureWindowsPath, "exists", lambda self: False, raising=False)
    with caplog.at_level(logging.INFO):
        assert _mod.is_pending_draft(draft, "content")
    assert "MISSING: skills/sample/SKILL.md" in caplog.text


def test_directory_source_uses_forward_slashes(pending_example, monkeypatch):
    agents, source, output, draft = pending_example
    bundle = agents / "bundle"
    (bundle / "nested").mkdir(parents=True)
    (bundle / "README.md").write_text(PENDING_SOURCE, encoding="utf-8", newline="\n")
    (bundle / "nested" / "notes.md").write_text(
        "Extra guidance.", encoding="utf-8", newline="\n",
    )
    original_relative_to = Path.relative_to

    def windows_relative_to(path, *other):
        return PureWindowsPath(*original_relative_to(path, *other).parts)

    monkeypatch.setattr(Path, "relative_to", windows_relative_to)
    assert convert_agent(bundle, output) == [draft]
    assert "## Source: nested/notes.md" in draft.read_text(encoding="utf-8")
