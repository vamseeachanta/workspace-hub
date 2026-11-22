"""Keep the live adapter on the onboarding and authority surfaces in AGENTS.md."""

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LEGACY_TARGET = "docs/work-queue-workflow.md"
WORKFLOW_PREFIXES = ("- Current workflow surface:", "- Gate evidence:")
MARKDOWN_LINK = re.compile(r"\[[^\]\n]+\]\((?P<target>[^)\s]+)\)")


def _assert_workflow_links(text: str) -> None:
    assert LEGACY_TARGET not in text, "Legacy workflow pointer in live adapter"
    targets = set()
    for prefix in WORKFLOW_PREFIXES:
        lines = [line for line in text.splitlines() if line.startswith(prefix)]
        assert lines, f"Missing workflow guidance: {prefix}"
        for line in lines:
            links = MARKDOWN_LINK.findall(line)
            assert links, f"Missing workflow Markdown links: {prefix}"
            targets.update(links)

    # Canonical destinations are declared by AGENTS.md, Retrieval and planning.
    assert "docs/plans/README.md" in targets, "Missing current onboarding link"
    assert "AGENTS.md" in targets, "Missing canonical instructions link"
    assert "config/agents/SHARED_SOUL.md" in targets, "Missing authority link"
    for target in targets:
        relative = Path(target)
        assert not relative.is_absolute(), f"Expected repository-relative link: {target}"
        destination = (REPO_ROOT / relative).resolve()
        assert destination.is_relative_to(REPO_ROOT), f"Link escapes repository: {target}"
        assert destination.suffix == ".md" and destination.is_file(), (
            f"Workflow document does not exist: {target}"
        )


def test_gemini_workflow_links() -> None:
    _assert_workflow_links((REPO_ROOT / "GEMINI.md").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "extra_pointer, reason",
    [
        (f"[legacy]({LEGACY_TARGET})", "Legacy workflow pointer"),
        (f"`{LEGACY_TARGET}`", "Legacy workflow pointer"),
        ("[missing](docs/nonexistent-workflow-target.md)", "does not exist"),
    ],
    ids=["legacy-markdown", "legacy-inline-code", "missing-destination"],
)
def test_workflow_link_regressions_are_rejected(extra_pointer: str, reason: str) -> None:
    # Synthetic guidance uses the destinations independently specified in AGENTS.md.
    text = (
        "- Current workflow surface: [guide](docs/plans/README.md)\n"
        "- Gate evidence: [instructions](AGENTS.md), "
        "[authority](config/agents/SHARED_SOUL.md), " + extra_pointer + "\n"
    )
    with pytest.raises(AssertionError, match=reason):
        _assert_workflow_links(text)
