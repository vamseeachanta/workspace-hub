#!/usr/bin/env python3
"""
Batch classifier for ace-shard-04.json
Extracts text from PDFs and classifies by engineering discipline.
"""
import json
import os
import subprocess
import sys
import re
from datetime import datetime

SHARD_FILE = '/mnt/local-analysis/workspace-hub/data/document-index/shards/ace-shard-04.json'
OUT_DIR = '/mnt/local-analysis/workspace-hub/data/document-index/summaries'
TIMESTAMP = '2026-02-24T00:00:00Z'

# ---------------------------------------------------------------------------
# Keyword-based classifier using path + extracted text
# ---------------------------------------------------------------------------

DISCIPLINE_RULES = [
    # (discipline, [keywords/patterns])
    ('cathodic-protection', [
        'cathodic protection', 'sacrificial anode', 'impressed current',
        'corrosion protection', 'galvanic anode', 'iccp', 'cp system',
        'cathodic', 'anode', 'impressed current cathodic',
        'f401', 'rp f401', 'dnv rp f401',
    ]),
    ('pipeline', [
        'pipeline', 'subsea pipeline', 'submarine pipeline', 'on-bottom stability',
        'pipe laying', 'pipelaying', 'line pipe', 'api 5l', 'api spec 5l',
        'os f101', 'dnv f101', 'rp f101', 'pressure containment',
        'pipe design', 'flowline', 'trunkline', 'riser design',
        'free span', 'free spanning', 'vortex induced', 'rp f105', 'dnv f105',
        'lateral buckling', 'upheaval buckling', 'pipe-in-pipe',
        'scour', 'on bottom stability',
    ]),
    ('drilling', [
        'wellbore', 'casing design', 'bop', 'blowout preventer',
        'well control', 'completion', 'drilling riser', 'marine riser',
        'mud weight', 'drill string', 'drillstring', 'wellhead',
        'christmas tree', 'tubing hanger', 'casing string',
        'api 6a', 'api spec 6a', '6a_e20', 'api 16r', 'riser coupling',
        'drilling unit', 'jack-up', 'jackup',
        'api 1104', '1104', 'pipeline welding', 'well completion',
        'amjig', 'drilling riser development',
    ]),
    ('marine', [
        'offshore structure', 'wave load', 'hydrodynamic', 'mooring',
        'tether', 'tendon', 'tethered', 'semi-submersible', 'semisubmersible',
        'spar', 'fpso', 'tlp', 'tension leg', 'deepwater platform',
        'api rp 2t', '2td', '2t ', 'api 2t', 'fatigue offshore',
        'dnv rp c203', 'vortex shedding', 'viv', 'vortex-induced vibration',
        'rp c203', 'fatigue design offshore',
        'floating wind', 'marine renewable', 'otc', 'offshore technology conference',
        'fixed offshore platform', 'jacket', 'api rp 2a', '2a wsd',
        'tubular joint', 'chord', 'brace',
    ]),
    ('installation', [
        'marine installation', 'lifting', 'load-out', 'loadout', 'transportation',
        'vessel operations', 'crane', 'rigging', 'heavy lift',
        'launch', 'upending', 'tow-out', 'towout', 'modu',
    ]),
    ('structural', [
        'structural integrity', 'stress analysis', 'finite element',
        'fea', 'pressure vessel', 'tank design', 'frame analysis',
        'api 579', '579', 'fitness for service', 'fitness-for-service',
        'api rp 579', 'fracture mechanics', 'stress concentration',
        'beam-column', 'buckling', 'shell theory', 'collapse',
    ]),
    ('materials', [
        'metallurgy', 'ndt', 'non-destructive', 'nondestructive',
        'fracture toughness', 'charpy', 'impact test', 'hardness',
        'yield strength', 'tensile strength', 'material property',
        'weld', 'welding', 'heat affected zone', 'haz',
        'api 5l', 'astm a', 'astm b', 'astm c', 'astm d', 'astm e',
        'astm f', 'astm g',
        'steel specification', 'alloy', 'corrosion resistance',
        'microstructure', 'grain', 'temper', 'anneal',
        'pipe specification', 'material specification',
        'astm a36', 'a572', 'a992', 'a500', 'a53', 'a106', 'a312',
        'astm e', 'mechanical test', 'tensile test',
        'titanium', 'inconel', 'duplex stainless',
        'standard specification',
    ]),
    ('geotechnical', [
        'soil mechanics', 'foundation', 'pile design', 'seabed',
        'geotechnical', 'soil investigation', 'bore hole',
        'consolidation', 'shear strength', 'bearing capacity',
        '2geo', 'api 2geo', 'geohazard', 'slope stability',
        'drag anchor', 'anchor design', 'suction caisson',
    ]),
    ('fire-safety', [
        'fire and explosion', 'hazop', 'hazardous area',
        'fire protection', 'explosion risk', 'atex', 'iec 60079',
        'fire suppression', 'deluge', 'blast', 'deflagration',
        'zone classification', 'flame detection',
    ]),
    ('electrical', [
        'electrical system', 'power system', 'instrumentation',
        'electrical cable', 'power cable', 'rp f401', 'electrical power cable',
        'transformer', 'switchgear', 'motor control',
        'cathodic protection electrical',
    ]),
    ('regulatory', [
        'codes and standards', 'compliance', 'safety management',
        'regulation', 'recommended practice', 'rp ', ' std ', 'standard',
        'dnv os', 'dnv rp', 'api rp', 'iso ', 'norsok',
        'certification', 'class notation', 'classification society',
        'safety case', 'risk-based inspection', 'rbi',
        'api 581', 'isp 581',
    ]),
    ('production', [
        'production system', 'esp', 'electrical submersible pump',
        'artificial lift', 'well surveillance', 'rod pump',
        'gas lift', 'subsea production', 'production tree',
        'separator', 'processing facility',
    ]),
    ('energy-economics', [
        'energy market', 'production forecast', 'economics',
        'reserves', 'resource assessment', 'decline curve',
    ]),
    ('document-processing', [
        'software', 'data processing', 'computing', 'algorithm',
        'database', 'information system', 'xml', 'metadata',
    ]),
]


