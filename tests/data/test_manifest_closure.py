"""Closure examples derive expectations by enumeration, not validator output.

Basis: issue 3952 and docs/architecture/agent-data-handling-contract.md,
"Original retention, rights and publication" (repository revision at introduction).
Fixture arithmetic: two files, one original byte sequence and two records;
record keys {a, b} are unique and every parent value a belongs to {a, b}.
All counts below are synthetic enumerations, not engineering limits.
"""

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from data.manifest_closure import ClosureError, readback


def encoded(value):
    return json.dumps(value, sort_keys=True).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def bundle(tmp_path):
    raw = b"received original\n"
    rows = encoded([{"id": "a", "parent": "a"}, {"id": "b", "parent": "a"}])
    files = [
        {
            "id": "original",
            "role": "retained-original",
            "path": "raw/input.txt",
            "format": "bytes",
            "record_count": None,
            "primary_key": None,
        },
        {
            "id": "records",
            "role": "derived",
            "path": "rows.json",
            "format": "json-records",
            "record_count": 2,
            "primary_key": "id",
        },
    ]
    contract = {
        "version": "manifest-closure-contract/v1",
        "files": files,
        "foreign_keys": [
            {
                "from_file": "records",
                "field": "parent",
                "to_file": "records",
                "key": "id",
            }
        ],
    }
    manifest = {
        "version": "manifest-closure/v1",
        "files": [
            dict(files[0], sha256=digest(raw)),
            dict(files[1], sha256=digest(rows)),
        ],
    }
    (tmp_path / "raw").mkdir()
    (tmp_path / "raw/input.txt").write_bytes(raw)
    (tmp_path / "rows.json").write_bytes(rows)
    return tmp_path, contract, manifest


def accept(bundle, **kwargs):
    root, contract, manifest = bundle
    return readback(
        encoded(manifest),
        encoded(contract),
        contract_sha256=digest(encoded(contract)),
        manifest_sha256=digest(encoded(manifest)),
        root=root,
        view="working-tree",
        **kwargs,
    )


def test_complete_example_returns_verified_bytes_and_separate_receipt(bundle):
    result = accept(bundle)
    assert set(result.contents) == {"original", "records"}
    assert result.receipt["manifest_sha256"] == digest(encoded(bundle[2]))
    assert result.receipt["contract_sha256"] == digest(encoded(bundle[1]))
    assert result.receipt["version"] == "manifest-closure-receipt/v1"
    assert result.receipt["view"] == "working-tree"
    assert "manifest_sha256" not in bundle[2]
    with pytest.raises(TypeError):
        result.contents["original"] = b"replacement"


@pytest.mark.parametrize("identifier", ["original", "records"])
def test_manifest_pin_rejects_coordinated_payload_changes(
    bundle, monkeypatch, identifier
):
    root, contract, manifest = bundle
    pin = digest(encoded(manifest))
    entry = next(item for item in manifest["files"] if item["id"] == identifier)
    raw = (
        b"changed original"
        if identifier == "original"
        else encoded(
            [{"id": "a", "parent": "a", "value": 99}, {"id": "b", "parent": "a"}]
        )
    )
    (root / entry["path"]).write_bytes(raw)
    entry["sha256"] = digest(raw)

    def unexpected_read(*args):
        pytest.fail("payload read before manifest pin acceptance")

    monkeypatch.setattr("data.manifest_closure._read", unexpected_read)
    with pytest.raises(ClosureError, match="manifest digest mismatch"):
        readback(
            encoded(manifest),
            encoded(contract),
            contract_sha256=digest(encoded(contract)),
            manifest_sha256=pin,
            root=root,
            view="working-tree",
        )


def test_correct_independent_manifest_pin_passes(bundle):
    root, contract, manifest = bundle
    pin = digest(encoded(manifest))
    result = readback(
        encoded(manifest),
        encoded(contract),
        contract_sha256=digest(encoded(contract)),
        manifest_sha256=pin,
        root=root,
        view="working-tree",
    )
    assert result.receipt["integrity"] == "verified"
    assert result.receipt["manifest_sha256"] == pin
    assert result.contents["original"] == (root / "raw/input.txt").read_bytes()


