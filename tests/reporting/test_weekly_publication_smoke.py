"""Local weekly publication qualification for issue #2171.

Run with pytest and the shared test-setup dependency PyYAML available::

    uv run --no-project --with pytest --with pyyaml python -m pytest \
        tests/reporting/test_weekly_renderer.py \
        tests/reporting/test_weekly_history.py \
        tests/reporting/test_bundle_manifest.py \
        tests/reporting/test_publication_navigation.py \
        tests/reporting/test_weekly_publication_smoke.py \
        -q -rA -p no:cacheprovider

Only synthetic, already normalized sections and supplied statuses are assembled.
This checks local bytes and navigation, not upstream validation, operational
health, publication authorization or remote deployment. No workflow, browser,
network, operational data or solver execution is involved. Assembly glue belongs
only to this test; it does not define a production publication layout.

Expected paths, metadata and anchors below are hand-authored examples. The dates
follow the synthetic successive Mondays in test_weekly_history.py: October 5
precedes October 12. One supplied record followed by one append gives two records
by hand count. Section order follows the independent table in
test_weekly_renderer.py (issue #2154): ecosystem health before freshness, even
when supplied in reverse. The evidence size and digest use that suite's sibling
test_bundle_manifest.py ASCII abc example: three bytes, RFC 6234 section 8.5.
The manifest version is the local interface in bundle_manifest.py's docstring.
"""

import hashlib
from html.parser import HTMLParser
import json
import shutil

import bundle_manifest
from publication_navigation import NavigationIssue, check_bundle
from weekly_history import write_history
from weekly_renderer import render_html, render_markdown


FIRST = {
    "run_id": "review-a",
    "published_at": "2026-10-05T12:00:00Z",
    "artifact": "review-a.html",
}
SECOND = {
    "run_id": "review-b",
    "published_at": "2026-10-12T12:00:00Z",
    "artifact": "review-b.html",
}
# Enumerated independently of the assembly helper and production inventory.
FIRST_PATHS = {
    "artifacts/checks.txt", "bundle-manifest.json", "history.html", "index.json",
    "latest.html", "latest.json", "review-a.html", "review-a.md",
}
SECOND_PATHS = {
    "artifacts/checks.txt", "bundle-manifest.json", "history.html", "index.json",
    "latest.html", "latest.json", "review-a.html", "review-a.md",
    "review-b.html", "review-b.md",
}


class Page(HTMLParser):
    """Read literal anchors, section order and displayed text without a browser."""

    def __init__(self, text):
        super().__init__()
        self.links = []
        self.sections = []
        self.text = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a":
            self.links.append(attributes.get("href"))
        if tag == "section":
            self.sections.append(attributes.get("id"))

    def handle_data(self, text):
        self.text.append(text)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _publish(root, record, *, status="ok"):
    """Render supplied normalized content, then assemble a local example tree."""
    sections = [
        {"key": "freshness", "status": "ok", "summary": "Current fixture",
         "items": []},
        {"key": "ecosystem_health", "status": status,
         "summary": "Refresh required" if status == "warning" else "Checks passed",
         "items": [{"text": "Evidence", "artifact": "artifacts/checks.txt"}]},
    ]
    metadata = {"title": "Weekly review", "run_reference": record["run_id"]}
    report = root / record["artifact"]
    _write(report.with_suffix(".md"), render_markdown(metadata, sections))
    _write(report, render_html(metadata, sections))
    _write(root / "artifacts/checks.txt", "abc")
    assert write_history(root, **record) is True

    # Navigation glue consumes the written metadata, so stale latest pointers
    # and missing history entries remain observable in the literal assertions.
    latest = json.loads((root / "latest.json").read_text(encoding="utf-8"))
    records = json.loads((root / "index.json").read_text(encoding="utf-8"))
    _write(root / "latest.html", (
        '<!doctype html><html><body><h1>Latest</h1>'
        f'<a href="{latest["artifact"]}#ecosystem_health">Latest report</a>'
        '<a href="history.html">History</a>'
        '<a href="latest.json">Metadata</a></body></html>'
    ))
    _write(root / "history.html", (
        '<!doctype html><html><body><h1>History</h1>'
        '<a href="latest.html">Latest</a><a href="index.json">Metadata</a>'
        + "".join(f'<a href="{entry["artifact"]}#ecosystem_health">'
                  f'{entry["run_id"]}</a>' for entry in records)
        + '</body></html>'
    ))
    manifest_path = root / "bundle-manifest.json"
    manifest_path.write_bytes(bundle_manifest.serialize_manifest(
        bundle_manifest.inventory(root, exclude_output=manifest_path)
    ))


def _snapshot(root):
    return {
        path.relative_to(root).as_posix(): (
            path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns
        )
        for path in root.rglob("*") if path.is_file()
    }


