"""Reporting evidence tests; counts are independent enumeration, not solver values.

The synthetic population has three distinct targets: one saved snapshot, one
queued receipt and one unreachable target. Hand count: snapshots = 1, receipts
= 1, targets = 3; neither a queue nor a saved file establishes adoption.
Source: engineering-reporting-conventions-proposed.html, section 10 (P6, 2026).
"""

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/reporting/audit_reporting_adoption.py"
SPEC = importlib.util.spec_from_file_location("reporting_adoption", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)
AS_OF = "2026-10-22T12:00:00Z"


@pytest.fixture
def bundle(tmp_path):
    standard = tmp_path / "standard.html"
    standard.write_text("Synthetic reporting convention\n", encoding="utf-8")
    digest = hashlib.sha256(standard.read_bytes()).hexdigest()
    receipt = {
        "target": "target-b",
        "status": "queued",
        "revision": "synthetic",
        "sha256": digest,
        "observed_at": "2026-10-22T10:00:00Z",
    }
    (tmp_path / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    manifest = {
        "standard": {
            "path": "standard.html", "revision": "synthetic", "sha256": digest,
        },
        "observed_at": "2026-10-22T11:00:00Z",
        "targets": [
            {"id": "target-a", "status": "saved", "artifact": "standard.html"},
            {"id": "target-b", "status": "queued", "receipt": "receipt.json"},
            {"id": "target-c", "status": "unreachable", "reason": "No access"},
        ],
    }
    return tmp_path, manifest


def run_bundle(bundle):
    root, manifest = bundle
    return audit.verify(manifest, root, AS_OF)


def test_hand_counted_evidence_is_not_adoption(bundle):
    result = run_bundle(bundle)
    assert result["counts"] == {"targets": 3, "snapshots_verified": 1, "receipts_verified": 1}
    assert result["ecosystem_adoption"] == "NOT_EVALUATED"
    assert result["targets"][1]["reported_status"] == "queued"
    assert result["targets"][1]["snapshot"] == "NOT_EVALUATED"
    assert all(t["adoption"] == "NOT_EVALUATED" for t in result["targets"])


@pytest.mark.parametrize("status", ["not inspected", "unreachable"])
def test_gaps_are_retained_with_reasons(bundle, status):
    root, manifest = bundle
    manifest["targets"] = [{"id": "target-a", "status": status, "reason": "Not accessible"}]
    assert audit.verify(manifest, root, AS_OF)["counts"]["snapshots_verified"] == 0
    del manifest["targets"][0]["reason"]
    with pytest.raises(ValueError, match="reason"):
        audit.verify(manifest, root, AS_OF)


@pytest.mark.parametrize("status", ["saved", "revision-verified", "adopted"])
def test_snapshot_required_for_storage_and_adoption_records(bundle, status):
    _, manifest = bundle
    manifest["targets"] = [{"id": "target-a", "status": status}]
    with pytest.raises(ValueError, match="artifact"):
        run_bundle(bundle)


@pytest.mark.parametrize("status", ["queued", "acknowledged", "adopted"])
def test_delivery_requires_a_receipt(bundle, status):
    _, manifest = bundle
    manifest["targets"] = [{"id": "target-a", "status": status, "artifact": "standard.html"}]
    with pytest.raises(ValueError, match="receipt"):
        run_bundle(bundle)


@pytest.mark.parametrize("field,value", [
    ("target", "target-other"), ("status", "adopted"),
    ("revision", "old"), ("sha256", "0" * 64),
    ("observed_at", "2026-10-23T10:00:00Z"),
])
def test_stale_or_mismatched_receipt_rejected(bundle, field, value):
    root, _ = bundle
    path = root / "receipt.json"
    receipt = json.loads(path.read_text())
    receipt[field] = value
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="receipt"):
        run_bundle(bundle)


def test_adopted_receipt_is_still_only_a_reported_claim(bundle):
    root, manifest = bundle
    target = manifest["targets"][1]
    target.update(status="adopted", artifact="standard.html")
    manifest["targets"] = [target]
    path = root / "receipt.json"
    receipt = json.loads(path.read_text())
    receipt["status"] = "adopted"
    path.write_text(json.dumps(receipt))
    result = audit.verify(manifest, root, AS_OF)
    assert result["targets"][0]["receipt"] == "VERIFIED"
    assert result["targets"][0]["adoption"] == "NOT_EVALUATED"


