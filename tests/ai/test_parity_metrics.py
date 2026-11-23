"""Tests for behavioral parity metrics (#3061, epic #3058)."""
import importlib.util
import os

_SPEC = importlib.util.spec_from_file_location(
    "parity_metrics",
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "ai", "parity_metrics.py"),
)
pm = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pm)


def _dig(model, turns, out_tokens, askuser=0, agent=0):
    return {
        "turns_by_model": {model: turns},
        "out_tokens_by_model": {model: out_tokens},
        "tool_histogram": {"AskUserQuestion": askuser, "Agent": agent},
    }


def test_tokens_per_turn_aggregates_across_sessions():
    digs = [_dig("m", 10, 100), _dig("m", 10, 300)]
    m = pm.metrics_from_digests(digs, "m")
    assert m["sessions"] == 2
    assert m["total_turns"] == 20
    assert m["tokens_per_turn"] == 20.0  # (100+300)/20


def test_only_counts_sessions_using_the_model():
    digs = [_dig("m", 5, 50), _dig("other", 5, 9999)]
    m = pm.metrics_from_digests(digs, "m")
    assert m["sessions"] == 1
    assert m["tokens_per_turn"] == 10.0


def test_askuser_and_fanout_means():
    digs = [_dig("m", 1, 1, askuser=0, agent=2), _dig("m", 1, 1, askuser=2, agent=4)]
    m = pm.metrics_from_digests(digs, "m")
    assert m["askuser_per_session"] == 1.0
    assert m["agent_fanout_per_session"] == 3.0


def test_verbosity_regression_d1_fires():
    base = {"tokens_per_turn": 20, "askuser_per_session": 0}
    cur = {"model": "opus", "tokens_per_turn": 60, "askuser_per_session": 0}  # 3x
    regs = pm.compare_to_baseline(cur, base, verbosity_mult=2.0)
    assert any(r["delta"] == "D1" for r in regs)


def test_verbosity_within_bound_no_regression():
    base = {"tokens_per_turn": 20, "askuser_per_session": 0}
    cur = {"model": "opus", "tokens_per_turn": 30, "askuser_per_session": 0}  # 1.5x
    assert pm.compare_to_baseline(cur, base, verbosity_mult=2.0) == []


def test_clarification_regression_d2_fires():
    base = {"tokens_per_turn": 20, "askuser_per_session": 0.1}
    cur = {"model": "opus", "tokens_per_turn": 20, "askuser_per_session": 2.0}
    regs = pm.compare_to_baseline(cur, base, clarif_delta=1.0)
    assert any(r["delta"] == "D2" for r in regs)


def test_main_exit_code(tmp_path):
    import json
    (tmp_path / "s.json").write_text(json.dumps(_dig("claude-opus-4-8", 10, 100)))
    base = tmp_path / "baseline.json"
    base.write_text(json.dumps({"baseline": {"tokens_per_turn": 2, "askuser_per_session": 0}}))
    # current 10 tok/turn vs baseline 2 -> >2x -> regression -> exit 1
    assert pm.main([str(tmp_path), "--model", "claude-opus-4-8", "--baseline", str(base)]) == 1