def classify_by_path_and_text(path: str, text: str, title: str = '') -> tuple:
    """Return (discipline, keywords_found) based on path + text."""
    combined = (path + ' ' + (title or '') + ' ' + (text or '')).lower()

    # Special path-based rules first
    fname = os.path.basename(path).lower()
    ppath = path.lower()

    # ASTM documents - nearly all are materials specs
    if '/astm/' in ppath or '\\astm\\' in ppath:
        # Check if it's a specific type
        if any(k in combined for k in ['pipeline', 'pipe spec', 'line pipe']):
            return 'materials', ['astm', 'pipe specification', 'materials']
        return 'materials', ['astm', 'standard specification', 'materials']

    # API Specification files
    if 'api spec 5l' in combined or 'api_spec_5l' in fname or 'spec_5l' in fname:
        return 'pipeline', ['line pipe', 'api 5l', 'pipeline']

    if 'api spec 6a' in combined or '6a_e20' in fname or 'api_spec_6a' in fname:
        return 'drilling', ['wellhead', 'christmas tree', 'api 6a']

    if 'api_spec_16r' in fname or '16r' in fname:
        return 'drilling', ['marine drilling riser', 'riser coupling']

    if 'api_spec_12' in fname or 'spec_12' in fname:
        # API 12 series - tanks, vessels
        return 'structural', ['tank', 'vessel', 'api 12']

    if '2geo' in fname or 'api_2geo' in fname:
        return 'geotechnical', ['geotechnical', 'api 2geo', 'foundation']

    if '2td' in fname:
        return 'marine', ['tension leg platform', 'tlp', 'api 2td']

    if 'api_581' in fname or '581' in fname and 'rbi' in combined:
        return 'regulatory', ['risk-based inspection', 'rbi', 'api 581']

    if 'dnv_os_f101' in fname.replace('-','_').replace(' ','_') or 'os f101' in combined or 'os-f101' in combined:
        return 'pipeline', ['submarine pipeline', 'dnv os f101', 'pipeline design']

    if 'rp_f105' in fname or 'rp f105' in combined or 'f105' in fname:
        return 'pipeline', ['free spanning pipelines', 'dnv rp f105', 'viv']

    if 'rp_f401' in fname or 'rp f401' in combined or 'f401' in fname:
        return 'electrical', ['electrical power cable', 'dnv rp f401', 'cable']

    if 'rp_c203' in fname or 'rp c203' in combined or 'c203' in fname:
        return 'marine', ['fatigue design', 'dnv rp c203', 'offshore structure']

    if 'rp f103' in combined or 'f103' in fname:
        return 'cathodic-protection', ['cathodic protection', 'galvanic anodes', 'pipeline cp']

    if 'api_1104' in fname or 'api.1104' in fname or 'api 1104' in combined or '1104' in fname:
        return 'materials', ['welding pipelines', 'api 1104', 'weld']

    if 'api rp 2a' in combined or 'rp 2a' in combined or '2a_wsd' in fname or '2a wsd' in combined:
        return 'marine', ['fixed offshore platform', 'api rp 2a', 'jacket structure']

    if 'api 2p' in combined or '_2p' in fname or '/2p.' in ppath:
        return 'marine', ['mooring', 'api 2p', 'offshore platform']

    if 'api 6af' in combined or '6af' in fname:
        return 'drilling', ['wellhead', 'christmas tree', 'fire test']

    if 'api 11p' in combined or 'spec_11p' in fname or 'spec 11p' in combined:
        return 'production', ['pumping unit', 'artificial lift', 'api 11p']

    if 'api std 677' in combined or 'std_677' in fname or '677' in fname:
        return 'production', ['gear units', 'rotating equipment', 'api 677']

    if 'api 579' in combined or 'api_579' in fname or '579back' in fname or 'sect_09' in fname:
        return 'structural', ['fitness for service', 'api 579', 'structural assessment']

    if 'amjig' in combined:
        return 'drilling', ['drilling riser', 'amjig', 'riser guidelines']

    if 'dnv-standard2-7-1' in fname or '2-7-1' in fname or 'dnv standard 2-7-1' in combined:
        return 'installation', ['offshore containers', 'lifting', 'dnv 2-7-1']

    if 'dnv_rules_drilling' in fname or 'rules for classification' in combined and 'drilling' in combined:
        return 'drilling', ['classification', 'drilling unit', 'dnv rules']

    if 'dnv rp o401' in combined or 'rp o401' in combined:
        return 'marine', ['subsea systems', 'reliability', 'dnv rp o401']

    if 'abs_guide' in fname or 'abs001' in fname:
        return 'marine', ['abs guide', 'offshore structure', 'marine classification']

    if 'norsok' in combined:
        return 'regulatory', ['norsok', 'norwegian standard', 'offshore standard']

    if 'append' in fname and ('e.pdf' in fname or '_e.pdf' in fname or 'append_e' in fname):
        return 'structural', ['appendix', 'design standard', 'structural']

    if 'append' in fname and ('i.pdf' in fname or '_i.pdf' in fname or 'append_i' in fname):
        return 'structural', ['appendix', 'design standard', 'structural']

    if 'errata' in fname:
        # Errata - check which standard
        if 'api' in ppath:
            return 'regulatory', ['errata', 'api standard', 'correction']
        return 'regulatory', ['errata', 'standard correction', 'regulatory']

    if 'addendum' in fname:
        if 'api' in ppath:
            return 'regulatory', ['addendum', 'api standard', 'amendment']
        return 'regulatory', ['addendum', 'standard amendment', 'regulatory']

    if 'otc' in fname or 'offshore technology conference' in combined:
        # OTC papers - check topic
        if 'mooring' in combined or 'riser' in combined:
            return 'marine', ['otc paper', 'offshore technology', 'marine']
        if 'wind' in combined:
            return 'marine', ['otc paper', 'floating wind', 'marine renewable']
        if 'pipeline' in combined:
            return 'pipeline', ['otc paper', 'pipeline', 'offshore']
        if 'drilling' in combined or 'well' in combined:
            return 'drilling', ['otc paper', 'drilling', 'well']
        return 'marine', ['otc paper', 'offshore technology', 'marine']

    if 'abstract' in fname or 'copyright' in fname or 'transfer_of_copyright' in fname:
        return 'document-processing', ['copyright', 'abstract submission', 'document']

    if 'keynote' in fname:
        return 'marine', ['keynote', 'offshore conference', 'marine']

    if 'floating wind' in combined or 'wind turbine' in combined:
        return 'marine', ['floating wind turbine', 'marine renewable energy', 'offshore wind']

    # Now use keyword matching on combined text
    scores = {}
    for discipline, keywords in DISCIPLINE_RULES:
        score = 0
        found = []
        for kw in keywords:
            if kw in combined:
                score += 1
                found.append(kw)
        if score > 0:
            scores[discipline] = (score, found)

    if scores:
        best = max(scores.items(), key=lambda x: x[1][0])
        return best[0], best[1][1][:5]

    # Fallback based on file path
    if 'astm' in ppath:
        return 'materials', ['astm', 'materials standard']
    if 'api' in ppath:
        return 'regulatory', ['api', 'standard']
    if 'iso' in ppath:
        return 'regulatory', ['iso', 'standard']
    if 'dnv' in ppath:
        return 'regulatory', ['dnv', 'standard']
    if 'bsi' in ppath:
        return 'regulatory', ['bsi', 'british standard']

    return 'other', ['unclassified']


