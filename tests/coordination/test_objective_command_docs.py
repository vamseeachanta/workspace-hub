from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_objective_slash_command_points_to_dry_run_script() -> None:
    text = (REPO_ROOT / ".claude" / "commands" / "objective.md").read_text(
        encoding="utf-8"
    )

    assert "/objective <issue#>" in text
    assert "uv run --no-project python -m scripts.coordination.objective" in text
    assert "--dry-run" in text
    assert "PARALLEL_FIRST_EXECUTION.md" in text
