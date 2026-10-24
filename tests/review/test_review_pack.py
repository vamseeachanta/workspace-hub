"""Review-pack contract tests; all engineering inputs below are synthetic.

Independent hand calculation: two support reactions of 4 N and 6 N balance
an applied 10 N load, so the expected reaction sum is 4 + 6 = 10 N.
The illustrative predeclared absolute tolerance is 0.5 N (test input, not a
design acceptance limit). Thus 10.5 N is on the boundary; 11 N is outside.
"""

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from review import review_pack as rp


@pytest.fixture
def pack():
    return json.loads((Path(__file__).parents[2] / "examples/review-pack/equilibrium.json")
                      .read_text(encoding="utf-8"))


def exported(pack, decision="accepted", note=""):
    return {"schema": "human-review-decisions/1", "pack_digest": rp.pack_digest(pack),
            "reviewer_ref": "review-record", "reviewed_at": "2026-10-22T12:00:00Z",
            "decisions": [{"card_id": "equilibrium", "decision": decision, "note": note}]}


def test_example_and_independent_boundary(pack):
    assert rp.check_verdict(pack["cards"][0]["checks"][0]) == "not_implausible"
    check = pack["cards"][0]["checks"][0]
    check["observed"] = 10.5
    assert rp.check_verdict(check) == "not_implausible"
    check["observed"] = 11
    assert rp.check_verdict(check) == "implausible"


@pytest.mark.parametrize("field,value", [
    ("comparator", "PASS"), ("observed", float("nan")), ("observed", True),
    ("observed", float("inf")), ("tolerance", -1), ("independent", "yes"),
    ("qualification", "unverified"),
])
def test_bad_check_schema(pack, field, value):
    pack["cards"][0]["checks"][0][field] = value
    with pytest.raises(ValueError):
        rp.validate_pack(pack)


@pytest.mark.parametrize("comparator", ["archived-run", "none"])
def test_regression_only_denies_acceptance(pack, comparator):
    pack["cards"][0]["checks"][0]["comparator"] = comparator
    result = rp.ingest_decisions(pack, exported(pack))
    assert not result["issuable"]
    assert result["cards"][0]["focus"] == "check flagged"


@pytest.mark.parametrize("mutation", ["missing", "late", "unqualified", "dependent"])
def test_absent_basis_is_not_evaluated(pack, mutation):
    check = pack["cards"][0]["checks"][0]
    if mutation == "missing":
        check["observed"] = None
    elif mutation == "late":
        check["fixed_at"] = "2026-10-22T10:00:01Z"
    elif mutation == "unqualified":
        check["qualification"] = "not_evaluated"
    else:
        check["independent"] = False
    result = rp.ingest_decisions(pack, exported(pack))
    assert result["cards"][0]["checks"][0]["verdict"] == "not_evaluated"
    assert not result["issuable"]


def test_schema_rejects_missing_fields_duplicate_ids_and_unknown_keys(pack):
    for mutate in [lambda p: p["cards"][0].pop("evidence"),
                   lambda p: p["cards"].append(copy.deepcopy(p["cards"][0])),
                   lambda p: p.update(acceptance="accepted")]:
        candidate = copy.deepcopy(pack)
        mutate(candidate)
        with pytest.raises(ValueError):
            rp.validate_pack(candidate)


def test_hosted_surface_requires_explicit_disclosure_review(pack):
    pack["surface"] = "hosted"
    with pytest.raises(ValueError, match="disclosure"):
        rp.render_pack(pack)
    pack["disclosure"] = {"status": "cleared", "reference": "publication-review"}
    assert "hosted" in rp.render_pack(pack)
    pack["cards"][0]["evidence"][0]["identifier_status"] = "present"
    with pytest.raises(ValueError, match="identifier"):
        rp.render_pack(pack)


def test_render_embeds_evidence_escapes_text_and_binds_export(pack):
    pack["cards"][0]["title"] = '</script><img src=x onerror="alert(1)">'
    page = rp.render_pack(pack)
    assert '<img src=x' not in page
    assert "&lt;/script&gt;" in page
    assert 'src="data:image/png;base64,' in page
    assert rp.pack_digest(pack) in page
    assert "localStorage" in page and "pack_digest" in page
    assert "Content-Security-Policy" in page
    assert "candidate" in page and "physical expectation" in page


