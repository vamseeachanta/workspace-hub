"""Synthetic YAML contracts for the inventory input boundary.

Expected records are hand-enumerated from the literals below, not parsed from
malformed YAML. Duplicate and merge-collision expectations follow the existing
scripts/lib/strict_yaml.py contract (YAML 1.1 unique mapping keys and scalar
resolution). Numeric scalar probes are zero, one and one as a float; none is a
boolean. Subprocess status zero means success; nonzero means failure, per the
Python subprocess contract. The repository root is two parents above this file's
directory. No real configuration or generated report is used or changed.
"""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/repositories/work_surface_inventory.py"
RECORD = "{repo: sample, profile: code, sensitivity: public, mcp_required: false}"
DECLARATION = f"repos: [{RECORD}]\n"
CONFIGURATION = "machines: {target: {repos: [sample]}}\n"

DECLARATION_DUPLICATES = (
    ("top-level", f"repos: []\n{DECLARATION}"),
    ("top-level-equal", DECLARATION + DECLARATION),
    ("profile", "repos: [{repo: sample, profile: knowledge, profile: code, "
     "sensitivity: public, mcp_required: false}]\n"),
    ("profile-equal", "repos: [{repo: sample, profile: code, profile: code, "
     "sensitivity: public, mcp_required: false}]\n"),
    ("boolean", "repos: [{repo: sample, profile: code, sensitivity: public, "
     "mcp_required: true, mcp_required: false}]\n"),
    ("boolean-equal", "repos: [{repo: sample, profile: code, sensitivity: public, "
     "mcp_required: false, mcp_required: false}]\n"),
    ("merge-collision", "repos: [{<<: {profile: code}, repo: sample, profile: code, "
     "sensitivity: public, mcp_required: false}]\n"),
)
CONFIGURATION_DUPLICATES = (
    ("top-level", "machines: {}\n" + CONFIGURATION),
    ("top-level-equal", CONFIGURATION + CONFIGURATION),
    ("record", "machines: {target: {repos: []}, target: {repos: [sample]}}\n"),
    ("record-equal", "machines: {target: {repos: []}, target: {repos: []}}\n"),
    ("repos", "machines: {target: {repos: [], repos: [sample]}}\n"),
    ("repos-equal", "machines: {target: {repos: [sample], repos: [sample]}}\n"),
    ("merge-collision", "machines: {target: {<<: {repos: [sample]}, repos: [sample]}}\n"),
)


@pytest.fixture
def inventory_module():
    spec = importlib.util.spec_from_file_location("inventory_yaml_boundary", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path, text):
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("text", [text for _, text in DECLARATION_DUPLICATES],
                         ids=[name for name, _ in DECLARATION_DUPLICATES])
def test_declaration_yaml_rejects_duplicate_keys(inventory_module, tmp_path, text):
    path = _write(tmp_path / "declarations.yaml", text)
    with pytest.raises(ValueError, match="^invalid YAML input$"):
        inventory_module.load_declared_repositories(path)


@pytest.mark.parametrize("text", [text for _, text in CONFIGURATION_DUPLICATES],
                         ids=[name for name, _ in CONFIGURATION_DUPLICATES])
def test_configuration_yaml_rejects_duplicate_keys(inventory_module, tmp_path, text):
    path = _write(tmp_path / "configuration.yaml", text)
    with pytest.raises(ValueError, match="^invalid YAML input$"):
        inventory_module.load_machine_repositories(path, "target")


def test_inventory_yaml_retains_valid_records_and_boolean_contract(inventory_module, tmp_path):
    declaration = tmp_path / "declarations.yaml"
    for text in ("", "{}", "repos: []"):
        assert inventory_module.load_declared_repositories(_write(declaration, text)) == {}
    expected = {"sample": {"repo": "sample", "profile": "code",
                           "sensitivity": "public", "mcp_required": False}}
    assert inventory_module.load_declared_repositories(_write(declaration, DECLARATION)) == expected

    # Preserve the existing PyYAML/YAML 1.1 boolean spellings, without coercion.
    for scalar, value in (("false", False), ("False", False), ("FALSE", False),
                          ("no", False), ("No", False), ("NO", False),
                          ("off", False), ("Off", False), ("OFF", False),
                          ("true", True), ("True", True), ("TRUE", True),
                          ("yes", True), ("Yes", True), ("YES", True),
                          ("on", True), ("On", True), ("ON", True)):
        text = DECLARATION.replace("false", scalar)
        record = inventory_module.load_declared_repositories(_write(declaration, text))
        assert record == {"sample": {"repo": "sample", "profile": "code",
                                     "sensitivity": "public", "mcp_required": value}}
        assert record["sample"]["mcp_required"] is value
    for scalar in ("0", "1", "1.0", "'false'", "'true'", "'0'", "null"):
        with pytest.raises(ValueError):
            inventory_module.load_declared_repositories(
                _write(declaration, DECLARATION.replace("false", scalar)))

    configuration = tmp_path / "configuration.yaml"
    for text in ("", "{}", "machines: {}", "machines: {target: {repos: []}}"):
        assert inventory_module.load_machine_repositories(_write(configuration, text), "target") == set()
    assert inventory_module.load_machine_repositories(
        _write(configuration, CONFIGURATION), "target") == {"sample"}


