#!/usr/bin/env bash
# provider-cost-tracker.sh — Estimate provider token spend per session and WRK item.
#
# Reads session-signals/*.jsonl for session metadata and estimates token cost using
# pricing from config/agents/model-registry.yaml. Emits cost records to
# .claude/state/session-signals/cost-tracking.jsonl. Flags sessions with spend >2x
# median as anomalies. Aggregates cost per WRK item over the last 30 sessions.
#
# Output record schema:
#   {"ts":"ISO8601","session_id":"...","provider":"claude","model":"sonnet-4-6",
#    "input_tokens":10000,"output_tokens":5000,"cost_usd":0.105,"wrk":"WRK-123",
#    "anomaly":false,"estimated":true}
#
# Returns 0 always — failures are logged, never fatal (best-effort readiness check).
# Called from: comprehensive-learning-nightly.sh (best-effort step)
# WRK-237
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
SIGNALS_DIR="${WORKSPACE_HUB}/.claude/state/session-signals"
COST_OUT="${SIGNALS_DIR}/cost-tracking.jsonl"
MODEL_REGISTRY="${WORKSPACE_HUB}/config/agents/model-registry.yaml"
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MAX_SESSIONS=30
ANOMALY_MULTIPLIER=2

mkdir -p "$SIGNALS_DIR"

log()  { echo "[cost-tracker] $*"; }
warn() { echo "[cost-tracker] WARN: $*" >&2; }

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

if ! command -v python3 &>/dev/null; then
  warn "python3 not found — cost tracking requires python3; skipping"
  exit 0
fi

# ---------------------------------------------------------------------------
# Delegate core logic to a Python helper written to a temp file.
# This avoids heredoc-in-function-in-subshell issues that cause hangs.
# ---------------------------------------------------------------------------

PY_HELPER=$(mktemp /tmp/cost_tracker_XXXXXX.py)
trap 'rm -f "$PY_HELPER"' EXIT

cat > "$PY_HELPER" << 'EOF'
"""
cost_tracker.py — provider cost tracking helper for provider-cost-tracker.sh

Invocation modes:
  python3 cost_tracker.py process  <signals_dir> <max_sessions> <registry> <run_ts>
      Reads session-signal JSONL files, estimates costs, prints pipe-separated records.

  python3 cost_tracker.py write    <cost_out> <max_sessions> <anomaly_mult> <run_ts>
      Reads pipe-separated records from stdin, writes JSONL to cost_out, prints summary.
"""
import sys
import os
import json
import math
import statistics
import collections
import re


# ---------------------------------------------------------------------------
# Pricing table ($/M tokens) — from model-registry.yaml or hard-coded fallback
# ---------------------------------------------------------------------------

FALLBACK_PRICING = {
    # (provider, model_fragment): (input_$/M, output_$/M)
    ("claude", "opus"):    (5.00,  25.00),
    ("claude", "sonnet"):  (3.00,  15.00),
    ("claude", "haiku"):   (0.80,   4.00),
    ("codex",  ""):        (2.00,   8.00),
    ("gemini", "pro"):     (1.25,   5.00),
    ("gemini", "flash"):   (0.15,   0.60),
    ("openai", "gpt-4"):   (2.00,   8.00),
}
DEFAULT_RATE = (3.00, 15.00)


def load_registry_pricing(registry_path):
    """Parse model-registry.yaml and return {(provider, model_key): (in_rate, out_rate)}."""
    pricing = {}
    if not registry_path or not os.path.isfile(registry_path):
        return pricing
    try:
        import yaml
        with open(registry_path) as f:
            reg = yaml.safe_load(f)
        providers = reg.get("providers", {})
        for prov_name, prov_data in providers.items():
            for model_key, model_data in prov_data.get("models", {}).items():
                cost = model_data.get("cost_usd_per_1m", {})
                inp = cost.get("input")
                out = cost.get("output")
                if inp is not None and out is not None:
                    pricing[(prov_name, model_key)] = (float(inp), float(out))
    except Exception:
        pass
    return pricing


def get_rates(provider, model, registry_pricing):
    """Return (input_rate, output_rate) in $/M tokens."""
    # Try exact registry match
    key = (provider, model)
    if key in registry_pricing:
        return registry_pricing[key]
    # Try partial registry match
    for (p, m), rates in registry_pricing.items():
        if p == provider and (model in m or m in model):
            return rates
    # Fallback table
    model_lower = model.lower()
    for (p, frag), rates in FALLBACK_PRICING.items():
        if p == provider and (not frag or frag in model_lower):
            return rates
    return DEFAULT_RATE


# ---------------------------------------------------------------------------
# Token heuristics
# ---------------------------------------------------------------------------

BASE_CONTEXT = 4000
INPUT_PER_TOOL = 2500
INPUT_PER_SCRIPT = 500
OUTPUT_PER_TOOL = 800
OUTPUT_PER_FILE = 1500
MIN_INPUT = 1000
MIN_OUTPUT = 200


