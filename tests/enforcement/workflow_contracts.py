"""Closed scheduler event contracts, derived from the repository workflows.

GitHub Actions workflow syntax (accessed 2026-10-22): on.push filters,
on.pull_request.types, jobs.<job_id>.if and jobs.<job_id>.steps[*].if.
https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
"""
from __future__ import annotations


def expected_events(event):
    if event == "push":
        return {"push": {"branches": ["main"]}}
    assert event == "pull_request", f"unreviewed event: {event}"
    return {"pull_request": {
        "branches": ["main"], "types": ["opened", "synchronize", "reopened"],
    }}


def assert_scheduler_workflow(workflow, event):
    """Require the whole event map and unconditional scheduler job and steps."""
    assert workflow["on"] == expected_events(event), "scheduler event schema changed"
    job = workflow["jobs"]["scheduler-mutation-surfaces"]
    for node in (job, *job["steps"]):
        assert "if" not in node, "scheduler checks must be unconditional"
        assert node.get("continue-on-error", "false") in (False, "false"), "failure must propagate"
