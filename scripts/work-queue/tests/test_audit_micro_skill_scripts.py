"""
TDD tests for audit-micro-skill-scripts.py
Run with: uv run --no-project python -m pytest scripts/work-queue/tests/test_audit_micro_skill_scripts.py -v
"""
import sys
import textwrap
from pathlib import Path

import pytest

# Add scripts/work-queue to path so we can import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))

from audit_micro_skill_scripts import classify, priority_score, extract_checklist_lines, load_known_scripts


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

KNOWN_SCRIPTS = {"verify-gate-evidence", "audit-skill-violations", "checkpoint", "claim-item"}


# ---------------------------------------------------------------------------
# classify() tests
# ---------------------------------------------------------------------------

class TestClassify:
    def test_already_scripted_exact_name(self):
        """Line calling an existing script → already-scripted."""
        line = "Run verify-gate-evidence.py WRK-NNN before claiming"
        assert classify(line, KNOWN_SCRIPTS) == "already-scripted"

    def test_scriptable_verify_keyword(self):
        """'verify gate evidence exists' → scriptable (binary keyword)."""
        line = "verify gate evidence exists before proceeding"
        assert classify(line, KNOWN_SCRIPTS) == "scriptable"

    def test_judgment_assess(self):
        """'assess if plan is complete' → judgment (denylist hit)."""
        line = "assess if plan is complete and covers all ACs"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_judgment_evaluate(self):
        """'evaluate whether scope is appropriate' → judgment (denylist)."""
        line = "evaluate whether scope is appropriate for the team"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_scriptable_check_keyword(self):
        """'check that all files exist' → scriptable."""
        line = "check that all required evidence files exist"
        assert classify(line, KNOWN_SCRIPTS) == "scriptable"

    def test_judgment_default_safe(self):
        """Line with no keywords → judgment (default-safe fallback)."""
        line = "walk through section by section with the user"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_already_scripted_takes_priority_over_judgment(self):
        """Script name present + judgment keyword → already-scripted (script wins)."""
        line = "evaluate the output of checkpoint.sh before proceeding"
        assert classify(line, KNOWN_SCRIPTS) == "already-scripted"

    def test_judgment_takes_priority_over_scriptable(self):
        """Both judgment + binary keyword present → judgment (denylist wins over allowlist)."""
        line = "assess and verify that the artifact is present"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"


# ---------------------------------------------------------------------------
# priority_score() tests
# ---------------------------------------------------------------------------

class TestPriorityScore:
    def test_judgment_item_scores_zero(self):
        """Judgment items in hard-gate stages must score 0."""
        item = {"cls": "judgment", "stage": 1, "n_stages": 1}
        assert priority_score(item) == 0

    def test_already_scripted_scores_zero(self):
        """Already-scripted items score 0 (no child WRK needed)."""
        item = {"cls": "already-scripted", "stage": 5, "n_stages": 5}
        assert priority_score(item) == 0

    def test_scriptable_hard_gate_stage_scores_high(self):
        """Scriptable item in a hard-gate stage (1/5/7/17) gets ≥ 3."""
        item = {"cls": "scriptable", "stage": 5, "n_stages": 1}
        assert priority_score(item) >= 3

    def test_scriptable_non_hard_gate_scores_lower(self):
        """Scriptable item outside hard-gate stages scores less than hard-gate."""
        hard_gate = {"cls": "scriptable", "stage": 7, "n_stages": 1}
        regular = {"cls": "scriptable", "stage": 10, "n_stages": 1}
        assert priority_score(hard_gate) > priority_score(regular)

    def test_multi_stage_appearance_boosts_score(self):
        """Item appearing in 3+ stages gets a bonus."""
        single = {"cls": "scriptable", "stage": 10, "n_stages": 1}
        multi = {"cls": "scriptable", "stage": 10, "n_stages": 3}
        assert priority_score(multi) > priority_score(single)


# ---------------------------------------------------------------------------
# extract_checklist_lines() tests
# ---------------------------------------------------------------------------

class TestExtractChecklistLines:
    def test_numbered_steps(self):
        content = textwrap.dedent("""\
            Stage 3 · Triage
            1. Read resource-intelligence.yaml
            2. Confirm route (A/B/C)
            3. Surface open questions
        """)
        lines = extract_checklist_lines(content)
        assert len(lines) == 3
        assert any("Read resource-intelligence" in l for l in lines)

    def test_checkbox_style(self):
        content = textwrap.dedent("""\
            Checklist:
            - [ ] verify gate evidence
            - [ ] assess if plan complete
        """)
        lines = extract_checklist_lines(content)
        assert len(lines) == 2

    def test_empty_file(self):
        """Empty file returns empty list, no crash."""
        lines = extract_checklist_lines("")
        assert lines == []

    def test_no_checklist_items(self):
        """File with only prose returns empty list."""
        content = "This is a description without any list items.\n"
        lines = extract_checklist_lines(content)
        assert lines == []
