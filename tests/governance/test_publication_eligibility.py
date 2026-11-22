"""Publication contract regressions for issue 3942.

Expected sets are hand-derived: source -> entity -> cost is a chain; removing
source removes all three, while independent has no dependencies and survives.
Counts are set cardinalities, not empirical engineering acceptance limits.
Policy basis: docs/architecture/agent-data-handling-contract.md, Original
retention, rights and publication; issue 3942 dependency-closure requirements.
"""
import copy
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/governance'))
import publication_eligibility as pe


def record(identity, dependencies=()):
    return {'id': identity, 'dependencies': list(dependencies),
            'original_ids': ['input'], 'payload': {'value': identity}}


def approved():
    return {'decision': 'eligible_factual_derivative', 'basis': 'public-reference',
            'reviewer': 'maintainer', 'evidence_ref': 'review-record'}


def fixture(tmp_path):
    records = [record('source'), record('entity', ['source']),
               record('cost', ['entity']), record('independent')]
    bundle = {'records': records, 'decisions': {r['id']: approved() for r in records},
              'originals': [{'id': 'input', 'retention': 'private_retained',
                             'raw_sha256': hashlib.sha256(b'original').hexdigest(),
                             'archive_sha256': hashlib.sha256(b'archive').hexdigest(),
                             'evidence_ref': 'retention-record'}], 'files': [], 'publication': {'destination': 'public-example', 'audience': 'public'}}
    stage = tmp_path / 'stage'
    stage.mkdir(parents=True)
    write_export(bundle, stage, records)
    return bundle, stage


def write_export(bundle, stage, records):
    # Independent public format: private original links never enter the stage.
    public = [{key: row[key] for key in ('id', 'dependencies', 'payload')}
              for row in records]
    content = json.dumps({'records': public}).encode()
    (stage / 'export.json').write_bytes(content)
    bundle['files'] = [{'path': 'export.json', 'role': 'eligible_export',
                        'record_ids': [r['id'] for r in records],
                        'sha256': hashlib.sha256(content).hexdigest()}]


def evaluate(bundle, stage, digest=None):
    return pe.validate_bundle(bundle, stage, digest or pe.bundle_digest(bundle), 'public-example')


def test_complete_export(tmp_path):
    bundle, stage = fixture(tmp_path)
    result = evaluate(bundle, stage)
    assert result['status'] == 'eligible'
    assert result['counts'] == {'eligible': 4, 'deferred': 0, 'exported': 4}
    assert result['errors'] == []


def test_source_deferral_cascades_through_parent(tmp_path):
    """D0={source}; D1 adds entity; D2 adds cost; independent survives."""
    bundle, stage = fixture(tmp_path)
    bundle['decisions']['source']['decision'] = 'unresolved'
    write_export(bundle, stage, [bundle['records'][-1]])
    result = evaluate(bundle, stage)
    assert result['status'] == 'eligible'
    assert result['counts'] == {'eligible': 1, 'deferred': 3, 'exported': 1}
    # Public receipt contains no private/deferred identity or evidence locator.
    assert 'source' not in json.dumps(result)
    assert 'retention-record' not in json.dumps(result)


def test_public_export_has_no_private_original_links(tmp_path):
    """Hand projection removes only original_ids; four records remain eligible."""
    bundle, stage = fixture(tmp_path)
    original = bundle['originals'][0]
    original['id'] = 'restricted-original-reference'
    for row in bundle['records']:
        row['original_ids'] = [original['id']]
    write_export(bundle, stage, bundle['records'])
    assert evaluate(bundle, stage)['status'] == 'eligible'
    assert original['id'] not in (stage / 'export.json').read_text()
    assert original['evidence_ref'] not in (stage / 'export.json').read_text()


def test_private_links_in_staged_rows_are_rejected(tmp_path):
    """Even reviewed bytes may not export the private provenance envelope."""
    bundle, stage = fixture(tmp_path)
    content = json.dumps({'records': bundle['records']}).encode()
    (stage / 'export.json').write_bytes(content)
    bundle['files'][0]['sha256'] = hashlib.sha256(content).hexdigest()
    result = evaluate(bundle, stage)
    assert result['errors'] == ['export_record_mismatch']


