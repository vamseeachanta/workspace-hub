"""Regression tests for SKILL.md frontmatter validation (#2981)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "skills" / "validate-skills.sh"


def _write_skill(root: Path, rel: str, frontmatter: str, body: str = "# Body\n") -> Path:
    path = root / rel / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
    return path


def _run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(REPO_ROOT / ".claude" / "state" / "uv-cache")
    return subprocess.run(
        ["bash", str(VALIDATOR), str(root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_validator_fails_on_unquoted_colon_description(tmp_path: Path) -> None:
    """Unquoted colon-bearing descriptions must fail YAML validation."""
    _write_skill(
        tmp_path,
        "bad-colon",
        "name: bad-colon\n"
        "description: Convert lessons into proposed durable assets: skills, scripts, rules.\n",
    )

    result = _run_validator(tmp_path)

    assert result.returncode == 1
    assert "bad-colon" in result.stdout
    assert "YAML" in result.stdout or "mapping values are not allowed" in result.stdout


def test_validator_passes_on_quoted_colon_description(tmp_path: Path) -> None:
    """Quoted descriptions may safely contain colon-bearing trigger text."""
    _write_skill(
        tmp_path,
        "quoted-colon",
        'name: quoted-colon\n'
        'description: "Convert lessons into proposed durable assets: skills, scripts, rules."\n',
    )

    result = _run_validator(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Skill validation passed (1 files)." in result.stdout


def test_validator_requires_name_and_description(tmp_path: Path) -> None:
    """Both name and description are required string fields."""
    _write_skill(tmp_path, "missing-description", "name: missing-description\n")
    _write_skill(tmp_path, "missing-name", "description: valid description\n")

    result = _run_validator(tmp_path)

    assert result.returncode == 1
    assert "missing-description" in result.stdout
    assert "missing-name" in result.stdout
    assert "name" in result.stdout
    assert "description" in result.stdout


def test_validator_rejects_empty_or_non_string_name_description(tmp_path: Path) -> None:
    """YAML-valid but loader-unsafe metadata values must fail."""
    cases = {
        "numeric-name": "name: 123\ndescription: valid description\n",
        "false-description": "name: false-description\ndescription: false\n",
        "list-description": "name: list-description\ndescription: []\n",
        "empty-name": 'name: ""\ndescription: valid description\n',
        "blank-name": 'name: "   "\ndescription: valid description\n',
        "empty-description": 'name: empty-description\ndescription: ""\n',
        "blank-description": 'name: blank-description\ndescription: "   "\n',
    }
    for rel, frontmatter in cases.items():
        _write_skill(tmp_path, rel, frontmatter)

    result = _run_validator(tmp_path)

    assert result.returncode == 1
    combined = result.stdout + result.stderr
    assert "Traceback" not in combined
    for rel in cases:
        assert rel in combined


def test_validator_accepts_crlf_frontmatter_delimiters(tmp_path: Path) -> None:
    """The conservative delimiter splitter supports CRLF frontmatter files."""
    path = tmp_path / "crlf" / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"---\r\n"
        b"name: crlf\r\n"
        b"description: \"Colon text is safe when quoted: yes.\"\r\n"
        b"---\r\n"
        b"\r\n"
        b"# Body\r\n"
    )

    result = _run_validator(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout


def test_live_claude_skill_tree_passes_after_fix() -> None:
    """The live workspace skill inventory must parse after the #2981 fix."""
    result = _run_validator(REPO_ROOT / ".claude" / "skills")

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Skill validation passed" in result.stdout
