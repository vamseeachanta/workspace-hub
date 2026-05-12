from __future__ import annotations

import json
from pathlib import Path

from scripts.preflight.checks import build_report, parse_probe_output
from scripts.preflight.render import render_json, render_markdown, write_artifacts


FIXTURES = Path(__file__).parent / "fixtures"


def _sample_report() -> dict:
    probe = parse_probe_output((FIXTURES / "auth-invalid.txt").read_text())
    return build_report(
        probe,
        target={
            "name": "ace-linux-2",
            "hostname": "ace-linux-2",
            "role": "secondary-dev",
            "workspace_root": "/mnt/workspace-hub",
        },
        from_host="ace-linux-1",
        invocation={"mode": "fixture"},
    )


def test_json_renderer_has_frozen_schema_version() -> None:
    data = json.loads(render_json(_sample_report()))

    assert data["schema_version"] == "1"
    assert data["summary"]["github_mutation_allowed"] is False


def test_markdown_renderer_names_github_mutation_blocker() -> None:
    markdown = render_markdown(_sample_report())

    assert "# Hermes Preflight" in markdown
    assert "github_mutation" in markdown
    assert "gho_" not in markdown


def test_write_artifacts_creates_json_and_markdown(tmp_path: Path) -> None:
    artifacts = write_artifacts(_sample_report(), tmp_path)

    assert artifacts["json"].exists()
    assert artifacts["markdown"].exists()
    assert artifacts["json"].suffix == ".json"
    assert artifacts["markdown"].suffix == ".md"
