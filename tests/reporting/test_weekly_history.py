"""Synthetic boundary examples; expected order is calculated by hand.

The calendar examples order the first Monday before the second Monday, then
break equal publication times alphabetically by identifier. JSON expectations
are literals, independent of the writer. Numeric dates are synthetic fixtures.
"""

import json
import os
from pathlib import Path

import pytest

import weekly_history as history


EARLY = {
    "run_id": "review-a",
    "published_at": "2026-10-05T12:00:00Z",
    "artifact": "runs/review-a.json",
}
LATE = {
    "run_id": "review-b",
    "published_at": "2026-10-12T12:00:00Z",
    "artifact": "runs/review-b.json",
}


def snapshot(directory):
    return {p.name: p.read_bytes() for p in directory.iterdir()}


def test_bootstrap_and_append(tmp_path):
    directory = tmp_path / "history"
    assert history.write_history(directory, **EARLY) is True
    assert json.loads((directory / "index.json").read_text()) == [EARLY]
    assert json.loads((directory / "latest.json").read_text()) == EARLY
    assert history.write_history(directory, **LATE) is True
    assert json.loads((directory / "index.json").read_text()) == [EARLY, LATE]
    assert json.loads((directory / "latest.json").read_text()) == LATE
    assert set(snapshot(directory)) == {"index.json", "latest.json"}


def test_identical_rerun_is_noop(tmp_path, monkeypatch):
    history.write_history(tmp_path, **EARLY)
    history.write_history(tmp_path, **LATE)
    before = snapshot(tmp_path)

    def unexpected_replace(*args):
        pytest.fail("an identical rerun must not replace any file")

    monkeypatch.setattr(os, "replace", unexpected_replace)
    assert history.write_history(tmp_path, **EARLY) is False
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("changed", [
    {"published_at": "2026-10-06T12:00:00Z"},
    {"artifact": "runs/different.json"},
])
def test_conflicting_identifier_preserves_history(tmp_path, changed):
    history.write_history(tmp_path, **EARLY)
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match="conflicting"):
        history.write_history(tmp_path, **{**EARLY, **changed})
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("locator", [
    "../outside.json", "runs/../../outside.json", "/outside.json",
    "runs/../outside.json", "runs/./review.json", "runs//review.json",
    "runs/", "", ".", "..", "C:/outside.json", r"runs\review.json",
    "//example/review.json", "https://example.invalid/review.json",
    "%2e%2e/outside.json", "runs/review.json?raw=yes", "runs/review.json#part",
    "runs/\nreview.json", None,
])
def test_relative_locator_cannot_escape(tmp_path, locator):
    history.write_history(tmp_path, **EARLY)
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match="artifact"):
        history.write_history(tmp_path, **{**LATE, "artifact": locator})
    assert snapshot(tmp_path) == before


def test_relative_locator_rejects_symlink_escape(tmp_path):
    directory = tmp_path / "history"
    directory.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (directory / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="artifact"):
        history.write_history(directory, **{**EARLY, "artifact": "linked/review.json"})
    assert not (directory / "index.json").exists()
    assert not (directory / "latest.json").exists()


def test_latest_uses_time_not_call_order(tmp_path):
    # Later time wins even though the older identifier sorts after it.
    older = {**EARLY, "run_id": "review-z"}
    history.write_history(tmp_path, **LATE)
    history.write_history(tmp_path, **older)
    assert json.loads((tmp_path / "index.json").read_text()) == [older, LATE]
    assert json.loads((tmp_path / "latest.json").read_text()) == LATE


def test_equal_times_use_identifier_tie_breaking(tmp_path):
    first = {**EARLY, "run_id": "review-z"}
    second = {**EARLY, "run_id": "review-b"}
    history.write_history(tmp_path, **first)
    history.write_history(tmp_path, **second)
    assert json.loads((tmp_path / "index.json").read_text()) == [second, first]
    assert json.loads((tmp_path / "latest.json").read_text()) == first


@pytest.mark.parametrize("timestamp", [
    "2026-10-05", "2026-10-05T12:00:00", "2026-10-05T13:00:00+01:00",
    "2026-10-05T12:00:00-00:00", "2026-02-30T12:00:00Z",
    "2026-10-05T12:00:00.1234567Z", "2026-10-05 12:00:00Z", "", None,
])
def test_invalid_publication_time_preserves_outputs(tmp_path, timestamp):
    history.write_history(tmp_path, **EARLY)
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match="published_at"):
        history.write_history(tmp_path, **{**LATE, "published_at": timestamp})
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("run_id", ["", " ", "../review", "review/id", "review\n", None])
def test_invalid_identifier_does_not_bootstrap(tmp_path, run_id):
    directory = tmp_path / "history"
    with pytest.raises(ValueError, match="run_id"):
        history.write_history(directory, **{**EARLY, "run_id": run_id})
    assert not directory.exists()


