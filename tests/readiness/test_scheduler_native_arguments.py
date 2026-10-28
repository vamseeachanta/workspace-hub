"""Synthetic scheduler-call regressions for issue #3737.

Contract: issue #3737 and scripts/readiness/collect-equality.sh, section 8
(SCHEDULER). The existing
declarations define the argv, command-scoped conversion exclusion and failure
diagnostic. No scheduler policy thresholds or live measurements are introduced.
Only that production section executes; no solver or provider probe is loaded.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


COLLECTOR = Path(__file__).resolve().parents[2] / "scripts/readiness/collect-equality.sh"


def _query(root, *, rows=b"", status=0, inherited=None, available=True):
    """Record token boundaries and child/parent settings in a fresh fixture shell."""
    root.mkdir()
    bindir = root / "bin"
    bindir.mkdir()
    (root / "rows.csv").write_bytes(rows)
    shim = bindir / "schtasks"
    shim.write_text(
        '#!/bin/bash\n'
        'printf "%s\\0" "$@" > "$RECORD_DIR/argv"\n'
        'printf "%s" "${MSYS2_ARG_CONV_EXCL-unset}" > "$RECORD_DIR/conversion"\n'
        'cat "$RECORD_DIR/rows.csv"\n'
        'if [[ "$QUERY_STATUS" != 0 ]]; then\n'
        '  printf "%s\\n" "synthetic query diagnostic" >&2\n'
        'fi\n'
        'exit "$QUERY_STATUS"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    source = COLLECTOR.read_text(encoding="utf-8")
    start = "# ── 8. SCHEDULER"
    end = "# ── 9. PROVENANCE"
    assert source.count(start) == source.count(end) == 1
    section = source.split(start)[1].split(end)[0].split("\n", 1)[1]
    # A fresh environment excludes BASH_ENV, exported functions and Git bindings.
    # No ambient command can replace the synthetic query or select another OS.
    env = {
        "PATH": f"{bindir}:/usr/bin:/bin",
        "HOME": str(root),
        "TMPDIR": str(root),
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C",
        "OS": "windows",
        "RECORD_DIR": str(root),
        "QUERY_STATUS": str(status),
    }
    if inherited is not None:
        env["MSYS2_ARG_CONV_EXCL"] = inherited
    have = 'have() { command -v "$1" >/dev/null 2>&1; }\n'
    if not available:
        # Deterministic unavailability even if the test runner has a scheduler.
        have = 'have() { return 1; }\n'
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-c",
         "set -uo pipefail\n" + have + section +
         '\nprintf "%s %s %s\\n" "$has_sync" "$has_parity" "$job_count"\n'
         'printf "%s" "${MSYS2_ARG_CONV_EXCL-unset}" > "$RECORD_DIR/after"\n'],
        env=env, capture_output=True, text=True, check=False,
    )
    return result


@pytest.mark.parametrize("inherited", [None, "", "existing-exclusion"])
def test_native_query_preserves_slash_arguments(tmp_path, inherited):
    """The declared four native tokens survive; the exclusion stays call-scoped."""
    root = tmp_path / "fixture with spaces"
    result = _query(root, inherited=inherited)
    assert result.returncode == 0, result.stderr
    # Compare NUL-separated bytes: joining tokens with spaces would hide changes
    # such as passing '/query /fo' as a single argument.
    assert (root / "argv").read_bytes() == b"/query\0/fo\0csv\0/nh\0"
    assert (root / "conversion").read_bytes() == b"*"
    expected_after = "unset" if inherited is None else inherited
    assert (root / "after").read_text() == expected_after
    # Hand count: no CSV records means zero tasks and neither name predicate.
    assert result.stdout == "false false 0\n"
    assert result.stderr == ""


@pytest.mark.parametrize("status", [7, 42])
@pytest.mark.parametrize("partial", [b"", b'"\\Synthetic\\Repo Sync","N/A","Ready"\r\n'])
def test_failed_query_is_not_empty_success(tmp_path, status, partial):
    """Arbitrary synthetic nonzero statuses must survive in the failure diagnostic.

    Section 8 intentionally aborts with shell status one and reports the native
    status separately. These fixture statuses are test inputs, not policy values.
    """
    failure = _query(tmp_path / "failed", rows=partial, status=status)
    empty = _query(tmp_path / "empty")
    absent_root = tmp_path / "absent"
    absent = _query(absent_root, available=False)
    assert failure.returncode == 1
    assert failure.stdout == ""
    assert failure.stderr == (
        f"collect-equality.sh: schtasks query failed (exit {status}); evidence not written\n"
    )
    # Both empty success and no executable complete, with distinct evidence.
    assert empty.returncode == absent.returncode == 0
    assert empty.stdout == "false false 0\n"
    assert absent.stdout == "unknown unknown unknown\n"
    assert empty.stderr == absent.stderr == ""
    assert not (absent_root / "argv").exists()


def test_crlf_task_rows_are_counted(tmp_path):
    r"""Hand count: three quoted CSV rows, plus two non-record lines = three tasks.

    Repo Sync sets sync; Parity Review sets parity. The third row has commas and
    a doubled quote in its unrelated name. Alias text in its status alone must
    set neither predicate, checked independently with that row by itself.
    """
    unrelated = b'"\\Synthetic\\Archive, ""Daily""","N/A","Repo Sync Parity Review"\r\n'
    listing = (
        b"INFO: synthetic listing\r\n\r\n"
        b'"\\Synthetic\\Repo Sync","N/A","Ready"\r\n'
        b'"\\Synthetic\\Parity Review","N/A","Ready"\r\n'
        + unrelated
    )
    result = _query(tmp_path / "listing", rows=listing)
    decoy = _query(tmp_path / "status only", rows=unrelated)
    assert result.returncode == decoy.returncode == 0
    assert result.stdout == "true true 3\n"
    # Hand count: the unrelated row alone is one task with no matching name.
    assert decoy.stdout == "false false 1\n"
    assert result.stderr == decoy.stderr == ""