def test_missing_manifest_pin_fails_closed(bundle):
    with pytest.raises(TypeError, match="manifest_sha256"):
        readback(
            encoded(bundle[2]),
            encoded(bundle[1]),
            contract_sha256=digest(encoded(bundle[1])),
            root=bundle[0],
            view="working-tree",
        )


@pytest.mark.parametrize("pin", [None, "", "bad", "0" * 64])
def test_invalid_manifest_pin_fails_before_payload_read(bundle, monkeypatch, pin):
    def unexpected_read(*args):
        pytest.fail("payload read before manifest pin acceptance")

    monkeypatch.setattr("data.manifest_closure._read", unexpected_read)
    with pytest.raises(ClosureError, match="manifest digest"):
        readback(
            encoded(bundle[2]),
            encoded(bundle[1]),
            contract_sha256=digest(encoded(bundle[1])),
            manifest_sha256=pin,
            root=bundle[0],
            view="working-tree",
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "omitted",
        "extra",
        "duplicate-id",
        "duplicate-path",
        "role",
        "redirect",
        "count",
        "digest",
        "format",
        "unknown-field",
        "contract-empty",
        "contract-duplicate",
        "contract-count-bool",
        "contract-count-negative",
        "contract-unknown",
        "manifest-version",
        "contract-version",
    ],
)
def test_inventory_and_shape_fail_closed(bundle, mutation):
    _, contract, manifest = bundle
    entry = manifest["files"][1]
    if mutation == "omitted":
        manifest["files"].pop()
    elif mutation == "extra":
        manifest["files"].append(dict(entry, id="extra"))
    elif mutation == "duplicate-id":
        entry["id"] = "original"
    elif mutation == "duplicate-path":
        entry["path"] = "raw/input.txt"
    elif mutation == "contract-empty":
        contract["files"] = []
    elif mutation == "contract-duplicate":
        contract["files"].append(copy.deepcopy(contract["files"][0]))
    elif mutation == "contract-count-bool":
        contract["files"][1]["record_count"] = True
    elif mutation == "contract-count-negative":
        contract["files"][1]["record_count"] = -1
    elif mutation == "contract-unknown":
        contract["ignored"] = True
    elif mutation.endswith("version"):
        (contract if mutation.startswith("contract") else manifest)["version"] = (
            "future"
        )
    else:
        field, value = {
            "role": ("role", "different"),
            "redirect": ("path", "uncounted.json"),
            "count": ("record_count", 1),
            "digest": ("sha256", "bad"),
            "format": ("format", "csv"),
            "unknown-field": ("unused", "value"),
        }[mutation]
        entry[field] = value
    with pytest.raises(ClosureError):
        accept(bundle)


@pytest.mark.parametrize(
    "path",
    [
        "../escape",
        "/absolute",
        "C:/outside",
        "raw/../rows.json",
        "raw//input.txt",
        "./rows.json",
        "raw\\input.txt",
        "",
    ],
)
def test_root_relative_paths_are_canonical(bundle, path):
    for document in bundle[1:]:
        document["files"][0]["path"] = path
    with pytest.raises(ClosureError):
        accept(bundle)


@pytest.mark.parametrize(
    "path", ["raw/input.txt.", "raw/input.txt ", "raw./input.txt", "raw /input.txt"]
)
def test_windows_trimmed_path_segments_are_rejected(bundle, path):
    root, contract, manifest = bundle
    payload = root / path
    if sys.platform == "win32":
        # Extended paths preserve the invalid segments for the validator to reject.
        payload = Path("\\\\?\\" + str(payload.absolute()))
    payload.parent.mkdir(exist_ok=True)
    payload.write_bytes((root / "raw/input.txt").read_bytes())
    for document in (contract, manifest):
        document["files"][0]["path"] = path
    with pytest.raises(ClosureError, match="canonical"):
        accept(bundle)


