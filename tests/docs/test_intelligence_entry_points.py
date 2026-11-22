"""Offline checks for the existing intelligence navigation contract.

Run from the repository root:
    python -m pytest tests/docs/test_intelligence_entry_points.py

Inventory before this test was added: dedicated coverage was absent. The
canonical page is docs/document-intelligence/README.md. docs/README.md links
there from its ecosystem table and reading guidance; the capabilities summary
also links there. The AI documentation index lacked a direct backlink.

The allowlist below comes from that inventory and the canonical page's
"Reading Order for Newcomers" section. Only these in-repository inline Markdown
routes are checked. Wiki assets, sibling repositories, remote URLs, other
inventory links, and non-ATX or duplicate-heading anchors are outside this
contract. No page counts, freshness dates, or network access are required.
"""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
CANONICAL = "docs/document-intelligence/README.md"
# Sources: the existing top-level docs routes and their related AI index.
BACKLINKS = (
    ("docs/README.md", "document-intelligence/README.md"),
    ("docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md", "document-intelligence/README.md"),
    ("docs/modules/ai/README.md", "../../document-intelligence/README.md"),
    (CANONICAL, "../README.md"),
)
# Source: docs/document-intelligence/README.md, Reading Order for Newcomers.
READING_ORDER = (
    "llm-wiki-resource-doc-intelligence-operating-model.md",
    "standards-codes-provenance-reuse-contract.md",
    "durable-vs-transient-knowledge-boundary.md",
    "intelligence-accessibility-map.md",
)


def _navigation_text(text: str) -> str:
    """Exclude examples and comments, which do not provide navigation."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = []
    fence = None
    for line in text.splitlines():
        if fence is None and re.match(r"^(?: {4}| {0,3}\t)", line):
            continue
        marker = re.match(r"^\s*(?P<fence>`{3,}|~{3,})", line)
        if marker:
            token = marker["fence"]
            if fence is None:
                fence = token
            elif token.startswith(fence[0]) and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def _section(text: str, title: str) -> str:
    """Select a required second-level section, excluding later tables."""
    heading = f"## {title}"
    lines = text.splitlines()
    assert heading in lines, f"Missing section: {title}"
    following = iter(lines)
    for line in following:
        if line == heading:
            break
    selected = []
    for line in following:
        if re.match(r"^#{1,2}\s", line):
            break
        selected.append(line)
    return "\n".join(selected)


def _assert_local_link(root: Path, source: str, href: str, *, section=None) -> None:
    """Require a visible inline link, a contained file, and a valid ATX anchor.

    The constrained syntax matches the allowlisted routes; this is not a
    general Markdown crawler. Reference-style links are outside its scope.
    """
    page = root / source
    assert page.is_file(), f"Missing source: {source}"
    text = _navigation_text(page.read_text(encoding="utf-8"))
    if section is not None:
        text = _section(text, section)
    links = []
    for match in re.finditer(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)\)", text):
        prefix = text[:match.start()]
        # An odd number of backslashes escapes the opening bracket.
        if (len(prefix) - len(prefix.rstrip("\\"))) % 2 == 0:
            links.append(match[1])
    assert href in links, f"Missing link in {source}: {href}"
    route = urlsplit(href)
    assert not (route.scheme or route.netloc or route.query), "Expected local route"
    assert not Path(unquote(route.path)).is_absolute(), "Expected relative route"
    target = (page.parent / unquote(route.path)).resolve() if route.path else page.resolve()
    assert target.is_relative_to(root.resolve()), f"Route leaves repository: {href}"
    assert target.is_file(), f"Missing destination from {source}: {href}"
    if route.fragment:
        headings = re.findall(
            r"^#{1,6}\s+(.+?)(?:\s+#+)?\s*$",
            _navigation_text(target.read_text(encoding="utf-8")),
            flags=re.MULTILINE,
        )
        # GitHub-style unique ATX slugs: lowercase, drop punctuation, hyphenate spaces.
        anchors = {re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-") for title in headings}
        assert unquote(route.fragment) in anchors, f"Broken local anchor: {href}"


def test_canonical_intelligence_page_has_doc_backlinks():
    for source, href in BACKLINKS:
        _assert_local_link(ROOT, source, href)


def test_local_reading_order_targets_resolve():
    for href in READING_ORDER:
        _assert_local_link(ROOT, CANONICAL, href, section="Reading Order for Newcomers")


def test_checker_accepts_relative_link_and_local_anchors(tmp_path):
    """Expected slugs are hand-derived from the literal fixture headings."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(
        "# Index\n[Target](../target.md#local-heading)\n[Here](#index)\n",
        encoding="utf-8", newline="\n",
    )
    (tmp_path / "target.md").write_text("## Local heading!\n", encoding="utf-8", newline="\n")
    _assert_local_link(tmp_path, "docs/index.md", "../target.md#local-heading")
    _assert_local_link(tmp_path, "docs/index.md", "#index")


