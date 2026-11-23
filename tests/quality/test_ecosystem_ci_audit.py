from scripts.ci_health.ecosystem_ci_audit import (
    EXPECTED_REPOS,
    classify_repo,
    latest_relevant_runs_by_workflow,
    render_markdown_report,
)


def test_latest_relevant_runs_ignore_pull_request_noise() -> None:
    runs = [
        {
            "workflowName": "CI",
            "headBranch": "dependabot/example",
            "event": "pull_request",
            "status": "completed",
            "conclusion": "success",
            "createdAt": "2026-04-27T13:04:44Z",
            "url": "https://example.invalid/pr-success",
        },
        {
            "workflowName": "CI",
            "headBranch": "main",
            "event": "push",
            "status": "completed",
            "conclusion": "failure",
            "createdAt": "2026-04-27T12:00:00Z",
            "url": "https://example.invalid/main-failure",
        },
    ]

    latest = latest_relevant_runs_by_workflow(runs)

    assert latest == [
        {
            "workflowName": "CI",
            "headBranch": "main",
            "event": "push",
            "status": "completed",
            "conclusion": "failure",
            "createdAt": "2026-04-27T12:00:00Z",
            "url": "https://example.invalid/main-failure",
        }
    ]
    assert classify_repo(latest)["state"] == "red"


def test_report_covers_expected_ecosystem_repos_and_open_followups() -> None:
    repo_runs = {
        "vamseeachanta/workspace-hub": [
            {
                "workflowName": "Baseline Testing",
                "headBranch": "main",
                "event": "push",
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2026-04-27T10:00:00Z",
                "url": "https://example.invalid/ws",
            }
        ],
        "vamseeachanta/worldenergydata": [
            {
                "workflowName": "CI",
                "headBranch": "main",
                "event": "schedule",
                "status": "completed",
                "conclusion": "failure",
                "createdAt": "2026-04-27T09:00:00Z",
                "url": "https://example.invalid/wed",
            }
        ],
        "vamseeachanta/digitalmodel": [
            {
                "workflowName": "Quality Gates",
                "headBranch": "main",
                "event": "push",
                "status": "completed",
                "conclusion": "failure",
                "createdAt": "2026-04-27T08:00:00Z",
                "url": "https://example.invalid/dm",
            }
        ],
        "vamseeachanta/assethold": [
            {
                "workflowName": "Python Tests",
                "headBranch": "main",
                "event": "schedule",
                "status": "completed",
                "conclusion": "failure",
                "createdAt": "2026-04-27T07:00:00Z",
                "url": "https://example.invalid/ah",
            }
        ],
        "vamseeachanta/achantas-data": [
            {
                "workflowName": "markdown-lint",
                "headBranch": "main",
                "event": "push",
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2026-04-27T06:00:00Z",
                "url": "https://example.invalid/data",
            }
        ],
        "vamseeachanta/aceengineer-admin": [
            {
                "workflowName": "CI",
                "headBranch": "main",
                "event": "push",
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2026-04-27T05:00:00Z",
                "url": "https://example.invalid/admin",
            }
        ],
        "vamseeachanta/assetutilities": [
            {
                "workflowName": "Tests",
                "headBranch": "main",
                "event": "push",
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2026-04-27T04:00:00Z",
                "url": "https://example.invalid/au",
            }
        ],
    }

    issue_rows = {
        2433: {"state": "OPEN", "labels": ["status:plan-approved"]},
        2490: {"state": "OPEN", "labels": ["status:plan-review"]},
    }

    report = render_markdown_report(
        repo_runs, issue_rows, generated_at="2026-04-27T22:00:00Z"
    )

    for repo in EXPECTED_REPOS:
        assert f"`{repo.full_name}`" in report
    assert "`#2433` OPEN" in report
    assert "`#2490` OPEN" in report
    assert "| Red | 3 |" in report
