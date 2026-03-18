#!/usr/bin/env python3
"""Tests for PDF tool benchmark script."""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Import will work after we create the module
SCRIPT_DIR = Path(__file__).parent.parent
BENCHMARK_SCRIPT = SCRIPT_DIR / "benchmark_pdf_tools.py"


def find_test_pdf():
    """Find a single accessible PDF for testing."""
    candidates = [
        Path("/mnt/local-analysis/workspace-hub/digitalmodel/docs/Padeye Design Guide TP2016-001-Rev01.pdf"),
        Path("/mnt/local-analysis/workspace-hub/.claude/skills/_internal/builders/skill-creator/references/anthropic-complete-guide-building-skills.pdf"),
    ]
    for p in candidates:
        if p.exists():
            return p
    pytest.skip("No test PDF available")


class TestPypdfium2Extraction:
    """Test pypdfium2 can extract text from PDFs."""

    def test_import_pypdfium2(self):
        import pypdfium2
        assert hasattr(pypdfium2, "PdfDocument")

    def test_extract_text_basic(self):
        pdf_path = find_test_pdf()
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(str(pdf_path))
        assert len(doc) > 0
        page = doc[0]
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        assert len(text) > 0
        doc.close()

    def test_extract_all_pages(self):
        pdf_path = find_test_pdf()
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(str(pdf_path))
        texts = []
        for page in doc:
            tp = page.get_textpage()
            texts.append(tp.get_text_range())
        doc.close()
        full_text = "\n".join(texts)
        assert len(full_text) > 50


class TestPdftotext:
    """Test pdftotext subprocess baseline."""

    def test_pdftotext_available(self):
        result = subprocess.run(
            ["which", "pdftotext"], capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_extract_text(self):
        pdf_path = find_test_pdf()
        result = subprocess.run(
            ["pdftotext", "-q", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert len(result.stdout) > 50


class TestReadabilityClassification:
    """Test pypdfium2 can classify readability (replacing pdfplumber)."""

    def test_classify_machine_readable(self):
        pdf_path = find_test_pdf()
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(str(pdf_path))
        total = len(doc)
        max_pages = min(5, total)
        pages_with_text = 0
        for i in range(max_pages):
            tp = doc[i].get_textpage()
            text = tp.get_text_range().strip()
            if len(text) >= 50:
                pages_with_text += 1
        doc.close()

        ratio = pages_with_text / max_pages
        # Known machine-readable PDF should classify correctly
        assert ratio >= 0.8, f"Expected machine-readable, got ratio {ratio}"


class TestBenchmarkOutput:
    """Test that benchmark produces valid structured output."""

    def test_benchmark_script_exists(self):
        assert BENCHMARK_SCRIPT.exists(), f"Benchmark script not found at {BENCHMARK_SCRIPT}"

    def test_benchmark_runs(self):
        """Run benchmark on a tiny sample and verify output."""
        pdf_path = find_test_pdf()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            out_path = f.name

        try:
            result = subprocess.run(
                [
                    "uv", "run", "--no-project", "python3",
                    str(BENCHMARK_SCRIPT),
                    "--sample", "2",
                    "--output", out_path,
                    "--pdf-dir", str(pdf_path.parent),
                ],
                capture_output=True, text=True, timeout=60,
                cwd="/mnt/local-analysis/workspace-hub",
            )
            assert result.returncode == 0, f"stderr: {result.stderr}"
            assert os.path.exists(out_path)

            with open(out_path) as f:
                data = json.load(f)
            assert "results" in data
            assert "summary" in data
            assert len(data["results"]) > 0

            # Each result should have both tool timings
            for r in data["results"]:
                assert "pdftotext_seconds" in r
                assert "pypdfium2_seconds" in r
                assert "file" in r
        finally:
            os.unlink(out_path)
