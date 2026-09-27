"""Tests for scripts/legal/public_redaction.py (owner decision C20).

Every generator that writes a PUBLIC file of this repository from text it does
not control -- GitHub issue titles and bodies, host agent state -- applies the
identifier gate's single ``Redactor`` before writing, and fails closed when the
redactor cannot load. Names here are synthetic.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "legal" / "public_redaction.py"

SYNTH_WORD = "zorblaxcorp"
SYNTH_PHRASE = "Quux Marine Nine"


def load():
    spec = importlib.util.spec_from_file_location("public_redaction_under_test", MODULE)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def deny_list(tmp_path, monkeypatch):
    p = tmp_path / "deny.txt"
    p.write_text(f"# synthetic\n{SYNTH_WORD}\nre:(?i)quux\\s+marine\\s+nine\n", encoding="utf-8")
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(p))
    monkeypatch.delenv("LEGAL_CLIENT_MAP", raising=False)
    return p


def test_redactor_is_the_gate_redactor(deny_list):
    mod = load()
    red = mod.load_redactor()
    ci = mod._gate()
    assert isinstance(red, ci.Redactor)


def test_redacts_private_word_and_pattern(deny_list):
    mod = load()
    red = mod.load_redactor()
    out = red.redact(f"Issue for {SYNTH_WORD.title()} on the {SYNTH_PHRASE} hull")
    assert SYNTH_WORD not in out.lower()
    assert "quux" not in out.lower()
    assert "[redacted]" in out
    assert "hull" in out


def test_redacts_public_classes_without_private_list_when_allowed(monkeypatch, tmp_path):
    monkeypatch.delenv("WORKSPACE_HUB_DENY_LIST", raising=False)
    mod = load()
    ci = mod._gate()
    monkeypatch.setattr(ci, "DEFAULT_PRIVATE", str(tmp_path / "absent.txt"))
    red = mod.load_redactor(require_private=False)
    # Synthetic shapes assembled at run time so this file itself passes the gate.
    job, host = "B1" + "999", "zz-" + "ws" + "099"
    out = red.redact(f"job {job} on host {host}")
    assert job not in out and host not in out


def test_fails_closed_by_default_without_a_private_list(monkeypatch, tmp_path):
    """The public hashes do not cover multi-word private names: a generator
    must not publish with the public rules alone."""
    monkeypatch.delenv("WORKSPACE_HUB_DENY_LIST", raising=False)
    mod = load()
    ci = mod._gate()
    monkeypatch.setattr(ci, "DEFAULT_PRIVATE", str(tmp_path / "absent.txt"))
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_codename_map_patterns_are_applied(tmp_path, monkeypatch, deny_list):
    m = tmp_path / "map.yaml"
    m.write_text(
        "rules:\n"
        "  - {pattern: 'florpco', replacement: 'client-z', word_bound: true}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LEGAL_CLIENT_MAP", str(m))
    mod = load()
    red = mod.load_redactor()
    assert "florpco" not in red.redact("the Florpco riser").lower()


def test_fails_closed_when_named_codename_map_is_missing(tmp_path, monkeypatch, deny_list):
    monkeypatch.setenv("LEGAL_CLIENT_MAP", str(tmp_path / "nomap.yaml"))
    mod = load()
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_fails_closed_when_named_private_list_is_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    mod = load()
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_fails_closed_when_rules_file_is_missing(monkeypatch, tmp_path, deny_list):
    mod = load()
    ci = mod._gate()
    monkeypatch.setattr(ci, "RULES", str(tmp_path / "no-rules.yaml"))
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_fails_closed_when_rules_have_no_names_or_patterns(monkeypatch, tmp_path):
    """A rules file that loads but carries no hashed names and no private list
    redacts nothing a name-bearing title needs: refuse it."""
    rules = tmp_path / "rules.yaml"
    rules.write_text("salt: s\nstructural: []\nhashed_names: []\n", encoding="utf-8")
    monkeypatch.delenv("WORKSPACE_HUB_DENY_LIST", raising=False)
    mod = load()
    ci = mod._gate()
    monkeypatch.setattr(ci, "RULES", str(rules))
    monkeypatch.setattr(ci, "DEFAULT_PRIVATE", str(tmp_path / "absent.txt"))
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_redact_tree_values_and_keys_idempotent(deny_list):
    mod = load()
    red = mod.load_redactor()
    data = {
        "title": f"{SYNTH_WORD} riser",
        "n": 3,
        "flag": True,
        "none": None,
        "labels": ["ok", f"x-{SYNTH_WORD}"],
        f"{SYNTH_WORD}-key": {"nested": [f"{SYNTH_PHRASE}"]},
    }
    out = mod.redact_tree(data, red)
    blob = json.dumps(out)
    assert SYNTH_WORD not in blob.lower() and "quux" not in blob.lower()
    assert out["n"] == 3 and out["flag"] is True and out["none"] is None
    assert out["labels"][0] == "ok"
    assert mod.redact_tree(out, red) == out
    # the input is not mutated
    assert data["title"] == f"{SYNTH_WORD} riser"


def test_redact_json_file_stays_valid(tmp_path, deny_list):
    mod = load()
    red = mod.load_redactor()
    src = tmp_path / "a.json"
    drive = "D" + ":"  # assembled so this file passes the gate
    src.write_text(json.dumps({"path": drive + '\\ws\\x\\"q', "t": SYNTH_WORD}), encoding="utf-8")
    text = mod.redact_file_text(src.read_text(encoding="utf-8"), ".json", red)
    obj = json.loads(text)
    assert SYNTH_WORD not in text.lower()
    assert "t" in obj


def test_redact_jsonl_keeps_clean_lines_byte_identical(tmp_path, deny_list):
    mod = load()
    red = mod.load_redactor()
    clean = '{"a":1,  "b":"plain text"}'
    profile = "C" + ":\\\\" + "Users"  # assembled so this file passes the gate
    dirty = json.dumps({"text": f"see {SYNTH_WORD} and {profile}\\\\someone\\\\x \\\" q"})
    text = mod.redact_file_text(clean + "\n" + dirty + "\n", ".jsonl", red)
    lines = text.splitlines()
    assert lines[0] == clean
    assert SYNTH_WORD not in lines[1].lower()
    json.loads(lines[1])


def _cli(args, env):
    return subprocess.run(
        [sys.executable, str(MODULE), *args], capture_output=True, text=True, env=env
    )


def test_cli_copy_redacts_content(tmp_path, deny_list):
    src = tmp_path / "history.jsonl"
    src.write_text(json.dumps({"text": f"{SYNTH_WORD} job"}) + "\n", encoding="utf-8")
    dest = tmp_path / "out" / "history.jsonl"
    env = dict(os.environ)
    r = _cli(["copy", str(src), str(dest)], env)
    assert r.returncode == 0, r.stderr
    assert dest.exists()
    assert SYNTH_WORD not in dest.read_text(encoding="utf-8").lower()
    assert SYNTH_WORD not in (r.stdout + r.stderr).lower()


def test_cli_copy_skips_a_file_whose_name_carries_an_identifier(tmp_path, deny_list):
    src = tmp_path / f"note_{SYNTH_WORD}_lifecycle.md"
    src.write_text("clean body\n", encoding="utf-8")
    destdir = tmp_path / "out"
    destdir.mkdir()
    env = dict(os.environ)
    r = _cli(["copy", str(src), str(destdir / src.name)], env)
    assert r.returncode == 0, r.stderr
    assert list(destdir.iterdir()) == []
    assert SYNTH_WORD not in (r.stdout + r.stderr).lower()


def test_cli_copy_fails_closed_and_writes_nothing(tmp_path):
    src = tmp_path / "h.jsonl"
    src.write_text(f"{SYNTH_WORD}\n", encoding="utf-8")
    dest = tmp_path / "out.jsonl"
    env = dict(os.environ)
    env["WORKSPACE_HUB_DENY_LIST"] = str(tmp_path / "missing.txt")
    r = _cli(["copy", str(src), str(dest)], env)
    assert r.returncode == 3
    assert not dest.exists()


def test_cli_in_place_and_check(tmp_path, deny_list):
    f = tmp_path / "board.yaml"
    f.write_text(f"title: {SYNTH_WORD} board\n", encoding="utf-8")
    env = dict(os.environ)
    assert _cli(["check", str(f)], env).returncode == 1
    assert _cli(["inplace", str(f)], env).returncode == 0
    assert SYNTH_WORD not in f.read_text(encoding="utf-8").lower()
    assert _cli(["check", str(f)], env).returncode == 0


def test_cli_self_check(tmp_path, deny_list):
    env = dict(os.environ)
    assert _cli(["self-check"], env).returncode == 0
    env["WORKSPACE_HUB_DENY_LIST"] = str(tmp_path / "missing.txt")
    assert _cli(["self-check"], env).returncode == 3
