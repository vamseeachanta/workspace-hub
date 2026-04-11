from __future__ import annotations

import pytest

from tests.helpers.stale_reference_docs import scan_stale_reference_hits

STRICT_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
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
    "docs/work-queue-workflow.md",
]


@pytest.mark.parametrize("relative_path", STRICT_FILES)
def test_curated_planning_and_docs_files_do_not_reference_deleted_workflow_paths(relative_path: str) -> None:
    violations = scan_stale_reference_hits(relative_path)
    assert not violations, "Found banned stale references:\n" + "\n".join(violations)