@pytest.mark.parametrize("text", [
    "# Index\nNo backlink remains.\n",
    "The target.md path is mentioned without a link.\n",
    "<!-- [Target](target.md) -->\n",
    "```markdown\n[Target](target.md)\n```\n",
    "~~~markdown\n[Target](target.md)\n~~~\n",
    "Example: `[Target](target.md)`\n",
    "![Target](target.md)\n",
    "    [Target](target.md)\n",
    "\t[Target](target.md)\n",
    "  \t[Target](target.md)\n",
    "    ```\n    [Target](target.md)\n    ```\n",
    r"\[Target](target.md)",
    r"\\\[Target](target.md)",
])
def test_checker_detects_removed_backlink(tmp_path, text):
    (tmp_path / "index.md").write_text(text, encoding="utf-8", newline="\n")
    (tmp_path / "target.md").write_text("# Target\n", encoding="utf-8", newline="\n")
    with pytest.raises(AssertionError, match="Missing link"):
        _assert_local_link(tmp_path, "index.md", "target.md")


def test_checker_detects_nonexistent_local_target(tmp_path):
    (tmp_path / "index.md").write_text("[Missing](missing.md)\n", encoding="utf-8", newline="\n")
    with pytest.raises(AssertionError, match="Missing destination"):
        _assert_local_link(tmp_path, "index.md", "missing.md")


@pytest.mark.parametrize("href", ["target.md#absent", "#absent"])
def test_checker_detects_broken_local_anchor(tmp_path, href):
    (tmp_path / "index.md").write_text(f"# Index\n[Link]({href})\n", encoding="utf-8", newline="\n")
    (tmp_path / "target.md").write_text("## Present\n", encoding="utf-8", newline="\n")
    with pytest.raises(AssertionError, match="Broken local anchor"):
        _assert_local_link(tmp_path, "index.md", href)


def test_checker_detects_reading_order_link_moved_to_another_section(tmp_path):
    (tmp_path / "index.md").write_text(
        "## Reading Order for Newcomers\nNo route.\n"
        "## Architecture\n[Target](target.md)\n",
        encoding="utf-8", newline="\n",
    )
    (tmp_path / "target.md").write_text("# Target\n", encoding="utf-8", newline="\n")
    with pytest.raises(AssertionError, match="Missing link"):
        _assert_local_link(tmp_path, "index.md", "target.md", section="Reading Order for Newcomers")


@pytest.mark.parametrize("href,reason", [
    ("../sibling.md", "Route leaves repository"),
    ("https://example.invalid/target.md", "Expected local route"),
    ("//example.invalid/target.md", "Expected local route"),
])
def test_checker_rejects_routes_outside_local_contract(tmp_path, href, reason):
    (tmp_path / "index.md").write_text(f"[Link]({href})\n", encoding="utf-8", newline="\n")
    with pytest.raises(AssertionError, match=reason):
        _assert_local_link(tmp_path, "index.md", href)


@pytest.mark.parametrize("text", [
    "[Target](target.md)\n",
    "- [Target](target.md)\n",
    "  - [Target](target.md)\n",
    "1. [Target](target.md)\n",
    r"\\[Target](target.md)",
    "    ```\n\n[Target](target.md)\n",
])
def test_checker_accepts_visible_backlink(tmp_path, text):
    (tmp_path / "index.md").write_text(text, encoding="utf-8", newline="\n")
    (tmp_path / "target.md").write_text("# Target\n", encoding="utf-8", newline="\n")
    _assert_local_link(tmp_path, "index.md", "target.md")
