"""Tests for the schemas CLI (__main__.py)."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from coordination.schemas.__main__ import main


@pytest.mark.unit
class TestCLI:
    def test_valid_file_exit_zero(self, tmp_path):
        data = {
            "last_id": 10,
            "last_processed": None,
            "created_at": "2026-01-29T00:00:00Z",
            "stats": {"total_captured": 10, "total_processed": 5, "total_archived": 3},
        }
        f = tmp_path / "state.yaml"
        f.write_text(yaml.dump(data))

        rc = main([str(f)])
        assert rc == 0

    def test_invalid_file_exit_one(self, tmp_path):
        data = {"last_id": -1, "created_at": "2026-01-29T00:00:00Z"}
        f = tmp_path / "state.yaml"
        f.write_text(yaml.dump(data))

        rc = main([str(f)])
        assert rc == 1

    def test_nonexistent_file_exit_one(self, tmp_path):
        f = tmp_path / "does-not-exist.yaml"
        rc = main([str(f)])
        assert rc == 1

    def test_json_output_valid(self, tmp_path, capsys):
        data = {
            "last_id": 10,
            "last_processed": None,
            "created_at": "2026-01-29T00:00:00Z",
            "stats": {"total_captured": 10, "total_processed": 5, "total_archived": 3},
        }
        f = tmp_path / "state.yaml"
        f.write_text(yaml.dump(data))

        rc = main([str(f), "--json"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["valid"] is True
        assert out["errors"] == []

    def test_json_output_invalid(self, tmp_path, capsys):
        data = {"last_id": -1, "created_at": "2026-01-29T00:00:00Z"}
        f = tmp_path / "state.yaml"
        f.write_text(yaml.dump(data))

        rc = main([str(f), "--json"])
        assert rc == 1
        out = json.loads(capsys.readouterr().out)
        assert out["valid"] is False
        assert len(out["errors"]) > 0

    def test_unknown_schema_file(self, tmp_path):
        f = tmp_path / "unknown.yaml"
        f.write_text("key: value")

        rc = main([str(f)])
        assert rc == 1

    def test_json_output_nonexistent(self, tmp_path, capsys):
        f = tmp_path / "state.yaml"
        rc = main([str(f), "--json"])
        assert rc == 1
        out = json.loads(capsys.readouterr().out)
        assert out["valid"] is False
