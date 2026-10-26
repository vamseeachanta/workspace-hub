from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "provider-autolabel.py"
spec = importlib.util.spec_from_file_location("provider_autolabel", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_compute_confidence_high_for_execution_ready_codex_fix() -> None:
    issue = {
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "implementation/test/fix language",
        "provider_priority": "highest",
        "labels": [],
    }
    confidence, reasons = module.compute_confidence("codex", issue)
    assert confidence >= 0.9
    assert "strong-codex-language-match" in reasons


def test_compute_confidence_zero_when_ai_label_exists() -> None:
    issue = {
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "strategy/workflow/architecture language",
        "provider_priority": "high",
        "labels": ["ai:claude"],
    }
    confidence, reasons = module.compute_confidence("claude", issue)
    assert confidence == 0.0
    assert "provider-label-exists" in reasons


def test_compute_confidence_zero_when_legacy_agent_label_exists() -> None:
    issue = {
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "strategy/workflow/architecture language",
        "provider_priority": "high",
        "labels": ["agent:claude"],
    }
    confidence, reasons = module.compute_confidence("claude", issue)
    assert confidence == 0.0
    assert "provider-label-exists" in reasons


def test_collect_candidates_marks_only_high_confidence_items_eligible() -> None:
    work_queue = {
        "provider_queues": {
            "claude": {"top_issues": [{"number": 1, "title": "epic: strategy", "labels": [], "execution_ready": True, "priority_rank": 1, "routing_reason": "strategy/workflow/architecture language", "provider_priority": "high"}]},
            "codex": {"top_issues": [{"number": 2, "title": "fix: implementation", "labels": [], "execution_ready": True, "priority_rank": 1, "routing_reason": "implementation/test/fix language", "provider_priority": "highest"}]},
            "agy": {"top_issues": [{"number": 3, "title": "audit: research", "labels": [], "execution_ready": False, "priority_rank": 2, "routing_reason": "research/triage/audit language", "provider_priority": "highest"}]},
        }
    }
    candidates = module.collect_candidates(work_queue)
    assert all(item["target_label"].startswith("ai:") for item in candidates)
    eligible_numbers = {item["number"] for item in candidates if item["eligible"]}
    assert 1 in eligible_numbers
    assert 2 in eligible_numbers
    assert 3 not in eligible_numbers


# Synthetic issue numbers and counts below identify fixture records only.
# Confidence examples use the existing policy's independent sum:
# 0.35 readiness + 0.15 priority + 0.35 routing + 0.10 provider priority = 0.95.
@pytest.fixture(autouse=True)
def no_live_github(monkeypatch):
    def deny(*args, **kwargs):
        pytest.fail("GitHub access requires an explicit local stub")

    monkeypatch.setattr(module.subprocess, "run", deny)


@pytest.fixture
def work_queue():
    return {
        "provider_queues": {
            "claude": {"top_issues": []},
            "codex": {"top_issues": [{
                "number": 2,
                "title": "fixture title withheld",
                "body": "fixture body withheld",
                "assignee": "fixture identity withheld",
                "private_telemetry": "fixture telemetry withheld",
                "labels": [],
                "execution_ready": True,
                "priority_rank": 1,
                "routing_reason": "implementation/test/fix language",
                "provider_priority": "highest",
            }]},
            "agy": {"top_issues": []},
        }
    }


@pytest.fixture
def github(monkeypatch):
    class Stub:
        failure = None
        bad_response = None
        bad_resource = "labels"
        label_pages = None

        def run(self, args, **kwargs):
            assert args[0] == "gh"
            assert kwargs == {"check": True, "capture_output": True, "text": True}
            self.calls.append(args)
            if args[1] == "api":
                kind = args[-1].rsplit("/", 1)[-1]
                assert "--paginate" in args and "--slurp" in args
                if self.failure == kind:
                    raise subprocess.CalledProcessError(1, args)
                assert kind in ("labels", "comments")
                assert args[-1] == f"repos/{{owner}}/{{repo}}/issues/2/{kind}"
                if kind == "labels":
                    response = self.label_pages or [[{"name": label} for label in self.labels]]
                else:
                    response = self.comments
                raw = self.bad_response if kind == self.bad_resource else None
                return subprocess.CompletedProcess(args, 0, raw or json.dumps(response))
            if args[1:3] == ["issue", "edit"]:
                if self.failure == "label":
                    raise subprocess.CalledProcessError(1, args)
                self.labels.append(args[-1])
            elif args[1:3] == ["issue", "comment"]:
                if self.failure == "comment":
                    raise subprocess.CalledProcessError(1, args)
                self.comments.append([{"body": args[-1]}])
            else:
                pytest.fail("Unexpected GitHub command")
            return subprocess.CompletedProcess(args, 0, "")

    stub = Stub()
    # Instance collections prevent state leaking between tests.
    stub.labels, stub.comments, stub.calls = [], [[]], []
    monkeypatch.setattr(module.subprocess, "run", stub.run)
    return stub


def writes(github):
    return [call for call in github.calls if call[1] == "issue"]


def test_apply_with_comment_explains_new_label(work_queue, github):
    payload = module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert payload["applied"] == [{"number": 2, "target_label": "ai:codex", "confidence": 0.95}]
    assert [call[1:3] for call in github.calls] == [
        ["api", "--paginate"], ["api", "--paginate"],
        ["issue", "edit"], ["issue", "comment"],
    ]
    body = writes(github)[-1][-1]
    assert body == (
        "Automated provider label applied: `ai:codex`.\n\n"
        "- Confidence: 0.95\n"
        "- Routing reason: implementation/test/fix language\n"
        "- Provider priority: highest\n"
        "- Execution-ready: yes\n\n"
        "<!-- provider-autolabel:issue=2;label=ai:codex -->"
    )
    assert payload["candidates"][0]["title"] == "[withheld; see issue]"
    for value in work_queue["provider_queues"]["codex"]["top_issues"][0].values():
        if isinstance(value, str) and value.startswith("fixture"):
            assert value not in body


def test_repeated_apply_does_not_duplicate_comment(work_queue, github):
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    # Reuse stale input; the current issue already has the label.
    again = module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert again["applied"] == []
    assert len(writes(github)) == 2  # One label and one explanation, across both runs.
    # A retained marker also prevents a new claim after label removal.
    github.labels.clear()
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert len(writes(github)) == 2


@pytest.mark.parametrize("label", ["ai:codex", "ai:claude", "agent:codex", "agent:gemini"])
@pytest.mark.parametrize("comment", [False, True])
def test_existing_manual_label_is_not_claimed(work_queue, github, label, comment):
    github.labels = [label]
    payload = module.build_payload(work_queue, apply_mode=True, limit=1, comment=comment)
    assert payload["applied"] == []
    assert writes(github) == []


@pytest.mark.parametrize("failure", ["labels", "comments"])
def test_dedup_read_failure_posts_nothing(work_queue, github, failure):
    github.failure = failure
    with pytest.raises(subprocess.CalledProcessError):
        module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert writes(github) == []


@pytest.mark.parametrize("resource", ["labels", "comments"])
@pytest.mark.parametrize("response", ["not json", "null", "[]", "[{}]", "[[{}]]", "[[null]]"])
def test_invalid_dedup_response_posts_nothing(work_queue, github, response, resource):
    github.bad_response = response
    github.bad_resource = resource
    with pytest.raises(ValueError):
        module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert writes(github) == []


def test_failed_label_posts_no_comment(work_queue, github):
    github.failure = "label"
    with pytest.raises(subprocess.CalledProcessError):
        module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert [call[1:3] for call in writes(github)] == [["issue", "edit"]]


def test_failed_comment_is_not_backfilled(work_queue, github):
    github.failure = "comment"
    with pytest.raises(subprocess.CalledProcessError):
        module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    github.failure = None
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert [call[1:3] for call in writes(github)] == [["issue", "edit"], ["issue", "comment"]]


@pytest.mark.parametrize("apply_mode,comment", [(False, False), (False, True), (True, False)])
def test_dry_run_and_default_mode_never_comment(work_queue, github, apply_mode, comment):
    module.build_payload(work_queue, apply_mode=apply_mode, limit=1, comment=comment)
    assert all(call[1:3] != ["issue", "comment"] for call in github.calls)
    if not apply_mode:
        assert github.calls == []
    else:
        assert [call[1:3] for call in writes(github)] == [["issue", "edit"]]
        assert all(not call[-1].endswith("/comments") for call in github.calls)


def test_default_api_call_remains_label_only(work_queue, github):
    module.build_payload(work_queue, apply_mode=True, limit=1)
    assert github.calls[0][-1].endswith("/labels")
    assert [call[1:3] for call in writes(github)] == [["issue", "edit"]]


@pytest.mark.parametrize("marker", [
    "<!-- provider-autolabel:issue=3;label=ai:codex -->",
    "<!-- provider-autolabel:issue=2;label=ai:claude -->",
])
def test_marker_is_bound_to_issue_and_label(work_queue, github, marker):
    github.comments = [[{"body": marker}]]
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert len(writes(github)) == 2  # Unrelated marker permits a label and comment.


def test_marker_on_later_comment_page_suppresses_writes(work_queue, github):
    github.comments = [[{"body": "unrelated"}], [
        {"body": "<!-- provider-autolabel:issue=2;label=ai:codex -->"},
    ]]
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert writes(github) == []


def test_low_confidence_never_reads_or_writes(work_queue, github):
    work_queue["provider_queues"]["codex"]["top_issues"][0]["execution_ready"] = False
    payload = module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert payload["eligible_count"] == 0
    assert github.calls == []


@pytest.mark.parametrize("flags", [[], ["--comment"], ["--apply"], ["--apply", "--comment"]])
def test_cli_with_fixture_queue_and_stubbed_gh(work_queue, github, monkeypatch, tmp_path, flags):
    queue = tmp_path / "queue.json"
    output_json = tmp_path / "candidates.json"
    output_md = tmp_path / "candidates.md"
    queue.write_text(json.dumps(work_queue), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", [
        str(MODULE_PATH), "--work-queue", str(queue),
        "--output-json", str(output_json), "--output-md", str(output_md), *flags,
    ])
    module.main()
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["apply_mode"] == ("--apply" in flags)
    assert output_md.is_file()
    assert "fixture title withheld" not in output_md.read_text(encoding="utf-8")
    comments = [call for call in writes(github) if call[2] == "comment"]
    assert bool(comments) == ("--apply" in flags and "--comment" in flags)
    if "--apply" not in flags:
        assert github.calls == []


