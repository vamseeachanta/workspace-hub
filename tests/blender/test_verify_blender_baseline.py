from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "blender" / "verify-blender-baseline.sh"
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "blender" / "smoke-render.py"
WORKFLOW_DOC = REPO_ROOT / "docs" / "engineering" / "portability" / "blender-headless-baseline-workflow.md"
MANIFEST_DOC = REPO_ROOT / "examples" / "blender" / "cube-render" / "README.md"
CHECKLIST_DOC = REPO_ROOT / "docs" / "engineering" / "portability" / "ENGINEERING_DELIVERY_CHECKLIST.md"


def _run_verify(*args: str, env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        ["bash", str(VERIFY_SCRIPT), *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _fake_blender(path: Path, *, version: str = "Blender 4.1.1", fail_render: bool = False) -> Path:
    path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [[ \"${1:-}\" == \"--version\" ]]; then\n"
        f"  printf '%s\\n' '{version}'\n"
        "  exit 0\n"
        "fi\n"
        "if [[ \"${1:-}\" == \"-b\" && \"${2:-}\" == \"--python\" ]]; then\n"
        "  shift 3\n"
        "  output=''\n"
        "  while [[ $# -gt 0 ]]; do\n"
        "    case \"$1\" in\n"
        "      --output) output=\"$2\"; shift 2 ;;\n"
        "      *) shift ;;\n"
        "    esac\n"
        "  done\n"
        f"  {'echo render failed >&2; exit 9' if fail_render else 'mkdir -p \"$(dirname \"$output\")\"; printf fakepng > \"$output\"; exit 0'}\n"
        "fi\n"
        "echo unexpected blender invocation: $* >&2\n"
        "exit 64\n"
    )
    path.chmod(0o755)
    return path


def test_verify_script_writes_passing_verdict_with_injected_blender(tmp_path: Path) -> None:
    verdict_path = tmp_path / "blender-verdict.yaml"
    fake_bin = _fake_blender(tmp_path / "blender")

    result = _run_verify("--verdict", str(verdict_path), env_overrides={"BLENDER_BIN": str(fake_bin), "BLENDER_HOSTNAME": "dev-secondary"})

    assert result.returncode == 0, result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "PASS"
    assert verdict["tool"] == "blender"
    assert verdict["version"] == "4.1.1"
    assert verdict["smoke_case"] == "cube-render"
    assert verdict["render_output"].endswith("smoke-render.png")
    assert Path(verdict["render_output"]).exists()


def test_verify_script_fails_with_machine_readable_verdict_when_blender_missing(tmp_path: Path) -> None:
    verdict_path = tmp_path / "missing.yaml"

    result = _run_verify("--verdict", str(verdict_path), env_overrides={"BLENDER_BIN": str(tmp_path / "does-not-exist")})

    assert result.returncode != 0
    assert "Blender binary not found" in result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "FAIL"
    assert verdict["error_summary"] == "missing-blender"
    assert verdict["tool"] == "blender"


def test_verify_script_records_render_failure(tmp_path: Path) -> None:
    verdict_path = tmp_path / "render-fail.yaml"
    fake_bin = _fake_blender(tmp_path / "blender", fail_render=True)

    result = _run_verify("--verdict", str(verdict_path), env_overrides={"BLENDER_BIN": str(fake_bin)})

    assert result.returncode != 0
    assert "render failed" in result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "FAIL"
    assert verdict["error_summary"] == "render-failure"
    assert verdict["version"] == "4.1.1"


def test_repo_tracks_smoke_script_manifest_and_workflow_doc() -> None:
    assert SMOKE_SCRIPT.exists()
    smoke_text = SMOKE_SCRIPT.read_text()
    assert "--output" in smoke_text
    assert "argv[0] == \"--\"" in smoke_text
    manifest = MANIFEST_DOC.read_text()
    assert "# Blender cube-render smoke manifest" in manifest
    assert "blender -b --python scripts/blender/smoke-render.py" in manifest
    workflow = WORKFLOW_DOC.read_text()
    assert "Blender headless baseline workflow" in workflow
    assert "dev-secondary" in workflow
    assert "latest-verdict.yaml" in workflow
    assert "<scene-name>_frame-<NNNN>.png" in workflow
    assert "CLI-Anything" in workflow
    assert "convenience-only" in workflow


def test_engineering_checklist_references_blender_baseline_bundle() -> None:
    text = CHECKLIST_DOC.read_text()
    assert "blender-headless-baseline-workflow.md" in text
    assert "scripts/blender/verify-blender-baseline.sh" in text
