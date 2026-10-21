"""Write synthetic publication inputs; this example grants no source rights.

Usage: python examples/governance/publication_eligibility_example.py --output example
The output directory must not exist. Nothing is published or approved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/governance'))
from publication_eligibility import bundle_digest


def build_example(output):
    """Create a hand-checkable chain and an independent eligible record.

    Issue 3942 requires transitive deferral. Hand calculation: unresolved source
    defers entity, which defers cost. Only independent remains: eligible=1,
    deferred=3, exported=1. These are graph cardinalities, not sourced constants.
    All payloads, identities and retention declarations here are synthetic.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    stage = output / 'stage'
    stage.mkdir()
    dependencies = {'source': [], 'entity': ['source'], 'cost': ['entity'],
                    'independent': []}
    records = [{'id': key, 'dependencies': links, 'original_ids': ['synthetic-input'],
                'payload': {'note': 'synthetic example'}} for key, links in dependencies.items()]
    decisions = {key: {'decision': 'eligible_factual_derivative',
                       'basis': 'synthetic demonstration only',
                       'reviewer': 'synthetic-reviewer',
                       'evidence_ref': 'synthetic-review'} for key in dependencies}
    decisions['source']['decision'] = 'unresolved'
    content = json.dumps({'records': [records[-1]]}).encode('utf-8')
    (stage / 'export.json').write_bytes(content)
    bundle = {'publication': {'destination': 'public-example', 'audience': 'public'},
              'records': records, 'decisions': decisions,
              'originals': [{'id': 'synthetic-input', 'retention': 'private_retained',
                             'raw_sha256': hashlib.sha256(b'synthetic raw').hexdigest(),
                             'archive_sha256': hashlib.sha256(b'synthetic archive').hexdigest(),
                             'evidence_ref': 'synthetic-retention'}],
              'files': [{'path': 'export.json', 'role': 'eligible_export',
                         'record_ids': ['independent'],
                         'sha256': hashlib.sha256(content).hexdigest()}]}
    (output / 'bundle.json').write_text(json.dumps(bundle, indent=2) + '\n', encoding='utf-8')
    return bundle_digest(bundle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(build_example(args.output))


if __name__ == '__main__':
    main()
