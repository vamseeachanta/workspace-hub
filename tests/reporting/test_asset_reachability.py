"""Synthetic reachability examples with independently enumerated set oracles.

Contract proposed by these cases: inventory I = {live.svg, old.svg, saved.svg,
spare.svg}; current C = {live.svg}; history H = {old.svg}; recovery R =
{saved.svg}. By hand, I intersect (C union H union R) is {live.svg, old.svg,
saved.svg}, and I minus that union is exactly {spare.svg}. No production
result constructs an expected set. All fixture writes stay in tmp_path.
"""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from asset_reachability import main, plan_reachability


INVENTORY = ["assets/live.svg", "assets/old.svg", "assets/saved.svg", "assets/spare.svg"]
# tests/reporting and scripts/reporting are both two directories below root.
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/reporting/asset_reachability.py"


def write_json(root, name, value):
    (root / name).write_text(json.dumps(value), encoding="utf-8")


def snapshot(root):
    """Compare bytes, entries, link targets and stable caller metadata.

    Access times are filesystem-managed observations, excluded from this oracle.
    Mode, modification/change times, inode, size and link count must be preserved.
    """
    result = {}
    for path in [root, *sorted(root.rglob("*"))]:
        metadata = path.lstat()
        content = (os.readlink(path) if path.is_symlink() else
                   path.read_bytes() if path.is_file() else None)
        result[str(path.relative_to(root))] = (
            content, metadata.st_mode, metadata.st_mtime_ns, metadata.st_ctime_ns,
            metadata.st_ino, metadata.st_size, metadata.st_nlink,
        )
    return result


@pytest.fixture
def inputs(tmp_path):
    tmp_path = tmp_path / "root"
    tmp_path.mkdir()
    (tmp_path / "assets").mkdir()
    for name in INVENTORY:
        (tmp_path / name).write_bytes(name.encode())
    write_json(tmp_path, "inventory.json", {"schema": "asset-inventory-v1", "assets": INVENTORY})
    write_json(tmp_path, "current.json", {
        "schema": "asset-references-v1", "assets": ["assets/live.svg"],
    })
    write_json(tmp_path, "history.json", {
        "schema": "asset-references-v1", "assets": ["assets/old.svg"],
    })
    write_json(tmp_path, "recovery.json", {
        "schema": "asset-references-v1", "assets": ["assets/saved.svg"],
    })
    write_json(tmp_path, "index.json", {
        "schema": "asset-reference-index-v1", "publication_status": "succeeded",
        "current": ["current.json"], "history": ["history.json"],
        "recovery": ["recovery.json"],
    })
    return tmp_path


def run_plan(root):
    before = snapshot(root)
    result = plan_reachability(root, "inventory.json", "index.json")
    assert snapshot(root) == before
    return result


def unresolved(root):
    result = run_plan(root)
    assert result["status"] == "UNRESOLVED"
    assert result["dry_run"] is True
    assert result["referenced"] == []
    assert result["unreferenced"] == []
    assert result["prune_candidates"] == []
    assert result["reason"]
    return result


def test_unreferenced_partition_is_exact(inputs):
    result = run_plan(inputs)
    assert result == {
        "status": "RESOLVED", "dry_run": True,
        "referenced": ["assets/live.svg", "assets/old.svg", "assets/saved.svg"],
        "unreferenced": ["assets/spare.svg"], "prune_candidates": ["assets/spare.svg"],
    }
    # Independent set identity: the two partitions are disjoint and cover I.
    assert set(result["referenced"]).isdisjoint(result["unreferenced"])
    assert set(result["referenced"]) | set(result["unreferenced"]) == set(INVENTORY)


def test_recovery_reference_retains_asset(inputs):
    result = run_plan(inputs)
    assert "assets/saved.svg" in result["referenced"]
    assert "assets/saved.svg" not in result["prune_candidates"]


def test_failed_publication_has_no_candidates(inputs):
    index = json.loads((inputs / "index.json").read_bytes())
    index["publication_status"] = "failed"
    write_json(inputs, "index.json", index)
    unresolved(inputs)


