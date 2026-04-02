#!/usr/bin/env python3
"""
Curate worked examples from data/doc-intelligence/worked_examples.jsonl
into TDD test fixture YAML files organized by domain.

Issue: #1294 (WRK-1370)

The worked_examples.jsonl contains two schemas:
  Schema A: Text-based entries with raw OCR text, source doc/page, domain
  Schema B: Structured entries with expected_value, output_unit, input_count, source_book

This script:
  1. Reads all entries from worked_examples.jsonl
  2. Also reads EN400 worked examples from en400-worked-examples.yaml
  3. Scores each entry for quality as a test vector
  4. Maps source books to engineering domains
  5. Filters entries meeting quality thresholds
  6. Writes curated fixtures to tests/fixtures/test_vectors/<domain>/

Quality criteria for test vectors:
  - Must have a clear expected output value
  - Must have identifiable input parameters (input_count >= 2)
  - Must have a calculation method reference (title or section number)
  - Must map to a recognized domain
"""

import json
import re
import sys
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone


# ── Domain mapping ──────────────────────────────────────────────────────────

# Map source books to our target domain taxonomy
BOOK_TO_DOMAIN = {
    # Marine / Naval Architecture
    "DNV-RP-H103-Marine-Operations-2010": "marine",
    "DNV-RP-H103-Marine-Operations-2010.pdf": "marine",
    "Principles-of-Naval-Architecture-SecondRevision-Vol1": "marine",
    "Principles-of-Naval-Architecture-SecondRevision-Vol1.pdf": "marine",
    "Principles-of-Naval-Architecture-SecondRevision-Vol2-Resistance-Propulsion": "marine",
    "Principles-of-Naval-Architecture-SecondRevision-Vol2-Resistance-Propulsion.pdf": "marine",
    "Principles-of-Naval-Architecture-SecondRevision-Vol3-Motions-Controllability": "marine",
    "Principles-of-Naval-Architecture-SecondRevision-Vol3-Motions-Controllability.pdf": "marine",
    "Principles-of-Naval-Architecture-Vol2-Resistance-Propulsion-Vibration": "marine",
    "Principles-of-Naval-Architecture-Vol2-Resistance-Propulsion-Vibration.pdf": "marine",
    "Introduction-to-Naval-Architecture-Tupper-1996": "marine",
    "Introduction-to-Naval-Architecture-Tupper-1996.pdf": "marine",
    "Introduction-to-Naval-Architecture-Comstock-1942": "marine",
    "Introduction-to-Naval-Architecture-Comstock-1942.pdf": "marine",
    "Theoretical-Naval-Architecture-Attwood-1899": "marine",
    "Theoretical-Naval-Architecture-Attwood-1899.pdf": "marine",
    "Ship-Hydrostatics-and-Stability-Biran": "marine",
    "Ship-Hydrostatics-and-Stability-Biran.pdf": "marine",
    "Ship-Hydrostatics-and-Stability-2ndEd": "marine",
    "USNA-EN400-Principles-Ship-Performance-2020": "marine",
    "USNA-EN400-Principles-Ship-Performance-2020.pdf": "marine",
    "Marine-Hydrodynamics-Newman-2018": "marine",
    "Marine-Hydrodynamics-Newman-2018.pdf": "marine",
    "Practical-Ship-Hydrodynamics-Bertram-2000": "marine",
    "Practical-Ship-Hydrodynamics-Bertram-2000.pdf": "marine",
    "Design-Principles-Ships-Marine-Structures": "marine",
    "Warship-2011-Naval-Submarines-UUVs": "marine",
    "Warship-2011-Naval-Submarines-UUVs.pdf": "marine",
    "Warship-Naval-Submarines-9": "marine",
    "Warship-Naval-Submarines-9.pdf": "marine",
    "UK-MCA-MSIS43-Intact-Stability-Guidance": "marine",
    "UK-MCA-MSIS43-Intact-Stability-Guidance.pdf": "marine",
    "Offshore-Hydromechanics-2001": "marine",
    "Offshore-Hydromechanics-2001.pdf": "marine",

    # Structural
    "Ship-Structural-Analysis-Design-Hughes-Paik": "structural",
    "Ship-Structural-Analysis-Design-Hughes-Paik.pdf": "structural",
    "Panel_Member_copy_of_SNAME_5-5_and_5-5A_Rev3": "structural",
    "Panel_Member_copy_of_SNAME_5-5_and_5-5A_Rev3.pdf": "structural",
    "Handbook-Offshore-Engineering-Chakrabarti-2005": "structural",

    # Pipeline / Fluid dynamics
    "Fluid-Dynamic-Drag-Hoerner-1965": "pipeline",
    "Fluid-Dynamic-Drag-Hoerner-1965.pdf": "pipeline",

    # Environmental loads
    "DNV-RP-C205-Environmental-Conditions-Loads-2007": "marine",
}

