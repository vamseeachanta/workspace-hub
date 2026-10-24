"""Three-label hand calculation (synthetic hashes denote chosen byte classes).

Size 10, digest a: A/a, A/b, B/a => 3 files, (3-1)*10 = 20 bytes.
Size 4, digest b: C/a, C/b => 2 files, (2-1)*4 = 4 bytes.
Total: 2 groups, 5 files, 24 bytes. Across labels: 1 group, 3 files, 20
bytes. Within one label: 1 group, 2 files, 4 bytes. Per-label local
savings: A=10, B=0, C=4. Per-label totals overlap global categories.
"""

import json
import os

import pytest
from dedupe.merge_manifests import merge


def row(label, path, size=10, digest="a", sample="c"):
    return {
        "label": label,
        "root": 0,
        "path": path,
        "size": size,
        "mtime": 1,
        "stage": "full" if digest else ("sample" if sample else "size"),
        "sha256": digest * 64 if digest else None,
        "sample_sha256": sample * 64 if sample else None,
    }


def manifest(tmp_path, label, rows, complete=True, suffix=""):
    out = tmp_path / (label + suffix + ".jsonl")
    header = {
        "type": "manifest",
        "version": 1,
        "label": label,
        "complete": complete,
        "errors": [],
    }
    out.write_text(
        "\n".join(json.dumps(r) for r in [header, *rows]) + "\n",
        encoding="utf-8", newline="\n",
    )
    return out


def test_hand_computed_totals(tmp_path):
    inputs = [
        manifest(tmp_path, "A", [row("A", "a"), row("A", "b")]),
        manifest(tmp_path, "B", [row("B", "a")]),
        manifest(tmp_path, "C", [row("C", "a", 4, "b"), row("C", "b", 4, "b")]),
    ]
    result = merge(inputs)
    assert result["totals"]["verified"] == {
        "groups": 2,
        "files": 5,
        "bytes_reclaimable": 24,
    }
    assert result["totals"]["across_labels"] == {
        "groups": 1,
        "files": 3,
        "bytes_reclaimable": 20,
    }
    assert result["totals"]["within_label"] == {
        "groups": 1,
        "files": 2,
        "bytes_reclaimable": 4,
    }
    assert {
        label: values["bytes_reclaimable"]
        for label, values in result["totals"]["per_label"].items()
    } == {
        "A": 10,
        "B": 0,
        "C": 4,
    }
    assert len(result["across_labels"]) == len(result["within_label"]) == 1


def test_incomplete_entries_never_verified(tmp_path):
    inputs = [
        manifest(tmp_path, "A", [row("A", "a"), row("A", "b")], False),
        manifest(tmp_path, "B", [row("B", "a")]),
    ]
    result = merge(inputs)
    assert result["totals"]["verified"]["groups"] == 0
    assert len(result["candidate_groups"]) == 1
    assert result["candidate_groups"][0]["basis"] == "size_and_sample"
    assert all(g["status"] == "candidate" for g in result["candidate_groups"])


def test_size_only_candidates_and_sample_separation(tmp_path):
    inputs = [
        manifest(tmp_path, "A", [row("A", "a", digest=None, sample=None)]),
        manifest(tmp_path, "B", [row("B", "a", digest=None, sample=None)]),
    ]
    result = merge(inputs)
    assert len(result["candidate_groups"]) == 1
    assert result["candidate_groups"][0]["basis"] == "size"
    inputs = [
        manifest(tmp_path, "A", [row("A", "a", digest=None, sample="a")]),
        manifest(tmp_path, "B", [row("B", "a", digest=None, sample="b")]),
    ]
    assert merge(inputs)["candidate_groups"] == []


def test_complete_full_and_partial_evidence_separate(tmp_path):
    inputs = [
        manifest(tmp_path, "A", [row("A", "a"), row("A", "b")]),
        manifest(tmp_path, "B", [row("B", "a")], False),
    ]
    result = merge(inputs)
    assert result["totals"]["verified"]["files"] == 2
    assert len(result["candidate_groups"][0]["files"]) == 3


def test_same_manifest_twice_rejected(tmp_path):
    one = manifest(tmp_path, "A", [row("A", "a"), row("A", "b")])
    with pytest.raises(ValueError):
        merge([one, one])


def test_input_order_does_not_change_result(tmp_path):
    a = manifest(tmp_path, "A", [row("A", "a")])
    b = manifest(tmp_path, "B", [row("B", "a")])
    assert merge([a, b]) == merge([b, a])


