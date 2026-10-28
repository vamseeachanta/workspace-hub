"""CLI boundary tests use only synthetic files in the approved scratch directory."""

import json
import tempfile
from pathlib import Path

import pytest
from test_exposure import record_data

from src.workspace_hub.exposure.cli import main


@pytest.fixture
def registry_path():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "registry.json"
        path.write_text(json.dumps({"schema_version": 1, "records": [record_data()]}))
        yield path


def test_configured_registry_lookup(registry_path, monkeypatch, capsys):
    monkeypatch.setenv("DATA_REGISTRY_PATH", str(registry_path))
    assert main(["--id", "V-0107", "--surface", "newsletter"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["fields"]["name"] == "bulk carrier A"
    assert "id" not in output


def test_client_lookup(registry_path, capsys):
    assert (
        main(
            [
                "--registry",
                str(registry_path),
                "--id",
                "V-0107",
                "--surface",
                "client",
                "--client-id",
                "C-0004",
            ]
        )
        == 0
    )
    assert (
        json.loads(capsys.readouterr().out)["fields"]["name"] == "Synthetic Hull Zephyr"
    )


@pytest.mark.parametrize(
    "payload",
    [
        '{"schema_version":1,"records":[],"records":[]}',
        '{"schema_version":1,"records":NaN}',
        '{"schema_version":2,"records":[]}',
        '{"schema_version":true,"records":[]}',
        "{",
    ],
)
def test_malformed_registry_has_no_payload_or_path_in_errors(
    registry_path, capsys, payload
):
    registry_path.write_text(payload)
    assert (
        main(
            [
                "--registry",
                str(registry_path),
                "--id",
                "V-0107",
                "--surface",
                "newsletter",
            ]
        )
        == 2
    )
    result = capsys.readouterr()
    assert result.out == ""
    assert str(registry_path) not in result.err
    assert "Traceback" not in result.err


def test_duplicate_ids_refused(registry_path, capsys):
    registry_path.write_text(
        json.dumps({"schema_version": 1, "records": [record_data(), record_data()]})
    )
    assert (
        main(
            [
                "--registry",
                str(registry_path),
                "--id",
                "V-0107",
                "--surface",
                "internal",
            ]
        )
        == 2
    )
    assert not capsys.readouterr().out


def test_missing_config_does_not_search_worktree(monkeypatch, capsys):
    monkeypatch.delenv("DATA_REGISTRY_PATH", raising=False)
    assert main(["--id", "V-0107", "--surface", "newsletter"]) == 2
    assert not capsys.readouterr().out


def test_unknown_id_has_no_output(registry_path, capsys):
    assert (
        main(
            [
                "--registry",
                str(registry_path),
                "--id",
                "V-9999",
                "--surface",
                "newsletter",
            ]
        )
        == 2
    )
    assert not capsys.readouterr().out


def test_registry_wide_real_name_scan(registry_path, capsys):
    first = record_data()
    second = record_data()
    second["id"] = "V-0108"
    second["fields"]["name"]["value"] = "Synthetic Hull Nimbus"
    first["fields"]["region"]["value"] = "Synthetic Hull Nimbus"
    registry_path.write_text(
        json.dumps({"schema_version": 1, "records": [first, second]})
    )
    assert (
        main(
            [
                "--registry",
                str(registry_path),
                "--id",
                "V-0107",
                "--surface",
                "newsletter",
            ]
        )
        == 2
    )
    assert not capsys.readouterr().out


def test_module_entrypoint(registry_path):
    import os
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.workspace_hub.exposure",
            "--registry",
            str(registry_path),
            "--id",
            "V-0107",
            "--surface",
            "public_repository",
        ],
        capture_output=True,
        text=True,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}
        },
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["fields"]["name"] == "bulk carrier A"


def test_refusal_never_emits_partial_json(registry_path, capsys):
    data = record_data()
    data["singling_out"]["combinations"] = [["name", "capacity"]]
    registry_path.write_text(json.dumps({"schema_version": 1, "records": [data]}))
    assert (
        main(
            [
                "--registry",
                str(registry_path),
                "--id",
                "V-0107",
                "--surface",
                "newsletter",
            ]
        )
        == 2
    )
    assert not capsys.readouterr().out
