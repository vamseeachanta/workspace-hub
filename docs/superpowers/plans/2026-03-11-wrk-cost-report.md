# WRK-1069: Per-WRK Token Cost Attribution — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable per-WRK AI spend reporting by writing `scripts/ai/wrk-cost-report.py`, consolidating pricing into `config/ai-tools/pricing.yaml`, and integrating cost summary into `close-item.sh`.

**Architecture:** The `cost-tracking.jsonl` already has full per-session, per-WRK cost records (`wrk` field confirmed). This plan builds the reporting layer on top: a standalone Python script that reads that JSONL, groups by WRK, and renders a cost table. Pricing lives in a dedicated YAML so it can be updated without touching the tracker script.

**Tech Stack:** Python 3 (stdlib only — json, sys, argparse, csv), bash, YAML, uv run --no-project

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `config/ai-tools/pricing.yaml` | Canonical per-model pricing (input/output $/1M tokens) |
| Create | `scripts/ai/wrk-cost-report.py` | Read cost-tracking.jsonl, aggregate by WRK, render table |
| Create | `scripts/ai/tests/test_wrk_cost_report.py` | TDD tests for aggregation and formatting logic |
| Modify | `scripts/work-queue/close-item.sh` | Call wrk-cost-report.py at close and print summary |

---

## Chunk 1: Pricing YAML + Aggregation Script (TDD)

### Task 1: Create `config/ai-tools/pricing.yaml`

**Files:**
- Create: `config/ai-tools/pricing.yaml`

Pricing data comes from `config/agents/model-registry.yaml` (cost_usd_per_1m fields). Do NOT duplicate — extract only what wrk-cost-report.py needs.

- [ ] **Step 1: Write pricing.yaml**

```yaml
# config/ai-tools/pricing.yaml
# Per-model pricing in USD per 1M tokens.
# Update manually when provider pricing changes.
# Source: https://www.anthropic.com/pricing (Claude), https://openai.com/pricing, Google AI
version: "2026-03-11"
models:
  claude-opus-4-6:
    provider: claude
    input_per_1m: 5.00
    output_per_1m: 25.00
  claude-sonnet-4-6:
    provider: claude
    input_per_1m: 3.00
    output_per_1m: 15.00
  claude-haiku-4-5:
    provider: claude
    input_per_1m: 0.80
    output_per_1m: 4.00
  o4-mini:
    provider: codex
    input_per_1m: 0.50
    output_per_1m: 1.50
  gemini-2.5-pro:
    provider: gemini
    input_per_1m: 0.075
    output_per_1m: 0.30
  gemini-2.5-flash:
    provider: gemini
    input_per_1m: 0.075
    output_per_1m: 0.30
defaults:
  unknown_model:
    input_per_1m: 3.00
    output_per_1m: 15.00
```

- [ ] **Step 2: Verify YAML is valid**

```bash
uv run --no-project python -c "import json, sys; import subprocess; r=subprocess.run(['uv','run','--no-project','python','-c','import yaml,sys; yaml.safe_load(open(sys.argv[1]))',  'config/ai-tools/pricing.yaml'], capture_output=True, text=True); print('OK' if r.returncode==0 else r.stderr)"
```
Expected: OK (or just check no parse error)

- [ ] **Step 3: Commit**

```bash
git add config/ai-tools/pricing.yaml
git commit -m "feat(harness): add canonical ai-tools/pricing.yaml for WRK cost attribution"
```

---

### Task 2: TDD — Write failing tests for wrk-cost-report.py

**Files:**
- Create: `scripts/ai/tests/test_wrk_cost_report.py`

The cost-tracking.jsonl schema (confirmed from live data):
```
{"ts":"...","session_id":"...","provider":"claude","model":"sonnet-4-6",
 "input_tokens":4000,"output_tokens":200,"cost_usd":0.015000,
 "wrk":"WRK-287","anomaly":false,"estimated":true,"run_ts":"..."}
```

- [ ] **Step 1: Write failing tests**

