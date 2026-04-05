#!/usr/bin/env python3
"""
Marine Subdomain Taxonomy Classifier — V2 Expanded (#1653)

Classifies marine domain documents in index.jsonl into 9 subdomains
using filename, path, and standard number mapping.

The V1 classifier only used basic keywords. V2 adds:
1. API standard number mapping (2SK=mooring, 2A=structural, etc.)
2. DNV standard number mapping (E301=mooring, E304=pipeline, etc.)
3. Expanded keyword lists based on unclassified samples
4. Project folder path patterns
"""

import json
import yaml
import os
import sys
from collections import Counter

INDEX_PATH = 'data/document-index/index.jsonl'
OUTPUT_PATH = 'data/document-index/marine-subdomain-tags.yaml'
REPORT_PATH = 'data/document-intelligence/taxonomy-all-domains-plan.md'

# === STANDARD NUMBER MAPPINGS ===
# These map common standard prefixes/codes to subdomains
STANDARD_MAP = {
    # API standards
    'rp 2sk': 'mooring', '2sk': 'mooring',
    'rp 2a': 'structural', '2a-w': 'structural', '2a-wsd': 'structural',
    'rp 2i': 'mooring', '2i': 'mooring',
    'rp 2fp': 'marine_operations', '2fp': 'marine_operations',
    'rp 2t': 'marine_operations', '2t': 'marine_operations',
    'spec 2f': 'mooring', 'spec 2c': 'mooring', 'spec 17': 'subsea_pipelines', '2f': 'mooring',
    'rp 1111': 'subsea_pipelines', '1111': 'subsea_pipelines',
    'rp 11gp': 'subsea_pipelines', '11gp': 'subsea_pipelines',
    'bulletin 2int': 'structural', '2int': 'structural',
    
    # DNV standards
    'os-e301': 'mooring', 'e301': 'mooring',
    'os-e302': 'vessels_floaters', 'e302': 'vessels_floaters',
    'os-e303': 'hydrodynamics', 'e303': 'hydrodynamics',
    'os-e304': 'subsea_pipelines', 'e304': 'subsea_pipelines',
    'os-e305': 'installation', 'e305': 'installation',
    'os-e401': 'subsea_pipelines', 'e401': 'subsea_pipelines',
    'os-c101': 'vessels_floaters', 'c101': 'vessels_floaters',
    'os-c201': 'subsea_pipelines', 'c201': 'subsea_pipelines',
    'os-j101': 'vessels_floaters', 'j101': 'vessels_floaters',
    'rp-c103': 'subsea_pipelines', 'rp-c203': 'structural', 'rp-c205': 'hydrodynamics', 'c205': 'hydrodynamics',
    'rp-e301': 'mooring', 'rp-d101': 'mooring', 'd101': 'mooring',
    'rp-e401': 'subsea_pipelines',
    'rp-e402': 'installation', 'e402': 'installation',
    'rp-e405': 'marine_operations', 'e405': 'marine_operations',
    'rp-e406': 'marine_operations',
    'rp-e407': 'subsea_pipelines',
    'rp-c203': 'structural', 'c203': 'structural',
    'rp-202': 'marine_operations',
    'rp-e403': 'subsea_pipelines', 'e403': 'subsea_pipelines',
    'rp-e404': 'subsea_pipelines',
    'rp-e409': 'risers_umbilicals',
    'rp-e408': 'installation',
    'rp-e406': 'marine_operations',
    'rp-e403': 'subsea_pipelines',
    'rp-e405': 'marine_operations',
    'rp-c405': 'subsea_pipelines',
    'rp-c501': 'hydrodynamics',
    'cn 30.4': 'vessels_floaters',
    'cn 31.2': 'vessels_floaters',
    
    # DNVGL
    'st-0177': 'risers_umbilicals',
    'st-0162': 'subsea_pipelines',
    'st-0145': 'mooring',
    'st-0126': 'mooring',
    'st-f101': 'subsea_pipelines', 'f101': 'subsea_pipelines',
    'st-os-f101': 'subsea_pipelines',
    'se-0402': 'marine_operations',
    
    # ABS
    'guide-buckling': 'structural',
    'guide-dynamic-positioning': 'marine_operations',
    'fpi': 'vessels_floaters',
    'mouv': 'vessels_floaters',
    'guide-survey-after-construction': 'marine_operations',
    'guide-crane': 'installation',
    'guide-lifting': 'installation',
    'guide-hsb': 'hydrodynamics',
    'guide-sls': 'hydrodynamics',
    'guide-lrs': 'hydrodynamics',
    
    # ISO
    '13624': 'risers_umbilicals', '13628': 'subsea_pipelines', '19901': 'subsea_pipelines',
    '19902': 'subsea_pipelines', '19904': 'subsea_pipelines', '19905': 'subsea_pipelines',
    '301': 'subsea_pipelines',
}

