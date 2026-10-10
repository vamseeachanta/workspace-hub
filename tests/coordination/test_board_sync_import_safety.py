import json

from tests.coordination.test_board_sync import _run


def _write_decisions(tmp_path, payload):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _assert_no_writes(calls):
    assert not any(call[:2] in (["issue", "comment"], ["issue", "edit"], ["issue", "close"]) for call in calls)


def test_import_rejects_unknown_answer(tmp_path):
    decisions = _write_decisions(
        tmp_path,
        [{"id": "D03", "repo": "vamseeachanta/workspace-hub", "issue": 4001, "choice": "hold"}],
    )

    result, calls = _run(tmp_path, ["import", "--decisions", str(decisions)], {}, check=False)

    assert result.returncode != 0
    assert "invalid answer" in result.stderr
    _assert_no_writes(calls)


def test_import_accepts_known_answers_case_insensitively(tmp_path):
    decisions = _write_decisions(
        tmp_path,
        [
            {"id": "D03A", "repo": "vamseeachanta/workspace-hub", "issue": 4001, "choice": "APPROVE"},
            {"id": "D03B", "repo": "vamseeachanta/workspace-hub", "issue": 4002, "choice": "DeFeR"},
            {"id": "D03C", "repo": "vamseeachanta/workspace-hub", "issue": 4003, "choice": "Drop"},
        ],
    )

    result, calls = _run(tmp_path, ["import", "--decisions", str(decisions)], {}, check=False)

    assert result.returncode == 0
    assert "DRY-RUN vamseeachanta/workspace-hub#4001" in result.stdout
    assert "add=dispatch:ready" in result.stdout
    assert "DRY-RUN vamseeachanta/workspace-hub#4002" in result.stdout
    assert "add=dispatch:blocked" in result.stdout
    assert "DRY-RUN vamseeachanta/workspace-hub#4003" in result.stdout
    assert "add=dispatch:done" in result.stdout
    _assert_no_writes(calls)


def test_import_rejects_injected_target_label(tmp_path):
    decisions = _write_decisions(
        tmp_path,
        [
            {
                "id": "D04",
                "repo": "vamseeachanta/workspace-hub",
                "issue": 4001,
                "answer": "approve",
                "target_label": "dispatch:active",
            }
        ],
    )

    result, calls = _run(tmp_path, ["import", "--decisions", str(decisions)], {}, check=False)

    assert result.returncode != 0
    assert "target label 'dispatch:active' is not allowed" in result.stderr
    _assert_no_writes(calls)


def test_import_rejects_allowed_label_that_mismatches_answer(tmp_path):
    decisions = _write_decisions(
        tmp_path,
        [
            {
                "id": "D04B",
                "repo": "vamseeachanta/workspace-hub",
                "issue": 4001,
                "answer": "approve",
                "target_label": "dispatch:blocked",
            }
        ],
    )

    result, calls = _run(tmp_path, ["import", "--decisions", str(decisions)], {}, check=False)

    assert result.returncode != 0
    assert "does not match required label dispatch:ready" in result.stderr
    _assert_no_writes(calls)


def test_import_rejects_unknown_repo(tmp_path):
    decisions = _write_decisions(
        tmp_path,
        [{"id": "D05", "repo": "example/unknown", "issue": 4001, "answer": "approve"}],
    )

    result, calls = _run(tmp_path, ["import", "--decisions", str(decisions)], {}, check=False)

    assert result.returncode != 0
    assert "repo is not canonical" in result.stderr
    _assert_no_writes(calls)


def test_export_rejects_unknown_repo(tmp_path):
    result, calls = _run(
        tmp_path,
        ["export", "--repo", "example/unknown", "--out-dir", str(tmp_path / "board")],
        {},
        check=False,
    )

    assert result.returncode != 0
    assert "repo is not canonical" in result.stderr
    assert calls == []


def test_import_apply_failed_label_edit_leaves_comment_unwritten(tmp_path):
    decisions = _write_decisions(
        tmp_path,
        [{"id": "D06", "repo": "vamseeachanta/workspace-hub", "issue": 4001, "answer": "approve"}],
    )
    responses = {
        "issue view 4001": {"labels": [{"name": "decision:ecosystem"}], "comments": []},
        "issue edit 4001": {"__rc__": 1, "stderr": "edit failed"},
    }

    result, calls = _run(tmp_path, ["import", "--decisions", str(decisions), "--apply"], responses, check=False)

    assert result.returncode != 0
    assert any(call[:3] == ["issue", "edit", "4001"] for call in calls)
    assert not any(call[:2] == ["issue", "comment"] for call in calls)


def test_import_apply_drop_closes_issue_after_label_edit_and_comment(tmp_path):
    decisions = _write_decisions(
        tmp_path,
        [{"id": "D07", "repo": "vamseeachanta/workspace-hub", "issue": 4001, "answer": "drop"}],
    )
    responses = {
        "issue view 4001": {
            "labels": [{"name": "decision:ecosystem"}, {"name": "dispatch:blocked"}],
            "comments": [],
        }
    }

    _, calls = _run(tmp_path, ["import", "--decisions", str(decisions), "--apply"], responses)

    assert [
        "issue",
        "edit",
        "4001",
        "--repo",
        "vamseeachanta/workspace-hub",
        "--add-label",
        "dispatch:done",
        "--remove-label",
        "decision:ecosystem",
        "--remove-label",
        "dispatch:blocked",
    ] in calls
    assert ["issue", "comment", "4001", "--repo", "vamseeachanta/workspace-hub", "--body", "Owner decision D07: drop"] in calls
    assert ["issue", "close", "4001", "--repo", "vamseeachanta/workspace-hub"] in calls
