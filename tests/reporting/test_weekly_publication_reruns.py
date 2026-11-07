"""Offline composition checks for weekly publication reruns (issue #2172).

Focused command (PyYAML is imported by the shared reporting conftest)::

    uv run --no-project --with pytest --with PyYAML python -m pytest \
        tests/reporting/test_weekly_publication_reruns.py -q -rA -p no:cacheprovider

Only local composition is exercised; no deployment service, clock or operational
records are used. Dates follow the synthetic weekly calendar example in
test_weekly_history.py: October 5 precedes October 12. Identifiers deliberately
sort in the opposite order. Cardinalities are hand-counted distinct identities:
one identity on a repeat, two identities after the second publication (#2172).

Rendered files are prepared in a sibling staging directory, outside retained.
Its names are transient preparation details, not publication deliverables.
Snapshots enumerate every retained file, including the manifest, without name
filters. The history writer manages its own temporary files; any leaked file
inside retained therefore fails the literal expected-file-set assertions.
"""

from copy import deepcopy
import hashlib
import json

import pytest

import bundle_manifest as bundle
import weekly_history as history
import weekly_renderer as renderer


# Independent synthetic inputs and expected history, not writer return values.
EARLY = {
    "run_id": "review-z",
    "published_at": "2026-10-05T12:00:00Z",
    "artifact": "runs/review-z/summary.html",
}
LATE = {
    "run_id": "review-a",
    "published_at": "2026-10-12T12:00:00Z",
    "artifact": "runs/review-a/summary.html",
}
EXPECTED_ORDER = [
    ("2026-10-05T12:00:00Z", "review-z"),
    ("2026-10-12T12:00:00Z", "review-a"),
]
EARLY_FILES = {
    "index.json",
    "latest.json",
    "manifest.json",
    "runs/review-z/summary.md",
    "runs/review-z/summary.html",
    "runs/review-z/evidence.json",
}
BOTH_FILES = EARLY_FILES | {
    "runs/review-a/summary.md",
    "runs/review-a/summary.html",
    "runs/review-a/evidence.json",
}


@pytest.fixture
def publications():
    """Fresh nested inputs make mutation assertions independent across tests."""
    return {
        name: {
            "history": deepcopy(record),
            "metadata": {"title": "Synthetic weekly review", "run_reference": name},
            "sections": [{
                "key": "ecosystem_health",
                "status": "ok",
                "summary": f"Synthetic {name} evidence",
                "items": [{"text": "Evidence", "artifact": "evidence.json"}],
            }],
            "evidence": {"status": "ok", "source": name},
        }
        for name, record in (("early", EARLY), ("late", LATE))
    }


def _publish(root, publication):
    """Compose real components; reject history conflicts before promoting files.

    This test-only ordering guarantees metadata-conflict preservation, not crash
    recovery or atomicity across history and rendered artifacts.
    """
    retained = root / "retained"
    retained.mkdir(parents=True, exist_ok=True)
    record = publication["history"]
    staged = root / "staging" / record["run_id"]
    staged.mkdir(parents=True, exist_ok=True)
    (staged / "summary.md").write_text(
        renderer.render_markdown(publication["metadata"], publication["sections"]),
        encoding="utf-8",
    )
    (staged / "summary.html").write_text(
        renderer.render_html(publication["metadata"], publication["sections"]),
        encoding="utf-8",
    )
    (staged / "evidence.json").write_text(
        json.dumps(publication["evidence"], sort_keys=True) + "\n", encoding="utf-8",
    )

    history.write_history(retained, **record)
    destination = retained / "runs" / record["run_id"]
    destination.mkdir(parents=True, exist_ok=True)
    for source in staged.iterdir():
        (destination / source.name).write_bytes(source.read_bytes())
    manifest = retained / "manifest.json"
    manifest.write_bytes(bundle.serialize_manifest(
        bundle.inventory(retained, exclude_output=manifest)
    ))


def _snapshot(root):
    """Read the complete retained file population independently of inventory."""
    retained = root / "retained"
    return {
        path.relative_to(retained).as_posix(): path.read_bytes()
        for path in retained.rglob("*") if path.is_file()
    }