def extract_text(pdf_path: str) -> str:
    """Extract text from PDF using pdftotext, first 3 pages, max 4000 chars."""
    try:
        result = subprocess.run(
            ['pdftotext', '-f', '1', '-l', '3', pdf_path, '-'],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout[:4000]
        return text
    except Exception:
        return ''


def infer_org_from_path(path: str) -> str:
    """Infer organization from path."""
    p = path.lower()
    if '/api/' in p or 'api spec' in p or 'api rp' in p or 'api_spec' in p:
        return 'API'
    if '/astm/' in p:
        return 'ASTM'
    if '/dnv/' in p or 'dnv' in p:
        return 'DNV'
    if '/iso/' in p:
        return 'ISO'
    if '/bsi/' in p or 'bs_' in p or '/bsi_' in p:
        return 'BSI'
    if '/abs/' in p or 'abs_' in p:
        return 'ABS'
    if '/norsok/' in p or 'norsok' in p:
        return 'NORSOK'
    if '/mil/' in p or 'mil-' in p:
        return 'MIL'
    if '/onepetro/' in p:
        return 'OTC'
    return 'Unknown'


def generate_title_from_path(path: str, text: str) -> str:
    """Generate title from PDF text or filename."""
    # Try to extract title from first line of text
    if text and len(text) > 20:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:10]:
            if 20 < len(line) < 200 and not line.startswith('http'):
                # Skip page numbers, dates
                if not re.match(r'^\d+$', line) and not re.match(r'^\d{1,2}/\d{1,2}/\d{4}', line):
                    return line[:200]

    # Fall back to filename
    fname = os.path.basename(path)
    fname = os.path.splitext(fname)[0]
    fname = fname.replace('_', ' ').replace('-', ' ')
    return fname[:200]


