"""Synthetic incremental-window examples for the backfill contract in #3138.

Basis: the inclusive calendar-day windows and (session_id, ts, skill_name) key
specified by #3138 and exercised in test_backfill_skill_invocations.py. Dates
below are invented fixture values, not observations from retained transcripts.
Expected keys and filenames are written explicitly, independently of the parser.

Hand calculation for the overlapping example: the first May window admits the
May 1 alpha row and the May 2 alpha/beta rows (three keys). The next window
retains those rows and adds the May 3 row plus a distinct secondary-source key
(two additions). April 30 and May 4 remain excluded; the copied key adds nothing.
The append example starts with two keys and adds one May 2 key. An identical
rerun adds zero keys and leaves every output byte unchanged.
"""

from collections import Counter
import json

from test_backfill_skill_invocations import (
    _setup_transcripts,
    _transcript_record,
    _write_jsonl,
    bf as bf,
)


def _snapshot(out):
    """Include every output entry so extra files or directories fail comparison."""
    return {
        path.relative_to(out).as_posix(): path.read_bytes() if path.is_file() else None
        for path in out.rglob("*")
    }


def _assert_keys_by_file(out, expected):
    snapshot = _snapshot(out)
    assert set(snapshot) == set(expected)
    for filename, keys in expected.items():
        rows = [json.loads(line) for line in snapshot[filename].splitlines()]
        actual = Counter(
            (row["session_id"], row["ts"], row["skill_name"]) for row in rows
        )
        # A multiset detects duplicate rows as well as missing or unexpected keys.
        assert actual == Counter(keys), filename


def test_overlapping_windows_do_not_duplicate(bf, tmp_path):
    skill_alpha = str(tmp_path / ".claude/skills/testing/alpha/SKILL.md")
    skill_beta = str(tmp_path / ".claude/skills/testing/beta/SKILL.md")
    transcripts = _setup_transcripts(
        tmp_path,
        [
            _transcript_record(
                "Read", skill_alpha, ts="2026-04-30T23:59:59.000Z", sid="fixture-a"
            ),
            _transcript_record(
                "Read", skill_alpha, ts="2026-05-01T00:00:00.000Z", sid="fixture-a"
            ),
            _transcript_record(
                "Read", skill_alpha, ts="2026-05-02T12:00:00.000Z", sid="fixture-a"
            ),
            _transcript_record(
                "Read", skill_beta, ts="2026-05-02T12:00:00.000Z", sid="fixture-a"
            ),
            _transcript_record(
                "Read", skill_alpha, ts="2026-05-03T23:59:59.000Z", sid="fixture-b"
            ),
            _transcript_record(
                "Read", skill_alpha, ts="2026-05-04T00:00:00.000Z", sid="fixture-b"
            ),
        ],
    )
    out = tmp_path / "out"
    first = bf.backfill(
        transcripts_root=transcripts,
        sessions_dirs=[],
        out_dir=out,
        since="2026-05-01",
        until="2026-05-02",
    )
    expected_first = {
        "session_20260501.backfill.jsonl": [
            ("fixture-a", "2026-05-01T00:00:00.000Z", "testing/alpha"),
        ],
        "session_20260502.backfill.jsonl": [
            ("fixture-a", "2026-05-02T12:00:00.000Z", "testing/alpha"),
            ("fixture-a", "2026-05-02T12:00:00.000Z", "testing/beta"),
        ],
    }
    _assert_keys_by_file(out, expected_first)
    assert first["events_written"] == 3  # May 1 alpha + May 2 alpha/beta.
    previous = _snapshot(out)

    # Introduce the second source only after the first output has been persisted.
    secondary = tmp_path / "secondary"
    secondary.mkdir()
    _write_jsonl(
        secondary / "session_20260502.jsonl",
        [
            {
                "ts": "2026-05-02T12:00:00.000Z",
                "tool": "Read",
                "file": skill_alpha,
                "session_id": "fixture-a",
            },
            {
                "ts": "2026-05-02T12:00:00.000Z",
                "tool": "Read",
                "file": skill_alpha,
                "session_id": "fixture-b",
            },
        ],
    )
    second = bf.backfill(
        transcripts_root=transcripts,
        sessions_dirs=[secondary],
        out_dir=out,
        since="2026-05-02",
        until="2026-05-03",
    )
    _assert_keys_by_file(
        out,
        {
            "session_20260501.backfill.jsonl": [
                ("fixture-a", "2026-05-01T00:00:00.000Z", "testing/alpha"),
            ],
            "session_20260502.backfill.jsonl": [
                ("fixture-a", "2026-05-02T12:00:00.000Z", "testing/alpha"),
                ("fixture-a", "2026-05-02T12:00:00.000Z", "testing/beta"),
                ("fixture-b", "2026-05-02T12:00:00.000Z", "testing/alpha"),
            ],
            "session_20260503.backfill.jsonl": [
                ("fixture-b", "2026-05-03T23:59:59.000Z", "testing/alpha"),
            ],
        },
    )
    assert second["events_written"] == 2  # May 3 + the distinct secondary key.
    assert (out / "session_20260501.backfill.jsonl").read_bytes() == previous[
        "session_20260501.backfill.jsonl"
    ]