# Sub-topic classification based on content keywords
TOPIC_KEYWORDS = {
    "hydrostatics": ["buoyancy", "draft", "displacement", "waterplane", "metacent",
                      "freeboard", "tonnage", "archimedes", "hydrostatic"],
    "stability": ["stability", "righting", "heel", "trim", "gm", "metacentric",
                   "inclining", "capsiz", "keel", "bilge"],
    "resistance": ["resistance", "drag", "friction", "wave-making", "reynolds",
                   "froude", "hull form", "wake", "propulsion"],
    "structural": ["stress", "moment", "shear", "bending", "section modulus",
                   "buckling", "hull girder", "plate", "stiffener", "weld"],
    "dynamics": ["motion", "wave", "response", "rao", "damping", "natural period",
                 "oscillat", "heave", "pitch", "roll", "sloshing"],
    "lifting": ["lifting", "crane", "cable", "hoist", "rigging", "lift-off",
                "sling", "lowering"],
}

# Known clean output units (used for quality filtering)
CLEAN_UNITS = {
    "m", "m2", "m3", "m4", "m^4", "mm", "cm",
    "ft", "ft2", "ft3", "ft4",
    "kg", "kg/m3", "ton", "tonne", "LT", "lb", "slug",
    "N", "kN", "MN", "kip", "MNm",
    "Pa", "kPa", "MPa", "MN/m2", "psi", "ksi", "bar",
    "m/s", "knots", "knot",
    "degrees", "deg", "rad", "rad/s",
    "HP", "kW",
    "cubic inches",
}


def load_jsonl(path):
    """Load entries from worked_examples.jsonl, separating by schema."""
    schema_a = []  # text-based
    schema_b = []  # structured with expected_value

    with open(path) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            obj["_line_number"] = i + 1

            if "expected_value" in obj:
                schema_b.append(obj)
            elif "text" in obj and obj.get("text", "").strip():
                schema_a.append(obj)

    return schema_a, schema_b


def load_en400_examples(path):
    """Load EN400 worked examples from YAML."""
    if not Path(path).exists():
        return []
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("examples", [])


def resolve_domain(entry):
    """Determine the domain for an entry."""
    # Try source_book first (Schema B)
    source_book = entry.get("source_book", "")
    if source_book in BOOK_TO_DOMAIN:
        return BOOK_TO_DOMAIN[source_book]

    # Try source.document (Schema A)
    source = entry.get("source", {})
    doc = source.get("document", entry.get("manifest", ""))
    if doc in BOOK_TO_DOMAIN:
        return BOOK_TO_DOMAIN[doc]

    # Try domain field
    domain = entry.get("domain", "")
    if domain == "naval-architecture":
        return "marine"

    return None


def resolve_topic(entry):
    """Determine sub-topic from content."""
    text = entry.get("text", "") + " " + entry.get("title", "")
    tl = text.lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in tl:
                return topic
    return "general"


def clean_output_unit(unit_str):
    """Normalize and validate output unit string."""
    if not unit_str:
        return None
    unit = unit_str.strip()
    # Remove trailing noise
    unit = re.sub(r'\n.*', '', unit)  # Drop anything after newline
    unit = unit.strip()
    if unit in CLEAN_UNITS:
        return unit
    # Try common normalizations
    norm_map = {
        "foot": "ft", "feet": "ft",
        "pounds per inch of weld": None,  # too noisy
        "tonsnearly": "ton",
        "ms": "m/s",
    }
    return norm_map.get(unit, None)


