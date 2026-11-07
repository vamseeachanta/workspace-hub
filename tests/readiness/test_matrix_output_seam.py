"""Builder path selection is isolated from real user state and repository output."""
import importlib.util

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_builder_honors_generation_and_publication_paths(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("matrix_seam", ROOT / "scripts/readiness/build-equality-matrix.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.delenv("EQ_STATE_DIR", raising=False)
    monkeypatch.delenv("EQ_REPORT_DIR", raising=False)
    state, reports = builder.resolve_paths([])
    assert state == tmp_path / "state/workspace-hub/equality"
    assert reports == state / "reports"
    monkeypatch.setenv("EQ_STATE_DIR", str(tmp_path / "evidence"))
    monkeypatch.setenv("EQ_REPORT_DIR", str(tmp_path / "render"))
    assert builder.resolve_paths([]) == (tmp_path / "evidence", tmp_path / "render")
    assert builder.resolve_paths(["--state-dir", str(tmp_path / "publish-state"),
                                  "--out-dir", str(tmp_path / "publish-render")]) == (
                                      tmp_path / "publish-state", tmp_path / "publish-render")


def test_standalone_builder_writes_only_to_selected_output(tmp_path):
    import os
    import shutil
    import subprocess
    import sys

    repo = tmp_path / "fixture"
    scripts = repo / "scripts/readiness"
    scripts.mkdir(parents=True)
    for name in ("build-equality-matrix.py", "equality_actions.py"):
        shutil.copy2(ROOT / "scripts/readiness" / name, scripts / name)
    (scripts / "harness-config.yaml").write_text("workstations: {}\n", encoding="utf-8", newline="\n")
    state, reports = tmp_path / "evidence", tmp_path / "render"
    state.mkdir()
    env = {k: v for k, v in os.environ.items()
           if k not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"}}
    env["XDG_STATE_HOME"] = str(tmp_path / "default-state")
    env.pop("EQ_REPORT_DIR", None)
    env.pop("EQ_STATE_DIR", None)
    cmd = [sys.executable, str(scripts / "build-equality-matrix.py")]
    subprocess.run(cmd, cwd=repo, env=env, check=True, capture_output=True)
    default = tmp_path / "default-state/workspace-hub/equality/reports"
    assert len(list(default.glob("*machine-equality-matrix.html"))) == 2
    subprocess.run(cmd + ["--state-dir", str(state), "--out-dir", str(reports)],
                   cwd=repo, env=env, check=True, capture_output=True)
    assert len(list(reports.glob("*machine-equality-matrix.html"))) == 2
    assert not (repo / "docs").exists()


@pytest.mark.parametrize("mode", ["default", "environment", "explicit"])
def test_nonempty_input_layers(tmp_path, monkeypatch, mode):
    spec = importlib.util.spec_from_file_location(
        "matrix_inputs", ROOT / "scripts/readiness/build-equality-matrix.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    repo = tmp_path / "repository"
    tracked = repo / ".claude/state"
    tracked.mkdir(parents=True)
    external = tmp_path / "external"
    external.mkdir()
    for name, payload in (("local", "origin: repository"), ("peer", "origin: peer")):
        (tracked / f"equality-{name}.yaml").write_text(
            payload + "\n", encoding="utf-8", newline="\n")
    (external / "equality-local.yaml").write_text(
        "origin: override\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(builder, "REPO", repo)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.delenv("EQ_STATE_DIR", raising=False)
    argv = []
    if mode == "default":
        external = tmp_path / "state/workspace-hub/equality"
        external.mkdir(parents=True)
        (external / "equality-local.yaml").write_text(
            "origin: override\n", encoding="utf-8", newline="\n")
    elif mode == "environment":
        monkeypatch.setenv("EQ_STATE_DIR", str(external))
    else:
        monkeypatch.setenv("EQ_STATE_DIR", str(tmp_path / "ignored"))
        argv = [f"--state-dir={external}"]
    reports = builder.load_reports(builder.resolve_input_paths(argv))
    assert reports["local"] == {"origin": "override"}
    if mode == "explicit":
        assert "peer" not in reports
    else:
        assert reports["peer"] == {"origin": "peer"}
