#!/usr/bin/env python3
"""Tests for split-oversized-skill.py."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parent.parent / "split-oversized-skill.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
    )


def _make_large_skill(tmpdir: Path, lines: int = 1200) -> Path:
    """Generate a large SKILL.md fixture with known H2/H3 structure."""
    skill_dir = tmpdir / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_path = skill_dir / "SKILL.md"

    sections = []
    sections.append("---")
    sections.append("name: large-test-skill")
    sections.append("description: A test skill with many sections to validate splitting behavior across H2 and H3 boundaries.")
    sections.append("version: 1.0.0")
    sections.append("category: engineering")
    sections.append("tags: [test]")
    sections.append("scripts_exempt: true")
    sections.append("---")
    sections.append("")
    sections.append("# Large Test Skill")
    sections.append("")
    sections.append("## When to Use")
    sections.append("")
    sections.append("- For testing the split script")
    sections.append("")
    sections.append("## Prerequisites")
    sections.append("")
    sections.append("- Python 3.10+")
    sections.append("")
    sections.append("## Core Capabilities")
    sections.append("")

    # Generate H3 sub-sections to reach target line count
    lines_per_section = (lines - 40) // 4
    for i in range(4):
        sections.append(f"### Capability {i + 1}")
        sections.append("")
        sections.append(f"This is capability {i + 1} documentation.")
        sections.append("")
        sections.append("```python")
        sections.append(f"# Example for capability {i + 1}")
        sections.append(f"from cap{i + 1} import Cap{i + 1}")
        sections.append(f"c = Cap{i + 1}()")
        sections.append("c.run()")
        sections.append("```")
        sections.append("")
        for j in range(lines_per_section - 10):
            sections.append(f"Detail line {j + 1} for capability {i + 1}.")
        sections.append("")

    sections.append("## Integration Examples")
    sections.append("")
    sections.append("```bash")
    sections.append("python -m test_skill --run")
    sections.append("```")
    sections.append("")
    for j in range(30):
        sections.append(f"Integration detail line {j + 1}.")
    sections.append("")
    sections.append("## Best Practices")
    sections.append("")
    for j in range(20):
        sections.append(f"- Best practice {j + 1}: do good things.")
    sections.append("")
    sections.append("## Troubleshooting")
    sections.append("")
    for j in range(15):
        sections.append(f"- Issue {j + 1}: check the logs.")
    sections.append("")
    sections.append("## Related Skills")
    sections.append("")
    sections.append("- [other-skill](../other-skill/SKILL.md)")

    skill_path.write_text("\n".join(sections), encoding="utf-8")
    return skill_path


def _make_marginal_skill(tmpdir: Path) -> Path:
    """Generate a 250-line skill for --trim mode testing."""
    skill_dir = tmpdir / "marginal-skill"
    skill_dir.mkdir(parents=True)
    skill_path = skill_dir / "SKILL.md"

    lines = []
    lines.append("---")
    lines.append("name: marginal-test-skill")
    lines.append("description: A marginally oversized skill for trim-mode testing with appendix extraction.")
    lines.append("version: 1.0.0")
    lines.append("category: engineering")
    lines.append("scripts_exempt: true")
    lines.append("---")
    lines.append("")
    lines.append("# Marginal Test Skill")
    lines.append("")
    lines.append("## When to Use")
    lines.append("")
    lines.append("- For trim testing")
    lines.append("")
    lines.append("## Core Capabilities")
    lines.append("")
    for j in range(100):
        lines.append(f"Core content line {j + 1}.")
    lines.append("")
    lines.append("## Best Practices")
    lines.append("")
    for j in range(40):
        lines.append(f"- Practice {j + 1}.")
    lines.append("")
    lines.append("## Troubleshooting")
    lines.append("")
    for j in range(40):
        lines.append(f"- Troubleshooting item {j + 1}.")
    lines.append("")
    lines.append("## Integration Examples")
    lines.append("")
    for j in range(30):
        lines.append(f"Integration line {j + 1}.")
    lines.append("")
    lines.append("## Related Skills")
    lines.append("")
    lines.append("- [other](../other/SKILL.md)")

    skill_path.write_text("\n".join(lines), encoding="utf-8")
    return skill_path


class TestDryRun:
    def test_dry_run_does_not_write(self):
        """--dry-run should preview changes without creating files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_large_skill(Path(tmpdir))
            result = _run(["--dry-run", str(skill_path)])
            assert result.returncode == 0
            # No sub-skill directories should be created
            skill_dir = skill_path.parent
            subdirs = [d for d in skill_dir.iterdir() if d.is_dir()]
            assert len(subdirs) == 0
            # But output should mention what would be created
            assert "would create" in result.stdout.lower() or "dry run" in result.stdout.lower()

    def test_dry_run_shows_planned_splits(self):
        """--dry-run should list the sub-skills that would be created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_large_skill(Path(tmpdir))
            result = _run(["--dry-run", str(skill_path)])
            assert result.returncode == 0
            # Should mention sub-skill names
            assert "core-capabilities" in result.stdout.lower() or "capability" in result.stdout.lower()


class TestSplitFull:
    def test_split_creates_hub_under_200_lines(self):
        """After split, hub SKILL.md should be under 200 lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_large_skill(Path(tmpdir))
            result = _run([str(skill_path)])
            assert result.returncode == 0
            hub_content = skill_path.read_text(encoding="utf-8")
            hub_lines = len(hub_content.splitlines())
            assert hub_lines <= 200, f"Hub has {hub_lines} lines, expected <= 200"

    def test_split_creates_sub_skill_directories(self):
        """Split should create sub-skill directories with SKILL.md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_large_skill(Path(tmpdir))
            result = _run([str(skill_path)])
            assert result.returncode == 0
            skill_dir = skill_path.parent
            sub_dirs = [d for d in skill_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
            assert len(sub_dirs) >= 1, "Expected at least one sub-skill directory"

    def test_sub_skills_under_200_lines(self):
        """Every sub-skill SKILL.md should be under 200 lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_large_skill(Path(tmpdir))
            _run([str(skill_path)])
            skill_dir = skill_path.parent
            for sub_dir in skill_dir.iterdir():
                if sub_dir.is_dir():
                    sub_skill = sub_dir / "SKILL.md"
                    if sub_skill.exists():
                        line_count = len(sub_skill.read_text(encoding="utf-8").splitlines())
                        assert line_count <= 200, f"{sub_skill} has {line_count} lines"

    def test_hub_has_see_also(self):
        """Hub should have see_also in frontmatter pointing to sub-skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_large_skill(Path(tmpdir))
            _run([str(skill_path)])
            content = skill_path.read_text(encoding="utf-8")
            # Parse frontmatter
            parts = content.split("---", 2)
            assert len(parts) >= 3, "Hub should have frontmatter"
            meta = yaml.safe_load(parts[1])
            assert "see_also" in meta, "Hub frontmatter should have see_also"
            assert len(meta["see_also"]) >= 1

    def test_sub_skill_has_frontmatter(self):
        """Sub-skills should have proper YAML frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_large_skill(Path(tmpdir))
            _run([str(skill_path)])
            skill_dir = skill_path.parent
            for sub_dir in skill_dir.iterdir():
                if sub_dir.is_dir():
                    sub_skill = sub_dir / "SKILL.md"
                    if sub_skill.exists():
                        content = sub_skill.read_text(encoding="utf-8")
                        assert content.startswith("---"), f"{sub_skill} missing frontmatter"
                        parts = content.split("---", 2)
                        meta = yaml.safe_load(parts[1])
                        assert "name" in meta, f"{sub_skill} missing name"
                        assert "category" in meta, f"{sub_skill} missing category"
                        assert meta.get("type") == "reference"

    def test_flags_oversized_h3_sections(self):
        """If a single H3 section exceeds 200 lines, it should be flagged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create skill with one giant H3 section
            skill_path = _make_large_skill(Path(tmpdir), lines=1200)
            result = _run([str(skill_path)])
            # Check stderr for warnings about oversized H3 sections
            output = result.stdout + result.stderr
            # At least one section should be flagged since each H3 is ~290 lines
            assert "manual review" in output.lower() or "warning" in output.lower() or "oversized" in output.lower()


class TestTrimMode:
    def test_trim_extracts_appendix(self):
        """--trim mode should extract appendix sections (Troubleshooting, Integration Examples)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = _make_marginal_skill(Path(tmpdir))
            original_count = len(skill_path.read_text(encoding="utf-8").splitlines())
            assert original_count > 200, f"Fixture should be >200 lines, got {original_count}"
            result = _run(["--trim", str(skill_path)])
            assert result.returncode == 0
            # Hub should now be shorter
            new_count = len(skill_path.read_text(encoding="utf-8").splitlines())
            assert new_count <= 200, f"Trimmed hub has {new_count} lines, expected <= 200"


class TestBatchMode:
    def test_batch_processes_directory(self):
        """--batch should process all oversized skills in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            # Create two oversized skills
            for name in ["skill-a", "skill-b"]:
                skill_dir = tmp / name
                skill_dir.mkdir()
                lines = ["---", f"name: {name}",
                         f"description: Batch test skill {name} for testing batch mode processing of multiple skills.",
                         "version: 1.0.0", "category: engineering",
                         "scripts_exempt: true", "---", "", f"# {name}", ""]
                lines.append("## When to Use")
                lines.append("")
                lines.append("- Batch testing")
                lines.append("")
                lines.append("## Core Capabilities")
                lines.append("")
                for i in range(250):
                    lines.append(f"Content line {i + 1}.")
                (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")

            result = _run(["--batch", str(tmp), "--min-lines", "200"])
            assert result.returncode == 0
            # Both should have been processed
            for name in ["skill-a", "skill-b"]:
                hub = (tmp / name / "SKILL.md").read_text(encoding="utf-8")
                assert len(hub.splitlines()) <= 200, f"{name} hub still over 200 lines"