@pytest.mark.skipif(
    sys.platform == "win32", reason="the native parametrized cases cover win32"
)
def test_windows_alias_setup_preserves_segments(bundle, monkeypatch):
    """Exercise Windows path selection without requiring a Windows filesystem."""
    captured = []
    real_path = Path

    def capture_path(value):
        captured.append(value)
        return real_path(value.removeprefix("\\\\?\\"))

    with monkeypatch.context() as patch:
        patch.setattr(sys, "platform", "win32")
        patch.setattr(sys.modules[__name__], "Path", capture_path)
        test_windows_trimmed_path_segments_are_rejected(bundle, "raw /input.txt")
    assert captured == ["\\\\?\\" + str((bundle[0] / "raw /input.txt").absolute())]


@pytest.mark.parametrize(
    "rows",
    [
        [{"id": "a", "parent": "absent"}],
        [{"id": "a", "parent": "a"}, {"id": "a", "parent": "a"}],
        [{"id": "a"}, {"id": "b", "parent": "a"}],
        [{"id": None, "parent": "a"}, {"id": "b", "parent": "a"}],
        [{"id": True, "parent": "a"}, {"id": "b", "parent": "a"}],
        {"id": "a"},
    ],
)
def test_rehashed_invalid_semantics_are_rejected(bundle, rows):
    raw = encoded(rows)
    (bundle[0] / "rows.json").write_bytes(raw)
    bundle[2]["files"][1]["sha256"] = digest(raw)
    with pytest.raises(ClosureError):
        accept(bundle)


def test_rehashed_foreign_key_failure_with_correct_count(bundle):
    raw = encoded([{"id": "a", "parent": "missing"}, {"id": "b", "parent": "a"}])
    (bundle[0] / "rows.json").write_bytes(raw)
    bundle[2]["files"][1]["sha256"] = digest(raw)
    with pytest.raises(ClosureError, match="foreign key"):
        accept(bundle)


@pytest.mark.parametrize("document", ["manifest", "contract", "records"])
def test_duplicate_json_keys_rejected_at_every_level(bundle, document):
    root, contract, manifest = bundle
    raw_manifest, raw_contract = encoded(manifest), encoded(contract)
    if document == "records":
        raw = b'[{"id":"a","id":"b"}]'
        (root / "rows.json").write_bytes(raw)
        manifest["files"][1]["sha256"] = digest(raw)
        raw_manifest = encoded(manifest)
    elif document == "manifest":
        raw_manifest = raw_manifest.replace(b'"files":', b'"files":[],"files":', 1)
    else:
        raw_contract = raw_contract.replace(b'"files":', b'"files":[],"files":', 1)
    with pytest.raises(ClosureError, match="duplicate JSON key"):
        readback(
            raw_manifest,
            raw_contract,
            contract_sha256=digest(raw_contract),
            manifest_sha256=digest(raw_manifest),
            root=root,
            view="working-tree",
        )


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_json_rejected(bundle, value):
    raw = ('[{"id":"a","parent":"a","value":' + value + "}]").encode()
    (bundle[0] / "rows.json").write_bytes(raw)
    bundle[2]["files"][1]["sha256"] = digest(raw)
    with pytest.raises(ClosureError):
        accept(bundle)


def test_contract_pin_prevents_redeclared_omissions(bundle):
    pin = digest(encoded(bundle[1]))
    bundle[1]["files"].pop()
    bundle[2]["files"].pop()
    with pytest.raises(ClosureError, match="contract digest"):
        readback(
            encoded(bundle[2]),
            encoded(bundle[1]),
            contract_sha256=pin,
            manifest_sha256=digest(encoded(bundle[2])),
            root=bundle[0],
            view="working-tree",
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("from_file", "absent"),
        ("to_file", "original"),
        ("key", "unqualified"),
        ("field", ""),
    ],
)
def test_foreign_key_contract_is_closed(bundle, field, value):
    bundle[1]["foreign_keys"][0][field] = value
    with pytest.raises(ClosureError):
        accept(bundle)


