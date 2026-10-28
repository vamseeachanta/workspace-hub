"""Exercise the section script with synthetic research, never saved prose.

Heading conventions: .planning/research/2026-04-10-synthesis.md:25,51,53.
Legacy headings and fallback text: scripts/productivity/sections/research-highlights.sh.
All expected output below is written by hand from the synthetic fixture bullets.
"""

import os
from pathlib import Path
import subprocess
import time

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts/productivity/sections/research-highlights.sh"
)
HEADER = "## Research Highlights\n\n"
# Citation: the script's find -mtime -1 selects the preceding day.
# Hand calculation: one day = 24 hours * 60 minutes * 60 seconds.
DAY_SECONDS = 24 * 60 * 60


def write_research(root, markdown, name="sample.md", *, stale=False):
    directory = root / ".planning" / "research"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(markdown, encoding="utf-8")
    # Hand calculation: half a day is recent; two days is outside the window.
    age = DAY_SECONDS * 2 if stale else DAY_SECONDS / 2
    modified = time.time() - age
    os.utime(path, (modified, modified))


def render(root):
    result = subprocess.run(
        ["bash", str(SCRIPT), str(root)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stderr == ""
    return result.stdout


def test_existing_findings_and_actions_are_extracted(tmp_path):
    write_research(
        tmp_path,
        "## Key Findings\n- A synthetic finding.\n\n"
        "## Recommended Actions\n- Check the example.\n",
    )
    assert render(tmp_path) == (
        HEADER + "### sample\n\n- A synthetic finding.\n\n"
        "**Actions:**\n- Check the example.\n\n"
    )


def test_synthesis_findings_are_extracted(tmp_path):
    # Citation: synthesis heading lines 25 and 51, subordinate heading line 53.
    write_research(
        tmp_path,
        "## Top 3 Insights for PROJECT.md\n- A synthetic insight.\n\n"
        "## Detailed Action Items\n\n### Follow through\n- Check the insight.\n",
    )
    assert render(tmp_path) == (
        HEADER + "### sample\n\n- A synthetic insight.\n\n"
        "**Actions:**\n\n### Follow through\n- Check the insight.\n\n"
    )


def test_research_multiline_findings(tmp_path):
    write_research(
        tmp_path,
        "## Key Findings\n- First finding\n  continued on another line.\n\n"
        "### Supporting details\n- Second finding.\n",
    )
    assert render(tmp_path) == (
        HEADER + "### sample\n\n- First finding\n"
        "  continued on another line.\n\n"
        "### Supporting details\n- Second finding.\n\n"
    )


@pytest.mark.parametrize("boundary", ["## Next section", "# Next chapter"])
@pytest.mark.parametrize(
    ("findings_heading", "actions_heading"),
    [
        ("Key Findings", "Recommended Actions"),
        ("Top 3 Insights for PROJECT.md", "Detailed Action Items"),
    ],
)
def test_research_section_stops_at_peer_heading(
    tmp_path, boundary, findings_heading, actions_heading
):
    write_research(
        tmp_path,
        f"## {findings_heading}\n- Included finding.\n"
        f"{boundary}\n- Unrelated finding.\n"
        f"## {actions_heading}\n- Included action.\n\n"
        "### Action details\n- Included detail.\n"
        f"{boundary}\n- Unrelated action.\n",
    )
    assert render(tmp_path) == (
        HEADER + "### sample\n\n- Included finding.\n\n"
        "**Actions:**\n- Included action.\n\n"
        "### Action details\n- Included detail.\n\n"
    )


def test_research_filenames_with_spaces(tmp_path):
    root = tmp_path / "workspace with spaces"
    write_research(root, "## Key Findings\n- Later file.\n", "b notes.md")
    write_research(root, "## Key Findings\n- Earlier file.\n", "a notes.md")
    assert render(root) == (
        HEADER + "### a notes\n\n- Earlier file.\n\n"
        "### b notes\n\n- Later file.\n\n"
    )


@pytest.mark.parametrize(
    "markdown",
    [
        "## Unrelated section\n- Unrelated bullet.\n",
        "## Key Findings\n## Recommended Actions\n",
        "## Key Findings\n\n## Recommended Actions\n\n",
        "## Top 3 Insights for PROJECT.md\n\n## Detailed Action Items\n\n",
        "## Key Findings\n \t\n## Recommended Actions\n \t\n",
    ],
)
def test_research_empty_and_missing_fallbacks(tmp_path, markdown):
    write_research(tmp_path, markdown)
    assert render(tmp_path) == (
        HEADER + "### sample\n\n_(could not extract findings)_\n\n"
    )


def test_research_missing_directory(tmp_path):
    assert render(tmp_path) == HEADER + "_No research directory found._\n\n"


def test_research_empty_directory(tmp_path):
    (tmp_path / ".planning" / "research").mkdir(parents=True)
    assert render(tmp_path) == HEADER + "_No new research from last night._\n\n"


def test_research_stale_files_are_excluded(tmp_path):
    write_research(tmp_path, "## Key Findings\n- Old finding.\n", stale=True)
    assert render(tmp_path) == HEADER + "_No new research from last night._\n\n"


def test_research_only_recent_markdown_is_rendered(tmp_path):
    write_research(tmp_path, "## Key Findings\n- Old finding.\n", "old.md", stale=True)
    write_research(tmp_path, "## Key Findings\n- Other format.\n", "other.txt")
    write_research(tmp_path, "## Key Findings\n- Recent finding.\n", "recent.md")
    assert render(tmp_path) == HEADER + "### recent\n\n- Recent finding.\n\n"
