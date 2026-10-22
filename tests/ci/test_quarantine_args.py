"""Expected tokens are expanded by hand from the original workflow's loop.

Each non-comment line yields --deselect, the node-id, --deselect, its alternate
prefix. The independent bash oracle is the original domain-matrix.yml loop.
"""

import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "scripts/ci/quarantine_args.py"
BASH_ORACLE = r'''
DESELECT=()
if [ -f "$QUARANTINE_FILE" ]; then
  while IFS= read -r raw; do
    line="${raw%%#*}"
    line="$(echo "$line" | xargs || true)"
    [ -z "$line" ] && continue
    DESELECT+=(--deselect "$line")
    if [ "${line#tests/}" != "$line" ]; then
      DESELECT+=(--deselect "${line#tests/}")
    else
      DESELECT+=(--deselect "tests/${line}")
    fi
  done < "$QUARANTINE_FILE"
fi
if [ "${#DESELECT[@]}" -gt 0 ]; then
  printf '%s\0' "${DESELECT[@]}"
fi
'''


@pytest.fixture
def sample(tmp_path):
    script = tmp_path / SOURCE.name
    script.write_bytes(SOURCE.read_bytes())
    source = tmp_path / "quarantine.txt"
    source.write_text(
        "# comment\n\n  tests/unit/test_a.py::test_one   # trailing comment\n"
        "unit/test_b.py::test_two \t\n"
    )
    return script, source


def test_comments_blanks_spaces_and_prefixes(sample):
    script, source = sample
    assert runpy.run_path(str(script))["build_args"](source) == [
        "--deselect", "tests/unit/test_a.py::test_one",
        "--deselect", "unit/test_a.py::test_one",
        "--deselect", "unit/test_b.py::test_two",
        "--deselect", "tests/unit/test_b.py::test_two",
    ]


def test_absent(sample, tmp_path):
    script, _ = sample
    assert runpy.run_path(str(script))["build_args"](tmp_path / "absent") == []


@pytest.mark.parametrize("content", [
    "# comment\n\n tests/a.py::test_a  # inline\nb.py::test_b \t\n",
    "", "tests/final.py::test_no_newline", '"tests/a.py::test spaced"\n',
    '"tests/a.py::test\\b"\n', 'tests/a.py::test\\ spaced\n',
    'tests/a.py::test[unmatched\']\n', 'tests/a.py::test\r\n',
    '"tests/a.py::test  spaced"\n',
])
def test_matches_existing_bash(sample, content, monkeypatch):
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not on PATH; original-loop comparison unavailable")
    script, source = sample
    source.write_text(content)
    monkeypatch.setenv("QUARANTINE_FILE", str(source))
    expected = subprocess.run([bash, "-c", BASH_ORACLE], capture_output=True, check=True)
    result = subprocess.run(
        [sys.executable, str(script), str(source), "--null"], capture_output=True, check=True,
    )
    assert result.stdout == expected.stdout
    display = subprocess.run(
        [sys.executable, str(script), str(source)], capture_output=True, check=True,
    )
    assert display.stdout.rstrip(b"\n") == expected.stdout.rstrip(b"\0").replace(b"\0", b" ")
