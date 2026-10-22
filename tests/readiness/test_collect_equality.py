"""TDD tests for #2801 collect-equality.sh — per-machine self-report collector.

Subprocess contract tests against a controlled WORKSPACE_HUB fixture root, so the
emitted YAML schema, label resolution, data-access normalization, secret-allowlist,
behavior typing, and commit-on-change idempotency are all verifiable without
depending on the host's real hardware.
"""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

import yaml
from collector_support import (
    BASH_PATH,
    SCRIPT,
    _fixture,
    collector_env,
)
from collector_support import (
    bash_path as _bash_path,
)


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
        env=collector_env({"WORKSPACE_HUB": _bash_path(ws), "PATH": f"{_bash_path(bin_dir)}:{BASH_PATH}"}),
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
        env=collector_env({"WORKSPACE_HUB": _bash_path(ws), "PATH": f"{_bash_path(bin_dir)}:{BASH_PATH}"}),
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


def test_collect_commit_on_change_idempotent(tmp_path):
    # D1/DC4: two runs with no real change must not rewrite (hash excludes volatile + generated_at)
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-machine-a.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "machine-a"], env=collector_env(env), timeout=60, check=True)
    first_mtime = out.stat().st_mtime_ns
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "machine-a"], env=collector_env(env), timeout=60, check=True)
    assert out.stat().st_mtime_ns == first_mtime         # unchanged content → not rewritten


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
    assert out.read_text() == prior
    assert not list(out.parent.glob(".equality-machine-a.yaml.tmp.*"))


def test_collect_keeps_old_report_visible_until_atomic_rename(tmp_path):
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-machine-a.yaml"
    prior = 'generated_at: "prior"\nmachine: "machine-a"\nsentinel: old\n'
    out.write_text(prior)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    entered = tmp_path / "mv-entered"
    release = tmp_path / "mv-release"
    fake_mv = bindir / "mv"
    fake_mv.write_text(
        "#!/usr/bin/env bash\n"
        f"touch {_bash_path(entered)!r}\n"
        f"while [[ ! -f {_bash_path(release)!r} ]]; do sleep 0.02; done\n"
        "exec /usr/bin/mv \"$@\"\n"
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

    def read_continuously() -> None:
        while not stop_reader.is_set():
            try:
                observations.append(out.read_text())
            except Exception as exc:  # surfaced below; never swallowed as a pass
                read_errors.append(exc)
            time.sleep(0.001)

    reader = threading.Thread(target=read_continuously)
    reader.start()
    deadline = time.time() + 30
    while not entered.exists() and time.time() < deadline:
        time.sleep(0.02)
    assert entered.exists(), proc.communicate(timeout=5)
    assert out.read_text() == prior
    release.touch()
    stdout, stderr = proc.communicate(timeout=60)
    time.sleep(0.02)
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
