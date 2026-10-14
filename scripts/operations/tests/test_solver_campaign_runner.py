import ast
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import xml.etree.ElementTree as ET
import uuid
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = REPO_ROOT / "scripts" / "operations" / "solver-campaign" / "campaign_runner.py"
WRAPPER_PATH = REPO_ROOT / "scripts" / "operations" / "solver-campaign" / "run-solver-campaigns.bat"
RUNNER_CREATION_FLAGS = 0
if os.name == "nt":
    RUNNER_CREATION_FLAGS = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NO_WINDOW


def load_runner():
    spec = importlib.util.spec_from_file_location("campaign_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def runner():
    return load_runner()


@pytest.fixture()
def work_area():
    base = Path(os.environ.get("TMPDIR") or os.environ.get("TEMP") or tempfile.gettempdir())
    path = base / f"solver-campaign-test-{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture()
def root(work_area):
    root = work_area / "campaign-root"
    (root / "approved").mkdir(parents=True)
    (root / "state").mkdir()
    (root / "done").mkdir()
    return root


@pytest.fixture()
def fake_checkout(work_area):
    checkout = work_area / "checkout"
    commit = "a" * 40
    git_dir = checkout / ".git"
    (git_dir / "refs" / "heads").mkdir(parents=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git_dir / "refs" / "heads" / "main").write_text(f"{commit}\n", encoding="utf-8")
    (checkout / "drivers").mkdir()
    (checkout / "drivers" / "driver.py").write_text(
        textwrap.dedent(
            """
            import argparse
            import json
            import os
            import pathlib
            import signal
            import sys
            import time

            parser = argparse.ArgumentParser()
            parser.add_argument("--progress-dir")
            parser.add_argument("--total", type=int, default=1)
            parser.add_argument("--write", type=int, default=None)
            parser.add_argument("--exit-code", type=int, default=0)
            parser.add_argument("--sleep", type=float, default=0.0)
            parser.add_argument("--record")
            args = parser.parse_args()
            if args.record:
                pathlib.Path(args.record).write_text(json.dumps(sys.argv), encoding="utf-8")
            stop = False
            def _stop(signum, frame):
                global stop
                stop = True
            signal.signal(signal.SIGTERM, _stop)
            end = time.monotonic() + args.sleep
            while time.monotonic() < end:
                if stop:
                    sys.exit(77)
                time.sleep(0.05)
            if args.progress_dir:
                progress = pathlib.Path(args.progress_dir)
                progress.mkdir(parents=True, exist_ok=True)
                count = args.total if args.write is None else args.write
                for index in range(count):
                    (progress / f"case-{index}.done").write_text("done\\n", encoding="utf-8")
            sys.exit(args.exit_code)
            """
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    return checkout, commit


def make_manifest(root, fake_checkout, campaign_id="example-campaign", **overrides):
    checkout, commit = fake_checkout
    progress_dir = root / "progress" / campaign_id
    manifest = {
        "id": campaign_id,
        "title": "Example campaign",
        "repo_dir": str(checkout),
        "ref": commit,
        "driver": [
            sys.executable,
            str(checkout / "drivers" / "driver.py"),
            "--progress-dir",
            str(progress_dir),
            "--total",
            "2",
        ],
        "cwd": str(checkout),
        "env": {},
        "expected_hours": 1,
        "max_hours": 2,
        "progress": {"glob": str(progress_dir / "*.done"), "total": 2},
        "licence_exit_codes": [12],
        "retry": {"max_attempts": 2, "backoff_minutes": 1, "licence_tries_per_day": 2},
        "priority": 10,
        "after": [],
    }
    manifest.update(overrides)
    path = root / "approved" / f"{campaign_id}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    return path, manifest


def git_run(repo, *args):
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "placeholder",
            "GIT_AUTHOR_EMAIL": "placeholder",
            "GIT_COMMITTER_NAME": "placeholder",
            "GIT_COMMITTER_EMAIL": "placeholder",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    return subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False, env=env)


@pytest.fixture()
def git_checkout(work_area):
    checkout = work_area / "git-checkout"
    checkout.mkdir()
    assert subprocess.run(["git", "init", str(checkout)], text=True, capture_output=True, check=False).returncode == 0
    (checkout / "drivers").mkdir()
    (checkout / "drivers" / "driver.py").write_text("print('ok')\n", encoding="utf-8")
    assert git_run(checkout, "add", "drivers/driver.py").returncode == 0
    assert git_run(checkout, "commit", "-m", "initial").returncode == 0
    commit = git_run(checkout, "rev-parse", "HEAD").stdout.strip()
    assert git_run(checkout, "remote", "add", "origin", "placeholder://repo").returncode == 0
    assert git_run(checkout, "update-ref", "refs/remotes/origin/main", commit).returncode == 0
    (checkout / ".git" / "refs" / "remotes" / "origin" / "HEAD").write_text("ref: refs/remotes/origin/main\n", encoding="utf-8")
    return checkout, commit


def make_policy_manifest(root, git_checkout, **overrides):
    checkout, commit = git_checkout
    manifest = {
        "id": "policy-example",
        "title": "Policy Example",
        "repo_dir": str(checkout),
        "ref": commit,
        "driver": [sys.executable, "drivers/driver.py"],
        "driver_file": "drivers/driver.py",
        "cwd": str(checkout),
        "env": {},
        "expected_hours": 1,
        "max_hours": 1,
        "workers": 1,
        "licence_exit_codes": [12],
        "retry": {"max_attempts": 1, "backoff_minutes": 0},
        "priority": 1,
        "after": [],
    }
    manifest.update(overrides)
    (root / "requested").mkdir(exist_ok=True)
    path = root / "requested" / f"{manifest['id']}.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path, manifest


def write_policy(root, **limits):
    data = {
        "repositories": ["placeholder://repo"],
        "interpreters": [sys.executable],
        "limits": {"id_prefixes": ["policy-"], "max_workers": 2, "max_hours": 2},
    }
    data["limits"].update(limits)
    (root / "policy.json").write_text(json.dumps(data), encoding="utf-8")


def approve(root, path, approval_ref="approval-ref-001", date="2026-10-13"):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    campaign_id = path.stem
    current = root / "approvals.tsv"
    with current.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{campaign_id}\t{digest}\t{approval_ref}\t{date}\n")
    return digest


def run_cli(args, root):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(RUNNER_PATH), *args, "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
        env=env,
        creationflags=RUNNER_CREATION_FLAGS,
    )


def popen_runner(args, root):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.Popen(
        [sys.executable, str(RUNNER_PATH), *args, "--root", str(root)],
        env=env,
        creationflags=RUNNER_CREATION_FLAGS,
    )


def test_j1_happy_path_records_done(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout)
    approve(root, path)
    done = run_cli(["run-once"], root)
    assert done.returncode == 0, done.stderr
    result = (root / "done" / "example-campaign.result").read_text(encoding="utf-8")
    assert result.splitlines()[0].startswith("DONE\t")
    assert "\t2\t2" in result.splitlines()[0]


def test_j2_digest_not_listed_is_refused(root, fake_checkout):
    make_manifest(root, fake_checkout)
    done = run_cli(["run-once"], root)
    assert done.returncode == 0
    assert not (root / "done" / "example-campaign.result").exists()
    assert "unapproved" in run_cli(["status"], root).stdout


def test_j3_digest_mismatch_is_refused(root, fake_checkout):
    path, manifest = make_manifest(root, fake_checkout)
    approve(root, path)
    manifest["title"] = "Changed"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert run_cli(["run-once"], root).returncode == 0
    assert "digest-mismatch" in run_cli(["status"], root).stdout


def test_j4_overlapping_calls_start_only_one_driver(root, fake_checkout, work_area):
    record = work_area / "driver-record.json"
    path, manifest = make_manifest(
        root,
        fake_checkout,
        driver=[
            sys.executable,
            str(fake_checkout[0] / "drivers" / "driver.py"),
            "--sleep",
            "1",
            "--record",
            str(record),
        ],
        progress=None,
    )
    approve(root, path)
    first = popen_runner(["run-once"], root)
    time.sleep(0.2)
    second = run_cli(["run-once"], root)
    first.wait(timeout=10)
    assert second.returncode == 0
    log = (root / "state" / "global" / "runner.log").read_text(encoding="utf-8")
    assert "operating-system lock" in log
    assert json.loads(record.read_text(encoding="utf-8")) == manifest["driver"][1:]


def test_j5_stale_lock_resumes_and_counts_attempt(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout)
    approve(root, path)
    (root / "runner.lock").write_text(json.dumps({"pid": 999999, "boot_time": "old"}), encoding="utf-8")
    done = run_cli(["run-once"], root)
    assert done.returncode == 0
    assert (root / "state" / "example-campaign" / "attempts.txt").read_text(encoding="utf-8").strip() == "1"


def test_j6_licence_exit_is_held_then_retried_without_attempt_use(root, fake_checkout):
    path, manifest = make_manifest(
        root,
        fake_checkout,
        driver=[sys.executable, str(fake_checkout[0] / "drivers" / "driver.py"), "--exit-code", "12"],
        progress=None,
    )
    approve(root, path)
    assert run_cli(["run-once", "--backoff-minutes", "0"], root).returncode == 0
    assert (root / "state" / "example-campaign" / "attempts.txt").read_text(encoding="utf-8").strip() == "0"
    result = (root / "done" / "example-campaign.result").read_text(encoding="utf-8")
    assert result.startswith("HELD\t")
    assert "licence-unavailable" in result
    manifest["driver"] = [sys.executable, str(fake_checkout[0] / "drivers" / "driver.py")]
    path.write_text(json.dumps(manifest), encoding="utf-8")
    approve(root, path)
    assert run_cli(["run-once"], root).returncode == 0
    assert (root / "done" / "example-campaign.result").read_text(encoding="utf-8").startswith("DONE\t")


def test_j7_other_failure_retries_then_failed(root, fake_checkout):
    path, _ = make_manifest(
        root,
        fake_checkout,
        driver=[sys.executable, str(fake_checkout[0] / "drivers" / "driver.py"), "--exit-code", "9"],
        progress=None,
        retry={"max_attempts": 1, "backoff_minutes": 0, "licence_tries_per_day": 2},
    )
    approve(root, path)
    assert run_cli(["run-once"], root).returncode == 0
    assert "FAILED" in (root / "done" / "example-campaign.result").read_text(encoding="utf-8")


def test_j8_stop_file_stops_and_blocks_restart(root, fake_checkout):
    path, _ = make_manifest(
        root,
        fake_checkout,
        driver=[sys.executable, str(fake_checkout[0] / "drivers" / "driver.py"), "--sleep", "5"],
        progress=None,
    )
    approve(root, path)
    (root / "state" / "example-campaign").mkdir(parents=True)
    (root / "state" / "example-campaign" / "STOP").write_text("", encoding="utf-8")
    assert run_cli(["run-once", "--heartbeat-seconds", "0.1"], root).returncode == 0
    assert not (root / "done" / "example-campaign.result").exists()
    (root / "state" / "example-campaign" / "STOP").unlink()
    process = popen_runner(["run-once", "--heartbeat-seconds", "0.1", "--stop-grace-seconds", "1"], root)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not (root / "state" / "example-campaign" / "driver.json").exists():
        time.sleep(0.05)
    assert (root / "state" / "example-campaign" / "driver.json").exists()
    (root / "state" / "example-campaign" / "STOP").write_text("", encoding="utf-8")
    process.wait(timeout=10)
    assert "STOPPED" in (root / "done" / "example-campaign.result").read_text(encoding="utf-8")


def test_j9_max_hours_reached_holds(root, fake_checkout):
    path, _ = make_manifest(
        root,
        fake_checkout,
        driver=[sys.executable, str(fake_checkout[0] / "drivers" / "driver.py"), "--sleep", "5"],
        progress=None,
        max_hours=0.00005,
        expected_hours=0.00001,
    )
    approve(root, path)
    assert run_cli(["run-once", "--heartbeat-seconds", "0.1"], root).returncode == 0
    result = (root / "done" / "example-campaign.result").read_text(encoding="utf-8")
    assert result.startswith("HELD\t")
    assert "max-hours" in result


def test_j10_after_ordering(root, fake_checkout):
    first_path, _ = make_manifest(root, fake_checkout, "first", priority=5)
    second_path, _ = make_manifest(root, fake_checkout, "second", priority=1, after=["first"])
    approve(root, first_path)
    approve(root, second_path)
    assert run_cli(["run-once"], root).returncode == 0
    assert (root / "done" / "first.result").exists()
    assert not (root / "done" / "second.result").exists()


def test_j11_ref_mismatch_records_reason(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout, ref="b" * 40)
    approve(root, path)
    assert run_cli(["run-once"], root).returncode == 0
    log = (root / "state" / "example-campaign" / "runner.log").read_text(encoding="utf-8")
    assert "checkout HEAD mismatch" in log


def test_j12_heartbeat_and_status_format(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout)
    approve(root, path)
    assert run_cli(["run-once"], root).returncode == 0
    heartbeat = root / "state" / "example-campaign" / "heartbeat.json"
    assert heartbeat.exists()
    status_lines = run_cli(["status"], root).stdout.strip().splitlines()
    assert status_lines[0] == "task-mode\tunknown"
    parts = status_lines[1].split("\t")
    assert parts[0] == "example-campaign"
    assert parts[1] == "DONE"
    assert parts[2:4] == ["2", "2"]
    assert len(parts) == 5


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (lambda m: m.pop("id"), "missing field: id"),
        (lambda m: m.__setitem__("extra", True), "unknown field: extra"),
        (lambda m: m.__setitem__("id", "bad/id"), "id must be a short safe token"),
        (lambda m: m.__setitem__("ref", "main"), "ref must be a full commit id"),
        (lambda m: m.__setitem__("repo_dir", "relative"), "repo_dir must be absolute"),
        (lambda m: m.__setitem__("after", [m["id"]]), "after must not include the campaign id"),
        (lambda m: m.__setitem__("max_hours", 0), "max_hours must be positive"),
        (lambda m: m.__setitem__("max_hours", 0.5), "max_hours must be greater than or equal to expected_hours"),
    ],
)
def test_j13_validate_names_each_manifest_error(root, fake_checkout, mutate, expected):
    path, manifest = make_manifest(root, fake_checkout)
    mutate(manifest)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    done = run_cli(["validate", str(path)], root)
    assert done.returncode != 0
    assert expected in done.stdout


