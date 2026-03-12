"""
TDD tests for audit_micro_skill_scripts.py
Run with: uv run --no-project python -m pytest scripts/work-queue/tests/test_audit_micro_skill_scripts.py -v
"""
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from audit_micro_skill_scripts import (
    classify,
    priority_score,
    extract_checklist_lines,
    load_known_scripts,
    _add_cross_stage_counts,
    audit_stage_files,
    build_report,
)


KNOWN_SCRIPTS = {"verify-gate-evidence.py", "audit-skill-violations.sh",
                 "checkpoint.sh", "claim-item.sh"}


# ---------------------------------------------------------------------------
# classify() — basic classification
# ---------------------------------------------------------------------------

class TestClassify:
    def test_already_scripted_exact_filename(self):
        line = "Run verify-gate-evidence.py WRK-NNN before claiming"
        assert classify(line, KNOWN_SCRIPTS) == "already-scripted"

    def test_scriptable_verify_keyword(self):
        line = "verify gate evidence exists before proceeding"
        assert classify(line, KNOWN_SCRIPTS) == "scriptable"

    def test_judgment_assess(self):
        line = "assess if plan is complete and covers all ACs"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_judgment_evaluate(self):
        line = "evaluate whether scope is appropriate for the team"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_scriptable_check_keyword(self):
        line = "check that all required evidence files exist"
        assert classify(line, KNOWN_SCRIPTS) == "scriptable"

    def test_judgment_default_safe(self):
        line = "walk through section by section with the user"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_already_scripted_takes_priority_over_judgment(self):
        line = "evaluate the output of checkpoint.sh before proceeding"
        assert classify(line, KNOWN_SCRIPTS) == "already-scripted"

    def test_judgment_takes_priority_over_scriptable(self):
        """Judgment denylist wins over binary allowlist."""
        line = "assess and verify that the artifact is present"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_no_false_positive_from_stem_substring(self):
        """'test' as a stem must NOT flag lines containing 'latest'."""
        small_scripts = {"test.py"}
        line = "run the latest version of the pipeline"
        # 'test' as a filename requires word boundary — 'latest' must not match
        assert classify(line, small_scripts) != "already-scripted"

    def test_no_false_positive_confirm_in_compound_word(self):
        """'confirm' in 'gates_confirmed' should not classify as scriptable."""
        line = "Write evidence/activation.yaml (activated_at, gates_confirmed)"
        # Write-prefix rule should suppress scriptable
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_write_prefix_forces_judgment(self):
        """Lines starting with 'Write' should never be scriptable."""
        line = "Write evidence/user-review-capture.yaml (scope_approved: true)"
        assert classify(line, KNOWN_SCRIPTS) == "judgment"

    def test_no_false_positive_fail_in_caps(self):
        """'FAIL' word boundary should still match as scriptable (uppercase)."""
        line = "exit 0 on PASS, exit 1 on FAIL"
        assert classify(line, KNOWN_SCRIPTS) == "scriptable"


# ---------------------------------------------------------------------------
# priority_score()
# ---------------------------------------------------------------------------

class TestPriorityScore:
    def test_judgment_item_scores_zero(self):
        item = {"cls": "judgment", "stage": 1, "n_distinct_stages": 1}
        assert priority_score(item) == 0

    def test_already_scripted_scores_zero(self):
        item = {"cls": "already-scripted", "stage": 5, "n_distinct_stages": 5}
        assert priority_score(item) == 0

    def test_scriptable_hard_gate_stage_scores_high(self):
        item = {"cls": "scriptable", "stage": 5, "n_distinct_stages": 1}
        assert priority_score(item) >= 3

    def test_scriptable_non_hard_gate_scores_lower(self):
        hard = {"cls": "scriptable", "stage": 7, "n_distinct_stages": 1}
        regular = {"cls": "scriptable", "stage": 10, "n_distinct_stages": 1}
        assert priority_score(hard) > priority_score(regular)

    def test_multi_stage_appearance_boosts_score(self):
        single = {"cls": "scriptable", "stage": 10, "n_distinct_stages": 1}
        multi = {"cls": "scriptable", "stage": 10, "n_distinct_stages": 3}
        assert priority_score(multi) > priority_score(single)


