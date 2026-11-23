"""TDD suite for #2845 — non-JSON poison handling in the cross-provider dream distiller.

The distiller (`scripts/memory/distill-provider-sessions.py`) previously returned `[]`
for BOTH "Claude returned valid {"learnings":[]}" AND "Claude returned non-JSON garble".
The caller advanced the watermark over garbled batches => silent data loss.

This suite pins the fixed contract:
  - `claude_distill` returns the `POISON` sentinel (not []) for non-JSON, non-transient output.
  - garbled batches HOLD the watermark and are retried (bounded by MAX_POISON_RETRIES),
    keyed on a content digest of the batch's session paths (batch identity is not stable).
  - after MAX_POISON_RETRIES (or AGE_ESCAPE_DAYS of continuous hold) the batch is
    dead-lettered to an auditable JSONL file and the watermark advances (no permanent wedge).
  - `main()` exits non-zero when any sessions were dead-lettered.
  - dry-run writes neither the dead-letter file, the watermark, nor poison state.

The script is kebab-named (not importable as a package), so we load it via importlib with
the auto-memory dir redirected to a tmp path BEFORE import (module-level paths derive from it).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "distill-provider-sessions.py"


def _load_module(mem_dir: Path):
    """Import the kebab-named script with MEM_DIR redirected to `mem_dir`."""
    import os
    os.environ["CLAUDE_AUTO_MEMORY_DIR"] = str(mem_dir)
    spec = importlib.util.spec_from_file_location("distill_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so any @dataclass/forward refs resolve (defensive).
    sys.modules["distill_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mod(tmp_path):
    mem = tmp_path / "memory"
    mem.mkdir()
    m = _load_module(mem)
    # Sanity: the new public surface must exist.
    assert hasattr(m, "POISON"), "POISON sentinel missing"
    return m


def _args(**over):
    base = dict(provider="codex", backfill=False, dry_run=False, limit=0,
                batch_size=8, since_days=0, max_learnings_per_provider=0)
    base.update(over)
    return argparse.Namespace(**base)


def _fake_sessions(mod, tmp_path, n=2, base_mtime=1_000_000.0):
    """Create n fake session files and point PROVIDERS[codex] at them with a
    filter that always yields enough text to clear MIN_SESSION_CHARS."""
    files = []
    d = tmp_path / "sessions"
    d.mkdir(exist_ok=True)
    for i in range(n):
        f = d / f"rollout-{i}.jsonl"
        f.write_text("x")
        import os
        os.utime(f, (base_mtime + i, base_mtime + i))
        files.append(f)
    mod.PROVIDERS = dict(mod.PROVIDERS)
    mod.PROVIDERS["codex"] = (lambda: sorted(files), lambda p: "DURABLE LEARNING TEXT " * 30)
    return files


# --------------------------------------------------------------------------- #
# claude_distill return contract
# --------------------------------------------------------------------------- #

def test_poison_sentinel_identity_invariant(mod):
    """POISON must be a unique, NON-falsy singleton compared by identity — a falsy
    sentinel could be routed into the empty-success path by a future refactor."""
    assert mod.POISON is not None
    assert mod.POISON != []
    assert bool(mod.POISON) is True


def test_claude_distill_returns_poison_on_non_json(mod, monkeypatch):
    """Non-JSON, non-transient model output -> POISON (was []), distinct from valid-empty."""
    class P:
        returncode = 0
        stdout = '{"type":"result","result":"sorry, here is some prose not json"}'
        stderr = ""
    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: P())
    assert mod.claude_distill("codex", "body") is mod.POISON


def test_claude_distill_valid_empty_is_list_not_poison(mod, monkeypatch):
    """Valid {"learnings":[]} stays [] — genuinely nothing durable, safe to advance."""
    class P:
        returncode = 0
        stdout = '{"type":"result","result":"{\\"learnings\\": []}"}'
        stderr = ""
    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: P())
    out = mod.claude_distill("codex", "body")
    assert out == [] and out is not mod.POISON


# --------------------------------------------------------------------------- #
# run_provider poison handling
# --------------------------------------------------------------------------- #

def test_valid_empty_advances_watermark(mod, tmp_path, monkeypatch):
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: [])
    wm = {}
    st = mod.run_provider("codex", _args(), wm)
    assert wm.get("codex", 0) > 0          # advanced
    assert st.get("deadlettered_sessions", 0) == 0
    assert not (mod.MEM_DIR / ".provider-bridge-deadletter.jsonl").exists()


def test_poison_holds_watermark_first_attempt(mod, tmp_path, monkeypatch):
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    wm = {}
    st = mod.run_provider("codex", _args(), wm)
    assert wm.get("codex", 0) == 0         # held, not advanced
    assert st.get("deadlettered_sessions", 0) == 0
    pf = mod.MEM_DIR / ".provider-bridge-poison.json"
    assert pf.exists()                      # attempt recorded
    import json
    assert json.loads(pf.read_text())["codex"]["attempts"] == 1


def test_poison_retried_then_deadlettered(mod, tmp_path, monkeypatch):
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    assert mod.MAX_POISON_RETRIES >= 1
    last = None
    for _ in range(mod.MAX_POISON_RETRIES):
        wm = mod.load_watermark()
        last = mod.run_provider("codex", _args(), wm)
    # On the MAX-th run the batch is dead-lettered and the watermark advances.
    assert last.get("deadlettered_sessions", 0) == 2
    dl = mod.MEM_DIR / ".provider-bridge-deadletter.jsonl"
    assert dl.exists() and dl.read_text().strip()
    assert mod.load_watermark().get("codex", 0) > 0


def test_transient_none_holds_watermark(mod, tmp_path, monkeypatch):
    """Regression guard: transient None still HOLDS the watermark (existing behavior)."""
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: None)
    wm = {}
    mod.run_provider("codex", _args(), wm)
    assert wm.get("codex", 0) == 0
    assert not (mod.MEM_DIR / ".provider-bridge-deadletter.jsonl").exists()


def test_successful_batch_writes_and_advances(mod, tmp_path, monkeypatch):
    _fake_sessions(mod, tmp_path, n=2)
    learning = {"title": "t", "body": "b", "tags": ["x"]}
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: [learning])
    wm = {}
    st = mod.run_provider("codex", _args(), wm)
    assert wm.get("codex", 0) > 0
    assert st["learnings"] == 1
    assert list(mod.MEM_DIR.glob("crossprovider_codex_*.md"))


def test_poison_counter_resets_after_success(mod, tmp_path, monkeypatch):
    """A recovered provider drops its poison count so a later single garble
    doesn't prematurely dead-letter."""
    _fake_sessions(mod, tmp_path, n=2)
    seq = [mod.POISON, [{"title": "t", "body": "b", "tags": []}]]
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: seq.pop(0))
    for _ in range(2):
        wm = mod.load_watermark()
        mod.run_provider("codex", _args(), wm)
    pf = mod.MEM_DIR / ".provider-bridge-poison.json"
    state = {} if not pf.exists() else __import__("json").loads(pf.read_text())
    assert state.get("codex") in (None, {})   # cleared on recovery