```python
# scripts/ai/tests/test_wrk_cost_report.py
"""Tests for wrk-cost-report.py aggregation logic."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import wrk_cost_report as wcr


SAMPLE_RECORDS = [
    {"ts": "2026-03-01T10:00:00Z", "session_id": "s1", "provider": "claude",
     "model": "sonnet-4-6", "input_tokens": 10000, "output_tokens": 2000,
     "cost_usd": 0.06, "wrk": "WRK-100", "anomaly": False, "estimated": True},
    {"ts": "2026-03-01T11:00:00Z", "session_id": "s2", "provider": "claude",
     "model": "opus-4-6", "input_tokens": 5000, "output_tokens": 1000,
     "cost_usd": 0.05, "wrk": "WRK-100", "anomaly": False, "estimated": True},
    {"ts": "2026-03-02T09:00:00Z", "session_id": "s3", "provider": "codex",
     "model": "o4-mini", "input_tokens": 8000, "output_tokens": 500,
     "cost_usd": 0.0075, "wrk": "WRK-200", "anomaly": False, "estimated": True},
]


def _make_jsonl(records: list[dict]) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for r in records:
        f.write(json.dumps(r) + "\n")
    f.close()
    return Path(f.name)


def test_load_records_returns_all_lines():
    path = _make_jsonl(SAMPLE_RECORDS)
    records = wcr.load_records(path)
    assert len(records) == 3


def test_load_records_skips_malformed_lines():
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    f.write('{"wrk":"WRK-1","cost_usd":0.01}\n')
    f.write("not-json\n")
    f.write('{"wrk":"WRK-1","cost_usd":0.02}\n')
    f.close()
    records = wcr.load_records(Path(f.name))
    assert len(records) == 2


def test_aggregate_by_wrk_sums_tokens_and_cost():
    result = wcr.aggregate_by_wrk(SAMPLE_RECORDS)
    assert "WRK-100" in result
    assert result["WRK-100"]["input_tokens"] == 15000
    assert result["WRK-100"]["output_tokens"] == 3000
    assert abs(result["WRK-100"]["cost_usd"] - 0.11) < 0.001
    assert result["WRK-100"]["session_count"] == 2


def test_aggregate_by_wrk_handles_empty():
    assert wcr.aggregate_by_wrk([]) == {}


def test_filter_by_wrk_returns_only_matching():
    result = wcr.aggregate_by_wrk(SAMPLE_RECORDS, wrk_filter="WRK-100")
    assert set(result.keys()) == {"WRK-100"}


def test_format_cost_table_includes_headers():
    data = wcr.aggregate_by_wrk(SAMPLE_RECORDS)
    table = wcr.format_cost_table(data)
    assert "WRK-ID" in table
    assert "INPUT" in table
    assert "OUTPUT" in table
    assert "COST_USD" in table


def test_format_cost_table_single_wrk():
    data = wcr.aggregate_by_wrk(SAMPLE_RECORDS, wrk_filter="WRK-100")
    table = wcr.format_cost_table(data)
    assert "WRK-100" in table
    assert "WRK-200" not in table
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd /mnt/local-analysis/workspace-hub
uv run --no-project python -m pytest scripts/ai/tests/test_wrk_cost_report.py -v 2>&1 | head -30
```
Expected: ImportError or ModuleNotFoundError (wrk_cost_report not found yet)

---

### Task 3: Implement `scripts/ai/wrk-cost-report.py`

**Files:**
- Create: `scripts/ai/wrk-cost-report.py`

- [ ] **Step 1: Write implementation**

