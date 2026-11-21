"""Offline checks of the report and the generator's read-only sections."""

import os
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/maintenance/claude-plugin-audit.sh"
REPORT = ROOT / "docs/reports/claude-plugin-audit-latest.md"


def section(start, end):
    source = SCRIPT.read_text()
    return source[source.index(start):source.index(end)]


def run_section(source, **variables):
    env = {key: value for key, value in os.environ.items()
           if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}}
    env.update(variables)
    return subprocess.run(["bash", "-c", source], env=env, check=True,
                          capture_output=True, text=True).stdout


@pytest.mark.parametrize("records,expected", [
    ("alpha|1.0|unknown|unknown|unknown\nbeta|unknown|user|abc|date", "2:1:beta"),
    ("alpha|unknown|user|abc|date\nalpha|unknown|user|abc|date", "1:1:alpha"),
    ("alpha|1.0|user|abc|date\nalpha|unknown|user|abc|date", "1:0:"),
    ("", "0:0:"),
])
def test_version_alerts_match_displayed_inventory(records, expected, tmp_path):
    source = section("UNKNOWN_COUNT=", "# ── Write report")
    source += '\nprintf "%s:%s:%s" "$INSTALLED_COUNT" "$UNKNOWN_COUNT" '
    source += '"$(printf "%s\\n" "$UNKNOWN_PLUGINS" | cut -d"|" -f1)"'
    assert run_section(source, INSTALLED_PLUGINS=records) == expected
    report = tmp_path / "report.md"
    source = section("UNKNOWN_COUNT=", 'echo "[$DATE] Report written')
    run_section(source, INSTALLED_PLUGINS=records, REPORT=str(report), DATE="fixture",
                AVAILABLE_COUNT="0", AVAILABLE_PLUGINS="", MARKETPLACE_SHA="fixture",
                OVERLAP_COUNT="0", SP_VERSION="unknown", DEPRECATED_SKILLS="")
    rendered = report.read_text()
    installed, unknown, names = expected.split(":")
    assert f"**Installed plugins:** {installed}" in rendered
    assert f"**Plugins with unknown version:** {unknown}" in rendered
    alerts = rendered.split("## Version Alerts", 1)[1].split("## Superpowers Status", 1)[0]
    assert [line[2:] for line in alerts.splitlines() if line.startswith("- ")] == (
        names.split() if names else []
    )


def test_overlap_paths_are_repository_relative(tmp_path):
    skill = tmp_path / ".claude/skills/development/code-review/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("fixture")
    source = section('CUSTOM_SKILLS_DIR=', '# ── Check for version:')
    source += '\nprintf "%b" "$OVERLAPS"'
    output = run_section(source, REPO_ROOT=str(tmp_path))
    assert output.strip() == "- code-review: .claude/skills/development/code-review/SKILL.md"
    assert str(tmp_path) not in output


def test_retained_report_counts_and_alert_membership():
    text = REPORT.read_text()
    table = text.split("## Installed Plugins\n", 1)[1].split("## Version Alerts", 1)[0]
    rows = [line.split("|")[1:-1] for line in table.splitlines()
            if line.startswith("| ") and not line.startswith("| Plugin ")]
    unknown = {row[0].strip() for row in rows if row[1].strip() == "unknown"}
    alerts = text.split("## Version Alerts\n", 1)[1].split("## Superpowers Status", 1)[0]
    assert int(re.search(r"unknown version:\*\* (\d+)", text)[1]) == len(unknown)
    assert int(re.search(r"\*\*(\d+) plugins report", alerts)[1]) == len(unknown)
    assert {line[2:] for line in alerts.splitlines() if line.startswith("- ")} == unknown
    assert int(re.search(r"Installed plugins:\*\* (\d+)", text)[1]) == len(rows)


def test_retained_overlap_references():
    text = REPORT.read_text().split("## Custom Skill Overlaps\n", 1)[1]
    text = text.split("## Available but Not Installed", 1)[0]
    references = [line.split(": ", 1)[1] for line in text.splitlines()
                  if line.startswith("- ")]
    assert len(references) == 6
    assert all(reference.startswith(".claude/skills/") for reference in references)
    assert all(not Path(reference).is_absolute() for reference in references)
