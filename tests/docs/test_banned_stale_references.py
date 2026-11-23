from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import stale_reference_docs
from tests.helpers.stale_reference_docs import scan_stale_reference_hits

# Current standards selected for strict coverage; historical reference documents
# remain governed by tests/docs/test_legacy_reference_allowlist.py.
CURRENT_STANDARDS_FILES = [
    "docs/standards/AI_REVIEW_ROUTING_POLICY.md",
    "docs/standards/CROSS_PLATFORM_ARTIFACT_POLICY.md",
    "docs/standards/FILE_STRUCTURE_TAXONOMY.md",
]

STRICT_FILES = [
    "AGENTS.md",
    # CLAUDE.md retired 2026-08-01 — AGENTS.md is canonical.
    "GEMINI.md",
    "README.md",
    ".planning/templates/route-c-generic.md",
    ".planning/templates/route-c-energy.md",
    ".planning/templates/route-c-marine.md",
    ".planning/templates/route-c-structural.md",
    "docs/README.md",
    "docs/context-pipeline.md",
    "docs/governance/TRUST-ARCHITECTURE.md",
    "docs/modules/workflow/SPEC_LOCALITY_POLICY.md",
    "docs/plans/README.md",
    "docs/ROUTING_INDEX.md",
    *CURRENT_STANDARDS_FILES,
    "docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md",
    "docs/standards/TIER1_INDEXING_CHECKLIST.md",
    "docs/work-queue-workflow.md",
]


@pytest.mark.parametrize("relative_path", STRICT_FILES)
def test_curated_planning_and_docs_files_do_not_reference_deleted_workflow_paths(relative_path: str) -> None:
    violations = scan_stale_reference_hits(relative_path)
    assert not violations, "Found banned stale references:\n" + "\n".join(violations)


@pytest.mark.parametrize("relative_path", CURRENT_STANDARDS_FILES)
def test_current_standard_mutation_detects_deleted_workflow_path(
    relative_path: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Protect the selected standards using a synthetic document, never live prose.

    The deleted new-spec helper and diagnostic label are specified by
    CORE_BANNED_STALE_REFERENCE_PATTERNS in tests/helpers/stale_reference_docs.py.
    """
    assert relative_path in STRICT_FILES
    document = tmp_path / relative_path
    document.parent.mkdir(parents=True)
    clean_text = "# Current standard\n\n"
    document.write_text(clean_text, encoding="utf-8")
    monkeypatch.setattr(stale_reference_docs, "REPO_ROOT", tmp_path)
    assert scan_stale_reference_hits(relative_path) == []

    deleted_path = "scripts/work-queue/new-spec.sh"
    document.write_text(clean_text + f"See `{deleted_path}`.\n", encoding="utf-8")

    # The injected reference follows the heading and blank line: line 3.
    assert scan_stale_reference_hits(relative_path) == [
        f"{relative_path}:3: deleted new-spec helper: {deleted_path}"
    ]
