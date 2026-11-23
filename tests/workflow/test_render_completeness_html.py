"""Data-contract tests for the #2798 HTML renderer.

Per review fix (Claude#6 / Codex#19): assert the DATA the artifact carries, not
the CSS/markup. The rendered HTML must embed the exact persisted record (the same
```completeness {json}``` block the gate reads) so the artifact cannot drift from
the score that gates closure.
"""
import json
import re
import sys
from pathlib import Path

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import render_completeness_html as rch  # noqa: E402

_RECORD_RE = re.compile(r"```completeness\s*(\{.*?\})\s*```", re.DOTALL)


def _result(pct=95):
    return {
        "completeness_pct": pct,
        "cls": "code",
        "threshold": 90,
        "passed": pct >= 90,
        "snapshot_sha": "abc123",
        "evidence": ["digitalmodel: quality_score=95 test_source_ratio=0.9 -> 95",
                     "changed_code_coverage=0.92 (factor 1)"],
    }


def test_html_embeds_exact_record_roundtrip():
    html = rch.render_html(_result(95), issue=2798, title="demo")
    m = _RECORD_RE.search(html)
    assert m, "rendered HTML must embed a ```completeness {json}``` block"
    assert json.loads(m.group(1)) == _result(95)  # exact round-trip, no drift


def test_html_shows_pct_threshold_and_verdict():
    html = rch.render_html(_result(95), issue=2798, title="demo")
    assert "95" in html and "90" in html
    assert "PASS" in html.upper()


def test_html_shows_fail_verdict_below_threshold():
    html = rch.render_html(_result(70), issue=2798, title="demo")
    assert "FAIL" in html.upper() or "BLOCK" in html.upper()


def test_html_lists_every_evidence_item():
    res = _result(95)
    html = rch.render_html(res, issue=2798, title="demo")
    for ev in res["evidence"]:
        # evidence text appears (HTML-escaped ok — check a stable substring)
        assert ev.split(":")[0] in html


def test_html_is_escaped_against_injection():
    res = _result(95)
    res["evidence"] = ['<script>alert(1)</script>']
    html = rch.render_html(res, issue=2798, title="demo")
    assert "<script>alert(1)</script>" not in html  # must be escaped
