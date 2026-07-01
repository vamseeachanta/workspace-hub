"""Tests for #801 auto-suggestion: generator + UserPromptSubmit hook.

Run: python3 -m pytest tests/data_sources/test_ecosystem_data_sources_801.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
# staging layout: <impl>/tests/data_sources/... and <impl>/scripts/... and <impl>/.claude/...
IMPL = os.path.dirname(os.path.dirname(HERE))
GEN = os.path.join(IMPL, "scripts", "data-sources", "gen_domain_pointers.py")
HOOK = os.path.join(IMPL, ".claude", "hooks", "ecosystem-data-nudge.sh")

sys.path.insert(0, os.path.dirname(GEN))
import gen_domain_pointers as gen  # noqa: E402


FAKE_INDEX = {
    "domains": {
        "riser": {"repo_home": "digitalmodel", "tables": [
            {"name": "config"}, {"name": "precedent", "route": "private_sidecar"}]},
        "metocean": {"repo_home": "worldenergydata", "tables": [{"name": "buoys"}]},
    }
}


def test_build_map_shape_and_precedent():
    m = gen.build_map(FAKE_INDEX)
    assert set(m["domains"]) == {"riser", "metocean"}
    assert m["domains"]["riser"]["repo_home"] == "digitalmodel"
    assert m["domains"]["riser"]["has_ace_share_precedent"] is True
    assert m["domains"]["metocean"]["has_ace_share_precedent"] is False
    # keywords come from the curated map
    assert "riser" in m["domains"]["riser"]["keywords"]


def test_build_map_emits_no_issue_numbers():
    """De-stale invariant: the map must never carry GitHub issue numbers."""
    m = gen.build_map(FAKE_INDEX)
    blob = json.dumps(m).lower()
    assert "#1" not in blob and "issue" not in json.dumps(m["domains"]).lower()


def _run_hook(prompt, session_id, map_path_dir):
    env = dict(os.environ)
    env["WORKSPACE_HUB"] = map_path_dir
    # Isolate hook session-state inside this test's unique tmp dir (pytest gives a
    # fresh empty dir per run), so once-per-session state never leaks across runs.
    env["ECOSYSTEM_NUDGE_STATE_DIR"] = map_path_dir
    payload = json.dumps({"prompt": prompt, "session_id": session_id})
    p = subprocess.run(["bash", HOOK], input=payload, env=env,
                       capture_output=True, text=True, timeout=15)
    return p


@pytest.fixture()
def ws(tmp_path):
    """A fake workspace-hub root with the generated map + hook in place."""
    hooks = tmp_path / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    shutil.copy(HOOK, hooks / "ecosystem-data-nudge.sh")
    m = gen.build_map(FAKE_INDEX)
    (hooks / "ecosystem-domain-map.json").write_text(json.dumps(m))
    return str(tmp_path)


def _sid(ws, suffix=""):
    # Unique per test invocation (tmp_path basename) so the hook's /tmp session
    # state never collides across runs. Production session_ids are globally unique.
    return "test-" + os.path.basename(str(ws).rstrip("/")) + suffix


def test_hook_fires_on_domain_prompt(ws):
    p = _run_hook("Help me set up a riser fatigue analysis", _sid(ws), ws)
    assert p.returncode == 0
    assert "ecosystem-data" in p.stdout
    assert "riser" in p.stdout
    assert "ACE_SHARE" in p.stdout  # precedent line present for riser


def test_hook_silent_on_non_domain_prompt(ws):
    for i, prompt in enumerate(["What time is it?", "Refactor this python function please"]):
        p = _run_hook(prompt, _sid(ws, f"-s{i}"), ws)
        assert p.returncode == 0
        assert p.stdout.strip() == ""


def test_hook_idempotent_per_session(ws):
    sid = _sid(ws)
    a = _run_hook("riser VIV question", sid, ws)
    assert "ecosystem-data" in a.stdout
    b = _run_hook("another riser question", sid, ws)
    assert b.stdout.strip() == ""  # suppressed second time same domain/session


def test_hook_word_boundary_no_false_fire(ws):
    # 'riser' substring inside another word should not trigger
    p = _run_hook("the highriser building downtown", _sid(ws), ws)
    assert p.stdout.strip() == ""


def test_hook_failopen_without_map(tmp_path):
    hooks = tmp_path / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    shutil.copy(HOOK, hooks / "ecosystem-data-nudge.sh")
    # no map file present
    p = _run_hook("riser fatigue", "test-" + tmp_path.name, str(tmp_path))
    assert p.returncode == 0
    assert p.stdout.strip() == ""
