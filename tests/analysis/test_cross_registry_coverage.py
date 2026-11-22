"""Synthetic examples; all count expectations use hand arithmetic stated below."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/analysis/cross_registry_coverage.py"


@pytest.fixture
def reporter():
    spec = importlib.util.spec_from_file_location("cross_registry_coverage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def registry():
    return {
        "assets": [
            {
                "asset_key": "guide",
                "canonical_path": "docs/guide/",
                "human_entry_point": "docs/guide/index.md",
                "agent_entry_point": "docs/guide/agent.md",
            },
            {
                "asset_key": "catalog",
                "canonical_path": "data/catalog.yaml",
                "human_entry_point": None,
                "agent_entry_point": "data/catalog.yaml",
            },
        ]
    }


@pytest.fixture
def snapshot():
    # Hand calculation: alpha has 7+2+1=10 covered, 5 unresolved, total 15.
    # beta has 3 covered, 2 unresolved, total 5. Combined: 13+7=20 reads.
    # Percentages: 10/15*100=66.7, 3/5*100=60.0, 13/20*100=65.0.
    return {
        "scope": "synthetic fixed observation window",
        "completeness": "complete",
        "providers": {
            "alpha": {"reads": [
                {"path": "docs/guide/", "count": 7},
                {"path": "docs/guide/index.md", "count": 2},
                {"path": "docs/guide/agent.md", "count": 1},
                {"path": "docs/guide/child.md", "count": 5},
            ]},
            "beta": {"reads": [
                {"path": "data/catalog.yaml", "count": 3},
                {"path": "unknown.md", "count": 2},
            ]},
        },
    }


def test_weighted_coverage_uses_read_count_denominator(reporter, registry, snapshot):
    report = reporter.build_report(registry, snapshot)
    # Three of four distinct alpha paths match (75%); reads yield 66.7%.
    assert report["providers"]["alpha"]["totals"] == {
        "read_count": 15, "covered_count": 10, "unresolved_count": 5,
        "observed_coverage_percent": 66.7, "scope_coverage_percent": 66.7,
        "state": "complete",
    }
    assert report["providers"]["beta"]["totals"]["covered_count"] == 3
    assert report["totals"] == {
        "read_count": 20, "covered_count": 13, "unresolved_count": 7,
        "observed_coverage_percent": 65.0, "scope_coverage_percent": 65.0,
        "state": "complete",
    }


@pytest.mark.parametrize("providers", [{}, {"alpha": {"reads": []}}])
def test_empty_observations_are_not_full_coverage(reporter, registry, providers):
    report = reporter.build_report(registry, {
        "scope": "synthetic empty window", "completeness": "complete",
        "providers": providers,
    })
    # Empty sums are zero; division by zero supplies no coverage evidence.
    assert report["totals"] == {
        "read_count": 0, "covered_count": 0, "unresolved_count": 0,
        "observed_coverage_percent": None, "scope_coverage_percent": None,
        "state": "empty",
    }
    assert "N/A" in reporter.render_markdown(report)


def test_duplicate_registry_keys_are_rejected(reporter, registry, snapshot):
    registry["assets"].append(copy.deepcopy(registry["assets"][0]))
    with pytest.raises(ValueError, match="duplicate asset_key"):
        reporter.build_report(registry, snapshot)


def test_ambiguous_registry_paths_are_rejected(reporter, registry, snapshot):
    registry["assets"][1]["agent_entry_point"] = "docs/guide/agent.md"
    with pytest.raises(ValueError, match="ambiguous registry path"):
        reporter.build_report(registry, snapshot)


def test_same_asset_multiple_fields_count_once(reporter, registry, snapshot):
    report = reporter.build_report(registry, snapshot)
    row = report["providers"]["beta"]["observations"][0]
    # One counted row of three reads, despite two matching field names.
    assert row == {
        "path": "data/catalog.yaml", "count": 3, "asset_key": "catalog",
        "matched_fields": ["agent_entry_point", "canonical_path"],
    }


def test_coverage_json_markdown_totals_agree(reporter, registry, snapshot, tmp_path):
    registry_path = tmp_path / "registry.yaml"
    reads_path = tmp_path / "reads.json"
    json_path = tmp_path / "report.json"
    markdown_path = tmp_path / "report.md"
    registry_path.write_text(yaml.safe_dump(registry), encoding="utf-8")
    reads_path.write_text(json.dumps(snapshot), encoding="utf-8")
    assert reporter.main([
        "--registry", str(registry_path), "--counted-reads", str(reads_path),
        "--json-output", str(json_path), "--markdown-output", str(markdown_path),
    ]) == 0  # Conventional CLI success exit status.
    result = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    # Literal independently calculated totals from the fixture's arithmetic.
    assert result["totals"]["read_count"] == 20
    assert result["totals"]["covered_count"] == 13
    assert result["totals"]["unresolved_count"] == 7
    assert result["totals"]["observed_coverage_percent"] == 65.0
    assert "| alpha | 15 | 10 | 5 | 66.7% | 66.7% | complete |" in markdown
    assert "| beta | 5 | 3 | 2 | 60.0% | 60.0% | complete |" in markdown
    assert "| **Total** | 20 | 13 | 7 | 65.0% | 65.0% | complete |" in markdown
    assert "docs/guide/child.md" in markdown
    assert "alias, external-candidate and historical-trend classification are deferred" in markdown


def test_partial_snapshot_cannot_claim_global_coverage(reporter, registry, snapshot):
    snapshot["completeness"] = "partial"
    snapshot["providers"]["alpha"]["top_reads"] = snapshot["providers"]["alpha"].pop("reads")
    report = reporter.build_report(registry, snapshot)
    assert report["totals"]["scope_coverage_percent"] is None
    assert report["totals"]["observed_coverage_percent"] == 65.0
    assert report["totals"]["state"] == "partial"
    assert all(p["totals"]["scope_coverage_percent"] is None for p in report["providers"].values())
    markdown = reporter.render_markdown(report)
    assert "Partial snapshot: percentages describe only supplied reads" in markdown
    assert "| **Total** | 20 | 13 | 7 | 65.0% | N/A | partial |" in markdown


def test_sampled_top_reads_cannot_be_declared_complete(reporter, registry, snapshot):
    snapshot["providers"]["alpha"]["top_reads"] = snapshot["providers"]["alpha"].pop("reads")
    with pytest.raises(ValueError, match="top_reads.*partial"):
        reporter.build_report(registry, snapshot)


def test_fully_matched_partial_sample_is_still_partial(reporter, registry, snapshot):
    snapshot["completeness"] = "partial"
    snapshot["providers"] = {"alpha": {"top_reads": [{"path": "docs/guide/", "count": 3}]}}
    totals = reporter.build_report(registry, snapshot)["totals"]
    # Three of three supplied reads match: 3/3*100=100.0, but scope is incomplete.
    assert totals["observed_coverage_percent"] == 100.0
    assert totals["scope_coverage_percent"] is None
    assert totals["state"] == "partial"


def test_one_decimal_rounding_uses_half_up(reporter, registry, snapshot):
    snapshot["providers"] = {"alpha": {"reads": [
        {"path": "docs/guide/", "count": 1}, {"path": "unknown.md", "count": 15},
    ]}}
    # Hand calculation: 1/(1+15)*100=6.25, rounded half-up to 6.3 percent.
    report = reporter.build_report(registry, snapshot)
    assert report["totals"]["observed_coverage_percent"] == 6.3
    assert "| **Total** | 16 | 1 | 15 | 6.3% | 6.3% | complete |" in reporter.render_markdown(report)


def test_large_integer_counts_do_not_overflow(reporter, registry, snapshot):
    # Scale both terms by 10**400: 1/(1+3)*100 remains exactly 25.0 percent.
    unit = 10 ** 400
    snapshot["providers"] = {"alpha": {"reads": [
        {"path": "docs/guide/", "count": unit}, {"path": "unknown.md", "count": 3 * unit},
    ]}}
    assert reporter.build_report(registry, snapshot)["totals"]["observed_coverage_percent"] == 25.0


def test_coverage_is_deterministic(reporter, registry, snapshot):
    first = reporter.build_report(registry, snapshot)
    registry["assets"].reverse()
    snapshot["providers"] = dict(reversed(list(snapshot["providers"].items())))
    for provider in snapshot["providers"].values():
        provider["reads"].reverse()
    second = reporter.build_report(registry, snapshot)
    assert json.dumps(first) == json.dumps(second)
    assert reporter.render_markdown(first) == reporter.render_markdown(second)


def test_paths_are_matched_literally(reporter, registry, snapshot, tmp_path):
    # All five spellings differ from canonical_path: no prefix/alias resolution.
    paths = ["./docs/guide/", "docs/guide", "DOCS/guide/", "docs/guide/child.md",
             str(tmp_path / "docs/guide/")]
    snapshot["providers"] = {"alpha": {"reads": [{"path": p, "count": 1} for p in paths]}}
    totals = reporter.build_report(registry, snapshot)["totals"]
    assert totals["read_count"] == 5  # Five singleton rows.
    assert totals["covered_count"] == 0
    assert totals["unresolved_count"] == 5
    assert totals["observed_coverage_percent"] == 0.0


def test_duplicate_read_paths_are_rejected(reporter, registry, snapshot):
    snapshot["providers"]["alpha"]["reads"].append({"path": "docs/guide/", "count": 1})
    with pytest.raises(ValueError, match="duplicate read path"):
        reporter.build_report(registry, snapshot)


@pytest.mark.parametrize("count", [True, False, -1, 0, 1.5, "2", None])
def test_malformed_counts_are_rejected(reporter, registry, snapshot, count):
    snapshot["providers"]["alpha"]["reads"][0]["count"] = count
    with pytest.raises(ValueError, match="positive integer"):
        reporter.build_report(registry, snapshot)


@pytest.mark.parametrize("field", ["scope", "completeness"])
def test_snapshot_markers_are_required(reporter, registry, snapshot, field):
    del snapshot[field]
    with pytest.raises(ValueError):
        reporter.build_report(registry, snapshot)


@pytest.mark.parametrize("bad_snapshot", [
    None, {}, {"scope": "x", "completeness": "unknown", "providers": {}},
    {"scope": "x", "completeness": "complete", "providers": []},
    {"scope": "x", "completeness": "complete", "providers": {"": {"reads": []}}},
    {"scope": "x", "completeness": "complete", "providers": {}, "top_reads": []},
])
def test_malformed_snapshot_envelopes_are_rejected(reporter, registry, bad_snapshot):
    with pytest.raises(ValueError):
        reporter.build_report(registry, bad_snapshot)


@pytest.mark.parametrize("scope", ["", " ", None, [], True])
def test_invalid_scope_is_rejected(reporter, registry, snapshot, scope):
    snapshot["scope"] = scope
    with pytest.raises(ValueError):
        reporter.build_report(registry, snapshot)


@pytest.mark.parametrize("row", [{}, {"path": "x"}, {"path": "", "count": 1},
                                  {"path": " x", "count": 1}, {"path": [], "count": 1},
                                  {"path": "x", "count": 1, "extra": True}, None])
def test_malformed_read_rows_are_rejected(reporter, registry, snapshot, row):
    snapshot["providers"]["alpha"]["reads"] = [row]
    with pytest.raises(ValueError):
        reporter.build_report(registry, snapshot)


@pytest.mark.parametrize("asset", [{}, {"asset_key": "bad"},
                                    {"asset_key": "bad", "canonical_path": []},
                                    {"asset_key": "bad", "canonical_path": ""},
                                    {"asset_key": "bad", "canonical_path": "ok", "agent_entry_point": []},
                                    None])
def test_malformed_assets_are_rejected(reporter, snapshot, asset):
    with pytest.raises(ValueError):
        reporter.build_report({"assets": [asset]}, snapshot)


@pytest.mark.parametrize("provider", [{}, {"reads": {}}, {"reads": [], "top_reads": []},
                                     {"reads": [], "extra": True}, None])
def test_malformed_provider_snapshots_are_rejected(reporter, registry, snapshot, provider):
    snapshot["providers"]["alpha"] = provider
    with pytest.raises(ValueError):
        reporter.build_report(registry, snapshot)


def test_empty_registry_leaves_reads_unresolved(reporter, snapshot):
    # Fixture contains 20 reads; with no registry, all 20 are unresolved.
    totals = reporter.build_report({"assets": []}, snapshot)["totals"]
    assert totals["covered_count"] == 0
    assert totals["unresolved_count"] == 20
    assert totals["observed_coverage_percent"] == 0.0


@pytest.mark.parametrize("suffix, text", [
    ("yaml", "assets: []\nassets: []\n"),
    ("yaml", "assets:\n  - asset_key: a\n    asset_key: b\n    canonical_path: x\n"),
    ("json", '{"assets": [], "assets": []}'),
])
def test_duplicate_serialized_registry_keys_are_rejected(reporter, tmp_path, suffix, text):
    path = tmp_path / ("registry." + suffix)
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        reporter.load_registry(path)


def test_duplicate_json_keys_are_rejected(reporter, tmp_path):
    path = tmp_path / "reads.json"
    path.write_text('{"providers": {}, "providers": {}}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        reporter.load_counted_reads(path)


def test_markdown_escapes_table_cells(reporter, registry, snapshot):
    snapshot["providers"] = {"a|b": {"reads": [{"path": "odd|path.md", "count": 1}]}}
    markdown = reporter.render_markdown(reporter.build_report(registry, snapshot))
    assert "a\\|b" in markdown
    assert "odd\\|path.md" in markdown


def test_cli_rejects_input_output_collisions(reporter, registry, snapshot, tmp_path):
    registry_path = tmp_path / "registry.json"
    reads_path = tmp_path / "reads.json"
    registry_text = json.dumps(registry)
    registry_path.write_text(registry_text, encoding="utf-8")
    reads_path.write_text(json.dumps(snapshot), encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        reporter.main([
            "--registry", str(registry_path), "--counted-reads", str(reads_path),
            "--json-output", str(registry_path), "--markdown-output", str(tmp_path / "report.md"),
        ])
    assert error.value.code == 2  # argparse's invalid-input exit status.
    assert registry_path.read_text(encoding="utf-8") == registry_text


def test_cli_entrypoint_rejects_invalid_input_without_writing_reports(registry, snapshot, tmp_path):
    registry_path = tmp_path / "registry.json"
    reads_path = tmp_path / "reads.json"
    json_path = tmp_path / "report.json"
    markdown_path = tmp_path / "report.md"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    del snapshot["scope"]
    reads_path.write_text(json.dumps(snapshot), encoding="utf-8")
    result = subprocess.run([
        sys.executable, str(SCRIPT), "--registry", str(registry_path),
        "--counted-reads", str(reads_path), "--json-output", str(json_path),
        "--markdown-output", str(markdown_path),
    ], capture_output=True, text=True, check=False)
    assert result.returncode == 2  # argparse's invalid-input exit status.
    assert "no coverage claim made" in result.stderr
    assert not json_path.exists()
    assert not markdown_path.exists()


@pytest.mark.parametrize("existing_json", [False, True])
def test_cli_preserves_outputs_when_markdown_destination_is_directory(
    reporter, registry, snapshot, tmp_path, existing_json,
):
    registry_path = tmp_path / "registry.json"
    reads_path = tmp_path / "reads.json"
    json_path = tmp_path / "report.json"
    markdown_path = tmp_path / "report.md"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    reads_path.write_text(json.dumps(snapshot), encoding="utf-8")
    previous_json = b"previous JSON report\r\n"
    if existing_json:
        json_path.write_bytes(previous_json)
    markdown_path.mkdir()
    previous_markdown = markdown_path / "previous.md"
    previous_markdown.write_bytes(b"previous Markdown report\r\n")

    with pytest.raises(SystemExit) as error:
        reporter.main([
            "--registry", str(registry_path), "--counted-reads", str(reads_path),
            "--json-output", str(json_path), "--markdown-output", str(markdown_path),
        ])

    assert error.value.code == 2
    if existing_json:
        assert json_path.read_bytes() == previous_json
    else:
        assert not json_path.exists()
    assert markdown_path.is_dir()
    assert list(markdown_path.iterdir()) == [previous_markdown]
    assert previous_markdown.read_bytes() == b"previous Markdown report\r\n"
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted([
        "registry.json", "reads.json", "report.md", *(["report.json"] if existing_json else []),
    ])


@pytest.mark.parametrize("existing_json, existing_markdown", [
    (False, False), (False, True), (True, False), (True, True),
])
@pytest.mark.parametrize("failure", ["stage", "replace", None])
def test_cli_report_pair_publication(
    reporter, registry, snapshot, tmp_path, monkeypatch,
    existing_json, existing_markdown, failure,
):
    registry_path = tmp_path / "registry.json"
    reads_path = tmp_path / "reads.json"
    json_path = tmp_path / "report.json"
    markdown_path = tmp_path / "report.md"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    reads_path.write_text(json.dumps(snapshot), encoding="utf-8")
    previous = {json_path: b"previous JSON\r\n", markdown_path: b"previous Markdown\r\n"}
    for path, exists in [(json_path, existing_json), (markdown_path, existing_markdown)]:
        if exists:
            path.write_bytes(previous[path])
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    report = reporter.build_report(registry, snapshot)
    markdown = reporter.render_markdown(report)
    write_text = Path.write_text
    replace = Path.replace

    def fail_markdown_write(path, text, *args, **kwargs):
        if text == markdown:
            raise OSError("synthetic staging failure")
        return write_text(path, text, *args, **kwargs)

    def fail_markdown_replace(path, target):
        if target == markdown_path:
            raise OSError("synthetic publication failure")
        return replace(path, target)

    if failure == "stage":
        monkeypatch.setattr(Path, "write_text", fail_markdown_write)
    elif failure == "replace":
        monkeypatch.setattr(Path, "replace", fail_markdown_replace)
    argv = [
        "--registry", str(registry_path), "--counted-reads", str(reads_path),
        "--json-output", str(json_path), "--markdown-output", str(markdown_path),
    ]
    if failure:
        with pytest.raises(SystemExit) as error:
            reporter.main(argv)
        assert error.value.code == 2
        assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before
    else:
        assert reporter.main(argv) == 0
        assert json.loads(json_path.read_text(encoding="utf-8")) == report
        assert markdown_path.read_text(encoding="utf-8") == markdown
        assert sorted(path.name for path in tmp_path.iterdir()) == [
            "reads.json", "registry.json", "report.json", "report.md",
        ]
