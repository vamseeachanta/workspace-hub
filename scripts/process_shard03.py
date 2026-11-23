#!/usr/bin/env python3
"""
Batch processor for ace-shard-03.json
Extracts text from PDFs, classifies by engineering discipline, writes output JSON.
"""
import json
import os
import subprocess
import re
import sys
from datetime import datetime

SHARD_PATH = '/mnt/local-analysis/workspace-hub/data/document-index/shards/ace-shard-03.json'
OUT_DIR = '/mnt/local-analysis/workspace-hub/data/document-index/summaries'
TIMESTAMP = '2026-02-24T00:00:00Z'

os.makedirs(OUT_DIR, exist_ok=True)

def extract_text(pdf_path):
    """Extract first 3 pages text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', '-f', '1', '-l', '3', pdf_path, '-'],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout[:4000]
        return text
    except Exception:
        return ''

def classify(path, title, text):
    """Classify document into discipline based on path, title, and extracted text."""
    path_lower = path.lower()
    title_lower = (title or '').lower()
    text_lower = text.lower()
    combined = path_lower + ' ' + title_lower + ' ' + text_lower

    # Pipeline
    pipeline_keywords = [
        'pipeline', 'pipe line', 'subsea pipe', 'pressure containment',
        'on-bottom stability', 'flowline', 'flow line', 'riser pipe',
        'flexible pipe', 'umbilical', 'pipe stress', 'buried pipeline',
        'line pipe', 'coiled line pipe', 'piping inspection',
        'api 1104', 'api 1111', 'api spec 5l', 'api std 1102',
        'pipeline crossing', 'pipeline integrity', 'pipeline design',
        'unbonded flexible', 'api spec 17j', 'api 570'
    ]

    # Structural
    structural_keywords = [
        'structural', 'stress analysis', 'finite element', 'fea', 'fem',
        'vessel design', 'pressure vessel', 'tank design', 'steel tank',
        'frame analysis', 'beam', 'column design', 'buckling',
        'cylindrical shell', 'stability design', 'welded steel tank',
        'api 650', 'api 620', 'api bul 2u', 'asme', 'fitness-for-service',
        'api 579', 'structural integrity', 'fatigue analysis',
        'offshore platform', 'jacket', 'topside', 'topsides',
        'fixed platform', 'api rp 2a', 'api 2a'
    ]

    # Marine
    marine_keywords = [
        'offshore structure', 'wave load', 'hydrodynamic', 'mooring',
        'riser', 'fpso', 'floating production', 'tension leg platform',
        'tlp', 'spar', 'semi-submersible', 'vessel motion', 'sea state',
        'significant wave height', 'hurricane', 'storm condition',
        'api rp 2sk', 'api rp 2t', 'api 2t', 'api 2sk',
        'marine riser', 'drilling riser', 'api spec 2r',
        'mooring system', 'anchor', 'chain', 'taut leg mooring'
    ]

    # Cathodic Protection
    cp_keywords = [
        'cathodic protection', 'sacrificial anode', 'impressed current',
        'corrosion protection', 'anode', 'cathodic', 'galvanic',
        'api rp 651', 'api 651', 'corrosion of oil', 'corrosion prevention',
        'api vt-2', 'vt-2', 'cp system', 'pipeline corrosion', 'coating',
        'corrosion of oil- and gas', 'corrosion_of_oil'
    ]

    # Drilling
    drilling_keywords = [
        'drilling', 'wellbore', 'casing design', 'bop', 'blow out preventer',
        'well control', 'completion', 'drill stem', 'drill string',
        'hoisting equipment', 'api spec 8', 'api rp 7g', 'casing and tubing',
        'api spec 5ct', 'api 5ct', 'wellhead', 'christmas tree',
        'api spec 6a', 'api spec 8c', 'drill pipe', 'rotary drilling',
        'api 16a', 'bop equipment', 'well integrity', 'workover riser',
        'completion riser', 'api rp 17g'
    ]

    # Production
    production_keywords = [
        'production system', 'artificial lift', 'esp', 'electric submersible',
        'well surveillance', 'production facility', 'separator design',
        'production safety', 'api rp 14c', 'api 14c', 'process safety',
        'production platform', 'surface production'
    ]

    # Materials
    materials_keywords = [
        'metallurgy', 'ndt', 'non-destructive', 'fracture mechanics',
        'welding', 'material properties', 'weld', 'heat affected zone',
        'corrosion', 'fatigue crack', 'stress corrosion',
        'api rp 2201', 'hot tapping', 'weld procedure',
        'material specification', 'alloy', 'hardness'
    ]

    # Regulatory / Standards
    regulatory_keywords = [
        'recommended practice', 'standard', 'specification', 'code',
        'compliance', 'safety management', 'regulation', 'regulatory',
        'inspection', 'certification', 'api rp 75', 'api q1',
        'quality management', 'safety case', 'prescriptive',
        'isomerism', 'title page', 'foreword', 'scope',
        'astm', 'iso', 'dnv', 'abs', 'bureau veritas',
        'pressure-relieving', 'api rp 576', 'relief valve',
        'rotary positive displacement', 'compressor standard',
        'centrifugal fan', 'gear unit', 'centrifugal fan'
    ]

    # Installation
    installation_keywords = [
        'installation', 'marine installation', 'lifting', 'load-out',
        'transportation', 'vessel operation', 'heavy lift',
        'offshore installation', 'pipe laying', 'j-lay', 's-lay',
        'load out', 'offshore construction'
    ]

    # Geotechnical
    geotechnical_keywords = [
        'soil mechanics', 'foundation', 'pile design', 'seabed',
        'geotechnical', 'p-y', 'lateral load', 'soil investigation',
        'api rp 2geo', 'api 2geo', 'geotechnical design',
        'soil properties', 'soil strength', 'pile capacity',
        'clay', 'sand bearing', 'bearing capacity'
    ]

    # Fire Safety
    fire_safety_keywords = [
        'fire and explosion', 'hazop', 'hazardous area',
        'fire safety', 'explosion risk', 'fire protection',
        'fire detection', 'area classification', 'atex'
    ]

    # Electrical
    electrical_keywords = [
        'electrical system', 'power system', 'instrumentation',
        'electrical design', 'power distribution', 'control system',
        'electrical installation', 'intrinsically safe'
    ]

    # Document processing
    doc_proc_keywords = [
        'software', 'data processing', 'computing', 'algorithm',
        'database', 'information system', 'document management',
        'oasis', 'abstract submission', 'conference paper', 'otc paper',
        'online abstract', 'submission system', 'notification'
    ]

    # Energy economics
    energy_econ_keywords = [
        'energy market', 'production forecast', 'economic', 'economics',
        'oil price', 'gas price', 'reserve estimation', 'field development',
        'investment', 'cost analysis', 'financial'
    ]

    # Score each discipline
    scores = {}

    def score(keywords, discipline):
        count = sum(1 for kw in keywords if kw in combined)
        if count > 0:
            scores[discipline] = count

    score(pipeline_keywords, 'pipeline')
    score(structural_keywords, 'structural')
    score(marine_keywords, 'marine')
    score(cp_keywords, 'cathodic-protection')
    score(drilling_keywords, 'drilling')
    score(production_keywords, 'production')
    score(materials_keywords, 'materials')
    score(regulatory_keywords, 'regulatory')
    score(installation_keywords, 'installation')
    score(geotechnical_keywords, 'geotechnical')
    score(fire_safety_keywords, 'fire-safety')
    score(electrical_keywords, 'electrical')
    score(doc_proc_keywords, 'document-processing')
    score(energy_econ_keywords, 'energy-economics')

    if not scores:
        return 'other'

    return max(scores, key=scores.get)

def infer_org(path, text):
    """Infer organization from path or text."""
    path_lower = path.lower()
    if '/api/' in path_lower:
        return 'API'
    if '/dnv/' in path_lower or 'det norske' in text.lower() or 'dnvgl' in text.lower():
        return 'DNV'
    if '/astm/' in path_lower:
        return 'ASTM'
    if '/iso/' in path_lower:
        return 'ISO'
    if '/asme/' in path_lower:
        return 'ASME'
    if '/abs/' in path_lower:
        return 'ABS'
    if '/onepetro/' in path_lower or 'otc' in path_lower:
        return 'OTC'
    if '/norsok/' in path_lower:
        return 'NORSOK'
    # Check text
    text_l = text[:500].lower()
    if 'american petroleum institute' in text_l:
        return 'API'
    if 'det norske veritas' in text_l or 'dnv gl' in text_l:
        return 'DNV'
    if 'astm international' in text_l or 'american society for testing' in text_l:
        return 'ASTM'
    if 'american society of mechanical' in text_l:
        return 'ASME'
    return ''

def infer_title(path, text):
    """Infer document title from path filename or extracted text."""
    # Try filename first as it's usually more reliable for standards docs
    fname = os.path.basename(path)
    fname = os.path.splitext(fname)[0]
    # Clean up URL encoding and underscores
    fname_clean = fname.replace('%20', ' ').replace('_', ' ').replace('%2C', ',')
    # If filename looks like a real title (not just a code), use it
    if len(fname_clean) > 15 and not re.match(r'^[A-Z0-9\s\-\.]+$', fname_clean):
        return fname_clean[:200]

    # Try from text - skip IHS/copyright boilerplate lines
    skip_patterns = [
        r'^[-`~\.,]+$',  # lines of dashes/backticks (IHS boilerplate)
        r'^\d+$',         # page numbers
        r'^Table\s',      # table headers
        r'^Figure\s',     # figure captions
        r'copyright',
        r'all rights reserved',
        r'provided by ihs',
        r'licensee=',
        r'no reproduction',
    ]
    if text and len(text.strip()) > 10:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:15]:
            if len(line) > 10 and len(line) < 200:
                skip = False
                for pat in skip_patterns:
                    if re.search(pat, line, re.IGNORECASE):
                        skip = True
                        break
                if not skip:
                    return line[:200]

    return fname_clean[:200]

def generate_summary(path, title, text, discipline):
    """Generate a 1-2 sentence summary."""
    fname = os.path.basename(path)
    org_part = ''
    if '/API/' in path:
        org_part = 'API '
    elif '/ASTM/' in path:
        org_part = 'ASTM '
    elif '/DNV/' in path:
        org_part = 'DNV '

    # Use text hints
    text_preview = text[:800] if text else ''

    # Generate based on discipline and title
    if discipline == 'drilling':
        return f"{org_part}document covering drilling and production equipment specifications. Provides technical requirements for wellbore equipment, hoisting systems, and related drilling operations."
    elif discipline == 'pipeline':
        return f"{org_part}document covering pipeline design, specifications, or inspection requirements. Addresses pressure containment, material specifications, and pipeline integrity."
    elif discipline == 'structural':
        return f"{org_part}document covering structural engineering requirements for offshore or onshore structures. Includes design criteria, load analysis, and structural integrity assessment."
    elif discipline == 'marine':
        return f"{org_part}document covering offshore marine structures, floating systems, or mooring design. Addresses environmental loading, vessel motions, and offshore installation design."
    elif discipline == 'cathodic-protection':
        return f"{org_part}document covering corrosion protection systems for oil and gas equipment. Includes cathodic protection design, anode specifications, and corrosion prevention practices."
    elif discipline == 'materials':
        return f"{org_part}document covering material specifications, welding procedures, or non-destructive testing. Addresses metallurgical properties and material qualification requirements."
    elif discipline == 'regulatory':
        return f"{org_part}standard or recommended practice covering regulatory requirements, safety management, or inspection codes for oil and gas facilities."
    elif discipline == 'geotechnical':
        return f"{org_part}document covering geotechnical engineering for offshore foundations and seabed conditions. Includes pile design, soil characterization, and foundation analysis."
    elif discipline == 'production':
        return f"{org_part}document covering production systems, surface facilities, or well completion equipment. Addresses production safety systems and process equipment requirements."
    elif discipline == 'installation':
        return f"{org_part}document covering offshore installation, marine transportation, or construction operations. Includes lifting, load-out, and vessel operation requirements."
    elif discipline == 'fire-safety':
        return f"{org_part}document covering fire and explosion safety, hazardous area classification, or HAZOP methodology for oil and gas facilities."
    elif discipline == 'electrical':
        return f"{org_part}document covering electrical systems, instrumentation, or power distribution for oil and gas facilities."
    elif discipline == 'document-processing':
        return f"Document related to software tools, conference abstracts, or data processing for engineering applications in the oil and gas industry."
    elif discipline == 'energy-economics':
        return f"Document covering energy economics, production forecasting, or field development economics for oil and gas projects."
    else:
        return f"{org_part}technical document from the oil and gas industry. Content covers engineering standards, specifications, or technical guidance."

def extract_keywords(text, path, discipline):
    """Extract relevant keywords from text and path."""
    keywords = []
    path_lower = path.lower()
    text_lower = (text or '').lower()

    # Add discipline-specific keywords
    kw_map = {
        'pipeline': ['pipeline', 'flexible pipe', 'riser', 'flowline', 'subsea'],
        'structural': ['structural', 'stress analysis', 'FEA', 'vessel', 'tank'],
        'marine': ['offshore', 'mooring', 'FPSO', 'wave loads', 'hydrodynamics'],
        'cathodic-protection': ['cathodic protection', 'anode', 'corrosion', 'galvanic'],
        'drilling': ['drilling', 'casing', 'wellbore', 'BOP', 'hoisting'],
        'production': ['production', 'separator', 'artificial lift', 'ESP', 'wellhead'],
        'materials': ['welding', 'NDT', 'metallurgy', 'fracture mechanics', 'corrosion'],
        'regulatory': ['standards', 'inspection', 'compliance', 'recommended practice'],
        'installation': ['installation', 'lifting', 'marine operations', 'load-out'],
        'geotechnical': ['geotechnical', 'pile', 'soil', 'foundation', 'seabed'],
        'fire-safety': ['fire safety', 'explosion', 'HAZOP', 'hazardous area'],
        'electrical': ['electrical', 'instrumentation', 'power systems'],
        'document-processing': ['software', 'data processing', 'abstract', 'conference'],
        'energy-economics': ['economics', 'forecasting', 'production', 'markets'],
        'other': ['oil and gas', 'engineering', 'technical']
    }

    keywords = kw_map.get(discipline, ['oil and gas', 'engineering'])

    # Add org-specific keywords
    if '/API/' in path:
        keywords.append('API')
    elif '/ASTM/' in path:
        keywords.append('ASTM')
    elif '/DNV/' in path:
        keywords.append('DNV')

    # Add specific API doc identifiers from path
    api_match = re.search(r'API[_\s]?(RP|SPEC|STD|BUL)?[_\s]?(\d+\w*)', path, re.IGNORECASE)
    if api_match:
        keywords.append(f"API {api_match.group(0)[:20]}")

    return list(dict.fromkeys(keywords))[:8]  # deduplicate, max 8


def process_doc(doc):
    sha = doc['sha']
    path = doc['path']
    source = doc.get('source', 'ace_standards')
    org = doc.get('org', '')
    title = doc.get('title', '')

    out_path = os.path.join(OUT_DIR, sha + '.json')

    # Check skip
    if os.path.exists(out_path):
        try:
            with open(out_path) as f:
                existing = json.load(f)
            if 'discipline' in existing:
                return 'skipped'
        except Exception:
            pass

    # Only process PDFs (skip docx, doc, xls, etc.)
    ext = os.path.splitext(path)[1].lower()
    if ext not in ['.pdf', '.PDF']:
        # Write a basic record for non-PDFs
        if not org:
            org = infer_org(path, '')
        result = {
            'sha': sha,
            'path': path,
            'source': source,
            'org': org,
            'title': title or os.path.splitext(os.path.basename(path))[0].replace('_', ' ')[:200],
            'summary': None,
            'discipline': 'other',
            'keywords': ['non-pdf', ext.lstrip('.')],
            'extraction_method': 'failed',
            'extracted_at': TIMESTAMP
        }
        with open(out_path, 'w') as f:
            json.dump(result, f, indent=2)
        return 'processed'

    # Extract text
    text = extract_text(path)

    if len(text.strip()) < 50:
        method = 'failed'
        discipline = 'other'
        summary = None
        kws = ['extraction-failed']
        if not org:
            org = infer_org(path, '')
        if not title:
            title = os.path.splitext(os.path.basename(path))[0].replace('_', ' ')[:200]
    else:
        method = 'pdftotext'
        if not org:
            org = infer_org(path, text)
        if not title:
            title = infer_title(path, text)
        discipline = classify(path, title, text)
        summary = generate_summary(path, title, text, discipline)
        kws = extract_keywords(text, path, discipline)

    result = {
        'sha': sha,
        'path': path,
        'source': source,
        'org': org,
        'title': title,
        'summary': summary,
        'discipline': discipline,
        'keywords': kws,
        'extraction_method': method,
        'extracted_at': TIMESTAMP
    }

    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    return 'processed'


def main():
    with open(SHARD_PATH) as f:
        data = json.load(f)

    docs = data['docs']
    total = len(docs)
    processed = 0
    skipped = 0
    failed = 0

    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else total

    print(f"Processing docs {start_idx} to {end_idx} of {total}", flush=True)

    for i, doc in enumerate(docs[start_idx:end_idx], start=start_idx):
        try:
            result = process_doc(doc)
            if result == 'skipped':
                skipped += 1
            else:
                processed += 1
        except Exception as e:
            failed += 1
            print(f"ERROR doc {i} {doc.get('sha','?')}: {e}", flush=True)

        if (i + 1) % 100 == 0:
            print(f"Progress: {i+1}/{end_idx} | processed={processed} skipped={skipped} failed={failed}", flush=True)

    print(f"\nDone: processed={processed}, skipped={skipped}, failed={failed}", flush=True)


if __name__ == '__main__':
    main()
