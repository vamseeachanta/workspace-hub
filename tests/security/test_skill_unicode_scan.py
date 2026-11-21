"""Named Unicode controls, hand-counted locators, and read-only CLI behavior.

Character/property citations are Python unicodedata.lookup, category (Cf =
Other, Format), and bidirectional (the Unicode Bidirectional_Class property).
Expected line numbers count physical LF, CRLF, or CR terminators in each fixture.
Exit statuses are the CLI contract: success = 0, input failure = 1, usage = 2.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unicodedata

import pytest


# Resolve from this file's tests/security directory to the repository root.
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/security/scan_skill_unicode.py"

# Unicode Bidi_Control characters and their Bidirectional_Class values, exposed
# by unicodedata. Each fixture contains exactly one named control on line two.
BIDI_CONTROLS = [
    ("ARABIC LETTER MARK", "AL"),
    ("LEFT-TO-RIGHT MARK", "L"),
    ("RIGHT-TO-LEFT MARK", "R"),
    ("LEFT-TO-RIGHT EMBEDDING", "LRE"),
    ("RIGHT-TO-LEFT EMBEDDING", "RLE"),
    ("POP DIRECTIONAL FORMATTING", "PDF"),
    ("LEFT-TO-RIGHT OVERRIDE", "LRO"),
    ("RIGHT-TO-LEFT OVERRIDE", "RLO"),
    ("LEFT-TO-RIGHT ISOLATE", "LRI"),
    ("RIGHT-TO-LEFT ISOLATE", "RLI"),
    ("FIRST STRONG ISOLATE", "FSI"),
    ("POP DIRECTIONAL ISOLATE", "PDI"),
]

# Explicit selected format controls, by Unicode character name; no severity
# threshold or inference from non-ASCII text is used.
ZERO_WIDTH_CONTROLS = [
    "ZERO WIDTH SPACE",
    "ZERO WIDTH NON-JOINER",
    "ZERO WIDTH JOINER",
    "WORD JOINER",
    "ZERO WIDTH NO-BREAK SPACE",
]


def run_cli(directory, *arguments):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, arguments)],
        cwd=directory,
        capture_output=True,
        check=False,
    )


def records(output):
    return [json.loads(line) for line in output.splitlines()]


@pytest.mark.parametrize("name,bidi_class", BIDI_CONTROLS)
def test_named_bidi_control_at_hand_counted_line(tmp_path, name, bidi_class):
    control = unicodedata.lookup(name)
    assert unicodedata.category(control) == "Cf"
    assert unicodedata.bidirectional(control) == bidi_class
    source = tmp_path / "SKILL.md"
    source.write_text("heading\nPAYLOAD_SENTINEL" + control + "hidden\n", encoding="utf-8")

    result = run_cli(tmp_path, source.name)

    assert result.returncode == 0
    assert result.stderr == b""
    assert records(result.stdout) == [
        {"path": source.name, "line": 2, "rule": "BIDI_CONTROL:" + name}
    ]
    assert b"PAYLOAD_SENTINEL" not in result.stdout + result.stderr
    assert b"hidden" not in result.stdout + result.stderr
    assert control.encode("utf-8") not in result.stdout + result.stderr


@pytest.mark.parametrize("name", ZERO_WIDTH_CONTROLS)
def test_named_zero_width_format_control(tmp_path, name):
    control = unicodedata.lookup(name)
    assert unicodedata.category(control) == "Cf"
    source = tmp_path / "SKILL.md"
    source.write_text("heading\n\nPAYLOAD_SENTINEL" + control, encoding="utf-8")

    result = run_cli(tmp_path, source.name)

    assert result.returncode == 0
    assert result.stderr == b""
    # Heading LF, blank LF, then the single control on physical line three.
    assert records(result.stdout) == [
        {"path": source.name, "line": 3, "rule": "ZERO_WIDTH_FORMAT:" + name}
    ]
    assert b"PAYLOAD_SENTINEL" not in result.stdout + result.stderr


@pytest.mark.parametrize("text", [
    "",
    "# Skill\nPlain ASCII, punctuation and tabs:\tOK\n",
    "Café — naïve Ελληνικά 日本語 العربية עברית 👩🏽\n",
])
def test_ordinary_text_is_clean(tmp_path, text):
    source = tmp_path / "SKILL.md"
    source.write_text(text, encoding="utf-8")
    result = run_cli(tmp_path, source.name)
    assert result.returncode == 0
    assert result.stdout == result.stderr == b""


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
def test_physical_lines_and_each_control_occurrence(tmp_path, ending):
    rlo = unicodedata.lookup("RIGHT-TO-LEFT OVERRIDE")
    zwsp = unicodedata.lookup("ZERO WIDTH SPACE")
    source = tmp_path / "SKILL.md"
    # Hand count: heading = line one; both RLOs = line two; blank = line
    # three; ZWSP = line four. A Unicode LINE SEPARATOR is not a CR or LF.
    source.write_bytes(
        ("heading" + ending + rlo + "\u2028" + rlo + ending + ending + zwsp).encode("utf-8")
    )
    result = run_cli(tmp_path, source.name)
    assert result.returncode == 0
    assert result.stderr == b""
    assert records(result.stdout) == [
        {"path": source.name, "line": 2, "rule": "BIDI_CONTROL:RIGHT-TO-LEFT OVERRIDE"},
        {"path": source.name, "line": 2, "rule": "BIDI_CONTROL:RIGHT-TO-LEFT OVERRIDE"},
        {"path": source.name, "line": 4, "rule": "ZERO_WIDTH_FORMAT:ZERO WIDTH SPACE"},
    ]


def test_repeated_output_and_source_bytes_are_unchanged(tmp_path):
    source = tmp_path / "SKILL.md"
    original = "heading\r\nPAYLOAD_SENTINEL\u202e\r\n".encode("utf-8")
    source.write_bytes(original)

    first = run_cli(tmp_path, source.name)
    second = run_cli(tmp_path, source.name)

    assert first.returncode == second.returncode == 0
    assert first.stderr == second.stderr == b""
    assert first.stdout == second.stdout == (
        b'{"path": "SKILL.md", "line": 2, "rule": "BIDI_CONTROL:RIGHT-TO-LEFT OVERRIDE"}\n'
    )
    assert source.read_bytes() == original


def test_only_explicit_files_in_argument_order(tmp_path):
    listed = tmp_path / "listed.md"
    other = tmp_path / "other.md"
    unlisted = tmp_path / "unlisted.md"
    for source in (listed, other, unlisted):
        source.write_text("\u200b", encoding="utf-8")

    result = run_cli(tmp_path, other.name, listed.name)

    assert result.returncode == 0
    assert result.stderr == b""
    # Two explicit arguments, one control each; unlisted input is not scanned.
    assert records(result.stdout) == [
        {"path": other.name, "line": 1, "rule": "ZERO_WIDTH_FORMAT:ZERO WIDTH SPACE"},
        {"path": listed.name, "line": 1, "rule": "ZERO_WIDTH_FORMAT:ZERO WIDTH SPACE"},
    ]


@pytest.mark.parametrize("kind", ["missing", "directory", "invalid_utf8"])
def test_bad_input_fails_without_payload_or_traceback(tmp_path, kind):
    source = tmp_path / "bad.md"
    rule = "INPUT_UNREADABLE"
    if kind == "directory":
        source.mkdir()
        (source / "nested.md").write_text("\u202e", encoding="utf-8")
    elif kind == "invalid_utf8":
        source.write_bytes(b"PAYLOAD_SENTINEL\xff")
        rule = "INPUT_NOT_UTF8"

    result = run_cli(tmp_path, source.name)

    assert result.returncode == 1
    assert result.stdout == b""
    assert records(result.stderr) == [{"path": source.name, "line": None, "rule": rule}]
    assert b"PAYLOAD_SENTINEL" not in result.stderr
    assert b"Traceback" not in result.stderr


def test_permission_error_fails_without_exception_text(tmp_path, monkeypatch, capsys):
    # Inject the OS error so this check also works with elevated test privileges.
    spec = importlib.util.spec_from_file_location("skill_unicode_scan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / "denied.md"
    source.write_text("PAYLOAD_SENTINEL", encoding="utf-8")

    def denied(*args, **kwargs):
        raise PermissionError("PAYLOAD_SENTINEL")

    monkeypatch.setattr(Path, "open", denied)
    assert module.main([str(source)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert records(captured.err) == [
        {"path": str(source), "line": None, "rule": "INPUT_UNREADABLE"}
    ]


def test_failure_does_not_hide_other_explicit_file_findings(tmp_path):
    source = tmp_path / "SKILL.md"
    source.write_text("\u200b", encoding="utf-8")
    result = run_cli(tmp_path, "absent.md", source.name)
    assert result.returncode == 1
    assert records(result.stdout) == [
        {"path": source.name, "line": 1, "rule": "ZERO_WIDTH_FORMAT:ZERO WIDTH SPACE"}
    ]
    assert records(result.stderr) == [
        {"path": "absent.md", "line": None, "rule": "INPUT_UNREADABLE"}
    ]


def test_filename_control_characters_are_escaped(tmp_path):
    source = tmp_path / ('odd"\n\x1b' + unicodedata.lookup("RIGHT-TO-LEFT OVERRIDE") + ".md")
    source.write_text("\u200b", encoding="utf-8")
    result = run_cli(tmp_path, source.name)
    assert result.returncode == 0
    assert result.stderr == b""
    assert result.stdout.isascii()
    assert b"\x1b" not in result.stdout
    # One input control yields one JSON record, even with a newline in its path.
    assert records(result.stdout) == [
        {"path": source.name, "line": 1, "rule": "ZERO_WIDTH_FORMAT:ZERO WIDTH SPACE"}
    ]


def test_option_like_filename_requires_explicit_delimiter(tmp_path):
    source = tmp_path / "--skill.md"
    source.write_text("\u200b", encoding="utf-8")
    result = run_cli(tmp_path, "--", source.name)
    assert result.returncode == 0
    assert result.stderr == b""
    assert records(result.stdout) == [
        {"path": source.name, "line": 1, "rule": "ZERO_WIDTH_FORMAT:ZERO WIDTH SPACE"}
    ]


@pytest.mark.parametrize("arguments", [[], ["--PAYLOAD_SENTINEL"]])
def test_no_implicit_scan_or_reflected_usage_arguments(tmp_path, arguments):
    (tmp_path / "SKILL.md").write_text("\u202e", encoding="utf-8")
    result = run_cli(tmp_path, *arguments)
    assert result.returncode == 2
    assert result.stdout == b""
    assert records(result.stderr) == [{"path": None, "line": None, "rule": "INVALID_ARGUMENTS"}]


def test_help_documents_report_contract(tmp_path):
    result = run_cli(tmp_path, "--help")
    assert result.returncode == 0
    assert result.stderr == b""
    assert b"explicit UTF-8 files" in result.stdout
    assert b"report only" in result.stdout