@pytest.mark.parametrize("field", ["path", "artifact", "receipt"])
def test_paths_cannot_escape_evidence_root(bundle, field):
    root, manifest = bundle
    if field == "path":
        manifest["standard"][field] = "../outside"
    else:
        manifest["targets"][1][field] = "../outside"
    with pytest.raises(ValueError, match="path"):
        audit.verify(manifest, root, AS_OF)


def test_symlink_escape_rejected(bundle):
    root, manifest = bundle
    (root / "escape").symlink_to(root.parent, target_is_directory=True)
    manifest["standard"]["path"] = "escape/outside"
    with pytest.raises(ValueError, match="path"):
        run_bundle(bundle)


@pytest.mark.parametrize("value", ["/absolute", "C:\\outside", "", ".", "a/../standard.html"])
def test_nonportable_paths_rejected(bundle, value):
    _, manifest = bundle
    manifest["standard"]["path"] = value
    with pytest.raises(ValueError, match="path"):
        run_bundle(bundle)


@pytest.mark.parametrize("mutation", ["empty", "duplicate", "unknown-status", "unknown-key", "bad-digest"])
def test_malformed_inventory_rejected(bundle, mutation):
    _, manifest = bundle
    if mutation == "empty":
        manifest["targets"] = []
    elif mutation == "duplicate":
        manifest["targets"].append(copy.deepcopy(manifest["targets"][0]))
    elif mutation == "unknown-status":
        manifest["targets"][0]["status"] = "installed"
    elif mutation == "unknown-key":
        manifest["targets"][0]["typo"] = "value"
    else:
        manifest["standard"]["sha256"] = "not-a-digest"
    with pytest.raises(ValueError):
        run_bundle(bundle)


@pytest.mark.parametrize("date", ["invalid", "2026-10-22", "2026-10-23T00:00:00Z"])
def test_invalid_or_future_observation_rejected(bundle, date):
    _, manifest = bundle
    manifest["observed_at"] = date
    with pytest.raises(ValueError, match="observed_at"):
        run_bundle(bundle)


def test_equal_instants_with_timezone_offsets(bundle):
    _, manifest = bundle
    manifest["observed_at"] = "2026-10-22T06:00:00-05:00"
    assert run_bundle(bundle)["counts"]["receipts_verified"] == 1


def test_changed_snapshot_rejected(bundle):
    root, manifest = bundle
    (root / "copy.html").write_text("Different revision")
    manifest["targets"][0]["artifact"] = "copy.html"
    with pytest.raises(ValueError, match="digest"):
        run_bundle(bundle)


def test_changed_standard_rejected(bundle):
    root, _ = bundle
    (root / "standard.html").write_text("Changed source")
    with pytest.raises(ValueError, match="digest"):
        run_bundle(bundle)


def test_duplicate_json_keys_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        audit.parse_json('{"targets": [], "targets": []}')


def test_nonfinite_json_rejected():
    with pytest.raises(ValueError):
        audit.parse_json('{"value": NaN}')


def test_checked_in_example_matches_hand_count():
    path = ROOT / "examples/reporting/adoption/manifest.json"
    result = audit.verify(audit.parse_json(path.read_text()), ROOT, AS_OF)
    assert result["counts"] == {"targets": 3, "snapshots_verified": 1, "receipts_verified": 1}
    assert result["ecosystem_adoption"] == "NOT_EVALUATED"


def test_cli_works_outside_repository_and_does_not_modify_inputs(bundle):
    root, manifest = bundle
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest))
    before = {p.name: p.read_bytes() for p in root.iterdir()}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--root", str(root), "--as-of", AS_OF],
        cwd=root.parent, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["counts"]["targets"] == 3
    assert before == {p.name: p.read_bytes() for p in root.iterdir()}


def test_cli_errors_do_not_echo_input_or_local_paths(bundle):
    root, manifest = bundle
    manifest["standard"]["path"] = "missing-private-locator"
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--root", str(root), "--as-of", AS_OF],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "missing-private-locator" not in result.stderr
    assert str(root) not in result.stderr