def score_schema_b(entry):
    """Score a Schema B entry for test vector quality (0-100)."""
    score = 0

    # Must have expected_value
    ev = entry.get("expected_value")
    if ev is None:
        return 0
    score += 20

    # Numeric expected value (not a string or weird value)
    if isinstance(ev, (int, float)):
        score += 10
    else:
        return 0  # Non-numeric expected values are unreliable

    # Clean output unit
    raw_unit = entry.get("output_unit", "")
    clean_unit = clean_output_unit(raw_unit)
    if clean_unit:
        score += 20
    elif raw_unit.strip():
        score += 5  # Has some unit but it's noisy

    # Input count (more inputs = more complex, but we need at least 2)
    ic = entry.get("input_count", 0)
    if ic >= 2:
        score += 10
    if ic >= 5:
        score += 5
    if ic >= 10:
        score += 5

    # Has a meaningful title
    title = entry.get("title", "")
    if len(title) > 10:
        score += 10

    # Has example number
    num = entry.get("number", "")
    if num:
        score += 5

    # Domain can be resolved
    domain = resolve_domain(entry)
    if domain:
        score += 10

    # Source book is known
    sb = entry.get("source_book", "")
    if sb:
        score += 5

    return score


def score_schema_a(entry):
    """Score a Schema A (text-based) entry for test vector quality."""
    text = entry.get("text", "")
    tl = text.lower()
    score = 0

    # Explicit worked example markers
    if "example" in tl:
        score += 10
    if "worked example" in tl:
        score += 10
    if "solution" in tl:
        score += 5
    if "calculate" in tl:
        score += 5
    if "given" in tl and "find" in tl:
        score += 10

    # Named parameters with values and engineering units
    params = re.findall(
        r'(\w+)\s*=\s*([\d.]+)\s*'
        r'(m|kg|kN|MPa|mm|N|m/s|rad|deg|Pa|bar|psi|kPa|ft|lb|slug|ton|knot|m2|m3|ft2|ft3)',
        text
    )
    score += min(len(params) * 3, 30)

    # Equations with numeric results
    equations = re.findall(r'=\s*[\d.]+', text)
    score += min(len(equations) * 2, 20)

    # Domain resolution
    if resolve_domain(entry):
        score += 10

    return score


def extract_params_from_text(text):
    """Extract named parameters with values and units from text."""
    params = re.findall(
        r'(\w+)\s*=\s*([\d.]+)\s*'
        r'(m|kg|kN|MPa|mm|N|m/s|rad|deg|Pa|bar|psi|kPa|ft|lb|slug|ton|knots?|m2|m3|m4|ft2|ft3|ft4)',
        text
    )
    result = {}
    for name, value, unit in params:
        try:
            v = float(value)
            result[name] = {"value": v, "unit": unit}
        except ValueError:
            pass
    return result


def build_fixture_entry_schema_b(entry, idx):
    """Build a YAML fixture entry from a Schema B record."""
    ev = entry.get("expected_value")
    raw_unit = entry.get("output_unit", "")
    clean_unit = clean_output_unit(raw_unit) or raw_unit.strip()

    source_book = entry.get("source_book", "unknown")
    number = entry.get("number", "?")
    title = entry.get("title", "").strip()
    # Truncate long titles
    if len(title) > 120:
        title = title[:117] + "..."

    fixture = {
        "id": f"WE-B-{idx:04d}",
        "source": {
            "book": source_book,
            "example_number": str(number),
            "extraction": "deep",
        },
        "description": title,
        "domain": resolve_domain(entry),
        "topic": resolve_topic(entry),
        "expected_output": {
            "value": ev,
        },
        "input_count": entry.get("input_count", 0),
        "quality_score": score_schema_b(entry),
    }

    if clean_unit:
        fixture["expected_output"]["unit"] = clean_unit

    return fixture


