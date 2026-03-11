"""Tests for wrk_cost_report.py aggregation logic."""
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
     "model": "claude-opus-4-6", "input_tokens": 5000, "output_tokens": 1000,
     "cost_usd": 0.05, "wrk": "WRK-100", "anomaly": False, "estimated": True},
    {"ts": "2026-03-02T09:00:00Z", "session_id": "s3", "provider": "codex",
     "model": "o4-mini", "input_tokens": 8000, "output_tokens": 500,
     "cost_usd": 0.0075, "wrk": "WRK-200", "anomaly": False, "estimated": True},
]


def _make_jsonl(records):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for r in records:
        f.write(json.dumps(r) + "\n")
    f.close()
    return Path(f.name)


def test_load_records_returns_all_lines():
    path = _make_jsonl(SAMPLE_RECORDS)
    records, _ = wcr.load_records(path)
    assert len(records) == 3


def test_load_records_skips_malformed_lines():
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    f.write('{"wrk":"WRK-1","cost_usd":0.01,"input_tokens":100,"output_tokens":10}\n')
    f.write("not-json\n")
    f.write('{"wrk":"WRK-1","cost_usd":0.02,"input_tokens":200,"output_tokens":20}\n')
    f.close()
    records, skipped = wcr.load_records(Path(f.name))
    assert len(records) == 2
    assert skipped == 1


def test_load_records_returns_skip_count():
    path = _make_jsonl(SAMPLE_RECORDS)
    records, skipped = wcr.load_records(path)
    assert skipped == 0


def test_aggregate_by_wrk_sums_tokens_and_cost():
    records, _ = wcr.load_records(_make_jsonl(SAMPLE_RECORDS))
    result = wcr.aggregate_by_wrk(records)
    assert "WRK-100" in result
    assert result["WRK-100"]["input_tokens"] == 15000
    assert result["WRK-100"]["output_tokens"] == 3000
    assert abs(result["WRK-100"]["cost_usd"] - 0.11) < 0.001
    assert result["WRK-100"]["session_count"] == 2


def test_aggregate_by_wrk_handles_empty():
    assert wcr.aggregate_by_wrk([]) == {}


def test_filter_by_wrk_returns_only_matching():
    records, _ = wcr.load_records(_make_jsonl(SAMPLE_RECORDS))
    result = wcr.aggregate_by_wrk(records, wrk_filter="WRK-100")
    assert set(result.keys()) == {"WRK-100"}


def test_missing_wrk_field_goes_to_unattributed():
    records = [{"ts": "2026-03-01T10:00:00Z", "provider": "claude", "model": "sonnet-4-6",
                "input_tokens": 1000, "output_tokens": 100, "cost_usd": 0.003}]
    result = wcr.aggregate_by_wrk(records)
    assert "unattributed" in result


def test_format_cost_table_includes_headers():
    records, _ = wcr.load_records(_make_jsonl(SAMPLE_RECORDS))
    data = wcr.aggregate_by_wrk(records)
    table = wcr.format_cost_table(data, skipped=0)
    assert "WRK-ID" in table
    assert "INPUT" in table
    assert "COST_USD" in table


def test_format_cost_table_shows_skipped_count():
    records, _ = wcr.load_records(_make_jsonl(SAMPLE_RECORDS))
    data = wcr.aggregate_by_wrk(records)
    table = wcr.format_cost_table(data, skipped=3)
    assert "3 records skipped" in table


def test_load_records_missing_file_returns_empty():
    records, skipped = wcr.load_records(Path("/nonexistent/path.jsonl"))
    assert records == []
    assert skipped == 0


def test_aggregate_skips_non_numeric_fields_no_orphan_bucket():
    """Non-numeric tokens/cost: record is skipped and no empty bucket created."""
    records = [
        {"wrk": "WRK-BAD", "input_tokens": "not-a-number", "output_tokens": 0,
         "cost_usd": 0.01, "provider": "claude"},
        {"wrk": "WRK-OK", "input_tokens": 1000, "output_tokens": 100,
         "cost_usd": 0.003, "provider": "claude"},
    ]
    result = wcr.aggregate_by_wrk(records)
    assert "WRK-BAD" not in result
    assert "WRK-OK" in result
    assert result["WRK-OK"]["session_count"] == 1


def test_format_cost_table_csv_mode_valid_csv():
    """CSV mode output is parseable and handles commas/quotes in values."""
    import csv as csv_mod
    records = [{"wrk": "WRK-1,x", "input_tokens": 100, "output_tokens": 10,
                "cost_usd": 0.01, "provider": 'prov"a'}]
    data = wcr.aggregate_by_wrk(records)
    output = wcr.format_cost_table(data, skipped=0, csv_mode=True)
    rows = list(csv_mod.reader(output.splitlines()))
    assert rows[0] == ["WRK-ID", "INPUT", "OUTPUT", "COST_USD", "SESSIONS", "PROVIDERS"]
    assert rows[1][0] == "WRK-1,x"


def test_format_cost_table_csv_skipped_not_in_stdout(capsys):
    """CSV mode: skipped footer goes to stderr, not stdout."""
    records, _ = wcr.load_records(_make_jsonl(SAMPLE_RECORDS))
    data = wcr.aggregate_by_wrk(records)
    output = wcr.format_cost_table(data, skipped=5, csv_mode=True)
    assert "skipped" not in output
    captured = capsys.readouterr()
    assert "5 records skipped" in captured.err