@pytest.mark.parametrize('field', ['raw_sha256', 'archive_sha256'])
def test_original_bytes_cannot_be_relabelled_as_export(tmp_path, field):
    """Equal hashes identify the same known retained bytes, regardless of role."""
    bundle, stage = fixture(tmp_path)
    bundle['originals'][0][field] = bundle['files'][0]['sha256']
    result = evaluate(bundle, stage)
    assert result['status'] == 'blocked'
    assert result['errors'] == ['retained_bytes_in_stage']


def test_relationship_and_inherited_parent_closure(tmp_path):
    """Hand closure: source defers entity, cost, relationship, inherited cost.

    Independent and its independently sourced child survive: E has two members,
    D has five. The relationship needs both an entity and an independent record;
    a valid second dependency cannot compensate for the deferred entity.
    """
    bundle, stage = fixture(tmp_path)
    bundle['records'].extend([
        record('relationship', ['entity', 'independent']),
        record('inherited', ['cost']), record('child', ['independent']),
    ])
    bundle['decisions'].update({key: approved() for key in
                                ('relationship', 'inherited', 'child')})
    bundle['decisions']['source']['decision'] = 'prohibited'
    write_export(bundle, stage, [bundle['records'][3], bundle['records'][-1]])
    assert evaluate(bundle, stage) == {
        'status': 'eligible', 'counts': {'eligible': 2, 'deferred': 5, 'exported': 2},
        'errors': [],
    }


def test_graph_order_does_not_change_closure(tmp_path):
    """Reverse topological order still has four eligible graph members."""
    bundle, stage = fixture(tmp_path)
    bundle['records'].reverse()
    write_export(bundle, stage, bundle['records'])
    assert evaluate(bundle, stage)['counts'] == {
        'eligible': 4, 'deferred': 0, 'exported': 4,
    }


def test_missing_dependency_defers_its_dependants(tmp_path):
    """Absent root defers source, entity and cost; independent alone survives."""
    bundle, stage = fixture(tmp_path)
    bundle['records'][0]['dependencies'] = ['absent']
    write_export(bundle, stage, [bundle['records'][-1]])
    assert evaluate(bundle, stage)['counts'] == {
        'eligible': 1, 'deferred': 3, 'exported': 1,
    }


def test_closure_across_export_files(tmp_path):
    """Two exports partition the four-node graph; cross-file links stay valid."""
    bundle, stage = fixture(tmp_path)
    first_entry = copy.deepcopy(bundle['files'][0])
    write_export(bundle, stage, bundle['records'][:2])
    (stage / 'export.json').rename(stage / 'parents.json')
    first_entry.update(bundle['files'][0], path='parents.json')
    write_export(bundle, stage, bundle['records'][2:])
    bundle['files'].append(first_entry)
    assert evaluate(bundle, stage)['status'] == 'eligible'
    # The known retained bytes match the second entry, so every file is checked.
    bundle['originals'][0]['archive_sha256'] = first_entry['sha256']
    assert evaluate(bundle, stage)['errors'] == ['retained_bytes_in_stage']


def test_deferred_record_in_stage_blocks(tmp_path):
    bundle, stage = fixture(tmp_path)
    del bundle['decisions']['source']
    assert evaluate(bundle, stage)['status'] == 'blocked'


def test_all_deferred_is_not_success(tmp_path):
    bundle, stage = fixture(tmp_path)
    bundle['decisions'] = {}
    write_export(bundle, stage, [])
    assert evaluate(bundle, stage)['status'] == 'blocked'


@pytest.mark.parametrize('mutation', ['missing', 'cycle', 'self'])
def test_unresolved_graph_blocks_export(tmp_path, mutation):
    bundle, stage = fixture(tmp_path)
    bundle['records'][0]['dependencies'] = {
        'missing': ['absent'], 'cycle': ['cost'], 'self': ['source']}[mutation]
    write_export(bundle, stage, bundle['records'])
    assert evaluate(bundle, stage)['status'] == 'blocked'


def test_changed_decisions_invalidate_review(tmp_path):
    bundle, stage = fixture(tmp_path)
    digest = pe.bundle_digest(bundle)
    bundle['decisions']['source']['basis'] = 'different-reference'
    assert evaluate(bundle, stage, digest)['status'] == 'blocked'


