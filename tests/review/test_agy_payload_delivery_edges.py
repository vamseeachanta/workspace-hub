"""Fixture-only review payload delivery checks for submit-to-agy.sh.

Issue #3896 supplies the 41,000-byte regression size. The cap and failure
statuses are declared in scripts/review/submit-to-agy.sh: AGY_MAX_BYTES,
emit_invalid_output, the payload write guard, and the receipt check. These
tests measure local Bash delivery; native Windows behavior is unmeasured.

Plan-lite
---------
Scope: keep this slice test-only; production transport remains unchanged.
Acceptance: independently constructed input bytes arrive completely by file;
the cap allows equality and rejects an input one byte above it; a payload write
failure and a successful reader without a receipt both produce INVALID_OUTPUT
with the declared nonzero exit status.
Validation: run this module and tests/ai/test_run_agent_agy.py offline, using
local executable fixtures and temporary directories outside the repository.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import textwrap
from types import SimpleNamespace

import pytest


WRAPPER = Path(__file__).resolve().parents[2] / "scripts/review/submit-to-agy.sh"
# Independent hand count: ten ASCII digits * four + newline = 41 bytes;
# repeating that record a thousand times gives the issue's 41,000 bytes.
LARGE_CONTENT = (b"0123456789" * 4 + b"\n") * 1000


def _executable(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


@pytest.fixture
def delivery(tmp_path):
    # Both quote characters and spaces occur in the executable, input, payload,
    # capture and logging paths. Nothing is interpolated into shell source.
    root = tmp_path / "delivery with 'single' and \"double\" quotes"
    root.mkdir()
    bin_dir = root / "bin"
    bin_dir.mkdir()
    temp_dir = root / "temp"
    temp_dir.mkdir()
    repo = root / "repo"
    repo.mkdir()
    capture = root / "capture.json"
    payload_copy = root / "payload.bin"

    # Only required local utilities are visible: no provider executables,
    # credential helpers, network programs or inherited command overrides.
    for name in (
        "bash", "dirname", "mktemp", "tr", "date", "wc", "mkdir",
        "grep", "cat", "tail", "rm",
    ):
        executable = shutil.which(name)
        assert executable is not None, f"required fixture utility: {name}"
        (bin_dir / name).symlink_to(executable)

    reader = bin_dir / "local reader"
    _executable(
        reader,
        f"#!{sys.executable}\n" + textwrap.dedent(r'''
            import json
            import os
            from pathlib import Path
            import sys

            args = sys.argv[1:]
            prompt = args[args.index("--print") + 1]
            reference = prompt.split(
                "The review payload has been written to this local file:\n", 1
            )[1].split("\n", 1)[0]
            content = Path(reference).read_bytes()
            Path(os.environ["FIXTURE_PAYLOAD_COPY"]).write_bytes(content)
            Path(os.environ["FIXTURE_CAPTURE"]).write_text(json.dumps({
                "argv": args, "payload_path": reference, "cwd": os.getcwd(),
            }))
            # A successful local process without a receipt must still fail
            # delivery validation (the wrapper's receipt check declares rc=5).
            if os.environ.get("FIXTURE_OMIT_RECEIPT"):
                sys.exit(0)
            receipt, = (
                line for line in content.decode("utf-8").splitlines()
                if line.startswith("PAYLOAD-RECEIPT: ")
            )
            print("## Verdict\nAPPROVE\n\n## Retrieval\n" + receipt)
            print("\n## Findings\n(none)\n\n## Blockers\n(none)")
        '''),
    )
    env = {
        "PATH": str(bin_dir),
        "TMPDIR": str(temp_dir),
        "REPO_ROOT": str(repo),
        "AGY_CMD": str(reader),
        "AGY_REVIEW_MODE": "1",  # Review-mode selector declared by the wrapper.
        "PYTHONDONTWRITEBYTECODE": "1",
        "FIXTURE_CAPTURE": str(capture),
        "FIXTURE_PAYLOAD_COPY": str(payload_copy),
    }
    return SimpleNamespace(
        root=root, bin_dir=bin_dir, temp_dir=temp_dir, repo=repo, env=env,
        capture=capture, payload_copy=payload_copy,
    )


def _submit(delivery, content: bytes):
    source = delivery.root / "input plan.md"
    source.write_bytes(content)
    result = subprocess.run(
        [str(delivery.bin_dir / "bash"), str(WRAPPER), "--file", str(source),
         "--prompt", "Review this synthetic content."],
        env=delivery.env,
        cwd=delivery.root,
        capture_output=True,
        text=True,
        # Synthetic local-process deadline, not a provider or platform cap.
        timeout=30,
    )
    (delivery.root / "stdout.md").write_text(result.stdout, encoding="utf-8")
    (delivery.root / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    return result


def _assert_complete_delivery(delivery, expected: bytes, result):
    assert result.returncode == 0, result.stderr
    assert "INVALID_OUTPUT" not in result.stdout
    assert "UNAVAILABLE" not in result.stdout
    record = json.loads(delivery.capture.read_text(encoding="utf-8"))
    payload_path = Path(record["payload_path"])
    assert payload_path.is_relative_to(delivery.temp_dir)
    assert Path(record["cwd"]) == payload_path.parent
    assert payload_path.name == "agy-review-payload.md"
    assert "'single'" in str(payload_path) and '"double"' in str(payload_path)
    assert record["argv"][0] == "--print"
    assert record["argv"][2:] == [
        "--print-timeout", "240s", "--dangerously-skip-permissions",
    ]  # Existing argument contract and AGY_PRINT_TIMEOUT default declaration.
    assert str(payload_path) in record["argv"][1]
    assert expected.decode("utf-8") not in "\n".join(record["argv"])

    # Recover framing from the delivered file, then compare the entire body,
    # including its last byte, against independently constructed input bytes.
    header, start, body = delivery.payload_copy.read_bytes().split(b"\n", 2)
    prefix = b"--- "
    suffix = b" START ---"
    assert start.startswith(prefix) and start.endswith(suffix)
    boundary = start[len(prefix):-len(suffix)]
    assert boundary in header
    ending = b"\n--- " + boundary + b" END ---\n"
    receipt, = (line for line in body.splitlines()
                if line.startswith(b"PAYLOAD-RECEIPT: "))
    assert body == expected + ending + receipt + b"\n"
    assert receipt.decode("utf-8") in result.stdout
    assert list(delivery.repo.glob("logs/orchestrator/agy/*.log"))


def _assert_invalid(result, reason: str):
    assert result.returncode != 0
    assert result.stdout.startswith("## Verdict\nINVALID_OUTPUT (")
    assert reason in result.stdout
    assert "## Retrieval" in result.stdout
    assert "## Findings" in result.stdout
    assert "## Blockers" in result.stdout
    assert "UNAVAILABLE" not in result.stdout


def test_large_payload_travels_by_file(delivery):
    assert len(LARGE_CONTENT) == 41000  # Issue #3896, hand count above.
    _assert_complete_delivery(delivery, LARGE_CONTENT, _submit(delivery, LARGE_CONTENT))


def test_cap_violation_has_invalid_output_and_nonzero_exit(delivery):
    # Explicit synthetic boundary: the issue's 41,000 bytes exceed this cap
    # by exactly one byte, independently of the wrapper's default cap.
    delivery.env["AGY_MAX_BYTES"] = "40999"
    result = _submit(delivery, LARGE_CONTENT)
    _assert_invalid(result, "payload exceeds delivery cap (41000 > 40999 bytes")
    assert result.returncode == 3  # Wrapper's review-cap guard declaration.
    assert not delivery.capture.exists()
    assert not delivery.payload_copy.exists()


def test_fake_reader_sees_complete_payload(delivery):
    # Quotes, shell metacharacters, UTF-8 and final whitespace must survive.
    content = "FIRST 'quoted' \"text\"\n$(literal) `literal` π\nLAST\t \n".encode("utf-8")
    # Equality is allowed: the cap guard declares a strict greater-than check.
    # Length is calculated from fixture bytes, never from the wrapper's output.
    delivery.env["AGY_MAX_BYTES"] = str(len(content))
    _assert_complete_delivery(delivery, content, _submit(delivery, content))


def test_local_payload_write_failure_is_invalid_output(delivery):
    # Make the payload destination a directory so the real shell redirection
    # fails, even with elevated filesystem permissions. No data is removed.
    real_mktemp = str((delivery.bin_dir / "mktemp").resolve())
    shim = delivery.root / "failing mktemp"
    _executable(shim, f"#!{sys.executable}\n" + textwrap.dedent('''
        import os
        from pathlib import Path
        import subprocess
        import sys

        result = subprocess.run([os.environ["FIXTURE_MKTEMP"], *sys.argv[1:]],
                                check=True, capture_output=True, text=True)
        if "-d" in sys.argv:
            (Path(result.stdout.strip()) / "agy-review-payload.md").mkdir()
        print(result.stdout, end="")
    '''))
    # Select the shim through a fresh directory rather than replace a utility.
    shim_dir = delivery.root / "failure bin"
    shim_dir.mkdir()
    (shim_dir / "mktemp").symlink_to(shim)
    delivery.env["PATH"] = str(shim_dir) + os.pathsep + delivery.env["PATH"]
    delivery.env["FIXTURE_MKTEMP"] = real_mktemp
    result = _submit(delivery, LARGE_CONTENT)
    _assert_invalid(result, "payload temp-file write failed")
    assert result.returncode == 4  # Wrapper's temp-file write guard declaration.
    assert not delivery.capture.exists()
    assert not delivery.payload_copy.exists()


def test_successful_reader_without_receipt_is_invalid_output(delivery):
    delivery.env["FIXTURE_OMIT_RECEIPT"] = "1"
    result = _submit(delivery, LARGE_CONTENT)
    _assert_invalid(result, "payload receipt nonce missing")
    assert result.returncode == 5  # Wrapper's missing-receipt check declaration.
    assert delivery.capture.exists()  # The fixture did run and return success.
    assert LARGE_CONTENT in delivery.payload_copy.read_bytes()