@pytest.mark.parametrize("group", ["current", "history", "recovery"])
@pytest.mark.parametrize("fault", ["missing", "malformed", "incomplete"])
def test_every_manifest_is_required(inputs, group, fault):
    path = inputs / f"{group}.json"
    if fault == "missing":
        # Point at an absent fixture; preserve every caller file.
        index = json.loads((inputs / "index.json").read_bytes())
        index[group] = ["absent.json"]
        write_json(inputs, "index.json", index)
    elif fault == "malformed":
        path.write_text('{"assets":', encoding="utf-8")
    else:
        write_json(inputs, path.name, {"schema": "asset-references-v1"})
    unresolved(inputs)


@pytest.mark.parametrize("field", ["schema", "publication_status", "current", "history", "recovery"])
def test_incomplete_index_is_unresolved(inputs, field):
    index = json.loads((inputs / "index.json").read_bytes())
    del index[field]
    write_json(inputs, "index.json", index)
    unresolved(inputs)


@pytest.mark.parametrize("value", [[], None, {}, "current.json"])
def test_current_state_must_be_explicit_and_nonempty(inputs, value):
    index = json.loads((inputs / "index.json").read_bytes())
    index["current"] = value
    write_json(inputs, "index.json", index)
    unresolved(inputs)


def test_explicit_empty_history_and_recovery_are_valid(inputs):
    index = json.loads((inputs / "index.json").read_bytes())
    index.update(history=[], recovery=[])
    write_json(inputs, "index.json", index)
    result = run_plan(inputs)
    # By hand: I minus {live.svg} = {old.svg, saved.svg, spare.svg}.
    assert result["referenced"] == ["assets/live.svg"]
    assert result["unreferenced"] == ["assets/old.svg", "assets/saved.svg", "assets/spare.svg"]


@pytest.mark.parametrize("document", ["inventory.json", "index.json", "recovery.json"])
@pytest.mark.parametrize("raw", ["null", "[]", '{"schema":NaN}', '{"assets":[],"assets":[]}'])
def test_invalid_or_ambiguous_json_is_unresolved(inputs, document, raw):
    (inputs / document).write_text(raw, encoding="utf-8")
    unresolved(inputs)


@pytest.mark.parametrize("document", ["inventory.json", "recovery.json"])
def test_duplicate_json_key_cannot_hide_references(inputs, document):
    schema = "asset-inventory-v1" if document == "inventory.json" else "asset-references-v1"
    # Ordinary JSON last-key-wins parsing would conceal the saved reference.
    raw = ('{"schema":' + json.dumps(schema)
           + ',"assets":["assets/saved.svg"],"assets":[]}')
    (inputs / document).write_text(raw, encoding="utf-8")
    unresolved(inputs)


def test_duplicate_json_key_cannot_hide_failed_publication(inputs):
    raw = (inputs / "index.json").read_text(encoding="utf-8")
    raw = raw.replace('"publication_status": "succeeded"',
                      '"publication_status":"failed","publication_status":"succeeded"')
    (inputs / "index.json").write_text(raw, encoding="utf-8")
    unresolved(inputs)


@pytest.mark.parametrize("document", ["inventory.json", "index.json", "recovery.json"])
@pytest.mark.parametrize("fault", ["unknown_schema", "unknown_field"])
def test_unknown_contract_cannot_be_treated_as_complete(inputs, document, fault):
    value = json.loads((inputs / document).read_bytes())
    if fault == "unknown_schema":
        value["schema"] = "unsupported"
    else:
        value["omitted_references"] = ["assets/spare.svg"]
    write_json(inputs, document, value)
    unresolved(inputs)


@pytest.mark.parametrize("value", [None, True, "pending", "failed"])
def test_only_explicit_success_allows_candidates(inputs, value):
    index = json.loads((inputs / "index.json").read_bytes())
    index["publication_status"] = value
    write_json(inputs, "index.json", index)
    unresolved(inputs)


@pytest.mark.parametrize("path", ["../outside.svg", "assets/../outside.svg", "./assets/live.svg",
                                 "assets//live.svg", "assets\\live.svg", "", ".", "bad\x00path",
                                 "assets/live.svg/", "drive:asset.svg", "bad\udfffpath"])
