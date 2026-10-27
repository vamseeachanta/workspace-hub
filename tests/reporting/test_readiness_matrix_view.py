"""Synthetic review-view contract; no inventory, credentials or probes are used.

The example has two roles. Sorting their literal keys gives batch then review;
only batch has a summary, so review is unverified. Every expected row below is
written independently from those inputs. Reference coverage is set inclusion,
not a readiness decision. All generated files and metadata sentinels use tmp_path.
CLI exit values follow argparse (usage error) and conventional success/failure.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path

import pytest

from reporting import readiness_matrix_view as view

# Repository test layout: this file is below tests/reporting.
ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/reporting/readiness_matrix_view.py"


@pytest.fixture
def registry():
    return {
        "review": {
            "task_classes": ["review"],
            "auth_expectations": ["interactive approval"],
            "required_clis": [],
            "verification_refs": ["checks/review"],
            "inventory_note": "not projected",
        },
        "batch": {
            "task_classes": ["test", "build"],
            "auth_expectations": ["local token"],
            "required_clis": ["python", "git"],
            "verification_refs": ["checks/test", "checks/build"],
        },
    }


@pytest.fixture
def evidence():
    return {
        "batch": {
            "status": "pass",
            "verification_refs": ["checks/test", "checks/build"],
        }
    }


@pytest.fixture
def expected_rows():
    """Hand projection: sort keys and set fields; never infer ready."""
    return [
        {
            "role": "batch",
            "task_classes": ["build", "test"],
            "auth_expectations": ["local token"],
            "required_clis": ["git", "python"],
            "verification_refs": ["checks/build", "checks/test"],
            "evidence_status": "pass",
            "evidence_refs": ["checks/build", "checks/test"],
        },
        {
            "role": "review",
            "task_classes": ["review"],
            "auth_expectations": ["interactive approval"],
            "required_clis": [],
            "verification_refs": ["checks/review"],
            "evidence_status": "unverified",
            "evidence_refs": [],
        },
    ]


def test_every_registry_role_has_one_row(registry, evidence, expected_rows):
    assert view.build_rows(registry, evidence) == expected_rows


def test_missing_evidence_is_unverified(registry):
    rows = view.build_rows(registry, {})
    assert [row["evidence_status"] for row in rows] == ["unverified", "unverified"]
    assert all(row["evidence_refs"] == [] for row in rows)


def test_partial_reference_coverage_is_unverified(registry, evidence):
    evidence["batch"]["verification_refs"] = ["checks/build"]
    row, _ = view.build_rows(registry, evidence)
    assert row["evidence_status"] == "unverified"
    assert row["evidence_refs"] == ["checks/build"]


@pytest.mark.parametrize("status", ["pass", "warn", "fail", "error", "skip", "unverified"])
def test_status_is_observation_never_readiness(registry, evidence, status):
    evidence["batch"]["status"] = status
    row, _ = view.build_rows(registry, evidence)
    assert row["evidence_status"] == status
    assert "ready" not in row


def test_stable_order_and_no_input_mutation(registry, evidence):
    before = copy.deepcopy((registry, evidence))
    rows = view.build_rows(registry, evidence)
    assert (registry, evidence) == before
    reordered = copy.deepcopy(dict(reversed(list(registry.items()))))
    for record in reordered.values():
        for field, values in list(record.items()):
            if isinstance(values, list):
                record[field] = list(reversed(values)) + values
    assert view.build_rows(reordered, evidence) == rows
    assert (registry, evidence) == before


class _Cells(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.cells = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "td":
            self.current = ""

    def handle_data(self, data):
        if self.current is not None:
            self.current += data

    def handle_endtag(self, tag):
        if tag == "td":
            self.cells.append(self.current)
            self.current = None


def test_html_fields_are_escaped():
    """An attack string in every free-text column remains literal cell text."""
    attack = '<script>"quoted" & \'single\'</script>'
    record = {
        field: [attack]
        for field in ("task_classes", "auth_expectations", "required_clis", "verification_refs")
    }
    registry = {attack: record}
    evidence = {attack: {"status": "pass", "verification_refs": [attack]}}
    markup = view.render_html(registry, evidence)
    assert escape(attack, quote=True) in markup
    parsed = _Cells()
    parsed.feed(markup)
    assert "script" not in parsed.tags
    assert parsed.cells == [attack, attack, attack, attack, attack, "pass", attack]


def test_json_is_deterministic_and_complete(registry, evidence, expected_rows):
    rendered = view.render_json(registry, evidence)
    assert json.loads(rendered) == {"rows": expected_rows}
    assert rendered == view.render_json(dict(reversed(list(registry.items()))), evidence)
    assert rendered.endswith("\n")
    assert "not projected" not in rendered


def test_html_is_deterministic_and_complete(registry, evidence, expected_rows):
    markup = view.render_html(registry, evidence)
    assert markup == view.render_html(dict(reversed(list(registry.items()))), evidence)
    parsed = _Cells()
    parsed.feed(markup)
    # The literal expected rows define the column order independently of COLUMNS.
    assert parsed.cells == [
        ", ".join(value) if isinstance(value, list) else value
        for row in expected_rows
        for value in row.values()
    ]


def test_explicit_empty_registry_has_no_rows():
    assert view.build_rows({}, {}) == []


@pytest.mark.parametrize("field", ["task_classes", "auth_expectations", "required_clis", "verification_refs"])
def test_required_fields_cannot_be_omitted(registry, field):
    del registry["batch"][field]
    with pytest.raises(ValueError):
        view.build_rows(registry, {})


@pytest.mark.parametrize("bad", [None, "git", [""], ["   "], [False], {}])
def test_invalid_field_types_are_rejected(registry, bad):
    registry["batch"]["required_clis"] = bad
    with pytest.raises(ValueError):
        view.build_rows(registry, {})


@pytest.mark.parametrize("field", ["task_classes", "auth_expectations", "verification_refs"])
def test_required_expectations_are_nonempty(registry, field):
    registry["batch"][field] = []
    with pytest.raises(ValueError):
        view.build_rows(registry, {})


@pytest.mark.parametrize("bad", [None, [], {"": {}}, {"batch": None}])
def test_invalid_registry_is_rejected(bad):
    with pytest.raises(ValueError):
        view.build_rows(bad, {})


@pytest.mark.parametrize(
    "bad",
    [None, [], {"other": {"status": "pass", "verification_refs": ["checks/build"]}},
     {"batch": {"status": "ready", "verification_refs": ["checks/build"]}},
     {"batch": {"status": "pass", "verification_refs": []}},
     {"batch": {"status": "pass"}},
     {"batch": {"status": "pass", "verification_refs": ["checks/build"], "validated": True}},
     {"batch": None}, {"batch": {"status": [], "verification_refs": ["checks/build"]}}],
)
def test_invalid_summaries_are_rejected(registry, bad):
    with pytest.raises(ValueError):
        view.build_rows(registry, bad)


def _inputs(tmp_path, registry, evidence):
    registry_path = tmp_path / "synthetic-registry.json"
    evidence_path = tmp_path / "synthetic-evidence.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    return registry_path, evidence_path


def _args(registry_path, evidence_path, output, format_name="json"):
    return ["--registry", str(registry_path), "--evidence", str(evidence_path),
            "--output", str(output), "--format", format_name]


def _snapshot(path):
    data = path.read_bytes()
    stat = path.stat()
    return data, stat.st_mode, stat.st_mtime_ns, stat.st_ino


@pytest.mark.parametrize("format_name", ["json", "html"])
def test_cli_generates_only_explicit_output_and_preserves_caller(
    tmp_path, registry, evidence, expected_rows, monkeypatch, format_name
):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    caller = tmp_path / "caller"
    metadata = caller / ".git"
    metadata.mkdir(parents=True)
    sentinel = metadata / "HEAD"
    sentinel.write_text("caller metadata\n", encoding="utf-8")
    marker = caller / "keep.txt"
    marker.write_text("caller file\n", encoding="utf-8")
    paths = (registry_path, evidence_path, sentinel, marker)
    before = {path: _snapshot(path) for path in paths}
    monkeypatch.chdir(caller)
    for variable in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.setenv(variable, str(metadata))
    output = tmp_path / f"matrix.{format_name}"
    assert view.main(_args(registry_path, evidence_path, output, format_name)) == 0
    assert {path: _snapshot(path) for path in paths} == before
    assert set(tmp_path.iterdir()) == {registry_path, evidence_path, caller, output}
    if format_name == "json":
        assert json.loads(output.read_text(encoding="utf-8")) == {"rows": expected_rows}
    else:
        assert "<table>" in output.read_text(encoding="utf-8")


@pytest.mark.parametrize("target", ["existing", "registry", "evidence", "symlink", "hardlink"])
def test_cli_never_overwrites_caller_files(tmp_path, registry, evidence, target, capsys):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    original = tmp_path / "keep.txt"
    original.write_text("preserve\n", encoding="utf-8")
    output = tmp_path / "matrix.json"
    if target == "existing":
        output.write_text("existing\n", encoding="utf-8")
    elif target == "registry":
        output = registry_path
    elif target == "evidence":
        output = evidence_path
    elif target == "symlink":
        output.symlink_to(original)
    else:
        os.link(original, output)
    paths = (registry_path, evidence_path, original, output)
    before = {path: _snapshot(path) for path in paths}
    assert view.main(_args(registry_path, evidence_path, output)) == 1
    assert {path: _snapshot(path) for path in paths} == before
    captured = capsys.readouterr()
    assert str(tmp_path) not in captured.out + captured.err


@pytest.mark.parametrize("raw", ['{"batch": {}, "batch": {}}', '{"value": NaN}', '[', '[]'])
def test_cli_rejects_ambiguous_or_invalid_input(tmp_path, registry, evidence, raw):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    registry_path.write_text(raw, encoding="utf-8")
    output = tmp_path / "matrix.json"
    assert view.main(_args(registry_path, evidence_path, output)) == 1
    assert not output.exists()


def test_cli_invalid_evidence_leaves_no_output(tmp_path, registry, evidence):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    evidence_path.write_text('{"batch": {"status": "ready"}}', encoding="utf-8")
    output = tmp_path / "matrix.json"
    assert view.main(_args(registry_path, evidence_path, output)) == 1
    assert not output.exists()


def test_cli_dangling_symlink_is_preserved(tmp_path, registry, evidence):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    destination = tmp_path / "absent.json"
    output = tmp_path / "matrix.json"
    output.symlink_to(destination)
    before = output.lstat()
    assert view.main(_args(registry_path, evidence_path, output)) == 1
    assert output.is_symlink()
    assert output.lstat() == before
    assert not destination.exists()


@pytest.mark.parametrize("which", ["registry", "evidence"])
def test_cli_unreadable_input_leaves_no_output(tmp_path, registry, evidence, which):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    if which == "registry":
        registry_path = tmp_path / "absent.json"
    else:
        evidence_path = tmp_path / "absent.json"
    output = tmp_path / "matrix.json"
    assert view.main(_args(registry_path, evidence_path, output)) == 1
    assert not output.exists()


@pytest.mark.parametrize("missing", ["registry", "evidence", "output"])
def test_cli_requires_explicit_records_and_output(tmp_path, registry, evidence, missing, capsys):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    args = _args(registry_path, evidence_path, tmp_path / "matrix.json")
    flag = f"--{missing}"
    selected = iter(args)
    remaining = []
    for argument in selected:
        if argument == flag:
            next(selected)
        else:
            remaining.append(argument)
    with pytest.raises(SystemExit) as error:
        view.main(remaining)
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert str(tmp_path) not in captured.out + captured.err


def test_cli_has_no_live_reads_or_probes(tmp_path, registry, evidence, monkeypatch):
    import socket

    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    allowed = {registry_path, evidence_path}
    read_text = Path.read_text

    def guarded_read(path, *args, **kwargs):
        assert path in allowed
        return read_text(path, *args, **kwargs)

    def forbidden(*args, **kwargs):
        pytest.fail("unexpected probe")

    monkeypatch.setattr(Path, "read_text", guarded_read)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    assert view.main(_args(registry_path, evidence_path, tmp_path / "matrix.json")) == 0


def test_script_entrypoint(tmp_path, registry, evidence, expected_rows):
    registry_path, evidence_path = _inputs(tmp_path, registry, evidence)
    output = tmp_path / "matrix.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *_args(registry_path, evidence_path, output)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert result.stdout == result.stderr == ""
    assert json.loads(output.read_text(encoding="utf-8")) == {"rows": expected_rows}
