from pathlib import Path
from scripts.ecosystem_sync.digest import render_digest
from scripts.ecosystem_sync.models import Signal

GOLDEN = Path(__file__).parent / "golden"


def test_render_empty_day():
    out = render_digest(
        signals_by_repo={},
        skipped={},
        date="2026-04-20",
        duration_s=42,
        repos_total=6,
        issues_filed=0,
        suppressed_signals=[],
    )
    expected = (GOLDEN / "empty.md").read_text()
    assert out == expected


def test_render_with_signals():
    sig = Signal(
        repo="digitalmodel", kind="release",
        title="[sync] digitalmodel released v2.1.3",
        body="body here",
        dedupe_key="release:digitalmodel:v2.1.3",
        payload={"tag": "v2.1.3"},
    )
    out = render_digest(
        signals_by_repo={"digitalmodel": [sig]},
        skipped={"doris": "fetch timeout"},
        date="2026-04-20",
        duration_s=47,
        repos_total=6,
        issues_filed=1,
        suppressed_signals=[],
    )
    expected = (GOLDEN / "with_signals.md").read_text()
    assert out == expected
