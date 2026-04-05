#!/usr/bin/env python3
"""
Marine Subdomain Taxonomy Classifier — #1653

Classifies marine domain documents in index.jsonl into 9 subdomains
using filename, old_path, and path-based keyword matching.

Output: data/document-index/marine-subdomain-tags.yaml + distribution report.
"""

import json
import yaml
import os
import sys
from collections import Counter
from pathlib import Path

INDEX_PATH = 'data/document-index/index.jsonl'
OUTPUT_PATH = 'data/document-index/marine-subdomain-tags.yaml'
REPORT_PATH = 'docs/document-intelligence/marine-taxonomy-classification-report.md'

# 9 subdomains with keyword lists for path/filename matching
# Order matters — more specific subdomains first to avoid false positives
SUBDOMAINS = {
    'hydrodynamics': {
        'name': 'Hydrodynamics',
        'keywords': [
            'rao', 'diffraction', 'radiation', 'response amplitude', 'seakeeping',
            'wave loading', 'wave force', 'hydrodynamic', 'potential flow',
            'morison', 'drag coefficient', 'added mass', 'wave kinematics',
            'current force', 'wind load', 'wind tunnel', 'model test',
            'basin test', 'towing tank', 'aqua', 'aqwa', 'wadam', 'wamit',
            'hydrostar', 'sesam', 'hydrodynam', 'wave elevation', 'wave height',
            'significant wave', 'wave scatter', 'wave spectrum', 'jswap',
            'jonswap', 'pierson', 'wave period', 'wave direction', 'metocean',
            'hydrostatic', 'stability curve', 'trim', 'heel', 'draft',
            'inclining', 'intact stability', 'damage stability',
            'vessel motion', 'vessel response', 'motion analysis',
            'transfer function', 'phase angle', 'rao phase',
        ],
    },
    'mooring': {
        'name': 'Mooring',
        'keywords': [
            'mooring', 'catenary', 'turret', 'spread mooring', 'anchor',
            'hawser', 'fairlead', 'moorpy', 'moor', 'static mooring',
            'dynamic mooring', 'mooring line', 'chain', 'wire rope',
            'fiber rope', 'polyester', 'nylon', 'hawser analysis',
            'offloading', 'side-by-side', 'tandem mooring',
            'calm buoy', 'spar mooring', 'fpso mooring',
            'mooring integrity', 'mooring assessment',
            'quay wall', 'jetty', 'berthing',
            'mooring hook_up', 'hook up',
        ],
    },
    'risers_umbilicals': {
        'name': 'Risers & Umbilicals',
        'keywords': [
            'riser', 'umbilical', 'flexible riser', 'steel catenary riser',
            'scr', 'scr_', 'top tensioned riser', 'ttr', 'top tensioned',
            'production riser', 'drilling riser', 'hybrid riser',
            'lazy wave riser', 'lazy s riser', 'steep wave riser',
            'flexible pipe', 'flexible riser', 'bonded hose',
            'riser connector', 'riser base', 'hang-off',
            'well intervention riser', 'workover riser',
            'umbilical termination', 'control umbilical',
            'riser analysis', 'riser design', 'riser assessment',
        ],
    },
    'viv_fatigue': {
        'name': 'VIV & Fatigue',
        'keywords': [
            'viv', 'vortex induced', 'vortex-induced', 'viva', 'vivana',
            'shear7', 'orcafleviv', 'shev7',
            'fatigue', 'sn curve', 's-n curve', 'rainflow', 'palmgren-miner',
            'damage accumulation', 'fatigue assessment', 'fatigue analysis',
            'fatigue life', 'design fatigue', 'fatigue design factor',
            'free span fatigue', 'wave fatigue', 'vortex shedding',
            'strake', 'helical strake', 'viv suppression',
            'inline vibration', 'cross-flow vibration', 'galloping',
            'lock-in', 'reduced velocity',
        ],
    },
    'installation': {
        'name': 'Installation',
        'keywords': [
            'installation', 'pipelay', 'lay', 's-lay', 'j-lay', 'reel-lay',
            'reel lay', 'heavy lift', 'crane', 'lifting', 'lifting analysis',
            'lift', 'rigging', 'haul', 'towing', 'tow', 'deployment',
            'flot-over', 'floatover', 'float-over', 'mating',
            'subsea installation', 'foundation install', 'pile driving',
            'hammer', 'piling', 'spud', 'jack-up',
            'surf installation', 'cable lay',
            'hookup and commissioning', 'huc', 'commissioning',
            'installation analysis', 'transportation analysis',
            'offshore installation',
        ],
    },
    'marine_operations': {
        'name': 'Marine Operations',
        'keywords': [
            'marine operations', 'marine warranty', 'mws', 'survey',
            'marine assurance', 'simops', 'simultaneous operations',
            'dynamic positioning', 'dp system', 'dp analysis', 'dp capability',
            'cam', 'capability plot',
            'rov', 'diving', 'subsea intervention',
            'operability', 'weather window', 'downtime',
            'marine procedure', 'marine plan',
            'campaign', 'logistics', 'marine risk assessment',
            'transfer', 'personnel transfer', 'walk-to-work',
            'gangway', 'ctv', 'ahts', 'psv', 'anchor handling',
            'sea fastening', 'marine transport',
        ],
    },
    'vessels_floaters': {
        'name': 'Vessels & Floaters',
        'keywords': [
            'fpso', 'spar', 'semi-sub', 'semisub', 'semi submersible',
            'tension leg', 'tlp', 'tender', 'drillship', 'vessel',
            'barge', 'ship', 'floating', 'floater', 'floating production',
            'naval architecture', 'general arrangement', 'ga',
            'ballast', 'trim and stability', 'hydrostatics',
            'class notation', 'flag state', 'vessel spec',
            'hull form', 'principal particulars',
            'cargo capacity', 'storage capacity',
            'moonpool', 'column', 'pontoon', 'hull strength',
            'vessel r', 'loading arm', 'loading analysis',
            'stinger', 'dp vessel', 'construction vessel',
            'dsv', 'csv', 'osv', 'supply vessel',
        ],
    },
    'subsea_pipelines': {
        'name': 'Subsea & Pipelines',
        'keywords': [
            'subsea', 'pipeline', 'flowline', 'manifold', 'plet',
            'plem', 'spool', 'end expansion', 'on-bottom', 'on bottom',
            'lateral buckling', ' upheaval', 'pipeline stability',
            'pipeline walking', 'walking', 'trenching', 'burial',
            'pipeline crossing', 'tie-in', 'jumpers', 'spoolpiece',
            'pigrun', 'pigg', 'pigging', 'expansion spool',
            'corrosion allowance', 'anode', 'cp for pipeline',
            'seabed', 'mudline', 'soil interaction', 'pipe-soil',
            'on-bottom stability', 'abs_lrf', 'dnv f101',
            'flow assurance', 'slug', 'slugging', 'hydrate',
            'subsea tree', 'wellhead', 'xmas tree',
        ],
    },
    'other': {
        'name': 'Other',
        'keywords': [
            # Catch-all for marine docs that don't fit above
            'acoustic', 'ice', 'lightning', 'earthing', 'cable',
            'power generation', 'generator', 'power cable',
            'emissions', 'flaring', 'vent',
        ],
    },
}

