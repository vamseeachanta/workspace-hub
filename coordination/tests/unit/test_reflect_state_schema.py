"""Tests for ReflectState schema validation."""

import pytest
from datetime import datetime, date
from pydantic import ValidationError

from coordination.schemas.reflect_state import (
    ChecklistStatus,
    PhasesCompleted,
    ReflectMetrics,
    ReflectChecklist,
    ActionsTaken,
    ReflectFiles,
    ReflectState,
)


@pytest.mark.unit
class TestChecklistStatus:
    def test_valid_statuses(self):
        assert ChecklistStatus("pass") == ChecklistStatus.PASS
        assert ChecklistStatus("fail") == ChecklistStatus.FAIL
        assert ChecklistStatus("warn") == ChecklistStatus.WARN
        assert ChecklistStatus("none") == ChecklistStatus.NONE

    def test_invalid_status(self):
        with pytest.raises(ValueError):
            ChecklistStatus("invalid")


@pytest.mark.unit
class TestPhasesCompleted:
    def test_all_true(self):
        p = PhasesCompleted(reflect=True, abstract=True, generalize=True, store=True)
        assert p.reflect is True
        assert p.store is True

    def test_defaults_to_false(self):
        p = PhasesCompleted()
        assert p.reflect is False
        assert p.abstract is False
        assert p.generalize is False
        assert p.store is False

    def test_extra_fields_allowed(self):
        p = PhasesCompleted(reflect=True, new_phase=True)
        assert p.reflect is True


@pytest.mark.unit
class TestReflectMetrics:
    def test_valid_metrics(self):
        m = ReflectMetrics(
            repos_analyzed=3,
            commits_found=96,
            patterns_extracted=10,
            script_ideas_found=8,
            sessions_analyzed=1127,
            conversations_analyzed=212,
            corrections_detected=32,
            correction_file_types=6,
            correction_chains=145,
            correction_top_extension="py",
            correction_long_chains=6,
        )
        assert m.repos_analyzed == 3
        assert m.correction_top_extension == "py"

    def test_negative_value_rejected(self):
        with pytest.raises(ValidationError):
            ReflectMetrics(repos_analyzed=-1)

    def test_defaults(self):
        m = ReflectMetrics()
        assert m.repos_analyzed == 0
        assert m.correction_top_extension == ""


@pytest.mark.unit
class TestReflectChecklist:
    def test_status_fields(self):
        c = ReflectChecklist(
            cross_review=ChecklistStatus.PASS,
            test_coverage=ChecklistStatus.FAIL,
            context_management=ChecklistStatus.WARN,
        )
        assert c.cross_review == ChecklistStatus.PASS
        assert c.test_coverage == ChecklistStatus.FAIL

    def test_int_fields(self):
        c = ReflectChecklist(pending_reviews=5, repos_with_tests=25)
        assert c.pending_reviews == 5
        assert c.repos_with_tests == 25

    def test_negative_int_rejected(self):
        with pytest.raises(ValidationError):
            ReflectChecklist(pending_reviews=-1)

    def test_date_fields(self):
        c = ReflectChecklist(
            aceengineer_stats_date=date(2026, 1, 31),
            session_rag_date=date(2026, 2, 1),
        )
        assert c.aceengineer_stats_date == date(2026, 1, 31)

    def test_kb_avg_confidence_bounds(self):
        c = ReflectChecklist(kb_avg_confidence=0.92)
        assert c.kb_avg_confidence == 0.92

        with pytest.raises(ValidationError):
            ReflectChecklist(kb_avg_confidence=1.5)

    def test_string_fields(self):
        c = ReflectChecklist(cc_version="1.0.61", cc_last_reviewed="2.1.27")
        assert c.cc_version == "1.0.61"

    def test_extra_fields_allowed(self):
        c = ReflectChecklist(new_check="pass", new_count=42)
        assert c.cross_review == ChecklistStatus.NONE  # default


@pytest.mark.unit
class TestActionsTaken:
    def test_valid(self):
        a = ActionsTaken(
            skills_created=0,
            skills_enhanced=0,
            learnings_stored=10,
            knowledge_captured=0,
            stale_reviews_approved=0,
        )
        assert a.learnings_stored == 10

    def test_negative_rejected(self):
        with pytest.raises(ValidationError):
            ActionsTaken(skills_created=-1)


@pytest.mark.unit
class TestReflectFiles:
    def test_valid_paths(self):
        f = ReflectFiles(
            analysis="/mnt/github/workspace-hub/.claude/state/analysis.json",
            patterns="/mnt/github/workspace-hub/.claude/state/patterns.json",
        )
        assert f.analysis == "/mnt/github/workspace-hub/.claude/state/analysis.json"

    def test_none_string_coerced(self):
        f = ReflectFiles(skill_eval_report="none")
        assert f.skill_eval_report is None

    def test_none_string_case_insensitive(self):
        f = ReflectFiles(skill_eval_report="None")
        assert f.skill_eval_report is None

    def test_actual_none(self):
        f = ReflectFiles(analysis=None)
        assert f.analysis is None


@pytest.mark.unit
class TestReflectState:
    def test_minimal_valid(self):
        s = ReflectState(
            version="2.1",
            last_run=datetime(2026, 2, 1, 5, 0, 1),
            analysis_window_days=30,
        )
        assert s.version == "2.1"
        assert s.dry_run is False

    def test_full_valid(self):
        s = ReflectState(
            version="2.1",
            last_run="2026-02-01T05:00:01-06:00",
            analysis_window_days=30,
            dry_run=False,
            phases_completed={
                "reflect": True,
                "abstract": True,
                "generalize": True,
                "store": True,
            },
            metrics={"repos_analyzed": 3, "commits_found": 96},
            checklist={"cross_review": "pass", "test_coverage": "fail"},
            actions_taken={"learnings_stored": 10},
            files={"analysis": "/tmp/a.json", "skill_eval_report": "none"},
        )
        assert s.phases_completed.reflect is True
        assert s.metrics.repos_analyzed == 3
        assert s.checklist.cross_review == ChecklistStatus.PASS
        assert s.files.skill_eval_report is None

    def test_missing_version_rejected(self):
        with pytest.raises(ValidationError):
            ReflectState(
                last_run=datetime(2026, 2, 1),
                analysis_window_days=30,
            )

    def test_zero_analysis_window_rejected(self):
        with pytest.raises(ValidationError):
            ReflectState(
                version="2.1",
                last_run=datetime(2026, 2, 1),
                analysis_window_days=0,
            )

    def test_extra_fields_allowed(self):
        s = ReflectState(
            version="2.1",
            last_run=datetime(2026, 2, 1),
            analysis_window_days=30,
            future_field="something",
        )
        assert s.version == "2.1"
