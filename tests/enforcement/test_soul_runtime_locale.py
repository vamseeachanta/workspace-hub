"""Locale-independent ordering for the generated Codex skill index."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]


def bash_executable() -> str:
    local = os.environ.get("LOCALAPPDATA")
    candidates = [
        Path(local) / "Programs/Git/usr/bin/bash.exe" if local else None,
        Path(shutil.which("bash") or ""),
    ]
    found = next((str(path) for path in candidates if path and path.is_file()), None)
    assert found, "Bash capability unavailable"
    return found


@pytest.mark.parametrize("inherited_locale", ["C.UTF-8", "en_US.UTF-8"])
def test_skill_index_sort_pins_c_locale(tmp_path: Path, inherited_locale: str) -> None:
    repo = tmp_path / "repo"
    skills = repo / ".claude/skills"
    for family in ("business", "business-finance", "data", "data-science"):
        (skills / family / "nested").mkdir(parents=True)
        (skills / family / "nested/SKILL.md").write_text("---\n", encoding="utf-8")
    (repo / ".claude/rules").mkdir(parents=True)
    for rule in ("coding-style.md", "patterns.md"):
        (repo / ".claude/rules" / rule).write_text(f"{rule}\n", encoding="utf-8")

    marker = tmp_path / f"sort-{inherited_locale}.txt"
    output = tmp_path / f"runtime-{inherited_locale}.md"
    env = os.environ.copy()
    env.update(
        LC_ALL=inherited_locale,
        SORT_MARKER=marker.as_posix(),
    )
    command = (
        "PATH=/usr/bin:/bin; export PATH; "
        "sort() { printf '%s\\n' \"${LC_ALL-UNSET}\" >> \"${SORT_MARKER}\"; "
        "[[ \"${LC_ALL-}\" == C ]] || return 91; /usr/bin/sort \"$@\"; }; "
        f"source '{(ROOT / 'scripts/agents/soul-runtime-lib.sh').as_posix()}'; "
        f"append_codex_agents_extras '{repo.as_posix()}' '{output.as_posix()}'"
    )
    result = subprocess.run(
        [bash_executable(), "-c", command],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert marker.read_text(encoding="utf-8").splitlines() == ["C"]
    text = output.read_text(encoding="utf-8")
    assert text.index("**business-finance/") < text.index("**business/")
    assert text.index("**data-science/") < text.index("**data/")