# ---------------------------------------------------------------------------
# extract_checklist_lines()
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

    def test_checkbox_style_hyphen(self):
        content = textwrap.dedent("""\
            Checklist:
            - [ ] verify gate evidence
            - [ ] assess if plan complete
        """)
        lines = extract_checklist_lines(content)
        assert len(lines) == 2

    def test_checkbox_style_asterisk(self):
        content = "* [ ] verify all files exist\n"
        lines = extract_checklist_lines(content)
        assert len(lines) == 1

    def test_empty_file(self):
        assert extract_checklist_lines("") == []

    def test_no_checklist_items(self):
        content = "This is a description without any list items.\n"
        assert extract_checklist_lines(content) == []


# ---------------------------------------------------------------------------
# _add_cross_stage_counts() — distinct stage counting
# ---------------------------------------------------------------------------

class TestCrossStageCount:
    def test_same_line_different_stages_counts_distinct(self):
        items = [
            {"stage": 5, "line": "DO NOT proceed until decision: approved confirmed"},
            {"stage": 5, "line": "DO NOT proceed until decision: approved confirmed"},  # same stage
            {"stage": 7, "line": "DO NOT proceed until decision: approved confirmed"},
        ]
        result = _add_cross_stage_counts(items)
        # Appears in stage 5 and 7 — distinct count = 2, not 3
        assert result[0]["n_distinct_stages"] == 2
        assert result[1]["n_distinct_stages"] == 2
        assert result[2]["n_distinct_stages"] == 2

    def test_unique_lines_score_one(self):
        items = [{"stage": 3, "line": "unique checklist item here"}]
        result = _add_cross_stage_counts(items)
        assert result[0]["n_distinct_stages"] == 1


# ---------------------------------------------------------------------------
# Integration: real stage files
# ---------------------------------------------------------------------------

class TestIntegration:
    """Run against the real 20 stage files to catch regressions."""

    @pytest.fixture(scope="class")
    def workspace(self):
        return Path(__file__).resolve().parents[3]

    @pytest.fixture(scope="class")
    def report(self, workspace):
        stages_dir = workspace / ".claude/skills/workspace-hub/stages"
        wq_dir = workspace / "scripts/work-queue"
        if not stages_dir.is_dir():
            pytest.skip("stages dir not found")
        known = load_known_scripts(wq_dir)
        items = audit_stage_files(stages_dir, known)
        return build_report(items)

    def test_report_has_at_least_3_high_priority(self, report):
        assert report["summary"]["high_priority_count"] >= 3

    def test_no_duplicate_proposed_wrks(self, report):
        titles = [w["proposed_title"] for w in report["proposed_wrks"]]
        assert len(titles) == len(set(titles)), "duplicate proposed WRK titles"

    def test_stage5_not_duplicated_in_proposed(self, report):
        """Stage 5 duplicate route entries must not create duplicate proposals."""
        stage5_proposals = [w for w in report["proposed_wrks"] if w["stage"] == 5]
        lines = [w["proposed_title"] for w in stage5_proposals]
        assert len(lines) == len(set(lines)), "Stage 5 duplicate in proposed_wrks"

    def test_write_prefix_items_not_scriptable(self, report):
        """No item starting with 'Write' should be classified scriptable."""
        bad = [
            i for i in report["all_items"]
            if i["cls"] == "scriptable" and i["line"].strip().lower().startswith("write")
        ]
        assert bad == [], f"Write-prefix items incorrectly classified: {bad}"

    def test_total_items_reasonable(self, report):
        assert report["summary"]["total"] >= 50