```python
#!/usr/bin/env python3
"""
wrk-cost-report.py — Aggregate AI token costs by WRK item.

Usage:
  uv run --no-project python scripts/ai/wrk-cost-report.py           # all WRKs
  uv run --no-project python scripts/ai/wrk-cost-report.py WRK-NNN  # single WRK
  uv run --no-project python scripts/ai/wrk-cost-report.py --csv     # CSV output

Reads: .claude/state/session-signals/cost-tracking.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

COST_TRACKING_PATH = Path(".claude/state/session-signals/cost-tracking.jsonl")
REPO_ROOT = Path(__file__).parent.parent.parent


def load_records(path: Path) -> list[dict]:
    """Load all valid JSONL records from path."""
    records = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    except FileNotFoundError:
        print(f"ERROR: {path} not found", file=sys.stderr)
    return records


def aggregate_by_wrk(
    records: list[dict], wrk_filter: str | None = None
) -> dict[str, dict]:
    """Sum tokens and cost per WRK item."""
    result: dict[str, dict] = {}
    for r in records:
        wrk = r.get("wrk", "UNKNOWN")
        if wrk_filter and wrk != wrk_filter:
            continue
        if wrk not in result:
            result[wrk] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
                "session_count": 0,
                "providers": set(),
            }
        result[wrk]["input_tokens"] += r.get("input_tokens", 0)
        result[wrk]["output_tokens"] += r.get("output_tokens", 0)
        result[wrk]["cost_usd"] += r.get("cost_usd", 0.0)
        result[wrk]["session_count"] += 1
        result[wrk]["providers"].add(r.get("provider", "unknown"))
    return result


def format_cost_table(data: dict[str, dict], csv_mode: bool = False) -> str:
    """Render aggregated cost data as a formatted table or CSV."""
    if not data:
        return "(no records)"
    rows = sorted(data.items(), key=lambda x: x[1]["cost_usd"], reverse=True)
    if csv_mode:
        lines = ["WRK-ID,INPUT,OUTPUT,COST_USD,SESSIONS,PROVIDERS"]
        for wrk, d in rows:
            providers = "|".join(sorted(d["providers"]))
            lines.append(
                f"{wrk},{d['input_tokens']},{d['output_tokens']},"
                f"{d['cost_usd']:.4f},{d['session_count']},{providers}"
            )
        return "\n".join(lines)
    # Human-readable table
    lines = [
        f"{'WRK-ID':<12} {'INPUT':>10} {'OUTPUT':>10} {'COST_USD':>10} "
        f"{'SESSIONS':>9} {'PROVIDERS'}",
        "-" * 70,
    ]
    for wrk, d in rows:
        providers = "+".join(sorted(d["providers"]))
        lines.append(
            f"{wrk:<12} {d['input_tokens']:>10,} {d['output_tokens']:>10,} "
            f"${d['cost_usd']:>9.4f} {d['session_count']:>9} {providers}"
        )
    total_cost = sum(d["cost_usd"] for d in data.values())
    lines.append("-" * 70)
    lines.append(f"{'TOTAL':<12} {'':>10} {'':>10} ${total_cost:>9.4f}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="WRK AI cost report")
    parser.add_argument("wrk_id", nargs="?", help="Filter to single WRK (e.g. WRK-100)")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.add_argument(
        "--data-file",
        default=str(REPO_ROOT / COST_TRACKING_PATH),
        help="Path to cost-tracking.jsonl",
    )
    args = parser.parse_args()

    records = load_records(Path(args.data_file))
    if not records:
        print("No cost records found.", file=sys.stderr)
        sys.exit(1)

    data = aggregate_by_wrk(records, wrk_filter=args.wrk_id)
    if not data:
        msg = f"No records for {args.wrk_id}" if args.wrk_id else "No records"
        print(msg, file=sys.stderr)
        sys.exit(1)

    print(format_cost_table(data, csv_mode=args.csv))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run tests — verify they pass**

```bash
cd /mnt/local-analysis/workspace-hub
uv run --no-project python -m pytest scripts/ai/tests/test_wrk_cost_report.py -v
```
Expected: 7 PASSED

- [ ] **Step 3: Smoke test with live data**

```bash
uv run --no-project python scripts/ai/wrk-cost-report.py 2>&1 | head -20
```
Expected: table with WRK-NNN rows, no errors

- [ ] **Step 4: Commit**

```bash
git add scripts/ai/wrk-cost-report.py scripts/ai/tests/test_wrk_cost_report.py
git commit -m "feat(harness): add wrk-cost-report.py — per-WRK AI token cost aggregation"
```

---

## Chunk 2: close-item.sh Integration

### Task 4: Integrate cost summary into `close-item.sh`

**Files:**
- Modify: `scripts/work-queue/close-item.sh`

The script currently handles HTML gate evidence. We append a cost summary block at the end of the normal close flow (before the final exit 0).

- [ ] **Step 1: Read close-item.sh to find insertion point**

```bash
grep -n "exit 0\|echo.*Done\|echo.*Closed" scripts/work-queue/close-item.sh | tail -10
```

- [ ] **Step 2: Add cost summary call before final exit**

Find the last `echo` or `exit 0` block and insert before it:

```bash
# Print WRK cost summary at close (best-effort — don't fail close if script missing)
if [[ -f "scripts/ai/wrk-cost-report.py" ]]; then
    echo ""
    echo "=== AI Cost Summary: ${WRK_ID} ==="
    uv run --no-project python scripts/ai/wrk-cost-report.py "${WRK_ID}" 2>/dev/null \
        || echo "(no cost records found for ${WRK_ID})"
fi
```

> Use the actual WRK_ID variable name from close-item.sh — check with `grep -n 'WRK_ID\|wrk_id' scripts/work-queue/close-item.sh | head -5`

- [ ] **Step 3: Test integration**

```bash
# Dry-run: just check cost report for a real WRK
uv run --no-project python scripts/ai/wrk-cost-report.py WRK-1069 2>&1
```
Expected: table or "(no records)" — either is acceptable

- [ ] **Step 4: Commit**

```bash
git add scripts/work-queue/close-item.sh
git commit -m "feat(harness): print AI cost summary in close-item.sh at WRK close"
```

---

## Verification

After all tasks complete, run:

```bash
# 1. All tests pass
uv run --no-project python -m pytest scripts/ai/tests/test_wrk_cost_report.py -v

# 2. Report runs without error
uv run --no-project python scripts/ai/wrk-cost-report.py 2>&1 | head -5

# 3. CSV mode works
uv run --no-project python scripts/ai/wrk-cost-report.py --csv 2>&1 | head -5

# 4. pricing.yaml is valid YAML
uv run --no-project python -c "import yaml; yaml.safe_load(open('config/ai-tools/pricing.yaml'))" && echo "OK"
```
