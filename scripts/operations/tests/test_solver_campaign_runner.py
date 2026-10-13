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
import uuid
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = REPO_ROOT / "scripts" / "operations" / "solver-campaign" / "campaign_runner.py"
WRAPPER_PATH = REPO_ROOT / "scripts" / "operations" / "solver-campaign" / "run-solver-campaigns.bat"


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
    first = subprocess.Popen([sys.executable, str(RUNNER_PATH), "run-once", "--root", str(root)])
    time.sleep(0.2)
    second = run_cli(["run-once"], root)
    first.wait(timeout=10)
    assert second.returncode == 0
    log = (root / "state" / "global" / "runner.log").read_text(encoding="utf-8")
    assert "lock holder" in log
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
    process = subprocess.Popen([sys.executable, str(RUNNER_PATH), "run-once", "--root", str(root), "--heartbeat-seconds", "0.1"])
    time.sleep(0.3)
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
    status = run_cli(["status"], root).stdout.strip()
    parts = status.split("\t")
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
        process = subprocess.Popen([sys.executable, str(RUNNER_PATH), "run-once", "--root", str(root), "--heartbeat-seconds", "0.1"])
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