def test_j13_validate_reports_several_errors(root, fake_checkout):
    path, manifest = make_manifest(root, fake_checkout)
    manifest.pop("title")
    manifest["extra"] = True
    manifest["repo_dir"] = "relative"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    done = run_cli(["validate", str(path)], root)
    assert done.returncode != 0
    assert "missing field: title" in done.stdout
    assert "unknown field: extra" in done.stdout
    assert "repo_dir must be absolute" in done.stdout


def test_j14_credential_like_env_name_is_refused(root, fake_checkout):
    path, manifest = make_manifest(root, fake_checkout, env={"API_TOKEN": "placeholder"})
    done = run_cli(["validate", str(path)], root)
    assert done.returncode != 0
    assert "env name looks like a credential" in done.stdout


def test_j14_credential_tokens_are_separator_based(root, fake_checkout):
    path, manifest = make_manifest(root, fake_checkout, env={"MONKEY_COUNT": "1"})
    assert run_cli(["validate", str(path)], root).returncode == 0
    manifest["env"] = {"db_pass": "placeholder"}
    path.write_text(json.dumps(manifest), encoding="utf-8")
    done = run_cli(["validate", str(path)], root)
    assert done.returncode != 0
    assert "env name looks like a credential" in done.stdout


def test_windows_liveness_probe_does_not_call_os_kill(monkeypatch, runner):
    calls = []
    monkeypatch.setattr(runner.os, "name", "nt", raising=False)
    monkeypatch.setattr(runner.os, "kill", lambda *args: calls.append(args))
    monkeypatch.setattr(runner, "_windows_process_creation_time", lambda pid: 123.0)
    assert runner.process_alive(44, 123.0)
    assert not runner.process_alive(44, 124.0)
    assert calls == []