def test_equivalent_utc_timestamp_is_an_identical_rerun(tmp_path):
    history.write_history(tmp_path, **EARLY)
    before = snapshot(tmp_path)
    assert history.write_history(
        tmp_path, **{**EARLY, "published_at": "2026-10-05T12:00:00.000000+00:00"}
    ) is False
    assert snapshot(tmp_path) == before


def test_fractional_times_are_sorted_as_instants(tmp_path):
    # Half a second follows the whole second, regardless of identifier order.
    fractional = {**EARLY, "run_id": "review-0", "published_at": "2026-10-05T12:00:00.5Z"}
    normalized = {**fractional, "published_at": "2026-10-05T12:00:00.500000Z"}
    history.write_history(tmp_path, **fractional)
    history.write_history(tmp_path, **EARLY)
    assert json.loads((tmp_path / "index.json").read_text()) == [EARLY, normalized]
    assert json.loads((tmp_path / "latest.json").read_text()) == normalized


@pytest.mark.parametrize("invalid_index", [
    "not json", "{}", "[null]", '[{"run_id": "review-a"}]',
    json.dumps([EARLY, EARLY]),
    json.dumps([{**EARLY, "artifact": "../outside.json"}]),
])
def test_invalid_existing_history_is_not_overwritten(tmp_path, invalid_index):
    (tmp_path / "index.json").write_text(invalid_index)
    (tmp_path / "latest.json").write_text("preserve this pointer\n")
    before = snapshot(tmp_path)
    with pytest.raises(ValueError):
        history.write_history(tmp_path, **LATE)
    assert snapshot(tmp_path) == before


def test_orphan_latest_is_not_overwritten(tmp_path):
    (tmp_path / "latest.json").write_text(json.dumps(EARLY))
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match="index"):
        history.write_history(tmp_path, **LATE)
    assert snapshot(tmp_path) == before


def test_prepares_both_files_before_replacing_either(tmp_path, monkeypatch):
    history.write_history(tmp_path, **EARLY)
    before = snapshot(tmp_path)
    real_dump = json.dump

    def fail_latest(value, stream, **kwargs):
        if isinstance(value, dict):
            raise OSError("synthetic staging failure")
        return real_dump(value, stream, **kwargs)

    monkeypatch.setattr(json, "dump", fail_latest)
    with pytest.raises(OSError, match="synthetic"):
        history.write_history(tmp_path, **LATE)
    assert snapshot(tmp_path) == before


def test_replacements_are_complete_and_latest_is_last(tmp_path, monkeypatch):
    history.write_history(tmp_path, **EARLY)
    replace = os.replace
    replaced = []

    def observe(source, target):
        # Parse complete staged bytes before each atomic replacement.
        value = json.loads(Path(source).read_text())
        assert Path(source).parent == tmp_path
        if Path(target).name == "index.json":
            assert value == [EARLY, LATE]
            assert json.loads((tmp_path / "latest.json").read_text()) == EARLY
        else:
            assert value == LATE
        replaced.append(Path(target).name)
        replace(source, target)

    monkeypatch.setattr(os, "replace", observe)
    history.write_history(tmp_path, **LATE)
    assert replaced == ["index.json", "latest.json"]


def test_duplicate_json_fields_are_rejected(tmp_path):
    (tmp_path / "index.json").write_text(
        '[{"run_id":"hidden","run_id":"review-a",'
        '"published_at":"2026-10-05T12:00:00Z","artifact":"runs/review-a.json"}]'
    )
    (tmp_path / "latest.json").write_text(json.dumps(EARLY))
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match="JSON"):
        history.write_history(tmp_path, **LATE)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("filename", ["index.json", "latest.json"])
def test_symlink_output_is_rejected(tmp_path, filename):
    directory = tmp_path / "history"
    directory.mkdir()
    target = tmp_path / "target.json"
    target.write_text("[]")
    (directory / filename).symlink_to(target)
    with pytest.raises(ValueError, match="symlinks"):
        history.write_history(directory, **EARLY)
    assert (directory / filename).is_symlink()
    assert target.read_text() == "[]"
    assert {p.name for p in directory.iterdir()} == {filename}


def test_failed_index_replacement_preserves_latest(tmp_path, monkeypatch):
    history.write_history(tmp_path, **EARLY)
    before = snapshot(tmp_path)

    def fail_replace(*args):
        raise OSError("synthetic replacement failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="synthetic"):
        history.write_history(tmp_path, **LATE)
    assert snapshot(tmp_path) == before


def test_call_order_does_not_change_serialized_outputs(tmp_path):
    forward = tmp_path / "forward"
    reverse = tmp_path / "reverse"
    history.write_history(forward, **EARLY)
    history.write_history(forward, **LATE)
    history.write_history(reverse, **LATE)
    history.write_history(reverse, **EARLY)
    assert snapshot(forward) == snapshot(reverse)