def _assert_complete(root, expected_paths):
    """Check exact tree and byte inventory, and prove inspection is read-only."""
    before = _snapshot(root)
    assert set(before) == expected_paths
    manifest = json.loads((root / "bundle-manifest.json").read_text(encoding="utf-8"))
    assert set(manifest) == {"schema", "files"}
    assert manifest["schema"] == "bundle-manifest-v1"
    # A manifest cannot inventory its own final bytes; all payloads are listed.
    assert [entry["path"] for entry in manifest["files"]] == sorted(
        expected_paths - {"bundle-manifest.json"}
    )
    for entry in manifest["files"]:
        payload = (root / entry["path"]).read_bytes()
        assert set(entry) == {"path", "size", "sha256"}
        assert entry["size"] == len(payload)
        assert entry["sha256"] == hashlib.sha256(payload).hexdigest()
    assert next(entry for entry in manifest["files"]
                if entry["path"] == "artifacts/checks.txt") == {
        "path": "artifacts/checks.txt",
        "size": 3,  # Hand count: ASCII a, b, c; see module evidence citation.
        "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    }
    assert check_bundle(root) == []
    assert _snapshot(root) == before


def _page(root, name):
    return Page((root / name).read_text(encoding="utf-8"))


def test_first_and_subsequent_publication_smoke(tmp_path):
    root = tmp_path / "bundle"
    _publish(root, FIRST)
    _assert_complete(root, FIRST_PATHS)
    assert json.loads((root / "index.json").read_text(encoding="utf-8")) == [{
        "run_id": "review-a", "published_at": "2026-10-05T12:00:00Z",
        "artifact": "review-a.html",
    }]
    assert json.loads((root / "latest.json").read_text(encoding="utf-8")) == {
        "run_id": "review-a", "published_at": "2026-10-05T12:00:00Z",
        "artifact": "review-a.html",
    }
    assert _page(root, "latest.html").links == [
        "review-a.html#ecosystem_health", "history.html", "latest.json",
    ]
    assert _page(root, "history.html").links == [
        "latest.html", "index.json", "review-a.html#ecosystem_health",
    ]
    original_reports = {name: (root / name).read_bytes()
                        for name in ("review-a.md", "review-a.html")}

    _publish(root, SECOND)
    _assert_complete(root, SECOND_PATHS)
    assert json.loads((root / "index.json").read_text(encoding="utf-8")) == [
        {"run_id": "review-a", "published_at": "2026-10-05T12:00:00Z",
         "artifact": "review-a.html"},
        {"run_id": "review-b", "published_at": "2026-10-12T12:00:00Z",
         "artifact": "review-b.html"},
    ]
    assert json.loads((root / "latest.json").read_text(encoding="utf-8")) == {
        "run_id": "review-b", "published_at": "2026-10-12T12:00:00Z",
        "artifact": "review-b.html",
    }
    assert _page(root, "latest.html").links == [
        "review-b.html#ecosystem_health", "history.html", "latest.json",
    ]
    assert _page(root, "history.html").links == [
        "latest.html", "index.json", "review-a.html#ecosystem_health",
        "review-b.html#ecosystem_health",
    ]
    for name, content in original_reports.items():
        assert (root / name).read_bytes() == content
    for name in ("review-a.html", "review-b.html"):
        page = _page(root, name)
        assert page.links == ["artifacts/checks.txt"]
        assert page.sections == ["ecosystem_health", "freshness"]
        assert "Status: OK" in page.text
    for name in ("review-a.md", "review-b.md"):
        assert "[Evidence](artifacts/checks.txt)" in (root / name).read_text(encoding="utf-8")


def test_degraded_publication_remains_warning(tmp_path):
    root = tmp_path / "bundle"
    _publish(root, FIRST, status="warning")
    _assert_complete(root, FIRST_PATHS)
    markdown = (root / "review-a.md").read_text(encoding="utf-8")
    assert [line for line in markdown.splitlines() if line.startswith("## ")] == [
        "## Ecosystem health", "## Freshness",
    ]
    assert [line for line in markdown.splitlines() if line.startswith("Status:")] == [
        "Status: Warning", "Status: OK",
    ]
    assert "> [!WARNING]\n> Refresh required" in markdown
    assert "[Evidence](artifacts/checks.txt)" in markdown
    page = _page(root, "review-a.html")
    assert page.sections == ["ecosystem_health", "freshness"]
    assert [text for text in page.text if text.startswith("Status:")] == [
        "Status: Warning", "Status: OK",
    ]
    assert "Refresh required" in "".join(page.text)
    assert page.links == ["artifacts/checks.txt"]


def test_relocated_bundle_and_missing_asset_negative(tmp_path):
    original = tmp_path / "original"
    _publish(original, FIRST)
    _publish(original, SECOND)
    _assert_complete(original, SECOND_PATHS)
    before = _snapshot(original)
    relocated = tmp_path / "elsewhere" / "bundle"
    shutil.copytree(original, relocated)
    _assert_complete(relocated, SECOND_PATHS)
    assert {name: value[0] for name, value in _snapshot(relocated).items()} == {
        name: value[0] for name, value in before.items()
    }  # Tuple offset zero selects the saved bytes, independently of copy metadata.

    (relocated / "artifacts/checks.txt").unlink()
    broken = _snapshot(relocated)
    assert check_bundle(relocated) == [
        NavigationIssue("review-a.html", "artifacts/checks.txt", "missing-target"),
        NavigationIssue("review-b.html", "artifacts/checks.txt", "missing-target"),
    ]
    assert _snapshot(relocated) == broken
    assert _snapshot(original) == before
    assert check_bundle(original) == []
