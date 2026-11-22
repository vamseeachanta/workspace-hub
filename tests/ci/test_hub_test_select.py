"""Selection expectations are hand-computed set unions for synthetic maps.

Rule requirements: issue #4228 (2026). Git's --name-status -z format is
documented at https://git-scm.com/docs/git-diff (accessed 2026-10-22).
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def selector(tmp_path):
    spec = importlib.util.spec_from_file_location("hub_select", ROOT / "scripts/ci/hub_test_select.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = {
        "tests/data": ["tests/data/test_one.py"],
        "scripts/data/tests": ["scripts/data/tests/test_two.py"],
        "tests/skills": ["tests/skills/test_three.py"],
        "tests/contract": ["tests/contract/test_four.py"],
        "tests/ci": ["tests/ci/test_five.py"],
        "tests/root": ["tests/test_six.py"],
        "coordination/tests": ["coordination/tests/test_seven.py"],
    }
    target = tmp_path / "inventory.json"
    target.write_text(json.dumps({"families": paths}))
    rules = tmp_path / "rules.json"
    rules.write_bytes((ROOT / "config/ci/hub-test-rules.json").read_bytes())
    return module, module.load_families(target), module.load_rules(rules)


@pytest.mark.parametrize(("path", "expected"), [
    ("scripts/data/read.py", {"tests/data", "scripts/data/tests"}),
    (".claude/skills/example/SKILL.md", {"tests/skills"}),
    ("config/example.json", {"tests/ci", "tests/contract"}),
    (".github/workflows/check.yml", {"tests/ci", "tests/contract"}),
    ("docs/guide.md", set()),
    ("README.md", set()),
    ("tests/data/test_added.py", {"tests/data"}),
    ("coordination/check.py", {"coordination/tests"}),
    ("tests/test_root.py", {"tests/root"}),
    ("src/unknown.py", {"tests/data", "scripts/data/tests", "tests/skills",
                        "tests/ci", "tests/contract", "tests/root", "coordination/tests"}),
])
def test_ten_hand_calculated_diffs(selector, path, expected):
    """Each row lists the literal family names expected from one changed path."""
    module, families, rules = selector
    assert set(module.select([("M", path)], families, rules)["families"]) == expected


@pytest.mark.parametrize("path", ["scripts/new/tool.py", "tests/new/test_new.py", "docs/tool.py"])
def test_unmapped_code_never_silently_selects_none(selector, path):
    module, families, rules = selector
    assert set(module.select([("A", path)], families, rules)["families"]) == set(families)


def test_every_family_is_directly_reachable(selector):
    module, families, rules = selector
    # Independent witness: change a test file in each family; no fallback allowed.
    for family, files in families.items():
        result = module.select([("M", files[0])], families, rules)
        assert family in result["families"]
        assert result["paths"][0]["rule"] != "unmapped-code"


def test_rename_and_deletion_format(selector):
    module, _, _ = selector
    raw = b"R100\0docs/old name.md\0scripts/data/new name.py\0D\0tests/skills/test_old.py\0"
    assert module.parse_diff(raw) == [
        ("R100", "docs/old name.md"), ("R100", "scripts/data/new name.py"),
        ("D", "tests/skills/test_old.py"),
    ]


@pytest.mark.parametrize("raw", [b"M\0", b"R100\0old\0", b"nonsense\0p\0"])
def test_malformed_diff_fails_closed(selector, raw):
    with pytest.raises(ValueError):
        selector[0].parse_diff(raw)


@pytest.mark.parametrize(("changes", "expected"), [
    ([("M", "docs/guide.md")],
     ("M docs/guide.md\n  rule: documentation\n  families: none\n"
     "Selected families: none\nTest files: 0\nPytest: none\n")),
    ([("M", "scripts/data/read.py")],
     ("M scripts/data/read.py\n  rule: script-area\n  families: scripts/data/tests, tests/data\n"
     "Selected families: scripts/data/tests, tests/data\nTest files: 2\n"
     "Pytest: python -m pytest -q -- scripts/data/tests/test_two.py tests/data/test_one.py\n")),
    ([("D", "tests/skills/test_old.py")],
     ("D tests/skills/test_old.py\n  rule: test-area\n  families: tests/skills\n"
     "Selected families: tests/skills\nTest files: 1\n"
     "Pytest: python -m pytest -q -- tests/skills/test_three.py\n")),
    ([("R100", "docs/old.md"), ("R100", "scripts/data/new.py")],
     ("R100 docs/old.md\n  rule: documentation\n  families: none\n"
     "R100 scripts/data/new.py\n  rule: script-area\n  families: scripts/data/tests, tests/data\n"
     "Selected families: scripts/data/tests, tests/data\nTest files: 2\n"
     "Pytest: python -m pytest -q -- scripts/data/tests/test_two.py tests/data/test_one.py\n")),
])
def test_four_golden_explanations(selector, changes, expected):
    """Golden text lists literal fixture paths; union counts are 0, 2, 1, 2."""
    module, families, rules = selector
    assert module.explain(module.select(changes, families, rules)) == expected


def test_shell_metacharacters_are_quoted(selector):
    module, _, rules = selector
    families = {"tests/root": ["tests/test_$(marker).py"]}
    text = module.explain(module.select([("M", "tests/test_root.py")], families, rules))
    assert "'tests/test_$(marker).py'" in text


def test_invalid_inventory_path_is_rejected(selector, tmp_path):
    module = selector[0]
    target = tmp_path / "bad.json"
    target.write_text(json.dumps({"families": {"tests/root": ["../test_escape.py"]}}))
    with pytest.raises(ValueError):
        module.load_families(target)


@pytest.mark.parametrize("path", ["tests/data/fixtures/input.md", "scripts/data/tests/fixtures/input.txt"])
def test_document_shaped_test_fixtures_still_select_tests(selector, path):
    module, families, rules = selector
    result = module.select([("M", path)], families, rules)
    assert "tests/data" in result["families"]


def test_git_reader_clears_inherited_repository_bindings(selector, tmp_path, monkeypatch):
    module = selector[0]
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "other"))
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return module.subprocess.CompletedProcess(command, 0, b"D\0docs/old.md\0", b"")

    monkeypatch.setattr(module.subprocess, "run", run)
    assert module.git_changes(tmp_path, "base", "head") == [("D", "docs/old.md")]
    command, kwargs = calls[0]
    assert "GIT_DIR" not in kwargs["env"]
    assert kwargs["cwd"] == tmp_path
    assert "--end-of-options" in command
    assert command[-2:] == ["base...head", "--"]
