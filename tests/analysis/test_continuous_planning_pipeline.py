from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "continuous-planning-pipeline.py"
spec = importlib.util.spec_from_file_location("continuous_planning_pipeline", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def issue(number: int, labels: list[str], title: str = "sample issue", **extra):
    data = {
        "number": number,
        "title": title,
        "url": f"https://example.test/issues/{number}",
        "state": "OPEN",
        "body": "",
        "labels": [{"name": label} for label in labels],
        "comments": [],
    }
    data.update(extra)
    return data


def plan(root: Path, number: int, body: str = "body") -> Path:
    return write(
        root / "docs" / "plans" / f"2026-04-26-issue-{number}-sample.md",
        f"# Plan for #{number}\n\n> **Status:** plan-review\n\n{body}\n",
    )


def review(root: Path, number: int, provider: str, verdict: str = "MINOR", *, sha: str | None = None, text: str = "") -> Path:
    header = f"Plan-SHA256: {sha}\n" if sha else ""
    return write(root / "scripts" / "review" / "results" / f"2026-04-26-plan-{number}-{provider}.md", f"{header}Verdict: {verdict}\n{text}\n")


def marker(root: Path, number: int, text: str | None = None) -> Path:
    return write(
        root / ".planning" / "plan-approved" / f"{number}.md",
        text
        or f"Approved by: user\nIssue: #{number}\nPlan: docs/plans/2026-04-26-issue-{number}-sample.md\nApproval source: test\n",
    )


def clean_reviews(root: Path, number: int, sha: str | None = None) -> None:
    for provider in ("claude", "codex", "gemini"):
        review(root, number, provider, "MINOR", sha=sha)
    review(root, number, "disagreement", "MAJOR", text="summary files must be ignored")


def classify(root: Path, issues: list[dict], **kwargs):
    return module.build_snapshot(issues, root=root, generated_at="2026-04-26T00:00:00Z", **kwargs)


def item(snapshot: dict, number: int) -> dict:
    return next(entry for entries in snapshot["lanes"].values() for entry in entries if entry["number"] == number)


def test_lane_b_requires_label_plan_review_and_marker(tmp_path: Path) -> None:
    plan_path = plan(tmp_path, 101)
    clean_reviews(tmp_path, 101, sha=module.sha256_file(plan_path))
    marker(tmp_path, 101)

    snapshot = classify(tmp_path, [issue(101, ["status:plan-approved"])])

    entry = item(snapshot, 101)
    assert entry["lane"] == "B"
    assert entry["review_clean"] is True
    assert entry["marker_quality"] == "revision-bound"


def test_approved_without_marker_not_lane_b(tmp_path: Path) -> None:
    plan_path = plan(tmp_path, 102)
    clean_reviews(tmp_path, 102, sha=module.sha256_file(plan_path))

    snapshot = classify(tmp_path, [issue(102, ["status:plan-approved"])])

    entry = item(snapshot, 102)
    assert entry["lane"] != "B"
    assert "approved_no_marker" in entry["warnings"]


def test_plan_review_with_clean_reviews_and_canonical_comment_is_lane_a(tmp_path: Path) -> None:
    plan_path = plan(tmp_path, 103)
    sha = module.sha256_file(plan_path)
    clean_reviews(tmp_path, 103, sha=sha)
    comments = [
        {
            "body": f"Plan path: docs/plans/2026-04-26-issue-103-sample.md\nPlan-SHA256: {sha}\nReview artifacts: scripts/review/results/2026-04-26-plan-103-claude.md, scripts/review/results/2026-04-26-plan-103-codex.md, scripts/review/results/2026-04-26-plan-103-gemini.md\nVerdicts: claude MINOR, codex MINOR, gemini MINOR\nChoices: Approve / Revise / Hold\nExecution remains unauthorized until approval marker creation.",
        }
    ]

    snapshot = classify(tmp_path, [issue(103, ["status:plan-review"], comments=comments)])

    entry = item(snapshot, 103)
    assert entry["lane"] == "A"
    assert entry["primary_action"] == "request_approval"


def test_missing_and_empty_and_major_reviews_are_not_clean(tmp_path: Path) -> None:
    plan_path = plan(tmp_path, 104)
    sha = module.sha256_file(plan_path)
    review(tmp_path, 104, "claude", "MINOR", sha=sha)
    review(tmp_path, 104, "codex", "MAJOR", sha=sha)
    write(tmp_path / "scripts" / "review" / "results" / "2026-04-26-plan-104-gemini.md", "")

    snapshot = classify(tmp_path, [issue(104, ["status:plan-review"])])

    entry = item(snapshot, 104)
    assert entry["review_clean"] is False
    assert "major_review" in entry["warnings"]
    assert "empty_review" in entry["warnings"]
    assert entry["lane"] != "A"


def test_legacy_review_without_sha_requires_explicit_allowance(tmp_path: Path) -> None:
    plan(tmp_path, 105)
    clean_reviews(tmp_path, 105, sha=None)
    marker(tmp_path, 105)

    strict = classify(tmp_path, [issue(105, ["status:plan-approved"])])
    allowed = classify(tmp_path, [issue(105, ["status:plan-approved"])], allow_legacy_review_artifacts=True)

    assert item(strict, 105)["lane"] != "B"
    assert "legacy_review_no_sha" in item(strict, 105)["warnings"]
    assert item(allowed, 105)["lane"] == "B"
    assert "legacy_review_no_sha" in item(allowed, 105)["warnings"]


def test_plan_sha_parser_prefers_canonical_header_over_reviewed_header(tmp_path: Path) -> None:
    plan_path = plan(tmp_path, 115)
    plan_sha = module.sha256_file(plan_path)
    old_sha = "a" * 64
    for provider in ("claude", "codex", "gemini"):
        write(
            tmp_path / "scripts" / "review" / "results" / f"2026-04-26-plan-115-{provider}.md",
            f"Reviewed-Plan-SHA256: {old_sha}\nPlan-SHA256: {plan_sha}\nVerdict: MINOR\n",
        )
    marker(tmp_path, 115)

    snapshot = classify(tmp_path, [issue(115, ["status:plan-approved"])])

    entry = item(snapshot, 115)
    assert entry["lane"] == "B"
    assert "sha_mismatch_review" not in entry["warnings"]


def test_missing_ledger_is_global_warning_not_issue_primary_blocker(tmp_path: Path) -> None:
    snapshot = classify(tmp_path, [issue(116, [], title="unplanned")])

    entry = item(snapshot, 116)
    assert "ledger_missing" in snapshot["global_warnings"]
    assert "ledger_missing" not in entry["warnings"]
    assert entry["primary_blocker"] is None


def test_self_approved_marker_and_non_numeric_marker_are_not_lane_b(tmp_path: Path) -> None:
    plan_path = plan(tmp_path, 106)
    clean_reviews(tmp_path, 106, sha=module.sha256_file(plan_path))
    marker(tmp_path, 106, "self-approved by automation\n")
    write(tmp_path / ".planning" / "plan-approved" / "aces-2.md", "Approved by: user\n")

    snapshot = classify(tmp_path, [issue(106, ["status:plan-approved"])])

    entry = item(snapshot, 106)
    assert entry["lane"] != "B"
    assert "self_approved_marker" in entry["warnings"]
    assert snapshot["out_of_scope_markers"] == ["aces-2.md"]


def test_active_dispatch_and_open_pr_override_lane_b(tmp_path: Path) -> None:
    plan_path = plan(tmp_path, 107)
    clean_reviews(tmp_path, 107, sha=module.sha256_file(plan_path))
    marker(tmp_path, 107)
    write(
        tmp_path / "docs" / "reports" / "continuous-work" / "dispatch-ledger-2026-04-26.json",
        json.dumps([{"issue": 107, "state": "running", "lease_scope": "issue-107"}]),
    )

    snapshot = classify(tmp_path, [issue(107, ["status:plan-approved"])])

    entry = item(snapshot, 107)
    assert entry["lane"] == "D"
    assert "active_lease_conflict" in entry["warnings"]


def test_open_pr_with_complete_handoff_is_lane_e_review_ready(tmp_path: Path) -> None:
    body = """
Implementation handoff:
issue: #108
PR/branch: https://example.test/pull/1
dispatch id: d-1
plan SHA: abc
approval marker: .planning/plan-approved/108.md
changed files: scripts/ai/x.py
tests/CI: pytest passed
artifacts: report.md
risks: low
implementation-review status: pending
recommended human action: review
review effort: low
priority reason: high impact
"""
    snapshot = classify(tmp_path, [issue(108, [], pull_request={"url": "https://example.test/pull/1", "body": body})])

    entry = item(snapshot, 108)
    assert entry["lane"] == "E"
    assert entry["substate"] == "review-ready"


def test_buffer_health_caps_and_markdown_top_actions(tmp_path: Path) -> None:
    issues = [issue(i, [], title=f"feedstock {i}") for i in range(201, 214)]
    snapshot = classify(tmp_path, issues)
    md = module.render_markdown(snapshot)

    assert snapshot["buffer_health"]["lane_a"]["status"] == "below_minimum"
    assert "planning/QA only" in snapshot["recommendations"][0]
    assert "## Morning user approval packet" in md
    assert "## Overnight dispatch packet" in md
    assert md.split("## Top actions today", 1)[1].split("##", 1)[0].count("- ") <= 5


def test_json_schema_is_deterministic(tmp_path: Path) -> None:
    snapshot = classify(tmp_path, [issue(302, []), issue(301, ["priority:high"])])
    encoded = module.dumps_json(snapshot)

    assert json.loads(encoded)["generated_at"] == "2026-04-26T00:00:00Z"
    assert encoded.endswith("\n")
    assert encoded == module.dumps_json(snapshot)


def test_live_issue_list_enriches_unlabeled_issues_for_lane_e(monkeypatch) -> None:
    calls: list[list[str]] = []

    class Result:
        def __init__(self, stdout: str):
            self.stdout = stdout
            self.returncode = 0

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[:3] == ["gh", "issue", "list"]:
            return Result(json.dumps([issue(401, [], title="implementation output")]))
        if cmd[:3] == ["gh", "issue", "view"]:
            return Result(json.dumps({"comments": [], "closedByPullRequestsReferences": [{"url": "https://example.test/pull/401"}]}))
        raise AssertionError(cmd)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    issues = module.gh_issue_list()

    assert issues[0]["closedByPullRequestsReferences"][0]["url"].endswith("/401")
    assert any(call[:3] == ["gh", "issue", "view"] and call[3] == "401" for call in calls)


def test_continuous_planning_pipeline_exports_reusable_readiness_primitives() -> None:
    """Per #2665 acceptance criterion: provider-kanban.py must consume the
    existing plan/review/marker/lane classification primitives instead of
    re-implementing readiness logic. This test pins the stable public surface
    so a future refactor cannot silently break the Kanban consumer.
    """
    public_primitives = [
        "discover_plan_files",
        "discover_reviews",
        "discover_markers",
        "marker_quality",
        "review_summary",
        "classify_issue",
        "build_snapshot",
        "label_names",
        "priority_rank",
        "issue_state",
        "sha256_file",
        "LANE_NAMES",
    ]
    for name in public_primitives:
        assert hasattr(module, name), (
            f"continuous-planning-pipeline.{name} is the documented reuse contract for "
            f"provider-kanban; do not remove or rename without coordinating both consumers."
        )

    # Lane key contract — Kanban remaps these onto its own lane vocabulary; the
    # set of keys must stay stable.
    assert set(module.LANE_NAMES.keys()) == {"A", "B", "C", "D", "E"}


def test_kanban_consumer_can_classify_shared_fixture(tmp_path: Path) -> None:
    """Smoke test that the Kanban consumer's flow (build_snapshot on a small
    fixture set) returns the lane/review_clean/approval_marker fields the
    Kanban relies on. If this test starts failing, provider-kanban will too.
    """
    plan_path = plan(tmp_path, 9001)
    sha = module.sha256_file(plan_path)
    clean_reviews(tmp_path, 9001, sha=sha)
    marker(tmp_path, 9001)
    plan(tmp_path, 9003)  # plan-review fixture, no marker

    snapshot = classify(
        tmp_path,
        [
            issue(9001, ["status:plan-approved"]),
            issue(9003, ["status:plan-review"]),
        ],
    )

    fields_kanban_consumes = {"lane", "review_clean", "approval_marker", "warnings", "primary_action"}
    for entry in snapshot["items"]:
        missing = fields_kanban_consumes - set(entry.keys())
        assert not missing, f"entry for #{entry['number']} missing Kanban-required fields: {missing}"


def test_overnight_packet_limits_new_dispatch_candidates_to_three(tmp_path: Path) -> None:
    issues = []
    for number in range(501, 506):
        plan_path = plan(tmp_path, number)
        clean_reviews(tmp_path, number, sha=module.sha256_file(plan_path))
        marker(tmp_path, number)
        issues.append(issue(number, ["status:plan-approved"]))

    snapshot = classify(tmp_path, issues)
    md = module.render_markdown(snapshot)
    dispatch_section = md.split("## Overnight dispatch packet", 1)[1].split("## Buffer health", 1)[0]

    assert snapshot["thresholds"]["max_new_implementation_prs_per_night"] == 3
    assert dispatch_section.count("execution-ready") == 3
    assert "limited to 3" in dispatch_section