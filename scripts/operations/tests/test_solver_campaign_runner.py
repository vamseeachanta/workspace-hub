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



def make_requested_manifest(root, fake_checkout, campaign_id="requested-campaign", **overrides):
    path, manifest = make_manifest(root, fake_checkout, campaign_id, **overrides)
    path.unlink()
    requested = root / "requested"
    requested.mkdir(exist_ok=True)
    target = requested / path.name
    target.write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    return target, manifest


def all_runner_logs(root):
    return "\n".join(p.read_text(encoding="utf-8") for p in (root / "state").glob("*/runner.log"))


def test_requested_manifest_policy_file_and_stale_policy_line_do_not_authorize(root, fake_checkout):
    requested_path, _ = make_requested_manifest(root, fake_checkout)
    approved_path, _ = make_manifest(root, fake_checkout, "person-approved", priority=5)
    approve(root, requested_path, approval_ref="policy")
    before = (root / "approvals.tsv").read_bytes()
    approve(root, approved_path)
    after_person_approval = (root / "approvals.tsv").read_bytes()
    (root / "policy.json").write_text('{"standing": true}\n', encoding="utf-8")

    assert run_cli(["run-once"], root).returncode == 0

    assert (root / "done" / "person-approved.result").exists()
    assert not (root / "done" / "requested-campaign.result").exists()
    assert (root / "approvals.tsv").read_bytes() == after_person_approval
    assert before in after_person_approval
    log = (root / "state" / "global" / "runner.log").read_text(encoding="utf-8")
    assert log.count("standing approval is not available in this release") == 1


def test_status_ignores_requested_folder(root, fake_checkout):
    make_requested_manifest(root, fake_checkout)
    lines = run_cli(["status"], root).stdout.splitlines()
    assert all("requested-campaign" not in line for line in lines)


def test_policy_approval_reference_on_approved_manifest_does_not_authorize(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout)
    approve(root, path, approval_ref="policy")
    assert run_cli(["run-once"], root).returncode == 0
    assert not (root / "done" / "example-campaign.result").exists()
    log = (root / "state" / "example-campaign" / "runner.log").read_text(encoding="utf-8")
    assert "approval reference policy is not available in this release" in log


def test_status_shows_policy_reference_as_unapproved(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout)
    approve(root, path, approval_ref="policy")

    lines = run_cli(["status"], root).stdout.splitlines()

    assert any(line.startswith("example-campaign\tunapproved\t") for line in lines)
    assert not any(line.startswith("example-campaign\tdigest-mismatch\t") for line in lines)


def test_runner_static_release_has_no_policy_execution_surface():
    source = RUNNER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"run", "Popen"} and node.args:
                first = node.args[0]
                if isinstance(first, ast.List) and first.elts and isinstance(first.elts[0], ast.Constant):
                    assert first.elts[0].value != "git"
    assert 'root / "requested"' not in source
    assert "append_policy_approval" not in source
    assert "run_git" not in source

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
    assert (root / "state" / "bad" / "runner.log").exists()


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


def test_case_folded_duplicate_ids_are_skipped_without_halting_root(root, fake_checkout, runner, monkeypatch):
    class FakeManifestPath:
        def __init__(self, name):
            self.name = name
            self.stem = name.rsplit(".", 1)[0]

        def __lt__(self, other):
            return self.name < other.name

        def __eq__(self, other):
            return isinstance(other, FakeManifestPath) and self.name == other.name

        def __hash__(self):
            return hash(self.name)

    upper = FakeManifestPath("POL-A.json")
    lower = FakeManifestPath("pol-a.json")
    good = FakeManifestPath("good-campaign.json")
    _, good_manifest = make_manifest(root, fake_checkout, "good-campaign", priority=3)
    digest_by_path = {
        upper: "1" * 64,
        lower: "2" * 64,
        good: "3" * 64,
    }

    manifests = {
        upper: {**good_manifest, "id": "POL-A", "priority": 1},
        lower: {**good_manifest, "id": "pol-a", "priority": 2},
        good: good_manifest,
    }

    def fake_load_manifest(path):
        return manifests[path], [], digest_by_path[path]

    def fake_sha256_file(path):
        if path in digest_by_path:
            return digest_by_path[path]
        return hashlib.sha256(path.read_bytes()).hexdigest()

    original_glob = Path.glob

    def fake_glob(path, pattern):
        if path == root / "approved" and pattern == "*.json":
            return iter([upper, lower, good])
        return original_glob(path, pattern)

    monkeypatch.setattr(runner, "load_manifest", fake_load_manifest)
    monkeypatch.setattr(runner, "sha256_file", fake_sha256_file)
    monkeypatch.setattr(Path, "glob", fake_glob)
    with (root / "approvals.tsv").open("w", encoding="utf-8", newline="\n") as stream:
        for campaign_id, path in (("POL-A", upper), ("pol-a", lower), ("good-campaign", good)):
            stream.write(f"{campaign_id}\t{digest_by_path[path]}\tapproval-ref\t2026-10-13\n")
    campaigns, approval_errors = runner.discover_campaigns(root)

    assert approval_errors == []
    by_id = {campaign["id"]: campaign for campaign in campaigns}
    assert by_id["good-campaign"]["approved"]
    assert not by_id["POL-A"]["approved"]
    assert not by_id["pol-a"]["approved"]
    assert any("campaign id differs only by case" in error for error in by_id["POL-A"]["errors"])
    assert any("campaign id differs only by case" in error for error in by_id["pol-a"]["errors"])