def test_symlink_payload_is_rejected(bundle, tmp_path):
    target = tmp_path / "elsewhere.txt"
    target.write_bytes((bundle[0] / "raw/input.txt").read_bytes())
    (bundle[0] / "raw/input.txt").unlink()
    (bundle[0] / "raw/input.txt").symlink_to(target)
    with pytest.raises(ClosureError):
        accept(bundle)


def test_retained_and_fresh_views_do_not_inherit_working_tree_acceptance(
    bundle, tmp_path
):
    import shutil

    copy_root = tmp_path / "fresh"
    shutil.copytree(bundle[0] / "raw", copy_root / "raw")
    (copy_root / "rows.json").write_bytes((bundle[0] / "rows.json").read_bytes())
    result = readback(
        encoded(bundle[2]),
        encoded(bundle[1]),
        contract_sha256=digest(encoded(bundle[1])),
        manifest_sha256=digest(encoded(bundle[2])),
        root=copy_root,
        view="fresh-checkout",
    )
    assert result.receipt["view"] == "fresh-checkout"
    (copy_root / "raw/input.txt").write_bytes(b"tampered")
    accept(bundle)
    with pytest.raises(ClosureError, match="digest"):
        readback(
            encoded(bundle[2]),
            encoded(bundle[1]),
            contract_sha256=digest(encoded(bundle[1])),
            root=copy_root,
            manifest_sha256=digest(encoded(bundle[2])),
            view="retained-original",
        )


