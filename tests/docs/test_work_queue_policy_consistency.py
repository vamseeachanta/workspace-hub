"""Policy consistency checks for GitHub issues vs legacy work-queue docs."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
LEGACY_DOCS = [
    REPO_ROOT / "docs" / "work-queue-workflow.md",
    REPO_ROOT / "docs" / "assessments" / "document-intelligence-audit.md",
    REPO_ROOT / "docs" / "modules" / "ai" / "AGENT_EQUIVALENCE_ARCHITECTURE.md",
]


def test_agents_declares_github_issues_canonical():
    text = AGENTS_PATH.read_text()
    assert "Tasks tracked as GitHub issues" in text
    assert "no local work-queue" in text


def test_legacy_docs_mark_work_queue_as_legacy_or_compatibility():
    for path in LEGACY_DOCS:
        text = path.read_text().lower()
        assert (
            "legacy" in text or "compatibility" in text or "github issues" in text
        ), f"{path} must describe work-queue as legacy/compatibility or point to GitHub issues"
