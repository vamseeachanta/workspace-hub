"""Equivalent workflow bypasses must fail the same closed schema.

Expected maps are hand-transcribed from the committed scheduler workflows.
Filter/condition semantics: GitHub Actions workflow syntax, accessed 2026-10-22,
https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
sections on.push, on.pull_request, jobs.<job_id>.if and steps.if.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml
from workflow_contracts import assert_scheduler_workflow, expected_events

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(params=["push", "pull_request"])
def contract(request):
    event = request.param
    filename = "scheduler-mutation-main.yml" if event == "push" else "enforcement-gate.yml"
    workflow = yaml.load((ROOT / ".github/workflows" / filename).read_text(), Loader=yaml.BaseLoader)
    return event, workflow


def test_real_workflow_matches_closed_contract(contract):
    event, workflow = contract
    assert_scheduler_workflow(workflow, event)


@pytest.mark.parametrize("field,value", [
    ("paths", ["scripts/**"]),
    ("paths-ignore", ["docs/**"]),
    ("branches-ignore", ["main"]),
    ("tags", ["v*"]),
    ("tags-ignore", ["*"]),
    ("types", ["opened"]),
    ("branches", ["release"]),
])
def test_event_filter_bypasses_are_rejected(contract, field, value):
    event, workflow = contract
    workflow["on"][event][field] = value
    with pytest.raises(AssertionError, match="event schema"):
        assert_scheduler_workflow(workflow, event)


@pytest.mark.parametrize("condition", ["false", "${{ false }}", "${{ github.ref != 'refs/heads/main' }}"])
@pytest.mark.parametrize("location", ["job", "step"])
def test_conditional_skip_bypasses_are_rejected(contract, condition, location):
    event, workflow = contract
    job = workflow["jobs"]["scheduler-mutation-surfaces"]
    targets = [job] if location == "job" else job["steps"]
    for target in targets:
        target["if"] = condition
        with pytest.raises(AssertionError, match="unconditional"):
            assert_scheduler_workflow(workflow, event)
        del target["if"]


def test_exact_events_reject_added_or_missing_triggers(contract):
    event, workflow = contract
    original = copy.deepcopy(workflow["on"])
    for changed in ({}, {**original, "workflow_dispatch": {}}, {event: None}):
        workflow["on"] = changed
        with pytest.raises(AssertionError, match="event schema"):
            assert_scheduler_workflow(workflow, event)


def test_expected_event_mapping_is_not_shared_mutable_state():
    changed = expected_events("push")
    changed["push"]["branches"].append("release")
    assert expected_events("push") == {"push": {"branches": ["main"]}}