def test_live_and_ended_process_identity(runner):
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(2)"])
    try:
        identity = runner.process_identity(process.pid)
        assert identity is not None
        assert runner.process_alive(identity["pid"], identity["creation_time"])
    finally:
        process.terminate()
        process.wait(timeout=5)
    assert not runner.process_alive(identity["pid"], identity["creation_time"])


def test_approvals_accept_bom_and_strip_carriage_return(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / "approvals.tsv").write_bytes(f"\ufeffexample-campaign\t{digest}\tapproval-ref\t2026-10-13\r\n".encode("utf-8"))
    assert run_cli(["run-once"], root).returncode == 0
    assert (root / "done" / "example-campaign.result").exists()


def test_requested_manifest_without_policy_does_not_run_or_call_git(root, git_checkout, monkeypatch, runner):
    make_policy_manifest(root, git_checkout)
    approvals = root / "approvals.tsv"
    before = approvals.read_bytes() if approvals.exists() else b""
    calls = []
    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs: calls.append(args) or subprocess.CompletedProcess(args, 1))
    campaigns, errors = runner.discover_campaigns(root)
    assert errors == []
    assert campaigns == []
    assert calls == []
    assert (approvals.read_bytes() if approvals.exists() else b"") == before


def test_status_is_read_only_for_requested_manifest(root, git_checkout, monkeypatch, runner):
    make_policy_manifest(root, git_checkout)
    write_policy(root)
    calls = []
    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs: calls.append(args) or subprocess.CompletedProcess(args, 1))
    lines = runner.status_lines(root)
    assert any(line.startswith("policy-example\trequested\t") for line in lines)
    assert calls == []
    assert not (root / "approvals.tsv").exists()


