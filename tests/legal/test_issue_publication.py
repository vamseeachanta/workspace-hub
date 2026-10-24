"""Synthetic disclosure probes for issue 3768; no private map is needed."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TEXT = "synthetic unpublished prose <tag> | newline\ncontinuation"
PROBE = "synthetic unpublished prose"


def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_projection_is_recursive_nonmutating_and_idempotent():
    """Hand calculation: replace each prose field, retain both references in order."""
    mod = load("scripts/lib/issue_publication.py")
    original = {"items": [{"number": 1, "title": TEXT, "body_excerpt": TEXT},
                          {"number": 2, "hover": {"plan_summary": TEXT, "risks": TEXT,
                                                   "tests": TEXT, "body": TEXT}}],
                "count": 2, "url": "https://example.test/issues/1"}
    before = json.dumps(original)
    result = mod.public_issue_view(original)
    assert PROBE not in json.dumps(result)
    assert result["items"][0] == {"number": 1, "title": "[withheld; see issue]",
                                  "body_excerpt": "[withheld; see issue]"}
    assert [item["number"] for item in result["items"]] == [1, 2]
    assert result["count"] == 2
    assert result["url"] == original["url"]
    assert json.dumps(original) == before
    assert mod.public_issue_view(result) == result


def test_planning_outputs_withhold_titles(tmp_path):
    mod = load("scripts/ai/continuous-planning-pipeline.py")
    issue = {"number": 1, "title": TEXT, "body": TEXT, "state": "OPEN",
             "url": "https://example.test/issues/1", "labels": [], "comments": []}
    snapshot = mod.build_snapshot([issue], root=tmp_path)
    assert PROBE not in mod.dumps_json(snapshot)
    assert PROBE not in mod.render_markdown(snapshot)
    assert snapshot["items"][0]["number"] == 1
    assert issue["title"] == TEXT
    # Also protect rendering old, locally retained snapshots.
    snapshot["items"][0]["title"] = TEXT
    assert PROBE not in mod.dumps_json(snapshot)
    assert PROBE not in mod.render_markdown(snapshot)


def test_autolabel_legacy_input_preserves_scoring():
    """Hand calculation from existing scoring: .35 + .15 + .35 + .10 = .95."""
    mod = load("scripts/ai/provider-autolabel.py")
    issue = {"number": 1, "title": TEXT, "body_excerpt": TEXT, "labels": [],
             "execution_ready": True, "priority_rank": 1,
             "routing_reason": "implementation/test/fix language", "provider_priority": "highest"}
    queue = {"provider_queues": {p: {"top_issues": [issue] if p == "codex" else []}
                                 for p in mod.PROVIDERS}}
    result = mod.build_payload(queue, apply_mode=False, limit=1)
    assert PROBE not in json.dumps(result)
    assert PROBE not in mod.render_markdown(result)
    assert result["candidates"][0]["confidence"] == .95
    assert result["eligible_count"] == 1
    assert issue["title"] == TEXT
    result["candidates"][0]["title"] = TEXT
    assert PROBE not in mod.render_markdown(result)


def test_queue_rows_withhold_titles():
    mod = load("scripts/refresh-agent-work-queue.py")
    assert mod._format_issue_row(1, {"number": 2, "title": TEXT}) == (
        "| 1 | #2 | [withheld; see issue] |")


@pytest.mark.parametrize("as_json", [False, True])
def test_domain_outputs_withhold_titles(monkeypatch, capsys, as_json):
    """Hand calculation: one issue with zero domains gives one violation."""
    mod = load("scripts/kanban/domain_coverage.py")
    report = {"any_taxonomy": False, "repos": {"example/repository": mod.analyze(
        [{"number": 1, "title": TEXT, "labels": []}], None, None)}}
    md, total = mod.render(report)
    assert PROBE not in md
    assert "#1" in md
    assert total == 1
    monkeypatch.setattr(mod, "collect", lambda *a: report)
    monkeypatch.setattr(mod.private_overlay, "repo_aliases", dict)
    monkeypatch.setattr(sys, "argv", ["domain_coverage.py", "--strict"] +
                        (["--json"] if as_json else []))
    assert mod.main() == 1
    assert PROBE not in capsys.readouterr().out


def test_local_mirrors_remain_ignored():
    """Source: existing local-only output policy in .gitignore."""
    import subprocess

    samples = [
        ".claude/memory/kanban/boards/repo-example.yaml",
        "config/ai-tools/provider-work-queue.json",
        "config/ai-tools/provider-kanban.json",
        "docs/reports/provider-work-queue.md",
        "docs/reports/provider-kanban-dashboard.md",
        "docs/reports/provider-kanban-dashboard.html",
        "docs/reports/example-orca-kanban-data.json",
        "docs/dashboards/example-orca-kanban.html",
    ]
    for path in samples:
        assert subprocess.run(
            ["git", "check-ignore", "-q", "--no-index", path], cwd=ROOT,
            check=False,
        ).returncode == 0
        assert not subprocess.run(
            ["git", "ls-files", "--", path], cwd=ROOT, capture_output=True,
            text=True, check=True,
        ).stdout


@pytest.mark.parametrize("script", [
    "scripts/ai/continuous-planning-pipeline.py",
    "scripts/ai/provider-autolabel.py",
])
def test_cli_writes_projected_json_and_markdown(tmp_path, script):
    """Expected one issue, fixed prose and one retained reference, by inspection."""
    import subprocess

    source = tmp_path / "input.json"
    output = tmp_path / "output.json"
    markdown = tmp_path / "output.md"
    if "autolabel" in script:
        issue = {"number": 1, "title": TEXT, "body_excerpt": TEXT, "labels": [],
                 "execution_ready": True, "priority_rank": 1,
                 "routing_reason": "implementation/test/fix language",
                 "provider_priority": "highest"}
        data = {"provider_queues": {p: {"top_issues": [issue] if p == "codex" else []}
                                     for p in ("codex", "agy", "claude")}}
        option = "--work-queue"
    else:
        data = [{"number": 1, "title": TEXT, "body": TEXT, "labels": [],
                 "state": "OPEN", "url": "https://example.test/issues/1", "comments": []}]
        option = "--issues-json"
    source.write_text(json.dumps(data))
    result = subprocess.run(
        [sys.executable, str(ROOT / script), option, str(source),
         "--output-json", str(output), "--output-md", str(markdown)],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert PROBE not in output.read_text()
    assert PROBE not in markdown.read_text()
    result_data = json.loads(output.read_text())
    record = result_data["candidates" if "autolabel" in script else "items"][0]
    assert record["number"] == 1
    assert record["title"] == "[withheld; see issue]"
