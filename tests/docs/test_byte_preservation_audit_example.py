"""Execute only the synthetic example in the byte-preservation audit.

Expected payloads are hand-written literals: change alpha to gamma and copy
every other byte unchanged, per issue #4089's acceptance example. The hex
escapes below are synthetic invalid UTF-8 sentinels, not captured content.
"""

from pathlib import Path
import re

import pytest


AUDIT = (
    Path(__file__).resolve().parents[2]
    / "docs/reports/byte-preservation-rewrite-audit.md"
)


@pytest.fixture
def example(tmp_path, monkeypatch):
    text = AUDIT.read_text(encoding="utf-8")
    blocks = re.findall(r"^```python\n(.*?)^```$", text, flags=re.MULTILINE | re.DOTALL)
    (source,) = blocks
    monkeypatch.chdir(tmp_path)
    namespace = {}
    exec(compile(source, str(AUDIT), "exec"), namespace)
    return namespace


def test_documented_binary_capture_preserves_delimiters(example):
    assert example["binary_capture"] == b"alpha\r\nbeta\r\n"
    assert example["text_capture"] == "alpha\nbeta\n"
    assert example["rewritten"] == b"gamma\r\nbeta\r\n"


@pytest.mark.parametrize(
    "payload, expected",
    [
        pytest.param(b"alpha\r\nbeta\r\n", b"gamma\r\nbeta\r\n", id="crlf"),
        pytest.param(b"alpha\nbeta\n", b"gamma\nbeta\n", id="lf"),
        pytest.param(b"alpha\rbeta\r", b"gamma\rbeta\r", id="cr"),
        pytest.param(
            b"alpha\r\nbeta\nalpha\r",
            b"gamma\r\nbeta\ngamma\r",
            id="mixed",
        ),
        pytest.param(b"alpha\r\nbeta", b"gamma\r\nbeta", id="unterminated"),
        pytest.param(
            b"\xffalpha\r\nbeta\xfe\n\x80",
            b"\xffgamma\r\nbeta\xfe\n\x80",
            id="undecodable",
        ),
        pytest.param(b"beta\r\n\xfftail", b"beta\r\n\xfftail", id="no-match"),
    ],
)
def test_documented_token_replacement_preserves_unrelated_bytes(example, payload, expected):
    assert example["replace_token"](payload) == expected
