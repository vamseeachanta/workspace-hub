from __future__ import annotations

from pathlib import Path

from scripts.preflight.checks import build_report, parse_probe_output


FIXTURES = Path(__file__).parent / "fixtures"


def _report(name: str, role: str = "secondary-dev") -> dict:
    probe = parse_probe_output((FIXTURES / f"{name}.txt").read_text())
    return build_report(
        probe,
        target={
            "name": "ace-linux-2",
            "hostname": probe["hostname"],
            "role": role,
            "workspace_root": probe["workspace_root"],
        },
        from_host="ace-linux-1",
        invocation={"mode": "fixture"},
    )


def _check(report: dict, name: str) -> dict:
    return next(check for check in report["checks"] if check["name"] == name)


def test_reachable_fixture_has_no_blocking_failures() -> None:
    report = _report("reachable")

    assert report["summary"]["block"] == 0
    assert report["summary"]["machine_ready"] is True
    assert _check(report, "host.reachability")["status"] == "pass"


def test_auth_invalid_on_overflow_blocks_github_mutation_only() -> None:
    report = _report("auth-invalid")
    auth = _check(report, "auth.gh_status")

    assert auth["status"] == "warn"
    assert auth["blocks"] == ["github_mutation"]
    assert report["summary"]["machine_ready"] is True
    assert report["summary"]["github_mutation_allowed"] is False
    assert "gho_" not in auth["detail"]


def test_tool_missing_fixture_warns_for_optional_agent_cli() -> None:
    report = _report("tool-missing")

    assert _check(report, "tool.path.codex")["status"] == "warn"
    assert _check(report, "tool.path.gemini")["status"] == "warn"
    assert report["summary"]["block"] == 0


def test_clean_repo_fixture_passes_repo_checks() -> None:
    report = _report("clean-repo", role="primary-dev")

    assert _check(report, "repo.tier1_branch_status")["status"] == "pass"
    assert _check(report, "repo.ahead_behind")["status"] == "pass"
    assert report["summary"]["machine_ready"] is True