def test_no_evidence_and_untrusted_active_images_refused(pack):
    for data in ["data:image/svg+xml;base64,PHN2Zz4=", "https://invalid.test/a.png",
                 "data:image/png;base64,bm90IGEgcG5n"]:
        pack["cards"][0]["evidence"][0]["data"] = data
        with pytest.raises(ValueError):
            rp.render_pack(pack)
    pack["cards"][0]["evidence"] = []
    with pytest.raises(ValueError):
        rp.validate_pack(pack)


def test_json_roundtrip_and_readback_lists_overrides_and_all_notes(pack):
    data = json.loads(json.dumps(exported(pack, "queried", "Inspect support reactions.")))
    record = rp.ingest_decisions(pack, data)
    assert record["differences"] == ["equilibrium"]
    assert record["instruction_notes"] == [
        {"card_id": "equilibrium", "note": "Inspect support reactions."}]
    assert not record["issuable"]
    assert rp.ingest_decisions(pack, exported(pack))["issuable"]


@pytest.mark.parametrize("mutation", ["stale", "duplicate", "unknown", "missing",
                                      "bad_enum", "missing_note", "future_pack"])
def test_reject_invalid_or_stale_decisions(pack, mutation):
    data = exported(pack)
    if mutation == "stale":
        pack["cards"][0]["checks"][0]["observed"] = 11
    elif mutation == "duplicate":
        data["decisions"] *= 2
    elif mutation == "unknown":
        data["decisions"][0]["card_id"] = "other"
    elif mutation == "missing":
        data["decisions"] = []
    elif mutation == "bad_enum":
        data["decisions"][0]["decision"] = "PASS"
    elif mutation == "missing_note":
        data["decisions"][0]["decision"] = "accepted_with_note"
    else:
        data["reviewed_at"] = "2026-10-22T09:00:00Z"
    with pytest.raises(ValueError):
        rp.ingest_decisions(pack, data)


def test_pending_rejected_and_flagged_results_never_issue(pack):
    for decision in ["pending", "queried", "rejected"]:
        assert not rp.ingest_decisions(pack, exported(pack, decision))["issuable"]
    pack["cards"][0]["checks"][0]["observed"] = 11
    assert not rp.ingest_decisions(pack, exported(pack))["issuable"]


def test_digest_is_key_order_independent_and_rejects_duplicate_json_keys(pack, tmp_path):
    assert rp.pack_digest(pack) == rp.pack_digest(dict(reversed(list(pack.items()))))
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema":"one","schema":"two"}', encoding="utf-8", newline="\n")
    with pytest.raises(ValueError, match="duplicate"):
        rp.load_json(path)