def test_policy_approves_requested_manifest(root, git_checkout):
    path, _ = make_policy_manifest(root, git_checkout)
    write_policy(root)
    assert run_cli(["run-once"], root).returncode == 0
    approvals = (root / "approvals.tsv").read_text(encoding="utf-8")
    assert f"policy-example\t{hashlib.sha256(path.read_bytes()).hexdigest()}\tpolicy\t" in approvals
    assert (root / "done" / "policy-example.result").exists()


def test_policy_removed_after_approval_refuses_retry(root, git_checkout):
    path, manifest = make_policy_manifest(
        root,
        git_checkout,
        driver=[sys.executable, "drivers/driver.py"],
        retry={"max_attempts": 2, "backoff_minutes": 0},
    )
    (git_checkout[0] / "drivers" / "driver.py").write_text("import sys\nsys.exit(9)\n", encoding="utf-8")
    git_run(git_checkout[0], "add", "drivers/driver.py")
    git_run(git_checkout[0], "commit", "-m", "failing driver")
    commit = git_run(git_checkout[0], "rev-parse", "HEAD").stdout.strip()
    git_run(git_checkout[0], "update-ref", "refs/remotes/origin/main", commit)
    manifest["ref"] = commit
    path.write_text(json.dumps(manifest), encoding="utf-8")
    write_policy(root)
    assert run_cli(["run-once", "--backoff-minutes", "0"], root).returncode == 0
    assert (root / "done" / "policy-example.result").read_text(encoding="utf-8").startswith("HELD\t")
    (root / "policy.json").unlink()
    (root / "done" / "policy-example.result").unlink()
    assert run_cli(["run-once"], root).returncode == 0
    log = (root / "state" / "policy-example" / "runner.log").read_text(encoding="utf-8")
    assert "policy.json is not valid at start time" in log


