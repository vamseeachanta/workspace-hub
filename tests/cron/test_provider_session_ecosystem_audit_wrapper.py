from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import textwrap

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "provider-session-ecosystem-audit.sh"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"

# Contract: scripts/cron/provider-session-ecosystem-audit.sh output/key checks.
JSON_ARTIFACT = Path("analysis/provider-session-ecosystem-audit.json")
MARKDOWN_ARTIFACT = Path("docs/reports/provider-session-ecosystem-audit.md")
REQUIRED_PROVIDERS = ("claude", "codex", "hermes", "gemini")
# Synthetic examples deliberately include whitespace, an empty argument and a glob.
FORWARDED_ARGS = ("--fixture-option", "value with spaces", "", "*.json")
REPORT = "# Synthetic audit\n\nFixture output only.\n"
# Fixture-defined failure sentinel, per Python's SystemExit integer-status contract.
ANALYZER_FAILURE = 23


@pytest.fixture
def wrapper_repo(tmp_path: Path) -> Path:
    root = tmp_path / "temporary repository"
    wrapper = root / "scripts/cron" / SCRIPT.name
    wrapper.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPT, wrapper)
    assert wrapper.read_bytes() == SCRIPT.read_bytes()

    analyzer = root / "scripts/analysis/provider_session_ecosystem_audit.py"
    analyzer.parent.mkdir(parents=True)
    analyzer.write_text(
        textwrap.dedent(
            """\
            import json
            import os
            from pathlib import Path
            import sys

            root = Path.cwd()
            # Python CLI convention: argv[0] is the script, remaining entries are arguments.
            (root / "analyzer-call.json").write_text(json.dumps({
                "argv": sys.argv[1:],
                "cwd": str(root),
                "pythonpath": os.environ["PYTHONPATH"],
            }), encoding="utf-8")
            print("synthetic analyzer stdout", flush=True)
            print("synthetic analyzer stderr", file=sys.stderr, flush=True)
            mode = os.environ["FIXTURE_MODE"]
            if mode == "analyzer-failure":
                raise SystemExit(int(os.environ["FIXTURE_FAILURE"]))
            outputs = {
                "json": ("analysis/provider-session-ecosystem-audit.json",
                         os.environ["FIXTURE_JSON"]),
                "markdown": ("docs/reports/provider-session-ecosystem-audit.md",
                             os.environ["FIXTURE_REPORT"]),
            }
            for kind, (relative_path, content) in outputs.items():
                if mode == "absent-" + kind:
                    continue
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            """
        ),
        encoding="utf-8",
    )
    shim = root / "bin/uv"
    shim.parent.mkdir()
    shim.write_text(
        f"#!{sys.executable}\n"
        + textwrap.dedent(
            """\
            import json
            import os
            from pathlib import Path
            import sys

            # Python argv convention and the wrapper's 'run --no-project python' prefix.
            _, *args = sys.argv
            run, no_project, python, *python_args = args
            assert (run, no_project, python) == ("run", "--no-project", "python")
            with Path("uv-calls.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(args) + "\\n")
            # Keep stdin intact so the wrapper's inline validator executes unchanged.
            os.execv(sys.executable, [sys.executable, *python_args])
            """
        ),
        encoding="utf-8",
    )
    shim.chmod(shim.stat().st_mode | stat.S_IXUSR)
    for directory in ("home", "tmp", "extra-imports"):
        (root / directory).mkdir()
    return root


def _run_wrapper(
    root: Path, mode: str = "success", missing_provider: str | None = None
) -> subprocess.CompletedProcess[str]:
    payload = {"providers": {key: {} for key in REQUIRED_PROVIDERS if key != missing_provider}}
    return subprocess.run(
        ["bash", str(root / "scripts/cron" / SCRIPT.name), *FORWARDED_ARGS],
        cwd=root / "tmp",  # The wrapper must resolve and enter its own repository root.
        # A fresh environment avoids inherited provider configuration and Git bindings.
        env={
            "PATH": str(root / "bin") + os.pathsep + os.defpath,
            "HOME": str(root / "home"),
            "TMPDIR": str(root / "tmp"),
            "PYTHONDONTWRITEBYTECODE": "1",  # Python's documented bytecode-disable flag.
            "PYTHONPATH": str(root / "extra-imports"),
            "LC_ALL": "C",
            "FIXTURE_MODE": mode,
            "FIXTURE_JSON": "{" if mode == "malformed-json" else json.dumps(payload),
            "FIXTURE_REPORT": REPORT,
            "FIXTURE_FAILURE": str(ANALYZER_FAILURE),
        },
        capture_output=True,
        text=True,
        check=False,
        timeout=30,  # Test-defined seconds budget for local subprocesses; no network work.
    )


