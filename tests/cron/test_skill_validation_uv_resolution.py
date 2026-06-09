"""Cron-like uv resolution tests for skill validation (#2986)."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "skills" / "validate-skills.sh"


def _write_skill(root: Path) -> Path:
    skill_dir = root / "sample"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\n"
        "name: sample\n"
        "description: Valid sample skill.\n"
        "---\n"
        "\n"
        "# Sample\n",
        encoding="utf-8",
    )
    return root


def _write_fake_uv(path: Path, *, fail_version: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    version_exit = "1" if fail_version else "0"
    path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [[ \"${1:-}\" == \"--version\" ]]; then\n"
        "  echo 'uv 0.0.0-test'\n"
        f"  exit {version_exit}\n"
        "fi\n"
        "printf 'argv=%s\\n' \"$*\" >> \"${FAKE_UV_LOG:?}\"\n"
        "printf 'UV_CACHE_DIR=%s\\n' \"${UV_CACHE_DIR:-}\" >> \"${FAKE_UV_LOG:?}\"\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_validate_skills_resolves_uv_from_home_local_under_minimal_path(
    tmp_path: Path,
) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    home = tmp_path / "home"
    fake_uv = _write_fake_uv(home / ".local" / "bin" / "uv")
    log = tmp_path / "fake-uv.log"
    cache = tmp_path / "uv-cache"
    env = {
        "HOME": str(home),
        "PATH": "/usr/bin:/bin",
        "FAKE_UV_LOG": str(log),
        "UV_CACHE_DIR": str(cache),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert log.exists()
    assert str(fake_uv) not in result.stderr
    assert "run --no-project --with pyyaml python" in log.read_text(encoding="utf-8")


def test_validate_skills_honors_uv_bin_override(tmp_path: Path) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    fake_uv = _write_fake_uv(tmp_path / "bin" / "explicit-uv")
    log = tmp_path / "fake-uv.log"
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "FAKE_UV_LOG": str(log),
        "UV_BIN": str(fake_uv),
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "run --no-project --with pyyaml python" in log.read_text(encoding="utf-8")


def test_validate_skills_rejects_non_executable_uv_bin(tmp_path: Path) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    uv_bin = tmp_path / "bin" / "uv"
    uv_bin.parent.mkdir(parents=True)
    uv_bin.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "UV_BIN": str(uv_bin),
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "UV_BIN" in result.stderr
    assert "not executable" in result.stderr


def test_validate_skills_rejects_executable_but_failing_uv_bin(tmp_path: Path) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    fake_uv = _write_fake_uv(tmp_path / "bin" / "uv", fail_version=True)
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "UV_BIN": str(fake_uv),
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "UV_BIN" in result.stderr
    assert "failed validation" in result.stderr


def test_validate_skills_rejects_failing_path_uv_and_uses_home_candidate(
    tmp_path: Path,
) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    path_dir = tmp_path / "path-bin"
    _write_fake_uv(path_dir / "uv", fail_version=True)
    home = tmp_path / "home"
    _write_fake_uv(home / ".local" / "bin" / "uv")
    log = tmp_path / "fake-uv.log"
    env = {
        "HOME": str(home),
        "PATH": f"{path_dir}:/usr/bin:/bin",
        "FAKE_UV_LOG": str(log),
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "PATH uv" in result.stderr
    assert "failed validation" in result.stderr
    assert log.exists()


def test_validate_skills_rejects_failing_home_candidate(tmp_path: Path) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    home = tmp_path / "home"
    _write_fake_uv(home / ".local" / "bin" / "uv", fail_version=True)
    env = {
        "HOME": str(home),
        "PATH": "/usr/bin:/bin",
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "common path" in result.stderr
    assert "failed validation" in result.stderr
    assert "UV_BIN=/path/to/uv" in result.stderr


def test_uv_resolver_is_source_safe_when_uv_missing(tmp_path: Path) -> None:
    resolver = REPO_ROOT / "scripts" / "lib" / "uv-resolver.sh"
    env = {"PATH": "/usr/bin:/bin"}

    result = subprocess.run(
        ["bash", "-c", f"source {resolver}; echo after"],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert result.stdout.strip() == "after"


def test_uv_resolver_source_does_not_enable_errexit(tmp_path: Path) -> None:
    resolver = REPO_ROOT / "scripts" / "lib" / "uv-resolver.sh"
    env = {"PATH": "/usr/bin:/bin"}

    result = subprocess.run(
        ["bash", "-c", f"set +e; source {resolver}; false; echo after"],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert result.stdout.strip() == "after"


def test_validate_skills_default_root_is_repo_relative_from_foreign_cwd(
    tmp_path: Path,
) -> None:
    fake_uv = _write_fake_uv(tmp_path / "bin" / "uv")
    log = tmp_path / "fake-uv.log"
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "FAKE_UV_LOG": str(log),
        "UV_BIN": str(fake_uv),
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR)],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Skills root not found" not in result.stderr
    assert str(REPO_ROOT / ".claude" / "skills") in log.read_text(encoding="utf-8")


def test_validate_skills_relative_root_arg_is_repo_relative_from_foreign_cwd(
    tmp_path: Path,
) -> None:
    fake_uv = _write_fake_uv(tmp_path / "bin" / "uv")
    log = tmp_path / "fake-uv.log"
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "FAKE_UV_LOG": str(log),
        "UV_BIN": str(fake_uv),
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), ".claude/skills"],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Skills root not found" not in result.stderr
    assert str(REPO_ROOT / ".claude" / "skills") in log.read_text(encoding="utf-8")


def test_validate_skills_missing_uv_diagnostic_is_actionable(tmp_path: Path) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    env = {
        "PATH": "/usr/bin:/bin",
        "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "UV_BIN" in result.stderr
    assert "$HOME/.local/bin/uv" in result.stderr
    assert "$HOME/.cargo/bin/uv" in result.stderr
    assert "/usr/local/bin/uv" in result.stderr
    assert "HOME-derived paths were skipped" in result.stderr
    assert "UV_BIN=/path/to/uv" in result.stderr


def test_validate_skills_honors_explicit_uv_cache_dir(tmp_path: Path) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    fake_uv = _write_fake_uv(tmp_path / "bin" / "uv")
    log = tmp_path / "fake-uv.log"
    cache = tmp_path / "explicit-cache"
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "FAKE_UV_LOG": str(log),
        "UV_BIN": str(fake_uv),
        "UV_CACHE_DIR": str(cache),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert f"UV_CACHE_DIR={cache}" in log.read_text(encoding="utf-8")


def test_validate_skills_derives_uv_cache_default(tmp_path: Path) -> None:
    skills_root = _write_skill(tmp_path / "skills")
    fake_uv = _write_fake_uv(tmp_path / "bin" / "uv")
    log = tmp_path / "fake-uv.log"
    env = {
        "HOME": str(tmp_path / "home"),
        "PATH": "/usr/bin:/bin",
        "FAKE_UV_LOG": str(log),
        "UV_BIN": str(fake_uv),
    }

    result = subprocess.run(
        ["bash", str(VALIDATOR), str(skills_root)],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    expected = REPO_ROOT / ".claude" / "state" / "uv-cache"
    assert f"UV_CACHE_DIR={expected}" in log.read_text(encoding="utf-8")


def test_skills_validation_workflow_includes_new_paths() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "skills-validation.yml").read_text(
        encoding="utf-8"
    )

    assert workflow.count("scripts/lib/uv-resolver.sh") == 2
    assert workflow.count("scripts/lib/uv-env.sh") == 2
    assert workflow.count("tests/cron/test_skill_validation_uv_resolution.py") >= 3