def test_malformed_manifest_is_skipped_without_halting_root(root, fake_checkout):
    bad = root / "approved" / "bad-campaign.json"
    bad.write_text("{\n", encoding="utf-8")
    good, _ = make_manifest(root, fake_checkout, "good-campaign")
    approve(root, good)

    assert run_cli(["run-once"], root).returncode == 0

    assert (root / "done" / "good-campaign.result").exists()
    log = (root / "state" / "bad-campaign" / "runner.log").read_text(encoding="utf-8")
    assert "invalid JSON" in log


@pytest.mark.parametrize("bad_payload", [{"title": "Missing id"}, {"id": 5, "title": "Non-string id"}])
def test_manifest_without_string_id_is_skipped_without_halting_root(root, fake_checkout, bad_payload):
    bad = root / "approved" / "bad-campaign.json"
    bad.write_text(json.dumps(bad_payload), encoding="utf-8")
    approve(root, bad)
    good, _ = make_manifest(root, fake_checkout, "good-campaign")
    approve(root, good)

    assert run_cli(["run-once"], root).returncode == 0

    assert (root / "done" / "good-campaign.result").exists()
    status = run_cli(["status"], root)
    assert status.returncode == 0, status.stderr
    assert "good-campaign\tDONE\t" in status.stdout
    assert "\tinvalid\t" in status.stdout


def test_invalid_mismatched_id_does_not_create_casefold_collision(root, fake_checkout):
    good, _ = make_manifest(root, fake_checkout, "good")
    approve(root, good)
    evil, manifest = make_manifest(root, fake_checkout, "evil", id="Good")
    approve(root, evil)

    status = run_cli(["status"], root)

    assert status.returncode == 0, status.stderr
    assert "good\tpending\t" in status.stdout
    assert "evil\tinvalid\t" in status.stdout
    assert "good\tinvalid\t" not in status.stdout
    done = run_cli(["run-once"], root)
    assert done.returncode == 0, done.stderr
    assert (root / "done" / "good.result").exists()
    assert not (root / "done" / "evil.result").exists()
    assert manifest["id"] == "Good"


@pytest.mark.parametrize("bad_id", ["something-else", "good"])
def test_invalid_mismatched_or_duplicate_id_does_not_disable_valid_campaign(root, fake_checkout, bad_id):
    good, _ = make_manifest(root, fake_checkout, "good")
    approve(root, good)
    bad, _ = make_manifest(root, fake_checkout, "bad", id=bad_id)
    approve(root, bad)

    status = run_cli(["status"], root)

    assert status.returncode == 0, status.stderr
    assert "good\tpending\t" in status.stdout
    assert "bad\tinvalid\t" in status.stdout
    assert "good\tinvalid\t" not in status.stdout


def test_valid_casefold_id_collision_is_reported(root, fake_checkout):
    if os.name == "nt":
        pytest.skip("casefold collision requires a case-sensitive approved directory")
    lower, _ = make_manifest(root, fake_checkout, "good")
    upper, _ = make_manifest(root, fake_checkout, "Good")
    approve(root, lower)
    approve(root, upper)

    status = run_cli(["status"], root)

    assert status.returncode == 0, status.stderr
    assert "good\tinvalid\t" in status.stdout
    assert "Good\tinvalid\t" in status.stdout


def test_start_failure_is_recorded_and_next_campaign_runs(root, fake_checkout):
    bad_cwd = fake_checkout[0] / "missing-cwd"
    bad, _ = make_manifest(root, fake_checkout, "bad-start", cwd=str(bad_cwd), priority=1)
    good, _ = make_manifest(root, fake_checkout, "good-campaign", priority=2)
    approve(root, bad)
    approve(root, good)

    assert run_cli(["run-once"], root).returncode == 0

    assert (root / "done" / "good-campaign.result").exists()
    bad_result = (root / "done" / "bad-start.result").read_text(encoding="utf-8")
    assert "driver-start-failed" in bad_result
    assert (root / "state" / "bad-start" / "attempts.txt").read_text(encoding="utf-8").strip() == "1"


