from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "blender" / "verify-blender-baseline.sh"
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "blender" / "smoke-render.py"
WORKFLOW_DOC = REPO_ROOT / "docs" / "engineering" / "portability" / "blender-headless-baseline-workflow.md"
MANIFEST_DOC = REPO_ROOT / "examples" / "blender" / "cube-render" / "README.md"
CHECKLIST_DOC = REPO_ROOT / "docs" / "engineering" / "portability" / "ENGINEERING_DELIVERY_CHECKLIST.md"
DOCS_INDEX = REPO_ROOT / "docs" / "README.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"
BLENDER_SKILL = REPO_ROOT / ".claude" / "skills" / "engineering" / "cad" / "blender" / "SKILL.md"

REQUIRED_MANIFEST_HEADINGS = [
    "# Blender cube-render smoke manifest",
    "## Overview",
    "## Prerequisites",
    "## Commands",
    "## Expected Outputs",
    "## Failure Modes",
]


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


def _write_fake_blender(path: Path, *, metadata: str | None = None, exit_code: int = 0) -> None:
    metadata_block = metadata or """
scene_name: cube-render
frame: 1
render_engine: BLENDER_EEVEE
resolution:
  width: 320
  height: 240
image:
  format: PNG
  color_mode: RGBA
  output_file: __OUTPUT__
  file_size_bytes: __SIZE__
objects:
  - name: Smoke_Cube
    type: MESH
camera: Smoke_Camera
"""
    path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [[ \"${1:-}\" == \"--version\" ]]; then\n"
        "  printf 'Blender 5.0.1\\n'\n"
        "  exit 0\n"
        "fi\n"
        "out=''\n"
        "meta=''\n"
        "while [[ $# -gt 0 ]]; do\n"
        "  case \"$1\" in\n"
        "    --output) out=\"$2\"; shift 2 ;;\n"
        "    --metadata) meta=\"$2\"; shift 2 ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "mkdir -p \"$(dirname \"$out\")\" \"$(dirname \"$meta\")\"\n"
        "printf '\\211PNG\\r\\n\\032\\nsmoke-render' > \"$out\"\n"
        "size=$(wc -c < \"$out\" | tr -d ' ')\n"
        "cat > \"$meta\" <<'YAML'\n"
        f"{metadata_block}\n"
        "YAML\n"
        "sed -i \"s#__OUTPUT__#$out#g; s#__SIZE__#$size#g\" \"$meta\"\n"
        f"exit {exit_code}\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_verify_script_fails_when_blender_missing(tmp_path: Path) -> None:
    verdict_path = tmp_path / "missing.yaml"

    result = _run_verify(
        "--verdict",
        str(verdict_path),
        env_overrides={"BLENDER_BIN": str(tmp_path / "does-not-exist")},
    )

    assert result.returncode != 0
    assert "Blender binary not found" in result.stderr
    assert verdict_path.exists(), "failure verdict should still be written"
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "FAIL"
    assert verdict["error_summary"] == "missing-blender"
    assert verdict["smoke_render"]["status"] == "NOT_RUN"


def test_verify_script_succeeds_and_validates_render_metadata(tmp_path: Path) -> None:
    fake_blender = tmp_path / "blender"
    _write_fake_blender(fake_blender)
    verdict_path = tmp_path / "verdict.yaml"

    result = _run_verify(
        "--verdict",
        str(verdict_path),
        "--output-dir",
        str(tmp_path / "renders"),
        env_overrides={"BLENDER_BIN": str(fake_blender), "BLENDER_HOSTNAME": "dev-secondary"},
    )

    assert result.returncode == 0, result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert set(verdict) == {
        "generated_at",
        "machine",
        "blender_path",
        "version",
        "canonical_invocation",
        "overall_verdict",
        "smoke_render",
        "output_validation",
    }
    assert verdict["machine"] == "dev-secondary"
    assert verdict["version"] == "5.0.1"
    assert verdict["overall_verdict"] == "PASS"
    assert verdict["canonical_invocation"] == "blender -b --factory-startup --python scripts/blender/smoke-render.py -- --output <output> --metadata <metadata>"
    assert verdict["smoke_render"]["status"] == "PASS"
    assert verdict["smoke_render"]["scene_name"] == "cube-render"
    assert verdict["smoke_render"]["render_engine"] == "BLENDER_EEVEE"
    assert verdict["smoke_render"]["resolution"] == {"width": 320, "height": 240}
    assert verdict["smoke_render"]["frame"] == 1
    assert verdict["smoke_render"]["file_size_bytes"] > 8
    assert verdict["output_validation"] == {
        "metadata_schema_valid": True,
        "png_signature_valid": True,
        "expected_scene_name": "cube-render",
        "expected_output_name": "cube-render_frame-0001.png",
    }


def test_verify_script_rejects_malformed_render_metadata(tmp_path: Path) -> None:
    fake_blender = tmp_path / "blender"
    _write_fake_blender(
        fake_blender,
        metadata="""
scene_name: wrong-scene
frame: 2
render_engine: CYCLES
resolution:
  width: 640
  height: 480
image:
  format: PNG
  output_file: __OUTPUT__
  file_size_bytes: __SIZE__
objects: []
camera: null
""",
    )
    verdict_path = tmp_path / "bad-metadata.yaml"

    result = _run_verify(
        "--verdict",
        str(verdict_path),
        "--output-dir",
        str(tmp_path / "renders"),
        env_overrides={"BLENDER_BIN": str(fake_blender)},
    )

    assert result.returncode != 0
    assert "metadata validation failed" in result.stderr.lower()
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "FAIL"
    assert verdict["error_summary"] == "metadata-invalid"
    assert verdict["smoke_render"]["status"] == "FAIL"
    assert verdict["output_validation"]["metadata_schema_valid"] is False


def test_verify_script_emits_failure_verdict_on_render_error(tmp_path: Path) -> None:
    fake_blender = tmp_path / "blender"
    _write_fake_blender(fake_blender, exit_code=7)
    verdict_path = tmp_path / "render-error.yaml"

    result = _run_verify(
        "--verdict",
        str(verdict_path),
        "--output-dir",
        str(tmp_path / "renders"),
        env_overrides={"BLENDER_BIN": str(fake_blender)},
    )

    assert result.returncode != 0
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "FAIL"
    assert verdict["error_summary"] == "render-failure"
    assert verdict["smoke_render"]["status"] == "FAIL"


def test_manifest_instructions_do_not_commit_render_outputs() -> None:
    assert MANIFEST_DOC.exists()
    text = MANIFEST_DOC.read_text()
    for heading in REQUIRED_MANIFEST_HEADINGS:
        assert heading in text
    committed_images = [
        path
        for path in MANIFEST_DOC.parent.rglob("*")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".blend"}
    ]
    assert committed_images == []


def test_workflow_doc_covers_traceable_issue_requirements() -> None:
    assert WORKFLOW_DOC.exists()
    text = WORKFLOW_DOC.read_text()
    for required in [
        "blender -b --factory-startup --python scripts/blender/smoke-render.py",
        "Blender 5.0.1",
        "dev-secondary",
        "cube-render_frame-0001.png",
        "logs/engineering/blender-baseline/latest-verdict.yaml",
        "metadata_schema_valid",
        "CLI-Anything",
        "convenience-only",
        "Requirement traceability",
        "Failure modes",
    ]:
        assert required in text

    assert "blender-headless-baseline-workflow.md" in CHECKLIST_DOC.read_text()
    assert "blender-headless-baseline-workflow.md" in DOCS_INDEX.read_text()


def test_pytest_harness_and_skill_cover_blender_contract() -> None:
    assert VERIFY_SCRIPT.exists()
    assert SMOKE_SCRIPT.exists()
    assert "blender" in PYPROJECT.read_text()
    assert "blender-headless baseline package" in BLENDER_SKILL.read_text()
    contents = Path(__file__).read_text()
    assert "@pytest.mark.blender" in contents
    assert "test_verify_script_fails_when_blender_missing" in contents
    assert "test_verify_script_rejects_malformed_render_metadata" in contents


@pytest.mark.blender
def test_smoke_render_script_produces_png_on_real_host(tmp_path: Path) -> None:
    blender_bin = os.environ.get("BLENDER_BIN") or "blender"
    if subprocess.run(["bash", "-lc", f"command -v {blender_bin!r}"], capture_output=True).returncode != 0:
        pytest.skip("Blender runtime not available on this host")

    verdict_path = tmp_path / "real-host.yaml"
    result = _run_verify("--verdict", str(verdict_path), "--output-dir", str(tmp_path / "renders"))

    assert result.returncode == 0, result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "PASS"
    assert verdict["version"]
    assert verdict["smoke_render"]["scene_name"] == "cube-render"
    assert verdict["smoke_render"]["file_size_bytes"] > 8
