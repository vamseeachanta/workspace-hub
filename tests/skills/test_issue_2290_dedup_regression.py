from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import warnings
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
AUDIT_PATH = REPO_ROOT / "scripts" / "skills" / "weekly_skills_audit.py"

TARGET_DUPLICATE_NAMES = {
    "cross-agent-skill-audit",
    "github-code-review",
    "obsidian",
    "corporate-tax-strategic-planning",
    "writing-plans",
    "dspy",
    "systematic-debugging",
}

TARGET_LEAF_COLLISIONS = {
    "code-review",
    "pyproject-toml",
    "uv-package-manager",
}

STALE_DIRS = [
    "cross-agent-skill-audit",
    "github/github-code-review",
    "note-taking/obsidian",
    "corporate-tax-strategic-planning",
    "software-development/writing-plans",
    "mlops/research/dspy",
    "software-development/systematic-debugging",
    "software-development/code-review",
    "operations/devtools/pyproject-toml",
    "operations/devtools/uv-package-manager",
]

CANONICAL_DIRS = [
    "coordination/cross-agent-skill-audit",
    "development/github/code-review",
    "business/productivity/obsidian",
    "business-finance/corporate-tax-strategic-planning",
    "development/planning/writing-plans",
    "ai/prompting/dspy",
    "development/systematic-debugging",
    "development/devtools/pyproject-toml",
    "development/devtools/uv-package-manager",
]


