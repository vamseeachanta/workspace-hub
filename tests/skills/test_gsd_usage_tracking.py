"""Tests for GSD-aware skill scoring (#1742)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "skills" / "skill-usage-report.py"
SPEC = importlib.util.spec_from_file_location("skill_usage_report_gsd", SCRIPT_PATH)
module = importlib.util.module_from_spec(SPEC)
sys.modules["skill_usage_report_gsd"] = module
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def test_gsd_skill_gets_framework_usage_flag():
    skills = {
        'coordination/gsd-plan-phase': {
            'short_name': 'gsd-plan-phase',
            'full_rel': 'coordination/gsd-plan-phase',
        },
        'development/python-project-template': {
            'short_name': 'python-project-template',
            'full_rel': 'development/python-project-template',
        },
    }

    tiers = module.classify_tiers(skills, ref_counts={}, git_mentioned=set())
    warm_names = {entry['skill'] for entry in tiers['warm']}
    dead_names = {entry['skill'] for entry in tiers['dead']}

    assert 'gsd-plan-phase' in warm_names
    assert 'python-project-template' in dead_names


def test_gsd_skill_scores_record_framework_usage_metric():
    skills = {
        'coordination/gsd-plan-phase': {
            'short_name': 'gsd-plan-phase',
            'full_rel': 'coordination/gsd-plan-phase',
        },
    }
    tiers = module.classify_tiers(skills, ref_counts={}, git_mentioned=set())
    data = module.generate_skill_scores(skills, ref_counts={}, tiers=tiers, existing_scores={})
    assert data['skills']['gsd-plan-phase']['framework_usage'] is True