def test_policy_rechecks_checkout_before_retry(root, git_checkout):
    path, manifest = make_policy_manifest(root, git_checkout, driver=[sys.executable, "drivers/driver.py"])
    (git_checkout[0] / "drivers" / "driver.py").write_text("import sys\nsys.exit(9)\n", encoding="utf-8")
    git_run(git_checkout[0], "add", "drivers/driver.py")
    git_run(git_checkout[0], "commit", "-m", "failing driver")
    commit = git_run(git_checkout[0], "rev-parse", "HEAD").stdout.strip()
    git_run(git_checkout[0], "update-ref", "refs/remotes/origin/main", commit)
    manifest["ref"] = commit
    path.write_text(json.dumps(manifest), encoding="utf-8")
    write_policy(root)
    assert run_cli(["run-once", "--backoff-minutes", "0"], root).returncode == 0
    (root / "done" / "policy-example.result").unlink()
    (git_checkout[0] / "drivers" / "driver.py").write_text("print('changed')\n", encoding="utf-8")
    assert run_cli(["run-once"], root).returncode == 0
    log = (root / "state" / "policy-example" / "runner.log").read_text(encoding="utf-8")
    assert "policy unapproved" in log
    assert "tracked files differ from ref" in log


def test_policy_refuses_driver_code_option_and_loading_env(root, git_checkout):
    path, manifest = make_policy_manifest(root, git_checkout, driver=[sys.executable, "-c", "print('outside')", "drivers/driver.py"])
    write_policy(root)
    assert run_cli(["run-once"], root).returncode == 0
    logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
    assert "driver must execute driver_file directly" in logs
    manifest["driver"] = [sys.executable, "drivers/driver.py"]
    manifest["env"] = {"PYTHONPATH": "placeholder"}
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert run_cli(["run-once"], root).returncode == 0
    logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
    assert "env name changes program loading: PYTHONPATH" in logs


