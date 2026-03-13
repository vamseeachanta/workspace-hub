"""Tests for extract-document CLI entry point."""

import os
import subprocess
import sys

import yaml
from pathlib import Path

SCRIPT = str(
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "data"
    / "doc-intelligence"
    / "extract-document.py"
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


class TestCliExitCodes:
    def test_missing_input_exits_nonzero(self):
        r = _run_cli()
        assert r.returncode != 0

    def test_missing_file_exits_1(self):
        r = _run_cli("--input", "/nonexistent/file.pdf")
        assert r.returncode == 1

    def test_unsupported_format_exits_2(self, tmp_dir):
        txt = tmp_dir / "readme.txt"
        txt.write_text("hello")
        r = _run_cli("--input", str(txt))
        assert r.returncode == 2


class TestCliDryRun:
    def test_dry_run_does_not_write(self, sample_pdf, tmp_dir):
        out = tmp_dir / "output.yaml"
        r = _run_cli(
            "--input", str(sample_pdf),
            "--output", str(out),
            "--domain", "test",
            "--dry-run",
        )
        assert r.returncode == 0
        assert not out.exists()

    def test_dry_run_prints_stats(self, sample_pdf):
        r = _run_cli(
            "--input", str(sample_pdf),
            "--domain", "test",
            "--dry-run",
        )
        assert r.returncode == 0
        assert "sections" in r.stdout.lower()


class TestCliExtraction:
    def test_valid_input_produces_yaml(self, sample_pdf, tmp_dir):
        out = tmp_dir / "out.manifest.yaml"
        r = _run_cli("--input", str(sample_pdf), "--output", str(out))
        assert r.returncode == 0
        loaded = yaml.safe_load(out.read_text())
        assert loaded["version"] == "1.0.0"

    def test_domain_propagated(self, sample_pdf, tmp_dir):
        out = tmp_dir / "out.manifest.yaml"
        r = _run_cli(
            "--input", str(sample_pdf),
            "--output", str(out),
            "--domain", "naval-architecture",
        )
        assert r.returncode == 0
        loaded = yaml.safe_load(out.read_text())
        assert loaded["domain"] == "naval-architecture"

    def test_doc_ref_in_manifest(self, sample_pdf, tmp_dir):
        out = tmp_dir / "out.manifest.yaml"
        r = _run_cli(
            "--input", str(sample_pdf),
            "--output", str(out),
            "--domain", "test",
            "--doc-ref", "custom-ref-123",
        )
        assert r.returncode == 0
        loaded = yaml.safe_load(out.read_text())
        assert loaded["doc_ref"] == "custom-ref-123"

    def test_verbose_prints_details(self, sample_pdf):
        r = _run_cli(
            "--input", str(sample_pdf),
            "--domain", "test",
            "--dry-run",
            "--verbose",
        )
        assert r.returncode == 0
        assert "format" in r.stdout.lower()