def build_fixture_entry_schema_a(entry, idx):
    """Build a YAML fixture entry from a Schema A (text-based) record."""
    text = entry.get("text", "")
    source = entry.get("source", {})
    doc = source.get("document", entry.get("manifest", "unknown"))
    page = source.get("page", None)

    # Extract parameters
    params = extract_params_from_text(text)

    # Extract equations with results
    equations = re.findall(r'(\w[\w\s]*?)\s*=\s*([\d.]+)\s*(\w*)', text)
    results = []
    for name, val, unit in equations[:5]:  # Top 5 results
        name = name.strip()
        if len(name) > 30:
            continue
        try:
            results.append({"name": name, "value": float(val), "unit": unit.strip()})
        except ValueError:
            pass

    # Truncate description from text
    desc_match = re.search(r'(?:example|calculate|find|given)[:\s]+(.*?)(?:\n|$)', text.lower())
    desc = desc_match.group(1)[:120] if desc_match else text[:120].replace('\n', ' ')

    fixture = {
        "id": f"WE-A-{idx:04d}",
        "source": {
            "document": doc,
            "page": page,
        },
        "description": desc.strip(),
        "domain": resolve_domain(entry),
        "topic": resolve_topic(entry),
        "extracted_parameters": params if params else None,
        "extracted_results": results if results else None,
        "quality_score": score_schema_a(entry),
        "raw_text_length": len(text),
    }

    # Remove None values
    fixture = {k: v for k, v in fixture.items() if v is not None}

    return fixture


def build_fixture_entry_en400(entry, idx):
    """Build a YAML fixture entry from EN400 worked example."""
    fixture = {
        "id": entry.get("id", f"EN400-{idx:04d}"),
        "source": {
            "book": "USNA-EN400-Principles-Ship-Performance-2020",
            "example_number": entry.get("example_number", str(idx)),
            "chapter": entry.get("chapter"),
            "page": entry.get("page"),
        },
        "description": entry.get("raw_text", "")[:120].replace('\n', ' ').strip(),
        "domain": "marine",
        "topic": entry.get("topic", "general"),
        "extracted_values": entry.get("extracted_values", []),
        "quality_score": 75,  # EN400 examples are pre-curated
    }
    return fixture


def write_domain_fixture(domain, entries, output_dir):
    """Write fixture YAML for a domain."""
    domain_dir = output_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    # Sort by quality score descending
    entries.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

    fixture_data = {
        "metadata": {
            "domain": domain,
            "generated_by": "scripts/curate_worked_examples.py",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "issue": "#1294 (WRK-1370)",
            "total_vectors": len(entries),
            "source": "data/doc-intelligence/worked_examples.jsonl",
        },
        "test_vectors": entries,
    }

    filepath = domain_dir / "worked_examples.yaml"
    with open(filepath, "w") as f:
        yaml.dump(fixture_data, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True, width=120)

    return filepath


def deduplicate_schema_b(entries):
    """Remove duplicate Schema B entries, keeping highest-quality version."""
    seen = {}
    for entry in entries:
        key = (entry.get("source_book", ""), entry.get("number", ""))
        score = score_schema_b(entry)
        if key not in seen or score > seen[key][0]:
            seen[key] = (score, entry)
    return [v[1] for v in seen.values()]


def assign_quality_tier(score, schema):
    """Assign a quality tier label based on score.
    
    Tier 1 (gold):   Highest quality - suitable as regression test vectors
    Tier 2 (silver): Good quality - suitable as validation examples  
    Tier 3 (bronze): Acceptable - suitable as reference/documentation
    """
    if schema == "B":
        if score >= 80:
            return "gold"
        elif score >= 60:
            return "silver"
        else:
            return "bronze"
    elif schema == "A":
        if score >= 40:
            return "gold"
        elif score >= 30:
            return "silver"
        else:
            return "bronze"
    return "bronze"


