"""Exercise declarations only; never source or run the production script.

Rule citations in scripts/memory/pre-bridge-quality.sh:
* line 22: initial score 100; lines 38-42: missing -30, empty -25.
* lines 59-69: missing files ignored; over limit -20; strictly above the
  integer threshold (limit * 90 / 100) -5, including equality with the cap.
* lines 45-47 and 62: wc counts newline characters and bytes, respectively.
* lines 71-72: headroom is limit minus bytes.

Fixture calculations below are independent, hand-counted ASCII examples.
Shell exit values use the conventional zero for success and one for failure.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest


SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "scripts/memory/pre-bridge-quality.sh"
)
FUNCTIONS = ("check_files_exist", "check_char_limits")
# Only wc may execute a real external program. These names resolve to a sentinel,
# never to bridge, Git, notification, network, scheduler or provider programs.
BLOCKED_COMMANDS = (
    "blocked-probe",
    "bash",
    "sh",
    "git",
    "bridge-hermes-claude.sh",
    "notify-send",
    "curl",
    "wget",
    "crontab",
    "systemctl",
    "hermes",
    "claude",
    "codex",
    "gemini",
)


@dataclass
class State:
    score: int
    criticals: list[str]
    warnings: list[str]
    logs: list[str]


def function_declarations() -> str:
    """Fail closed if either uniquely named declaration changes its shape.

    These functions have unindented opening/closing lines and indented bodies.
    Matching that format excludes all top-level initialization and main code.
    No other declaration, including production logging, is loaded.
    """
    source = SCRIPT.read_text(encoding="utf-8")
    declarations = []
    for name in FUNCTIONS:
        matches = re.findall(
            rf"^{name}\(\) \{{\n(?:[ \t]+[^\n]*\n|\n)*^\}}$",
            source,
            flags=re.MULTILINE,
        )
        (declaration,) = matches
        declarations.append(declaration)
    return "\n\n".join(declarations)


@pytest.fixture
def harness(tmp_path: Path):
    """A disposable Bash script with an isolated environment and private PATH."""
    bash = shutil.which("bash")
    wc = shutil.which("wc")
    assert bash is not None, "required dependency unavailable: bash"
    assert wc is not None, "required dependency unavailable: wc"
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "wc").symlink_to(wc)
    sentinel = tmp_path / "sentinel.sh"
    sentinel.write_text(
        f"#!{bash}\n"
        'printf "%s\\n" "${0##*/}" >> "$SENTINEL"\n'
        "exit 1\n",
        encoding="utf-8",
    )
    sentinel.chmod(0o700)  # User read/write/execute bits; no group or other access.
    for name in BLOCKED_COMMANDS:
        (tools / name).symlink_to(sentinel)
    record = tmp_path / "forbidden-calls.txt"
    script = tmp_path / "harness.sh"
    script.write_text(
        "set -euo pipefail\n"
        # Production initial score: pre-bridge-quality.sh:22.
        "SCORE=100\nWARNINGS=()\nCRITICALS=()\nLOGS=()\n"
        'log() { LOGS+=("$1"); }\n'
        'logc() { LOGS+=("$1"); }\n'
        # Unknown external names are also denied and recorded, even if their
        # failure occurs in a substitution with an error-handling fallback.
        "command_not_found_handle() {\n"
        '    printf "%s\\n" "$1" >> "$SENTINEL"\n'
        "    return 1\n}\n"
        + function_declarations()
        + '\nif [[ "${1:-}" == "probe" ]]; then\n'
        "    blocked-probe\n"
        "    exit 1\n"
        "fi\n"
        # Calls arrive as positional arguments, not interpolated shell source.
        'while (( $# )); do\n    case "$1" in\n'
        '        check_files_exist) check_files_exist "$2" "$3"; shift 3 ;;\n'
        '        check_char_limits) check_char_limits "$2" "$3" "$4"; shift 4 ;;\n'
        "        *) exit 1 ;;\n"
        "    esac\ndone\n"
        # NUL delimiters preserve spaces and newlines in messages and paths.
        'printf "score\\0%s\\0" "$SCORE"\n'
        'for value in "${CRITICALS[@]}"; do printf "critical\\0%s\\0" "$value"; done\n'
        'for value in "${WARNINGS[@]}"; do printf "warning\\0%s\\0" "$value"; done\n'
        'for value in "${LOGS[@]}"; do printf "log\\0%s\\0" "$value"; done\n',
        encoding="utf-8",
    )
    # Deliberately do not inherit BASH_ENV, exported functions, Git bindings,
    # credentials or any real memory location from the calling environment.
    env = {
        "PATH": str(tools),
        "HOME": str(tmp_path),
        "TMPDIR": str(tmp_path),
        "LC_ALL": "C",
        "SENTINEL": str(record),
        "PYTHONDONTWRITEBYTECODE": "1",
    }

    def run(*calls: tuple[str, ...], probe: bool = False):
        args = ["probe"] if probe else [arg for call in calls for arg in call]
        result = subprocess.run(
            [bash, "--noprofile", "--norc", str(script), *args],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,  # Safety bound in seconds for these tiny offline fixtures.
        )
        if probe:
            assert result.returncode != 0
            assert record.read_text(encoding="utf-8") == "blocked-probe\n"
            return None
        assert not record.exists(), "a forbidden subprocess was attempted"
        assert result.returncode == 0, result.stderr
        assert result.stderr == ""
        fields = iter(result.stdout.split("\0")[:-1])
        values: dict[str, list[str]] = {
            "score": [], "critical": [], "warning": [], "log": []
        }
        for key in fields:
            values[key].append(next(fields))
        (score,) = values["score"]
        return State(int(score), values["critical"], values["warning"], values["log"])

    return run


# Hand count: empty = 0 bytes; "fact" = 4 bytes, with LF = 5 bytes and 1 line.
# Scores: 100 - 30 = 70; 100 - 25 = 75; present leaves 100 unchanged.
@pytest.mark.parametrize(
    ("content", "score", "critical", "logs"),
    [
        (None, 70, "missing", []),
        (b"", 75, "is empty", []),
        (b"fact", 100, None, ["  sample: 0 lines, 4 chars"]),
        (b"fact\n", 100, None, ["  sample: 1 lines, 5 chars"]),
    ],
    ids=["missing", "empty", "present-without-newline", "present-with-newline"],
)
def test_missing_and_empty_memory_scores(
    harness, tmp_path: Path, content, score, critical, logs
):
    path = tmp_path / "input with spaces.md"
    if content is not None:
        path.write_bytes(content)
    state = harness(("check_files_exist", str(path), "sample"))
    criticals = [] if critical is None else [f"sample {critical}: {path}"]
    assert state == State(score, criticals, [], logs)
    if content is None:
        assert not path.exists()
    else:
        assert path.read_bytes() == content


# Hand count: successive ASCII letters a-h/a-i/a-j/a-k/a-l occupy 8/9/10/11/12
# bytes, without LF. Caller caps 10 and 11 have integer 90% threshold 9:
# 10*90/100 = 9; 11*90/100 = 9 after truncation. At 9 there is no warning;
# 10/10 and 11/11 warn. Scores: 100-5 = 95; 100-20 = 80.
# Literal headroom examples: 10-0 = 10, 10-8 = 2, 10-9 = 1, 11-9 = 2.
@pytest.mark.parametrize(
    ("content", "limit", "score", "criticals", "warnings", "logs"),
    [
        (None, 10, 100, [], [], []),
        (b"", 10, 100, [], [], ["  sample: 10 chars remaining (OK)"]),
        (b"abcdefgh", 10, 100, [], [], ["  sample: 2 chars remaining (OK)"]),
        (b"abcdefghi", 10, 100, [], [], ["  sample: 1 chars remaining (OK)"]),
        (b"abcdefghij", 10, 95, [], ["sample approaching limit: 10/10"], []),
        (b"abcdefghijk", 10, 80, ["sample exceeds limit: 11/10 chars"], [], []),
        (b"abcdefghi", 11, 100, [], [], ["  sample: 2 chars remaining (OK)"]),
        (b"abcdefghij", 11, 95, [], ["sample approaching limit: 10/11"], []),
        (b"abcdefghijk", 11, 95, [], ["sample approaching limit: 11/11"], []),
        (b"abcdefghijkl", 11, 80, ["sample exceeds limit: 12/11 chars"], [], []),
    ],
    ids=[
        "missing", "empty", "below-warning", "equal-warning-threshold", "equal-cap",
        "above-cap", "equal-rounded-threshold", "above-rounded-threshold",
        "equal-second-cap", "above-second-cap",
    ],
)
def test_char_limit_boundaries(
    harness, tmp_path: Path, content, limit, score, criticals, warnings, logs
):
    path = tmp_path / "input with spaces.md"
    if content is not None:
        path.write_bytes(content)
    state = harness(("check_char_limits", str(path), "sample", str(limit)))
    assert state == State(score, criticals, warnings, logs)
    if content is None:
        assert not path.exists()
    else:
        assert path.read_bytes() == content


def test_checks_accumulate_without_resetting_state(harness, tmp_path: Path):
    missing = tmp_path / "missing.md"
    empty = tmp_path / "empty.md"
    empty.write_bytes(b"")
    present = tmp_path / "present.md"
    present.write_bytes(b"abcdefghij")  # Hand count: a-j = 10 ASCII bytes.
    state = harness(
        ("check_files_exist", str(missing), "missing"),
        ("check_files_exist", str(empty), "empty"),
        ("check_char_limits", str(present), "present", "10"),
        ("check_char_limits", str(present), "present", "9"),
    )
    # Cited penalties accumulate: 100-30-25-5-20 = 20; 10 exceeds caller cap 9.
    assert state == State(
        20,
        [f"missing missing: {missing}", f"empty is empty: {empty}",
         "present exceeds limit: 10/9 chars"],
        ["present approaching limit: 10/10"],
        [],
    )
    assert not missing.exists()
    assert empty.read_bytes() == b""
    assert present.read_bytes() == b"abcdefghij"


def test_subprocess_sentinel_is_armed(harness):
    """Calibrate the same stub used for forbidden names with a synthetic probe.

    All normal function calls assert that this record does not exist, so even
    an attempted command whose nonzero exit was swallowed would fail the test.
    No real bridge, Git, notification or provider executable is invoked.
    """
    harness(probe=True)