def test_policy_refuses_index_flags_and_untracked_loadable_files(root, git_checkout):
    path, _ = make_policy_manifest(root, git_checkout)
    write_policy(root)
    assert git_run(git_checkout[0], "update-index", "--skip-worktree", "drivers/driver.py").returncode == 0
    (git_checkout[0] / "drivers" / "driver.py").write_text("print('changed')\n", encoding="utf-8")
    assert run_cli(["run-once"], root).returncode == 0
    logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
    assert "skip-worktree or assume-unchanged" in logs
    assert git_run(git_checkout[0], "update-index", "--no-skip-worktree", "drivers/driver.py").returncode == 0
    original = git_run(git_checkout[0], "show", "HEAD:drivers/driver.py")
    assert original.returncode == 0
    (git_checkout[0] / "drivers" / "driver.py").write_text(original.stdout, encoding="utf-8")
    (git_checkout[0] / "drivers" / "helper.py").write_text("print('helper')\n", encoding="utf-8")
    (root / "approvals.tsv").unlink(missing_ok=True)
    assert run_cli(["run-once"], root).returncode == 0
    logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
    assert "untracked loadable file is present" in logs


def test_policy_type_checks_and_refuses_linked_policy(root, git_checkout):
    make_policy_manifest(root, git_checkout)
    write_policy(root, id_prefixes=[""])
    assert run_cli(["run-once"], root).returncode == 0
    logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
    assert "non-empty id_prefixes" in logs
    (root / "policy.json").write_text(json.dumps({"repositories": ["placeholder://repo"], "limits": {"id_pattern": 1, "max_workers": True, "max_hours": 1}}), encoding="utf-8")
    assert run_cli(["run-once"], root).returncode == 0
    logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
    assert "policy id_pattern must be a string" in logs
    if hasattr(os, "symlink"):
        (root / "policy.json").unlink()
        target = root / "policy-target.json"
        target.write_text(json.dumps({"repositories": ["placeholder://repo"], "interpreters": [sys.executable], "limits": {"id_prefixes": ["policy-"], "max_workers": 2, "max_hours": 2}}), encoding="utf-8")
        try:
            os.symlink(target, root / "policy.json")
        except OSError:
            pytest.skip("symbolic links are not available on this platform")
        assert run_cli(["run-once"], root).returncode == 0
        logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
        assert "policy.json must not be a symbolic link" in logs


@pytest.mark.parametrize(
    "mutate, message",
    [
        (lambda root, checkout, manifest: (root / "policy.json").write_text("{", encoding="utf-8"), "policy.json is invalid JSON"),
        (lambda root, checkout, manifest: manifest.__setitem__("workers", 3), "workers exceeds policy limit"),
        (lambda root, checkout, manifest: manifest.__setitem__("max_hours", 3), "max_hours exceeds policy limit"),
        (lambda root, checkout, manifest: manifest.__setitem__("id", "other-example"), "id is outside policy limit"),
        (lambda root, checkout, manifest: (checkout / "drivers" / "driver.py").write_text("changed\n", encoding="utf-8"), "tracked files differ from ref"),
    ],
)
def test_policy_negative_controls(root, git_checkout, mutate, message):
    path, manifest = make_policy_manifest(root, git_checkout)
    write_policy(root)
    mutate(root, git_checkout[0], manifest)
    path.unlink()
    path = root / "requested" / f"{manifest['id']}.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    before = (root / "approvals.tsv").read_bytes() if (root / "approvals.tsv").exists() else b""
    assert run_cli(["run-once"], root).returncode == 0
    after = (root / "approvals.tsv").read_bytes() if (root / "approvals.tsv").exists() else b""
    assert after == before
    logs = "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))
    assert message in logs


def test_invalid_manifest_id_logs_only_in_invalid_bucket(root, fake_checkout, work_area):
    outside = work_area / "outside"
    outside.mkdir()
    before = sorted(p.relative_to(work_area).as_posix() for p in work_area.rglob("*"))
    path, manifest = make_manifest(root, fake_checkout)
    path.unlink()
    bad = root / "approved" / "bad.json"
    manifest["id"] = "../outside/dotdot"
    bad.write_text(json.dumps(manifest), encoding="utf-8")
    run_cli(["run-once"], root)
    after = sorted(p.relative_to(work_area).as_posix() for p in work_area.rglob("*"))
    assert all(not item.startswith("outside/") for item in set(after) - set(before))
    assert (root / "state" / "invalid" / "runner.log").exists()


