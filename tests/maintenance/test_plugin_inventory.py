"""Offline contract examples for plugin_inventory.md; expected JSON is hand-written.

Fixture labels and versions are synthetic. The JSON envelope revision is the
supported revision documented in that contract. Counts follow direct enumeration:
a user record plus a project record are distinct; a repeated user record is not.
Unsupported revisions use the next integer and a same-valued float; integer
booleans probe strict type validation. Overflow exponent examples exceed the
finite float range described by Python's sys.float_info.max. These are input
boundary examples, not measured quantities.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/maintenance/plugin_inventory.py"


@pytest.fixture
def parser():
    spec = importlib.util.spec_from_file_location("plugin_inventory", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entry(**changes):
    record = {
        "version": "fixture-a",
        "scope": "user",
        "enabled": True,
        "installPath": "plugins/alpha",
    }
    record.update(changes)
    return record


def installed(records=None):
    return json.dumps({"version": 2, "plugins": records if records is not None else {
        "alpha@sample": [entry()],
    }})


def normalized(**changes):
    record = {
        "plugin_id": "alpha@sample",
        "version": "fixture-a",
        "scope": "user",
        "enabled": True,
        "install_path": "plugins/alpha",
    }
    record.update(changes)
    return record


def test_plugin_scopes_remain_distinct(parser):
    payload = installed({"alpha@sample": [
        entry(), entry(scope="project", enabled=False, installPath="project/plugins/alpha"),
    ]})
    assert parser.parse_inventory(payload, input_format="installed-json") == {
        "status": "complete",
        "plugins": [
            normalized(scope="project", enabled=False, install_path="project/plugins/alpha"),
            normalized(),
        ],
    }


def test_inventory_order_is_deterministic(parser):
    records = {
        "zeta@sample": [entry(), entry(scope="project")],
        "alpha@sample": [entry()],
    }
    reversed_records = {
        name: [dict(reversed(list(row.items()))) for row in reversed(rows)]
        for name, rows in reversed(list(records.items()))
    }
    expected = (
        '{"plugins":[{"enabled":true,"install_path":"plugins/alpha",'
        '"plugin_id":"alpha@sample","scope":"user","version":"fixture-a"},'
        '{"enabled":true,"install_path":"plugins/alpha","plugin_id":"zeta@sample",'
        '"scope":"project","version":"fixture-a"},{"enabled":true,'
        '"install_path":"plugins/alpha","plugin_id":"zeta@sample",'
        '"scope":"user","version":"fixture-a"}],"status":"complete"}\n'
    )
    first = parser.format_inventory(installed(records), input_format="installed-json")
    second = parser.format_inventory(installed(reversed_records), input_format="installed-json")
    assert first == second == expected


@pytest.mark.parametrize("payload,input_format", [
    (installed({}), "installed-json"),
    ('{"plugins":{}}', "installed-json"),
    ("No plugins installed.\n", "captured-list"),
])
def test_explicit_empty_inventory(parser, payload, input_format):
    assert parser.format_inventory(payload, input_format=input_format) == (
        '{"plugins":[],"status":"complete"}\n'
    )


@pytest.mark.parametrize("field,output_field", [
    ("version", "version"), ("enabled", "enabled"), ("installPath", "install_path"),
])
def test_missing_evidence_is_explicit(parser, field, output_field):
    record = entry()
    del record[field]
    assert parser.parse_inventory(installed({"alpha@sample": [record]}),
                                  input_format="installed-json") == {
        "status": "partial", "plugins": [normalized(**{output_field: None})],
    }


def test_null_evidence_is_explicit(parser):
    assert parser.parse_inventory(installed({"alpha@sample": [entry(
        version=None, enabled=None, installPath=None,
    )]}), input_format="installed-json") == {
        "status": "partial",
        "plugins": [normalized(version=None, enabled=None, install_path=None)],
    }


CAPTURE = """Installed plugins:

  ❯ alpha@sample
    Version: fixture-a
    Scope: user
    Status: ✔ enabled
    Path: plugins/alpha
