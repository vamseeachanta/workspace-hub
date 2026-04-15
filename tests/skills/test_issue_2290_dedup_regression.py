from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


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
