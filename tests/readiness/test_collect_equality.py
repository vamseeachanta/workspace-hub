"""TDD tests for #2801 collect-equality.sh — per-machine self-report collector.

Subprocess contract tests against a controlled WORKSPACE_HUB fixture root, so the
emitted YAML schema, label resolution, data-access normalization, secret-allowlist,
behavior typing, and commit-on-change idempotency are all verifiable without
depending on the host's real hardware.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "readiness" / "collect-equality.sh"
BASH_PATH = "/mingw64/bin:/usr/bin:/bin:/usr/local/bin"


def _bash_path(path: Path) -> str:
    try:
        return subprocess.check_output(["cygpath", "-u", str(path)], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return str(path)


def _fixture(tmp_path: Path) -> Path:
    """Minimal WORKSPACE_HUB tree the collector reads."""
    ws = tmp_path / "workspace-hub"
    (ws / ".claude" / "skills" / "cat" / "skillA").mkdir(parents=True)
    (ws / ".claude" / "skills" / "cat" / "skillA" / "SKILL.md").write_text("x")
    (ws / ".claude" / "dispatch").mkdir(parents=True)
    (ws / ".claude" / "dispatch" / "dev-primary.yaml").write_text("x")
    (ws / ".claude" / "dispatch" / "multi.yaml").write_text("x")
    (ws / ".claude" / "memory").mkdir(parents=True)
    (ws / ".claude" / "memory" / "context.md").write_text("ctx")
    (ws / ".claude" / "state").mkdir(parents=True)
    (ws / ".claude" / "state" / "harness-readiness-dev-primary.yaml").write_text(
        "overall: fail\npass_count: 17\n")
    # sibling tier-1 repo (not nested) — exercises bare-name + sibling mode
    (tmp_path / "digitalmodel" / ".git").mkdir(parents=True)
    return ws


def _run(ws: Path, *args: str) -> dict:
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout", "--machine", "dev-primary", *args],
        env={"WORKSPACE_HUB": _bash_path(ws), "PATH": BASH_PATH},
        capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    return yaml.safe_load(res.stdout)


def test_collect_emits_valid_yaml(tmp_path):
    d = _run(_fixture(tmp_path))
    assert d["machine"] == "dev-primary"
    assert set(d["dimensions"]) >= {"compute", "data_access", "harness", "skills",
                                    "kanban", "memory", "behavior", "scheduler",
                                    "provider_harness"}


def test_collect_machine_override(tmp_path):
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout", "--machine", "licensed-win-2"],
        env={"WORKSPACE_HUB": _bash_path(_fixture(tmp_path)), "PATH": BASH_PATH},
        capture_output=True, text=True, timeout=60)
    assert yaml.safe_load(res.stdout)["machine"] == "licensed-win-2"


def test_collect_windows_autodetect_unknown_host_fails_closed(tmp_path):
    ws = _fixture(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    hostname = bin_dir / "hostname"
    hostname.write_text("#!/usr/bin/env bash\nprintf '%s\\n' unknown-win\n")
    hostname.chmod(0o755)
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout"],
        env={
            "WORKSPACE_HUB": _bash_path(ws),
            "PATH": f"{bin_dir}:{BASH_PATH}",
            "HOME": str(tmp_path),
            "EQ_TEST_ENABLE_OS_OVERRIDE": "1",
            "EQ_OS_OVERRIDE": "windows",
        },
        capture_output=True, text=True, timeout=60)
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
    rf = ws / ".claude" / "state" / "harness-readiness-dev-primary.yaml"
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
        ["bash", str(SCRIPT), "--stdout", "--machine", "dev-primary"],
        env={"WORKSPACE_HUB": _bash_path(_fixture(tmp_path)), "PATH": BASH_PATH},
        capture_output=True, text=True, timeout=60)
    out = res.stdout
    assert "gho_" not in out and "ghp_" not in out       # no gh token
    assert "* * *" not in out and "cron" not in out.lower().replace("has_", "")  # no cron lines
    d = yaml.safe_load(out)
    assert d["dimensions"]["harness"]["gh_auth"] in ("ok", "logged-out", "absent")  # enum, not token


def test_collect_yaml_injection_escaped(tmp_path):
    # CC1/GC1: a machine label containing a double-quote must NOT break the emitted YAML
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout", "--machine", 'evil"label: injected'],
        env={"WORKSPACE_HUB": str(_fixture(tmp_path)), "PATH": "/usr/bin:/bin:/usr/local/bin"},
        capture_output=True, text=True, timeout=60)
    d = yaml.safe_load(res.stdout)          # must still parse
    assert d["machine"] == 'evil"label: injected'   # value preserved, not injected as structure


def test_collect_commit_on_change_idempotent(tmp_path):
    # D1/DC4: two runs with no real change must not rewrite (hash excludes volatile + generated_at)
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    first_mtime = out.stat().st_mtime_ns
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert out.stat().st_mtime_ns == first_mtime         # unchanged content → not rewritten


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
    assert set(harness["providers"]) == {"claude", "codex", "hermes"}
    for provider in ("claude", "codex", "hermes"):
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
        ["bash", str(SCRIPT), "--stdout", "--machine", "dev-primary"],
        env={
            "WORKSPACE_HUB": _bash_path(ws),
            "PATH": BASH_PATH,
            "HOME": str(tmp_path),
            "GITHUB_TOKEN": "ghp_should_not_leak",
            "CRON_EXAMPLE": "* * * * * /secret/path",
        },
        capture_output=True,
        text=True,
        timeout=60)
    assert res.returncode == 0, res.stderr
    provider_block = res.stdout.split("provider_harness:", 1)[1]
    assert "ghp_should_not_leak" not in provider_block
    assert "* * *" not in provider_block
    assert ".codex/auth.json" not in provider_block


def test_provider_harness_helper_is_windows_stdlib_safe(tmp_path):
    ws = _fixture(tmp_path)
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout", "--machine", "ace-win-1"],
        env={
            "WORKSPACE_HUB": _bash_path(ws),
            "PATH": BASH_PATH,
            "HOME": str(tmp_path),
            "EQ_TEST_ENABLE_OS_OVERRIDE": "1",
            "EQ_OS_OVERRIDE": "windows",
        },
        capture_output=True,
        text=True,
        timeout=60)
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
        ["bash", str(SCRIPT), "--stdout", "--machine", "dev-primary"],
        env={"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin",
             "ORCAWAVE_PATH": str(owp)},
        capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    solvers = {s["name"]: s for s in yaml.safe_load(res.stdout)["dimensions"]["solvers"]}
    assert solvers["orcawave"]["status"] == "present"
    assert solvers["orcawave"]["evidence"] == "env"
    # the env-derived value must still not leak the absolute path into the emitted cell
    assert "/" not in solvers["orcawave"]["status"] and "/" not in solvers["orcawave"]["evidence"]
    assert str(owp) not in res.stdout.split("solvers:")[1].split("harness:")[0]


# ── probe-solvers.sh unit semantics (#2849 / PR #2850 decision 2026-05-28) ──────
# present ≠ licensed: install/import/env presence classifies as `present`; `licensed`
# requires a real license signal (none available locally → never emitted here).
PROBE_LIB = REPO_ROOT / "scripts" / "readiness" / "lib" / "probe-solvers.sh"


def _probe(fn: str, env_extra: dict | None = None, fake_import_ok: bool = False,
           tmp_path: Path | None = None) -> str:
    """Source probe-solvers.sh and echo the result of one probe function.

    fake_import_ok=True shims a `python` on PATH whose `import OrcFxAPI` succeeds,
    so the OrcFxAPI SDK-present path is exercised without the real SDK installed.
    """
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin"}
    path_prefix = ""
    if fake_import_ok:
        assert tmp_path is not None
        binp = tmp_path / "bin"
        binp.mkdir(exist_ok=True)
        py = binp / "python"
        py.write_text("#!/usr/bin/env bash\nexit 0\n")  # any args → success (import ok)
        py.chmod(0o755)
        path_prefix = f"{binp}:"
    env["PATH"] = path_prefix + env["PATH"]
    if env_extra:
        env.update(env_extra)
    res = subprocess.run(
        ["bash", "-c", f'source "{PROBE_LIB}"; {fn}'],
        env=env, capture_output=True, text=True, timeout=30)
    assert res.returncode == 0, res.stderr
    return res.stdout.strip()


def test_probe_orcaflex_import_ok_is_present_not_licensed(tmp_path):
    # `import OrcFxAPI` success → present (NOT licensed). Load-bearing decision.
    assert _probe("probe_orcaflex", fake_import_ok=True, tmp_path=tmp_path) == "present"
    assert _probe("probe_orcaflex_evidence", fake_import_ok=True, tmp_path=tmp_path) == "import"


def test_probe_orcawave_import_ok_is_present_not_licensed(tmp_path):
    assert _probe("probe_orcawave", fake_import_ok=True, tmp_path=tmp_path) == "present"


def test_probe_orcawave_env_only_is_present(tmp_path):
    owp = tmp_path / "ow"; owp.mkdir()
    assert _probe("probe_orcawave", env_extra={"ORCAWAVE_PATH": str(owp)}) == "present"


def test_probe_ansys_license_env_does_not_upgrade_to_licensed(tmp_path):
    # A license-server env var is recorded as evidence but never upgrades status to licensed.
    # No ANSYS root on the test host → absent regardless of env (real signal still needed).
    assert _probe("probe_ansys",
                  env_extra={"ANSYSLI_SERVERS": "1055@licsrv"}) == "absent"


def test_probe_never_emits_licensed_locally(tmp_path):
    # No real license probe exists locally → no probe emits `licensed` on this host.
    for fn in ("probe_orcaflex", "probe_orcawave", "probe_aqwa", "probe_ansys"):
        assert _probe(fn, fake_import_ok=True, tmp_path=tmp_path) != "licensed"


def test_collect_solvers_canonical_hash_includes_block(tmp_path):
    # Toggling a solver status in the committed file is a MEANINGFUL change → rewrite.
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    text = out.read_text().replace(
        "{name: orcaflex, status: absent", "{name: orcaflex, status: licensed")
    out.write_text(text)
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    # real collection differs from the tampered file → rewritten back to absent
    assert "{name: orcaflex, status: absent" in out.read_text()


def test_collect_commit_on_change_detects_real_drift(tmp_path):
    # DC4: a change to a MEANINGFUL (non-volatile) field MUST trigger a rewrite. Guards the
    # canonical()-grep bug where a volatile field sharing a line masked its neighbors.
    ws = _fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    # tamper a meaningful field in the committed file; real collection differs → must rewrite
    text = out.read_text().replace("hermes_home: absent", "hermes_home: present")
    out.write_text(text)
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert "hermes_home: absent" in out.read_text()      # rewritten back to the real value


# ── #2851 freshness guard: checkout-provenance block ────────────────────────
MEASURED_PATH = ("scripts", "readiness", "harness-config.yaml")  # in the MEASURED allowlist


def _git(ws: Path, *args: str) -> None:
    """Run a git command in the fixture with deterministic identity."""
    env = {**os.environ,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.test",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.test",
           "HOME": str(ws.parent)}
    subprocess.run(["git", "-C", str(ws), *args], env=env, check=True,
                   capture_output=True, timeout=60)


def _git_fixture(tmp_path: Path) -> Path:
    """A WORKSPACE_HUB fixture that is also a committed git repo with an origin/main ref.

    The repo is clean and current → fresh provenance by default. A measured-path file
    (harness-config.yaml) is tracked so dirty-flag tests can toggle it.
    """
    ws = _fixture(tmp_path)
    (ws / "scripts" / "readiness").mkdir(parents=True, exist_ok=True)
    (ws / "scripts" / "readiness" / "harness-config.yaml").write_text("workstations: {}\n")
    _git(ws, "init", "-q", "-b", "main")
    _git(ws, "add", "-A")
    _git(ws, "commit", "-q", "-m", "init")
    _git(ws, "update-ref", "refs/remotes/origin/main", "HEAD")   # current with main → behind=0
    return ws


def _stdout_prov(ws: Path, *args: str, env_extra: dict | None = None) -> dict:
    env = {"WORKSPACE_HUB": _bash_path(ws), "PATH": BASH_PATH, "HOME": str(ws.parent)}
    if env_extra:
        env.update(env_extra)
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout", "--machine", "dev-primary", *args],
        env=env, capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    return yaml.safe_load(res.stdout)["provenance"]


def test_collect_emits_provenance(tmp_path):
    # report carries a top-level provenance block with the four freshness fields
    p = _stdout_prov(_git_fixture(tmp_path))
    assert set(p) >= {"checkout_sha", "dirty", "behind_main", "origin_ref_age_h"}


def test_collect_dirty_false_on_clean(tmp_path):
    # a clean, current checkout → dirty false
    p = _stdout_prov(_git_fixture(tmp_path))
    assert p["dirty"] is False


def test_collect_behind_main_zero_when_current(tmp_path):
    # origin/main ref == HEAD → behind_main 0 (not "unknown")
    p = _stdout_prov(_git_fixture(tmp_path))
    assert p["behind_main"] == 0


def test_collect_dirty_true_on_measured_path(tmp_path):
    # modify a tracked MEASURED-allowlist file → dirty true (BC1)
    ws = _git_fixture(tmp_path)
    (ws.joinpath(*MEASURED_PATH)).write_text("workstations: {dev-primary: {}}\n# changed\n")
    p = _stdout_prov(ws)
    assert p["dirty"] is True


def test_collect_dirty_false_on_unrelated_edit(tmp_path):
    # edit a tracked file OUTSIDE the measured allowlist (.claude/state/*) → dirty FALSE (BC1)
    ws = _git_fixture(tmp_path)
    (ws / ".claude" / "state" / "harness-readiness-dev-primary.yaml").write_text(
        "overall: fail\npass_count: 99\n")        # tracked, but not a measured path
    p = _stdout_prov(ws)
    assert p["dirty"] is False


def test_collect_dirty_false_on_untracked_noise(tmp_path):
    # Untracked cruft (.DS_Store, __pycache__, swap files) inside a MEASURED dir must NOT
    # false-STALE a healthy machine — dirty reflects TRACKED changes only (--untracked-files=no).
    ws = _git_fixture(tmp_path)
    (ws / ".claude" / "skills" / ".DS_Store").write_text("\x00")          # untracked noise
    (ws / "scripts" / "readiness" / "__pycache__").mkdir(exist_ok=True)
    (ws / "scripts" / "readiness" / "__pycache__" / "x.pyc").write_text("x")
    p = _stdout_prov(ws)
    assert p["dirty"] is False


def test_collect_origin_ref_age_recorded(tmp_path):
    # origin_ref_age_h is a number (just-created ref → small, well under the 12h window)
    p = _stdout_prov(_git_fixture(tmp_path))
    assert isinstance(p["origin_ref_age_h"], (int, float))
    assert 0 <= p["origin_ref_age_h"] <= 12


def test_collect_fetch_head_freshness_requires_origin_main_sha_match(tmp_path):
    ws = _git_fixture(tmp_path)
    _git(ws, "commit", "-q", "--allow-empty", "-m", "advance local head")
    head_sha = subprocess.check_output(["git", "-C", str(ws), "rev-parse", "HEAD"], text=True).strip()
    common_dir = subprocess.check_output(
        ["git", "-C", str(ws), "rev-parse", "--git-common-dir"], text=True).strip()
    git_dir = Path(common_dir)
    if not git_dir.is_absolute():
        git_dir = ws / git_dir
    origin_ref = git_dir / "refs" / "remotes" / "origin" / "main"
    fetch_head = git_dir / "FETCH_HEAD"
    fetch_head.write_text(f"{head_sha}\t\tbranch 'main' of https://example.invalid/repo\n")
    stale_time = time.time() - (26 * 3600)
    os.utime(origin_ref, (stale_time, stale_time))

    p = _stdout_prov(ws)
    assert p["ahead_main"] == 1
    assert p["origin_ref_age_h"] >= 24


def test_collect_provenance_unknown_when_not_git(tmp_path):
    # the non-git fixture (no .git) → fail-closed unknowns, never a crash
    p = _stdout_prov(_fixture(tmp_path))
    assert p["checkout_sha"] == "unknown"
    assert p["behind_main"] == "unknown"
    assert p["origin_ref_age_h"] == "unknown"


def test_collect_ahead_main_recorded(tmp_path):
    # ahead_main is emitted; current-with-main fixture → 0 (not "unknown")
    p = _stdout_prov(_git_fixture(tmp_path))
    assert p["ahead_main"] == 0


def test_collect_ahead_main_counts_local_commits(tmp_path):
    # a local commit ahead of origin/main → ahead_main > 0 (the unpushed-checkout case)
    ws = _git_fixture(tmp_path)
    _git(ws, "commit", "-q", "--allow-empty", "-m", "local ahead")   # HEAD ahead, origin/main not moved
    p = _stdout_prov(ws)
    assert p["ahead_main"] == 1
    assert p["behind_main"] == 0


def test_collect_sha_excluded_from_hash(tmp_path):
    # A1: a checkout_sha change ALONE → NO rewrite. To change sha WITHOUT changing ahead/behind
    # (which ARE hashed), advance origin/main in lockstep with HEAD — i.e. a normal pull where
    # local and remote move together. Only checkout_sha differs → canonical payload identical.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    first_mtime = out.stat().st_mtime_ns
    _git(ws, "commit", "-q", "--allow-empty", "-m", "advance sha")
    _git(ws, "update-ref", "refs/remotes/origin/main", "HEAD")       # origin advances too → ahead=behind=0
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert out.stat().st_mtime_ns == first_mtime     # only sha changed → must not rewrite


def test_collect_dirty_change_forces_rewrite(tmp_path):
    # A1: a clean→dirty transition (same emitted dims) MUST rewrite, so the committed report
    # cannot keep a stale dirty:false that fools the matrix.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert "dirty: false" in out.read_text()
    (ws.joinpath(*MEASURED_PATH)).write_text("workstations: {}\n# now dirty\n")
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert "dirty: true" in out.read_text()          # transition was hashed → rewrite happened


def test_collect_dirty_no_self_trigger(tmp_path):
    # A3: the collector's OWN output (.claude/state/equality-*.yaml) must not make dirty true.
    # dirty is captured pre-write AND .claude/state is outside the measured allowlist.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert "dirty: false" in out.read_text()         # writing its own report didn't self-dirty


def test_collect_origin_ref_age_in_worktree(tmp_path):
    # Worktree-safety (#2851): refs/remotes/origin/main + FETCH_HEAD live in --git-common-dir,
    # NOT the per-worktree --git-dir. The collector must resolve the common dir, else every
    # worktree-based collection fail-closes to origin_ref_age_h=unknown → false STALE-CHECKOUT.
    main_ws = _git_fixture(tmp_path)
    wt = tmp_path / "wt"
    _git(main_ws, "worktree", "add", "-q", "--detach", str(wt))   # full checkout (committed .claude tree)
    p = _stdout_prov(wt)
    assert isinstance(p["origin_ref_age_h"], (int, float)) and not isinstance(p["origin_ref_age_h"], bool), p
    assert 0 <= p["origin_ref_age_h"] <= 12
    assert p["behind_main"] == 0          # worktree HEAD == origin/main → current, not unknown


def test_winabs_guard_classifies_windows_drive_paths():
    # #2816 W4 worktree-freshness fix (Windows): a linked-worktree --git-common-dir on Windows is
    # an absolute drive-letter path (C:/repo/.git or C:\repo\.git) that does NOT start with "/", so
    # the bare "!= /*" guard alone would treat it as RELATIVE and corrupt it (WS/C:/repo/.git) ->
    # FETCH_HEAD unfound -> origin_ref_age_h "unknown" -> matrix false-STALEs every worktree run on
    # Windows. The Linux-only test_collect_origin_ref_age_in_worktree above cannot reproduce this
    # (Linux common-dirs are relative or "/"-absolute). Bind this test to the REAL winabs pattern
    # extracted from the script (not a copy) so weakening the guard fails CI.
    src = SCRIPT.read_text()
    m = re.search(r"winabs='([^']*)'", src)
    assert m, "winabs guard missing from collect-equality.sh (#2816 W4 worktree-freshness fix)"
    winabs = m.group(1)

    def classify(gd: str) -> str:
        prog = (f"winabs={shlex.quote(winabs)}\n"
                'if [[ -n "$1" && "$1" != /* && ! "$1" =~ $winabs ]]; then echo relative; '
                'else echo absolute; fi')
        return subprocess.run(["bash", "-c", prog, "_", gd],
                              capture_output=True, text=True, timeout=30).stdout.strip()

    # Windows linked-worktree common-dir (forward AND back slash) must classify ABSOLUTE -> no join
    assert classify("C:/workspace-hub/.git") == "absolute"
    assert classify(r"C:\workspace-hub\.git") == "absolute"
    # POSIX absolute stays absolute; genuine relative paths still join to WS
    assert classify("/srv/repo/.git") == "absolute"
    assert classify(".git") == "relative"
    assert classify("worktrees/x/.git") == "relative"


def test_collect_origin_ref_age_refreshed_not_frozen(tmp_path):
    # origin_ref_age_h is HASHED (A1: only checkout_sha is excluded from the canonical payload),
    # so a stale freshness value can never be frozen into the committed report and fool the
    # matrix. Tamper the committed age to a huge stale value; the next run MUST rewrite it back.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert re.search(r"origin_ref_age_h: \d", out.read_text())          # live numeric value
    out.write_text(re.sub(r"origin_ref_age_h: .*", "origin_ref_age_h: 999", out.read_text()))
    subprocess.run(["bash", str(SCRIPT), "--machine", "dev-primary"], env=env, timeout=60, check=True)
    assert "origin_ref_age_h: 999" not in out.read_text()               # refreshed, not frozen