# === EXPANDED KEYWORDS ===
# Based on analysis of unclassified samples
SUBDOMAINS = {
    'hydrodynamics': {
        'name': 'Hydrodynamics',
        'keywords': [
            'rao', 'diffraction', 'radiation', 'response amplitude', 'seakeeping',
            'wave loading', 'wave force', 'hydrodynamic', 'potential flow',
            'morison equation', 'drag coefficient', 'added mass', 'wave kinematics',
            'current force', 'wind load', 'wind tunnel', 'model test',
            'basin test', 'towing tank', 'hydrodynam', 'aqua', 'aqwa', 'wadam', 'wamit',
            'hydrostar', 'sesam', 'hydrodynam', 'wave elevation', 'wave height',
            'significant wave', 'wave scatter', 'wave spectrum', 'jonswap',
            'jonswap', 'pierson', 'moskowitz', 'wave period', 'wave direction', 'metocean',
            'hydrostatic', 'stability curve', 'trim', 'heel', 'draft condition',
            'inclining experiment', 'intact stability', 'damage stability',
            'vessel motion', 'vessel response', 'motion analysis',
            'transfer function', 'phase angle', 'rao phase',
            'environmental condition', 'environmental load', 'environmental data',
            'return period', 'extreme value', 'hindcast',
            'current profile', 'wave current', 'swell', 'sea state',
            'scatter diagram', 'weibull', 'extreme wave', 'design wave',
            'green water', 'slamming', 'air gap', 'wave crest',
            'wind speed', 'wind force', 'wind coefficient', 'wind tunnel',
        ],
    },
    'mooring': {
        'name': 'Mooring',
        'keywords': [
            'mooring', 'catenary', 'turret', 'spread mooring', 'anchor',
            'hawser', 'fairlead', 'moorpy', 'moor', 'static mooring',
            'dynamic mooring', 'mooring line', 'chain', 'wire rope',
            'fiber rope', 'polyester', 'nylon rope', 'hawser analysis',
            'offloading', 'side-by-side', 'tandem mooring',
            'calm buoy', 'spar mooring', 'fpso mooring',
            'mooring integrity', 'mooring assessment',
            'quay wall', 'jetty', 'berthing', 'dolphin', 'mooring hook_up', 'hook up',
            'station keeping', 'stationkeeping', 'station keeping system',
            'line tension', 'anchor drag', 'anchor pile', 'suction anchor', 'suction pile',
            'driven pile', 'plate anchor', 'drag embedment', 'vla', 'deep penetrating anchor',
            'drag anchor', 'dead weight anchor', 'gravity anchor',
            'mooring pattern', 'mooring layout', 'mooring arrangement',
            'chain diameter', 'chain grade', 'stud link', 'studless',
            'mooring recovery', 'mooring retrieval',
            'shackle', 'connecting link', 'swivel',
            'mooring analysis', 'mooring design', 'mooring specification',
        ],
    },
    'risers_umbilicals': {
        'name': 'Risers & Umbilicals',
        'keywords': [
            'riser', 'umbilical', 'flexible riser', 'steel catenary riser',
            'scr', 'scr_', 'top tensioned riser', 'ttr', 'top tensioned',
            'production riser', 'drilling riser', 'hybrid riser',
            'lazy wave riser', 'lazy s riser', 'steep wave riser',
            'flexible pipe', 'bonded hose', 'unbonded flexible',
            'riser connector', 'riser base', 'hang-off',
            'well intervention riser', 'workover riser',
            'umbilical termination', 'control umbilical',
            'riser analysis', 'riser design', 'riser assessment',
            'riser tensioner', 'riser support', 'riser clamp',
            'bend stiffener', 'bend restrictor', 'buoyancy module',
            'arch buoy', 'hog bend', 'sag bend', 'touchdown', 'tdp',
            'riser fatigue', 'riser stress', 'riser global',
            'power cable umbilical', 'hydraulic umbilical',
            'chemical injection', 'subsea umbilical',
        ],
    },
    'viv_fatigue': {
        'name': 'VIV & Fatigue',
        'keywords': [
            'viv', 'vortex induced', 'vortex-induced', 'viva', 'vivana',
            'shear7', 'orcafleviv', 'shev7', 'vivace',
            'fatigue', 'sn curve', 's-n curve', 'rainflow',
            'palmgren', 'damage accumulation',
            'fatigue assessment', 'fatigue analysis', 'fatigue life',
            'design fatigue', 'fatigue design factor',
            'free span fatigue', 'wave fatigue',
            'vortex shedding', 'strake', 'helical strake',
            'viv suppression', 'inline vibration', 'cross-flow vibration',
            'galloping', 'lock-in', 'reduced velocity',
            'stress concentration factor', 'scf', 'sn data',
            'fatigue crack', 'crack growth', 'corrosion fatigue',
            'endurance limit', 'weld fatigue', 'hot spot stress',
            'cumulative damage', 'palmgren-miner', 'miner sum',
            'fatigue safety factor', 'fsf',
            'spectral fatigue', 'time domain fatigue',
            't-n curve', 'tn curve', 'sn curve',
        ],
    },
    'installation': {
        'name': 'Installation',
        'keywords': [
            'installation', 'pipelay', 'pipelay analysis',
            's-lay', 'j-lay', 'reel-lay', 'reel lay',
            'heavy lift', 'crane', 'crane operation',
            'lifting', 'lifting analysis', 'lift plan', 'lift study',
            'rigging', 'haul', 'towing', 'tow study', 'towing analysis',
            'deployment', 'deploy',
            'flot-over', 'floatover', 'float-over', 'mating', 'mating analysis',
            'subsea installation', 'foundation install',
            'pile driving', 'hammer', 'piling', 'pile driving analysis',
            'driveability', 'drivability', 'hammer energy',
            'spud', 'spudcan', 'jack-up', 'jackup',
            'surf', 'surf installation', 'cable lay',
            'hookup and commissioning', 'huc', 'commissioning',
            'transportation analysis', 'offshore installation',
            'sea fastening', 'sea fastening analysis', 'transport',
            'transportation', 'load-out', 'loadout', 'load out',
            'upend', 'upending', 'upending analysis',
            'pre-lay', 'prelay', 'pre-lay survey',
            'post-lay', 'postlay', 'post-lay survey',
            'pull-in', 'pullin', 'make-up', 'makeup',
            'lay vessel', 'construction vessel', 'crane vessel',
            'abandonment', 'recovery', 'abandon and recovery',
            'pipelay tensioner', 'stinger', 'overbend', 'sagbend',
            'installation load', 'installation factor',
        ],
    },
    'marine_operations': {
        'name': 'Marine Operations',
        'keywords': [
            'marine operations', 'marine warranty', 'mws', 'marine assurance',
            'simops', 'simultaneous operations',
            'dynamic positioning', 'dp system', 'dp operation',
            'dp analysis', 'dp capability', 'cam',
            'capability analysis', 'capability plot',
            'rov', 'rov survey', 'diving', 'diving ops',
            'subsea intervention', 'well intervention',
            'operability', 'operability analysis', 'weather window',
            'downtime', 'downtime analysis',
            'marine procedure', 'marine plan', 'marine campaign',
            'workover', 'coiled tubing', 'wireline', 'snubbing',
            'campaign logistics', 'marine risk assessment',
            'transfer ops', 'personnel transfer', 'walk-to-work',
            'gangway', 'compensated gangway',
            'ctv', 'ahts', 'psv', 'anchor handling',
            'marine transport', 'supply vessel',
            'mooring operation', 'mooring ops',
            'anchor handling tug', 'supply boat',
            'marine spread', 'spread', 'marine resources',
            'weather criteria', 'sea state criteria',
            'marine campaign plan', 'campaign planning',
        ],
    },
    'vessels_floaters': {
        'name': 'Vessels & Floaters',
        'keywords': [
            'fpso', 'spar', 'semi-sub', 'semisub', 'semi submersible',
            'tension leg', 'tlp', 'tender', 'drillship', 'vessel',
            'barge', 'ship', 'floating', 'floater',
            'floating production', 'floating storage',
            'naval architecture', 'general arrangement', 'ga',
            'ballast', 'ballast system', 'ballast tank',
            'trim and stability', 'hydrostatics',
            'class notation', 'flag state',
            'vessel specification', 'vessel spec', 'hull specification',
            'hull form', 'principal particulars',
            'cargo capacity', 'storage capacity', 'cargo tank',
            'moonpool', 'column', 'pontoon', 'hull strength',
            'loading arm', 'loading analysis', 'offloading',
            'stinger', 'dp vessel', 'construction vessel',
            'dsv', 'csv', 'osv', 'supply vessel',
            'accommodation', 'accommodation block',
            'topside', 'topsides', 'hull and topsides',
            'hull design', 'hull structure', 'hull fabrication',
            'vessel type', 'vessel selection',
            'turret mooring', 'internal turret', 'external turret',
            'swivel', 'turret bearing',
            'production system', 'process', 'topsides process',
            'drilling system', 'drilling rig', 'modu',
            'offloading system', 'calm buoy', 'single buoy',
            'loading system',
        ],
    },
    'subsea_pipelines': {
        'name': 'Subsea & Pipelines',
        'keywords': [
            'subsea', 'pipeline', 'flowline', 'manifold', 'plet',
            'plem', 'spool', 'end expansion',
            'on-bottom stability', 'on-bottom', 'on bottom',
            'lateral buckling', 'upheaval buckling',
            'pipeline stability', 'pipeline walking', 'pipeline walking analysis',
            'trenching', 'burial', 'natural burial',
            'pipeline crossing', 'tie-in', 'jumpers', 'spoolpiece', 'in-line jumper',
            'pigrun', 'pigg', 'pigging', 'pig launch', 'pig receiver',
            'expansion spool', 'corrosion allowance',
            'cp for pipeline', 'seabed', 'mudline',
            'soil interaction', 'pipe-soil interaction', 'axial soil', 'lateral soil',
            'abs_lrf', 'dnv f101',
            'flow assurance', 'slug', 'slugging', 'hydrate', 'hydrate management',
            'subsea tree', 'wellhead', 'xmas tree',
            'subsea well', 'subsea equipment', 'subsea hardware',
            'pipeline wall thickness', 'pipeline design', 'pipeline installation',
            'pipeline stress', 'pipeline buckling', 'pipeline expansion',
            'propagating buckle', 'buckle arrestor', 'buckle detector',
            'reeling pipeline', 'reel lay pipeline',
            'coating', 'concrete weight coating', 'fjc', 'ffc',
            'subsea manifold', 'subsea template',
            'pipeline end manifold', 'pipeline end termination',
            'rigid pipeline', 'flexible pipeline',
        ],
    },
    'other': {
        'name': 'Other',
        'keywords': [
            'acoustic', 'acoustic monitoring',
            'ice', 'iceberg', 'ice loading',
            'lightning', 'earthing', 'cable routing',
            'power generation', 'power cable', 'power distribution',
            'emissions', 'flaring', 'vent system',
            'hse', 'health safety', 'hazop', 'hazid',
            'regulatory', 'permit', 'environmental impact',
            'project management', 'project plan',
            'report', 'summary', 'specification',
        ],
    },
}