@pytest.mark.parametrize(
    "patch",
    [
        {"path": "../escape"},
        {"path": "/absolute"},
        {"sha256": "bad"},
        {"size": -1},
        {"label": "B"},
        {"stage": "size"},
        {"root": -1},
        {"mtime": "unknown"},
        {"path": "bad\0name"},
    ],
)
def test_malformed_evidence_rejected(tmp_path, patch):
    entry = row("A", "a")
    entry.update(patch)
    path = manifest(tmp_path, "A", [entry])
    with pytest.raises(ValueError):
        merge([path])


def test_missing_header_rejected(tmp_path):
    path = tmp_path / "broken.jsonl"
    path.write_text(json.dumps(row("A", "a")) + "\n", encoding="utf-8", newline="\n")
    with pytest.raises(ValueError):
        merge([path])


def test_directory_scan_errors_preserved(tmp_path):
    path = manifest(tmp_path, "A", [], complete=False)
    header = json.loads(path.read_text(encoding="utf-8"))
    header["errors"] = [{"root": 0, "path": "private", "error": "PermissionError"}]
    path.write_text(json.dumps(header) + "\n", encoding="utf-8", newline="\n")
    result = merge([path])
    assert result["incomplete_labels"] == ["A"]
    assert result["scan_errors"] == [
        {"label": "A", "root": 0, "path": "private", "error": "PermissionError"},
    ]


@pytest.mark.skipif(os.name != "posix", reason="POSIX-only filename characters")
@pytest.mark.parametrize("name", ["report:copy", "report\\copy"])
def test_inventory_merge_filename_round_trip(tmp_path, name):
    from dedupe.dedupe_plan import make_plan
    from dedupe.hash_inventory import run

    root = tmp_path / "input"
    root.mkdir()
    (root / name).write_bytes(b"abc")
    (root / "ordinary").write_bytes(b"abc")
    output = tmp_path / "inventory.jsonl"
    rows, header = run({"roots": [str(root)]}, "A", output)
    assert header["complete"] is True
    result = merge([output])
    assert result["totals"]["verified"]["files"] == 2
    assert {r["path"] for r in rows} == {name, "ordinary"}
    plan = make_plan(result, {})
    item = plan["groups"][0]
    assert {item["keep"]["path"], item["candidates"][0]["path"]} == {
        name, "ordinary"
    }


def test_directory_reparse_points_are_not_scanned(tmp_path, monkeypatch):
    from dedupe import hash_inventory

    root = tmp_path / "input"
    root.mkdir()
    linked = root / "linked"
    linked.mkdir()
    (linked / "hidden").write_bytes(b"abc")
    linked_inode = linked.stat().st_ino
    monkeypatch.setattr(
        hash_inventory, "is_reparse_point", lambda info: info.st_ino == linked_inode,
        raising=False,
    )
    rows, header = hash_inventory.inventory({"roots": [str(root)]}, "A")
    assert header["complete"] is True
    assert rows == []
    with pytest.raises(ValueError):
        hash_inventory.inventory({"roots": [str(linked)]}, "A")


@pytest.mark.parametrize("attributes,expected", [(0, False), (1024, True), (1025, True)])
def test_reparse_attribute_detection(attributes, expected):
    from types import SimpleNamespace

    from dedupe._common import is_reparse_point

    # Windows FILE_ATTRIBUTE_REPARSE_POINT is 0x400; ordinary bits do not mask it.
    assert is_reparse_point(SimpleNamespace(st_file_attributes=attributes)) is expected
    assert is_reparse_point(SimpleNamespace()) is False


def test_output_alias_walk_prunes_reparse_directories(tmp_path, monkeypatch):
    from dedupe import _common

    root = tmp_path / "input"
    root.mkdir()
    linked = root / "linked"
    linked.mkdir()
    output = tmp_path / "output"
    output.write_bytes(b"abc")
    os.link(output, linked / "alias")
    linked_inode = linked.stat().st_ino
    monkeypatch.setattr(
        _common, "is_reparse_point", lambda info: info.st_ino == linked_inode
    )
    _common.distinct_outputs([output], roots=[root])


def test_atomic_text_output_has_utf8_and_lf(tmp_path):
    from dedupe._common import atomic_write_output

    output = tmp_path / "output"
    atomic_write_output(output, "caf\u00e9\nnext\n")
    assert output.read_bytes() == b"caf\xc3\xa9\nnext\n"