# Build lookup: keyword -> subdomain
KEYWORD_MAP = {}
for subdomain, info in SUBDOMAINS.items():
    for kw in info['keywords']:
        KEYWORD_MAP[kw.lower()] = subdomain


def classify_document(doc):
    """Classify a single marine document into a subdomain."""
    path = doc.get('path', '')
    old_path = doc.get('old_path', '')
    filename = os.path.basename(path)
    ext = doc.get('ext', 'unknown')

    # Handle DWG/DXF as CAD — needs different processing
    if ext in ('dwg', 'dxf'):
        return 'cad_drawing', 0

    # Combine searchable text: filename + path segments + old_path
    searchable = (
        filename.lower().replace('_', ' ').replace('-', ' ').replace('.', ' ') + ' ' +
        old_path.lower().replace('_', ' ').replace('-', ' ').replace('.', ' ')
    )

    # Score each subdomain
    scores = Counter()
    for kw, subdomain in KEYWORD_MAP.items():
        if kw in searchable:
            # Longer/more-specific keywords get higher weight
            weight = max(1, len(kw) // 4)
            scores[subdomain] += weight

    if not scores:
        return 'unclassified', 0

    top_subdomain, top_score = scores.most_common(1)[0]
    return top_subdomain, top_score


def main():
    print("Marine Subdomain Taxonomy Classifier (#1653)")
    print("=" * 50)

    entries = []
    counts = Counter()
    total = 0
    classified_text = 0
    unclassified = 0
    cad_drawings = 0
    min_threshold = 2  # require at least this score

    # Process index line by line
    print(f"Processing {INDEX_PATH}...")
    with open(INDEX_PATH) as f:
        for i, line in enumerate(f):
            if i % 100000 == 0 and i > 0:
                print(f"  Processed {i:,} entries...")
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                continue

            if doc.get('domain') != 'marine':
                continue

            total += 1
            subdomain, score = classify_document(doc)

            if score >= min_threshold and subdomain != 'cad_drawing':
                classified_text += 1
            elif subdomain == 'cad_drawing':
                cad_drawings += 1
                subdomain = 'cad_drawing'
            else:
                unclassified += 1
                subdomain = 'unclassified'

            counts[subdomain] += 1
            entries.append({
                'path': doc.get('path', ''),
                'old_path': doc.get('old_path', ''),
                'org': doc.get('org', ''),
                'ext': doc.get('ext', ''),
                'size_mb': doc.get('size_mb', 0),
                'subdomain': subdomain,
                'confidence': round(score, 1),
            })

    print(f"\nDone. Processed {total:,} marine documents.")
    print(f"\n=== Distribution ===")
    for subdomain, count in counts.most_common():
        pct = count / total * 100 if total else 0
        name = SUBDOMAINS.get(subdomain, {}).get('name', subdomain.replace('_', ' ').title())
        print(f"  {name:30s} {count:>8,}  ({pct:5.1f}%)")

    print(f"\n  CAD drawings (dwg/dxf): {cad_drawings:>8,} (skip — need CAD metadata)")
    print(f"  Classifiable text/docs: {classified_text:>8,}")
    print(f"  Unclassified:           {unclassified:>8,}")
    if classified_text > 0:
        print(f"  Unclassified rate (of text): {unclassified/max(1,classified_text)*100:.1f}%")
    print(f"  Total:                  {total:>8,}")

    # Write subdomain tags
    print(f"\nWriting taxonomy to {OUTPUT_PATH}...")
    output = {
        'generated': '2026-04-05T12:00:00',
        'issue': '#1653',
        'total_marine': total,
        'classifier': 'keyword-based (filename + path)',
        'distribution': dict(counts.most_common()),
        'entries': entries,
    }
    with open(OUTPUT_PATH, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    print(f"Done. {len(entries)} entries written to {OUTPUT_PATH}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