def _assert_bundle(root, expected_records, expected_files):
    files = _snapshot(root)
    assert set(files) == expected_files
    entries = json.loads(files["index.json"])
    assert entries == expected_records
    # Independent cardinality: distinct supplied identities, never writer output.
    assert len(entries) == len({record["run_id"] for record in expected_records})
    assert json.loads(files["latest.json"]) == expected_records[-1]
    # The manifest cannot inventory itself; it is still included in snapshots.
    # Hash basis is the inventory protocol in bundle_manifest's module contract;
    # lengths are independent counts of the actual retained byte strings.
    expected_manifest = {
        "schema": "bundle-manifest-v1",
        "files": [
            {"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for path, data in sorted(files.items()) if path != "manifest.json"
        ],
    }
    assert json.loads(files["manifest.json"]) == expected_manifest
    assert bundle.inventory(
        root / "retained", exclude_output=root / "retained" / "manifest.json"
    ) == expected_manifest
    return files


def test_identical_composed_publication_is_byte_stable(tmp_path, publications):
    inputs_before = deepcopy(publications)
    _publish(tmp_path, publications["early"])
    before = _assert_bundle(tmp_path, [EARLY], EARLY_FILES)
    assert b"Run: early" in before["runs/review-z/summary.md"]
    assert b"<p>Run: early</p>" in before["runs/review-z/summary.html"]
    _publish(tmp_path, publications["early"])
    after = _assert_bundle(tmp_path, [EARLY], EARLY_FILES)
    assert after == before
    assert after["latest.json"] == before["latest.json"]
    assert publications == inputs_before


def test_out_of_order_composed_rerun_keeps_latest(tmp_path, publications):
    inputs_before = deepcopy(publications)
    _publish(tmp_path, publications["early"])
    _publish(tmp_path, publications["late"])
    before = _assert_bundle(tmp_path, [EARLY, LATE], BOTH_FILES)
    _publish(tmp_path, publications["early"])
    after = _assert_bundle(tmp_path, [EARLY, LATE], BOTH_FILES)
    assert [(row["published_at"], row["run_id"])
            for row in json.loads(after["index.json"])] == EXPECTED_ORDER
    assert json.loads(after["latest.json"]) == LATE
    assert after == before
    assert publications == inputs_before


def test_composed_call_order_has_same_final_tree(tmp_path, publications):
    inputs_before = deepcopy(publications)
    forward = tmp_path / "forward"
    reverse = tmp_path / "reverse"
    for root, order in (
        (forward, ("early", "late", "early")),
        (reverse, ("late", "early", "early")),
    ):
        for name in order:
            _publish(root, publications[name])
        files = _assert_bundle(root, [EARLY, LATE], BOTH_FILES)
        assert [(row["published_at"], row["run_id"])
                for row in json.loads(files["index.json"])] == EXPECTED_ORDER
    assert _snapshot(forward) == _snapshot(reverse)
    assert publications == inputs_before


def test_conflicting_rerun_preserves_entire_bundle(tmp_path, publications):
    inputs_before = deepcopy(publications)
    _publish(tmp_path, publications["early"])
    _publish(tmp_path, publications["late"])
    before = _assert_bundle(tmp_path, [EARLY, LATE], BOTH_FILES)
    retry = deepcopy(publications["early"])
    # Synthetic conflicting date, after October 5 but before October 12.
    retry["history"]["published_at"] = "2026-10-06T12:00:00Z"
    retry["metadata"]["title"] = "Conflicting retry"
    retry["sections"][0]["summary"] = "Conflicting evidence"
    retry["evidence"]["status"] = "error"
    retry_before = deepcopy(retry)
    with pytest.raises(ValueError, match="conflicting metadata for existing run_id"):
        _publish(tmp_path, retry)
    assert _assert_bundle(tmp_path, [EARLY, LATE], BOTH_FILES) == before
    assert retry == retry_before
    assert publications == inputs_before
