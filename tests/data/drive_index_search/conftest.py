import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_DIR = REPO_ROOT / "scripts" / "data" / "drive-index-search"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(PACKAGE_DIR))


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def fixture_registry(fixtures_dir: Path) -> Path:
    return fixtures_dir / "test-registry.yml"


@pytest.fixture(autouse=True)
def forbid_live_mount_tests(monkeypatch):
    real_exists = os.path.exists

    def guarded_exists(path):
        text = os.fspath(path)
        if text.startswith(("/mnt/ace", "/mnt/dde")):  # abs-path-allowed
            raise AssertionError(f"test attempted to touch live mount: {text}")
        return real_exists(path)

    monkeypatch.setattr(os.path, "exists", guarded_exists)