def estimate_tokens(tool_calls, script_calls, new_files):
    """Return (input_tokens, output_tokens) from session activity signals."""
    inp = BASE_CONTEXT + tool_calls * INPUT_PER_TOOL + script_calls * INPUT_PER_SCRIPT
    out = tool_calls * OUTPUT_PER_TOOL + new_files * OUTPUT_PER_FILE
    return max(inp, MIN_INPUT), max(out, MIN_OUTPUT)


# ---------------------------------------------------------------------------
# Provider/model inference from session message text
# ---------------------------------------------------------------------------

def infer_provider_model(last_msg):
    """Infer (provider, model) from last_assistant_message text."""
    m = last_msg.lower()
    if re.search(r'\bcodex\b|o4-mini|openai codex', m):
        return "codex", "codex-cli"
    if re.search(r'\bgemini\b', m):
        return "gemini", "gemini-pro"
    if re.search(r'\bopus\b', m):
        return "claude", "opus-4-6"
    if re.search(r'\bhaiku\b', m):
        return "claude", "haiku-4-5"
    return "claude", "sonnet-4-6"


# ---------------------------------------------------------------------------
# Mode: process
# ---------------------------------------------------------------------------

def mode_process(signals_dir, max_sessions, registry_path, run_ts):
    """Read signal files; print pipe-separated cost records to stdout."""
    registry_pricing = load_registry_pricing(registry_path)

    # Collect candidate JSONL files (exclude special output files)
    EXCLUDE = {"cost-tracking.jsonl", "ai-readiness.jsonl",
               "test-health.jsonl", "network-mounts.jsonl",
               "network-mounts-cron.log"}
    files = sorted(
        f for f in os.listdir(signals_dir)
        if f.endswith(".jsonl") and f not in EXCLUDE
    )

    if not files:
        print("[cost-tracker] WARN: No session-signal files found", file=sys.stderr)
        return

    # Limit to last MAX_SESSIONS files
    files = files[-max_sessions:]
    print(f"[cost-tracker] Processing {len(files)} signal files", file=sys.stderr)

    record_count = 0
    for fname in files:
        fpath = os.path.join(signals_dir, fname)
        try:
            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    sig = d.get("signals", {})
                    session_id = d.get("session_id", "")
                    ts = d.get("ts", d.get("stop_ts", run_ts))
                    last_msg = d.get("last_assistant_message", "")

                    if not session_id:
                        session_id = re.sub(r'[: ]', '-', ts) if ts else fname

                    tcs = sig.get("tool_calls", [])
                    scs = sig.get("script_calls", [])
                    nfs = sig.get("new_files", [])
                    wrk_items = sig.get("wrk_items_touched", [])

                    tool_calls = len(tcs) if isinstance(tcs, list) else int(tcs or 0)
                    script_calls = len(scs) if isinstance(scs, list) else int(scs or 0)
                    new_files = len(nfs) if isinstance(nfs, list) else int(nfs or 0)

                    provider, model = infer_provider_model(last_msg)
                    in_rate, out_rate = get_rates(provider, model, registry_pricing)
                    in_tok, out_tok = estimate_tokens(tool_calls, script_calls,
                                                      new_files)
                    cost = (in_tok * in_rate + out_tok * out_rate) / 1_000_000

                    if wrk_items:
                        for wrk in wrk_items:
                            if wrk:
                                print(f"{session_id}|{ts}|{provider}|{model}"
                                      f"|{in_tok}|{out_tok}|{cost:.6f}|{wrk}")
                                record_count += 1
                    else:
                        print(f"{session_id}|{ts}|{provider}|{model}"
                              f"|{in_tok}|{out_tok}|{cost:.6f}|")
                        record_count += 1

        except OSError:
            pass

    print(f"[cost-tracker] Emitted {record_count} records", file=sys.stderr)


# ---------------------------------------------------------------------------
# Mode: write
# ---------------------------------------------------------------------------

