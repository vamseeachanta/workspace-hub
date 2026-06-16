"""G2 #3117 — CLAUDE.md ↔ AGENTS.md drift guard (Level-2 invariant, #3058 pattern).

AGENTS.md is the cross-provider canonical contract; CLAUDE.md is the Claude adapter
that delegates to it. They intentionally differ, but a small set of LOAD-BEARING
invariants must appear in BOTH so a non-Claude harness (reading AGENTS.md) and Claude
(reading CLAUDE.md) get the same gates. If a future edit drops/contradicts one in
either file, this guard fails — converting a manual "did they drift?" check into a
standing test (the #3058 manual-check → invariant promotion).

NOTE: this guards SHARED contract tokens only, not full equality (the files are
deliberately different surfaces). Harness-file SIZE is already enforced by
scripts/enforcement/check-harness-file-size.sh — not duplicated here.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MD = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
AGENTS_MD = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

# Load-bearing contract tokens that MUST appear in both harness files.
SHARED_INVARIANTS = [
    "SHARED_SOUL.md",            # same canonical cross-provider identity source
    "issue-planning-mode",       # same planning skill
    "_template-issue-plan.md",   # same plan template
    "Adversarial Review",        # same review gate
    "USER APPROVES",             # the load-bearing approval gate (never self-approve)
    "status:plan-approved",      # same gate label
    "TDD",                       # TDD mandatory in both
]


def _present(token: str, text: str) -> bool:
    return token in text


@pytest.mark.parametrize("token", SHARED_INVARIANTS)
def test_shared_invariant_in_both_harness_files(token):
    assert _present(token, CLAUDE_MD), f"CLAUDE.md dropped shared contract token: {token!r}"
    assert _present(token, AGENTS_MD), f"AGENTS.md dropped shared contract token: {token!r}"


def test_claude_md_declares_agents_md_canonical():
    # The delegation contract: CLAUDE.md must point to AGENTS.md as canonical.
    assert "AGENTS.md" in CLAUDE_MD, "CLAUDE.md must name AGENTS.md as the canonical contract"


def test_guard_is_not_vacuous_detects_drift():
    # Red-equivalent: prove the guard actually catches a dropped token (synthetic drift),
    # so a future no-op edit can't make the invariants silently pass.
    drifted = AGENTS_MD.replace("USER APPROVES", "user decides")
    assert not _present("USER APPROVES", drifted)
    assert _present("USER APPROVES", AGENTS_MD)  # ...and the real file still holds it
