"""Offline preflight contract tests using synthetic registry entries.

The identity and version rules come from docs/registry/README.md, sections
"How consumers read it" and "Field-set", and workflow-manifest.schema.json.
Expected resolutions are selected by hand from the literal fixture rows;
expected totals are counts of those rows, never outputs of the implementation.
No engineering calculation or externally derived coefficient is used.
"""

from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
wr = importlib.import_module("workflow_readiness")

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "docs/registry/examples/workflow-readiness.json"
SCRIPT = ROOT / "scripts/workflow/workflow_readiness.py"


@pytest.fixture
def manifest():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_worked_example_resolves_flagged_stable(manifest):
    """By inspection: stable @1 is flagged; experimental @2 is not selected."""
    assert wr.resolve_workflow(manifest, "sample:screen")["workflow_id"] == "sample:screen@1"
    assert wr.resolve_workflow(manifest, "sample:screen@2")["version"] == 2


def test_resolution_does_not_mutate_manifest(manifest):
    original = copy.deepcopy(manifest)
    wr.audit_manifest(manifest)
    assert manifest == original


@pytest.mark.parametrize("ref", ["missing:screen", "sample:screen@3", "", "sample:screen@0"])
def test_unknown_reference_rejected(manifest, ref):
    with pytest.raises(wr.ManifestError):
        wr.resolve_workflow(manifest, ref)


@pytest.mark.parametrize("field,value", [
    ("manifest_version", True), ("manifest_version", 2),
    ("workflow_count", 9), ("workflow_count", True),
    ("workflows", {}), ("repos", {}), ("latest_by_routing_id", []),
])
def test_invalid_manifest_structure(manifest, field, value):
    manifest[field] = value
    with pytest.raises(wr.ManifestError):
        wr.audit_manifest(manifest)


@pytest.mark.parametrize("field,value", [
    ("workflow_id", "sample:other@1"), ("routing_id", "other:screen"),
    ("repo", "../sample"), ("id", "../screen"),
    ("version", True), ("version", 0), ("version", "1"),
    ("latest", "false"), ("status", None),
])
def test_inconsistent_row_rejected(manifest, field, value):
    manifest["workflows"][0][field] = value
    with pytest.raises(wr.ManifestError):
        wr.audit_manifest(manifest)


def test_duplicate_identity_rejected(manifest):
    manifest["workflows"].append(copy.deepcopy(manifest["workflows"][0]))
    manifest["workflow_count"] += 1
    with pytest.raises(wr.ManifestError):
        wr.audit_manifest(manifest)


@pytest.mark.parametrize("mapping", [
    {}, {"sample:screen": "sample:screen@2"},
    {"sample:screen": "missing:screen@1"},
    {"sample:screen": "sample:screen@1", "missing:screen": "sample:screen@1"},
])
def test_stale_or_cross_routing_index_rejected(manifest, mapping):
    manifest["latest_by_routing_id"] = mapping
    with pytest.raises(wr.ManifestError):
        wr.audit_manifest(manifest)


@pytest.mark.parametrize("stable,latest,expected", [
    (True, False, "sample:screen@2"),
    (True, True, "sample:screen@2"),
    (False, False, "sample:screen@2"),
])
def test_latest_selection_fallbacks(manifest, stable, latest, expected):
    """Highest stable wins; absent any stable row, highest version wins."""
    first, second = manifest["workflows"]
    first["latest"] = False
    first["status"] = "stable" if stable else "experimental"
    second["status"] = first["status"]
    second["latest"] = latest
    manifest["latest_by_routing_id"]["sample:screen"] = expected
    assert wr.resolve_workflow(manifest, "sample:screen")["workflow_id"] == expected


def checks_for(manifest):
    report = wr.audit_manifest(manifest, ["sample:screen"])
    return {c["name"]: c["status"] for c in report["workflows"][0]["checks"]}


def test_metadata_cannot_establish_live_readiness(manifest):
    """Seven declarations pass; five independent live checks lack evidence."""
    report = wr.audit_manifest(manifest, ["sample:screen"])
    statuses = checks_for(manifest)
    assert list(statuses.values()).count("PASS") == 7
    assert list(statuses.values()).count("NOT_EVALUATED") == 5
    assert report["status"] == "NOT_EVALUATED"
    assert report["workflow_count"] == 1
    assert report["blocked_count"] == 0
    assert report["not_evaluated_count"] == 1


def test_all_versions_are_audited_without_silent_filtering(manifest):
    """Two rows: stable @1 lacks live evidence; experimental @2 is blocked."""
    report = wr.audit_manifest(manifest)
    assert report["workflow_count"] == 2
    assert report["blocked_count"] == 1
    assert report["not_evaluated_count"] == 1
    assert report["status"] == "BLOCKED"


@pytest.mark.parametrize("runtime,gate,expected", [
    ("requires-license", True, "FAIL"),
    ("requires-license", False, "FAIL"),
    ("offline", True, "FAIL"),
    ("offline", None, "NOT_EVALUATED"),
    ("offline", "false", "FAIL"),
])
def test_license_declaration_fails_closed(manifest, runtime, gate, expected):
    row = manifest["workflows"][0]
    row.update(runtime=runtime, license_gated=gate)
    assert checks_for(manifest)["license_policy"] == expected


@pytest.mark.parametrize("runtime", [None, "fast", "uv-python", "unknown"])
def test_runtime_is_not_inferred_from_speed_or_tool(manifest, runtime):
    manifest["workflows"][0]["runtime"] = runtime
    assert checks_for(manifest)["offline_runtime"] == "NOT_EVALUATED"