@pytest.mark.parametrize("value", [None, [], "sensitive-untrusted-input", 1])
def test_nonobject_manifest_is_rejected_without_echoing_value(tmp_path, value):
    with pytest.raises(TypeError, match="manifest: expected object") as error:
        audit.verify(value, tmp_path, AS_OF)
    assert "sensitive-untrusted-input" not in str(error.value)


@pytest.mark.parametrize("field,value", [
    ("targets", "not-an-array"), ("observed_at", None), ("standard", []),
])
def test_wrong_field_types_fail_closed(bundle, field, value):
    _, manifest = bundle
    manifest[field] = value
    with pytest.raises((TypeError, ValueError)):
        run_bundle(bundle)


def test_revision_verified_is_a_byte_check_only(bundle):
    _, manifest = bundle
    manifest["targets"] = [manifest["targets"][0]]
    manifest["targets"][0]["status"] = "revision-verified"
    target = run_bundle(bundle)["targets"][0]
    assert target["snapshot"] == "VERIFIED"
    assert target["receipt"] == target["adoption"] == "NOT_EVALUATED"


def test_acknowledgement_does_not_require_an_installed_snapshot(bundle):
    root, manifest = bundle
    manifest["targets"] = [manifest["targets"][1]]
    manifest["targets"][0]["status"] = "acknowledged"
    path = root / "receipt.json"
    receipt = json.loads(path.read_text())
    receipt["status"] = "acknowledged"
    path.write_text(json.dumps(receipt))
    target = run_bundle(bundle)["targets"][0]
    assert target["receipt"] == "VERIFIED"
    assert target["snapshot"] == target["adoption"] == "NOT_EVALUATED"


@pytest.mark.parametrize("mutation", ["alias", "gap-artifact", "storage-receipt", "bad-json", "missing-file"])
def test_invalid_optional_evidence_rejected(bundle, mutation):
    root, manifest = bundle
    if mutation == "alias":
        manifest["targets"][0]["id"] = "untrusted-identity"
    elif mutation == "gap-artifact":
        manifest["targets"][2]["artifact"] = "standard.html"
    elif mutation == "storage-receipt":
        manifest["targets"][0]["receipt"] = "receipt.json"
    elif mutation == "bad-json":
        (root / "receipt.json").write_text("not JSON")
    else:
        manifest["targets"][1]["receipt"] = "missing.json"
    with pytest.raises(ValueError):
        run_bundle(bundle)


def test_snapshot_hashes_exact_bytes_including_line_endings(bundle):
    """One newline becomes CRLF; exact-byte digests must differ by definition."""
    root, manifest = bundle
    content = (root / "standard.html").read_bytes().replace(b"\n", b"\r\n")
    (root / "copy.html").write_bytes(content)
    manifest["targets"][0]["artifact"] = "copy.html"
    with pytest.raises(ValueError, match="digest"):
        run_bundle(bundle)


def test_example_html_links_and_contract_anchors_resolve():
    from html.parser import HTMLParser

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self.ids = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if "id" in attrs:
                self.ids.append(attrs["id"])
            if tag == "a" and "href" in attrs:
                self.links.append(attrs["href"])

    source = ROOT / "docs/reports/reporting-adoption-worked-example.html"
    parsed = Links()
    parsed.feed(source.read_text())
    assert len(parsed.ids) == len(set(parsed.ids))
    for href in parsed.links:
        file, _, anchor = href.partition("#")
        target = source.parent / file if file else source
        assert target.is_file()
        if anchor:
            linked = Links()
            linked.feed(target.read_text())
            assert anchor in linked.ids


def test_contract_relative_source_links_resolve():
    import re
    from html.parser import HTMLParser

    class Ids(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = set()

        def handle_starttag(self, tag, attrs):
            value = dict(attrs).get("id")
            if value:
                self.ids.add(value)

    source = ROOT / "docs/standards/reporting-adoption-evidence.md"
    for href in re.findall(r"\[[^\]]+\]\(([^)]+)\)", source.read_text()):
        file, _, anchor = href.partition("#")
        target = source.parent / file
        assert target.is_file()
        if anchor:
            parsed = Ids()
            parsed.feed(target.read_text())
            assert anchor in parsed.ids
