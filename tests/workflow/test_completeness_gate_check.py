"""Tests for the #2798 close-gate decision (hardened per code review)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import completeness_gate_check as gate  # noqa: E402
import completeness_gate_runner as runner  # noqa: E402

VERIFIED = "status:completeness-verified"
OWNERS = {"vamseeachanta"}


def _record(pct=95, cls="code", issue=2798, **extra):
    r = {"completeness_pct": pct, "cls": cls, "issue_number": issue}
    r.update(extra)
    return r


def _eval(**kw):
    base = dict(record=_record(), labels=[VERIFIED], label_actor="vamseeachanta",
                closing_actor="hermes-bot", authorized_appliers=OWNERS,
                expected_issue=2798, body_verified_fresh=True, work_authors={"pr-author"})
    base.update(kw)
    return gate.evaluate_close(**base)


def test_allows_when_all_conditions_met():
    assert _eval().allowed is True


def test_denies_when_no_record():
    d = _eval(record=None)
    assert d.allowed is False and "record" in d.reason.lower()


def test_denies_when_record_issue_mismatch_forged():
    d = _eval(record=_record(issue=9999))  # copied/forged record from another issue
    assert d.allowed is False and ("match" in d.reason.lower() or "forged" in d.reason.lower())


def test_threshold_comes_from_config_not_record_so_forged_threshold_ignored():
    # forged record claims threshold 0 to sneak a low score past the gate
    d = _eval(record=_record(pct=10, cls="code", threshold=0))
    assert d.allowed is False  # config threshold 90 applies, 10 < 90
    assert "90" in d.reason


def test_denies_unknown_class():
    d = _eval(record=_record(cls="bogus"))
    assert d.allowed is False and "class" in d.reason.lower()


def test_denies_when_verified_label_absent():
    d = _eval(labels=["status:plan-approved"], label_actor=None)
    assert d.allowed is False and "label" in d.reason.lower()


def test_denies_unauthorized_label_actor():
    d = _eval(label_actor="random-contributor")
    assert d.allowed is False and ("authorized" in d.reason.lower() or "actor" in d.reason.lower())


def test_allows_same_actor_by_default_solo_operation():
    # solo operator both verifies and closes — allowed by default (separation is opt-in)
    d = _eval(label_actor="vamseeachanta", closing_actor="vamseeachanta")
    assert d.allowed is True


def test_denies_same_actor_only_when_separate_closer_required():
    d = _eval(label_actor="vamseeachanta", closing_actor="vamseeachanta", require_separate_closer=True)
    assert d.allowed is False and ("separate" in d.reason.lower() or "same" in d.reason.lower())


def test_denies_when_body_edited_after_verification():
    d = _eval(body_verified_fresh=False)
    assert d.allowed is False and ("edited" in d.reason.lower() or "re-verification" in d.reason.lower())


def test_denies_when_pct_below_config_threshold():
    d = _eval(record=_record(pct=70))
    assert d.allowed is False and "70" in d.reason


def test_evidence_class_uses_80_threshold():
    assert _eval(record=_record(pct=85, cls="evidence")).allowed is True   # 85 >= 80
    assert _eval(record=_record(pct=75, cls="evidence")).allowed is False  # 75 < 80


# ---- opt-in scoping (rollout fix) ----

def test_gate_applies_to_legacy_opt_in_with_plan_approval():
    assert gate.gate_applies(["gate:completeness", "status:plan-approved"]) is True


def test_gate_does_not_apply_without_opt_in_label():
    # the existing backlog (plan-approved but not opted-in) is untouched
    assert gate.gate_applies(["status:plan-approved"]) is False


def test_gate_applies_without_separate_plan_approval():
    assert gate.gate_applies(["gate:completeness", "gate:completeness-v2"]) is True


def test_bulk_labeled_legacy_backlog_remains_out_of_scope():
    assert gate.gate_applies(["gate:completeness"]) is False


def test_legacy_parameter_cannot_add_an_approval_requirement():
    assert gate.gate_applies(["custom:complete", "gate:completeness-v2"], "custom:complete", "legacy:approved") is True


def test_autoapply_covers_new_and_resumed_work_without_backlog_sweep():
    workflow = Path(__file__).resolve().parents[2] / ".github/workflows/autoapply-completeness-label.yml"
    text = workflow.read_text(encoding="utf-8")
    assert "types: [opened, labeled]" in text
    condition = text.split("    if: >-", 1)[1].split("    steps:", 1)[0]
    assert "github.event.action == 'opened'" in condition
    for status in ("status:plan-review", "dispatch:active", "status:plan-approved"):
        assert status in condition
    assert "issues: write" in text
    assert "gate:completeness-v2" in text


def test_gate_does_not_apply_to_unlabeled_issue():
    assert gate.gate_applies([]) is False


def test_closure_guidance_preserves_approval_independent_enrollment():
    from pathlib import Path
    text = (Path(__file__).resolve().parents[2] / ".claude/rules/completeness-before-close.md").read_text(encoding="utf-8")
    assert "gate:completeness-v2" in text
    assert "historical" in text
    assert "owner-only `status:completeness-verified`" not in text
    assert "did not write the work" in text
    assert "`work_by`" in text and "`verified_by`" in text


# ---- verifier did not write the work (rules review r5, card A) ----

def test_reviewer_who_is_not_the_author_may_verify():
    d = _eval(label_actor="reviewer", authorized_appliers={"vamseeachanta", "reviewer"},
              work_authors={"vamseeachanta"})
    assert d.allowed is True


def test_denies_labeler_who_authored_the_closing_pr_without_named_verifier():
    d = _eval(work_authors={"vamseeachanta"})
    assert d.allowed is False and "author of the closing PR or commit" in d.reason


def test_author_check_is_case_insensitive():
    assert _eval(work_authors={"VamseeAchanta"}).allowed is False


def test_known_author_using_personal_login_cannot_name_a_different_verifier():
    rec = _record(work_by="worker", verified_by="reviewer")
    decision_args = dict(record=rec, label_actor="personal", authorized_appliers={"personal"},
                         work_authors={"opener", "Personal"})
    assert not _eval(**decision_args).allowed
    assert not _eval(shared_logins={"shared-account"}, **decision_args).allowed


def _shared(**kw):
    return _eval(shared_logins={"VamseeAchanta"}, **kw)


def test_shared_login_passes_when_record_names_a_separate_verifier(run_close, monkeypatch):
    rec = _record(work_by="claude-worker", verified_by="codex-reviewer")
    issue = _issue(_pr("reviewer", _commit("writer")))
    monkeypatch.setenv("COMPLETENESS_SHARED_LOGINS", "team, Reviewer ")
    assert run_close(lambda **_: {"data": {"repository": {"issue": issue}}}, rec) == 0


@pytest.mark.parametrize(("work_by", "verified_by"), [
    ("worker", " Worker "), (" ", "reviewer"), ("worker", None),
    (1, "reviewer"), ("worker", ["reviewer"]),
])
def test_shared_login_requires_two_distinct_nonempty_strings(work_by, verified_by):
    rec = _record(work_by=work_by, verified_by=verified_by)
    assert not _shared(record=rec, work_authors={"vamseeachanta"}).allowed


def test_unknown_author_cannot_be_resolved_by_the_shared_login_record():
    rec = _record(work_by="worker", verified_by="reviewer")
    for unknown in (set(), None):
        assert not _shared(record=rec, work_authors=unknown).allowed


def test_unauthorized_labeler_still_denied_even_if_not_the_author():
    d = _eval(label_actor="random-contributor", work_authors={"vamseeachanta"})
    assert d.allowed is False and "unauthorized" in d.reason


def _page(*nodes, after=None, total=None):
    return {"nodes": list(nodes), "totalCount": len(nodes) if total is None else total,
            "pageInfo": {"hasNextPage": after is not None, "endCursor": after}}


def _commit(*logins, **paging):
    return {"__typename": "Commit", "id": f"commit-{logins[0]}",
            "authors": _page(*({"user": {"login": login}} for login in logins), **paging)}


def _pr(opener, *commits, state="MERGED", **paging):
    return {"__typename": "PullRequest", "id": f"pr-{opener}", "state": state,
            "author": {"login": opener}, "commits": _page(*({"commit": c} for c in commits), **paging)}


def _issue(closer=None, *links, **paging):
    return {"id": "issue-id", "closed": True, "createdAt": "2026-05-26T00:00:00Z",
            "lastEditedAt": None, "timelineItems": {"nodes": [{"closer": closer}]},
            "closedByPullRequestsReferences": _page(*links, **paging)}


def test_work_authors_from_pr_closer_commit_closer_and_merged_links():
    linked = _pr("linked-author", _commit("writer", "coauthor"))
    node = _issue(_pr("opener", _commit("other")), linked,
                  _pr("open-author", state="OPEN"), _pr("closed-author", state="CLOSED"))
    assert gate.work_authors_from(node) == {"opener", "other", "linked-author", "writer", "coauthor"}
    assert gate.work_authors_from(_issue(_commit("writer", "coauthor"))) == {"writer", "coauthor"}


def test_work_authors_from_manual_close_or_missing_data_is_unresolved():
    for node in (_issue(), None, {"timelineItems": {"nodes": [{"closer": {"author": None}}]}}):
        assert not gate.work_authors_from(node)


@pytest.mark.parametrize("incomplete", [
    {"author": None}, {"commits": None}, {"commits": _page()},
    {"commits": _page({"commit": _commit("writer", None)})},
    {"commits": _page({"commit": _commit("writer")}, total=2)},
    {"commits": {"nodes": [{"commit": _commit("writer")}]}},
])
def test_partial_author_evidence_invalidates_known_authors(incomplete):
    pr = _pr("opener", _commit("writer"))
    pr.update(incomplete)
    authors = gate.work_authors_from(_issue(None, _pr("other", _commit("other")), pr))
    assert not _eval(work_authors=authors).allowed


@pytest.fixture
def run_close(monkeypatch):
    monkeypatch.setenv("GH_REPO", "owner/repo")
    monkeypatch.setenv("ISSUE_NUMBER", "2798")
    monkeypatch.setenv("COMPLETENESS_REVIEWERS", "reviewer")
    monkeypatch.delenv("COMPLETENESS_SHARED_LOGINS", raising=False)
    monkeypatch.setattr(runner, "verified_label_event", lambda *_: ("reviewer", _t(16)))

    def run(graphql, record=None):
        def fake_gh(*args):
            if args[:2] == ("issue", "view"):
                labels = ["gate:completeness", "gate:completeness-v2", VERIFIED]
                return {"body": "```completeness " + json.dumps(record or _record()) + "```",
                        "labels": [{"name": label} for label in labels]}
            assert args[:2] == ("api", "graphql")
            return graphql(**dict(field.split("=", 1) for field in args[3::2]))

        monkeypatch.setattr(runner, "gh_json", fake_gh)
        return runner.main()

    return run


def test_authorized_reviewer_who_wrote_commits_is_denied(run_close):
    # The reviewer co-authored a commit on a later page of a second linked PR.
    issue = _issue(None, _pr("first-opener", _commit("first-writer")), after="more-prs", total=2)
    later_pr = _pr("second-opener", _commit("second-writer"), after="more-commits", total=2)
    commit = _commit("other-writer", after="more-authors", total=2)
    pages = {
        "more-prs": ("issue-id", "closedByPullRequestsReferences", _page(later_pr, total=2)),
        "more-commits": (later_pr["id"], "commits", _page({"commit": commit}, total=2)),
        "more-authors": (commit["id"], "authors", _page({"user": {"login": "reviewer"}}, total=2)),
    }
    cursors = []
    queries = []

    def graphql(query, **variables):
        queries.append("".join(query.split()))
        if "cursor" in variables:
            cursor = variables["cursor"]
            parent, field, page = pages[cursor]
            assert variables["id"] == parent
            assert field + "(" in query and "after:$cursor" in query.replace(" ", "")
            cursors.append(cursor)
            return {"data": {"node": {field: page}}}
        return {"data": {"repository": {"issue": issue}}}

    assert run_close(graphql) == 1
    assert cursors == list(pages)
    assert all(query.startswith("query(") and "user{login}" in query for query in queries)
    assert queries[0].count("author{login}commits(") == 2  # close event and linked PRs
    # Same evidence and authorization, with an independent reviewer.
    pages["more-authors"][2]["nodes"][0]["user"]["login"] = "other-coauthor"
    assert run_close(graphql) == 0


@pytest.mark.parametrize("api_failure", [False, True], ids=["partial-response", "token-denied"])
def test_graphql_error_denies_even_with_a_known_independent_opener(run_close, api_failure):
    def graphql(**_):
        if api_failure:
            raise subprocess.CalledProcessError(1, "gh", stderr="Resource not accessible by integration")
        issue = _issue(None, _pr("opener", _commit("writer")))
        return {"data": {"repository": {"issue": issue}}, "errors": [{"message": "field unavailable"}]}

    assert run_close(graphql) == 1


def test_workflow_passes_reviewer_appliers_variable():
    workflow = Path(__file__).resolve().parents[2] / ".github/workflows/completeness-gate.yml"
    text = workflow.read_text(encoding="utf-8")
    assert "COMPLETENESS_REVIEWERS: ${{ vars.COMPLETENESS_REVIEWERS }}" in text
    assert "COMPLETENESS_SHARED_LOGINS: ${{ vars.COMPLETENESS_SHARED_LOGINS }}" in text


# ---- body-freshness helper (fix #5: anchor on lastEditedAt, not updatedAt) ----

import datetime as _dt  # noqa: E402

def _t(h):  # helper: a UTC datetime at hour h on a fixed day
    return _dt.datetime(2026, 5, 26, h, 0, tzinfo=_dt.timezone.utc)


def test_fresh_when_label_after_body_edit():
    assert gate.body_is_fresh(label_at=_t(16), last_edited_at=_t(12), created_at=_t(0)) is True


def test_not_fresh_when_label_before_body_edit():
    assert gate.body_is_fresh(label_at=_t(11), last_edited_at=_t(12), created_at=_t(0)) is False


def test_falls_back_to_created_at_when_never_edited():
    # body never edited (lastEditedAt None) -> compare against createdAt
    assert gate.body_is_fresh(label_at=_t(16), last_edited_at=None, created_at=_t(0)) is True
    assert gate.body_is_fresh(label_at=_t(11), last_edited_at=None, created_at=_t(12)) is False


def test_not_fresh_when_no_label():
    assert gate.body_is_fresh(label_at=None, last_edited_at=_t(12), created_at=_t(0)) is False


def test_close_does_not_break_freshness_regression():
    # the bug: a later updatedAt (e.g. from the close) must NOT enter the calc.
    # helper only sees body-edit time, so a label applied after the body edit stays fresh
    # regardless of any later issue activity.
    assert gate.body_is_fresh(label_at=_t(16), last_edited_at=_t(12), created_at=_t(0)) is True