@pytest.mark.parametrize("text", [
    "[]", "false", "0", "sample", "repos: null", "repos: {}", "repos: sample",
    "repos: [null]", "repos: [[]]", "repos: [sample]",
    DECLARATION.replace("profile: code", "profile: []"),
    DECLARATION.replace("profile: code", "profile: other"),
    DECLARATION.replace("sensitivity: public", "sensitivity: {}"),
    DECLARATION.replace("sensitivity: public", "sensitivity: other"),
])
def test_declaration_yaml_rejects_invalid_shapes(inventory_module, tmp_path, text):
    with pytest.raises(ValueError):
        inventory_module.load_declared_repositories(_write(tmp_path / "declarations.yaml", text))


@pytest.mark.parametrize("text", [
    "[]", "false", "0", "sample", "machines: null", "machines: []", "machines: sample",
    "machines: {target: null}", "machines: {target: []}", "machines: {target: sample}",
    "machines: {target: {repos: null}}", "machines: {target: {repos: {}}}",
    "machines: {target: {repos: sample}}",
])
def test_configuration_yaml_rejects_invalid_shapes(inventory_module, tmp_path, text):
    with pytest.raises(ValueError):
        inventory_module.load_machine_repositories(_write(tmp_path / "configuration.yaml", text), "target")


def _cli(tmp_path, declaration, configuration, json_output, markdown_output, *extra):
    surface = tmp_path / "surface"
    surface.mkdir(exist_ok=True)
    # Exercise the standalone import bootstrap, without pytest's import path.
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run([
        sys.executable, str(SCRIPT), "--mission-map", str(declaration),
        "--workstations", str(configuration), "--workspace-root", str(surface),
        "--machine", "target", "--json-output", str(json_output),
        "--markdown-output", str(markdown_output), *extra,
    ], cwd=tmp_path, env=env, capture_output=True, text=True, check=False)


@pytest.mark.parametrize("source,text", [
    *(('declaration', text) for _, text in DECLARATION_DUPLICATES),
    *(('configuration', text) for _, text in CONFIGURATION_DUPLICATES),
    ("declaration", "PRIVATE_SENTINEL: ["),
    ("configuration", "PRIVATE_SENTINEL: ["),
    ("declaration", DECLARATION.replace("profile: code", "profile: PRIVATE_SENTINEL")),
    ("configuration", "machines: {target: PRIVATE_SENTINEL}"),
])
@pytest.mark.parametrize("existing", [False, True], ids=["absent", "existing"])
def test_cli_invalid_yaml_preserves_outputs(tmp_path, source, text, existing):
    # No duplicate diagnostic may reveal even an equal, otherwise valid value.
    text = text.replace("sample", "PRIVATE_SENTINEL")
    declaration = _write(tmp_path / "declarations.yaml", text if source == "declaration" else DECLARATION)
    configuration = _write(tmp_path / "configuration.yaml", text if source == "configuration" else CONFIGURATION)
    json_output, markdown_output = tmp_path / "inventory.json", tmp_path / "inventory.md"
    outputs = {json_output: b"existing JSON bytes\n", markdown_output: b"existing Markdown bytes\n"}
    if existing:
        for path, content in outputs.items():
            path.write_bytes(content)
    result = _cli(tmp_path, declaration, configuration, json_output, markdown_output)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == "invalid inventory input\n"
    assert "PRIVATE_SENTINEL" not in result.stderr
    assert str(tmp_path) not in result.stderr
    assert "Traceback" not in result.stderr
    for path, content in outputs.items():
        if existing:
            assert path.read_bytes() == content
        else:
            assert not path.exists()


def test_cli_valid_empty_fixture_preserves_exact_output(tmp_path, inventory_module):
    declaration = _write(tmp_path / "declarations.yaml", "repos: []\n")
    configuration = _write(tmp_path / "configuration.yaml", "machines: {}\n")
    json_output, markdown_output = tmp_path / "inventory.json", tmp_path / "inventory.md"
    # Hand calculation: no declarations, configured names or directories means
    # every count is zero; schema_version remains the existing version one.
    expected = {
        "repositories": [], "schema_version": 1,
        "summary": {"adapter_coverage": {"complete": 0, "incomplete": 0},
                    "contract_complete": 0, "configured": 0, "declared": 0,
                    "missing": 0, "non_git": 0, "observed_declared": 0,
                    "present": 0, "unexpected_count": 0, "unknown": 0},
    }
    expected_markdown = (
        "# Workspace Repository Overview\n\n"
        "> Generated by `scripts/repositories/work_surface_inventory.py`. Do not edit manually.\n\n"
        "This is discovery evidence only. It is not a routing, placement, or membership authority.\n\n"
        "## Summary\n\n"
        "- Declared repositories: 0\n"
        "- Configured for this machine: 0\n"
        "- Present Git repositories: 0\n"
        "- Missing declared repositories: 0\n"
        "- Declared non-Git directories: 0\n"
        "- Declared repositories observed locally: 0\n"
        "- Complete provider contracts: 0\n"
        "- Incomplete provider contracts: 0\n"
        "- Undeclared local repositories: 0 (names suppressed)\n\n"
        "## Declared repositories\n\n"
        "| Repository | Profile | Sensitivity | State | Machine configured | Local | Contract |\n"
        "|---|---|---|---|---:|---:|---|\n"
    )
    expected_json = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    assert inventory_module.render_markdown(expected) == expected_markdown
    json_output.write_text(expected_json, encoding="utf-8")
    markdown_output.write_text(expected_markdown, encoding="utf-8")
    for extra in (("--check",), ()):
        result = _cli(tmp_path, declaration, configuration, json_output, markdown_output, *extra)
        assert result.returncode == 0
        assert result.stderr == ""
        assert json_output.read_bytes() == expected_json.encode("utf-8")
        assert markdown_output.read_bytes() == expected_markdown.encode("utf-8")