def test_append_then_rerun_preserves_previous_rows(bf, tmp_path):
    skill = str(tmp_path / ".claude/skills/testing/alpha/SKILL.md")
    transcripts = _setup_transcripts(
        tmp_path,
        [
            _transcript_record(
                "Read", skill, ts="2026-05-01T10:00:00.000Z", sid="fixture-a"
            ),
            _transcript_record(
                "Read", skill, ts="2026-05-02T10:00:00.000Z", sid="fixture-a"
            ),
        ],
    )
    out = tmp_path / "out"
    options = dict(
        transcripts_root=transcripts,
        sessions_dirs=[],
        out_dir=out,
        since="2026-05-01",
        until="2026-05-02",
    )
    bf.backfill(**options)
    _assert_keys_by_file(
        out,
        {
            "session_20260501.backfill.jsonl": [
                ("fixture-a", "2026-05-01T10:00:00.000Z", "testing/alpha"),
            ],
            "session_20260502.backfill.jsonl": [
                ("fixture-a", "2026-05-02T10:00:00.000Z", "testing/alpha"),
            ],
        },
    )
    previous = _snapshot(out)
    # Append to the existing transcript, rather than replacing its earlier rows.
    with (transcripts / "-p" / "t.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps(
                _transcript_record(
                    "Read", skill, ts="2026-05-02T11:00:00.000Z", sid="fixture-a"
                )
            )
            + "\n"
        )

    stats = bf.backfill(**options)
    assert stats["events_written"] == 1  # Only the appended May 2 key is new.
    _assert_keys_by_file(
        out,
        {
            "session_20260501.backfill.jsonl": [
                ("fixture-a", "2026-05-01T10:00:00.000Z", "testing/alpha"),
            ],
            "session_20260502.backfill.jsonl": [
                ("fixture-a", "2026-05-02T10:00:00.000Z", "testing/alpha"),
                ("fixture-a", "2026-05-02T11:00:00.000Z", "testing/alpha"),
            ],
        },
    )
    after = _snapshot(out)
    assert after["session_20260501.backfill.jsonl"] == previous[
        "session_20260501.backfill.jsonl"
    ]
    assert after["session_20260502.backfill.jsonl"].startswith(
        previous["session_20260502.backfill.jsonl"]
    )


def test_identical_rerun_preserves_output_bytes(bf, tmp_path):
    skill = str(tmp_path / ".claude/skills/testing/alpha/SKILL.md")
    transcripts = _setup_transcripts(
        tmp_path,
        [
            _transcript_record(
                "Read", skill, ts="2026-05-01T10:00:00.000Z", sid="fixture-a"
            ),
            _transcript_record(
                "Read", skill, ts="2026-05-02T10:00:00.000Z", sid="fixture-a"
            ),
        ],
    )
    out = tmp_path / "out"
    options = dict(
        transcripts_root=transcripts,
        sessions_dirs=[],
        out_dir=out,
        since="2026-05-01",
        until="2026-05-02",
    )
    bf.backfill(**options)
    _assert_keys_by_file(
        out,
        {
            "session_20260501.backfill.jsonl": [
                ("fixture-a", "2026-05-01T10:00:00.000Z", "testing/alpha"),
            ],
            "session_20260502.backfill.jsonl": [
                ("fixture-a", "2026-05-02T10:00:00.000Z", "testing/alpha"),
            ],
        },
    )
    previous = _snapshot(out)

    stats = bf.backfill(**options)

    assert stats["events_written"] == 0  # Every input key is already persisted.
    assert _snapshot(out) == previous