def generate_summary(discipline: str, path: str, text: str, title: str) -> str:
    """Generate brief summary."""
    fname = os.path.basename(path)

    # Use text if available
    if text and len(text) > 100:
        # Find meaningful lines
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 30]
        if lines:
            # Pick first couple of content lines
            summary_parts = []
            for line in lines[:5]:
                if not re.match(r'^\d+$', line) and 'page' not in line.lower():
                    summary_parts.append(line)
                    if len(' '.join(summary_parts)) > 200:
                        break
            if summary_parts:
                summary = ' '.join(summary_parts)[:300]
                return summary

    # Fallback: use title + discipline description
    disc_descriptions = {
        'structural': 'structural engineering standard or technical document',
        'pipeline': 'pipeline design standard or technical reference',
        'cathodic-protection': 'cathodic protection standard or guideline',
        'marine': 'offshore marine structures standard or technical paper',
        'installation': 'marine installation standard or procedure',
        'drilling': 'drilling and well engineering standard or specification',
        'production': 'production systems standard or technical document',
        'materials': 'materials specification and testing standard',
        'regulatory': 'industry code, standard, or regulatory document',
        'energy-economics': 'energy economics and production document',
        'geotechnical': 'geotechnical engineering standard or guideline',
        'fire-safety': 'fire safety and explosion hazard document',
        'electrical': 'electrical systems and instrumentation standard',
        'document-processing': 'document processing and data management document',
        'other': 'engineering reference document',
    }
    desc = disc_descriptions.get(discipline, 'engineering document')
    return f'{title[:150] if title else fname}: {desc}.'


