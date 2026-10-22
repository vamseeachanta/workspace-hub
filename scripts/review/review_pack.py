"""Build evidence cards, read back human decisions and check issue eligibility.

Requires jsonschema. The schema and the semantic checks together define v1.
This tool neither runs solvers nor authenticates reviewers or publication rights.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import html
import json
import math
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "config/schemas/human-review-pack-v1.schema.json"
INDEPENDENT = {"closed-form", "measured", "cross-solver", "conservation"}
ACCEPTING = {"accepted", "accepted_with_note"}
DECISIONS = ("pending", "accepted", "accepted_with_note", "queried", "rejected")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_json(path):
    """Refuse duplicate keys rather than silently discarding evidence."""
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite number")
    if isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, list):
        for item in value:
            _finite(item)


def _validate(value, export=False):
    _finite(value)
    schema = load_json(SCHEMA_PATH)
    if export:
        schema = {"$ref": "#/$defs/export", "$defs": schema["$defs"]}
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    except ValidationError as exc:
        # Do not echo potentially restricted input values in diagnostics.
        raise ValueError("schema violation at " + "/".join(map(str, exc.absolute_path))) from None


def _time(value):
    return datetime.fromisoformat(value.upper())


def _image(data):
    formats = {"data:image/png;base64,": b"\x89PNG\r\n\x1a\n",
               "data:image/jpeg;base64,": b"\xff\xd8\xff"}
    for prefix, signature in formats.items():
        if data.startswith(prefix):
            try:
                raw = base64.b64decode(data[len(prefix):], validate=True)
            except (ValueError, binascii.Error):
                break
            if raw.startswith(signature) and len(raw) > len(signature):
                return
    raise ValueError("evidence must be an embedded PNG or JPEG")


def validate_pack(pack):
    """Validate structure, unique identity and explicit hosted-surface review."""
    _validate(pack)
    ids = [card["id"] for card in pack["cards"]]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate card id")
    if pack["surface"] == "hosted":
        review = pack["disclosure"]
        if review["status"] != "cleared" or not review["reference"].strip():
            raise ValueError("hosted disclosure review is required")
    for card in pack["cards"]:
        for evidence in card["evidence"]:
            _image(evidence["data"])
            if pack["surface"] == "hosted" and evidence["identifier_status"] not in {
                "absent", "redacted"
            }:
                raise ValueError("hosted evidence identifier review is incomplete")
    return pack


def pack_digest(pack):
    """Bind decisions to all inputs, including image bytes and criteria."""
    raw = json.dumps(pack, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def check_verdict(check):
    """Absolute discrepancy <= caller-supplied, pre-run tolerance.

    Basis: reproducibility-is-not-correctness.md, clauses 1 and 4; no
    engineering coefficient or default acceptance limit is supplied here.
    """
    if (any(check[key] is None for key in ("observed", "expected", "tolerance"))
            or check["comparator"] not in INDEPENDENT or not check["independent"]
            or check["qualification"] != "qualified"
            or _time(check["fixed_at"]) >= _time(check["run_started_at"])):
        return "not_evaluated"
    return ("not_implausible" if abs(check["observed"] - check["expected"])
            <= check["tolerance"] else "implausible")


def _card_record(card):
    checks = [{**check, "verdict": check_verdict(check)} for check in card["checks"]]
    if all(check["observed"] is None for check in checks):
        focus = "no value"
    elif any(check["verdict"] != "not_implausible" for check in checks):
        focus = "check flagged"
    else:
        focus = "candidate"
    return {"id": card["id"], "focus": focus, "checks": checks}


def ingest_decisions(pack, exported):
    """Return a fresh job record; never mutate the adapter's inputs.

    Every nonempty note is flagged conservatively for instruction read-back.
    A digest and reviewer reference provide traceability, not authentication.
    """
    validate_pack(pack)
    _validate(exported, export=True)
    if exported["pack_digest"] != pack_digest(pack):
        raise ValueError("decisions refer to a different pack revision")
    decisions = exported["decisions"]
    ids = [item["card_id"] for item in decisions]
    if len(set(ids)) != len(ids) or set(ids) != {card["id"] for card in pack["cards"]}:
        raise ValueError("decisions must cover each card exactly once")
    by_id = {item["card_id"]: item for item in decisions}
    cards, differences, notes = [], [], []
    for card in pack["cards"]:
        choice = by_id[card["id"]]
        if choice["decision"] == "accepted_with_note" and not choice["note"].strip():
            raise ValueError("accepted_with_note requires a note")
        if any(_time(exported["reviewed_at"]) < _time(check["run_started_at"])
               for check in card["checks"]):
            raise ValueError("review predates the run")
        if choice["decision"] != card["recommendation"]:
            differences.append(card["id"])
        if choice["note"].strip():
            notes.append({"card_id": card["id"], "note": choice["note"]})
        cards.append({**_card_record(card), "acceptance": choice["decision"],
                      "note": choice["note"]})
    issuable = all(card["acceptance"] in ACCEPTING and card["focus"] == "candidate"
                   for card in cards)
    return {"schema": "human-review-record/1", "pack_digest": pack_digest(pack),
            "reviewer_ref": exported["reviewer_ref"], "reviewed_at": exported["reviewed_at"],
            "cards": cards, "differences": differences, "instruction_notes": notes,
            "issuable": issuable}


_SCRIPT = r"""
const pack = JSON.parse(document.getElementById('pack-data').textContent);
const key = 'human-review-pack:' + pack.pack_digest;
const form = document.getElementById('review');
const status = document.getElementById('status');
function capture() {
  return {schema: 'human-review-decisions/1', pack_digest: pack.pack_digest,
    reviewer_ref: document.getElementById('reviewer').value,
    reviewed_at: new Date().toISOString(),
    decisions: pack.ids.map(id => ({card_id: id,
      decision: document.getElementById(id + '-decision').value,
      note: document.getElementById(id + '-note').value}))};
}
function save() {
  try { localStorage.setItem(key, JSON.stringify(capture())); status.textContent = 'Saved locally'; }
  catch (_) { status.textContent = 'Local storage unavailable; export decisions to retain them'; }
}
try {
  const saved = JSON.parse(localStorage.getItem(key) || 'null');
  if (saved && saved.pack_digest === pack.pack_digest && Array.isArray(saved.decisions)) {
    document.getElementById('reviewer').value = saved.reviewer_ref || '';
    for (const item of saved.decisions) {
      if (pack.ids.includes(item.card_id) && pack.decisions.includes(item.decision)) {
        document.getElementById(item.card_id + '-decision').value = item.decision;
        document.getElementById(item.card_id + '-note').value = item.note || '';
      }
    }
  }
} catch (_) { status.textContent = 'Stored decisions unavailable'; }
form.addEventListener('input', save);
document.getElementById('export').addEventListener('click', () => {
  const result = capture();
  if (!result.reviewer_ref.trim()) { status.textContent = 'Enter a reviewer reference'; return; }
  save();
  const url = URL.createObjectURL(new Blob([JSON.stringify(result, null, 2)],
    {type: 'application/json'}));
  const link = document.createElement('a');
  link.href = url; link.download = 'review-decisions.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
"""


def render_pack(pack):
    """Render a self-contained page with no remote resources or active images."""
    validate_pack(pack)
    def esc(value):
        return html.escape(str(value), quote=True)
    digest = pack_digest(pack)
    script_hash = base64.b64encode(hashlib.sha256(_SCRIPT.encode()).digest()).decode()
    csp = ("default-src 'none'; img-src data:; style-src 'unsafe-inline'; "
           f"script-src 'sha256-{script_hash}'; base-uri 'none'; form-action 'none'")
    parts = [(f'<!doctype html><html lang="en"><meta charset="utf-8">'
             f'<meta http-equiv="Content-Security-Policy" content="{esc(csp)}">'
             f'<meta name="viewport" content="width=device-width">'
             f'<title>{esc(pack["title"])}</title>'),
             ('<style>body{font:1em system-ui;max-width:80em;margin:2em auto;padding:1em}'
             'article{border:1px solid;padding:1em;margin:1em 0}table{border-collapse:collapse}'
             'td,th{border:1px solid;padding:.5em;text-align:left}img{max-width:100%}'
             'textarea{display:block;width:95%}label{display:block;margin:.5em 0}'
             '</style><body>'),
             (f'<h1>{esc(pack["title"])}</h1><p>Surface: {esc(pack["surface"])}; '
             f'revision: {esc(pack["revision"])}</p><p>Pack digest: {digest}</p>'),
             ('<p>Human review required. A candidate is not acceptance. Inspect unaltered evidence, '
             'the physical expectation, method qualification and pre-run criterion. '
             'Notes are instructions for read-back; export decisions to the record.</p>'),
             ('<form id="review"><label>Reviewer record reference '
             '<input id="reviewer" required></label>')]
    for card in pack["cards"]:
        record = _card_record(card)
        parts.append(f'<article><h2>{esc(card["title"])}</h2>'
                     f'<p>Review focus: {record["focus"]}</p>'
                     f'<p>Recommendation: {esc(card["recommendation"])}; '
                     f'{esc(card["rationale"])}</p>')
        for evidence in card["evidence"]:
            parts.append(f'<figure><img src="{esc(evidence["data"])}" '
                         f'alt="{esc(evidence["caption"])}"><figcaption>'
                         f'{esc(evidence["caption"])} — {esc(evidence["source_ref"])}'
                         '</figcaption></figure>')
        parts.append('<table><thead><tr>' + ''.join(f'<th>{label}</th>' for label in
                     ('quantity', 'physical expectation', 'comparator class',
                      'tolerance fixed before the run', 'observed value', 'verdict'))
                     + '</tr></thead><tbody>')
        for check in record["checks"]:
            values = (f'{check["quantity"]} ({check["units"]})',
                      f'{check["expectation"]}; expected {check["expected"]}',
                      check["comparator"],
                      (f'{check["tolerance"]}; fixed {check["fixed_at"]}; '
                      f'run {check["run_started_at"]}; {check["criterion_source"]}'),
                      check["observed"], check["verdict"])
            parts.append('<tr>' + ''.join(f'<td>{esc(v)}</td>' for v in values) + '</tr>')
        parts.append('</tbody></table>')
        for check in record["checks"]:
            parts.append(f'<p>Governing case: {esc(check["governing_case"])}; '
                         f'independent: {esc(check["independent"])}; qualification: '
                         f'{esc(check["qualification"])}; {esc(check["qualification_ref"])}</p>')
        parts.append(f'<label>Decision <select id="{card["id"]}-decision">'
                     + ''.join(f'<option>{value}</option>' for value in DECISIONS)
                     + f'</select></label><label>Note <textarea id="{card["id"]}-note">'
                     '</textarea></label></article>')
    data = json.dumps({"pack_digest": digest, "ids": [c["id"] for c in pack["cards"]],
                       "decisions": DECISIONS}).replace('<', '\\u003c')
    parts.append('</form><button id="export" type="button">Export decisions</button>'
                 '<p id="status" role="status"></p>'
                 f'<script id="pack-data" type="application/json">{data}</script>'
                 f'<script>{_SCRIPT}</script></body></html>')
    return '\n'.join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "ingest", "gate"):
        child = sub.add_parser(command)
        child.add_argument("pack", type=Path)
        if command != "build":
            child.add_argument("decisions", type=Path)
        if command != "gate":
            child.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        inputs = [args.pack]
        if args.command != "build":
            inputs.append(args.decisions)
        if args.command != "gate" and args.output.resolve() in {p.resolve() for p in inputs}:
            raise ValueError("output may not overwrite an input")
        pack = load_json(args.pack)
        if args.command == "build":
            args.output.write_text(render_pack(pack), encoding="utf-8")
        else:
            record = ingest_decisions(pack, load_json(args.decisions))
            if args.command == "gate":
                print(json.dumps({"issuable": record["issuable"],
                                  "pack_digest": record["pack_digest"]}))
                return 0 if record["issuable"] else 2
            args.output.write_text(json.dumps(record, indent=2, allow_nan=False) + '\n',
                                   encoding="utf-8")
    except (ValueError, OSError, OverflowError):
        # Paths and payload values may be private; diagnostics remain categorical.
        print("Review pack refused: invalid input, evidence, decision or output", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