@pytest.mark.parametrize("document", ["inventory.json", "recovery.json", "index.json"])
def test_unsafe_paths_are_rejected(inputs, path, document):
    value = json.loads((inputs / document).read_bytes())
    value["recovery" if document == "index.json" else "assets"] = [path]
    write_json(inputs, document, value)
    unresolved(inputs)


def test_absolute_path_is_rejected_without_disclosure(inputs):
    absolute = str(inputs / "assets/live.svg")
    write_json(inputs, "recovery.json", {"schema": "asset-references-v1", "assets": [absolute]})
    assert absolute not in json.dumps(unresolved(inputs))


@pytest.mark.parametrize("target", ["assets/live.svg", "assets", "current.json", "inventory.json", "index.json"])
@pytest.mark.parametrize("external", [False, True])
def test_symlinks_in_any_component_are_rejected(inputs, tmp_path, target, external):
    # Rename fixture content only during setup; planner must preserve this tree.
    original = inputs / target
    saved = tmp_path / "saved-target" if external else original.with_name(original.name + ".saved")
    original.rename(saved)
    original.symlink_to(saved, target_is_directory=saved.is_dir())
    before_target = snapshot(saved)
    unresolved(inputs)
    assert snapshot(saved) == before_target


def test_symlinked_root_is_rejected(inputs, tmp_path):
    alias = tmp_path / "root-alias"
    alias.symlink_to(inputs, target_is_directory=True)
    result = plan_reachability(alias, "inventory.json", "index.json")
    assert result["status"] == "UNRESOLVED"
    assert result["prune_candidates"] == []


def test_symlinked_root_ancestor_is_rejected(inputs, tmp_path):
    alias = tmp_path / "parent-alias"
    alias.symlink_to(inputs.parent, target_is_directory=True)
    before = snapshot(inputs)
    result = plan_reachability(alias / inputs.name, "inventory.json", "index.json")
    assert result["status"] == "UNRESOLVED"
    assert result["prune_candidates"] == []
    assert snapshot(inputs) == before


def test_dangling_symlink_is_rejected(inputs):
    (inputs / "dangling.svg").symlink_to(inputs / "absent.svg")
    write_json(inputs, "inventory.json", {
        "schema": "asset-inventory-v1", "assets": ["dangling.svg"],
    })
    unresolved(inputs)


def test_fifo_is_rejected_without_opening(inputs):
    os.mkfifo(inputs / "pipe")
    write_json(inputs, "index.json", {
        "schema": "asset-reference-index-v1", "publication_status": "succeeded",
        "current": ["pipe"], "history": [], "recovery": [],
    })
    unresolved(inputs)


@pytest.mark.parametrize("document", ["inventory.json", "recovery.json"])
@pytest.mark.parametrize("assets", [["absent.svg"], ["assets"], None, "assets/live.svg", [None]])
def test_missing_nonfile_or_invalid_assets_are_unresolved(inputs, document, assets):
    schema = "asset-inventory-v1" if document == "inventory.json" else "asset-references-v1"
    write_json(inputs, document, {"schema": schema, "assets": assets})
    unresolved(inputs)


def test_reference_outside_inventory_is_unresolved(inputs):
    (inputs / "other.svg").write_bytes(b"synthetic")
    write_json(inputs, "recovery.json", {"schema": "asset-references-v1", "assets": ["other.svg"]})
    unresolved(inputs)


def test_inventory_duplicates_are_unresolved(inputs):
    write_json(inputs, "inventory.json", {"schema": "asset-inventory-v1", "assets": INVENTORY + INVENTORY})
    unresolved(inputs)


def test_duplicate_references_are_retained_once(inputs):
    write_json(inputs, "recovery.json", {
        "schema": "asset-references-v1", "assets": ["assets/saved.svg", "assets/saved.svg"],
    })
    assert run_plan(inputs)["referenced"] == ["assets/live.svg", "assets/old.svg", "assets/saved.svg"]