def test_final_batch_only_poison(mod, tmp_path, monkeypatch):
    """A sole sub-batch_size batch never hits the mid-loop flush — the trailing
    flush path must apply identical poison handling."""
    _fake_sessions(mod, tmp_path, n=2)        # 2 < batch_size 8
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    wm = {}
    st = mod.run_provider("codex", _args(batch_size=8), wm)
    assert wm.get("codex", 0) == 0            # held via trailing-flush poison path
    assert (mod.MEM_DIR / ".provider-bridge-poison.json").exists()
    assert st.get("deadlettered_sessions", 0) == 0


def test_dry_run_no_deadletter_no_advance(mod, tmp_path, monkeypatch):
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    for _ in range(mod.MAX_POISON_RETRIES + 1):
        wm = mod.load_watermark()
        mod.run_provider("codex", _args(dry_run=True), wm)
    assert not (mod.MEM_DIR / ".provider-bridge-deadletter.jsonl").exists()
    assert not (mod.MEM_DIR / ".provider-bridge-poison.json").exists()
    assert mod.load_watermark().get("codex", 0) == 0


def test_limit_run_holds_without_counting(mod, tmp_path, monkeypatch):
    """--limit reshapes the window, so poison under --limit must HOLD without
    incrementing the counter (batches aren't comparable across runs)."""
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    wm = {}
    mod.run_provider("codex", _args(limit=2), wm)
    pf = mod.MEM_DIR / ".provider-bridge-poison.json"
    # No poison-state counting under --limit (hold-only).
    assert not pf.exists() or __import__("json").loads(pf.read_text()).get("codex") in (None, {})
    assert wm.get("codex", 0) == 0


