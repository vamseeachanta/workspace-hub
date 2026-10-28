"""TDD tests for #2801 collect-equality.sh — per-machine self-report collector.

Subprocess contract tests against a controlled WORKSPACE_HUB fixture root, so the
emitted YAML schema, label resolution, data-access normalization, secret-allowlist,
behavior typing, and commit-on-change idempotency are all verifiable without
depending on the host's real hardware.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
import yaml
from collector_support import (
    BASH_PATH,
    REPO,
    SCRIPT,
    _fixture,
    collector_env,
    native_path,
)
from collector_support import (
    bash_path as _bash_path,
)


@pytest.fixture(autouse=True)
def _isolate_collector_processes(tmp_path, monkeypatch):
    """Keep relative stub output and external tool discovery inside the fixture."""
    root_before = _directory_snapshot(REPO)
    monkeypatch.chdir(tmp_path)
    bindir = tmp_path / "offline-tools"
    bindir.mkdir()
    called = tmp_path / "external-tool-called"
    # Empty scheduler output is a successful query of an empty synthetic schedule.
    for name in ("crontab", "schtasks", "gh", "uv", "claude", "codex", "hermes", "gemini"):
        tool = bindir / name
        body = "exit 0\n" if name in ("crontab", "schtasks") else "exit 1\n"
        if name in ("claude", "codex", "hermes", "gemini"):
            body = f"touch {shlex.quote(_bash_path(called))}\n" + body
        tool.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8", newline="\n")
        tool.chmod(0o755)  # POSIX permission bits: u=rwx (7), g=rx and o=rx (5).
    original = collector_env

    def offline_env(env, *, stub_dirs=()):
        return original(env, stub_dirs=(*stub_dirs, bindir))

    monkeypatch.setitem(globals(), "collector_env", offline_env)
    yield
    assert not called.exists(), "a provider executable was invoked"
    assert _directory_snapshot(REPO) == root_before


def _directory_snapshot(root):
    """Detect new root entries and changes to existing root files."""
    return {path.name: None if path.is_dir() else path.read_bytes()
            for path in root.iterdir()}


def _fixture_snapshot(root):
    return {str(path.relative_to(root)): None if path.is_dir() else path.read_bytes()
            for path in root.rglob("*")}


def _assert_parent_environment_unchanged(before):
    changed = {name for name in before.keys() | os.environ.keys()
               if before.get(name) != os.environ.get(name)}
    # A failure reports names only; environment values may contain credentials.
    assert not changed, "parent environment changed"


def _run(ws: Path, *args: str) -> dict:
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a", *args],
        env=collector_env({"WORKSPACE_HUB": _bash_path(ws), "PATH": BASH_PATH}),
        capture_output=True, text=True, timeout=60, check=False)
    assert res.returncode == 0, res.stderr
    return yaml.safe_load(res.stdout)


def _uv_stub(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "uv-bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    python = shlex.quote(_bash_path(Path(sys.executable)))
    uv.write_text(
        "#!/usr/bin/env bash\n"
        "[[ \"$1 $2 $3\" == 'run --no-project python' ]] || exit 2\n"
        f"shift 3\nexec {python} \"$@\"\n"
    )
    uv.chmod(0o755)
    return bin_dir


def test_collect_publish_health_uses_working_resolver_and_exact_schema(tmp_path):
    ws = _fixture(tmp_path)
    health_dir = ws / ".claude" / "state" / "equivalence"
    health_dir.mkdir()
    (health_dir / "publish-health.json").write_text(json.dumps({
        "schema_version": 1,
        "ts": "2026-07-14T10:00:00+00:00",
        "phase": "publish",
        "duration_s": 2.5,
        "rc": 0,
    }))
    bin_dir = _uv_stub(tmp_path)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env({"WORKSPACE_HUB": _bash_path(ws), "PATH": BASH_PATH},
                          stub_dirs=(bin_dir,)),
        capture_output=True, text=True, timeout=60,
     check=False)
    assert res.returncode == 0, res.stderr
    health = yaml.safe_load(res.stdout)["dimensions"]["publish_health"]
    assert health == {
        "last_publish_at": "2026-07-14T10:00:00+00:00",
        "last_publish_duration_s": 2.5,
        "last_publish_rc": 0,
    }


def test_collect_invalid_publish_health_emits_no_partial_tuple(tmp_path):
    ws = _fixture(tmp_path)
    health_dir = ws / ".claude" / "state" / "equivalence"
    health_dir.mkdir()
    (health_dir / "publish-health.json").write_text(json.dumps({
        "schema_version": 1,
        "ts": "2026-07-14T10:00:00+00:00",
        "phase": "publish",
        "duration_s": True,
        "rc": 0,
    }))
    bin_dir = _uv_stub(tmp_path)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env({"WORKSPACE_HUB": _bash_path(ws), "PATH": BASH_PATH},
                          stub_dirs=(bin_dir,)),
        capture_output=True, text=True, timeout=60,
     check=False)
    assert res.returncode == 0, res.stderr
    health = yaml.safe_load(res.stdout)["dimensions"]["publish_health"]
    assert health == {
        "last_publish_at": "missing",
        "last_publish_duration_s": None,
        "last_publish_rc": None,
    }


def test_collect_emits_valid_yaml(tmp_path):
    d = _run(_fixture(tmp_path))
    assert d["machine"] == "machine-a"
    assert set(d["dimensions"]) >= {"compute", "data_access", "harness", "skills",
                                    "kanban", "memory", "behavior", "scheduler",
                                    "provider_harness"}


def test_collect_machine_override(tmp_path):
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-b"],
        env=collector_env({"WORKSPACE_HUB": _bash_path(_fixture(tmp_path)), "PATH": BASH_PATH}),
        capture_output=True, text=True, timeout=60, check=False)
    assert yaml.safe_load(res.stdout)["machine"] == "machine-b"


def test_collect_public_host_replaces_private_hostname(tmp_path):
    # The Windows wrapper exports EQ_PUBLIC_HOST=<public label>; tracked evidence must
    # carry that label, never the private OS hostname.
    ws = _fixture(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    hostname = bin_dir / "hostname"
    hostname.write_text("#!/usr/bin/env bash\nprintf '%s\\n' private-box-07\n")
    hostname.chmod(0o755)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env({"WORKSPACE_HUB": _bash_path(ws), "PATH": f"{_bash_path(bin_dir)}:{BASH_PATH}",
             "EQ_PUBLIC_HOST": "machine-a"}),
        capture_output=True, text=True, timeout=60, check=False)
    assert res.returncode == 0, res.stderr
    assert "private-box-07" not in res.stdout
    assert yaml.safe_load(res.stdout)["host"] == "machine-a"


def test_collect_host_defaults_to_os_hostname_without_public_host(tmp_path):
    ws = _fixture(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    hostname = bin_dir / "hostname"
    hostname.write_text("#!/usr/bin/env bash\nprintf '%s\\n' linux-box\n")
    hostname.chmod(0o755)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env({"WORKSPACE_HUB": _bash_path(ws), "PATH": f"{_bash_path(bin_dir)}:{BASH_PATH}"}),
        capture_output=True, text=True, timeout=60, check=False)
    assert res.returncode == 0, res.stderr
    assert yaml.safe_load(res.stdout)["host"] == "linux-box"


def test_collect_windows_autodetect_unknown_host_fails_closed(tmp_path):
    ws = _fixture(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    hostname = bin_dir / "hostname"
    hostname.write_text("#!/usr/bin/env bash\nprintf '%s\\n' unknown-win\n")
    hostname.chmod(0o755)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout"],
        env=collector_env({
            "WORKSPACE_HUB": _bash_path(ws),
            "PATH": f"{_bash_path(bin_dir)}:{BASH_PATH}",
            "HOME": str(tmp_path),
            "EQ_TEST_ENABLE_OS_OVERRIDE": "1",
            "EQ_OS_OVERRIDE": "windows",
        }),
        capture_output=True, text=True, timeout=60, check=False)
    assert res.returncode != 0
    assert "unknown Windows host" in res.stderr


def test_collect_compute_static_headroom_split(tmp_path):
    # DG1/DC4: static (hashed) vs headroom (volatile, excluded). RAM in MiB.
    c = _run(_fixture(tmp_path))["dimensions"]["compute"]
    assert "static" in c and "headroom" in c
    assert "ram_total_mib" in c["static"] and "cores" in c["static"]
    assert "disk_avail_gb" in c["headroom"]  # volatile lives here, not in static


def test_collect_data_access_bare_name_and_mode(tmp_path):
    # MC1/DG3: emit {repo: bare-name, mode}, never absolute /mnt path
    da = _run(_fixture(tmp_path))["dimensions"]["data_access"]
    by_repo = {e["repo"]: e["mode"] for e in da}
    assert by_repo["digitalmodel"] == "sibling"
    assert all("/" not in e["repo"] for e in da)        # bare names only
    assert "/mnt/" not in str(da)                        # no machine-layout leak


def test_collect_sources_readiness_value(tmp_path):
    # m1: readiness_overall SOURCED from the fixture file; file not modified
    ws = _fixture(tmp_path)
    rf = ws / ".claude" / "state" / "harness-readiness-machine-a.yaml"
    before = rf.read_text()
    d = _run(ws)
    assert d["dimensions"]["harness"]["readiness_overall"] == "fail"
    assert rf.read_text() == before                      # collector did not touch it


def test_collect_behavior_typed_groups(tmp_path):
    # MC3: behavior emits enums{} + hashes{} as distinct typed groups
    b = _run(_fixture(tmp_path))["dimensions"]["behavior"]
    assert "enums" in b and "hashes" in b
    assert isinstance(b["enums"], dict) and isinstance(b["hashes"], dict)


def test_collect_no_forbidden_fields(tmp_path):
    # C4: no tokens, env values, cron lines, or absolute $HOME paths in the emitted YAML
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env({"WORKSPACE_HUB": _bash_path(_fixture(tmp_path)), "PATH": BASH_PATH}),
        capture_output=True, text=True, timeout=60, check=False)
    out = res.stdout
    assert "gho_" not in out and "ghp_" not in out       # no gh token
    assert "* * *" not in out and "cron" not in out.lower().replace("has_", "")  # no cron lines
    d = yaml.safe_load(out)
    assert d["dimensions"]["harness"]["gh_auth"] in ("ok", "logged-out", "absent")  # enum, not token


def test_collect_yaml_injection_escaped(tmp_path):
    # CC1/GC1: a machine label containing a double-quote must NOT break the emitted YAML
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", 'evil"label: injected'],
        env=collector_env({"WORKSPACE_HUB": str(_fixture(tmp_path)), "PATH": "/usr/bin:/bin:/usr/local/bin"}),
        capture_output=True, text=True, timeout=60, check=False)
    d = yaml.safe_load(res.stdout)          # must still parse
    assert d["machine"] == 'evil"label: injected'   # value preserved, not injected as structure


def _report_snapshot(out):
    """Bytes and metadata independently detect a replacement, even within one clock tick."""
    stat = out.stat()
    return out.read_bytes(), stat.st_ino, stat.st_mtime_ns


def _publish_report(ws, env):
    result = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--machine", "machine-a"],
        env=collector_env(env, stub_dirs=(ws.parent / "report-tools",)),
        capture_output=True, text=True, timeout=60, check=False)
    assert result.returncode == 0, result.stderr
    return ws / ".claude" / "state" / "equality-machine-a.yaml"


def _controlled_report_fixture(tmp_path):
    # Reuse the provenance suite's disposable Git tree and isolated Git commands.
    from test_collect_equality_provenance import _git_fixture

    ws = _git_fixture(tmp_path)
    tools = tmp_path / "report-tools"
    tools.mkdir()
    real_date = _resolve_utility("date", collector_env(_atomic_write_env(ws)))
    date = tools / "date"
    date.write_text(
        "#!/usr/bin/env bash\n"
        'if [[ "$1" == +%Y-%m-%dT%H:%M:%S ]]; then printf "%s\\n" "$TEST_REPORT_TIME"; '
        'elif [[ "$1" == -r && "${3:-}" == +%Y-%m-%dT%H:%M:%S ]]; then '
        'printf "%s\\n" "$TEST_CONTEXT_TIME"; '
        f'else exec {shlex.quote(real_date)} "$@"; fi\n',
        encoding="utf-8", newline="\n")
    date.chmod(0o755)  # POSIX executable permissions, as in the isolation fixture.
    tasks = tools / "schtasks"
    tasks.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$TEST_TASKS"\n',
                     encoding="utf-8", newline="\n")
    tasks.chmod(0o755)
    env = _atomic_write_env(ws, tools)
    env.update(
        # Existing double-gated compute seam: this exercises serialization, not Windows.
        EQ_TEST_ENABLE_OS_OVERRIDE="1", EQ_OS_OVERRIDE="windows",
        # Independent synthetic example: two cores, one GiB total, half available,
        # and eight GiB disk space (one GiB = 1024 MiB).
        EQ_CORES="2", EQ_RAM_TOTAL_MIB="1024", EQ_RAM_AVAIL_MIB="512",
        EQ_DISK_AVAIL_GB="8", EQ_GPU_MODEL="none",
        # Distinct ISO calendar dates supply deterministic volatile values.
        TEST_REPORT_TIME="2026-01-01T00:00:00", TEST_CONTEXT_TIME="2026-01-01T00:00:00",
        TEST_TASKS="",
    )
    return ws, env


def _mark_report(out):
    # POSIX epoch zero is a deliberate marker: any publication changes the mtime,
    # even if generated_at is fixed and the filesystem has coarse clock resolution.
    os.utime(out, ns=(0, 0))
    return _report_snapshot(out)


def test_collect_commit_on_change_idempotent(tmp_path):
    ws, env = _controlled_report_fixture(tmp_path)
    out = _publish_report(ws, env)
    before = _mark_report(out)
    _publish_report(ws, env)
    assert _report_snapshot(out) == before


@pytest.mark.parametrize("changed", ["checkout_sha", "generated_at", "headroom",
                                     "context_md_mtime", "job_count"])
def test_collect_excluded_volatility_does_not_rewrite(tmp_path, changed):
    # Exclusion contract: collect-equality.sh's emit comment and the original
    # docs/plans/2026-05-26-issue-2801-machine-equality.md, canonical payload section.
    from test_collect_equality_provenance import _git

    ws, env = _controlled_report_fixture(tmp_path)
    out = _publish_report(ws, env)
    before = _mark_report(out)
    original = yaml.safe_load(before[0])
    if changed == "checkout_sha":
        _git(ws, "commit", "-q", "--allow-empty", "-m", "advance revision")
        _git(ws, "update-ref", "refs/remotes/origin/main", "HEAD")
    elif changed == "generated_at":
        env["TEST_REPORT_TIME"] = "2026-01-02T00:00:00"
    elif changed == "headroom":
        # Half of the initial synthetic example's available RAM and disk.
        env.update(EQ_RAM_AVAIL_MIB="256", EQ_DISK_AVAIL_GB="4")
    elif changed == "context_md_mtime":
        env["TEST_CONTEXT_TIME"] = "2026-01-02T00:00:00"
    else:
        # One synthetic CSV task, with neither stable scheduler capability set.
        env["TEST_TASKS"] = '"synthetic-task","ready"'

    candidate = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env(env, stub_dirs=(ws.parent / "report-tools",)),
        capture_output=True, text=True, timeout=60, check=False)
    assert candidate.returncode == 0, candidate.stderr
    current = yaml.safe_load(candidate.stdout)
    # Remove only the independently specified changing field, and require all
    # meaningful siblings (including freshness and scheduler flags) to stay equal.
    def take_changed(report):
        if changed == "checkout_sha":
            return report["provenance"].pop(changed)
        if changed == "generated_at":
            return report.pop(changed)
        dimension = {"headroom": "compute", "context_md_mtime": "memory",
                     "job_count": "scheduler"}[changed]
        return report["dimensions"][dimension].pop(changed)

    assert take_changed(current) != take_changed(original)
    assert current == original
    _publish_report(ws, env)
    assert _report_snapshot(out) == before


def test_collect_stable_capability_change_rewrites(tmp_path):
    ws, env = _controlled_report_fixture(tmp_path)
    out = _publish_report(ws, env)
    before = _mark_report(out)
    original = yaml.safe_load(before[0])
    # Independent positive control: double the synthetic two-core capability.
    env["EQ_CORES"] = "4"
    _publish_report(ws, env)
    after = _report_snapshot(out)
    current = yaml.safe_load(after[0])
    assert after[0] != before[0]
    assert after[2] != before[2]
    assert current["dimensions"]["compute"]["static"]["cores"] == 4
    original["dimensions"]["compute"]["static"]["cores"] = 4
    assert current == original


def _resolve_utility(name, env):
    """Ask Bash before adding an interception directory; never recurse into a stub."""
    result = subprocess.run(["bash", "-c", 'command -v -- "$1"', "_", name],
                            env=env, capture_output=True, text=True, timeout=60, check=True)
    utility = result.stdout.strip()
    assert utility, f"utility not found: {name}"
    return utility


def _atomic_write_env(ws: Path, bindir: Path | None = None) -> dict[str, str]:
    path = BASH_PATH if bindir is None else f"{_bash_path(bindir)}:{BASH_PATH}"
    return {
        "WORKSPACE_HUB": _bash_path(ws),
        "PATH": path,
        "HOME": _bash_path(ws.parent),
    }


def test_collect_atomic_failure_preserves_prior_report(tmp_path):
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-machine-a.yaml"
    prior = 'generated_at: "prior"\nmachine: "machine-a"\nsentinel: old\n'
    out.write_text(prior)
    before = _report_snapshot(out)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake_mv = bindir / "mv"
    fake_mv.write_text("#!/usr/bin/env bash\nexit 19\n")
    fake_mv.chmod(0o755)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--machine", "machine-a"],
        env=collector_env(_atomic_write_env(ws, bindir)), capture_output=True, text=True, timeout=60,
     check=False)
    assert res.returncode != 0
    assert "could not publish report atomically" in res.stderr
    assert _report_snapshot(out) == before
    assert not list(out.parent.glob(".equality-machine-a.yaml.tmp.*"))


@pytest.mark.parametrize("spaced_utility_path", [False, True])
def test_collect_keeps_old_report_visible_until_atomic_rename(tmp_path, spaced_utility_path):
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-machine-a.yaml"
    prior = 'generated_at: "prior"\nmachine: "machine-a"\nsentinel: old\n'
    out.write_text(prior)
    # Discover the genuine utility before the blocking stub enters PATH.
    discovery_env = collector_env(_atomic_write_env(ws))
    real_mv = _resolve_utility("mv", discovery_env)
    if spaced_utility_path:
        utilities = tmp_path / "move tools' directory"
        utilities.mkdir()
        source = native_path(real_mv)
        # Bash may omit the executable suffix that native filesystem APIs require.
        if not source.is_file():
            source = source.with_name(source.name + ".exe")
        shutil.copy2(source, utilities / source.name)
        discovery_env["PATH"] = f"{_bash_path(utilities)}:{discovery_env['PATH']}"
        real_mv = _resolve_utility("mv", discovery_env)
        assert " " in real_mv and "'" in real_mv
        assert native_path(real_mv).parent == utilities
    bindir = tmp_path / "bin"
    bindir.mkdir()
    entered = tmp_path / "mv-entered"
    release = tmp_path / "mv-release"
    fake_mv = bindir / "mv"
    fake_mv.write_text(
        "#!/usr/bin/env bash\n"
        f"touch {shlex.quote(_bash_path(entered))}\n"
        f"while [[ ! -f {shlex.quote(_bash_path(release))} ]]; do sleep 0.02; done\n"
        f'exec {shlex.quote(real_mv)} "$@"\n'
    )
    fake_mv.chmod(0o755)
    proc = subprocess.Popen(
        ["bash", _bash_path(SCRIPT), "--machine", "machine-a"],
        env=collector_env(_atomic_write_env(ws, bindir)), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    )
    observations: list[str] = []
    read_errors: list[Exception] = []
    stop_reader = threading.Event()
    prior_seen = threading.Event()
    published_seen = threading.Event()

    def read_continuously() -> None:
        while not stop_reader.is_set():
            try:
                content = out.read_text()
                observations.append(content)
                (prior_seen if content == prior else published_seen).set()
            except Exception as exc:  # surfaced below; never swallowed as a pass
                read_errors.append(exc)
            time.sleep(0.001)

    reader = threading.Thread(target=read_continuously)
    reader.start()
    try:
        deadline = time.monotonic() + 30
        while not entered.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert entered.exists(), "collector did not reach the rename barrier"
        assert out.read_text() == prior
        assert prior_seen.wait(timeout=5)
        release.touch()
        stdout, stderr = proc.communicate(timeout=60)
        assert published_seen.wait(timeout=5)
    finally:
        # Always release a failed assertion's barrier and join its reader.
        release.touch()
        try:
            if proc.poll() is None:
                proc.communicate(timeout=60)
        finally:
            stop_reader.set()
            reader.join(timeout=5)
    assert proc.returncode == 0, (stdout, stderr)
    final = out.read_text()
    parsed = yaml.safe_load(final)
    assert parsed["machine"] == "machine-a"
    assert "dimensions" in parsed
    assert not read_errors
    assert prior in observations
    assert final in observations
    assert set(observations) <= {prior, final}
    assert not list(out.parent.glob(".equality-machine-a.yaml.tmp.*"))


SOLVER_NAMES = {"orcaflex", "orcawave", "aqwa", "ansys"}
STATUS_ENUM = {"licensed", "present", "absent", "unknown"}
EVIDENCE_ENUM = {"import", "env", "root", "absent", "unknown"}


def _expected_solver_rows(present=False):
    # Independent truth table from probe-solvers.sh's documented output contract:
    # blocked imports + empty roots -> absent; an explicit directory -> present/env.
    return [{"name": name,
             "status": "present" if present and name == "orcawave" else "absent",
             "evidence": "env" if present and name == "orcawave" else "absent"}
            for name in ("orcaflex", "orcawave", "aqwa", "ansys")]


def test_solver_discovery_fixture_ignores_ambient_environment(tmp_path, monkeypatch):
    ws = _fixture(tmp_path)
    ambient = tmp_path / "ambient installation"
    ambient.mkdir()
    ambient_bin = ambient / "bin"
    ambient_bin.mkdir()
    called = tmp_path / "solver-or-interpreter-called"
    imported = tmp_path / "sdk-imported"
    for name in ("python", "python3", "OrcaFlex", "OrcaWave", "aqwa", "ansys"):
        tool = ambient_bin / name
        tool.write_text(
            "#!/usr/bin/env bash\n"
            f"touch {shlex.quote(_bash_path(called))}\nexit 1\n",
            encoding="utf-8", newline="\n")
        tool.chmod(0o755)  # POSIX permission bits: u=rwx (7), g=rx and o=rx (5).
    (ambient / "OrcFxAPI.py").write_text(
        f"from pathlib import Path\nPath({str(imported)!r}).touch()\n",
        encoding="utf-8")
    (ambient / "ansys" / "v252").mkdir(parents=True)  # Version token example in probe-solvers.sh.
    startup = ambient / "startup.sh"
    startup.write_text(f"touch {shlex.quote(_bash_path(called))}\n",
                       encoding="utf-8", newline="\n")
    for name, value in {
        "PATH": f"{_bash_path(ambient_bin)}:{BASH_PATH}",
        "HOME": str(ambient), "PYTHONPATH": str(ambient),
        "ORCAWAVE_PATH": str(ambient), "TEST_INSTALL_ROOT": str(ambient),
        "BASH_ENV": str(startup), "TMPDIR": str(ambient),
    }.items():
        monkeypatch.setenv(name, value)
    parent_before = dict(os.environ)
    fixture_before = _fixture_snapshot(ws)

    # Ambient discovery variables are not fixture inputs.
    assert _run(ws)["dimensions"]["solvers"] == _expected_solver_rows()
    # Even a supplied leading interpreter and importable synthetic SDK stay blocked.
    explicit = {"WORKSPACE_HUB": str(ws), "PATH": os.environ["PATH"],
                "PYTHONPATH": str(ambient), "TEST_INSTALL_ROOT": str(ambient)}
    explicit_before = dict(explicit)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "fixture"],
        env=collector_env(explicit), capture_output=True, text=True,
        timeout=60, check=False)  # Collector subprocess budget used throughout this suite.
    assert res.returncode == 0, res.stderr
    assert yaml.safe_load(res.stdout)["dimensions"]["solvers"] == _expected_solver_rows()
    assert explicit == explicit_before
    _assert_parent_environment_unchanged(parent_before)
    assert _fixture_snapshot(ws) == fixture_before
    assert not called.exists()
    assert not imported.exists()


@pytest.mark.parametrize("order", [(False, True, False), (True, False, True)],
                         ids=["absent-present-absent", "present-absent-present"])
@pytest.mark.parametrize("platform", ["linux", "windows"])
def test_solver_discovery_fixture_is_order_independent(tmp_path, order, platform):
    ws = _fixture(tmp_path)
    install = tmp_path / "synthetic installation"
    install.mkdir()
    report = ws / ".claude" / "state" / "equality-fixture.yaml"
    fixture_before = _fixture_snapshot(ws)
    env = {"WORKSPACE_HUB": str(ws), "PATH": BASH_PATH,
           "EQ_TEST_ENABLE_OS_OVERRIDE": "1", "EQ_OS_OVERRIDE": platform}
    parent_before = dict(os.environ)
    for present in order:
        inputs = dict(env)
        if present:
            inputs["ORCAWAVE_PATH"] = str(install)
        res = subprocess.run(
            ["bash", _bash_path(SCRIPT), "--machine", "fixture"],
            env=collector_env(inputs), capture_output=True, text=True,
            timeout=60, check=False)  # Collector subprocess budget used throughout this suite.
        assert res.returncode == 0, res.stderr
        data = yaml.safe_load(report.read_text())
        assert data["os"] == platform
        assert data["dimensions"]["solvers"] == _expected_solver_rows(present)
        after = _fixture_snapshot(ws)
        assert after.pop(str(report.relative_to(ws)))
        assert after == fixture_before
        assert "ORCAWAVE_PATH" not in env
        _assert_parent_environment_unchanged(parent_before)


def test_collect_relative_stub_outputs_stay_temporary(tmp_path):
    ws = _fixture(tmp_path)
    bindir = tmp_path / "relative-output-tools"
    bindir.mkdir()
    hostname = bindir / "hostname"
    hostname.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' called >> collector-counter\n"
        "pwd > collector-path\nprintf '%s\\n' fixture\n",
        encoding="utf-8", newline="\n")
    hostname.chmod(0o755)  # POSIX permission bits: u=rwx (7), g=rx and o=rx (5).
    before = _fixture_snapshot(ws)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "fixture"],
        env=collector_env({"WORKSPACE_HUB": str(ws), "PATH": BASH_PATH},
                          stub_dirs=(bindir,)),
        capture_output=True, text=True,
        timeout=60, check=False)  # Collector subprocess budget used throughout this suite.
    assert res.returncode == 0, res.stderr
    assert (tmp_path / "collector-counter").read_text().splitlines() == ["called"]
    assert (tmp_path / "collector-path").read_text().strip() == _bash_path(tmp_path)
    assert _fixture_snapshot(ws) == before


def test_collect_emits_schema_v4(tmp_path):
    # #2889: schema bumped to 4 with the provider_harness dimension added.
    d = _run(_fixture(tmp_path))
    assert d["schema_version"] == 4


def test_collect_emits_schema_v4_with_complete_provider_harness(tmp_path):
    d = _run(_fixture(tmp_path))
    harness = d["dimensions"]["provider_harness"]
    assert harness["schema_version"] == 1
    assert set(harness["providers"]) == {"claude", "codex", "hermes", "gemini"}
    for provider in ("claude", "codex", "hermes", "gemini"):
        record = harness["providers"][provider]
        assert set(record) >= {"present", "installed", "memory:read",
                               "skills:invoke", "workflow:gates"}
        for capability in ("memory:read", "skills:invoke", "workflow:gates"):
            assert set(record[capability]) == {"status", "reason"}
            assert record[capability]["status"] in {
                "present", "absent", "expected_divergence", "unknown"}
            assert isinstance(record[capability]["reason"], str)


def test_collect_provider_harness_no_forbidden_fields(tmp_path):
    ws = _fixture(tmp_path)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env({
            "WORKSPACE_HUB": _bash_path(ws),
            "PATH": BASH_PATH,
            "HOME": str(tmp_path),
            "GITHUB_TOKEN": "ghp_should_not_leak",
            "CRON_EXAMPLE": "* * * * * /secret/path",
        }),
        capture_output=True,
        text=True,
        timeout=60, check=False)
    assert res.returncode == 0, res.stderr
    provider_block = res.stdout.split("provider_harness:", 1)[1]
    assert "ghp_should_not_leak" not in provider_block
    assert "* * *" not in provider_block
    assert ".codex/auth.json" not in provider_block


def test_provider_harness_helper_is_windows_stdlib_safe(tmp_path):
    ws = _fixture(tmp_path)
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout", "--machine", "ace-win-1"],
        env=collector_env({
            "WORKSPACE_HUB": _bash_path(ws),
            "PATH": BASH_PATH,
            "HOME": str(tmp_path),
            "EQ_TEST_ENABLE_OS_OVERRIDE": "1",
            "EQ_OS_OVERRIDE": "windows",
        }),
        capture_output=True,
        text=True,
        timeout=60, check=False)
    assert res.returncode == 0, res.stderr
    data = yaml.safe_load(res.stdout)
    assert data["schema_version"] == 4
    assert "provider_harness" in data["dimensions"]


def test_collect_emits_solvers_block(tmp_path):
    # #2849: solvers dimension carries all four named solvers.
    d = _run(_fixture(tmp_path))
    solvers = d["dimensions"]["solvers"]
    assert isinstance(solvers, list) and len(solvers) == 4
    assert {s["name"] for s in solvers} == SOLVER_NAMES


def test_collect_solvers_status_enum_only(tmp_path):
    # Every emitted status/evidence is from the closed enum (no free-form leakage).
    solvers = _run(_fixture(tmp_path))["dimensions"]["solvers"]
    for s in solvers:
        assert s["status"] in STATUS_ENUM
        assert s["evidence"] in EVIDENCE_ENUM


def test_collect_solvers_absent_on_clean_fixture(tmp_path):
    # The fixture host has no OrcFxAPI / ORCAWAVE_PATH / ANSYS root → all absent.
    solvers = _run(_fixture(tmp_path))["dimensions"]["solvers"]
    assert all(s["status"] == "absent" for s in solvers), solvers


def test_collect_solvers_no_abs_paths(tmp_path):
    # bare-name rule: no '/' or '\' characters in any solver status/evidence value.
    solvers = _run(_fixture(tmp_path))["dimensions"]["solvers"]
    for s in solvers:
        assert "/" not in str(s["status"]) and "\\" not in str(s["status"])
        assert "/" not in str(s["evidence"]) and "\\" not in str(s["evidence"])


def test_collect_solvers_present_via_env_before_sandbox(tmp_path):
    # Non-vacuous: a real ORCAWAVE_PATH dir → orcawave `present` (evidence: env). Proves the
    # solver probe sees the real environment (runs BEFORE the HOME/XDG behaviour sandbox) and
    # that the present-classification path actually executes, not just the all-absent path.
    ws = _fixture(tmp_path)
    owp = tmp_path / "OrcaWaveInstall"
    owp.mkdir()
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "machine-a"],
        env=collector_env({"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin",
             "ORCAWAVE_PATH": str(owp)}),
        capture_output=True, text=True, timeout=60, check=False)
    assert res.returncode == 0, res.stderr
    solvers = {s["name"]: s for s in yaml.safe_load(res.stdout)["dimensions"]["solvers"]}
    assert solvers["orcawave"]["status"] == "present"
    assert solvers["orcawave"]["evidence"] == "env"
    # the env-derived value must still not leak the absolute path into the emitted cell
    assert "/" not in solvers["orcawave"]["status"] and "/" not in solvers["orcawave"]["evidence"]
    assert str(owp) not in res.stdout.split("solvers:")[1].split("harness:")[0]


def test_collect_solvers_canonical_hash_includes_block(tmp_path):
    # Toggling a solver status in the committed file is a MEANINGFUL change → rewrite.
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-machine-a.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "machine-a"], env=collector_env(env), timeout=60, check=True)
    text = out.read_text().replace(
        "{name: orcaflex, status: absent", "{name: orcaflex, status: licensed")
    out.write_text(text)
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "machine-a"], env=collector_env(env), timeout=60, check=True)
    # real collection differs from the tampered file → rewritten back to absent
    assert "{name: orcaflex, status: absent" in out.read_text()


def test_collect_commit_on_change_detects_real_drift(tmp_path):
    # DC4: a change to a MEANINGFUL (non-volatile) field MUST trigger a rewrite. Guards the
    # canonical()-grep bug where a volatile field sharing a line masked its neighbors.
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-machine-a.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "machine-a"], env=collector_env(env), timeout=60, check=True)
    # tamper a meaningful field in the committed file; real collection differs → must rewrite
    text = out.read_text().replace("hermes_home: absent", "hermes_home: present")
    out.write_text(text)
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "machine-a"], env=collector_env(env), timeout=60, check=True)
    assert "hermes_home: absent" in out.read_text()      # rewritten back to the real value


def test_collect_kanban_queue_order_is_byte_sorted(tmp_path):
    # LC_ALL=C: '_leader-state' sorts FIRST (byte order, matching Git Bash on Windows).
    # Locale collation buried it mid-list, so the same queue set graded DIVERGES across OSes.
    ws = _fixture(tmp_path)
    (ws / ".claude" / "dispatch" / "_leader-state.yaml").write_text("x")
    d = _run(ws)
    assert d["dimensions"]["kanban"]["dispatch_queues"] == "_leader-state,machine-a,multi"


# ── harness_checkup dimension (#3408) ────────────────────────────────────────
def test_collect_harness_checkup_failclosed_when_absent(tmp_path):
    # no harness-checkup-<machine>.json in the fixture → block present but all-null (fail-closed →
    # the matrix grades MISSING-EVIDENCE; never silently green).
    d = _run(_fixture(tmp_path))["dimensions"]["harness_checkup"]
    assert d["audited_at"] is None
    for k in ("cc_version", "cc_latest", "version_current", "install_method", "duplicate_installs",
              "settings_parse_ok", "broken_agents", "unused_skills", "unused_plugins",
              "default_mode", "auto_mode_default"):
        assert d[k] is None, k


def test_collect_harness_checkup_passthrough(tmp_path):
    import json as _json
    ws = _fixture(tmp_path)
    (ws / ".claude" / "state" / "harness-checkup-machine-a.json").write_text(_json.dumps({
        "audited_at": "2026-07-09T12:00:00+00:00", "cc_version": "2.1.205", "cc_latest": "2.1.205",
        "version_current": True, "install_method": "npm-global", "duplicate_installs": 0,
        "settings_parse_ok": True, "broken_agents": 0, "unused_skills": 23, "unused_plugins": 8,
        "default_mode": "auto", "auto_mode_default": True,
    }))
    d = _run(ws)["dimensions"]["harness_checkup"]
    assert d["cc_version"] == "2.1.205" and d["cc_latest"] == "2.1.205"
    assert d["version_current"] is True and d["auto_mode_default"] is True
    assert d["install_method"] == "npm-global" and d["default_mode"] == "auto"
    assert d["duplicate_installs"] == 0 and d["unused_skills"] == 23 and d["unused_plugins"] == 8


def test_collect_harness_checkup_type_gated(tmp_path):
    # a malformed audit (wrong JSON types) must NOT inject garbage into the graded cells — the
    # collector type-gates each field and drops mismatches to null (allowlist-safe by construction).
    import json as _json
    ws = _fixture(tmp_path)
    (ws / ".claude" / "state" / "harness-checkup-machine-a.json").write_text(_json.dumps({
        "audited_at": "2026-07-09T12:00:00+00:00",
        "version_current": "yes",          # wrong type → null
        "duplicate_installs": "lots",       # wrong type → null
        "settings_parse_ok": True,          # correct bool passes through
    }))
    d = _run(ws)["dimensions"]["harness_checkup"]
    assert d["version_current"] is None
    assert d["duplicate_installs"] is None
    assert d["settings_parse_ok"] is True


def test_shared_environment_blocks_ambient_external_tools(tmp_path):
    """The provenance helper must also isolate scheduler, auth and provider commands."""
    from collector_support import collector_env as shared_env

    ws = _fixture(tmp_path)
    ambient = tmp_path / "ambient-tools"
    ambient.mkdir()
    called = tmp_path / "ambient-called"
    for name in ("crontab", "schtasks", "gh", "uv", "claude", "codex", "hermes", "gemini"):
        tool = ambient / name
        tool.write_text(
            f"#!/usr/bin/env bash\ntouch {shlex.quote(_bash_path(called))}\n",
            encoding="utf-8", newline="\n")
        tool.chmod(0o755)
    env = shared_env(_atomic_write_env(ws, ambient))
    # Only synthetic executables could run even if isolation regresses.
    result = subprocess.run(
        ["bash", "-c", 'crontab -l; schtasks /query; gh auth status; uv --version; '
         'claude --version; codex --version; hermes --version; gemini --version'],
        env=env, capture_output=True, text=True, timeout=60, check=False)
    assert not called.exists(), "shared helper reached an ambient external tool"
    assert result.returncode != 0