def test_empty_inventory_and_references_have_empty_partitions(inputs):
    for document, schema in [("inventory.json", "asset-inventory-v1"),
                             ("current.json", "asset-references-v1")]:
        write_json(inputs, document, {"schema": schema, "assets": []})
    index = json.loads((inputs / "index.json").read_bytes())
    index.update(history=[], recovery=[])
    write_json(inputs, "index.json", index)
    assert run_plan(inputs) == {
        "status": "RESOLVED", "dry_run": True,
        "referenced": [], "unreferenced": [], "prune_candidates": [],
    }


def test_json_output_is_deterministic(inputs, capsys):
    args = ["--root", str(inputs), "--inventory", "inventory.json", "--references", "index.json"]
    # POSIX shell convention: success exit status is zero.
    assert main(args) == 0
    first = capsys.readouterr().out
    inventory = copy.deepcopy(INVENTORY)
    inventory.reverse()
    write_json(inputs, "inventory.json", {"schema": "asset-inventory-v1", "assets": inventory})
    assert main(args) == 0
    assert capsys.readouterr().out == first
    assert first == json.dumps(json.loads(first), sort_keys=True, separators=(",", ":")) + "\n"


def test_cli_is_read_only_and_reports_unavailable_input(inputs):
    before = snapshot(inputs)
    command = [sys.executable, str(SCRIPT), "--root", str(inputs),
               "--inventory", "inventory.json", "--references", "index.json"]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    assert json.loads(completed.stdout)["prune_candidates"] == ["assets/spare.svg"]
    assert not completed.stderr
    assert snapshot(inputs) == before
    # Missing manifest exit is nonzero; no filesystem error/path is disclosed.
    failed = subprocess.run(command[:-1] + ["missing.json"], capture_output=True, text=True)
    assert failed.returncode != 0
    assert json.loads(failed.stdout)["prune_candidates"] == []
    assert str(inputs) not in failed.stdout + failed.stderr
    assert snapshot(inputs) == before


def test_no_apply_option_exists(inputs):
    before = snapshot(inputs)
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(inputs),
         "--inventory", "inventory.json", "--references", "index.json", "--apply"],
        capture_output=True, text=True,
    )
    assert completed.returncode != 0
    assert "unrecognized arguments: --apply" in completed.stderr
    assert snapshot(inputs) == before


@pytest.mark.parametrize("group", ["history", "recovery"])
@pytest.mark.parametrize("value", [None, {}, "recovery.json", [None]])
def test_retained_state_lists_cannot_be_implicit(inputs, group, value):
    index = json.loads((inputs / "index.json").read_bytes())
    index[group] = value
    write_json(inputs, "index.json", index)
    unresolved(inputs)


def test_multiple_overlapping_manifests_are_unioned(inputs):
    write_json(inputs, "additional.json", {
        "schema": "asset-references-v1", "assets": ["assets/live.svg", "assets/saved.svg"],
    })
    index = json.loads((inputs / "index.json").read_bytes())
    index["current"].append("additional.json")
    write_json(inputs, "index.json", index)
    # The new references are already in C union R: neither partition changes.
    result = run_plan(inputs)
    assert result["referenced"] == ["assets/live.svg", "assets/old.svg", "assets/saved.svg"]
    assert result["unreferenced"] == ["assets/spare.svg"]


def test_caller_directory_and_git_bindings_do_not_redirect_reads(inputs, tmp_path):
    caller = tmp_path / "caller"
    caller.mkdir()
    (caller / ".git").mkdir()
    (caller / ".git" / "config").write_bytes(b"synthetic metadata")
    (caller / "inventory.json").write_bytes(b"caller content")
    before = snapshot(caller), snapshot(inputs)
    env = dict(os.environ, GIT_DIR=str(caller / ".git"), GIT_WORK_TREE=str(caller),
               GIT_COMMON_DIR=str(caller / ".git"))
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(inputs),
         "--inventory", "inventory.json", "--references", "index.json"],
        cwd=caller, env=env, capture_output=True, text=True, check=True,
    )
    assert json.loads(completed.stdout)["prune_candidates"] == ["assets/spare.svg"]
    assert (snapshot(caller), snapshot(inputs)) == before
