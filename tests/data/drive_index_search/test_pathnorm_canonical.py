from __future__ import annotations

from pathlib import Path

import pytest

from pathnorm import canonicalize, canonicalize_path, is_canonical, load_alias_map


ALIASES = {
    "/mnt/remote/ace-linux-1/ace": "/mnt/ace",  # abs-path-allowed
    "/mnt/remote/ace-linux-2/dde": "/mnt/dde",  # abs-path-allowed
    "/mnt/remote/dev-secondary/dde": "/mnt/dde",  # abs-path-allowed
    "/mnt/ace-data": "/mnt/ace",  # abs-path-allowed
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("/mnt/remote/dev-secondary/dde/Literature/x.pdf", "/mnt/dde/Literature/x.pdf"),  # abs-path-allowed
        ("/mnt/remote/ace-linux-2/dde/documents/y.xlsx", "/mnt/dde/documents/y.xlsx"),  # abs-path-allowed
        ("/mnt/dde/documents/y.xlsx", "/mnt/dde/documents/y.xlsx"),  # abs-path-allowed
        ("/mnt/ace/docs/a.pdf", "/mnt/ace/docs/a.pdf"),  # abs-path-allowed
        ("/mnt/remote/ace-linux-1/ace/data/document-index/summaries", "/mnt/ace/data/document-index/summaries"),  # abs-path-allowed
        ("/mnt/ace-data/digitalmodel/docs/z.md", "/mnt/ace/digitalmodel/docs/z.md"),  # abs-path-allowed
    ],
)
def test_canonicalize_alias_table(raw: str, expected: str) -> None:
    assert canonicalize_path(raw, ALIASES) == expected


def test_canonicalize_no_partial_segment_match() -> None:
    assert canonicalize_path("/mnt/remote/ace-linux-2/dde-extra/z", ALIASES) == "/mnt/remote/ace-linux-2/dde-extra/z"  # abs-path-allowed


def test_load_alias_map_from_registry(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yml"
    registry.write_text(
        "canonical_aliases:\n"
        "  /mnt/remote/ace-linux-2/dde: /mnt/dde\n"  # abs-path-allowed
        "  /mnt/remote/ace-linux-1/ace: /mnt/ace\n"  # abs-path-allowed
    )
    aliases = load_alias_map(registry)
    assert list(aliases) == ["/mnt/remote/ace-linux-2/dde", "/mnt/remote/ace-linux-1/ace"]  # abs-path-allowed
    assert canonicalize("/mnt/remote/ace-linux-1/ace/x", aliases) == "/mnt/ace/x"  # abs-path-allowed


def test_load_alias_map_rejects_noncanonical_value(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yml"
    registry.write_text("canonical_aliases:\n  /legacy: /mnt/remote/x/y\n")  # abs-path-allowed
    with pytest.raises(ValueError, match="non-canonical alias value"):
        load_alias_map(registry)


def test_is_canonical() -> None:
    assert is_canonical("/mnt/dde/documents/y.xlsx", ALIASES)  # abs-path-allowed
    assert not is_canonical("/mnt/remote/ace-linux-2/dde/documents/y.xlsx", ALIASES)  # abs-path-allowed
    assert not is_canonical("/mnt/remote/unknown/q", ALIASES)  # abs-path-allowed