def classify_document(doc, min_score=1):
    """Classify a marine document using standard mapping + keywords + path patterns."""
    path = doc.get('path', '')
    old_path = doc.get('old_path', '')
    filename = os.path.basename(path)
    ext = doc.get('ext', 'unknown')
    folder_hints = []

    # Skip CAD drawings — needs separate processing
    if ext in ('dwg', 'dxf'):
        return 'cad_drawing', 0

    # Build searchable text from path + filename + old_path
    searchable = (
        path.lower() + ' ' +
        filename.lower() + ' ' +
        old_path.lower()
    )
    searchable = searchable.replace('_', ' ').replace('-', ' ').replace('.', ' ')

    # Check for folder-based classification hints
    path_lower = path.lower()
    if 'disciplines/' in path_lower:
        # Extract discipline from path: disciplines/xxx/projects/...
        parts = path.split('/')
        for i, p in enumerate(parts):
            if p == 'disciplines' and i + 1 < len(parts):
                folder_hints.append(parts[i + 1].lower())

    # === Priority: 1. Standard Number Matching ===
    # Check filename and path for standard codes
    check_text = searchable.lower()
    for code, subdomain in STANDARD_MAP.items():
        if code in check_text:
            return subdomain, 10  # High confidence for known standards

    # === Priority: 2. Keyword Scoring ===
    scores = Counter()
    for subdomain, info in SUBDOMAINS.items():
        for kw in info['keywords']:
            if kw in searchable:
                weight = max(1, len(kw) // 4)
                scores[subdomain] += weight

    if scores:
        top_sub, top_score = scores.most_common(1)[0]
        if top_score >= min_score:
            return top_sub, top_score

    # === Priority: 3. Folder-based hints ===
    for hint in folder_hints:
        if 'mooring' in hint or 'moor' in hint:
            return 'mooring', 1
        if 'hydro' in hint or 'flowline' in hint or 'pipeline' in hint:
            return 'subsea_pipelines', 1
        if 'vessel' in hint or 'structural' in hint:
            return 'vessels_floaters', 1
        if 'drilling' in hint:
            return 'marine_operations', 1

    return 'unclassified', 0


def main():
    print("=" * 60)
    print("Marine Subdomain Taxonomy Classifier V2 (#1653)")
    print("=" * 60)
    print()

    counts = Counter()
    total = 0
    cad_drawings = 0
    classified_text = 0
    unclassified = 0
    
    # Sample of unclassified for debugging
    unclassified_samples = []

    with open(INDEX_PATH) as f:
        for i, line in enumerate(f):
            if i % 200000 == 0 and i > 0:
                print(f"  ... processed {i:,} index entries")
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                continue

            if doc.get('domain') != 'marine':
                continue

            total += 1
            subdomain, score = classify_document(doc, min_score=1)

            if subdomain == 'cad_drawing':
                cad_drawings += 1
            elif subdomain == 'unclassified':
                unclassified += 1
                if len(unclassified_samples) < 20:
                    unclassified_samples.append(doc.get('path', ''))
            else:
                classified_text += 1

            counts[subdomain] += 1

    # Print results
    print(f"\n{'=' * 60}")
    print(f"TOTAL MARINE DOCUMENTS: {total:,}")
    print(f"{'=' * 60}")
    print()

    by_category = {
        'cad_drawing': counts.get('cad_drawing', 0),
    }
    by_sub = {k: v for k, v in counts.items() if k not in ('cad_drawing', 'unclassified')}
    unclassified_count = counts.get('unclassified', 0)

    print(f"CAD Drawings (DWG/DXF): {by_category['cad_drawing']:>10,}  ({by_category['cad_drawing']/total*100:.1f}%)")
    print(f"Classified by V2:       {classified_text:>10,}  ({classified_text/total*100:.1f}%)")
    print(f"Unclassified:           {unclassified_count:>10,}  ({unclassified_count/total*100:.1f}%)")
    print()

    print("=== Subdomain Distribution (classified only) ===")
    for sub, cnt in sorted(by_sub.items(), key=lambda x: x[1], reverse=True):
        name = SUBDOMAINS.get(sub, {}).get('name', sub.replace('_', ' ').title())
        pct_of_total = cnt / total * 100 if total else 0
        pct_of_classified = cnt / classified_text * 100 if classified_text else 0
        print(f"  {name:30s} {cnt:>8,}  ({pct_of_total:5.1f}% of total, {pct_of_classified:5.1f}% of classified)")

    print()
    print("=== Unclassified Sample ===")
    for s in unclassified_samples[:20]:
        parts = s.split('/')
        print(f"  {parts[-5:]}")

    # Write compact output
    output = {
        'generated': '2026-04-05T12:00:00',
        'issue': '#1653 - Marine Subdomain Taxonomy V2',
        'total_marine_docs': total,
        'distribution': dict(counts.most_common()),
        'classifier': 'keyword+standard_mapping+folder_hints',
        'summary': {
            'cad_drawings': cad_drawings,
            'classified_text': classified_text,
            'unclassified': unclassified_count,
        }
    }

    with open(OUTPUT_PATH, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    print(f"\nWrote taxonomy: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")

    return 0


if __name__ == '__main__':
    sys.exit(main())
