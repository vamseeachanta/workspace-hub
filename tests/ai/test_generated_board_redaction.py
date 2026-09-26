"""C20: provider and Orca kanban generators redact before writing public files.

provider-work-queue.py, provider-kanban.py and build-orca-kanban.py write
files of this PUBLIC repository from GitHub issue text. Each applies the
identifier gate's Redactor before writing and fails closed -- writing
nothing -- when it cannot load. Names are synthetic.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AI = REPO_ROOT / "scripts" / "ai"
SYNTH = "zorblaxcorp"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, AI / file)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def deny_list(tmp_path_factory, monkeypatch):
    p = tmp_path_factory.mktemp("deny") / "deny.txt"
    p.write_text(f"{SYNTH}\n", encoding="utf-8")
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(p))
    monkeypatch.delenv("LEGAL_CLIENT_MAP", raising=False)
    return p


def _issues(tmp_path: Path) -> Path:
    issues = [
        {
            "number": 4242,
            "title": f"Fix riser test for {SYNTH.title()}",
            "labels": [{"name": "priority:high"}],
            "assignees": [],
            "updatedAt": "2026-09-26T00:00:00Z",
            "body": f"Body names {SYNTH} again.",
            "url": "https://example.test/issues/4242",
            "state": "OPEN",
        }
    ]
    p = tmp_path / "issues.json"
    p.write_text(json.dumps(issues), encoding="utf-8")
    return p


def _outputs_text(*paths: Path) -> str:
    return "".join(p.read_text(encoding="utf-8") for p in paths if p.exists())


# -- provider-work-queue.py ---------------------------------------------------

def test_work_queue_outputs_are_redacted(tmp_path, monkeypatch):
    mod = _load("pwq_c20", "provider-work-queue.py")
    out_json, out_md = tmp_path / "q.json", tmp_path / "q.md"
    monkeypatch.setattr(sys, "argv", [
        "provider-work-queue.py", "--issues-json", str(_issues(tmp_path)),
        "--output-json", str(out_json), "--output-md", str(out_md),
    ])
    mod.main()
    text = _outputs_text(out_json, out_md)
    assert "4242" in text
    assert SYNTH not in text.lower()
    json.loads(out_json.read_text(encoding="utf-8"))


def test_work_queue_fails_closed(tmp_path, monkeypatch):
    mod = _load("pwq_c20b", "provider-work-queue.py")
    out_json, out_md = tmp_path / "q.json", tmp_path / "q.md"
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    monkeypatch.setattr(sys, "argv", [
        "provider-work-queue.py", "--issues-json", str(_issues(tmp_path)),
        "--output-json", str(out_json), "--output-md", str(out_md),
    ])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code not in (0, None)
    assert not out_json.exists() and not out_md.exists()


# -- provider-kanban.py -------------------------------------------------------

def _kanban_args(tmp_path: Path, queue: Path) -> list[str]:
    scorecard = REPO_ROOT / "config" / "ai-tools" / "provider-routing-scorecard.json"
    return [
        "--work-queue-json", str(queue),
        "--scorecard-json", str(scorecard),
        "--utilization-json", str(tmp_path / "none.json"),
        "--issues-json", str(_issues(tmp_path)),
        "--output-json", str(tmp_path / "k.json"),
        "--output-md", str(tmp_path / "k.md"),
        "--output-html", str(tmp_path / "k.html"),
    ]


def _fake_kanban(**_):
    card = {
        "number": 4242,
        "title": f"Fix riser test for {SYNTH}",
        "url": "https://example.test/issues/4242",
        "lane": "planning_feedstock",
        "provider_route": "codex",
        "routing_reason": "fix",
        "machine_route": None,
        "machine_ready": False,
        "plan": f"docs/plans/2026-09-26-issue-4242-{SYNTH}-riser.md",
        "hover": {"summary": f"plan for {SYNTH}", "risks": "", "tests": "", "labels": [],
                  "provider_route": "codex", "machine_route": "(none ready)"},
        "approve": {"enabled": False, "reason": "no plan"},
    }
    return {"generated_at": "2026-09-26T00:00:00Z", "lanes": {"planning_feedstock": [card]},
            "cards": [card], "served_localhost": False}


def test_provider_kanban_outputs_are_redacted(tmp_path, monkeypatch):
    mod = _load("pk_c20", "provider-kanban.py")
    queue = tmp_path / "queue.json"
    queue.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(mod, "build_kanban", _fake_kanban)
    monkeypatch.setattr(mod, "render_markdown", lambda k: json.dumps(k))
    monkeypatch.setattr(mod, "render_html", lambda k: "<p>" + json.dumps(k) + "</p>")
    assert mod.main(_kanban_args(tmp_path, queue)) == 0
    text = _outputs_text(tmp_path / "k.json", tmp_path / "k.md", tmp_path / "k.html")
    assert "4242" in text
    assert SYNTH not in text.lower()


def test_provider_kanban_redacts_rendered_text_too(tmp_path, monkeypatch):
    """A renderer that adds text of its own (a plan file excerpt) is covered."""
    mod = _load("pk_c20c", "provider-kanban.py")
    queue = tmp_path / "queue.json"
    queue.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(mod, "build_kanban", _fake_kanban)
    monkeypatch.setattr(mod, "render_markdown", lambda k: f"extra {SYNTH}\n")
    monkeypatch.setattr(mod, "render_html", lambda k: f"<p>{SYNTH}</p>")
    assert mod.main(_kanban_args(tmp_path, queue)) == 0
    assert SYNTH not in _outputs_text(tmp_path / "k.md", tmp_path / "k.html").lower()


def test_provider_kanban_fails_closed(tmp_path, monkeypatch):
    mod = _load("pk_c20b", "provider-kanban.py")
    queue = tmp_path / "queue.json"
    queue.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(mod, "build_kanban", _fake_kanban)
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    rc = mod.main(_kanban_args(tmp_path, queue))
    assert rc != 0
    assert not any((tmp_path / n).exists() for n in ("k.json", "k.md", "k.html"))


# -- build-orca-kanban.py -----------------------------------------------------

def _orca_issue():
    return {
        "number": 4243, "title": f"OrcaFlex riser model for {SYNTH}", "state": "OPEN",
        "labels": [], "updatedAt": "2026-09-26T00:00:00Z", "createdAt": "2026-09-01T00:00:00Z",
        "closedAt": None, "url": "https://example.test/issues/4243", "assignees": [],
        "_domain": "OF", "_labels": [], "_status": None, "_priority": None,
    }


def test_orca_kanban_outputs_are_redacted(tmp_path, monkeypatch):
    mod = _load("orca_c20", "build-orca-kanban.py")
    monkeypatch.setattr(mod, "collect_issues", lambda: [_orca_issue()])
    monkeypatch.setattr(mod, "DATA_PATH", tmp_path / "o.json")
    monkeypatch.setattr(mod, "HTML_PATH", tmp_path / "o.html")
    assert mod.main() == 0
    text = _outputs_text(tmp_path / "o.json", tmp_path / "o.html")
    assert "4243" in text
    assert SYNTH not in text.lower()


def test_orca_kanban_fails_closed(tmp_path, monkeypatch):
    mod = _load("orca_c20b", "build-orca-kanban.py")
    monkeypatch.setattr(mod, "collect_issues", lambda: [_orca_issue()])
    monkeypatch.setattr(mod, "DATA_PATH", tmp_path / "o.json")
    monkeypatch.setattr(mod, "HTML_PATH", tmp_path / "o.html")
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    assert mod.main() != 0
    assert not (tmp_path / "o.json").exists() and not (tmp_path / "o.html").exists()
