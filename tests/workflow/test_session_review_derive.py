"""Tests for #3311 git-footprint derivation of the lean reference payload."""
import sys
from pathlib import Path

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import build_session_review as bsr  # noqa: E402


def _types(refs):
    return [(r["type"], r.get("num", r.get("path"))) for r in refs]


def test_pr_from_squash_subject_issue_from_body():
    msgs = ["feat(x): do a thing (#3299)\n\nCloses #3298. Refs #2110."]
    refs = bsr.derive_refs(msgs, [])
    assert ("pr", 3299) in _types(refs)
    assert ("issue", 3298) in _types(refs)
    assert ("issue", 2110) in _types(refs)
    # the PR number is not also listed as an issue
    assert ("issue", 3299) not in _types(refs)


def test_prs_render_before_issues():
    refs = bsr.derive_refs(["fix: y (#10)\n\nCloses #20."], [])
    types = [r["type"] for r in refs]
    assert types.index("pr") < types.index("issue")


def test_dedup_across_commits():
    msgs = ["a (#5)\n\n#9", "b (#5)\n\n#9"]
    refs = bsr.derive_refs(msgs, [])
    assert [r for r in refs if r["type"] == "pr"] == [{"type": "pr", "num": 5}]
    assert [r for r in refs if r["type"] == "issue"] == [{"type": "issue", "num": 9}]


def test_changed_files_map_to_typed_refs():
    files = [
        "docs/plans/2026-06-28-issue-3311-x.md",
        "docs/session-handoffs/2026-06-28-rec.md",
        "docs/governance/2026-06-28-publish-mode-decision.md",
        "docs/reports/foo.html",
        "scripts/workflow/build_session_review.py",   # not a doc → ignored
    ]
    refs = bsr.derive_refs([], files)
    t = {(r["type"], r["path"]) for r in refs if "path" in r}
    assert ("plan", "docs/plans/2026-06-28-issue-3311-x.md") in t
    assert ("handoff", "docs/session-handoffs/2026-06-28-rec.md") in t
    assert ("decision", "docs/governance/2026-06-28-publish-mode-decision.md") in t
    assert ("report", "docs/reports/foo.html") in t
    assert all(r.get("path") != "scripts/workflow/build_session_review.py" for r in refs)


def test_session_pages_are_excluded():
    files = ["docs/reports/sessions/2026-06-28-x.html",
             "docs/reports/sessions/index.html",
             "docs/reports/sessions/manifest.json"]
    assert bsr.derive_refs([], files) == []


def test_governance_non_decision_file_is_not_a_decision():
    # a governance doc that is not *-decision.md must not become a decision ref
    refs = bsr.derive_refs([], ["docs/governance/SESSION-GOVERNANCE.md"])
    assert refs == []


def test_labels_are_basenames():
    refs = bsr.derive_refs([], ["docs/plans/2026-06-28-issue-3311-x.md"])
    assert refs[0]["label"] == "2026-06-28-issue-3311-x.md"
