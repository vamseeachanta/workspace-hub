"""TDD tests for #2801 collect-equality.sh — per-machine self-report collector.

Subprocess contract tests against a controlled WORKSPACE_HUB fixture root, so the
emitted YAML schema, label resolution, data-access normalization, secret-allowlist,
behavior typing, and commit-on-change idempotency are all verifiable without
depending on the host's real hardware.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "readiness" / "collect-equality.sh"


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
        env={"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin"},
        capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    return yaml.safe_load(res.stdout)


def test_collect_emits_valid_yaml(tmp_path):
    d = _run(_fixture(tmp_path))
    assert d["machine"] == "dev-primary"
    assert set(d["dimensions"]) >= {"compute", "data_access", "harness", "skills",
                                    "kanban", "memory", "behavior", "scheduler"}


def test_collect_machine_override(tmp_path):
    res = subprocess.run(
        ["bash", str(SCRIPT), "--stdout", "--machine", "licensed-win-2"],
        env={"WORKSPACE_HUB": str(_fixture(tmp_path)), "PATH": "/usr/bin:/bin:/usr/local/bin"},
        capture_output=True, text=True, timeout=60)
    assert yaml.safe_load(res.stdout)["machine"] == "licensed-win-2"


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
        env={"WORKSPACE_HUB": str(_fixture(tmp_path)), "PATH": "/usr/bin:/bin:/usr/local/bin"},
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
