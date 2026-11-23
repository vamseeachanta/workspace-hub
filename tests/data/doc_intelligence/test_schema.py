"""Tests for doc_intelligence schema — round-trip YAML, validation, atomic write."""

import yaml
from pathlib import Path

from scripts.data.doc_intelligence.schema import (
    DocumentManifest,
    DocumentMetadata,
    ExtractedFigureRef,
    ExtractedSection,
    ExtractedTable,
    SourceLocation,
    manifest_to_dict,
    manifest_from_dict,
    write_manifest,
)


def _make_manifest() -> DocumentManifest:
    """Build a minimal valid manifest for testing."""
    src = SourceLocation(document="test.pdf", page=1)
    return DocumentManifest(
        version="1.0.0",
        tool="extract-document/1.0.0",
        domain="naval-architecture",
        metadata=DocumentMetadata(
            filename="test.pdf",
            format="pdf",
            size_bytes=12345,
            pages=2,
            checksum="abc123",
            extraction_timestamp="2026-03-12T00:00:00",
        ),
        sections=[
            ExtractedSection(heading="Intro", level=1, text="Hello", source=src),
        ],
        tables=[
            ExtractedTable(
                title="Table 1",
                columns=["A", "B"],
                rows=[["1", "2"]],
                source=src,
            ),
        ],
        figure_refs=[
            ExtractedFigureRef(caption="Fig 1", figure_id="Figure 1", source=src),
        ],
        extraction_stats={"sections": 1, "tables": 1, "figure_refs": 1},
        errors=[],
    )


class TestManifestRoundTrip:
    """manifest_to_dict → YAML dump → YAML load → manifest_from_dict."""

    def test_round_trip_preserves_data(self):
        m = _make_manifest()
        d = manifest_to_dict(m)
        yaml_str = yaml.dump(d, default_flow_style=False)
        loaded = yaml.safe_load(yaml_str)
        m2 = manifest_from_dict(loaded)
        assert m2.version == m.version
        assert m2.domain == m.domain
        assert m2.metadata.filename == "test.pdf"
        assert len(m2.sections) == 1
        assert len(m2.tables) == 1
        assert len(m2.figure_refs) == 1

    def test_round_trip_section_source(self):
        m = _make_manifest()
        d = manifest_to_dict(m)
        m2 = manifest_from_dict(d)
        assert m2.sections[0].source.page == 1
        assert m2.sections[0].source.document == "test.pdf"


class TestManifestValidation:
    """Validate required fields and error handling."""

    def test_valid_manifest_has_all_fields(self):
        m = _make_manifest()
        d = manifest_to_dict(m)
        for key in ("version", "tool", "domain", "metadata", "sections",
                     "tables", "figure_refs", "extraction_stats", "errors"):
            assert key in d

    def test_empty_sections_is_valid(self):
        m = _make_manifest()
        m.sections = []
        m.extraction_stats["sections"] = 0
        d = manifest_to_dict(m)
        m2 = manifest_from_dict(d)
        assert m2.sections == []

    def test_errors_list_preserved(self):
        m = _make_manifest()
        m.errors = ["page 3 extraction failed", "table on page 5 malformed"]
        d = manifest_to_dict(m)
        m2 = manifest_from_dict(d)
        assert len(m2.errors) == 2
        assert "page 3" in m2.errors[0]


class TestAtomicWrite:
    """write_manifest uses atomic os.replace."""

    def test_write_creates_file(self, tmp_dir):
        m = _make_manifest()
        out = tmp_dir / "out.manifest.yaml"
        write_manifest(m, out)
        assert out.exists()
        loaded = yaml.safe_load(out.read_text())
        assert loaded["version"] == "1.0.0"