def process_doc(doc: dict) -> dict:
    """Process a single document and return output JSON dict."""
    sha = doc['sha']
    path = doc['path']
    source = doc.get('source', 'ace_standards')
    org = doc.get('org', '') or infer_org_from_path(path)
    title = doc.get('title', '') or ''

    # Check if file exists
    if not os.path.exists(path):
        return {
            'sha': sha,
            'path': path,
            'source': source,
            'org': org,
            'title': title or os.path.basename(path),
            'summary': None,
            'discipline': 'other',
            'keywords': ['file not found'],
            'extraction_method': 'failed',
            'extracted_at': TIMESTAMP,
        }

    # Extract text
    text = ''
    extraction_method = 'pdftotext'
    ext = os.path.splitext(path)[1].lower()

    if ext in ('.pdf', '.PDF'):
        text = extract_text(path)
        if len(text) < 50:
            extraction_method = 'failed'
            text = ''
    else:
        # Non-PDF (docx, xlsx, etc.) - skip text extraction
        extraction_method = 'failed'
        text = ''

    # Generate title if missing
    if not title:
        title = generate_title_from_path(path, text)

    # Classify
    discipline, keywords = classify_by_path_and_text(path, text, title)

    # Generate summary
    if extraction_method == 'failed':
        summary = None
    else:
        summary = generate_summary(discipline, path, text, title)

    return {
        'sha': sha,
        'path': path,
        'source': source,
        'org': org,
        'title': title,
        'summary': summary,
        'discipline': discipline,
        'keywords': keywords,
        'extraction_method': extraction_method,
        'extracted_at': TIMESTAMP,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(SHARD_FILE) as f:
        data = json.load(f)

    docs = data['docs']
    pending = []

    for d in docs:
        sha = d['sha']
        # Strip sha256: prefix for filename
        sha_hex = sha.replace('sha256:', '')
        out_path = os.path.join(OUT_DIR, sha_hex + '.json')
        if os.path.exists(out_path):
            try:
                with open(out_path) as f2:
                    existing = json.load(f2)
                if 'discipline' in existing:
                    continue
            except Exception:
                pass
        pending.append(d)

    print(f'Pending: {len(pending)} / {len(docs)}', flush=True)

    processed = 0
    skipped = len(docs) - len(pending)
    failed = 0

    for i, doc in enumerate(pending):
        sha = doc['sha']
        sha_hex = sha.replace('sha256:', '')
        out_path = os.path.join(OUT_DIR, sha_hex + '.json')

        try:
            result = process_doc(doc)
            with open(out_path, 'w') as f:
                json.dump(result, f, indent=2)
            processed += 1
            if result['extraction_method'] == 'failed':
                failed += 1

            if (i + 1) % 100 == 0:
                print(f'Progress: {i+1}/{len(pending)} processed={processed} failed={failed}', flush=True)

        except Exception as e:
            print(f'ERROR processing {sha}: {e}', flush=True)
            failed += 1

    print(f'\nace-shard-04 complete: processed={processed}, skipped={skipped}, failed={failed}')


if __name__ == '__main__':
    main()
