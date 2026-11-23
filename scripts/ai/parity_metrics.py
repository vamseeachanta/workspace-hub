#!/usr/bin/env python3
"""parity_metrics.py — behavioral parity metrics from session digests.

Turns the one-off Fable corpus analysis (#3056) into a repeatable measurement so
"same pace / zero waste" is tracked, not asserted (#3061, harden-ecosystem epic
#3058). Operates on per-session digests from ``transcript-digest.py``.

Metrics (the deltas named in analysis/2026-06-13-fable5-opus-parity-learning.md):
  tokens_per_turn          — verbosity / output economy (delta D1, the top risk)
  askuser_per_session      — clarification-break rate (delta D2; AskUserQuestion proxy)
  agent_fanout_per_session — fan-out orchestration (delta D6)
  avg_turns                — turns-to-done

Stance fidelity (D3) needs text-level analysis and is intentionally out of v1.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics
import sys


def _mean(xs):
    xs = list(xs)
    return round(statistics.mean(xs), 3) if xs else 0.0


def metrics_from_digests(digests, model):
    """Aggregate behavioral metrics for ``model`` across sessions that used it."""
    sess = [d for d in digests if (d.get("turns_by_model") or {}).get(model, 0) > 0]
    total_turns = sum((d["turns_by_model"][model]) for d in sess)
    total_out = sum((d.get("out_tokens_by_model") or {}).get(model, 0) for d in sess)
    return {
        "model": model,
        "sessions": len(sess),
        "total_turns": total_turns,
        "tokens_per_turn": round(total_out / total_turns, 2) if total_turns else 0.0,
        "askuser_per_session": _mean((d.get("tool_histogram") or {}).get("AskUserQuestion", 0) for d in sess),
        "agent_fanout_per_session": _mean((d.get("tool_histogram") or {}).get("Agent", 0) for d in sess),
        "avg_turns": _mean(d["turns_by_model"][model] for d in sess),
    }


def compare_to_baseline(current, baseline, *, verbosity_mult=2.0, clarif_delta=1.0):
    """Return regressions where ``current`` (e.g. Opus) drifts worse than ``baseline`` (Fable)."""
    regressions = []
    b_tpt = baseline.get("tokens_per_turn", 0)
    c_tpt = current.get("tokens_per_turn", 0)
    if b_tpt > 0 and c_tpt > b_tpt * verbosity_mult:
        regressions.append({
            "delta": "D1", "metric": "tokens_per_turn",
            "detail": f"{current['model']} {c_tpt} tok/turn > {verbosity_mult}x Fable baseline {b_tpt}",
            "baseline": b_tpt, "current": c_tpt,
        })
    b_ask = baseline.get("askuser_per_session", 0)
    c_ask = current.get("askuser_per_session", 0)
    if c_ask > b_ask + clarif_delta:
        regressions.append({
            "delta": "D2", "metric": "askuser_per_session",
            "detail": f"{current['model']} {c_ask} clarification-breaks/session > Fable {b_ask} + {clarif_delta}",
            "baseline": b_ask, "current": c_ask,
        })
    return regressions


def load_digests(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            with open(p) as fh:
                out.append(json.load(fh))
        except (OSError, ValueError):
            pass
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Behavioral parity metrics from session digests")
    ap.add_argument("digest_dir")
    ap.add_argument("--model", default="claude-opus-4-8")  # model-id-ok (CLI default)
    ap.add_argument("--baseline", help="parity-baseline.json to compare against")
    ap.add_argument("--verbosity-mult", type=float, default=2.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    cur = metrics_from_digests(load_digests(a.digest_dir), a.model)
    regressions = []
    if a.baseline and os.path.exists(a.baseline):
        base = json.load(open(a.baseline))
        b = base.get("baseline") or base  # support {"baseline": {...}} or flat
        regressions = compare_to_baseline(cur, b, verbosity_mult=a.verbosity_mult)
    if a.json:
        print(json.dumps({"current": cur, "regressions": regressions}, indent=2))
    else:
        print(f"parity[{cur['model']}]: {cur['sessions']} sess, {cur['tokens_per_turn']} tok/turn, "
              f"{cur['askuser_per_session']} askuser/sess, {cur['agent_fanout_per_session']} fanout/sess")
        for r in regressions:
            print(f"  REGRESSION {r['delta']} {r['metric']}: {r['detail']}")
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
