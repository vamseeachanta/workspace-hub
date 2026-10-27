"""Synthetic regression cases for the existing detector (issue #3612).

Behavior declarations: scripts/skills/detect_duplicate_skills.py, extract_name
(quotes/case/fallback), find_skill_files (exact exclusions and sorted paths),
and main (separate groups, sorted diagnostics, nonblocking exit).

Hand count of ACTIVE_INVENTORY: alpha-shared occurs at beta, delta and zeta;
zebra-shared occurs at alpha and epsilon; amber-analysis, cobalt-analysis and
sole-name each occur once. Thus eight files have five distinct names, two
duplicate-name groups and two leaf collisions (analysis at amber and cobalt;
review at alpha and beta). Zebra and review are encountered first but each
will be printed after the alphabetically earlier group in its category.
These are fixture counts, not policy thresholds or a live corpus measurement.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


DETECTOR = (
    Path(__file__).resolve().parent.parent.parent
    / "scripts" / "skills" / "detect_duplicate_skills.py"
)
spec = importlib.util.spec_from_file_location("duplicate_skill_detector_cases", DETECTOR)
assert spec and spec.loader
detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector)

# Deliberately unsorted input; normalized expectations below are independent.
ACTIVE_INVENTORY = (
    ("skills/zeta/zeta-leaf/SKILL.md", "'ALPHA-SHARED'"),
    ("skills/beta/review/SKILL.md", '"Alpha-Shared"'),
    ("skills/alpha/review/SKILL.md", "'ZEBRA-SHARED'"),
    ("skills/epsilon/epsilon-leaf/SKILL.md", '"Zebra-Shared"'),
    ("skills/delta/delta-leaf/SKILL.md", "alpha-shared"),
    ("skills/cobalt/analysis/SKILL.md", "cobalt-analysis"),
    ("skills/amber/analysis/SKILL.md", "amber-analysis"),
    ("skills/neutral/solo/SKILL.md", "sole-name"),
)
PRUNED_INVENTORY = (
    ("skills/_archive/old/analysis/SKILL.md", "alpha-shared"),
    ("skills/_diverged/old/analysis/SKILL.md", "zebra-shared"),
    ("skills/alpha/_archive/deep/analysis/SKILL.md", "alpha-shared"),
    ("skills/beta/_diverged/deep/analysis/SKILL.md", "zebra-shared"),
)
EXPECTED_NAMES = {
    "skills/alpha/review/SKILL.md": "zebra-shared",
    "skills/amber/analysis/SKILL.md": "amber-analysis",
    "skills/beta/review/SKILL.md": "alpha-shared",
    "skills/cobalt/analysis/SKILL.md": "cobalt-analysis",
    "skills/delta/delta-leaf/SKILL.md": "alpha-shared",
    "skills/epsilon/epsilon-leaf/SKILL.md": "zebra-shared",
    "skills/neutral/solo/SKILL.md": "sole-name",
    "skills/zeta/zeta-leaf/SKILL.md": "alpha-shared",
}
EXPECTED_OUTPUT = (
    "Scanned 8 SKILL.md files across 5 unique names\n"
    "WARNING: DUPLICATE skill name 'alpha-shared': "
    "skills/beta/review/SKILL.md, skills/delta/delta-leaf/SKILL.md, "
    "skills/zeta/zeta-leaf/SKILL.md\n"
    "WARNING: DUPLICATE skill name 'zebra-shared': "
    "skills/alpha/review/SKILL.md, skills/epsilon/epsilon-leaf/SKILL.md\n"
    "WARNING: DUPLICATE leaf directory 'analysis': "
    "skills/amber/analysis/SKILL.md, skills/cobalt/analysis/SKILL.md\n"
    "WARNING: DUPLICATE leaf directory 'review': "
    "skills/alpha/review/SKILL.md, skills/beta/review/SKILL.md\n"
    "\n2 duplicate name(s) and 2 leaf collision(s) found across 8 skills.\n"
)


def write_inventory(root, inventory):
    for relative, name in inventory:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nname:   {name}   \n---\n", encoding="utf-8")


def run_cli(root, *arguments):
    # The only scanned files and the process working directory are synthetic.
    return subprocess.run(
        [sys.executable, str(DETECTOR), *map(str, arguments)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def skill_tree(tmp_path):
    write_inventory(tmp_path, ACTIVE_INVENTORY + PRUNED_INVENTORY)
    return tmp_path


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("---\nname:   'MiXeD-Name'   \n---\n", "mixed-name"),
        ('---\nname:   "MiXeD-Name"   \n---\n', "mixed-name"),
        ("---\nname:   MiXeD-Name   \n---\n", "mixed-name"),
        ("---\n  NaMe: 'MiXeD-Name'\n---\n", "mixed-name"),
        ("# No frontmatter\n", "fallback-leaf"),
        ("---\ndescription: no name declared\n---\n", "fallback-leaf"),
    ],
    ids=["single-quoted", "double-quoted", "unquoted", "mixed-key",
         "no-frontmatter", "no-name"],
)
def test_extract_name_normalizes_declared_names(tmp_path, content, expected):
    path = tmp_path / "fallback-leaf" / "SKILL.md"
    path.parent.mkdir()
    path.write_text(content, encoding="utf-8")

    assert detector.extract_name(path) == expected


def test_extract_name_returns_none_for_missing_file(tmp_path):
    assert detector.extract_name(tmp_path / "missing" / "SKILL.md") is None


@pytest.mark.parametrize("absolute_root", [False, True], ids=["relative", "absolute"])
def test_duplicate_names_and_leaf_collisions_are_distinct(skill_tree, absolute_root):
    skills_dir = skill_tree / "skills"
    files = detector.find_skill_files(skills_dir)
    assert [path.relative_to(skill_tree).as_posix() for path in files] == list(
        EXPECTED_NAMES
    )
    assert {
        path.relative_to(skill_tree).as_posix(): detector.extract_name(path)
        for path in files
    } == EXPECTED_NAMES

    result = run_cli(
        skill_tree, "--skills-dir", skills_dir if absolute_root else "skills"
    )
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == EXPECTED_OUTPUT


def test_archives_are_pruned(skill_tree):
    # Exact exclusions only: the two similarly prefixed leaves must survive.
    write_inventory(skill_tree, (
        ("skills/retained/_archive_notes/SKILL.md", "archive-notes"),
        ("skills/retained/_diverged_notes/SKILL.md", "diverged-notes"),
    ))
    # Lowercase filenames and non-skill Markdown files must not be discovered.
    (skill_tree / "skills" / "skill.md").write_text("ignored\n", encoding="utf-8")
    (skill_tree / "skills" / "README.md").write_text("ignored\n", encoding="utf-8")

    assert [
        path.relative_to(skill_tree).as_posix()
        for path in detector.find_skill_files(skill_tree / "skills")
    ] == [
        "skills/alpha/review/SKILL.md",
        "skills/amber/analysis/SKILL.md",
        "skills/beta/review/SKILL.md",
        "skills/cobalt/analysis/SKILL.md",
        "skills/delta/delta-leaf/SKILL.md",
        "skills/epsilon/epsilon-leaf/SKILL.md",
        "skills/neutral/solo/SKILL.md",
        "skills/retained/_archive_notes/SKILL.md",
        "skills/retained/_diverged_notes/SKILL.md",
        "skills/zeta/zeta-leaf/SKILL.md",
    ]


def test_detector_output_is_order_independent(tmp_path):
    inventory = ACTIVE_INVENTORY + PRUNED_INVENTORY
    for label, entries in (("forward", inventory), ("reverse", reversed(inventory))):
        root = tmp_path / label
        write_inventory(root, entries)

        result = run_cli(root, "--skills-dir", "skills")
        assert result.returncode == 0
        assert result.stderr == ""
        assert result.stdout == EXPECTED_OUTPUT


def test_cli_unique_tree_is_nonblocking(tmp_path):
    write_inventory(tmp_path, (("skills/unique/SKILL.md", "unique"),))

    result = run_cli(tmp_path, "--skills-dir", "skills")
    assert result.returncode == 0
    assert result.stderr == ""
    # One fixture file gives one unique name and no duplicate groups.
    assert result.stdout == (
        "Scanned 1 SKILL.md files across 1 unique names\n"
        "No duplicate skill names found.\n"
    )


def test_cli_empty_tree_is_nonblocking(tmp_path):
    (tmp_path / "skills").mkdir()

    result = run_cli(tmp_path, "--skills-dir", "skills")
    assert result.returncode == 0
    assert result.stderr == ""
    # The empty fixture contributes zero files and zero names.
    assert result.stdout == (
        "Scanned 0 SKILL.md files across 0 unique names\n"
        "No duplicate skill names found.\n"
    )


def test_cli_missing_tree_is_nonblocking(tmp_path):
    missing = tmp_path / "missing"

    result = run_cli(tmp_path, "--skills-dir", missing)
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == f"WARNING: skills directory not found: {missing}\n"


def test_cli_default_tree_is_confined_to_fixture(tmp_path):
    write_inventory(tmp_path, ((".claude/skills/unique/SKILL.md", "unique"),))

    result = run_cli(tmp_path)
    assert result.returncode == 0
    assert result.stderr == ""
    # The declared default in parse_args resolves against the synthetic cwd.
    assert result.stdout == (
        "Scanned 1 SKILL.md files across 1 unique names\n"
        "No duplicate skill names found.\n"
    )