@pytest.mark.parametrize("bad_id", [".", ".."])
def test_dot_manifest_ids_are_refused(root, fake_checkout, bad_id):
    path, manifest = make_manifest(root, fake_checkout)
    path.unlink()
    manifest["id"] = bad_id
    bad = root / "approved" / f"{bad_id}.json"
    bad.write_text(json.dumps(manifest), encoding="utf-8")
    approve(root, bad)
    assert run_cli(["run-once"], root).returncode == 0
    log = (root / "state" / "invalid" / "runner.log").read_text(encoding="utf-8")
    assert "id must be a short safe token" in log


def test_case_folded_duplicate_ids_are_refused(root, fake_checkout):
    first, _ = make_manifest(root, fake_checkout, "POL-A")
    requested = root / "requested"
    requested.mkdir()
    _, manifest = make_manifest(root, fake_checkout, "placeholder")
    (root / "approved" / "placeholder.json").unlink()
    manifest["id"] = "pol-a"
    second = requested / "pol-a.json"
    second.write_text(json.dumps(manifest), encoding="utf-8")
    approve(root, first)
    approve(root, second, approval_ref="policy")
    runner = load_runner()
    campaigns, errors = runner.discover_campaigns(root)
    assert errors == []
    assert any("campaign id differs only by case" in "; ".join(item["errors"]) for item in campaigns)


def test_low_disk_threshold_skips_campaign(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout)
    approve(root, path)
    assert run_cli(["run-once", "--min-free-bytes", str(10**18)], root).returncode == 0
    assert not (root / "done" / "example-campaign.result").exists()


def test_j15_k1_standard_library_imports_and_no_network_modules():
    tree = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"))
    blocked = {"socket", "ssl", "urllib", "http", "ftplib", "imaplib", "smtplib"}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not (imports & blocked)
    stdlib = set(sys.stdlib_module_names) | {"__future__"}
    assert imports <= stdlib


def test_j15_k2_runs_only_declared_driver(root, fake_checkout, work_area):
    record = work_area / "argv.json"
    path, manifest = make_manifest(
        root,
        fake_checkout,
        driver=[sys.executable, str(fake_checkout[0] / "drivers" / "driver.py"), "--record", str(record)],
        progress=None,
    )
    approve(root, path)
    assert run_cli(["run-once"], root).returncode == 0
    assert json.loads(record.read_text(encoding="utf-8")) == manifest["driver"][1:]


def test_j15_k3_stop_does_not_end_bystander(root, fake_checkout):
    bystander = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(5)"])
    try:
        path, _ = make_manifest(
            root,
            fake_checkout,
            driver=[sys.executable, str(fake_checkout[0] / "drivers" / "driver.py"), "--sleep", "5"],
            progress=None,
        )
        approve(root, path)
        process = popen_runner(["run-once", "--heartbeat-seconds", "0.1"], root)
        time.sleep(0.3)
        (root / "STOP").write_text("", encoding="utf-8")
        process.wait(timeout=10)
        assert bystander.poll() is None
    finally:
        bystander.terminate()
        bystander.wait(timeout=5)


def test_j15_k4_fake_checkout_unchanged(root, fake_checkout):
    checkout = fake_checkout[0]
    before = snapshot(checkout)
    path, _ = make_manifest(root, fake_checkout)
    approve(root, path)
    assert run_cli(["run-once"], root).returncode == 0
    assert snapshot(checkout) == before


def test_j15_k5_no_publish_surface_is_covered_by_imports_and_processes(root, fake_checkout, work_area):
    test_j15_k1_standard_library_imports_and_no_network_modules()
    test_j15_k2_runs_only_declared_driver(root, fake_checkout, work_area)


def test_j15_k6_unapproved_never_runs_and_approvals_unchanged(root, fake_checkout):
    make_manifest(root, fake_checkout)
    approvals = root / "approvals.tsv"
    approvals.write_text("bad\tline\n", encoding="utf-8")
    before = approvals.read_bytes()
    assert run_cli(["run-once"], root).returncode == 0
    assert approvals.read_bytes() == before


