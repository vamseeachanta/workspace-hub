#!/usr/bin/env python3
"""Tests for skill_eval_ecosystem.py orchestrator."""
import sys
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill_eval_ecosystem import run_ecosystem_eval, EvalResult


def test_run_ecosystem_eval_returns_result():
    """Integration test: runs real scripts against the workspace."""
    result = run_ecosystem_eval(Path("."))
    assert isinstance(result, EvalResult)
    assert result.total_skills > 0
    assert result.violations_count >= 0
    assert result.coverage_gap_count >= 0
    assert isinstance(result.pass_rate, str)


def test_eval_result_to_yaml():
    """Unit test: YAML output is valid and contains required keys."""
    result = EvalResult(
        total_skills=100, passed=10, warnings=50, critical=0,
        violations_count=5, coverage_gap_count=3,
    )
    output = result.to_yaml()
    data = yaml.safe_load(output)
    assert data["total_skills"] == 100
    assert data["eval_summary"]["passed"] == 10
    assert data["eval_summary"]["pass_rate"] == "10.0%"
    assert data["violations"]["count"] == 5
    assert data["coverage_gaps"]["count"] == 3


def test_eval_result_exit_code_zero_when_no_critical():
    result = EvalResult(total_skills=10, passed=5, warnings=3, critical=0,
                        violations_count=0, coverage_gap_count=0)
    assert result.exit_code == 0


def test_eval_result_exit_code_one_when_critical():
    result = EvalResult(total_skills=10, passed=5, warnings=3, critical=2,
                        violations_count=0, coverage_gap_count=0)
    assert result.exit_code == 1