def main():
    base_dir = Path(__file__).resolve().parent.parent
    jsonl_path = base_dir / "data" / "doc-intelligence" / "worked_examples.jsonl"
    en400_path = base_dir / "data" / "doc-intelligence" / "en400-worked-examples.yaml"
    output_dir = base_dir / "tests" / "fixtures" / "test_vectors"

    print(f"Reading {jsonl_path}...")
    schema_a, schema_b = load_jsonl(jsonl_path)
    print(f"  Schema A (text-based): {len(schema_a)} entries")
    print(f"  Schema B (structured): {len(schema_b)} entries")

    print(f"\nReading {en400_path}...")
    en400_examples = load_en400_examples(en400_path)
    print(f"  EN400 examples: {len(en400_examples)} entries")

    # ── Deduplicate Schema B ─────────────────────────────────────────────
    schema_b_deduped = deduplicate_schema_b(schema_b)
    print(f"\nSchema B after dedup: {len(schema_b_deduped)}/{len(schema_b)} unique entries")

    # ── Score and filter Schema B entries ────────────────────────────────
    SCHEMA_B_THRESHOLD = 55  # Must have expected_value + at least some quality signals
    scored_b = []
    rejected_b_score = 0
    for i, entry in enumerate(schema_b_deduped):
        score = score_schema_b(entry)
        if score >= SCHEMA_B_THRESHOLD:
            fixture = build_fixture_entry_schema_b(entry, i + 1)
            fixture["quality_tier"] = assign_quality_tier(score, "B")
            scored_b.append(fixture)
        else:
            rejected_b_score += 1

    print(f"Schema B: {len(scored_b)}/{len(schema_b_deduped)} pass threshold (>={SCHEMA_B_THRESHOLD}), {rejected_b_score} rejected")

    # ── Score and filter Schema A entries ────────────────────────────────
    SCHEMA_A_THRESHOLD = 25
    scored_a = []
    rejected_a_score = 0
    for i, entry in enumerate(schema_a):
        score = score_schema_a(entry)
        if score >= SCHEMA_A_THRESHOLD:
            fixture = build_fixture_entry_schema_a(entry, i + 1)
            fixture["quality_tier"] = assign_quality_tier(score, "A")
            scored_a.append(fixture)
        else:
            rejected_a_score += 1

    print(f"Schema A: {len(scored_a)}/{len(schema_a)} pass threshold (>={SCHEMA_A_THRESHOLD}), {rejected_a_score} rejected")

    # ── Process EN400 examples ───────────────────────────────────────────
    en400_fixtures = []
    for i, entry in enumerate(en400_examples):
        fixture = build_fixture_entry_en400(entry, i + 1)
        fixture["quality_tier"] = "gold"  # EN400 are pre-curated
        en400_fixtures.append(fixture)

    print(f"EN400:    {len(en400_fixtures)} curated examples (all gold tier)")

    # ── Organize by domain ───────────────────────────────────────────────
    by_domain = defaultdict(list)
    rejected_no_domain = 0

    for entry in scored_b + scored_a + en400_fixtures:
        domain = entry.get("domain")
        if domain:
            by_domain[domain].append(entry)
        else:
            rejected_no_domain += 1

    # ── Stats by tier ────────────────────────────────────────────────────
    tier_counts = defaultdict(int)
    for entry in scored_b + scored_a + en400_fixtures:
        tier_counts[entry.get("quality_tier", "unknown")] += 1

    print(f"\nRejected (no domain): {rejected_no_domain}")
    print(f"\n{'Domain':<25s} {'Gold':>6s} {'Silver':>8s} {'Bronze':>8s} {'Total':>7s}")
    print("-" * 58)
    total_curated = 0
    for domain in sorted(by_domain.keys()):
        entries = by_domain[domain]
        count = len(entries)
        total_curated += count
        gold = sum(1 for e in entries if e.get("quality_tier") == "gold")
        silver = sum(1 for e in entries if e.get("quality_tier") == "silver")
        bronze = sum(1 for e in entries if e.get("quality_tier") == "bronze")
        print(f"  {domain:<23s} {gold:>6d} {silver:>8d} {bronze:>8d} {count:>7d}")
    print("-" * 58)
    g = tier_counts.get("gold", 0)
    s = tier_counts.get("silver", 0)
    b = tier_counts.get("bronze", 0)
    print(f"  {'TOTAL':<23s} {g:>6d} {s:>8d} {b:>8d} {total_curated:>7d}")

    # ── Write fixture files ──────────────────────────────────────────────
    print(f"\nWriting fixtures to {output_dir}/")
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files = []
    for domain, entries in sorted(by_domain.items()):
        filepath = write_domain_fixture(domain, entries, output_dir)
        written_files.append(filepath)
        print(f"  {filepath} ({len(entries)} vectors)")

    # ── Write summary index ──────────────────────────────────────────────
    total_source = len(schema_a) + len(schema_b)
    total_rejected = (len(schema_b) - len(schema_b_deduped)) + rejected_b_score + rejected_a_score + rejected_no_domain
    index_data = {
        "metadata": {
            "generated_by": "scripts/curate_worked_examples.py",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "issue": "#1294 (WRK-1370)",
            "description": "Curated test vectors from worked examples extracted by doc-intelligence pipeline",
        },
        "summary": {
            "total_source_records": total_source,
            "total_curated": total_curated,
            "total_rejected": total_rejected,
            "en400_examples_included": len(en400_fixtures),
            "schema_a_curated": len(scored_a),
            "schema_b_curated": len(scored_b),
            "schema_b_duplicates_removed": len(schema_b) - len(schema_b_deduped),
            "rejected_low_quality": rejected_b_score + rejected_a_score,
            "rejected_no_domain": rejected_no_domain,
            "curation_rate": f"{total_curated / max(1, total_source) * 100:.1f}%",
        },
        "quality_tiers": {
            "gold": {
                "count": tier_counts.get("gold", 0),
                "description": "Highest quality - suitable as regression test vectors",
            },
            "silver": {
                "count": tier_counts.get("silver", 0),
                "description": "Good quality - suitable as validation examples",
            },
            "bronze": {
                "count": tier_counts.get("bronze", 0),
                "description": "Acceptable - suitable as reference/documentation",
            },
        },
        "domains": {
            domain: {
                "count": len(entries),
                "fixture_file": f"tests/fixtures/test_vectors/{domain}/worked_examples.yaml",
                "gold": sum(1 for e in entries if e.get("quality_tier") == "gold"),
                "silver": sum(1 for e in entries if e.get("quality_tier") == "silver"),
                "bronze": sum(1 for e in entries if e.get("quality_tier") == "bronze"),
            }
            for domain, entries in sorted(by_domain.items())
        },
    }

    index_path = output_dir / "INDEX.yaml"
    with open(index_path, "w") as f:
        yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)
    print(f"  {index_path} (index)")

    # ── Final stats ──────────────────────────────────────────────────────
    total_input = len(schema_a) + len(schema_b) + len(en400_examples)
    print(f"\n{'='*60}")
    print(f"CURATION SUMMARY — Issue #1294 (WRK-1370)")
    print(f"{'='*60}")
    print(f"  Source records (JSONL):       {total_source:>6d}")
    print(f"    Schema A (text-based):      {len(schema_a):>6d}")
    print(f"    Schema B (structured):      {len(schema_b):>6d}")
    print(f"  EN400 examples (YAML):       {len(en400_examples):>6d}")
    print(f"  Total input:                 {total_input:>6d}")
    print(f"  ─────────────────────────────────────")
    print(f"  Duplicates removed:          {len(schema_b) - len(schema_b_deduped):>6d}")
    print(f"  Rejected (low quality):      {rejected_b_score + rejected_a_score:>6d}")
    print(f"  Rejected (no domain):        {rejected_no_domain:>6d}")
    print(f"  ─────────────────────────────────────")
    print(f"  Total curated:               {total_curated:>6d}")
    print(f"    Gold tier:                  {tier_counts.get('gold', 0):>6d}")
    print(f"    Silver tier:                {tier_counts.get('silver', 0):>6d}")
    print(f"    Bronze tier:                {tier_counts.get('bronze', 0):>6d}")
    print(f"  Curation rate:               {total_curated / max(1, total_source) * 100:>5.1f}%")
    print(f"  Fixture files written:       {len(written_files):>6d}")
    print(f"  Domains covered:             {', '.join(sorted(by_domain.keys()))}")
    print()

    # Score distribution
    all_entries = scored_b + scored_a + en400_fixtures
    scores = [e.get("quality_score", 0) for e in all_entries]
    if scores:
        print(f"  Quality score range:         {min(scores)}-{max(scores)}")
        print(f"  Quality score median:        {sorted(scores)[len(scores)//2]}")
        print(f"  Quality score mean:          {sum(scores)/len(scores):.1f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
