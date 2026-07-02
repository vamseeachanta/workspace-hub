"""Playbook lint for #3340: docs/guides/drive-file-search-playbook.md.

Pins: required sections present, canonical-drive-paths-only rule (the playbook
eats its own cooking — zero transport-alias literals), cited repo paths
resolve, and the three workflow surfaces carry the drive-index Resource-Intel
line.

Run: python3 -m pytest tests/docs/test_drive_search_playbook_3340.py -v
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK = REPO_ROOT / "docs" / "guides" / "drive-file-search-playbook.md"

TEMPLATE = REPO_ROOT / "docs" / "plans" / "_template-issue-plan.md"
PLANNING_SKILL = (
    REPO_ROOT / ".claude" / "skills" / "coordination" / "issue-planning-mode" / "SKILL.md"
)
PLANS_README = REPO_ROOT / "docs" / "plans" / "README.md"
SEARCH_SKILL = REPO_ROOT / ".claude" / "skills" / "data" / "drive-file-search" / "SKILL.md"


def _text() -> str:
    return PLAYBOOK.read_text(encoding="utf-8")


def test_playbook_exists():
    assert PLAYBOOK.is_file()


def test_playbook_required_sections():
    headings = [
        line.lower() for line in _text().splitlines() if line.startswith("#")
    ]
    joined = "\n".join(headings)
    for required in (
        "integration points",
        "reading results",
        "de-identification",
        "what not to do",
        "metrics",
        "decision framework",
    ):
        assert required in joined, f"missing playbook section heading: {required}"


def test_playbook_canonical_paths_only():
    text = _text()
    assert "/mnt/remote/" not in text  # transport alias is described, never spelled
    for match in re.finditer(r"/mnt/[^\s`)\"',;]*", text):
        token = match.group(0)
        assert token.startswith(("/mnt/ace", "/mnt/dde", "/mnt/<drive>")), (
            f"non-canonical drive path in playbook: {token}"
        )


def test_playbook_links_resolve():
    text = re.sub(r"```.*?```", "", _text(), flags=re.S)  # inline spans only
    cited = {
        span.strip().rstrip("/")
        for span in re.findall(r"`([^`\n]+)`", text)
        if re.match(r"^(scripts|docs|data|config|tests|\.claude)/", span.strip())
    }
    assert cited, "playbook should cite repo paths"
    missing = [path for path in sorted(cited) if not (REPO_ROOT / path).exists()]
    assert not missing, f"playbook cites nonexistent repo paths: {missing}"


def test_playbook_hit_threshold_is_named_constant_only():
    text = _text()
    assert "HIT_SCORE_MIN" in text  # cite the constant (review r1 F7) ...
    assert "0.3" not in text  # ... never the literal


def test_template_and_skill_carry_drive_intel_line():
    for surface in (TEMPLATE, PLANNING_SKILL, PLANS_README):
        content = surface.read_text(encoding="utf-8")
        assert "drive-index-search" in content, f"missing drive-index line: {surface}"
        assert "--caller plan-resource-intel" in content, (
            f"missing plan-resource-intel attribution: {surface}"
        )


def test_search_skill_carries_caller_and_playbook_link():
    content = SEARCH_SKILL.read_text(encoding="utf-8")
    assert "--caller skill" in content
    assert "docs/guides/drive-file-search-playbook.md" in content
