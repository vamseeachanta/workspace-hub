"""C20 follow-up: provider-autolabel.py redacts before writing public files.

provider-autolabel.py writes config/ai-tools/provider-autolabel-candidates.json
and docs/reports/provider-autolabel-candidates.md -- files of this PUBLIC
repository -- from GitHub issue titles carried in the work queue. Like the other
board builders (tests/ai/test_generated_board_redaction.py) it applies the
identifier gate's Redactor and fails closed: when the Redactor cannot load it
writes nothing and applies no label. Names are synthetic.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "ai" / "provider-autolabel.py"
SYNTH = "zorblaxcorp"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
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


def _queue(tmp_path: Path) -> Path:
    issue = {
        "number": 4242,
        "title": f"fix: riser test for {SYNTH.title()}",
        "labels": [],
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "implementation/test/fix language",
        "provider_priority": "highest",
    }
    queue = {"provider_queues": {
        "claude": {"top_issues": []},
        "codex": {"top_issues": [issue]},
        "agy": {"top_issues": []},
    }}
    p = tmp_path / "queue.json"
    p.write_text(json.dumps(queue), encoding="utf-8")
    return p


def _argv(tmp_path: Path, *extra: str) -> list[str]:
    return [
        "provider-autolabel.py", "--work-queue", str(_queue(tmp_path)),
        "--output-json", str(tmp_path / "a.json"), "--output-md", str(tmp_path / "a.md"),
        *extra,
    ]


def test_autolabel_outputs_are_redacted(tmp_path, monkeypatch):
    mod = _load("pal_c20")
    monkeypatch.setattr(sys, "argv", _argv(tmp_path))
    mod.main()
    text = (tmp_path / "a.json").read_text(encoding="utf-8") + (tmp_path / "a.md").read_text(encoding="utf-8")
    assert "4242" in text
    assert "agent:codex" in text
    assert SYNTH not in text.lower()
    json.loads((tmp_path / "a.json").read_text(encoding="utf-8"))


def test_autolabel_fails_closed_without_writing(tmp_path, monkeypatch):
    mod = _load("pal_c20b")
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    monkeypatch.setattr(sys, "argv", _argv(tmp_path))
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code not in (0, None)
    assert not (tmp_path / "a.json").exists() and not (tmp_path / "a.md").exists()


def test_autolabel_applies_no_label_when_redactor_unavailable(tmp_path, monkeypatch):
    """--apply mutates GitHub; an unavailable redactor must stop it before any edit."""
    mod = _load("pal_c20c")
    calls: list[tuple[int, str]] = []
    monkeypatch.setattr(mod, "gh_issue_edit_add_label", lambda n, label: calls.append((n, label)))
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    monkeypatch.setattr(sys, "argv", _argv(tmp_path, "--apply"))
    with pytest.raises(SystemExit):
        mod.main()
    assert calls == []


def test_autolabel_apply_labels_the_original_issue_number(tmp_path, monkeypatch):
    """Redaction touches only what is written; the label goes to the real issue."""
    mod = _load("pal_c20d")
    calls: list[tuple[int, str]] = []
    monkeypatch.setattr(mod, "gh_issue_edit_add_label", lambda n, label: calls.append((n, label)))
    monkeypatch.setattr(sys, "argv", _argv(tmp_path, "--apply"))
    mod.main()
    assert calls == [(4242, "agent:codex")]
    assert SYNTH not in (tmp_path / "a.json").read_text(encoding="utf-8").lower()


def test_autolabel_redaction_failure_after_load_applies_no_label(tmp_path, monkeypatch):
    """A redactor that loads but then fails must stop --apply before any label edit."""
    mod = _load("pal_c20e")
    real = mod._public_redaction()

    class Broken:
        RedactorUnavailable = real.RedactorUnavailable
        load_redactor = staticmethod(real.load_redactor)

        @staticmethod
        def redact_tree(obj, redactor):
            raise RuntimeError("redaction failed")

    calls: list[tuple[int, str]] = []
    monkeypatch.setattr(mod, "_public_redaction", lambda: Broken)
    monkeypatch.setattr(mod, "gh_issue_edit_add_label", lambda n, label: calls.append((n, label)))
    monkeypatch.setattr(sys, "argv", _argv(tmp_path, "--apply"))
    with pytest.raises(RuntimeError):
        mod.main()
    assert calls == []
    assert not (tmp_path / "a.json").exists() and not (tmp_path / "a.md").exists()


@pytest.mark.parametrize("extra", [(), ("--apply",)])
def test_autolabel_console_output_carries_no_identifier(tmp_path, monkeypatch, capsys, extra):
    mod = _load("pal_c20f" + "".join(extra).replace("-", "_"))
    monkeypatch.setattr(mod, "gh_issue_edit_add_label", lambda n, label: None)
    monkeypatch.setattr(sys, "argv", _argv(tmp_path, *extra))
    mod.main()
    out = capsys.readouterr()
    assert SYNTH not in (out.out + out.err).lower()
    if extra:
        assert "Applied labels:" in out.out and "#4242 -> agent:codex" in out.out