def _import_audit():
    spec = importlib.util.spec_from_file_location("weekly_skills_audit_issue_2290", AUDIT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["weekly_skills_audit_issue_2290"] = mod
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _run_repo_audit(tmp_path: Path) -> dict:
    audit = _import_audit()
    return audit.run_audit(
        skills_dir=SKILLS_DIR,
        output_dir=tmp_path / "out",
        policy_path=REPO_ROOT / "config" / "skills" / "weekly-audit-policy.yaml",
    )


def test_target_duplicate_names_are_cleared(tmp_path: Path) -> None:
    result = _run_repo_audit(tmp_path)
    findings = [f for f in result["findings"] if f["classification"] == "exact-duplicate"]
    names = {name for finding in findings for name in finding.get("canonical_names", [])}
    assert TARGET_DUPLICATE_NAMES.isdisjoint(names)


def test_target_leaf_collisions_are_cleared(tmp_path: Path) -> None:
    result = _run_repo_audit(tmp_path)
    findings = [f for f in result["findings"] if f["classification"] == "generic-leaf-collision"]
    leaves = {finding.get("leaf_name") for finding in findings}
    assert TARGET_LEAF_COLLISIONS.isdisjoint(leaves)


def test_stale_directories_removed() -> None:
    missing = [str(SKILLS_DIR / rel) for rel in STALE_DIRS if (SKILLS_DIR / rel).exists()]
    assert not missing


def test_canonical_directories_still_exist() -> None:
    missing = [str(SKILLS_DIR / rel) for rel in CANONICAL_DIRS if not (SKILLS_DIR / rel / "SKILL.md").exists()]
    assert not missing


# Active surfaces listed in issue #2294. Git enumeration excludes untracked
# runtime material; no historical text within these surfaces is excluded.
REFERENCE_SURFACES = (
    ".claude/agent-skills-map.yaml",
    ".claude/skill-registry.yaml",
    "AGENTS.md",
    ".mcp.json",
    ".claude/rules",
    ".codex",
    ".gemini",
    ".hermes",
    "config",
    "scripts",
)


def _tracked_reference_files(root: Path) -> list[Path]:
    # Fixture callers and hooks may inherit bindings to another checkout.
    env = {key: value for key, value in os.environ.items()
           if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"}}
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *REFERENCE_SURFACES],
        cwd=root, env=env, check=True, capture_output=True,
    )
    return [root / os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def _deleted_path_references(root: Path, files: list[Path]) -> set[tuple[str, int, str]]:
    """Match exact retired path components, not skill names or live suffixes.

    Recognize qualified skill paths and unqualified directory/file paths.
    Bare single-component skill names are not directory references. Scan UTF-8
    text and symlink destinations; binary payloads are outside this text check.
    """
    patterns = {}
    for retired in STALE_DIRS:
        escaped = re.escape(retired)
        qualified = rf"(?:\.?\.?/)*(?:\.(?:claude|agents)/skills/|skills/){escaped}"
        bare = escaped if "/" in retired else rf"{escaped}(?=/)"
        patterns[retired] = re.compile(
            rf"(?:(?<![\w.-]){qualified}|(?<![\w./-]){bare})(?![\w.-])"
        )
    findings = set()
    for path in files:
        if path.is_symlink():
            text = os.readlink(path)
        else:
            try:
                text = path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                continue
        for number, line in enumerate(text.splitlines(), start=1):
            for retired, pattern in patterns.items():
                if pattern.search(line):
                    findings.add((path.relative_to(root).as_posix(), number, retired))
    return findings


def _canonical_auxiliary_problems(
    skills: Path, directories: list[str],
) -> set[tuple[str, int, str, str]]:
    """Check relative Markdown links and quoted references/assets paths.

    Repository command examples and external links are not local auxiliaries.
    Resolve fragments and symlinks, and require files inside the canonical tree.
    """
    links = re.compile(r"\[[^\]]*\]\(([^\s)]+)\)|`((?:references|assets)/[^`\s]+)`")
    findings = set()
    for directory in directories:
        tree = skills / directory
        source = tree / "SKILL.md"
        relative = source.relative_to(skills).as_posix()
        if not source.is_file():
            findings.add((relative, 1, "SKILL.md", "missing"))
            continue
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            for match in links.finditer(line):
                target = match.group(1) or match.group(2)
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
                    continue
                resolved = (tree / unquote(url.path)).resolve()
                if not resolved.is_relative_to(tree.resolve()):
                    reason = "outside canonical tree"
                elif not resolved.is_file():
                    reason = "missing"
                else:
                    continue
                findings.add((relative, number, target, reason))
    return findings


# Migration policy: issue #2294 and STALE_DIRS / CANONICAL_DIRS above.
# Fixture expectations below are hand-counted from their literal input lines.
@pytest.fixture
def reference_tree(tmp_path: Path) -> Path:
    for directory in (".codex", "config"):
        (tmp_path / directory).mkdir()
    return tmp_path


def test_deleted_path_reference_is_reported(reference_tree: Path) -> None:
    adapter = reference_tree / ".codex" / "AGENTS.md"
    adapter.write_text(
        "[retired](../.claude/skills/github/github-code-review/SKILL.md)\n"
        "` .claude/skills/software-development/code-review `\n",
        encoding="utf-8",
    )
    config = reference_tree / "config" / "skills.yaml"
    config.write_text(
        "skill: operations/devtools/uv-package-manager/SKILL.md\n",
        encoding="utf-8",
    )
    assert _deleted_path_references(reference_tree, [adapter, config]) == {
        (".codex/AGENTS.md", 1, "github/github-code-review"),
        (".codex/AGENTS.md", 2, "software-development/code-review"),
        ("config/skills.yaml", 1, "operations/devtools/uv-package-manager"),
    }


def test_similarly_named_live_paths_are_retained(reference_tree: Path) -> None:
    adapter = reference_tree / ".codex" / "AGENTS.md"
    adapter.write_text(
        "`.claude/skills/github/github-code-review-extra/SKILL.md`\n"
        "`.claude/skills/github/github-code-review.md`\n"
        "`.claude/skills/development/github/code-review/SKILL.md`\n"
        "`.claude/skills/coordination/cross-agent-skill-audit/SKILL.md`\n"
        "skill-name: cross-agent-skill-audit\n",
        encoding="utf-8",
    )
    assert _deleted_path_references(reference_tree, [adapter]) == set()


def test_injected_stale_reference_fails_clean_assertion(reference_tree: Path) -> None:
    config = reference_tree / "config" / "skills.yaml"
    config.write_text(
        "skill: .claude/skills/github/github-code-review/SKILL.md\n",
        encoding="utf-8",
    )
    with pytest.raises(AssertionError):
        assert not _deleted_path_references(reference_tree, [config])


@pytest.mark.parametrize("retired", STALE_DIRS)
def test_each_retired_directory_is_scanned(reference_tree: Path, retired: str) -> None:
    config = reference_tree / "config" / "skills.yaml"
    config.write_text(f"skill: .claude/skills/{retired}/SKILL.md\n", encoding="utf-8")
    assert _deleted_path_references(reference_tree, [config]) == {
        ("config/skills.yaml", 1, retired),
    }


def test_canonical_auxiliary_file_survives(reference_tree: Path) -> None:
    skills = reference_tree / ".claude" / "skills"
    canonical = skills / "development" / "github" / "code-review"
    references = canonical / "references"
    references.mkdir(parents=True)
    (canonical / "SKILL.md").write_text(
        "[template](references/template.md#summary)\n"
        "`references/template.md`\n"
        "[external](https://example.org/guide.md)\n",
        encoding="utf-8",
    )
    (references / "template.md").write_text("# Summary\n", encoding="utf-8")
    assert _canonical_auxiliary_problems(skills, ["development/github/code-review"]) == set()


def test_auxiliary_missing_and_escape_are_reported(reference_tree: Path) -> None:
    canonical = reference_tree / "review"
    canonical.mkdir()
    (reference_tree / "outside.md").write_text("outside\n", encoding="utf-8")
    (canonical / "escape.md").symlink_to(reference_tree / "outside.md")
    (canonical / "SKILL.md").write_text(
        "[missing](references/missing.md)\n"
        "[parent](../outside.md)\n"
        "[symlink](escape.md)\n",
        encoding="utf-8",
    )
    assert _canonical_auxiliary_problems(reference_tree, ["review"]) == {
        ("review/SKILL.md", 1, "references/missing.md", "missing"),
        ("review/SKILL.md", 2, "../outside.md", "outside canonical tree"),
        ("review/SKILL.md", 3, "escape.md", "outside canonical tree"),
    }


# Exact baseline observations from the canonical SKILL.md lines named below
# on the base revision. These findings remain visible; no tree is excluded.
BASELINE_AUXILIARY_PROBLEMS = {
    ("ai/prompting/dspy/SKILL.md", 1, "SKILL.md", "missing"),
    ("business/productivity/obsidian/SKILL.md", 1, "SKILL.md", "missing"),
    ("development/devtools/pyproject-toml/SKILL.md", 52, "1-version-constraints/SKILL.md", "missing"),
    ("development/devtools/pyproject-toml/SKILL.md", 56, "complete-pyprojecttoml-template/SKILL.md", "missing"),
    ("development/devtools/pyproject-toml/SKILL.md", 57, "1-build-system/SKILL.md", "missing"),
    ("development/devtools/pyproject-toml/SKILL.md", 58, "pytest/SKILL.md", "missing"),
    ("development/devtools/pyproject-toml/SKILL.md", 59, "example-1-data-processing-library/SKILL.md", "missing"),
    ("development/devtools/uv-package-manager/SKILL.md", 194, "1-project-initialization/SKILL.md", "missing"),
    ("development/devtools/uv-package-manager/SKILL.md", 195, "5-running-scripts-and-commands/SKILL.md", "missing"),
    ("development/devtools/uv-package-manager/SKILL.md", 196, "1-version-pinning/SKILL.md", "missing"),
}


def test_tracked_surface_enumeration_is_scoped(reference_tree: Path, monkeypatch) -> None:
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        monkeypatch.setenv(name, "unrelated-checkout")

    def fake_run(command, **kwargs):
        assert command == ["git", "ls-files", "-z", "--", *REFERENCE_SURFACES]
        assert kwargs["cwd"] == reference_tree
        assert kwargs["check"] and kwargs["capture_output"]
        assert not {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"} & kwargs["env"].keys()
        return subprocess.CompletedProcess(command, 0, b"AGENTS.md\0config/skills.yaml\0")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert _tracked_reference_files(reference_tree) == [
        reference_tree / "AGENTS.md", reference_tree / "config" / "skills.yaml",
    ]


def test_absolute_and_symlink_references_are_scanned(reference_tree: Path) -> None:
    adapter = reference_tree / ".codex" / "AGENTS.md"
    adapter.symlink_to("../.claude/skills/github/github-code-review/SKILL.md")
    config = reference_tree / "config" / "skills.yaml"
    config.write_text(
        f"skill: {reference_tree}/.claude/skills/software-development/code-review/SKILL.md\n",
        encoding="utf-8",
    )
    assert _deleted_path_references(reference_tree, [adapter, config]) == {
        (".codex/AGENTS.md", 1, "github/github-code-review"),
        ("config/skills.yaml", 1, "software-development/code-review"),
    }


def test_active_tracked_surfaces_have_no_deleted_path_references(record_property) -> None:
    files = _tracked_reference_files(REPO_ROOT)
    assert files, "tracked reference surfaces were not enumerated"
    record_property("tracked_surface_files", len(files))
    assert not _deleted_path_references(REPO_ROOT, files)


def test_canonical_auxiliary_baseline_is_reported(record_property) -> None:
    problems = _canonical_auxiliary_problems(SKILLS_DIR, CANONICAL_DIRS)
    known = problems & BASELINE_AUXILIARY_PROBLEMS
    record_property("baseline_auxiliary_problems", sorted(known))
    if known:
        warnings.warn(f"Pre-existing canonical reference problems: {sorted(known)}", stacklevel=1)
    assert not problems - BASELINE_AUXILIARY_PROBLEMS, "new canonical auxiliary problems"


def test_repository_canonical_auxiliary_file_survives() -> None:
    # Named by development/github/code-review/SKILL.md under Inline Commenting.
    tree = SKILLS_DIR / "development/github/code-review"
    auxiliary = "references/review-output-template.md"
    assert f"`{auxiliary}`" in (tree / "SKILL.md").read_text(encoding="utf-8")
    assert (tree / auxiliary).is_file()
    assert (tree / auxiliary).resolve().is_relative_to(tree.resolve())
