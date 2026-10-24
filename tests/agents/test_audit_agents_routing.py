"""Routing expectations are literal comparisons to issue 3958's Contract line.

The complete fixture contains both required tokens on one active line. Removing
one token gives partial coverage; removing both gives no coverage. Expected
line numbers are counted directly from the fixture strings, independently of
the auditor. All repositories and configuration files are synthetic.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/agents/audit_agents_routing.py"
TEMPLATE = SCRIPT.parents[2] / "docs/agents/hub-routing-block.md"
BLOCK = "# Repository instructions\nContract: ../workspace-hub/AGENTS.md\n"


def load_module():
    spec = importlib.util.spec_from_file_location("audit_agents_routing", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("text", "status", "lines"),
    [
        (BLOCK, "yes", [2]),
        ("Contract: ../workspace-hub/AGENTS.md | Source: src/digitalmodel/\n", "yes", [1]),
        ("Contract: ../workspace-hub/AGENTS.md | Source: src/example/ | Mode: local\n",
         "yes", [1]),
        ("Contract: ../workspace-hub/AGENTS.md unrelated\n", "partial", [1]),
        ("Contract: ../workspace-hub/AGENTS.md| Source: src/example/\n", "partial", [1]),
        (("# X\n```html\n<!-- example opener\n```\n"
          "Contract: ../workspace-hub/AGENTS.md\n"), "yes", [5]),
        (("# X\n~~~html\n<!-- example opener\n~~~\n"
          "Contract: ../workspace-hub/AGENTS.md\n"), "yes", [5]),
        ("\ufeffContract: ../workspace-hub/AGENTS.md\n", "yes", [1]),
        ("# Independent instructions\n", "no", []),
        ("Contract: elsewhere/AGENTS.md\n", "partial", [1]),
        ("../workspace-hub/AGENTS.md\n", "partial", [1]),
        ("Contract:\n../workspace-hub/AGENTS.md\n", "partial", [1, 2]),
        ("```text\n" + BLOCK + "```\n", "no", []),
        ("<!--\n" + BLOCK + "-->\n", "no", []),
        ("Do not use Contract: ../workspace-hub/AGENTS.md\n", "partial", [1]),
        ("Contract: ../workspace-hub/AGENTS.md.backup\n", "partial", [1]),
        ("workspace-hub/blob/main/AGENTS.md\n", "partial", [1]),
        ("~~~text\n" + BLOCK + "~~~\n", "no", []),
        ("    Contract: ../workspace-hub/AGENTS.md\n", "no", []),
    ],
)
def test_marker_classification(tmp_path, text, status, lines):
    repo = tmp_path / "sample"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(text, encoding="utf-8")
    row = load_module().audit_repository(repo)[0]
    assert row["routes"] == status
    assert row["lines"] == lines
    assert bool(row["missing"]) == (status != "yes")


def test_missing_files_and_read_only(tmp_path):
    repo = tmp_path / "sample"
    repo.mkdir()
    agents = repo / "AGENTS.md"
    agents.write_text(BLOCK, encoding="utf-8")
    legacy = repo / "CLAUDE.md"
    legacy.write_text("Contract: elsewhere/AGENTS.md\n", encoding="utf-8")
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in repo.iterdir()}
    module = load_module()
    rows = module.audit_repository(repo)
    assert [r["routes"] for r in rows] == ["yes", "partial"]
    assert before == {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in repo.iterdir()}
    empty = tmp_path / "empty"
    empty.mkdir()
    assert all(not r["present"] and r["routes"] == "no"
               for r in module.audit_repository(empty))
    missing_agents, missing_legacy = module.audit_repository(empty)
    assert missing_agents["missing"] == ["Contract: ../workspace-hub/AGENTS.md"]
    assert missing_legacy["missing"] == ["n/a (file absent)"]
    assert list(empty.iterdir()) == []


def test_template_is_the_canonical_fixture():
    assert TEMPLATE.read_text(encoding="utf-8") == BLOCK


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True, check=False)


def test_cli_paths_and_json_relative_to_config(tmp_path):
    repo = tmp_path / "sample"
    repo.mkdir()
    (repo / "AGENTS.md").write_text(BLOCK, encoding="utf-8")
    config = tmp_path / "repos.json"
    config.write_text(json.dumps(["sample"]), encoding="utf-8")
    direct = run_cli(repo)
    configured = run_cli("--repos-json", config)
    assert direct.returncode == configured.returncode == 0
    assert direct.stdout == configured.stdout
    assert "| sample | AGENTS.md: yes | yes | none | 2 |" in direct.stdout
    assert "| sample | CLAUDE.md: no | no | n/a (file absent) | none |" in direct.stdout
    assert str(tmp_path) not in direct.stdout


@pytest.mark.parametrize("value", [{"repos": []}, [1], [], [""]])
def test_invalid_json_schema(tmp_path, value):
    config = tmp_path / "repos.json"
    config.write_text(json.dumps(value), encoding="utf-8")
    result = run_cli("--repos-json", config)
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert str(tmp_path) not in result.stderr


def test_bad_json_and_nonexistent_checkout(tmp_path):
    config = tmp_path / "repos.json"
    config.write_text("{", encoding="utf-8")
    assert run_cli("--repos-json", config).returncode == 2
    assert run_cli(tmp_path / "absent").returncode == 2
    assert run_cli().returncode == 2


def test_unreadable_text_is_a_reported_gap(tmp_path):
    (tmp_path / "AGENTS.md").write_bytes(b"\xff")
    row = load_module().audit_repository(tmp_path)[0]
    assert row["present"]
    assert row["routes"] == "no"
    assert "unreadable UTF-8 file" in row["missing"]


def test_table_escapes_repository_names():
    row = {"repository": "sample|<x>", "file": "AGENTS.md", "present": False,
           "routes": "no", "missing": ["Contract: ../workspace-hub/AGENTS.md"],
           "lines": []}
    table = load_module().render_table([row])
    assert "| sample&#124;&lt;x&gt; | AGENTS.md: no |" in table


def test_duplicate_names_are_not_ambiguous(tmp_path):
    first = tmp_path / "first" / "sample"
    second = tmp_path / "second" / "sample"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    assert run_cli(first, second).returncode == 2
    assert run_cli(first, first).stdout.count("| sample | AGENTS.md:") == 1


def test_documented_fixture_table(tmp_path):
    """Four literal inputs yield eight rows: two filenames per directory.

    The expected table is written out in the documentation; the canonical
    marker is on line 2 of complete, line 1 of partial, and absent elsewhere.
    """
    inputs = {"complete": BLOCK, "unlinked": "# Local instructions\n",
              "partial": "Contract: elsewhere/AGENTS.md\n", "absent": None}
    module = load_module()
    rows = []
    for name, content in inputs.items():
        repo = tmp_path / name
        repo.mkdir()
        if content is not None:
            (repo / "AGENTS.md").write_text(content, encoding="utf-8")
        rows.extend(module.audit_repository(repo))
    documentation = (TEMPLATE.parent / "hub-routing-audit.md").read_text(encoding="utf-8")
    expected = documentation.split("<!-- fixture-table:start -->\n", 1)[1]
    expected = expected.split("\n<!-- fixture-table:end -->", 1)[0]
    assert module.render_table(rows) == expected
