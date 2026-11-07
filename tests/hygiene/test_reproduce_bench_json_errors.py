"""CLI decoder regressions for issue #3446; all inputs are synthetic.

A locally selected synthetic fixture uses 16384 nested arrays around the
eight-character SENTINEL; a raw-decoder RecursionError assertion establishes
its adequacy before the CLI envelope is tested:
2 * 16384 bracket bytes + 8 string bytes + 2 quotes = 32778 ASCII bytes.
These are finite test safety parameters, not production limits. The 30-second
child timeout is a test safety budget; expiration fails rather than rejects.
Setup status 2 and its diagnostic follow reproduce_bench.main and the setup
contract in REPRODUCE_BENCH.md. Configuration and timing numbers reuse config
and measured from test_reproduce_bench.py; no real rebuild commands are run.
"""

import json
import os
import subprocess
import sys

import pytest

import test_reproduce_bench as existing


SETUP_ERROR = (
    "benchmark input or execution setup error; "
    "check configuration and committed files\n"
)
REPORT_MARKER = b"retained JSON report\n"
HTML_MARKER = b"retained HTML report\n"

# Construct and decode deep input only in a disposable interpreter. Keep the
# default recursion limit so the real decoder, rather than schema validation,
# establishes the failure. The child calls the real main(), not a replacement.
CHILD = r'''
import importlib.util
import json
import sys
from pathlib import Path

module_path, root_path, mode = sys.argv[1:]
root = Path(root_path)
spec = importlib.util.spec_from_file_location("reproduce_bench", module_path)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
repo = root / "repo"
repo.mkdir(exist_ok=True)
config_path = root / "config.json"
output = root / "report.json"
html_output = output.with_suffix(".html")
output.write_bytes(b"retained JSON report\n")
html_output.write_bytes(b"retained HTML report\n")
loads = json.loads

# These sentinels independently expose any benchmark or command execution.
def forbidden(*args, **kwargs):
    (root / "execution-started").touch()
    raise AssertionError("unexpected benchmark or command execution")

bench.benchmark = forbidden
bench.run_process = forbidden
bench.git = forbidden

if mode == "valid":
    report = loads((root / "stand-in.json").read_text(encoding="utf-8"))
    settings = loads((root / "settings.json").read_text(encoding="utf-8"))
    config_path.write_text(json.dumps(settings), encoding="utf-8", newline="\n")

    def stand_in(repo_arg, config_arg, *, anonymise_host):
        assert repo_arg == repo
        assert all(config_arg[key] == value for key, value in settings.items())
        assert anonymise_host is True
        (root / "benchmark-called").touch()
        return report

    bench.benchmark = stand_in
else:
    def no_schema(*args, **kwargs):
        (root / "schema-started").touch()
        raise AssertionError("decoder failure must precede schema validation")

    bench.parse_config = no_schema
    if mode == "deep":
        payload = "[" * 16384 + '"SENTINEL"' + "]" * 16384
        assert len(payload.encode("ascii")) == 32778
        try:
            loads(payload)
        except RecursionError:
            (root / "raw-decoder-recursion").touch()
        else:
            raise AssertionError("fixture did not reproduce decoder recursion")
    elif mode == "malformed":
        payload = '{"synthetic": "SENTINEL",'
    elif mode == "injected":
        # Valid tiny JSON isolates exception routing from schema rejection.
        payload = '{"timeout_seconds": 5, "repeats": 1, "regression_ratio": 1.5}'
    else:
        raise AssertionError("unknown test mode")
    config_path.write_text(payload, encoding="utf-8", newline="\n")

    def decoder(text):
        assert text == payload
        (root / "cli-decoder-called").touch()
        if mode == "injected":
            raise RecursionError("SENTINEL decoder detail " + str(config_path))
        try:
            return loads(text)
        except RecursionError:
            (root / "cli-decoder-recursion").touch()
            raise

    bench.json.loads = decoder

raise SystemExit(bench.main([
    "--repo", str(repo), "--config", str(config_path), "--out", str(output)
]))
'''


def run_child(tmp_path, mode):
    # -B also prevents import bytecode with -I, which ignores Python env flags.
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env["TMPDIR"] = str(tmp_path)
    try:
        return subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                "-c",
                CHILD,
                str(existing.MODULE),
                str(tmp_path),
                mode,
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("disposable decoder interpreter timed out")


def assert_setup_rejection(result, tmp_path):
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == SETUP_ERROR
    for forbidden in (
        "SENTINEL", "RecursionError", "JSONDecodeError", "Traceback", str(tmp_path)
    ):
        assert forbidden not in result.stdout + result.stderr
    assert (tmp_path / "cli-decoder-called").is_file()
    assert not (tmp_path / "schema-started").exists()
    assert not (tmp_path / "execution-started").exists()


def test_deep_config_uses_generic_setup_error(tmp_path):
    result = run_child(tmp_path, "deep")
    # Require both raw decoding and decoding inside main() to raise recursion.
    assert (tmp_path / "raw-decoder-recursion").is_file()
    assert (tmp_path / "cli-decoder-recursion").is_file()
    assert_setup_rejection(result, tmp_path)


def test_decoder_recursion_never_starts_benchmark(tmp_path):
    result = run_child(tmp_path, "injected")
    assert_setup_rejection(result, tmp_path)


@pytest.mark.parametrize("mode", ["malformed", "deep", "injected"])
def test_json_failure_preserves_existing_reports(tmp_path, mode):
    result = run_child(tmp_path, mode)
    # Inspect retained bytes independently even if the error envelope is wrong.
    assert (tmp_path / "report.json").read_bytes() == REPORT_MARKER
    assert (tmp_path / "report.html").read_bytes() == HTML_MARKER
    assert_setup_rejection(result, tmp_path)


def test_valid_tiny_config_keeps_report_status(tmp_path):
    repo = tmp_path / "fixture-repo"
    repo.mkdir()
    existing.git(repo, "init", "-q")
    existing.commit_fixture(repo, {"build.py": "pass"})
    # Reuse test_report_and_schema's measured report fixture with one artifact.
    # Three one-second observations give min = median = max = 1, below the
    # guide's default 60-second budget, so PASS without regression implies 0.
    report = existing.measured(repo, tmp_path, [1] * 3)
    assert report["artifacts"]
    assert all(
        item["verdict"] == "PASS" and not item["regression"]
        for item in report["artifacts"]
    )
    expected_status = 0
    (tmp_path / "stand-in.json").write_text(
        json.dumps(report), encoding="utf-8", newline="\n"
    )
    (tmp_path / "settings.json").write_text(
        json.dumps(existing.config(repeats=3)), encoding="utf-8", newline="\n"
    )
    result = run_child(tmp_path, "valid")
    assert result.returncode == expected_status
    assert result.stdout == result.stderr == ""
    assert (tmp_path / "benchmark-called").is_file()
    assert not (tmp_path / "execution-started").exists()
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8")) == report
    assert (tmp_path / "report.html").read_text(
        encoding="utf-8"
    ) == existing.bench.render_html(report)