@pytest.mark.parametrize('field', ['basis', 'reviewer', 'evidence_ref'])
def test_missing_decision_evidence(tmp_path, field):
    bundle, stage = fixture(tmp_path)
    bundle['decisions']['source'][field] = ''
    assert evaluate(bundle, stage)['status'] == 'blocked'


def test_permission_requires_separate_evidence(tmp_path):
    bundle, stage = fixture(tmp_path)
    decision = bundle['decisions']['source']
    decision['decision'] = 'permission_granted'
    assert evaluate(bundle, stage)['status'] == 'blocked'
    decision['permission_ref'] = 'permission-record'
    assert evaluate(bundle, stage)['status'] == 'eligible'


@pytest.mark.parametrize('mutation', ['extra', 'original', 'tamper', 'payload', 'omitted'])
def test_staged_closure(tmp_path, mutation):
    bundle, stage = fixture(tmp_path)
    if mutation == 'extra':
        (stage / 'undeclared.json').write_text('{}')
    elif mutation == 'original':
        bundle['files'][0]['role'] = 'retained_original'
    elif mutation == 'tamper':
        (stage / 'export.json').write_text('{}')
    elif mutation == 'payload':
        altered = copy.deepcopy(bundle['records'])
        altered[0]['payload']['value'] = 'changed'
        write_export(bundle, stage, altered)
    else:
        write_export(bundle, stage, bundle['records'][:-1])
    assert evaluate(bundle, stage)['status'] == 'blocked'


@pytest.mark.parametrize('mutation', ['pending', 'archive_only', 'missing_original'])
def test_original_retention_is_separate(tmp_path, mutation):
    bundle, stage = fixture(tmp_path)
    if mutation == 'pending':
        bundle['originals'][0]['retention'] = 'required_pending'
    elif mutation == 'archive_only':
        del bundle['originals'][0]['raw_sha256']
    else:
        bundle['originals'] = []
    assert evaluate(bundle, stage)['status'] == 'blocked'


@pytest.mark.parametrize('path', ['../escape.json', '/absolute.json', 'a\\b.json', 'a/./b'])
def test_ambiguous_paths_rejected(tmp_path, path):
    bundle, stage = fixture(tmp_path)
    bundle['files'][0]['path'] = path
    assert evaluate(bundle, stage)['status'] == 'blocked'


def test_symlink_rejected(tmp_path):
    bundle, stage = fixture(tmp_path)
    (stage / 'alias').symlink_to(stage / 'export.json')
    assert evaluate(bundle, stage)['status'] == 'blocked'


@pytest.mark.parametrize('value', [None, {}, [], {'records': None}])
def test_malformed_bundle_fails_closed(tmp_path, value):
    assert pe.validate_bundle(value, tmp_path, 'unverified', 'public-example')['status'] == 'blocked'


def test_duplicate_identity_rejected(tmp_path):
    bundle, stage = fixture(tmp_path)
    bundle['records'].append(copy.deepcopy(bundle['records'][0]))
    assert evaluate(bundle, stage)['status'] == 'blocked'


def test_duplicate_json_keys_rejected():
    with pytest.raises(ValueError):
        pe.load_json('{"records": [], "records": []}')


def test_nonfinite_json_rejected():
    with pytest.raises(ValueError):
        pe.load_json('{"value": NaN}')


def test_review_binds_record_payload_and_original_hashes(tmp_path):
    bundle, stage = fixture(tmp_path)
    digest = pe.bundle_digest(bundle)
    bundle['records'][0]['payload']['value'] = 'unreviewed'
    write_export(bundle, stage, bundle['records'])
    assert evaluate(bundle, stage, digest)['status'] == 'blocked'
    bundle, stage = fixture(tmp_path / 'second')
    digest = pe.bundle_digest(bundle)
    bundle['originals'][0]['raw_sha256'] = hashlib.sha256(b'changed').hexdigest()
    assert evaluate(bundle, stage, digest)['status'] == 'blocked'


def test_review_binds_destination(tmp_path):
    bundle, stage = fixture(tmp_path)
    assert pe.validate_bundle(bundle, stage, pe.bundle_digest(bundle),
                              'different-public-target')['status'] == 'blocked'


