"""Fixture: relative path resolution only. MUST NOT trigger check-no-abs-paths."""
from pathlib import Path
import subprocess

REPO_ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
config = REPO_ROOT / "config" / "app.yaml"
