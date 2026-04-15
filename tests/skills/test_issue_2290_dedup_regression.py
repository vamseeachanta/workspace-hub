"""Regression tests for #2290: deduplicate exact-copy skills and reconcile leaf collisions.

Asserts:
  - 10 duplicate/collision directories are removed
  - 10 canonical directories survive with valid SKILL.md
  - Auxiliary reference files are preserved in canonical locations
  - agent-skills-map.yaml has no dangling references to deleted paths
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


# ── Directories that MUST be deleted (duplicates / losers) ──────────────

DELETED_DIRS = [
    # 7 canonical-name duplicate losers (non-canonical copies)
    "cross-agent-skill-audit",
    "github/github-code-review",
    "note-taking/obsidian",
    "corporate-tax-strategic-planning",
    "software-development/writing-plans",
    "mlops/research/dspy",
    "software-development/systematic-debugging",
    # 3 leaf-collision losers
    "software-development/code-review",
    "operations/devtools/pyproject-toml",
    "operations/devtools/uv-package-manager",
]


# ── Directories that MUST survive (approved canonical keepers) ──────────

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


# ── Auxiliary files that MUST be preserved in canonical locations ────────

REQUIRED_AUX_FILES = [
    "development/github/code-review/references/review-output-template.md",
    "ai/prompting/dspy/references/examples.md",
    "ai/prompting/dspy/references/modules.md",
    "ai/prompting/dspy/references/optimizers.md",
]


# ═════════════════════════════════════════════════════════════════════════
# Tests
# ═════════════════════════════════════════════════════════════════════════


class TestDuplicatesRemoved:
    """Every duplicate directory from #2290 must be gone."""

    @pytest.mark.parametrize("rel", DELETED_DIRS, ids=DELETED_DIRS)
    def test_duplicate_dir_absent(self, rel: str) -> None:
        d = SKILLS_DIR / rel
        assert not d.exists(), f"Duplicate directory still exists: {d}"


class TestCanonicalsValid:
    """Every canonical keeper must exist with a valid SKILL.md."""

    @pytest.mark.parametrize("rel", CANONICAL_DIRS, ids=CANONICAL_DIRS)
    def test_canonical_dir_exists(self, rel: str) -> None:
        d = SKILLS_DIR / rel
        assert d.is_dir(), f"Canonical directory missing: {d}"

    @pytest.mark.parametrize("rel", CANONICAL_DIRS, ids=CANONICAL_DIRS)
    def test_canonical_has_skill_md(self, rel: str) -> None:
        skill_md = SKILLS_DIR / rel / "SKILL.md"
        assert skill_md.is_file(), f"SKILL.md missing in canonical: {skill_md}"

    @pytest.mark.parametrize("rel", CANONICAL_DIRS, ids=CANONICAL_DIRS)
    def test_canonical_skill_md_nonempty(self, rel: str) -> None:
        skill_md = SKILLS_DIR / rel / "SKILL.md"
        assert skill_md.stat().st_size > 50, (
            f"SKILL.md suspiciously small (<50 bytes) in canonical: {skill_md}"
        )


class TestAuxiliaryFilesPreserved:
    """Auxiliary reference files must survive in canonical locations."""

    @pytest.mark.parametrize("rel", REQUIRED_AUX_FILES, ids=REQUIRED_AUX_FILES)
    def test_aux_file_exists(self, rel: str) -> None:
        f = SKILLS_DIR / rel
        assert f.is_file(), f"Required auxiliary file missing: {f}"


class TestNoLeafCollisionRemains:
    """After dedup, no two skill dirs should share the same leaf name
    within the set of pairs we resolved."""

    RESOLVED_LEAF_GROUPS = {
        "code-review": [
            "development/github/code-review",
            # github/github-code-review — deleted
            # software-development/code-review — deleted
        ],
        "pyproject-toml": [
            "development/devtools/pyproject-toml",
            # operations/devtools/pyproject-toml — deleted
        ],
        "uv-package-manager": [
            "development/devtools/uv-package-manager",
            # operations/devtools/uv-package-manager — deleted
        ],
    }

    @pytest.mark.parametrize(
        "leaf", RESOLVED_LEAF_GROUPS.keys(), ids=RESOLVED_LEAF_GROUPS.keys()
    )
    def test_no_residual_collision(self, leaf: str) -> None:
        """Only the canonical survivor should exist for each resolved leaf."""
        survivors = self.RESOLVED_LEAF_GROUPS[leaf]
        for s in survivors:
            assert (SKILLS_DIR / s).is_dir(), f"Expected survivor missing: {s}"
        # Make sure the deleted counterparts are truly gone
        for d in DELETED_DIRS:
            if Path(d).name == leaf or d.endswith(f"/{leaf}"):
                assert not (SKILLS_DIR / d).exists(), (
                    f"Leaf collision not resolved — {d} still exists"
                )


class TestReferenceSurfacesClean:
    """Approved reference surfaces must not reference deleted skill paths."""

    SURFACE_FILES = [
        REPO_ROOT / ".claude" / "agent-skills-map.yaml",
        REPO_ROOT / ".claude" / "skill-registry.yaml",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".mcp.json",
    ]

    SURFACE_DIRS = [
        REPO_ROOT / ".claude" / "rules",
        REPO_ROOT / ".codex",
        REPO_ROOT / ".gemini",
        REPO_ROOT / ".hermes",
        REPO_ROOT / "config",
        REPO_ROOT / "scripts",
    ]

    def test_no_deleted_path_fragments_in_approved_surfaces(self) -> None:
        deleted_fragments = [
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
            "ops-pyproject-toml",
            "ops-uv-package-manager",
        ]

        files = []
        for f in self.SURFACE_FILES:
            if f.exists() and f.is_file():
                files.append(f)
        for d in self.SURFACE_DIRS:
            if d.exists() and d.is_dir():
                for f in d.rglob("*"):
                    if f.is_file():
                        files.append(f)

        offenders = []
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for frag in deleted_fragments:
                if frag in content:
                    offenders.append((str(f.relative_to(REPO_ROOT)), frag))

        assert not offenders, f"Dangling deleted-path references found: {offenders[:20]}"