@pytest.mark.parametrize("path", [
    None, "", "../input.json", "a/../input.json", "a\\b", "C:/input", "input\x7f.json",
])
def test_invalid_input_locator(manifest, path):
    manifest["workflows"][0]["input"] = path
    assert checks_for(manifest)["input_declared"] == "FAIL"


def test_absolute_input_locator(manifest, tmp_path):
    manifest["workflows"][0]["input"] = str(tmp_path / "input.json")
    assert checks_for(manifest)["input_declared"] == "FAIL"


@pytest.mark.parametrize("template", [
    None, "", "python tests/test_it.py", "python {other}",
    "python {input!r}", "python {input:>9}", "python {input", "python {{input}}",
])
def test_incomplete_invocation_is_blocked(manifest, template):
    manifest["workflows"][0]["invocation"] = template
    assert checks_for(manifest)["invocation_declared"] == "FAIL"


@pytest.mark.parametrize("descriptor,expected", [
    (None, "NOT_EVALUATED"), ({}, "FAIL"),
    ({"kind": "files"}, "PASS"), ({"kind": "in_memory"}, "PASS"),
    ({"kind": "unknown"}, "FAIL"), ("files", "FAIL"),
])
def test_result_declaration_is_distinct_from_delivery(manifest, descriptor, expected):
    manifest["workflows"][0]["result"] = descriptor
    checks = checks_for(manifest)
    assert checks["result_declared"] == expected
    assert checks["artifact_delivery"] == "NOT_EVALUATED"


@pytest.mark.parametrize("records", [[], [{"repo": "sample", "status": "missing-registry"}]])
def test_missing_provenance_is_not_readiness(manifest, records):
    manifest["repos"] = records
    assert checks_for(manifest)["registry_provenance"] == "NOT_EVALUATED"


def test_duplicate_repository_provenance_rejected(manifest):
    manifest["repos"] *= 2
    with pytest.raises(wr.ManifestError):
        wr.audit_manifest(manifest)


@pytest.mark.parametrize("digest", [None, "", "not-a-digest", "a" * 63])
def test_invalid_digest_is_not_verified(manifest, digest):
    manifest["repos"][0]["registry_sha256"] = digest
    assert checks_for(manifest)["registry_provenance"] == "NOT_EVALUATED"


@pytest.mark.parametrize("raw", [
    '{"workflows": [], "workflows": []}',
    '{"value": NaN}', '{"value": Infinity}', '{"value": 1e999}', '[]', '{bad json}',
])
def test_strict_json_loading(tmp_path, raw):
    path = tmp_path / "manifest.json"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(wr.ManifestError):
        wr.load_manifest(path)


def test_report_does_not_copy_arbitrary_source_fields(manifest):
    row = manifest["workflows"][0]
    row["title"] = "private-marker"
    row["invocation"] = "python -m private-marker {input}"
    row["input"] = "private-marker/input.json"
    assert "private-marker" not in json.dumps(wr.audit_manifest(manifest))


def test_html_escapes_untrusted_report_text():
    report = {"status": "NOT_EVALUATED", "workflow_count": 0,
              "blocked_count": 0, "not_evaluated_count": 0,
              "workflows": [{"workflow_id": "<script>alert(1)</script>",
                             "status": "BLOCKED", "checks": []}]}
    rendered = wr.render_html(report)
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


@pytest.mark.parametrize("args,code", [
    (["--ref", "sample:screen"], 0), ([], 1),
    (["--ref", "missing:screen"], 2),
])
def test_cli_json(args, code):
    run = subprocess.run([sys.executable, str(SCRIPT), str(EXAMPLE), *args],
                         capture_output=True, text=True, check=False)
    assert run.returncode == code
    if code != 2:
        assert json.loads(run.stdout)["status"] in {"BLOCKED", "NOT_EVALUATED"}
    else:
        assert run.stdout == ""
        assert "Cannot assess manifest" in run.stderr


def test_cli_html(capsys):
    assert wr.main([str(EXAMPLE), "--ref", "sample:screen", "--format", "html"]) == 0
    assert "<!doctype html>" in capsys.readouterr().out


def test_cli_missing_file_does_not_echo_path(tmp_path, capsys):
    assert wr.main([str(tmp_path / "private-marker.json")]) == 2
    assert "private-marker" not in capsys.readouterr().err


def test_duplicate_request_refs_are_counted_once(manifest):
    assert wr.audit_manifest(manifest, ["sample:screen", "sample:screen@1"])["workflow_count"] == 1


def test_empty_registry_has_no_readiness_claim(manifest):
    manifest.update(workflows=[], workflow_count=0, latest_by_routing_id={})
    assert wr.audit_manifest(manifest)["status"] == "NOT_EVALUATED"


def test_committed_snapshot_can_be_inspected():
    manifest = wr.load_manifest(ROOT / "docs/registry/workflow-manifest.json")
    report = wr.audit_manifest(manifest)
    assert report["workflow_count"] == len(manifest["workflows"])
    assert all(w["status"] != "READY" for w in report["workflows"])


def test_assessment_does_not_read_files_or_spawn_processes(manifest, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("assessment attempted external access")

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    assert wr.audit_manifest(manifest)["workflow_count"] == 2


def test_network_metadata_does_not_change_license_declaration(manifest):
    manifest["workflows"][0]["data_source"] = {"network_required": True}
    assert checks_for(manifest)["license_policy"] == "PASS"


def test_example_conforms_to_discovery_schema():
    from jsonschema import Draft7Validator

    schema = json.loads((ROOT / "docs/registry/workflow-manifest.schema.json").read_text())
    Draft7Validator(schema).validate(json.loads(EXAMPLE.read_text()))