def mode_write(cost_out, max_sessions, anomaly_mult, run_ts):
    """Read pipe-separated records from stdin; write JSONL + print summary."""
    lines = [l.rstrip('\n') for l in sys.stdin if l.strip()]

    # Filter to data lines (not log lines starting with [)
    data = [l for l in lines if l and not l.startswith("[")]

    if not data:
        print("[cost-tracker] No data records to write", file=sys.stderr)
        return

    # Parse records
    records = []
    for line in data:
        parts = line.split("|")
        if len(parts) < 7:
            continue
        sid, ts, prov, model, in_tok, out_tok, cost = parts[:7]
        wrk = parts[7] if len(parts) > 7 else ""
        try:
            records.append({
                "session_id": sid,
                "ts": ts,
                "provider": prov,
                "model": model,
                "input_tokens": int(in_tok),
                "output_tokens": int(out_tok),
                "cost_usd": float(cost),
                "wrk": wrk,
            })
        except (ValueError, IndexError):
            continue

    if not records:
        print("[cost-tracker] No valid records parsed", file=sys.stderr)
        return

    # Compute per-session cost (sum across WRK attributions) for median
    session_costs = collections.defaultdict(float)
    for r in records:
        session_costs[r["session_id"]] += r["cost_usd"]
    session_cost_vals = list(session_costs.values())
    median_cost = statistics.median(session_cost_vals) if session_cost_vals else 0
    threshold = median_cost * anomaly_mult

    # Write JSONL records
    written = 0
    anomalies = []
    seen = set()
    with open(cost_out, "a") as f:
        for r in records:
            key = f"{r['session_id']}:{r['wrk']}"
            if key in seen:
                continue
            seen.add(key)

            sess_cost = session_costs.get(r["session_id"], r["cost_usd"])
            is_anomaly = bool(threshold > 0 and sess_cost > threshold)
            if is_anomaly and r["session_id"] not in anomalies:
                anomalies.append(r["session_id"])

            rec = {
                "ts": r["ts"] or run_ts,
                "session_id": r["session_id"],
                "provider": r["provider"],
                "model": r["model"],
                "input_tokens": r["input_tokens"],
                "output_tokens": r["output_tokens"],
                "cost_usd": round(r["cost_usd"], 6),
                "wrk": r["wrk"],
                "anomaly": is_anomaly,
                "estimated": True,
                "run_ts": run_ts,
            }
            f.write(json.dumps(rec) + "\n")
            written += 1

    print(f"[cost-tracker] Wrote {written} records to {cost_out}")
    if anomalies:
        print(f"[cost-tracker] ANOMALY: {len(anomalies)} session(s) with spend "
              f">2x median (${median_cost:.4f}): {', '.join(anomalies[:5])}")

    # Aggregate summary
    wrk_cost: dict = collections.defaultdict(float)
    wrk_sess: dict = collections.defaultdict(set)
    prov_cost: dict = collections.defaultdict(float)
    prov_in: dict = collections.defaultdict(int)
    prov_out: dict = collections.defaultdict(int)

    for r in records:
        if r["wrk"]:
            wrk_cost[r["wrk"]] += r["cost_usd"]
            wrk_sess[r["wrk"]].add(r["session_id"])
        prov_cost[r["provider"]] += r["cost_usd"]
        prov_in[r["provider"]] += r["input_tokens"]
        prov_out[r["provider"]] += r["output_tokens"]

    print(f"\n[cost-tracker] === Cost Summary (last {max_sessions} sessions) ===")
    print("[cost-tracker] Provider breakdown:")
    for prov, cost in sorted(prov_cost.items(), key=lambda x: -x[1]):
        print(f"[cost-tracker]   {prov:12s}  ${cost:.4f}  "
              f"in:{prov_in[prov]:>9,}  out:{prov_out[prov]:>9,}")

    if wrk_cost:
        print("[cost-tracker] Top 10 WRK items by cost:")
        for wrk, cost in sorted(wrk_cost.items(), key=lambda x: -x[1])[:10]:
            n = len(wrk_sess[wrk])
            print(f"[cost-tracker]   {wrk:12s}  ${cost:.4f}  ({n} session(s))")

    total = sum(prov_cost.values())
    print(f"[cost-tracker] Total estimated spend in window: ${total:.4f}")
    print(f"[cost-tracker] Median session cost: ${median_cost:.4f} | "
          f"Anomaly threshold: ${threshold:.4f}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cost_tracker.py <process|write> [args...]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "process":
        signals_dir  = sys.argv[2]
        max_sessions = int(sys.argv[3])
        registry     = sys.argv[4] if len(sys.argv) > 4 else ""
        run_ts       = sys.argv[5] if len(sys.argv) > 5 else ""
        mode_process(signals_dir, max_sessions, registry, run_ts)
    elif mode == "write":
        cost_out     = sys.argv[2]
        max_sessions = int(sys.argv[3])
        anomaly_mult = float(sys.argv[4])
        run_ts       = sys.argv[5] if len(sys.argv) > 5 else ""
        mode_write(cost_out, max_sessions, anomaly_mult, run_ts)
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)
EOF

log "Starting provider cost tracking — ${RUN_TS}"

# ---------------------------------------------------------------------------
# Step 1: Process signal files → pipe-separated cost records
# ---------------------------------------------------------------------------

log "Processing session-signal files..."
PROCESS_OUT=$(python3 "$PY_HELPER" process \
  "$SIGNALS_DIR" \
  "$MAX_SESSIONS" \
  "$MODEL_REGISTRY" \
  "$RUN_TS" 2>&1) || {
  warn "Signal processing failed"
  exit 0
}

# Print log lines from python
printf '%s\n' "$PROCESS_OUT" | grep '^\[cost-tracker\]'

# Extract data lines (non-log)
DATA_LINES=$(printf '%s\n' "$PROCESS_OUT" | grep -v '^\[cost-tracker\]' | grep -v '^$' || true)

if [[ -z "$DATA_LINES" ]]; then
  warn "No processable session records found"
  exit 0
fi

# ---------------------------------------------------------------------------
# Step 2: Write JSONL + print summary
# ---------------------------------------------------------------------------

log "Writing cost records..."
printf '%s\n' "$DATA_LINES" \
  | python3 "$PY_HELPER" write \
      "$COST_OUT" \
      "$MAX_SESSIONS" \
      "$ANOMALY_MULTIPLIER" \
      "$RUN_TS"

log "Cost tracking complete"