def test_provider_label_on_later_page_suppresses_writes(work_queue, github):
    github.label_pages = [[{"name": "bug"}], [{"name": "ai:codex"}]]
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert writes(github) == []


def test_duplicate_queue_records_do_not_repeat_writes(work_queue, github):
    issues = work_queue["provider_queues"]["codex"]["top_issues"]
    issues.append(dict(issues[0]))
    module.build_payload(work_queue, apply_mode=True, limit=len(issues), comment=True)
    assert len(writes(github)) == 2  # The duplicate adds neither label nor comment.


def test_limit_bounds_candidates_considered(work_queue, github):
    issues = work_queue["provider_queues"]["codex"]["top_issues"]
    issues.append({**issues[0], "number": 3})
    github.labels = ["agent:codex"]
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    assert len(github.calls) == 1  # Only the first candidate's labels are read.
    assert writes(github) == []


@pytest.mark.parametrize("limit", [0, 1])
def test_zero_limit_and_empty_queue_do_not_access_github(work_queue, github, limit):
    if limit:
        work_queue["provider_queues"]["codex"]["top_issues"] = []
    module.build_payload(work_queue, apply_mode=True, limit=limit, comment=True)
    assert github.calls == []


def test_explanation_rejects_arbitrary_routing_metadata(work_queue):
    item = {
        **work_queue["provider_queues"]["codex"]["top_issues"][0],
        "target_label": "ai:codex", "confidence": 0.95,
        "routing_reason": "untrusted routing text",
        "provider_priority": "untrusted priority text",
    }
    body = module.render_explanation(item)
    assert "Routing reason: unavailable" in body
    assert "Provider priority: unavailable" in body
    assert "untrusted" not in body


@pytest.mark.parametrize("provider,reason,priority,confidence", [
    # Independent policy sums: readiness + priority + strong match + preference.
    # Highest: 0.35 + 0.15 + 0.35 + 0.10 = 0.95; high substitutes 0.05 = 0.90.
    ("claude", "strategy/workflow/architecture language", "high", "0.90"),
    ("agy", "research/triage/audit language", "highest", "0.95"),
])
def test_explanations_for_other_eligible_providers(work_queue, github, provider, reason, priority, confidence):
    issue = work_queue["provider_queues"]["codex"]["top_issues"].pop()
    issue.update(routing_reason=reason, provider_priority=priority)
    work_queue["provider_queues"][provider]["top_issues"] = [issue]
    module.build_payload(work_queue, apply_mode=True, limit=1, comment=True)
    body = writes(github)[-1][-1]
    assert f"applied: `ai:{provider}`" in body
    assert f"Confidence: {confidence}" in body
    assert f"Routing reason: {reason}" in body
    assert f"Provider priority: {priority}" in body
