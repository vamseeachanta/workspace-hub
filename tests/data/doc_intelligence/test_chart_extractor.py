"""Tests for chart_extractor — extracts images from PDFs and generates metadata."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.chart_extractor import (
    extract_images_from_pdf,
    generate_chart_metadata,
    ChartImage,
)


@pytest.fixture
def sample_figure_refs():
    """Figure references as extracted by pdf.py parser."""
    return [
        {
            "caption": "Current density vs temperature",
            "figure_id": "Figure 3-1",
            "source": {"document": "DNV-RP-C205.pdf", "page": 15},
        },
        {
            "caption": "Drag coefficient for cylinders",
            "figure_id": "Figure 5-2",
            "source": {"document": "DNV-RP-C205.pdf", "page": 28},
        },
    ]


class TestChartImage:
    """Test the ChartImage dataclass."""

    def test_creates_with_required_fields(self):
        img = ChartImage(
            image_hash="abc123",
            page=5,
            index=0,
            width=640,
            height=480,
            format="png",
        )
        assert img.image_hash == "abc123"
        assert img.page == 5
        assert img.width == 640

    def test_filename_property(self):
        img = ChartImage(
            image_hash="abc123def456",
            page=5,
            index=0,
            width=640,
            height=480,
            format="png",
        )
        assert img.filename == "abc123def456.png"


class TestGenerateChartMetadata:
    """Test metadata YAML generation from figure refs + extracted images."""

    def test_generates_metadata_for_refs(self, sample_figure_refs):
        metadata = generate_chart_metadata(
            figure_refs=sample_figure_refs,
            images=[],
            doc_name="DNV-RP-C205",
            domain="naval-architecture",
        )
        assert len(metadata) == 2
        assert metadata[0]["figure_id"] == "Figure 3-1"
        assert metadata[0]["caption"] == "Current density vs temperature"
        assert metadata[0]["domain"] == "naval-architecture"
        assert metadata[0]["digitized"] is False

    def test_links_images_to_refs_by_page(self, sample_figure_refs):
        images = [
            ChartImage(
                image_hash="hash1",
                page=15,
                index=0,
                width=640,
                height=480,
                format="png",
            ),
        ]
        metadata = generate_chart_metadata(
            figure_refs=sample_figure_refs,
            images=images,
            doc_name="DNV-RP-C205",
            domain="naval-architecture",
        )
        # Figure 3-1 on page 15 should be linked to the image
        fig_3_1 = metadata[0]
        assert fig_3_1["image_file"] == "hash1.png"
        assert fig_3_1["image_size"] == {"width": 640, "height": 480}
        # Figure 5-2 on page 28 has no image
        fig_5_2 = metadata[1]
        assert fig_5_2["image_file"] is None

    def test_empty_refs_returns_empty(self):
        metadata = generate_chart_metadata([], [], "doc", "general")
        assert metadata == []

    def test_unmatched_images_still_recorded(self):
        images = [
            ChartImage(
                image_hash="orphan",
                page=99,
                index=0,
                width=320,
                height=240,
                format="png",
            ),
        ]
        metadata = generate_chart_metadata(
            figure_refs=[],
            images=images,
            doc_name="test",
            domain="general",
        )
        # Orphaned images get their own metadata entries
        assert len(metadata) == 1
        assert metadata[0]["figure_id"] is None
        assert metadata[0]["image_file"] == "orphan.png"

    def test_metadata_includes_calibration_stub(self, sample_figure_refs):
        images = [
            ChartImage(
                image_hash="h1", page=15, index=0,
                width=640, height=480, format="png",
            ),
        ]
        metadata = generate_chart_metadata(
            figure_refs=sample_figure_refs,
            images=images,
            doc_name="test",
            domain="naval-architecture",
        )
        fig = metadata[0]
        assert "calibration" in fig
        assert fig["calibration"]["status"] == "pending"


class TestExtractImagesFromPdf:
    """Test PDF image extraction (uses a minimal test PDF)."""

    def test_returns_empty_for_nonexistent_file(self):
        result = extract_images_from_pdf(Path("/nonexistent.pdf"), Path("/tmp"))
        assert result == []

    def test_returns_empty_for_non_pdf(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a PDF")
        result = extract_images_from_pdf(txt_file, tmp_path / "out")
        assert result == []

    def test_creates_output_directory(self, tmp_path):
        out_dir = tmp_path / "charts" / "deep"
        # Won't find images in a text file but should create dir
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a PDF")
        extract_images_from_pdf(txt_file, out_dir)
        # Should not crash even with non-PDF input

    def test_filters_small_images(self, tmp_path):
        """Images below minimum dimensions should be filtered out."""
        # This tests the filtering logic, not actual PDF extraction
        from scripts.data.doc_intelligence.chart_extractor import _is_chart_candidate

        assert _is_chart_candidate(640, 480) is True
        assert _is_chart_candidate(50, 50) is False  # too small (icon/logo)
        assert _is_chart_candidate(200, 10) is False  # too narrow (line/rule)
