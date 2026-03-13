"""Tests for the federated index builder."""

import csv
import json
import shutil
from pathlib import Path

import pytest
import yaml

from scripts.data.doc_intelligence.index_builder import BuildStats, build_indexes

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def manifest_dir(tmp_dir):
    """Copy fixture manifests into a tmp subdirectory structure."""
    domain_dir = tmp_dir / "manifests" / "offshore"
    domain_dir.mkdir(parents=True)
    for f in FIXTURES.glob("*.manifest.yaml"):
        shutil.copy(f, domain_dir / f.name)
    return tmp_dir / "manifests"


@pytest.fixture
def output_dir(tmp_dir):
    """Provide a clean output directory."""
    out = tmp_dir / "output"
    out.mkdir()
    return out


def _read_jsonl(path):
    """Read a JSONL file into a list of dicts."""
    records = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


class TestBuildIndexes:
    def test_returns_build_stats(self, manifest_dir, output_dir):
        stats = build_indexes(manifest_dir, output_dir)
        assert isinstance(stats, BuildStats)
        assert stats.manifests_processed == 3
        assert stats.manifests_skipped == 0

    def test_creates_manifest_index(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        idx = output_dir / "manifest-index.jsonl"
        assert idx.exists()
        records = _read_jsonl(idx)
        assert len(records) == 3
        filenames = {r["filename"] for r in records}
        assert "mixed-content.pdf" in filenames
        assert "tables-only.xlsx" in filenames
        assert "empty.pdf" in filenames

    def test_manifest_index_has_checksum(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        records = _read_jsonl(output_dir / "manifest-index.jsonl")
        for r in records:
            assert "checksum" in r
            assert r["checksum"]  # non-empty

    def test_manifest_index_has_counts(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        records = _read_jsonl(output_dir / "manifest-index.jsonl")
        mixed = [r for r in records if r["filename"] == "mixed-content.pdf"][0]
        assert mixed["counts"]["tables"] == 2
        assert mixed["counts"]["figure_refs"] == 2

    def test_creates_constants_jsonl(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        path = output_dir / "constants.jsonl"
        assert path.exists()
        records = _read_jsonl(path)
        assert len(records) >= 1
        assert records[0]["domain"] == "offshore"
        assert "source" in records[0]

    def test_creates_equations_jsonl(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        path = output_dir / "equations.jsonl"
        assert path.exists()
        records = _read_jsonl(path)
        assert len(records) >= 1

    def test_creates_requirements_jsonl(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        path = output_dir / "requirements.jsonl"
        assert path.exists()
        records = _read_jsonl(path)
        assert len(records) >= 1

    def test_creates_procedures_jsonl(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        path = output_dir / "procedures.jsonl"
        assert path.exists()

    def test_creates_definitions_jsonl(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        path = output_dir / "definitions.jsonl"
        assert path.exists()

    def test_creates_worked_examples_jsonl(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        path = output_dir / "worked_examples.jsonl"
        assert path.exists()

    def test_tables_csv_created(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        tables_dir = output_dir / "tables"
        assert tables_dir.exists()
        csvs = list(tables_dir.glob("*.csv"))
        assert len(csvs) >= 2  # at least mixed-content + tables-only

    def test_tables_index_created(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        idx = output_dir / "tables" / "index.jsonl"
        assert idx.exists()
        records = _read_jsonl(idx)
        # mixed-content has 2 tables, tables-only has 2 tables = 4 total
        assert len(records) == 4
        for r in records:
            assert "csv_path" in r
            assert "columns" in r
            assert "row_count" in r

    def test_table_csv_content(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        idx = _read_jsonl(output_dir / "tables" / "index.jsonl")
        mat_props = [r for r in idx if r["title"] == "Material Properties"][0]
        csv_path = output_dir / mat_props["csv_path"]
        assert csv_path.exists()
        with open(csv_path) as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert rows[0] == ["Material", "Yield (MPa)", "UTS (MPa)"]
        assert len(rows) == 3  # header + 2 data rows

    def test_curves_dir_created(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        curves_dir = output_dir / "curves"
        assert curves_dir.exists()
        idx = output_dir / "curves" / "index.jsonl"
        assert idx.exists()
        records = _read_jsonl(idx)
        # mixed-content has 2 figure_refs, tables-only has 1
        assert len(records) == 3

    def test_curves_index_fields(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        records = _read_jsonl(output_dir / "curves" / "index.jsonl")
        for r in records:
            assert "caption" in r
            assert "figure_id" in r
            assert "source" in r
            assert "domain" in r

    def test_empty_manifest_no_crash(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        records = _read_jsonl(output_dir / "manifest-index.jsonl")
        empty = [r for r in records if r["filename"] == "empty.pdf"][0]
        assert empty["counts"]["sections"] == 0
        assert empty["counts"]["tables"] == 0

    def test_unclassified_sections_skipped(self, manifest_dir, output_dir):
        """The 'General Notes' section should not appear in any content index."""
        build_indexes(manifest_dir, output_dir)
        all_texts = []
        for name in [
            "constants", "equations", "requirements",
            "procedures", "definitions", "worked_examples",
        ]:
            path = output_dir / f"{name}.jsonl"
            if path.exists():
                all_texts.extend(r["text"] for r in _read_jsonl(path))
        assert not any("general notes" in t.lower() for t in all_texts)


class TestIncrementalBuild:
    def test_second_run_skips_unchanged(self, manifest_dir, output_dir):
        stats1 = build_indexes(manifest_dir, output_dir)
        assert stats1.manifests_processed == 3

        stats2 = build_indexes(manifest_dir, output_dir)
        assert stats2.manifests_skipped == 3
        assert stats2.manifests_processed == 0

    def test_content_survives_incremental(self, manifest_dir, output_dir):
        """Index content must not be erased when all manifests are skipped."""
        build_indexes(manifest_dir, output_dir)
        tables_before = _read_jsonl(output_dir / "tables" / "index.jsonl")

        build_indexes(manifest_dir, output_dir)
        tables_after = _read_jsonl(output_dir / "tables" / "index.jsonl")
        assert len(tables_after) == len(tables_before)
        assert len(tables_after) == 4

    def test_force_rebuilds_all(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        stats = build_indexes(manifest_dir, output_dir, force=True)
        assert stats.manifests_processed == 3
        assert stats.manifests_skipped == 0

    def test_modified_manifest_detected(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)

        # Modify one manifest's checksum
        mf = list(manifest_dir.rglob("mixed-content.manifest.yaml"))[0]
        data = yaml.safe_load(mf.read_text())
        data["metadata"]["checksum"] = "changed999"
        mf.write_text(yaml.dump(data, default_flow_style=False))

        stats = build_indexes(manifest_dir, output_dir)
        assert stats.manifests_processed == 1
        assert stats.manifests_skipped == 2


class TestDryRun:
    def test_dry_run_no_writes(self, manifest_dir, output_dir):
        stats = build_indexes(manifest_dir, output_dir, dry_run=True)
        assert stats.manifests_processed == 3
        assert not (output_dir / "manifest-index.jsonl").exists()
        assert not (output_dir / "constants.jsonl").exists()


class TestAtomicWrites:
    def test_no_tmp_files_remain(self, manifest_dir, output_dir):
        build_indexes(manifest_dir, output_dir)
        tmp_files = list(output_dir.rglob("*.tmp"))
        assert len(tmp_files) == 0


class TestPathTraversalDefense:
    def test_malicious_doc_ref_sanitized(self, tmp_dir):
        """A doc_ref with path traversal must not write outside output_dir."""
        manifest_dir = tmp_dir / "manifests" / "evil"
        manifest_dir.mkdir(parents=True)
        output_dir = tmp_dir / "output"
        output_dir.mkdir()

        malicious = {
            "version": "1.0",
            "tool": "test",
            "domain": "test",
            "doc_ref": "../../etc/cron.d/evil",
            "metadata": {
                "filename": "evil.pdf",
                "format": "pdf",
                "size_bytes": 100,
                "checksum": "evil123",
            },
            "sections": [],
            "tables": [
                {
                    "title": "Bad Table",
                    "columns": ["a"],
                    "rows": [["1"]],
                    "source": {"document": "evil.pdf"},
                }
            ],
            "figure_refs": [],
        }
        mf = manifest_dir / "evil.manifest.yaml"
        mf.write_text(yaml.dump(malicious))

        build_indexes(manifest_dir, output_dir)

        # CSV must be inside output_dir/tables/, not escaped
        csvs = list((output_dir / "tables").glob("*.csv"))
        assert len(csvs) == 1
        assert ".." not in csvs[0].name
        # Verify nothing was written outside output_dir
        assert not (tmp_dir / "etc").exists()
