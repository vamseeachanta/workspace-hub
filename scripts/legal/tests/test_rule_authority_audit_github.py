"""Hermetic GitHub-surface inventory tests for rule-authority Phase A2."""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_github  # noqa: E402


class FixtureAdapter:
    def __init__(self, pages: dict[str, list[audit_github.ApiPage]]) -> None:
        self.pages = pages

    def snapshot(self) -> str:
        return "snapshot-1"

    def page(self, surface: str, cursor: str | None) -> audit_github.ApiPage:
        index = int(cursor or "0")
        return self.pages[surface][index]


def _empty_pages() -> dict[str, list[audit_github.ApiPage]]:
    return {
        surface: [audit_github.ApiPage(b"", None, "etag-empty", 0)]
        for surface in audit_github.REQUIRED_SURFACES
    }


def test_inventory_requires_every_surface_and_records_bytes() -> None:
    assert {"commits", "git-trees", "rulesets"} <= set(audit_github.REQUIRED_SURFACES)
    pages = _empty_pages()
    pages["issues"] = [audit_github.ApiPage(b"synthetic bytes", None, "etag-1", 1)]
    report = audit_github.inventory(FixtureAdapter(pages), max_pages=30, max_bytes=1000)
    assert set(report.surfaces) == set(audit_github.REQUIRED_SURFACES)
    assert report.surfaces["issues"].bytes_scanned == 15
    assert report.surfaces["issues"].state == "scanned"
    assert report.coverage_class == "complete"


def test_inventory_paginates_and_rejects_cursor_cycle() -> None:
    pages = _empty_pages()
    pages["comments"] = [
        audit_github.ApiPage(b"a", "1", "e1", 1),
        audit_github.ApiPage(b"b", None, "e2", 1),
    ]
    report = audit_github.inventory(FixtureAdapter(pages), max_pages=40, max_bytes=1000)
    assert report.surfaces["comments"].pages == 2
    pages["comments"] = [audit_github.ApiPage(b"a", "0", "e1", 1)]
    with pytest.raises(audit_github.CoverageError):
        audit_github.inventory(FixtureAdapter(pages), max_pages=40, max_bytes=1000)


def test_inventory_caps_are_fail_closed() -> None:
    pages = _empty_pages()
    pages["issues"] = [audit_github.ApiPage(b"too-large", None, "etag", 1)]
    with pytest.raises(audit_github.CoverageError):
        audit_github.inventory(FixtureAdapter(pages), max_pages=30, max_bytes=3)
    with pytest.raises(audit_github.CoverageError):
        audit_github.inventory(FixtureAdapter(pages), max_pages=1, max_bytes=1000)


def test_inventory_records_no_access_and_residual_without_clean_claim() -> None:
    pages = _empty_pages()
    pages["forks"] = [audit_github.ApiPage.no_access("permission-denied")]
    report = audit_github.inventory(FixtureAdapter(pages), max_pages=30, max_bytes=1000)
    assert report.surfaces["forks"].state == "queried-no-access"
    assert report.coverage_class == "partial"


def test_inventory_snapshot_drift_fails_closed() -> None:
    class DriftingAdapter(FixtureAdapter):
        calls = 0

        def snapshot(self) -> str:
            self.calls += 1
            return f"snapshot-{self.calls}"

    with pytest.raises(audit_github.CoverageError):
        audit_github.inventory(DriftingAdapter(_empty_pages()), max_pages=30, max_bytes=1000)


def test_inventory_rejects_missing_surface() -> None:
    pages = _empty_pages()
    pages.pop("wiki")
    with pytest.raises(audit_github.CoverageError):
        audit_github.inventory(FixtureAdapter(pages), max_pages=30, max_bytes=1000)


def _zip(entries: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    return output.getvalue()


def test_archive_adapter_is_bounded_and_rejects_traversal() -> None:
    result = audit_github.scan_zip(
        _zip({"safe.txt": b"safe"}), max_entries=2, max_expanded_bytes=10,
        max_ratio=20, max_depth=2,
    )
    assert result == {"safe.txt": b"safe"}
    with pytest.raises(audit_github.CoverageError):
        audit_github.scan_zip(
            _zip({"../escape": b"x"}), max_entries=2, max_expanded_bytes=10,
            max_ratio=20, max_depth=2,
        )


def test_archive_adapter_rejects_count_size_ratio_and_depth_caps() -> None:
    cases = [
        (_zip({"a": b"a", "b": b"b"}), {"max_entries": 1, "max_expanded_bytes": 10,
                                             "max_ratio": 20, "max_depth": 2}),
        (_zip({"a": b"abc"}), {"max_entries": 2, "max_expanded_bytes": 2,
                                  "max_ratio": 20, "max_depth": 2}),
        (_zip({"a": b"a" * 1000}), {"max_entries": 2, "max_expanded_bytes": 2000,
                                       "max_ratio": 2, "max_depth": 2}),
        (_zip({"a/b/c": b"x"}), {"max_entries": 2, "max_expanded_bytes": 10,
                                    "max_ratio": 20, "max_depth": 2}),
    ]
    for raw, limits in cases:
        with pytest.raises(audit_github.CoverageError):
            audit_github.scan_zip(raw, **limits)
