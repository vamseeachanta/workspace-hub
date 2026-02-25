"""Integration tests: validate real YAML state files from the workspace."""

from pathlib import Path

import pytest

from coordination.schemas import validate_file, load_and_validate


WORKSPACE_ROOT = Path("/mnt/github/workspace-hub")

REAL_FILES = {
    "reflect-state": WORKSPACE_ROOT / ".claude/state/reflect-state.yaml",
    "learnings": WORKSPACE_ROOT / ".claude/state/memory/patterns/learnings.yaml",
    "work-queue": WORKSPACE_ROOT / ".claude/work-queue/state.yaml",
    "cc-user-insights": WORKSPACE_ROOT / ".claude/state/cc-user-insights.yaml",
}


@pytest.mark.integration
class TestValidateRealFiles:
    @pytest.mark.parametrize("name,path", list(REAL_FILES.items()))
    def test_real_file_validates(self, name, path):
        if not path.exists():
            pytest.skip(f"{path} does not exist on this machine")

        errors = validate_file(path)
        assert errors == [], f"{name} validation errors: {errors}"

    @pytest.mark.parametrize("name,path", list(REAL_FILES.items()))
    def test_real_file_loads(self, name, path):
        if not path.exists():
            pytest.skip(f"{path} does not exist on this machine")

        model = load_and_validate(path)
        assert model is not None