def test_cli_build_readback_and_gate(pack, tmp_path):
    script = Path(rp.__file__)
    source, decisions = tmp_path / "pack.json", tmp_path / "decisions.json"
    source.write_text(json.dumps(pack), encoding="utf-8", newline="\n")
    decisions.write_text(json.dumps(exported(pack)), encoding="utf-8", newline="\n")
    for args in [("build", str(source), str(tmp_path / "review.html")),
                 ("ingest", str(source), str(decisions), str(tmp_path / "record.json")),
                 ("gate", str(source), str(decisions))]:
        run = subprocess.run([sys.executable, str(script), *args],
                             check=False, capture_output=True, text=True, encoding="utf-8")
        assert run.returncode == 0, run.stderr
    decisions.write_text(json.dumps(exported(pack, "pending")), encoding="utf-8", newline="\n")
    run = subprocess.run([sys.executable, str(script), "gate", str(source), str(decisions)],
                         check=False, capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 2


@pytest.mark.parametrize("comparator", ["closed-form", "measured", "cross-solver", "conservation"])
def test_independent_comparator_classes(pack, comparator):
    pack["cards"][0]["checks"][0]["comparator"] = comparator
    assert rp.ingest_decisions(pack, exported(pack))["issuable"]


@pytest.mark.parametrize("field", ["expected", "tolerance"])
def test_unknown_basis_remains_explicit(pack, field):
    pack["cards"][0]["checks"][0][field] = None
    assert rp.ingest_decisions(pack, exported(pack))["cards"][0]["focus"] == "check flagged"


def test_no_value_focus_and_equal_timestamp_cannot_qualify(pack):
    check = pack["cards"][0]["checks"][0]
    check["observed"] = None
    assert rp.ingest_decisions(pack, exported(pack))["cards"][0]["focus"] == "no value"
    check["observed"] = 10
    check["fixed_at"] = check["run_started_at"]
    assert not rp.ingest_decisions(pack, exported(pack))["issuable"]


def test_offset_timestamps_are_compared_as_instants(pack):
    check = pack["cards"][0]["checks"][0]
    check["fixed_at"] = "2026-10-22T02:00:00-07:00"
    assert rp.ingest_decisions(pack, exported(pack))["issuable"]


def test_every_card_requires_a_decision_and_favourable_checks(pack):
    second = copy.deepcopy(pack["cards"][0])
    second["id"] = "second"
    pack["cards"].append(second)
    data = exported(pack)
    with pytest.raises(ValueError):
        rp.ingest_decisions(pack, data)
    data["decisions"].append({"card_id": "second", "decision": "pending", "note": ""})
    assert not rp.ingest_decisions(pack, data)["issuable"]
    data["decisions"][1]["decision"] = "accepted"
    assert rp.ingest_decisions(pack, data)["issuable"]
    second["checks"][0]["observed"] = 11
    data["pack_digest"] = rp.pack_digest(pack)
    assert not rp.ingest_decisions(pack, data)["issuable"]


@pytest.mark.parametrize("field", ["evidence", "criterion", "revision"])
def test_review_binding_includes_all_evidence_and_basis(pack, field):
    data = exported(pack)
    if field == "evidence":
        pack["cards"][0]["evidence"][0]["caption"] += " changed"
    elif field == "criterion":
        pack["cards"][0]["checks"][0]["tolerance"] = 1
    else:
        pack["revision"] = "changed"
    with pytest.raises(ValueError, match="revision"):
        rp.ingest_decisions(pack, data)


def test_render_script_hash_matches_csp(pack):
    import base64

    page = rp.render_pack(pack)
    script = re.search(r'<script>(.*?)</script>', page, re.DOTALL).group(1)
    digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    assert f"sha256-{digest}" in page


@pytest.mark.parametrize("storage_unavailable", [False, True])
def test_actual_page_javascript_exports_decisions_for_python_readback(pack, storage_unavailable):
    """Execute the emitted script with a small DOM double, without a browser.

    This tests the actual JSON contract across JavaScript and Python, including
    the fallback when local storage cannot be used. It does not test layout.
    """
    page = rp.render_pack(pack)
    script = re.search(r'<script>(.*?)</script>', page, re.DOTALL).group(1)
    data = re.search(r'<script id="pack-data" type="application/json">(.*?)</script>',
                     page, re.DOTALL).group(1)
    harness = r"""
const vm = require('node:vm');
let input = '';
process.stdin.on('data', c => input += c);
process.stdin.on('end', async () => {
  const payload = JSON.parse(input);
  const nodes = new Map();
  function element(id) {
    if (!nodes.has(id)) nodes.set(id, {value: '', textContent: '', events: {},
      addEventListener(name, fn) { this.events[name] = fn; }});
    return nodes.get(id);
  }
  element('pack-data').textContent = payload.data;
  const store = new Map();
  let blob;
  const context = {document: {getElementById: element,
    createElement: () => ({click() {}})},
    localStorage: {
      getItem: key => { if (payload.unavailable) throw Error('unavailable'); return store.get(key); },
      setItem: (key, value) => { if (payload.unavailable) throw Error('unavailable'); store.set(key, value); }
    },
    URL: {createObjectURL: value => { blob = value; return 'blob:synthetic'; },
      revokeObjectURL() {}}, Blob,
    Date: class {toISOString() {return '2026-10-22T12:00:00Z';}},
    setTimeout: fn => fn()};
  vm.runInNewContext(payload.script, context);
  element('reviewer').value = 'review-record';
  element('equilibrium-decision').value = 'accepted_with_note';
  element('equilibrium-note').value = 'Retain the reaction sum.';
  element('review').events.input();
  element('export').events.click();
  process.stdout.write(await blob.text());
});
"""
    run = subprocess.run(["node", "-e", harness],
                         input=json.dumps({"script": script, "data": data,
                                           "unavailable": storage_unavailable}),
                         check=False, capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 0, run.stderr
    record = rp.ingest_decisions(pack, json.loads(run.stdout))
    assert record["issuable"]
    assert record["differences"] == ["equilibrium"]
    assert record["instruction_notes"][0]["note"] == "Retain the reaction sum."


def test_cli_refuses_input_overwrite_and_preserves_input(pack, tmp_path):
    source = tmp_path / "pack.json"
    original = json.dumps(pack)
    source.write_text(original, encoding="utf-8", newline="\n")
    run = subprocess.run([sys.executable, rp.__file__, "build", str(source), str(source)],
                         check=False, capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 1
    assert source.read_text(encoding="utf-8") == original
    assert "Traceback" not in run.stderr


@pytest.mark.parametrize("field", ["fixed_at", "run_started_at", "reviewed_at"])
@pytest.mark.parametrize("timestamp", ["2026-10-22", "2026-10-22T10:00:00",
                                      "invalid", "2026-02-30T10:00:00Z"])
def test_invalid_timestamps_refused(pack, field, timestamp):
    data = exported(pack)
    if field == "reviewed_at":
        data[field] = timestamp
    else:
        pack["cards"][0]["checks"][0][field] = timestamp
        data = exported(pack)
    with pytest.raises(ValueError):
        rp.ingest_decisions(pack, data)


def test_missing_datetime_checker_refused(pack, monkeypatch):
    monkeypatch.delitem(rp.FormatChecker.checkers, "date-time", raising=False)
    with pytest.raises(ValueError, match="date-time"):
        rp.validate_pack(pack)


def test_large_mixed_numbers_preserve_independent_difference(pack):
    check = pack["cards"][0]["checks"][0]
    # Independent integer arithmetic: 10000000000000001 - 10000000000000000 = 1.
    check.update(expected=1e16, observed=10000000000000001, tolerance=0)
    record = rp.ingest_decisions(pack, exported(pack))
    assert record["cards"][0]["checks"][0]["verdict"] == "implausible"
    assert not record["issuable"]
    check["tolerance"] = 1
    assert rp.ingest_decisions(pack, exported(pack))["issuable"]


@pytest.mark.parametrize("image_format", ["PNG", "JPEG"])
@pytest.mark.parametrize("damage", ["signature", "truncated", "corrupt", "valid"])
def test_raster_structure_required(pack, image_format, damage):
    import base64
    from io import BytesIO

    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", (8, 8), "white").save(buffer, format=image_format)
    raw = buffer.getvalue()
    if damage == "signature":
        raw = (b"\x89PNG\r\n\x1a\n" if image_format == "PNG" else b"\xff\xd8\xff") + b"x"
    elif damage == "truncated":
        raw = raw[:-10]
    elif damage == "corrupt":
        raw = raw[:20] + bytes([raw[20] ^ 255]) + raw[21:]
    mime = "png" if image_format == "PNG" else "jpeg"
    pack["cards"][0]["evidence"][0]["data"] = (
        f"data:image/{mime};base64," + base64.b64encode(raw).decode("ascii"))
    if damage == "valid":
        assert rp.ingest_decisions(pack, exported(pack))["issuable"]
    else:
        with pytest.raises(ValueError):
            rp.ingest_decisions(pack, exported(pack))


@pytest.mark.parametrize("command,input_index", [("build", 0), ("ingest", 0), ("ingest", 1)])
def test_cli_refuses_hardlink_output(pack, tmp_path, command, input_index):
    source, decisions = tmp_path / "pack.json", tmp_path / "decisions.json"
    source.write_text(json.dumps(pack), encoding="utf-8", newline="\n")
    decisions.write_text(json.dumps(exported(pack)), encoding="utf-8", newline="\n")
    inputs = [source] if command == "build" else [source, decisions]
    originals = [path.read_bytes() for path in inputs]
    output = tmp_path / "output"
    output.hardlink_to(inputs[input_index])
    args = [command, *map(str, inputs), str(output)]
    run = subprocess.run([sys.executable, rp.__file__, *args],
                         check=False, capture_output=True, text=True, encoding="utf-8")
    assert run.returncode == 1
    assert [path.read_bytes() for path in inputs] == originals
    assert output.read_bytes() == originals[input_index]
    assert "Traceback" not in run.stderr
