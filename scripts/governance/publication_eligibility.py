"""Validate a reviewed JSON publication bundle without writing or publishing.

Policy: docs/architecture/agent-data-handling-contract.md, Original retention,
rights and publication; issue 3942. No engineering coefficients are used.
Approval is a trusted caller input, never inferred from a bundle field.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


class InvalidBundle(ValueError):
    """A structural failure, reported without private input details."""


def _require(condition, code):
    if not condition:
        raise InvalidBundle(code)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _sha(value):
    # Hexadecimal width: config/schemas/resource-descriptor-v1.schema.json,
    # $defs/projection/content_digest (descriptor v1).
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidBundle('duplicate_json_key')
        result[key] = value
    return result


def _nonfinite(_value):
    raise InvalidBundle('nonfinite_json')


def load_json(text):
    """Reject duplicate keys and non-finite JSON before evidence is lost."""
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_nonfinite)


def bundle_digest(bundle):
    """Pin all declarations and payloads, including decisions and staged hashes.

    Canonical JSON follows agent-data-handling-contract.md, Stable projection
    and shared conformance contract: UTF-8, sorted keys, compact separators.
    """
    content = json.dumps(bundle, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False).encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def _records(bundle):
    rows = bundle['records']
    _require(isinstance(rows, list), 'invalid_records')
    records = {}
    for row in rows:
        _require(isinstance(row, dict) and set(row) == {
            'id', 'dependencies', 'original_ids', 'payload'}, 'invalid_record')
        identity = row['id']
        _require(_text(identity) and identity not in records, 'duplicate_or_invalid_identity')
        for field in ('dependencies', 'original_ids'):
            values = row[field]
            _require(isinstance(values, list) and all(_text(v) for v in values)
                     and len(set(values)) == len(values), 'invalid_record_links')
        _require(isinstance(row['payload'], dict), 'invalid_payload')
        records[identity] = row
    return records


def _originals(bundle, records):
    originals = bundle['originals']
    _require(isinstance(originals, list), 'invalid_originals')
    identities = set()
    for original in originals:
        _require(isinstance(original, dict) and set(original) == {
            'id', 'retention', 'raw_sha256', 'archive_sha256', 'evidence_ref'},
            'invalid_original')
        identity = original['id']
        _require(_text(identity) and identity not in identities, 'invalid_original_identity')
        _require(original['retention'] == 'private_retained'
                 and _sha(original['raw_sha256']) and _sha(original['archive_sha256'])
                 and _text(original['evidence_ref']), 'original_retention_unverified')
        identities.add(identity)
    _require(all(set(row['original_ids']) <= identities for row in records.values()),
             'missing_original_retention')


def _decision_valid(decision):
    if not isinstance(decision, dict):
        return False
    required = {'decision', 'basis', 'reviewer', 'evidence_ref'}
    if not required <= set(decision) or set(decision) - required - {'permission_ref'}:
        return False
    if not all(_text(decision[field]) for field in required):
        return False
    status = decision['decision']
    return (status == 'eligible_factual_derivative'
            or status == 'permission_granted' and _text(decision.get('permission_ref')))


def _eligible(records, decisions):
    _require(isinstance(decisions, dict) and set(decisions) <= set(records),
             'invalid_decision_identities')
    pending = {key for key in records if _decision_valid(decisions.get(key))}
    eligible = set()
    # Least fixed point: ungrounded cycles cannot certify each other.
    # E(next) = E union {r with valid decision and dependencies subset E}.
    # Basis: issue 3942 transitive dependency deferral; no numerical tolerance.
    while pending:
        added = {key for key in pending if set(records[key]['dependencies']) <= eligible}
        if not added:
            break
        eligible.update(added)
        pending.difference_update(added)
    return eligible


def _relative_path(value):
    _require(_text(value) and '\\' not in value and ':' not in value
             and all(ord(c) >= 32 and ord(c) != 127 for c in value), 'invalid_stage_path')
    parts = value.split('/')
    _require(all(p not in ('', '.', '..') and p == p.rstrip(' .') for p in parts),
             'invalid_stage_path')
    return value


def _inventory(stage):
    _require(stage.is_dir() and not stage.is_symlink(), 'invalid_stage_directory')
    found = set()
    directories = [stage]
    while directories:
        for path in directories.pop().iterdir():
            _require(not path.is_symlink(), 'stage_symlink')
            _require(path.is_file() or path.is_dir(), 'stage_special_file')
            if path.is_dir():
                directories.append(path)
            else:
                found.add(path.relative_to(stage).as_posix())
    return found


def _export_file(stage, entry, records, eligible):
    _require(isinstance(entry, dict) and set(entry) == {
        'path', 'role', 'record_ids', 'sha256'}, 'invalid_stage_entry')
    relative = _relative_path(entry['path'])
    _require(entry['role'] == 'eligible_export', 'original_or_unknown_stage_role')
    identities = entry['record_ids']
    _require(isinstance(identities, list) and all(_text(v) for v in identities)
             and len(set(identities)) == len(identities), 'invalid_export_identities')
    _require(set(identities) <= eligible, 'deferred_export_dependency')
    content = (stage / relative).read_bytes()
    _require(_sha(entry['sha256']) and hashlib.sha256(content).hexdigest() == entry['sha256'],
             'staged_digest_mismatch')
    payload = load_json(content.decode('utf-8'))
    _require(isinstance(payload, dict) and set(payload) == {'records'}
             and isinstance(payload['records'], list), 'invalid_export_payload')
    # Canonical bytes distinguish true from 1, unlike Python object equality.
    expected = {'records': [records[key] for key in identities]}
    _require(bundle_digest(payload) == bundle_digest(expected), 'export_record_mismatch')
    return relative, set(identities)


def _stage(bundle, stage, records, eligible):
    entries = bundle['files']
    _require(isinstance(entries, list), 'invalid_stage_entries')
    found = _inventory(stage)
    declared, exported = set(), set()
    for entry in entries:
        relative, identities = _export_file(stage, entry, records, eligible)
        _require(relative not in declared and not identities & exported,
                 'duplicate_export')
        declared.add(relative)
        exported.update(identities)
    _require(found == declared, 'undeclared_stage_files')
    _require(bool(exported), 'empty_or_all_deferred_export')
    _require(exported == eligible, 'incomplete_eligible_export')
    return exported


def validate_bundle(bundle, stage_dir, approved_bundle_sha256, destination):
    """Return an aggregate receipt. This is validation, not publication authority.

    The caller authenticates the human approval of the exact bundle digest and
    supplies a frozen, exclusively owned stage. Retention and rights evidence
    must be independently checked; this function does not access private stores.
    Private identities, payloads, locators and exception messages are omitted.
    """
    counts = {'eligible': 0, 'deferred': 0, 'exported': 0}
    try:
        _require(isinstance(bundle, dict) and set(bundle) == {
            'records', 'decisions', 'originals', 'files', 'publication'}, 'invalid_bundle')
        _require(isinstance(bundle['publication'], dict)
                 and bundle['publication'] == {'destination': destination, 'audience': 'public'}
                 and _text(destination), 'publication_scope_mismatch')
        _require(_sha(approved_bundle_sha256)
                 and bundle_digest(bundle) == approved_bundle_sha256, 'review_digest_mismatch')
        records = _records(bundle)
        _originals(bundle, records)
        eligible = _eligible(records, bundle['decisions'])
        counts.update(eligible=len(eligible), deferred=len(records) - len(eligible))
        exported = _stage(bundle, Path(stage_dir), records, eligible)
        counts['exported'] = len(exported)
        return {'status': 'eligible', 'counts': counts, 'errors': []}
    except InvalidBundle as error:
        code = str(error)
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        code = 'unreadable_or_malformed_evidence'
    return {'status': 'blocked', 'counts': counts, 'errors': [code]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--stage', required=True, type=Path)
    parser.add_argument('--approved-bundle-sha256', required=True)
    parser.add_argument('--destination', required=True)
    args = parser.parse_args(argv)
    try:
        bundle = load_json(args.bundle.read_text(encoding='utf-8'))
    except (OSError, ValueError, RecursionError):
        bundle = None
    result = validate_bundle(bundle, args.stage, args.approved_bundle_sha256, args.destination)
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] == 'eligible' else 1


if __name__ == '__main__':
    raise SystemExit(main())
