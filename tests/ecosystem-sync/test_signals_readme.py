from pathlib import Path
import pytest
from scripts.ecosystem_sync.signals import (
    detect_readme_capability_diff, _extract_section, _hash_section
)
from scripts.ecosystem_sync.state import RepoState

FIXTURE = Path(__file__).parent / "fixtures" / "repos" / "repo-with-readme"


def test_extract_section_basic():
    md = "# T\n\n## Capabilities\n- one\n- two\n\n## Other\nx\n"
    assert _extract_section(md, "Capabilities").strip() == "- one\n- two"


def test_extract_section_missing_returns_empty():
    md = "# T\n## Other\nx\n"
    assert _extract_section(md, "Capabilities") == ""


# Fence cases follow CommonMark, "Fenced code blocks" (section 4.5).
# Expected bodies are hand-selected literal lines between unfenced headings.
@pytest.mark.parametrize("md", [
    "```markdown\n## Capabilities\nexample\n```\n## Capabilities\nreal\n## Other\nx\n",
    "~~~markdown\n## Capabilities\nexample\n~~~\n## Capabilities\nreal\n## Other\nx\n",
    "   ```\n## Capabilities\nexample\n ```\n## Capabilities\nreal\n",
    "  ~~~\n## Capabilities\nexample\n   ~~~~\n## Capabilities\nreal\n",
])
def test_extract_section_ignores_fenced_target(md):
    assert _extract_section(md, "Capabilities") == "real"


@pytest.mark.parametrize(("md", "expected"), [
    (
        "## Capabilities\nbefore\n```md\n## Other\nexample\n```\nafter\n## End\nx\n",
        "before\n```md\n## Other\nexample\n```\nafter",
    ),
    (
        "## Capabilities\nbefore\n~~~\n## Other\nexample\n~~~\nafter\n## End\nx\n",
        "before\n~~~\n## Other\nexample\n~~~\nafter",
    ),
    (
        "## Capabilities\n   ```\n## Other\n ```\nafter\n## End\nx\n",
        "```\n## Other\n ```\nafter",
    ),
    (
        "## Capabilities\ntext  \n\n  ~~~\n## Other\n   ~~~\n\nafter\n## End\nx\n",
        "text  \n\n  ~~~\n## Other\n   ~~~\n\nafter",
    ),
])
def test_extract_section_ignores_fenced_boundary(md, expected):
    assert _extract_section(md, "Capabilities") == expected


@pytest.mark.parametrize(("md", "expected"), [
    ("```\n## Capabilities\nexample\n", ""),
    ("~~~\n## Capabilities\nexample\n", ""),
    ("```\n## Capabilities\nexample\n```\n## Other\nx\n", ""),
    ("~~~\n## Capabilities\nexample\n~~~\n## Other\nx\n", ""),
    (
        "## Capabilities\nreal\n```\n## Other\nexample\n",
        "real\n```\n## Other\nexample",
    ),
    (
        "## Capabilities\nreal\n~~~\n## Other\nexample\n",
        "real\n~~~\n## Other\nexample",
    ),
])
def test_extract_section_unclosed_or_missing_real_heading(md, expected):
    assert _extract_section(md, "Capabilities") == expected


@pytest.mark.parametrize("md", [
    "````\n```\n## Capabilities\nexample\n````\n## Capabilities\nreal\n",
    "~~~~\n~~~\n## Capabilities\nexample\n~~~~\n## Capabilities\nreal\n",
    "```\n~~~\n## Capabilities\nexample\n```\n## Capabilities\nreal\n",
    "~~~\n```\n## Capabilities\nexample\n~~~\n## Capabilities\nreal\n",
    "```\n``` trailing\n## Capabilities\nexample\n```\n## Capabilities\nreal\n",
    "~~~\n~~~ trailing\n## Capabilities\nexample\n~~~\n## Capabilities\nreal\n",
    "```\n    ```\n## Capabilities\nexample\n```\n## Capabilities\nreal\n",
    "~~~\n\t~~~\n## Capabilities\nexample\n~~~\n## Capabilities\nreal\n",
    "```\n## Capabilities\nexample\n````` \t\n## Capabilities\nreal\n",
    "~~~\n## Capabilities\nexample\n~~~~~\t\n## Capabilities\nreal\n",
])
def test_extract_section_requires_matching_fence_closure(md):
    assert _extract_section(md, "Capabilities") == "real"


@pytest.mark.parametrize("md", [
    "    ```\n## Capabilities\nreal\n## Other\nx\n",
    "    ~~~\n## Capabilities\nreal\n## Other\nx\n",
    "\t```\n## Capabilities\nreal\n## Other\nx\n",
    " \t~~~\n## Capabilities\nreal\n## Other\nx\n",
    "``\n## Capabilities\nreal\n## Other\nx\n",
    "~~\n## Capabilities\nreal\n## Other\nx\n",
    "```invalid`info\n## Capabilities\nreal\n## Other\nx\n",
    "inline ```\n## Capabilities\nreal\n## Other\nx\n",
])
def test_extract_section_ignores_invalid_fence_openers(md):
    assert _extract_section(md, "Capabilities") == "real"


@pytest.mark.parametrize("md", [
    "~~~info`allowed\n## Capabilities\nexample\n~~~\n## Capabilities\nreal\n",
    "```\n## Capabilities\nexample\n```\n~~~\n## Capabilities\nexample\n~~~\n## Capabilities\nreal\n",
])
def test_extract_section_resumes_after_fences(md):
    assert _extract_section(md, "Capabilities") == "real"


@pytest.mark.parametrize("md", [
    "```md\n## Capabilities\nexample\n```\n",
    "~~~md\n## Capabilities\nexample\n~~~\n",
    "```\n## Capabilities\nexample\n",
    "~~~\n## Capabilities\nexample\n",
])
def test_diff_fenced_only_target_is_silent(tmp_path, md):
    (tmp_path / "README.md").write_text(md)
    state = RepoState(last_sync_utc="", last_commit_sha="")
    assert detect_readme_capability_diff(
        "example", tmp_path, state, sections=["Capabilities"]
    ) == []


def test_hash_section_ignores_trailing_whitespace():
    a = _hash_section("- one\n- two")
    b = _hash_section("- one\n- two\n\n")
    assert a == b


def test_diff_fires_on_changed_hash():
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_readme_hash={"Capabilities": "sha256:wrong"},
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", FIXTURE, state, sections=["Capabilities"]
    )
    assert len(sigs) == 1
    assert sigs[0].kind == "readme-diff"


def test_diff_no_fire_when_hash_matches():
    md = (FIXTURE / "README.md").read_text()
    current = _hash_section(_extract_section(md, "Capabilities"))
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z",
        last_commit_sha="",
        last_readme_hash={"Capabilities": current},
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", FIXTURE, state, sections=["Capabilities"]
    )
    assert sigs == []


def test_missing_section_is_silent():
    state = RepoState(
        last_sync_utc="2026-04-20T00:00:00Z", last_commit_sha="",
    )
    sigs = detect_readme_capability_diff(
        "digitalmodel", FIXTURE, state, sections=["Nonexistent Heading"]
    )
    assert sigs == []