def test_start_failure_uses_backoff_and_fails_at_max_attempts(root, fake_checkout):
    bad_cwd = fake_checkout[0] / "missing-cwd"
    bad, _ = make_manifest(
        root,
        fake_checkout,
        "bad-start",
        cwd=str(bad_cwd),
        retry={"max_attempts": 2, "backoff_minutes": 0, "licence_tries_per_day": 2},
    )
    approve(root, bad)

    assert run_cli(["run-once"], root).returncode == 0
    first = (root / "done" / "bad-start.result").read_text(encoding="utf-8")
    assert first.startswith("HELD\t")
    assert "driver-start-failed" in first
    assert "next-try:" in first
    assert run_cli(["run-once"], root).returncode == 0
    second = (root / "done" / "bad-start.result").read_text(encoding="utf-8")
    assert second.startswith("FAILED\t")
    assert "driver-start-failed" in second
    assert (root / "state" / "bad-start" / "attempts.txt").read_text(encoding="utf-8").strip() == "2"
    assert run_cli(["run-once"], root).returncode == 0
    assert (root / "state" / "bad-start" / "attempts.txt").read_text(encoding="utf-8").strip() == "2"


def test_validate_refuses_relative_driver_program_path(root, fake_checkout):
    path, _ = make_manifest(root, fake_checkout, driver=["drivers/driver.py"])
    done = run_cli(["validate", str(path)], root)
    assert done.returncode == 1
    assert "driver program path must be absolute or resolved from PATH" in done.stdout


