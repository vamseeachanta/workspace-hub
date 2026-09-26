from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = [
    Path("scripts"),
    Path(".claude/hooks"),
    Path(".github/workflows"),
    Path("config/scheduled-tasks"),
    Path(".githooks"),
]

SCRIPT_SOURCE_SUFFIXES = (".sh", ".bash", ".zsh")
CONFIG_SOURCE_SUFFIXES = (".yml", ".yaml")

PATH_RE = re.compile(
    r"""(?P<path>
        (?:
            \$\{?(?:WORKSPACE_ROOT|REPO_ROOT|ROOT|WS)\}?|
            \$\{?SCRIPT_DIR\}?|
            \.
        )?
        /?
        (?:
            scripts|\.claude/hooks|\.githooks
        )
        /[A-Za-z0-9_./{}$()+@%-]+?
        \.(?:sh|py|ps1|js)
        (?=$|[\s"'`),;&|<>])
    )""",
    re.VERBOSE,
)

INVOKER_RE = re.compile(
    r"(^|[\s;&|(])("
    r"bash|sh|zsh|python|python3|node|uv|timeout|exec|source|\.|"
    r"FilePath|command|run|windows_script|script|path"
    r")([\s:=]|$)"
)

ROOT_PREFIXES = (
    "${WORKSPACE_ROOT}/",
    "$WORKSPACE_ROOT/",
    "${REPO_ROOT}/",
    "$REPO_ROOT/",
    "${ROOT}/",
    "$ROOT/",
    "${WS}/",
    "$WS/",
    "./",
)

DEFERRED_MISSING_REFERENCES = {
    (
        "config/scheduled-tasks/schedule-tasks.yaml",
        106,
        "scripts/deckhand/licensed-run-ops.py",
    ): "unresolved external deckhand-ops checkout after cd /mnt/local-analysis/deckhand-ops",
    (
        "scripts/operations/compliance/propagate_all_skills.sh",
        96,
        "./scripts/compliance/auto_propagate.sh",
    ): "needs decision; no auto_propagate.sh basename exists in this repo",
}


def _strip_inline_comment(line: str) -> str:
    if line.lstrip().startswith("#"):
        return ""
    return line.split(" #", 1)[0]


def _iter_scan_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        absolute_root = REPO_ROOT / root
        if not absolute_root.exists():
            continue
        for path in absolute_root.rglob("*"):
            if not path.is_file():
                continue
            rel_path = path.relative_to(REPO_ROOT)
            if rel_path.parts[0] == "scripts" and path.suffix not in SCRIPT_SOURCE_SUFFIXES:
                continue
            if rel_path.parts[0] == "config" and path.suffix not in CONFIG_SOURCE_SUFFIXES:
                continue
            if rel_path.parts[0] == ".github" and path.suffix not in CONFIG_SOURCE_SUFFIXES:
                continue
            files.append(path)
    return sorted(files)


def _looks_like_invocation(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(('"$', "'$", '"${', "'${", "$", "${", "./")):
        return True
    if stripped.startswith(("-", "run:", "windows_script:", "command:", "path:")):
        return True
    return bool(INVOKER_RE.search(stripped))


def _resolve_path(raw_path: str, source_file: Path) -> Path | None:
    cleaned = raw_path.strip("'\"`),")
    for prefix in ROOT_PREFIXES:
        if cleaned.startswith(prefix):
            return REPO_ROOT / cleaned[len(prefix) :]
    if cleaned.startswith("${SCRIPT_DIR}/"):
        return source_file.parent / cleaned[len("${SCRIPT_DIR}/") :]
    if cleaned.startswith("$SCRIPT_DIR/"):
        return source_file.parent / cleaned[len("$SCRIPT_DIR/") :]
    if cleaned.startswith("scripts/") or cleaned.startswith(".claude/hooks/"):
        return REPO_ROOT / cleaned
    if cleaned.startswith(".githooks/"):
        return REPO_ROOT / cleaned
    return None


def _is_swallowed(line: str) -> bool:
    return any(marker in line for marker in ("|| true", "|| :", "2>/dev/null", "continue"))


def test_static_script_invocations_reference_existing_files() -> None:
    broken: list[str] = []
    examined = 0

    for source_file in _iter_scan_files():
        rel_source = source_file.relative_to(REPO_ROOT)
        for line_number, line in enumerate(source_file.read_text(errors="ignore").splitlines(), 1):
            candidate_line = _strip_inline_comment(line)
            if not _looks_like_invocation(candidate_line):
                continue
            for match in PATH_RE.finditer(candidate_line):
                resolved = _resolve_path(match.group("path"), source_file)
                if resolved is None:
                    continue
                examined += 1
                if not resolved.exists():
                    key = (str(rel_source), line_number, match.group("path"))
                    if key in DEFERRED_MISSING_REFERENCES:
                        continue
                    swallowed = "yes" if _is_swallowed(candidate_line) else "no"
                    broken.append(
                        f"{rel_source}:{line_number}: {match.group('path')} "
                        f"(swallowed={swallowed})"
                    )

    assert examined > 0
    assert not broken, "Broken script references:\n" + "\n".join(broken)
