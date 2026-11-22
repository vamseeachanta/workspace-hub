"""Brief contract cases derive from issue 3828, Fix/workaround.

Expected results are categorical: explicit scope + owned files + checks + stop
conditions pass; omitting any one fails. No numerical engineering basis applies.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/agents/codex_brief.py"
SPEC = importlib.util.spec_from_file_location("codex_brief", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


@pytest.fixture
def brief():
    return {
        "objective": "Correct the parser's empty-input result.",
        "scope": ["Return an empty list for an empty document."],
        "owned_files": ["src/parser.py", "tests/test_parser.py"],
        "checks": ["python -m pytest tests/test_parser.py -q"],
        "stop_conditions": ["A required fix touches a file outside owned_files."],
    }


def test_valid_brief(brief):
    assert mod.validate_brief(brief) == brief


@pytest.mark.parametrize("field", ["objective", "scope", "owned_files", "checks", "stop_conditions"])
def test_missing_field_rejected(brief, field):
    del brief[field]
    with pytest.raises(ValueError):
        mod.validate_brief(brief)


@pytest.mark.parametrize("field", ["scope", "owned_files", "checks", "stop_conditions"])
@pytest.mark.parametrize("value", [[], "text", [""], ["   "], [None]])
def test_nonempty_string_lists_required(brief, field, value):
    brief[field] = value
    with pytest.raises(ValueError):
        mod.validate_brief(brief)


@pytest.mark.parametrize("value", [None, "", "   ", [], "line\nbreak"])
def test_invalid_objective(brief, value):
    brief["objective"] = value
    with pytest.raises(ValueError):
        mod.validate_brief(brief)


@pytest.mark.parametrize("path", [
    ".", "..", "../other.py", "src/../other.py", "/absolute.py",
    "C:/other.py", "src\\other.py", "src/*.py", "src/", "src//other.py",
    "./src/other.py", ".git/config", "src/.git/config", "~/other.py",
    "src/[abc].py", "src/a?.py", "src/other.py\nmore", "src/other.py\x00",
    ".GIT/config", "src/.Git/config", "src./other.py", "src /other.py",
    "src/other.py.", "src/other.py ", "src/<other>.py", 'src/"other".py',
    "src/other|file.py",
])
def test_unbounded_or_nonportable_paths_rejected(brief, path):
    brief["owned_files"] = [path]
    with pytest.raises(ValueError):
        mod.validate_brief(brief)


@pytest.mark.parametrize("value", [None, [], "brief", 7])
def test_object_required(value):
    with pytest.raises(ValueError):
        mod.validate_brief(value)


def test_unknown_fields_do_not_silently_disappear(brief):
    brief["allow_delete"] = True
    with pytest.raises(ValueError):
        mod.validate_brief(brief)


def test_duplicate_owned_file_rejected(brief):
    brief["owned_files"] *= 2
    with pytest.raises(ValueError):
        mod.validate_brief(brief)


def test_render_preserves_input_and_carries_constraints(brief):
    before = copy.deepcopy(brief)
    output = mod.render_brief(brief)
    assert brief == before
    for heading in ["Objective", "Scope", "Owned files", "Verification", "Stop conditions"]:
        assert f"## {heading}" in output
    for phrase in ["Do not delete data", "Do not rewrite history", "Do not publish",
                   "Do not modify runtime permissions", "not a filesystem sandbox"]:
        assert phrase in output
    for path in brief["owned_files"]:
        assert path in output


def run_cli(payload, tmp_path):
    source = tmp_path / "brief.json"
    source.write_text(payload, encoding="utf-8")
    before = source.read_bytes()
    result = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                            text=True, capture_output=True, check=False)
    assert source.read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["brief.json"]
    return result


def test_cli_renders_without_executing_checks(brief, tmp_path):
    brief["checks"] = ["a-command-that-does-not-exist"]
    result = run_cli(json.dumps(brief), tmp_path)
    assert result.returncode == 0
    assert "a-command-that-does-not-exist" in result.stdout
    assert result.stderr == ""


@pytest.mark.parametrize("payload", ["{", '{"objective": "sensitive-value"}',
                                     '{"objective":"a","objective":"b"}'])
def test_cli_invalid_input_has_no_partial_brief_or_payload_echo(payload, tmp_path):
    result = run_cli(payload, tmp_path)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "sensitive-value" not in result.stderr
    assert "Traceback" not in result.stderr


def test_worked_example_matches_documented_answer():
    example = ROOT / "docs/examples/codex-bounded-brief.json"
    output = mod.render_brief(json.loads(example.read_text(encoding="utf-8")))
    assert "Return an empty list for an empty document." in output
    assert "src/parser.py" in output
    assert "python -m pytest tests/test_parser.py -q" in output


def test_missing_input_file_has_fixed_diagnostic(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path / "absent.json")],
                            text=True, capture_output=True, check=False)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == "Invalid brief: unreadable JSON or incomplete bounded-brief contract.\n"


def test_unicode_input_and_invalid_encoding(brief, tmp_path):
    brief["objective"] = "Correct the parser’s empty-input result."
    assert run_cli(json.dumps(brief, ensure_ascii=False), tmp_path).returncode == 0
    source = tmp_path / "brief.json"
    source.write_bytes(b"\xff")
    result = subprocess.run([sys.executable, str(SCRIPT), str(source)],
                            text=True, capture_output=True, check=False)
    assert result.returncode != 0
    assert "Traceback" not in result.stderr


def test_runbook_links_and_expected_rendering():
    from html import unescape
    from html.parser import HTMLParser

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.targets = []

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                self.targets.extend(value for key, value in attrs if key == "href")

    doc = ROOT / "docs/runbooks/codex-bounded-briefs.html"
    text = doc.read_text(encoding="utf-8")
    links = Links()
    links.feed(text)
    for target in links.targets:
        if not target.startswith("https:"):
            assert (doc.parent / target).is_file()
    example = ROOT / "docs/examples/codex-bounded-brief.json"
    output = mod.render_brief(json.loads(example.read_text(encoding="utf-8")))
    expected = unescape(text.split("<pre><code>## Scope\n", 1)[1].split("</code></pre>", 1)[0])
    assert "## Scope\n" + expected in output