"""


def test_supported_capture_matches_json(parser):
    assert parser.format_inventory(CAPTURE, input_format="captured-list") == (
        parser.format_inventory(installed(), input_format="installed-json")
    )


def test_captured_scopes_and_field_order(parser):
    capture = """Installed plugins:
  ❯ alpha@sample
    Path: project/plugins/alpha
    Status: ✘ disabled
    Scope: project
    Version: fixture-a
  ❯ alpha@sample
    Scope: user
"""
    expected = {
        "status": "partial",
        "plugins": [
            normalized(scope="project", enabled=False, install_path="project/plugins/alpha"),
            normalized(version=None, enabled=None, install_path=None),
        ],
    }
    assert parser.parse_inventory(capture, input_format="captured-list") == expected
    assert parser.format_inventory(capture, input_format="captured-list") == (
        parser.format_inventory(installed({"alpha@sample": [
            entry(version=None, enabled=None, installPath=None),
            entry(scope="project", enabled=False, installPath="project/plugins/alpha"),
        ]}), input_format="installed-json")
    )


def test_values_are_preserved_and_never_resolved(parser):
    record = entry(version="opaque-version", scope="custom-scope",
                   installPath="missing folder/../plugins/α")
    assert parser.parse_inventory(installed({"alpha@sample": [record]}),
                                  input_format="installed-json") == {
        "status": "complete", "plugins": [normalized(
            version="opaque-version", scope="custom-scope",
            install_path="missing folder/../plugins/α",
        )],
    }


@pytest.mark.parametrize("payload,rule", [
    ("", "inventory.json"),
    ("{", "inventory.json"),
    ('{"plugins":{},"plugins":{}}', "inventory.duplicate-key"),
    ('{"plugins":{},"extra":{"a":true,"a":false}}', "inventory.duplicate-key"),
    ('{"plugins":{},"extra":NaN}', "inventory.json"),
    ('{"plugins":{},"extra":Infinity}', "inventory.json"),
    ('{"plugins":{},"extra":-Infinity}', "inventory.json"),
    ('{"plugins":{},"extra":1e999}', "inventory.json"),
    ('{"plugins":{},"extra":-1e999}', "inventory.json"),
    ('{"plugins":{},"version":true}', "inventory.shape"),
    ('{"plugins":{},"version":3}', "inventory.shape"),
    ('{"plugins":{},"version":2.0}', "inventory.shape"),
    ('{}', "inventory.shape"),
    ('[]', "inventory.shape"),
    ('null', "inventory.shape"),
    ('{"plugins":null}', "inventory.shape"),
    ('{"plugins":[]}', "inventory.shape"),
    (installed({"alpha@sample": []}), "inventory.record"),
    (installed({"alpha@sample": {}}), "inventory.record"),
    (installed({"alpha@sample": [None]}), "inventory.record"),
    (installed({"alpha@sample": [entry(scope=None)]}), "inventory.record"),
    (installed({"alpha@sample": [{"version": "fixture-a"}]}), "inventory.record"),
    (installed({"alpha@sample": [entry(enabled="false")]}), "inventory.record"),
    (installed({"alpha@sample": [entry(enabled=1)]}), "inventory.record"),
    (installed({"alpha@sample": [entry(version=False)]}), "inventory.record"),
    (installed({"alpha@sample": [entry(version="")]}), "inventory.record"),
    (installed({"alpha@sample": [entry(installPath=[])]}), "inventory.record"),
    (installed({"alpha@sample": [entry(scope=" user")]}), "inventory.record"),
    (installed({"alpha@sample": [entry(installPath="plugins/alpha\nextra")]}), "inventory.record"),
    (installed({"": [entry()]}), "inventory.record"),
    (installed({"alpha sample": [entry()]}), "inventory.record"),
    (installed({"alpha@sample": [entry(), entry()]}), "inventory.duplicate"),
    (installed({"alpha@sample": [entry(), entry(version="fixture-b")]}), "inventory.duplicate"),
])
def test_invalid_json_is_rejected(parser, payload, rule):
    with pytest.raises(parser.InventoryError) as error:
        parser.parse_inventory(payload, input_format="installed-json")
    assert str(error.value) == rule


@pytest.mark.parametrize("payload,rule", [
    ("", "inventory.text"),
    ("unrecognized output", "inventory.text"),
    ("Installed plugins:", "inventory.incomplete"),
    (CAPTURE + "unrecognized footer", "inventory.text"),
    (CAPTURE.replace("    Scope: user\n", ""), "inventory.record"),
    (CAPTURE.replace("    Scope: user", "    Scope: user\n    Scope: project"), "inventory.text"),
    (CAPTURE.replace("✔ enabled", "unknown"), "inventory.text"),
    (CAPTURE.replace("Version:", "Unexpected:"), "inventory.text"),
    (CAPTURE.replace("fixture-a", ""), "inventory.record"),
    (CAPTURE.replace("  ❯ alpha@sample\n", ""), "inventory.text"),
    (CAPTURE + CAPTURE.split("Installed plugins:\n", maxsplit=1)[1], "inventory.duplicate"),
    ("No plugins installed.\nextra", "inventory.text"),
])
def test_unsupported_or_incomplete_text_is_rejected(parser, payload, rule):
    with pytest.raises(parser.InventoryError) as error:
        parser.format_inventory(payload, input_format="captured-list")
    assert str(error.value) == rule


@pytest.mark.parametrize("input_format", ["installed-json", "captured-list"])
def test_malformed_inventory_reports_only_rule(parser, input_format, capsys):
    marker = "synthetic-private-value"
    payload = (installed({marker: [entry(enabled=marker, installPath=marker)]})
               if input_format == "installed-json" else f"Installed plugins:\n{marker}")
    with pytest.raises(parser.InventoryError) as error:
        parser.format_inventory(payload, input_format=input_format)
    assert str(error.value) in {"inventory.record", "inventory.text"}
    assert marker not in repr(error.value)
    assert vars(error.value) == {}
    assert capsys.readouterr() == ("", "")


def test_input_format_must_be_explicitly_supported(parser):
    with pytest.raises(parser.InventoryError, match=r"^inventory.format$"):
        parser.parse_inventory(CAPTURE, input_format="automatic")


def test_non_text_payload_is_rejected(parser):
    with pytest.raises(parser.InventoryError, match=r"^inventory.input$"):
        parser.parse_inventory(None, input_format="installed-json")


def test_parser_has_no_external_effects(parser, monkeypatch):
    import builtins
    import io
    import os
    import socket
    import subprocess

    def forbidden(*args, **kwargs):
        pytest.fail("External effect attempted")

    for module, names in [
        (builtins, ("open",)), (io, ("open",)),
        (os, ("open", "listdir", "scandir", "stat", "system", "popen")),
        (subprocess, ("Popen", "run")), (socket, ("socket", "create_connection")),
    ]:
        for name in names:
            monkeypatch.setattr(module, name, forbidden)
    assert parser.parse_inventory(installed(), input_format="installed-json") == {
        "status": "complete", "plugins": [normalized()],
    }
    assert parser.format_inventory(CAPTURE, input_format="captured-list").endswith("\n")


def test_captured_order_is_deterministic(parser):
    project = CAPTURE.replace("Scope: user", "Scope: project")
    header = "Installed plugins:\n"
    user_body = CAPTURE.removeprefix(header)
    project_body = project.removeprefix(header)
    forward = header + user_body + project_body
    reverse = header + project_body + user_body
    expected = parser.format_inventory(installed({"alpha@sample": [
        entry(), entry(scope="project"),
    ]}), input_format="installed-json")
    assert parser.format_inventory(forward, input_format="captured-list") == expected
    assert parser.format_inventory(reverse, input_format="captured-list") == expected