def test_j16_batch_wrapper_empty_root_passes_exit_code(work_area):
    if os.name != "nt":
        pytest.skip("run-solver-campaigns.bat is not applicable on this platform")
    root = work_area / "empty-root"
    root.mkdir()
    done = subprocess.run(
        ["cmd.exe", "/c", str(WRAPPER_PATH)],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "SOLVER_CAMPAIGN_ROOT": str(root), "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert done.returncode == 0, done.stderr + done.stdout


def snapshot(path):
    items = {}
    for entry in sorted(path.rglob("*")):
        rel = entry.relative_to(path).as_posix()
        if entry.is_file():
            data = entry.read_bytes()
            items[rel] = (len(data), hashlib.sha256(data).hexdigest())
        elif entry.is_dir():
            items[rel] = "dir"
    return items


def task_xml(mode):
    done = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "task-definition",
            mode,
            "--account",
            "{ACCOUNT}",
            "--wrapper",
            "{WRAPPER}",
            "--campaign-root",
            "{CAMPAIGN_ROOT}",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return ET.fromstring(done.stdout.split("\n", 1)[1])


def task_xml_bytes(mode, output):
    done = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "task-definition",
            mode,
            "--account",
            "{ACCOUNT}",
            "--wrapper",
            "{WRAPPER}",
            "--campaign-root",
            "{CAMPAIGN_ROOT}",
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return output.read_bytes()


def find_text(element, name):
    found = element.find(f".//{{http://schemas.microsoft.com/windows/2004/02/mit/task}}{name}")
    return found.text if found is not None else None


@pytest.mark.parametrize(
    "mode,logon,trigger",
    [
        ("batch", "S4U", "BootTrigger"),
        ("batch-password", "Password", "BootTrigger"),
        ("desktop", "InteractiveToken", "LogonTrigger"),
    ],
)
def test_task_definition_modes(mode, logon, trigger):
    root = task_xml(mode)
    assert find_text(root, "LogonType") == logon
    assert find_text(root, "UserId") == "{ACCOUNT}"
    assert root.find(f".//{{http://schemas.microsoft.com/windows/2004/02/mit/task}}{trigger}") is not None
    assert find_text(root, "Interval") == "PT10M"
    assert find_text(root, "ExecutionTimeLimit") == "PT0S"
    assert find_text(root, "MultipleInstancesPolicy") == "IgnoreNew"
    assert find_text(root, "DisallowStartIfOnBatteries") == "false"
    assert find_text(root, "RunOnlyIfIdle") == "false"
    assert find_text(root, "RunLevel") == "LeastPrivilege"
    assert find_text(root, "Command") == "cmd.exe"
    assert find_text(root, "Priority") == "5"
    if mode == "desktop":
        trigger_user = root.find(".//{http://schemas.microsoft.com/windows/2004/02/mit/task}LogonTrigger/{http://schemas.microsoft.com/windows/2004/02/mit/task}UserId")
        assert trigger_user is not None
        assert trigger_user.text == "{ACCOUNT}"
    assert "Password" not in "".join(root.itertext()) or mode == "batch-password"


def test_task_definition_output_is_utf16_with_declaration(work_area):
    output = work_area / "task.xml"
    raw = task_xml_bytes("batch", output)
    assert raw.startswith(b"\xff\xfe")
    decoded = raw.decode("utf-16")
    assert decoded.startswith('<?xml version="1.0" encoding="UTF-16"?>')
    assert ET.fromstring(decoded.split("\n", 1)[1]).tag.endswith("Task")


def test_status_task_mode_records(root):
    assert run_cli(["status"], root).stdout.splitlines()[0] == "task-mode\tunknown"
    for mode in ("batch", "batch-password", "desktop"):
        (root / "task-mode.txt").write_text(mode + "\n", encoding="utf-8")
        assert run_cli(["status"], root).stdout.splitlines()[0] == f"task-mode\t{mode}"


def test_wrapper_fallback_uses_runtime_errorlevel_check():
    text = WRAPPER_PATH.read_text(encoding="utf-8")
    assert "if not errorlevel 1 set \"PYTHON_CMD=python.exe\"" in text
    assert "if %ERRORLEVEL% EQU 0 set \"PYTHON_CMD=python.exe\"" not in text


def test_register_dry_run_exits_before_scheduled_task_command():
    text = (REPO_ROOT / "scripts" / "operations" / "solver-campaign" / "register-solver-campaign-task.bat").read_text(
        encoding="utf-8"
    )
    dry_run = text.split("if defined DRY_RUN", 1)[1].split(")", 1)[0]
    assert "exit /b 0" in dry_run
    assert "schtasks" not in dry_run.lower()
    assert "--output" in text
    assert '/RU "%ACCOUNT%" /F' not in text
    assert "Registered task logon type did not match requested mode." in text
