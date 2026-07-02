import random

from adapters.base import SearchResult
from merge import ranked_merge
from pathnorm import canonicalize_path


def _row(path, source, basis="token_match", raw_score=1.0, matched=1, total=1):
    return SearchResult(
        raw_path=path,
        source_index=source,
        adapter="fixture",
        raw_score=raw_score,
        rank_basis=basis,
        meta={"matched_tokens": matched, "total_tokens": total},
    )


def test_ranked_merge_deterministic():
    rows = [
        _row("/canonical/dde/b.pdf", "b"),
        _row("/canonical/dde/a.pdf", "a"),
        _row("/canonical/dde/c.pdf", "a"),
    ]
    outputs = []

    for _ in range(10):
        shuffled = rows[:]
        random.shuffle(shuffled)
        outputs.append([row.as_dict() for row in ranked_merge(shuffled, {}, limit=10)])

    assert all(output == outputs[0] for output in outputs)


def test_ranked_merge_dedupes_canonical_path():
    rows = [
        _row("/legacy/dde/same.pdf", "jsonl"),
        _row("/canonical/dde/same.pdf", "sqlite"),
    ]

    merged = ranked_merge(rows, {"/legacy/dde": "/canonical/dde"}, limit=10)

    assert len(merged) == 1
    assert merged[0].canonical_path == "/canonical/dde/same.pdf"
    assert merged[0].meta["also_in"] == ["sqlite"]


def test_merge_normalizes_scores_per_index():
    rows = [
        _row("/a/all-tokens.pdf", "jsonl", matched=2, total=2),
        _row("/b/singleton.pdf", "sqlite", basis="fts_bm25", raw_score=12.0),
    ]

    merged = ranked_merge(rows, {}, limit=10)

    assert all(0.0 <= row.score <= 1.0 for row in merged)
    assert merged[0].canonical_path == "/a/all-tokens.pdf"


def test_normalize_dev_secondary_alias():
    assert (
        canonicalize_path(
            "/mnt/remote/dev-secondary/dde/Literature/x.pdf",  # abs-path-allowed
            {"/mnt/remote/dev-secondary/dde": "/mnt/dde"},  # abs-path-allowed
        )
        == "/mnt/dde/Literature/x.pdf"  # abs-path-allowed
    )


def test_normalize_ace_linux2_alias():
    assert (
        canonicalize_path(
            "/mnt/remote/ace-linux-2/dde/documents/y.xlsx",  # abs-path-allowed
            {"/mnt/remote/ace-linux-2/dde": "/mnt/dde"},  # abs-path-allowed
        )
        == "/mnt/dde/documents/y.xlsx"  # abs-path-allowed
    )


def test_normalize_longest_prefix_and_noop():
    aliases = {
        "/mnt/remote/ace-linux-2/dde": "/mnt/dde",  # abs-path-allowed
    }

    assert canonicalize_path("/mnt/ace/docs/a.pdf", aliases) == "/mnt/ace/docs/a.pdf"  # abs-path-allowed
    assert (
        canonicalize_path("/mnt/remote/ace-linux-2/dde-extra/z", aliases)  # abs-path-allowed
        == "/mnt/remote/ace-linux-2/dde-extra/z"  # abs-path-allowed
    )
    assert canonicalize_path("/mnt/remote/ace-linux-2/dde/z", aliases) == "/mnt/dde/z"  # abs-path-allowed