def test_cli_receipt_and_exit(tmp_path, capsys):
    bundle, stage = fixture(tmp_path)
    manifest = tmp_path / 'bundle.json'
    manifest.write_text(json.dumps(bundle))
    args = ['--bundle', str(manifest), '--stage', str(stage),
            '--approved-bundle-sha256', pe.bundle_digest(bundle),
            '--destination', 'public-example']
    assert pe.main(args) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'eligible'
    manifest.write_text('{"records": [], "records": []}')
    assert pe.main(args) == 1
    assert json.loads(capsys.readouterr().out)['status'] == 'blocked'


def test_json_boolean_cannot_impersonate_number(tmp_path):
    bundle, stage = fixture(tmp_path)
    bundle['records'][0]['payload'] = {'value': True}
    altered = copy.deepcopy(bundle['records'])
    altered[0]['payload'] = {'value': 1}
    write_export(bundle, stage, altered)
    assert evaluate(bundle, stage)['status'] == 'blocked'


def test_empty_bundle_is_blocked(tmp_path):
    bundle, stage = fixture(tmp_path)
    bundle['records'] = []
    bundle['decisions'] = {}
    write_export(bundle, stage, [])
    assert evaluate(bundle, stage)['status'] == 'blocked'


def test_documented_example(tmp_path):
    """Independent hand result: source, entity, cost deferred; independent exported."""
    import importlib.util

    path = Path(__file__).resolve().parents[2] / 'examples/governance/publication_eligibility_example.py'
    spec = importlib.util.spec_from_file_location('publication_example', path)
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    output = tmp_path / 'example'
    digest = example.build_example(output)
    # Synthetic approval injection is confined to this test, not the generator.
    bundle = pe.load_json((output / 'bundle.json').read_text())
    staged = pe.load_json((output / 'stage/export.json').read_text())
    assert staged == {'records': [{
        'id': 'independent', 'dependencies': [],
        'payload': {'note': 'synthetic example'},
    }]}
    assert bundle['records'][-1]['original_ids'] == ['synthetic-input']
    result = pe.validate_bundle(bundle, output / 'stage', digest, 'public-example')
    assert result == {'status': 'eligible', 'counts': {
        'eligible': 1, 'deferred': 3, 'exported': 1}, 'errors': []}
    with pytest.raises(FileExistsError):
        example.build_example(output)


@pytest.mark.parametrize(('pinned', 'staged'), [
    ('0.0', '1e-400'), ('0.0', '-1e-400'),
    ('1.0', '1.00000000000000001'),
    ('9007199254740992.0', '9007199254740993.0'),
])
def test_numeric_rounding_cannot_hide_staged_mismatch(tmp_path, pinned, staged):
    """Pin the actual staged bytes while independently proving numeric inequality."""
    assert Decimal(pinned) != Decimal(staged)
    bundle, stage = fixture(tmp_path)
    bundle['records'][0]['payload'] = {'value': json.loads(pinned)}
    content = json.dumps({'records': bundle['records']})
    marker = '"value": ' + pinned
    assert content.count(marker) == 1
    content = content.replace(marker, '"value": ' + staged).encode()
    (stage / 'export.json').write_bytes(content)
    bundle['files'][0]['sha256'] = hashlib.sha256(content).hexdigest()
    result = evaluate(bundle, stage)
    assert result['status'] == 'blocked'
    assert result['errors'] == ['lossy_json_number']


@pytest.mark.parametrize('token', [
    '1e-400', '-1e-400', '1.00000000000000001', '9007199254740993.0',
])
def test_lossy_json_number_rejected(token):
    with pytest.raises(pe.InvalidBundle, match='^lossy_json_number$'):
        pe.load_json('{"nested": [{"value": ' + token + '}]}')


@pytest.mark.parametrize('token', ['1e999', '-1e999'])
def test_exponent_overflow_rejected_during_parsing(token):
    with pytest.raises(pe.InvalidBundle, match='^nonfinite_json$'):
        pe.load_json('{"value": ' + token + '}')


@pytest.mark.parametrize('token', [
    '0.0', '-0.0', '0.1', '1.00', '1e-300', '1e300', '9007199254740993',
])
def test_round_trip_numbers_remain_supported(token):
    parsed = pe.load_json('{"value": ' + token + '}')
    rendered = json.dumps(parsed)
    assert json.loads(rendered, parse_float=Decimal)['value'] == Decimal(token)
    assert pe.bundle_digest(parsed) == pe.bundle_digest(json.loads(rendered))
