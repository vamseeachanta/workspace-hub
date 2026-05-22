from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC_SCRIPT = REPO_ROOT / "scripts" / "_core" / "sync-agent-configs.sh"


def _function_body(script: str, name: str) -> str:
    marker = f"{name}() {{"
    start = script.index(marker)
    next_function = script.find("\n}\n\n", start)
    assert next_function != -1
    return script[start: next_function + 3]


def test_yaml_validation_uses_pyyaml_aware_launcher_and_fails_closed() -> None:
    script = SYNC_SCRIPT.read_text()
    body = _function_body(script, "validate_yaml_file")

    assert "run_config_python - \"$target\"" in body
    assert "python3 - \"$target\"" not in body
    assert "uv run --no-project python - \"$target\"" not in body
    assert "YAML validation failed" in body
    assert "return 1" in body
    assert "Skipping YAML validation" not in body


def test_hermes_yaml_merge_uses_single_pyyaml_aware_launcher() -> None:
    script = SYNC_SCRIPT.read_text()
    start = script.index("sync_hermes_yaml_config() {")
    end = script.index("\nsync_hermes_plain_file() {", start)
    body = script[start:end]

    assert "run_config_python - \"$target\" \"$resolved_template\" \"$merged\"" in body
    assert "python3 - \"$target\" \"$resolved_template\" \"$merged\"" not in body
    assert "uv run --no-project python - \"$target\" \"$resolved_template\" \"$merged\"" not in body
    assert "rm -f \"$resolved_template\" \"$merged\"" in body
    assert "return 1" in body