def test_deadletter_record_shape(mod, tmp_path, monkeypatch):
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    for _ in range(mod.MAX_POISON_RETRIES):
        wm = mod.load_watermark()
        mod.run_provider("codex", _args(), wm)
    import json
    rec = json.loads((mod.MEM_DIR / ".provider-bridge-deadletter.jsonl").read_text().splitlines()[0])
    for key in ("provider", "sessions", "reason", "attempts", "ts"):
        assert key in rec, f"dead-letter record missing {key}"
    assert rec["provider"] == "codex"


def test_main_exit_nonzero_on_deadletter(mod, tmp_path, monkeypatch):
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    monkeypatch.setattr(sys, "argv", ["distill", "--provider", "codex"])
    # Drive MAX-1 holds first, then the MAX-th run via main() should dead-letter -> rc 3.
    for _ in range(mod.MAX_POISON_RETRIES - 1):
        wm = mod.load_watermark()
        mod.run_provider("codex", _args(), wm)
    assert mod.main() == 3


def test_watermark_schema_backward_compatible(mod, tmp_path, monkeypatch):
    """A legacy watermark with no poison machinery loads and is read as a float mtime."""
    import json
    (mod.MEM_DIR / ".provider-bridge-watermark.json").write_text(json.dumps({"codex": 123.0}))
    _fake_sessions(mod, tmp_path, n=1, base_mtime=50.0)   # older than watermark -> nothing pending
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: [])
    wm = mod.load_watermark()
    st = mod.run_provider("codex", _args(), wm)
    assert float(wm.get("codex")) == 123.0
    assert st["pending"] == 0


# --------------------------------------------------------------------------- #
# r2 review fixes — mid-loop path (F3), dry-run preseeded (F1), re-deadletter
# loop (F2), age-escape (F3 gap)
# --------------------------------------------------------------------------- #

def test_mid_loop_poison_holds(mod, tmp_path, monkeypatch):
    """F3: with batch_size=1 the MID-LOOP flush fires (not just trailing). A poison
    mid-loop batch must hold + abort, exercising the previously-untested path."""
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    wm = {}
    st = mod.run_provider("codex", _args(batch_size=1), wm)
    assert wm.get("codex", 0) == 0
    assert st["batches"] >= 1
    import json
    assert json.loads((mod.MEM_DIR / ".provider-bridge-poison.json").read_text())["codex"]["attempts"] == 1


def test_mid_loop_recovery_advances(mod, tmp_path, monkeypatch):
    """F3: batch_size=1, two good batches via the mid-loop path -> both written, advanced."""
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill",
                        lambda p, t: [{"title": "t", "body": "b", "tags": []}])
    wm = {}
    st = mod.run_provider("codex", _args(batch_size=1), wm)
    assert st["learnings"] == 2
    assert wm.get("codex", 0) > 0


