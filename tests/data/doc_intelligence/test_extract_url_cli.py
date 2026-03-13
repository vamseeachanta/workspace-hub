"""Tests for extract-url.py CLI — exit codes, dry-run, routing."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# The CLI module path
CLI_MODULE = "scripts.data.doc_intelligence.extract_url"

REPO_ROOT = str(Path(__file__).resolve().parents[3])


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run extract-url.py as a subprocess."""
    return subprocess.run(
        [
            sys.executable,
            str(Path(REPO_ROOT) / "scripts" / "data" / "doc-intelligence" / "extract-url.py"),
            *args,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestCliArgs:
    def test_missing_url_exits_nonzero(self):
        result = run_cli()
        assert result.returncode != 0

    def test_help_flag(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "--url" in result.stdout


class TestCliDryRun:
    @patch(f"{CLI_MODULE}.UrlFetcher")
    def test_dry_run_html_exits_zero(self, mock_fetcher_cls, tmp_dir):
        """Dry-run with a mock fetcher returning HTML content."""
        # This test imports and calls main() directly to control mocking
        from scripts.data.doc_intelligence.extract_url import main

        html_content = b"<html><body><p>Hello</p></body></html>"

        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher

        from scripts.data.doc_intelligence.fetcher import FetchResult

        mock_fetcher.fetch.return_value = FetchResult(
            content_bytes=html_content,
            content_type="text/html",
            cached=False,
            status_code=200,
        )

        exit_code = main([
            "--url", "https://example.com/page.html",
            "--domain", "test",
            "--dry-run",
        ])
        assert exit_code == 0

    @patch(f"{CLI_MODULE}.UrlFetcher")
    def test_dry_run_does_not_write_file(self, mock_fetcher_cls, tmp_dir):
        from scripts.data.doc_intelligence.extract_url import main
        from scripts.data.doc_intelligence.fetcher import FetchResult

        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch.return_value = FetchResult(
            content_bytes=b"<html><body><p>Test</p></body></html>",
            content_type="text/html",
            cached=False,
            status_code=200,
        )

        output = tmp_dir / "should-not-exist.yaml"
        exit_code = main([
            "--url", "https://example.com/page.html",
            "--domain", "test",
            "--output", str(output),
            "--dry-run",
        ])
        assert exit_code == 0
        assert not output.exists()


class TestCliFetchErrors:
    @patch(f"{CLI_MODULE}.UrlFetcher")
    def test_fetch_failure_exits_1(self, mock_fetcher_cls):
        from scripts.data.doc_intelligence.extract_url import main
        from scripts.data.doc_intelligence.fetcher import FetchResult

        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch.return_value = FetchResult(
            content_bytes=b"Not Found",
            content_type="text/html",
            cached=False,
            status_code=404,
        )

        exit_code = main([
            "--url", "https://example.com/missing",
            "--domain", "test",
            "--dry-run",
        ])
        assert exit_code == 1

    @patch(f"{CLI_MODULE}.UrlFetcher")
    def test_robots_blocked_exits_2(self, mock_fetcher_cls):
        from scripts.data.doc_intelligence.extract_url import main

        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch.return_value = None  # None = robots blocked

        exit_code = main([
            "--url", "https://example.com/blocked",
            "--domain", "test",
            "--dry-run",
        ])
        assert exit_code == 2


class TestCliRouting:
    @patch(f"{CLI_MODULE}.UrlFetcher")
    def test_pdf_url_routes_to_pdf_parser(self, mock_fetcher_cls, tmp_dir):
        """PDF content type should delegate to PdfParser."""
        from scripts.data.doc_intelligence.extract_url import main
        from scripts.data.doc_intelligence.fetcher import FetchResult

        # Create a minimal valid PDF fixture
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, "Test PDF content")
        pdf_path = tmp_dir / "test.pdf"
        pdf.output(str(pdf_path))
        pdf_bytes = pdf_path.read_bytes()

        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch.return_value = FetchResult(
            content_bytes=pdf_bytes,
            content_type="application/pdf",
            cached=False,
            status_code=200,
        )

        exit_code = main([
            "--url", "https://example.com/doc.pdf",
            "--domain", "test",
            "--dry-run",
            "--verbose",
        ])
        assert exit_code == 0


class TestCliOutputWrite:
    @patch(f"{CLI_MODULE}.UrlFetcher")
    def test_writes_manifest_yaml(self, mock_fetcher_cls, tmp_dir):
        from scripts.data.doc_intelligence.extract_url import main
        from scripts.data.doc_intelligence.fetcher import FetchResult

        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        mock_fetcher.fetch.return_value = FetchResult(
            content_bytes=b"<html><body><h1>Title</h1><p>Body</p></body></html>",
            content_type="text/html",
            cached=False,
            status_code=200,
        )

        output = tmp_dir / "out.manifest.yaml"
        exit_code = main([
            "--url", "https://example.com/page.html",
            "--domain", "naval-architecture",
            "--output", str(output),
        ])
        assert exit_code == 0
        assert output.exists()

        import yaml

        manifest = yaml.safe_load(output.read_text())
        assert manifest["domain"] == "naval-architecture"
        assert manifest["tool"] == "extract-url/1.0.0"
        assert manifest["doc_ref"] is not None