def _assert_calls_and_log(root: Path, *, validator_ran: bool) -> None:
    call = json.loads((root / "analyzer-call.json").read_text(encoding="utf-8"))
    assert call == {
        "argv": list(FORWARDED_ARGS),
        "cwd": str(root),
        "pythonpath": str(root / "src") + os.pathsep + str(root / "extra-imports"),
    }
    expected_calls = [
        [
            "run", "--no-project", "python",
            "scripts/analysis/provider_session_ecosystem_audit.py", *FORWARDED_ARGS,
        ]
    ]
    if validator_ran:
        expected_calls.append(["run", "--no-project", "python", "-"])
    assert [
        json.loads(line)
        for line in (root / "uv-calls.jsonl").read_text(encoding="utf-8").splitlines()
    ] == expected_calls
    # Singleton unpacking requires exactly the log created by this wrapper invocation.
    log, = (root / "logs/quality").glob("provider-session-ecosystem-audit-*.log")
    assert log.read_text(encoding="utf-8") == (
        "synthetic analyzer stdout\nsynthetic analyzer stderr\n"
    )


def test_wrapper_subprocess_writes_artifacts_and_log(wrapper_repo: Path) -> None:
    result = _run_wrapper(wrapper_repo)

    assert result.returncode == os.EX_OK
    assert result.stdout == result.stderr == ""
    assert json.loads((wrapper_repo / JSON_ARTIFACT).read_text(encoding="utf-8")) == {
        "providers": {"claude": {}, "codex": {}, "hermes": {}, "gemini": {}}
    }
    assert (wrapper_repo / MARKDOWN_ARTIFACT).read_text(encoding="utf-8") == REPORT
    _assert_calls_and_log(wrapper_repo, validator_ran=True)


@pytest.mark.parametrize("missing_artifact", [JSON_ARTIFACT, MARKDOWN_ARTIFACT], ids=["json", "markdown"])
def test_wrapper_rejects_absent_output(wrapper_repo: Path, missing_artifact: Path) -> None:
    mode = "absent-json" if missing_artifact == JSON_ARTIFACT else "absent-markdown"
    result = _run_wrapper(wrapper_repo, mode)

    assert result.returncode != os.EX_OK
    assert result.stderr.strip() == f"ERROR: missing {wrapper_repo / missing_artifact}"
    assert not (wrapper_repo / missing_artifact).exists()
    remaining = MARKDOWN_ARTIFACT if missing_artifact == JSON_ARTIFACT else JSON_ARTIFACT
    assert (wrapper_repo / remaining).is_file()
    _assert_calls_and_log(wrapper_repo, validator_ran=False)


@pytest.mark.parametrize("missing_provider", REQUIRED_PROVIDERS)
def test_wrapper_rejects_missing_provider(wrapper_repo: Path, missing_provider: str) -> None:
    result = _run_wrapper(wrapper_repo, missing_provider=missing_provider)

    assert result.returncode != os.EX_OK
    assert result.stderr.strip() == f"missing provider keys: {missing_provider}"
    assert (wrapper_repo / JSON_ARTIFACT).is_file()
    assert (wrapper_repo / MARKDOWN_ARTIFACT).read_text(encoding="utf-8") == REPORT
    _assert_calls_and_log(wrapper_repo, validator_ran=True)


def test_wrapper_rejects_malformed_json(wrapper_repo: Path) -> None:
    result = _run_wrapper(wrapper_repo, "malformed-json")

    assert result.returncode != os.EX_OK
    assert "JSONDecodeError" in result.stderr
    assert (wrapper_repo / JSON_ARTIFACT).read_text(encoding="utf-8") == "{"
    assert (wrapper_repo / MARKDOWN_ARTIFACT).read_text(encoding="utf-8") == REPORT
    _assert_calls_and_log(wrapper_repo, validator_ran=True)


def test_wrapper_propagates_analyzer_failure(wrapper_repo: Path) -> None:
    result = _run_wrapper(wrapper_repo, "analyzer-failure")

    assert result.returncode == ANALYZER_FAILURE
    assert result.stdout == result.stderr == ""
    assert not (wrapper_repo / JSON_ARTIFACT).exists()
    assert not (wrapper_repo / MARKDOWN_ARTIFACT).exists()
    _assert_calls_and_log(wrapper_repo, validator_ran=False)


def test_wrapper_exists_and_uses_uv_no_project_python() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "PYTHONPATH=\"${REPO_ROOT}/src" in text
    assert "uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py" in text
    assert "analysis/provider-session-ecosystem-audit.json" in text
    assert "docs/reports/provider-session-ecosystem-audit.md" in text


def test_schedule_declares_provider_session_ecosystem_audit_task() -> None:
    payload = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))
    tasks = payload["tasks"]
    task = next(item for item in tasks if item["id"] == "provider-session-ecosystem-audit")

    assert task["schedule"] == "15 4 * * 1"
    assert task["log"] == "logs/quality/provider-session-ecosystem-audit-*.log"
    assert "bash scripts/cron/provider-session-ecosystem-audit.sh" in task["command"]