def test_optimization_cannot_disable_closure(bundle):
    """Omit one of two pinned entries: set difference is {records}, hence reject."""
    bundle[2]["files"].pop()
    root = bundle[0]
    (root / "contract.json").write_bytes(encoded(bundle[1]))
    (root / "manifest.json").write_bytes(encoded(bundle[2]))
    script = """
import sys
from pathlib import Path
from data.manifest_closure import ClosureError, readback
root = Path(sys.argv[1])
try:
    readback((root / "manifest.json").read_bytes(), (root / "contract.json").read_bytes(),
             contract_sha256=sys.argv[2], manifest_sha256=sys.argv[3],
             root=root, view="staged")
except ClosureError:
    sys.exit(0)
sys.exit(1)
"""
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}
    }
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "scripts")
    result = subprocess.run(
        [
            sys.executable,
            "-O",
            "-c",
            script,
            str(root),
            digest(encoded(bundle[1])),
            digest(encoded(bundle[2])),
        ],
        env=env,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()


def test_overflowing_json_number_rejected_even_after_rehash(bundle):
    raw = b'[{"id":"a","parent":"a","value":1e999},{"id":"b","parent":"a"}]'
    (bundle[0] / "rows.json").write_bytes(raw)
    bundle[2]["files"][1]["sha256"] = digest(raw)
    with pytest.raises(ClosureError):
        accept(bundle)


@pytest.mark.parametrize(
    "kind", ["missing", "directory", "changed-bytes", "parent-link"]
)
def test_invalid_payload_sources(bundle, kind):
    root = bundle[0]
    if kind == "parent-link":
        (root / "alias").symlink_to(root / "raw", target_is_directory=True)
        for document in bundle[1:]:
            document["files"][0]["path"] = "alias/input.txt"
    elif kind == "changed-bytes":
        (root / "raw/input.txt").write_bytes(b"changed")
    else:
        for document in bundle[1:]:
            document["files"][0]["path"] = "absent" if kind == "missing" else "raw"
    with pytest.raises(ClosureError):
        accept(bundle)


@pytest.mark.parametrize("raw", [b"[]", b"null", b"{}", b"not json", b"\xff"])
def test_malformed_document_has_controlled_failure(bundle, raw):
    with pytest.raises(ClosureError):
        readback(
            raw,
            encoded(bundle[1]),
            contract_sha256=digest(encoded(bundle[1])),
            manifest_sha256=digest(raw),
            root=bundle[0],
            view="working-tree",
        )


def test_all_four_views_must_read_their_own_bytes(bundle, tmp_path):
    """Four explicit materializations: one corruption must reject only that view."""
    import shutil

    receipts = []
    for view in ("working-tree", "staged", "fresh-checkout", "retained-original"):
        root = tmp_path / view
        shutil.copytree(bundle[0] / "raw", root / "raw")
        (root / "rows.json").write_bytes((bundle[0] / "rows.json").read_bytes())
        receipts.append(
            readback(
                encoded(bundle[2]),
                encoded(bundle[1]),
                contract_sha256=digest(encoded(bundle[1])),
                manifest_sha256=digest(encoded(bundle[2])),
                root=root,
                view=view,
            ).receipt
        )
    assert len({receipt["view"] for receipt in receipts}) == 4
    (tmp_path / "staged/raw/input.txt").write_bytes(b"changed staged bytes")
    with pytest.raises(ClosureError):
        readback(
            encoded(bundle[2]),
            encoded(bundle[1]),
            contract_sha256=digest(encoded(bundle[1])),
            root=tmp_path / "staged",
            manifest_sha256=digest(encoded(bundle[2])),
            view="staged",
        )
    accept(bundle)


def test_original_fixture_has_no_convertible_line_endings():
    """A newline-free synthetic original survives automatic checkout conversion."""
    example = Path(__file__).parents[1] / "fixtures/data/manifest_closure"
    assert (example / "raw/input.txt").read_bytes() == b"synthetic original"


def test_documented_example_and_cli_receipt(tmp_path):
    """Example has two files and keys a,b; both parent=a references resolve."""
    example = Path(__file__).parents[1] / "fixtures/data/manifest_closure"
    contract = (example / "contract.json").read_bytes()
    expected_pin = digest(contract)
    manifest_pin = digest((example / "manifest.json").read_bytes())
    documentation = (
        Path(__file__).parents[2] / "docs/architecture/manifest-closure.html"
    ).read_text(encoding="utf-8")
    literal = re.search(
        r"exact example contract pin is\s*<code>([0-9a-f]{64})</code>", documentation
    )
    assert literal is not None
    assert expected_pin == literal.group(1)
    assert f"--contract-sha256 {expected_pin}" in documentation
    assert f"--manifest-sha256 {manifest_pin}" in documentation
    assert b"\r" not in (example / "raw/input.txt").read_bytes()
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}
    }
    command = [
        sys.executable,
        "scripts/data/manifest_closure.py",
        "--root",
        str(example),
        "--manifest",
        str(example / "manifest.json"),
        "--contract",
        str(example / "contract.json"),
        "--contract-sha256",
        expected_pin,
        "--manifest-sha256",
        manifest_pin,
        "--view",
        "fresh-checkout",
    ]
    result = subprocess.run(command, capture_output=True, env=env, check=False)
    assert result.returncode == 0, result.stderr.decode()
    receipt = json.loads(result.stdout)
    assert receipt["file_count"] == 2
    assert receipt["authority"] == "not-established"
    assert receipt["manifest_sha256"] == digest(
        (example / "manifest.json").read_bytes()
    )
    command[command.index(expected_pin)] = digest(b"different contract")
    invalid = subprocess.run(command, capture_output=True, env=env, check=False)
    assert invalid.returncode != 0
    assert invalid.stdout == b""
    assert b"manifest closure failed" in invalid.stderr
    command[command.index(digest(b"different contract"))] = expected_pin
    command[command.index(manifest_pin)] = digest(b"different manifest")
    invalid_manifest = subprocess.run(
        command, capture_output=True, env=env, check=False
    )
    assert invalid_manifest.returncode != 0
    assert invalid_manifest.stdout == b""
    assert b"manifest closure failed" in invalid_manifest.stderr
    del command[
        command.index("--manifest-sha256") : command.index("--manifest-sha256") + 2
    ]
    missing_manifest = subprocess.run(
        command, capture_output=True, env=env, check=False
    )
    assert missing_manifest.returncode != 0
    assert missing_manifest.stdout == b""
    assert b"--manifest-sha256" in missing_manifest.stderr