def test_mid_loop_dead_letter_then_continue(mod, tmp_path, monkeypatch):
    """F3: mid-loop dead-letter of batch-1 must NOT lose batch-2 (the continue path)."""
    files = _fake_sessions(mod, tmp_path, n=2)
    import json, time as _t
    sig0 = mod._batch_sig([files[0]])
    # Pre-seed batch-0 at the cap edge so its mid-loop poison dead-letters this run.
    (mod.MEM_DIR / ".provider-bridge-poison.json").write_text(
        json.dumps({"codex": {"sig": sig0, "attempts": mod.MAX_POISON_RETRIES - 1, "first_ts": _t.time()}}))
    monkeypatch.setattr(mod, "claude_distill",
                        lambda p, t: mod.POISON if "rollout-0" in t
                        else [{"title": "t", "body": "b", "tags": []}])
    wm = {}
    st = mod.run_provider("codex", _args(batch_size=1), wm)
    assert st["deadlettered_sessions"] == 1          # batch-0 dead-lettered
    assert st["learnings"] == 1                       # batch-1 STILL processed (continue worked)
    assert "rollout-0.jsonl" in (mod.MEM_DIR / ".provider-bridge-deadletter.jsonl").read_text()


def test_dry_run_preseeded_no_phantom_rc3(mod, tmp_path, monkeypatch):
    """F1: a --dry-run over poison state pre-seeded near the cap must NOT phantom-
    increment deadlettered_sessions (which would make main() return 3) nor leak a .lock."""
    files = _fake_sessions(mod, tmp_path, n=2)
    import json, time as _t
    sig = mod._batch_sig(files)
    (mod.MEM_DIR / ".provider-bridge-poison.json").write_text(
        json.dumps({"codex": {"sig": sig, "attempts": mod.MAX_POISON_RETRIES - 1, "first_ts": _t.time()}}))
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    wm = {}
    st = mod.run_provider("codex", _args(dry_run=True), wm)
    assert st["deadlettered_sessions"] == 0
    assert not (mod.MEM_DIR / ".provider-bridge-deadletter.jsonl").exists()
    assert not (mod.MEM_DIR / ".provider-bridge-poison.lock").exists()


def test_deadlettered_session_skipped_on_reintake(mod, tmp_path, monkeypatch):
    """F2: once dead-lettered, a session is excluded from intake forever — no
    re-distill + duplicate dead-letter record on subsequent runs."""
    _fake_sessions(mod, tmp_path, n=2)
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    for _ in range(mod.MAX_POISON_RETRIES):
        wm = mod.load_watermark()
        mod.run_provider("codex", _args(), wm)
    dl = mod.MEM_DIR / ".provider-bridge-deadletter.jsonl"
    lines_after_first = len(dl.read_text().splitlines())
    # Several more runs must NOT re-dead-letter the same sessions.
    for _ in range(3):
        wm = mod.load_watermark()
        st = mod.run_provider("codex", _args(), wm)
        assert st["pending"] == 0          # dead-lettered sessions excluded from intake
    assert len(dl.read_text().splitlines()) == lines_after_first   # no duplicates


def test_age_escape_deadletters_stale_hold(mod, tmp_path, monkeypatch):
    """F3 gap: a batch whose sig changes every run (absorbs new sessions) still
    dead-letters once first_ts exceeds AGE_ESCAPE_DAYS, even though attempts<MAX."""
    _fake_sessions(mod, tmp_path, n=2)
    import json, time as _t
    old = _t.time() - (mod.AGE_ESCAPE_DAYS + 1) * 86400
    (mod.MEM_DIR / ".provider-bridge-poison.json").write_text(
        json.dumps({"codex": {"sig": "stale-different-sig", "attempts": 1, "first_ts": old}}))
    monkeypatch.setattr(mod, "claude_distill", lambda *a, **k: mod.POISON)
    wm = {}
    st = mod.run_provider("codex", _args(), wm)
    assert st["deadlettered_sessions"] == 2
    rec = json.loads((mod.MEM_DIR / ".provider-bridge-deadletter.jsonl").read_text().splitlines()[0])
    assert rec["reason"] == "age_escape"
