from __future__ import annotations

import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import yaml


def run_sync(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "scripts/_core/sync-agent-configs.sh", *args],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
        env=env,
    )


def path_without_uv() -> str:
    entries: list[str] = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        if shutil.which("uv", path=entry) is None:
            entries.append(entry)
    return os.pathsep.join(entries)


def test_sync_dry_run_resolves_tier1_repo_root_token():
    result = run_sync("--machine", "dev-primary", "--dry-run")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "__TIER1_REPO_ROOT__" not in result.stdout
    assert "unresolved token" not in result.stderr.lower()


def test_sync_dry_run_handles_machine_with_no_present_sibling_skill_dirs():
    result = run_sync("--machine", "licensed-win-1", "--dry-run")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "unresolved token" not in (result.stderr + result.stdout).lower()
    assert "could not find expected ':'" not in (result.stderr + result.stdout).lower()


def test_sync_dry_run_fails_closed_when_uv_is_absent(tmp_path):
    env = os.environ.copy()
    env["PATH"] = path_without_uv()
    env["HOME"] = str(tmp_path)
    assert shutil.which("uv", path=env["PATH"]) is None

    result = run_sync("--machine", "dev-primary", "--dry-run", env=env)

    assert result.returncode != 0
    assert "uv is required for Codex TOML sync" in result.stderr
    assert list(tmp_path.iterdir()) == []


def test_sync_dry_run_falls_back_to_uv_when_python3_lacks_yaml(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python3"
    fake_python.write_text("#!/usr/bin/env bash\necho 'No module named yaml' >&2\nexit 1\n")
    fake_python.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    assert shutil.which("python3", path=env["PATH"]) == str(fake_python)
    assert shutil.which("uv", path=env["PATH"]) is not None

    result = run_sync("--machine", "dev-primary", "--dry-run", env=env)

    assert result.returncode == 0, result.stderr + result.stdout
    assert "unresolved token" not in (result.stderr + result.stdout).lower()


def test_sync_uv_fallback_installs_pyyaml_for_stdin_rendering():
    script = (Path(__file__).resolve().parents[2] / "scripts/_core/sync-agent-configs.sh").read_text()
    assert "uv run --with pyyaml --no-project python \"$@\"" in script


def test_render_hermes_template_preserves_template_comments():
    script = (Path(__file__).resolve().parents[2] / "scripts/_core/sync-agent-configs.sh").read_text()
    render_body = script.split("render_hermes_template()", 1)[1].split("validate_json_file()", 1)[0]
    assert "yaml.safe_dump" not in render_body
    assert "output_path.write_text(rendered)" in render_body


def test_render_hermes_template_quotes_registry_skill_paths_as_yaml_scalars():
    script = (Path(__file__).resolve().parents[2] / "scripts/_core/sync-agent-configs.sh").read_text()
    assert "repo_skill_dirs.append(f\"- {json.dumps(str(path))}\")" in script


def test_sync_rejects_unknown_machine():
    result = run_sync("--machine", "definitely-not-a-machine", "--dry-run")
    assert result.returncode != 0
    assert "unknown machine" in (result.stderr + result.stdout).lower()


def test_sync_accepts_hostname_alias_machine_identifier():
    result = run_sync("--machine", "ace-linux-1", "--dry-run")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "unknown machine" not in (result.stderr + result.stdout).lower()


def make_harness_only_workspace(tmp_path: Path, canonical: str) -> tuple[Path, Path, Path]:
    repo_root = Path(__file__).resolve().parents[2]
    ws_root = tmp_path / "ws-hub"
    home_root = tmp_path / "home"
    hostname = subprocess.check_output(["hostname", "-s"], text=True).strip()

    for rel in (
        "scripts/_core",
        "scripts/readiness",
        "config/agents/claude",
        "config/agents/codex",
        "config/agents/gemini",
        "config/agents/hermes",
    ):
        (ws_root / rel).mkdir(parents=True, exist_ok=True)
    (home_root / ".codex").mkdir(parents=True)
    shutil.copy(repo_root / "scripts/_core/sync-agent-configs.sh", ws_root / "scripts/_core/sync-agent-configs.sh")
    (ws_root / "scripts/readiness/harness-config.yaml").write_text(
        f"workstations:\n  {hostname}:\n    ws_hub_path: {ws_root}\n"
    )
    (ws_root / "config/agents/claude/settings.json").write_text('{"statusLine": {"type": "command"}}\n')
    (ws_root / "config/agents/codex/config.toml").write_text(canonical)
    (ws_root / "config/agents/gemini/settings.json").write_text(
        '{"security": {"auth": {"selectedType": "oauth-personal"}}}\n'
    )
    (ws_root / "config/agents/hermes/config.yaml.template").write_text(
        "model:\n  default: gpt-5.5\nskills:\n  external_dirs:\n    - __WS_HUB_PATH__/.claude/skills\n"
    )
    (ws_root / "config/agents/hermes/SOUL.md").write_text("# Soul\n")
    local_codex = home_root / ".codex/config.toml"
    local_codex.write_text('model = "legacy-local-model"\n')
    return ws_root, home_root, local_codex


def test_sync_rejects_legacy_model_only_canonical_atomically(tmp_path):
    ws_root, home_root, local_codex = make_harness_only_workspace(
        tmp_path, 'model = "gpt-5.5"\n'
    )
    before = local_codex.read_bytes()

    env = os.environ.copy()
    env["HOME"] = str(home_root)
    result = subprocess.run(
        ["bash", str(ws_root / "scripts/_core/sync-agent-configs.sh")],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
        env=env,
    )

    assert result.returncode != 0
    assert "canonical Codex config does not match the owned-key contract" in result.stderr
    assert local_codex.read_bytes() == before
    assert not (home_root / ".hermes/config.yaml").exists()


def test_sync_preserves_harness_only_fallback_and_renders_hermes(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    canonical = (repo_root / "config/agents/codex/config.toml").read_text()
    ws_root, home_root, local_codex = make_harness_only_workspace(tmp_path, canonical)
    env = os.environ.copy()
    env["HOME"] = str(home_root)

    result = subprocess.run(
        ["bash", str(ws_root / "scripts/_core/sync-agent-configs.sh")],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    with local_codex.open("rb") as fh:
        codex = tomllib.load(fh)
    assert codex["model"] == "legacy-local-model"
    assert codex["tui"]["resume_cwd"] == "session"
    hermes = yaml.safe_load((home_root / ".hermes/config.yaml").read_text())
    assert f"{ws_root}/.claude/skills" in hermes["skills"]["external_dirs"]