def test_read_checkout_head_resolves_branch_ref_through_common_dir(work_area, runner):
    checkout = work_area / "linked-checkout"
    common = work_area / "common-git"
    gitdir = work_area / "linked-git"
    commit = "b" * 40
    checkout.mkdir()
    gitdir.mkdir()
    (common / "refs" / "heads").mkdir(parents=True)
    (checkout / ".git").write_text(f"gitdir: {gitdir.as_posix()}\n", encoding="utf-8")
    (gitdir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (gitdir / "commondir").write_text(common.as_posix() + "\n", encoding="utf-8")
    (common / "refs" / "heads" / "main").write_text(commit + "\n", encoding="utf-8")
    assert runner.read_checkout_head(checkout) == commit


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


def register_batch_text():
    return (REPO_ROOT / "scripts" / "operations" / "solver-campaign" / "register-solver-campaign-task.bat").read_text(
        encoding="utf-8"
    )


def register_parse_section():
    text = register_batch_text()
    return text.split("rem BEGIN_ARGUMENT_PARSE", 1)[1].split("rem END_ARGUMENT_PARSE", 1)[0]


def register_cleanup_section():
    text = register_batch_text()
    return text.rsplit(":cleanup_registration", 1)[1].split(":after_cleanup_registration", 1)[0]


def test_register_parse_section_cannot_reach_scheduled_task_commands():
    section = register_parse_section().lower()
    blocked = ["schtasks", "task-definition", "task-readback", " del ", " /delete", " /create"]
    for token in blocked:
        assert token not in section


def write_register_parse_probe(work_area):
    probe = work_area / "parse-probe.bat"
    body = "@echo off\r\nsetlocal\r\nset \"MODE=batch\"\r\nset \"MODE_SET=\"\r\nset \"ROOT=\"\r\nset \"DRY_RUN=\"\r\n"
    body += "rem BEGIN_ARGUMENT_PARSE" + register_parse_section() + "rem END_ARGUMENT_PARSE\r\n"
    tail = """
goto mode_ok
:missing_root
echo Campaign root must be an existing folder.
exit /b 2
:unsafe_root
echo Campaign root contains unsupported characters.
exit /b 2
:arg_error
echo Usage: register-solver-campaign-task.bat [batch^|batch-password^|desktop] root [--dry-run]
exit /b 2
:mode_ok
echo MODE=%MODE%
echo ROOT=%ROOT%
if defined DRY_RUN echo DRY_RUN=1
exit /b 0
"""
    body += textwrap.dedent(tail).lstrip().replace("\n", "\r\n")
    probe.write_text(body, encoding="utf-8", newline="")
    return probe


def write_register_argument_probe(work_area):
    probe = work_area / "argument-probe.bat"
    body = "@echo off\r\nsetlocal\r\nset \"MODE=batch\"\r\nset \"MODE_SET=\"\r\nset \"ROOT=\"\r\nset \"DRY_RUN=\"\r\n"
    body += "rem BEGIN_ARGUMENT_PARSE" + register_parse_section() + "rem END_ARGUMENT_PARSE\r\n"
    tail = """
goto mode_ok
:missing_root
echo Campaign root must be an existing folder.
exit /b 2
:unsafe_root
echo Campaign root contains unsupported characters.
exit /b 2
:arg_error
echo Usage: register-solver-campaign-task.bat [batch^|batch-password^|desktop] root [--dry-run]
exit /b 2
:mode_ok
if defined DRY_RUN (
  echo Resolved campaign root: %ROOT%
  exit /b 0
)
echo STANDIN_REACHED
exit /b 0
"""
    body += textwrap.dedent(tail).lstrip().replace("\n", "\r\n")
    lowered = body.lower()
    blocked = ["schtasks", " /delete", " /create"]
    for token in blocked:
        assert token not in lowered
    probe.write_text(body, encoding="utf-8", newline="")
    return probe


def write_register_cleanup_probe(work_area, delete_exit_code):
    section = register_cleanup_section()
    safe = section.replace('schtasks /Delete /TN "%TASK_NAME%" /F', f"cmd /c exit {delete_exit_code}")
    lowered = safe.lower()
    blocked = ["schtasks", " /delete", " /create"]
    for token in blocked:
        assert token not in lowered
    probe = work_area / f"cleanup-probe-{delete_exit_code}.bat"
    body = "@echo off\r\nsetlocal\r\nset \"TASK_NAME=solver-campaign-runner\"\r\n"
    body += ":cleanup_registration" + safe + ":after_cleanup_registration\r\nexit /b 0\r\n"
    probe.write_text(body, encoding="utf-8", newline="")
    return probe


def run_register_parse_probe(probe, *args, cwd=None):
    return subprocess.run(
        ["cmd.exe", "/c", str(probe), *args],
        text=True,
        capture_output=True,
        check=False,
        creationflags=RUNNER_CREATION_FLAGS,
        cwd=cwd,
    )


def run_register_probe(probe, *args):
    return subprocess.run(
        ["cmd.exe", "/c", str(probe), *args],
        text=True,
        capture_output=True,
        check=False,
        creationflags=RUNNER_CREATION_FLAGS,
    )


@pytest.mark.skipif(os.name != "nt", reason="batch parsing is Windows-specific")
@pytest.mark.parametrize(
    "mode",
    ["batch", "batch-password", "desktop"],
)
@pytest.mark.parametrize(
    "root_name",
    ["campaign root", "campaign root with spaces", "parent folder/campaign-root"],
)
@pytest.mark.parametrize(
    "form",
    [
        ("--dry-run", "{mode}", "{root}"),
        ("{mode}", "--dry-run", "{root}"),
        ("{mode}", "{root}", "--dry-run"),
    ],
)
def test_register_dry_run_option_accepts_roots_with_spaces(work_area, mode, root_name, form):
    root = work_area / root_name
    root.mkdir(parents=True)
    probe = write_register_parse_probe(work_area)
    expanded = [str(root) if item == "{root}" else mode if item == "{mode}" else item for item in form]
    done = run_register_parse_probe(probe, *expanded)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "DRY_RUN=1" in done.stdout
    assert f"ROOT={root.resolve()}" in done.stdout


@pytest.mark.skipif(os.name != "nt", reason="batch parsing is Windows-specific")
@pytest.mark.parametrize(
    "args",
    [
        ("batch", "--dry_run"),
        ("/?",),
        ("-n",),
        ("batch", "", "--dry-run"),
        ("",),
        tuple(),
        ("batch",),
        ("batch", "{missing}"),
        ("batch", "{file}"),
        ("batch", "desktop", "{root}"),
        ("batch", "{root}", "extra"),
    ],
)
def test_register_malformed_arguments_never_parse_as_real_registration(work_area, args):
    root = work_area / "campaign-root"
    root.mkdir()
    missing = work_area / "missing-root"
    existing_file = work_area / "not-a-root.txt"
    existing_file.write_text("not a folder\n", encoding="utf-8")
    probe = write_register_parse_probe(work_area)
    expanded = [
        str(root) if item == "{root}" else str(missing) if item == "{missing}" else str(existing_file) if item == "{file}" else item
        for item in args
    ]
    done = run_register_parse_probe(probe, *expanded)
    assert done.returncode != 0
    assert "DRY_RUN=1" not in done.stdout
    assert "MODE=" not in done.stdout


@pytest.mark.skipif(os.name != "nt", reason="batch parsing is Windows-specific")
@pytest.mark.parametrize("args", [(".",), ("relative-root",), ("batch", ".", "--dry-run"), ("desktop", "relative-root")])
def test_register_relative_roots_are_resolved_before_registration(work_area, args):
    relative_root = work_area / "relative-root"
    relative_root.mkdir()
    probe = write_register_parse_probe(work_area)
    done = run_register_parse_probe(probe, *args, cwd=work_area)
    expected = work_area if "." in args else relative_root
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"ROOT={expected.resolve()}" in done.stdout


@pytest.mark.skipif(os.name != "nt", reason="batch parsing is Windows-specific")
def test_register_absolute_root_remains_absolute(work_area):
    root = work_area / "campaign-root"
    root.mkdir()
    probe = write_register_parse_probe(work_area)
    done = run_register_parse_probe(probe, str(root))
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"ROOT={root.resolve()}" in done.stdout


@pytest.mark.skipif(os.name != "nt", reason="batch parsing is Windows-specific")
@pytest.mark.parametrize("mode", ["batch", "batch-password", "desktop"])
@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize(
    "root_name",
    [
        "Campaigns (2026)",
        "Campaigns ) 2026",
        "Campaigns & zz-not-a-command-4066",
        "Campaigns ^ 2026",
        "Campaigns % 2026",
        "Campaigns ! 2026",
    ],
)
def test_register_refuses_unsafe_root_characters_before_registration(work_area, mode, dry_run, root_name):
    root = work_area / root_name
    root.mkdir()
    probe = write_register_argument_probe(work_area)
    root_arg = str(root)
    if "^" in root_name:
        root_arg = root_arg.replace("^", "^^")
    args = [mode, root_arg]
    if dry_run:
        args.append("--dry-run")

    done = run_register_parse_probe(probe, *args)

    assert done.returncode != 0, done.stdout + done.stderr
    assert "Campaign root contains unsupported characters." in done.stdout
    assert "STANDIN_REACHED" not in done.stdout
    assert "zz-not-a-command-4066" not in done.stderr
    assert "not recognized as an internal or external command" not in done.stderr


def test_task_readback_parser_accepts_utf16_and_utf8(work_area):
    runner = load_runner()
    xml = runner.task_definition_xml("batch", "{ACCOUNT}", "{WRAPPER}", "{ROOT}")
    for encoding in ("utf-16", "utf-8"):
        path = work_area / f"readback-{encoding}.xml"
        path.write_text(xml, encoding=encoding)
        assert runner.parse_task_readback(path) == ("S4U", "{ACCOUNT}")


def test_task_readback_parser_accepts_8_bit_non_ascii_account(work_area):
    runner = load_runner()
    account = "PLACEHOLDER-" + chr(0x00C9)
    xml = runner.task_definition_xml("batch", account, "{WRAPPER}", "{ROOT}")
    readback = work_area / "readback-cp1252.xml"
    readback.write_bytes(xml.encode("cp1252"))
    assert runner.parse_task_readback(readback) == ("S4U", account)


def test_task_readback_command_compares_logon_and_account_case_insensitively(work_area):
    runner = load_runner()
    account = "PLACEHOLDER-" + chr(0x00C9)
    xml = runner.task_definition_xml("batch", account.upper(), "{WRAPPER}", "{ROOT}")
    readback = work_area / "readback.xml"
    readback.write_text(xml, encoding="utf-16")
    ok = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "task-readback",
            str(readback),
            "--expected-logon",
            "s4u",
            "--account",
            account.lower(),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert ok.returncode == 0
    assert "Registered task readback matches requested mode and account." in ok.stdout
    bad = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "task-readback",
            str(readback),
            "--expected-logon",
            "password",
            "--account",
            account.lower(),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert bad.returncode == 1
    assert "Registered task readback did not match requested mode and account." in bad.stdout


@pytest.mark.skipif(os.name != "nt", reason="batch cleanup is Windows-specific")
@pytest.mark.parametrize(
    "delete_exit_code, expected",
    [
        (0, "Cleanup deletion completed."),
        (5, "Cleanup deletion failed with exit code 5."),
    ],
)
def test_register_reports_readback_cleanup_result(work_area, delete_exit_code, expected):
    probe = write_register_cleanup_probe(work_area, delete_exit_code)
    done = run_register_probe(probe)
    assert done.returncode == delete_exit_code, done.stdout + done.stderr
    assert expected in done.stdout
    assert "findstr" not in register_batch_text().lower()
