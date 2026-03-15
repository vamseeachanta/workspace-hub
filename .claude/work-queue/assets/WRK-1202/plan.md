# WRK-1202: Doc-Extraction Skills → Reusable Scripts

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert 13 document extraction skills from LLM prose to deterministic, TDD-tested Python scripts with CLI interfaces.

**Architecture:** Each script is a standalone PEP 723 Python file in `scripts/data/doc_intelligence/` that reuses existing `schema.py`, `fetcher.py`, and `queue.py` infrastructure. All scripts use `uv run --no-project` and output YAML/JSONL. No external MCPs or paid services — use `httpx` + `beautifulsoup4` (already in tier-1 repos) and stdlib `urllib.robotparser`.

**Tech Stack:** Python 3.10+, PEP 723 inline deps, pyyaml, beautifulsoup4, httpx, pdfplumber, pytest

**Scope note:** This WRK exceeds chunk-sizing (13 scripts > 5 files). It is a child of Feature WRK-1179. The plan is decomposed into 4 chunks matching the 4 tiers. Each chunk is independently executable and committable.

---

## File Structure

All new scripts go in `scripts/data/doc_intelligence/`. Tests go in `scripts/data/doc_intelligence/tests/`.

| Script | Tier | Reuses | Purpose |
|--------|------|--------|---------|
| `manifest_to_archive.py` | 1 | `schema.py` | Manifest → dark-intelligence YAML |
| `deduplicate_manifests.py` | 1 | `schema.py` | Merge/dedup batch manifests |
| `fetch_queue_manager.py` | 1 | `fetcher.py`, `queue.py` | Async URL fetch queue with resume |
| `extract_engineering_constants.py` | 2 | `schema.py` | Deterministic constant extraction |
| `normalize_units.py` | 2 | — | SI/imperial/field unit normalization |
| `parse_standard_reference.py` | 2 | — | DNV/API/ISO ref → structured YAML |
| `validate_naval_architecture.py` | 2 | — | IMO criteria + hull coefficient checks |
| `crawl_and_enqueue.py` | 3 | `fetcher.py` | Seed URL crawl → link extraction |
| `fetch_from_api.py` | 3 | `fetcher.py` | REST API fetcher (BSEE/EIA/IMO) |
| `end_to_end_online_extraction.py` | 3 | all above | Orchestrate: fetch→extract→dedup→archive |
| `audit_extractions.py` | 4 | `schema.py` | Extraction stats report |
| `validate_confidence.py` | 4 | `schema.py` | Filter low-confidence manifests |
| `generate_research_brief.py` | 4 | — | Automate research-literature Steps 1-4 |

**Existing infrastructure to reuse (DO NOT recreate):**
- `scripts/data/doc_intelligence/schema.py` — `DocumentManifest`, `manifest_from_dict()`, `manifest_to_dict()`, `write_manifest()`
- `scripts/data/doc_intelligence/fetcher.py` — `UrlFetcher` with SSRF protection, robots.txt, rate limiting, disk cache
- `scripts/data/doc_intelligence/queue.py` — `load_queue()`, `save_queue()`, `get_pending()`, `mark_completed()`, `mark_failed()`
- `scripts/data/doc_intelligence/orchestrator.py` — `extract_document()` format detection + parser dispatch
- `scripts/lib/download-helpers.sh` — bash `download()` function with retry + logging

---

## Chunk 1: Tier 1 — High Priority (Blocking WRK-1183/1188)

### Task 1: `manifest_to_archive.py` — Manifest → Dark Intelligence YAML

**Files:**
- Create: `scripts/data/doc_intelligence/manifest_to_archive.py`
- Test: `scripts/data/doc_intelligence/tests/test_manifest_to_archive.py`
- Reference: `scripts/data/doc_intelligence/schema.py` (read only)

**Context:** Converts a `DocumentManifest` YAML (output of `extract-document.py`) into a dark-intelligence archive YAML (schema defined in `dark-intelligence-workflow` skill: `knowledge/dark-intelligence/<category>/<subcategory>/dark-intelligence-<name>.yaml`).

The manifest has: `sections` (heading + text), `tables` (columns + rows), `figure_refs`, `metadata`. The archive needs: `equations`, `inputs`, `outputs`, `worked_examples`, `assumptions`, `references`. The script extracts these deterministically using regex/heuristics on section text.

- [ ] **Step 1: Write failing test for equation extraction**

```python
# scripts/data/doc_intelligence/tests/test_manifest_to_archive.py
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "pytest"]
# ///
"""Tests for manifest_to_archive conversion."""

import pytest
import yaml

from scripts.data.doc_intelligence.manifest_to_archive import (
    extract_equations,
    extract_inputs_outputs,
    manifest_to_archive,
)


def test_extract_equations_from_section_text():
    """Equations referenced by standard notation are captured."""
    text = (
        "The wall thickness is calculated per DNV-ST-F101 Eq. 5.16:\n"
        "t_min = (P_d * D) / (2 * f_y * alpha_U)\n"
        "where P_d is design pressure and D is outer diameter."
    )
    equations = extract_equations(text)
    assert len(equations) >= 1
    assert equations[0]["name"] == "Eq. 5.16"
    assert "P_d" in equations[0]["formula"]
    assert equations[0]["standard"] == "DNV-ST-F101"


def test_extract_equations_empty_text():
    equations = extract_equations("")
    assert equations == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest scripts/data/doc_intelligence/tests/test_manifest_to_archive.py -v`
Expected: FAIL — ImportError (module doesn't exist yet)

- [ ] **Step 3: Write minimal implementation for equation extraction**

```python
# scripts/data/doc_intelligence/manifest_to_archive.py
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Convert doc-intelligence manifests to dark-intelligence archive YAML.

ABOUTME: Deterministic conversion of DocumentManifest extraction output into
ABOUTME: dark-intelligence archive format for downstream TDD test generation.

Usage:
    uv run --no-project python scripts/data/doc_intelligence/manifest_to_archive.py \
        --input data/doc-intelligence/manifests/structural/example.manifest.yaml \
        --category structural --subcategory wall_thickness \
        --output knowledge/dark-intelligence/structural/wall_thickness/dark-intelligence-example.yaml
"""

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

import yaml


# -- Equation extraction heuristics --

# Matches patterns like "Eq. 5.16", "Equation (3.2)", "eq 12", "Eqn. A-1"
EQ_REF_PATTERN = re.compile(
    r"(?:Eq(?:uation|n)?\.?\s*\(?)([\w\-\.]+)\)?",
    re.IGNORECASE,
)

# Matches standard references like "DNV-ST-F101", "API RP 2A", "ISO 19901-1"
STD_REF_PATTERN = re.compile(
    r"((?:DNV|API|ISO|ASME|NORSOK|IEC|ABS|BV|LR)[\s\-][\w\-]+(?:\s[\w\-]+)?)",
    re.IGNORECASE,
)

# Matches simple formula lines: variable = expression (no prose sentences)
FORMULA_PATTERN = re.compile(
    r"^\s*(\w[\w_]*)\s*=\s*(.+)$",
    re.MULTILINE,
)


def extract_equations(text: str) -> list[dict]:
    """Extract equations from section text using regex heuristics.

    Looks for equation references (Eq. N.N), nearby formula lines,
    and standard references on the same line or preceding lines.
    """
    if not text.strip():
        return []

    equations = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        eq_match = EQ_REF_PATTERN.search(line)
        if not eq_match:
            continue

        eq_name = f"Eq. {eq_match.group(1)}"

        # Find standard reference on this line or within 3 preceding lines
        standard = None
        search_window = "\n".join(lines[max(0, i - 3): i + 1])
        std_match = STD_REF_PATTERN.search(search_window)
        if std_match:
            standard = std_match.group(1).strip()

        # Find formula on next lines (within 3 lines)
        formula = None
        for j in range(i, min(len(lines), i + 4)):
            fm = FORMULA_PATTERN.match(lines[j])
            if fm:
                formula = lines[j].strip()
                break

        equations.append({
            "name": eq_name,
            "formula": formula or "",
            "standard": standard,
            "description": line.strip(),
        })

    return equations


def extract_inputs_outputs(text: str) -> tuple[list[dict], list[dict]]:
    """Extract input/output parameters from 'where' clauses and tables.

    Looks for patterns like:
    - 'where X is the <description>'
    - 'X = <description> (<unit>)'
    """
    inputs = []
    # Match "where X is ..." or "X = description (unit)"
    where_pattern = re.compile(
        r"(?:where\s+)?(\w[\w_]*)\s+(?:is|=)\s+(?:the\s+)?(.+?)(?:\(([^)]+)\))?$",
        re.MULTILINE | re.IGNORECASE,
    )
    for match in where_pattern.finditer(text):
        symbol = match.group(1)
        description = match.group(2).strip().rstrip(",.")
        unit = match.group(3).strip() if match.group(3) else None
        inputs.append({
            "name": description[:60],
            "symbol": symbol,
            "unit": unit,
        })
    return inputs, []  # outputs require more context — left for table extraction


def manifest_to_archive(
    manifest_dict: dict,
    category: str,
    subcategory: str,
) -> dict:
    """Convert a DocumentManifest dict to dark-intelligence archive dict."""
    all_text = "\n\n".join(
        s.get("text", "") for s in manifest_dict.get("sections", [])
    )

    equations = extract_equations(all_text)
    inputs, outputs = extract_inputs_outputs(all_text)

    # Extract standard references from all sections
    references = []
    for match in STD_REF_PATTERN.finditer(all_text):
        ref = match.group(1).strip()
        if ref not in references:
            references.append(ref)

    archive = {
        "source_type": manifest_dict.get("metadata", {}).get("format", "unknown"),
        "source_description": (
            f"Extracted from {manifest_dict.get('metadata', {}).get('filename', 'unknown')}"
        ),
        "extracted_date": date.today().isoformat(),
        "legal_scan_passed": False,  # Must be set to True after legal scan
        "category": category,
        "subcategory": subcategory,
        "equations": equations,
        "inputs": inputs,
        "outputs": outputs,
        "worked_examples": [],  # Populated from tables in future enhancement
        "assumptions": [],
        "references": references,
        "notes": f"Auto-extracted by manifest_to_archive.py from {manifest_dict.get('doc_ref', 'unknown')}",
    }
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert doc-intelligence manifest to dark-intelligence archive YAML"
    )
    parser.add_argument("--input", required=True, help="Path to manifest YAML")
    parser.add_argument("--category", required=True, help="Engineering category")
    parser.add_argument("--subcategory", required=True, help="Specific topic")
    parser.add_argument("--output", help="Output YAML path (default: stdout)")
    args = parser.parse_args()

    with open(args.input) as f:
        manifest_dict = yaml.safe_load(f)

    archive = manifest_to_archive(manifest_dict, args.category, args.subcategory)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(".yaml.tmp")
        tmp.write_text(yaml.dump(archive, default_flow_style=False, sort_keys=False))
        os.replace(tmp, out_path)
        print(f"Archive written to {args.output}")
    else:
        yaml.dump(archive, sys.stdout, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --no-project python -m pytest scripts/data/doc_intelligence/tests/test_manifest_to_archive.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Add integration test with full manifest round-trip**

```python
# Append to test_manifest_to_archive.py

def test_manifest_to_archive_full_roundtrip():
    """Full manifest dict → archive dict with all fields."""
    manifest = {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "engineering-standards",
        "doc_ref": "DNV-ST-F101",
        "metadata": {"filename": "dnv-st-f101.pdf", "format": "pdf", "size_bytes": 500000},
        "sections": [
            {
                "heading": "Wall Thickness Design",
                "level": 2,
                "text": (
                    "The minimum wall thickness per DNV-ST-F101 Eq. 5.16:\n"
                    "t_min = (P_d * D) / (2 * f_y * alpha_U)\n"
                    "where P_d is the design pressure (MPa)\n"
                    "where D is the outer diameter (mm)"
                ),
                "source": {"document": "dnv-st-f101.pdf", "page": 42},
            }
        ],
        "tables": [],
        "figure_refs": [],
        "extraction_stats": {"sections": 1, "tables": 0, "figure_refs": 0},
        "errors": [],
    }
    archive = manifest_to_archive(manifest, "pipeline", "wall_thickness")
    assert archive["category"] == "pipeline"
    assert archive["subcategory"] == "wall_thickness"
    assert archive["source_type"] == "pdf"
    assert archive["legal_scan_passed"] is False
    assert len(archive["equations"]) >= 1
    assert len(archive["inputs"]) >= 1
    assert "DNV-ST-F101" in archive["references"]
```

- [ ] **Step 6: Run full test suite, then commit**

Run: `uv run --no-project python -m pytest scripts/data/doc_intelligence/tests/test_manifest_to_archive.py -v`

```bash
git add scripts/data/doc_intelligence/manifest_to_archive.py scripts/data/doc_intelligence/tests/test_manifest_to_archive.py
git commit -m "feat(WRK-1202): manifest-to-archive conversion script with TDD"
git push
```

---

### Task 2: `deduplicate_manifests.py` — Merge/Dedup Batch Manifests

**Files:**
- Create: `scripts/data/doc_intelligence/deduplicate_manifests.py`
- Test: `scripts/data/doc_intelligence/tests/test_deduplicate_manifests.py`

**Context:** When batch-extract.py runs on overlapping document sets, manifests may contain duplicate sections/tables (same content hash from same source page). This script merges multiple manifests by content hash and deduplicates sections.

- [ ] **Step 1: Write failing tests for dedup logic**

```python
# scripts/data/doc_intelligence/tests/test_deduplicate_manifests.py
"""Tests for manifest deduplication."""

import pytest
from scripts.data.doc_intelligence.deduplicate_manifests import (
    deduplicate_sections,
    merge_manifests,
    compute_section_hash,
)


def test_compute_section_hash_deterministic():
    section = {"heading": "Intro", "level": 1, "text": "Hello world"}
    h1 = compute_section_hash(section)
    h2 = compute_section_hash(section)
    assert h1 == h2
    assert len(h1) == 16  # truncated sha256


def test_deduplicate_sections_removes_exact_dupes():
    sections = [
        {"heading": "A", "level": 1, "text": "content", "source": {"document": "a.pdf", "page": 1}},
        {"heading": "A", "level": 1, "text": "content", "source": {"document": "a.pdf", "page": 1}},
        {"heading": "B", "level": 1, "text": "different", "source": {"document": "a.pdf", "page": 2}},
    ]
    result = deduplicate_sections(sections)
    assert len(result) == 2


def test_merge_manifests_combines_sections():
    m1 = {
        "version": "1.0.0", "tool": "test", "domain": "test",
        "metadata": {"filename": "a.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [{"heading": "A", "level": 1, "text": "first", "source": {"document": "a.pdf"}}],
        "tables": [], "figure_refs": [], "extraction_stats": {}, "errors": [],
    }
    m2 = {
        "version": "1.0.0", "tool": "test", "domain": "test",
        "metadata": {"filename": "b.pdf", "format": "pdf", "size_bytes": 200},
        "sections": [{"heading": "B", "level": 1, "text": "second", "source": {"document": "b.pdf"}}],
        "tables": [], "figure_refs": [], "extraction_stats": {}, "errors": [],
    }
    merged = merge_manifests([m1, m2])
    assert len(merged["sections"]) == 2
    assert merged["metadata"]["source_count"] == 2
```

- [ ] **Step 2: Run to verify fails**

Run: `uv run --no-project python -m pytest scripts/data/doc_intelligence/tests/test_deduplicate_manifests.py -v`

- [ ] **Step 3: Implement `deduplicate_manifests.py`**

Script should:
1. Accept `--inputs` (glob or file list) or stdin (YAML stream)
2. Load all manifests, merge sections/tables/figure_refs
3. Deduplicate by content hash (heading + text for sections, columns + rows for tables)
4. Output merged manifest to `--output` or stdout
5. Print dedup stats to stderr

Key functions: `compute_section_hash(section)`, `deduplicate_sections(sections)`, `merge_manifests(manifest_dicts)`, `main()`.

- [ ] **Step 4: Run tests, then commit**

```bash
git add scripts/data/doc_intelligence/deduplicate_manifests.py scripts/data/doc_intelligence/tests/test_deduplicate_manifests.py
git commit -m "feat(WRK-1202): manifest deduplication script with TDD"
git push
```

---

### Task 3: `fetch_queue_manager.py` — Async URL Fetch Queue

**Files:**
- Create: `scripts/data/doc_intelligence/fetch_queue_manager.py`
- Test: `scripts/data/doc_intelligence/tests/test_fetch_queue_manager.py`
- Reuse: `scripts/data/doc_intelligence/fetcher.py` (`UrlFetcher`), `scripts/data/doc_intelligence/queue.py`

**Context:** Manages a YAML-based fetch queue with domain-aware throttling, resume capability, and progress tracking. Uses the existing `UrlFetcher` (which already handles robots.txt, rate limiting, SSRF prevention, caching) and `queue.py` (which already handles queue load/save/mark).

**Decision (2026-03-14):** No external MCP needed. Uses `httpx` for async where beneficial, falls back to existing `requests`-based `UrlFetcher` for synchronous fetching. The queue file is the resume checkpoint.

- [ ] **Step 1: Write failing tests**

```python
# scripts/data/doc_intelligence/tests/test_fetch_queue_manager.py
"""Tests for fetch queue manager."""

import pytest
import yaml
from pathlib import Path

from scripts.data.doc_intelligence.fetch_queue_manager import (
    create_queue,
    process_queue,
    get_domain_stats,
)


def test_create_queue_from_url_list(tmp_path):
    urls = [
        "https://example.com/doc1.pdf",
        "https://example.com/doc2.pdf",
        "https://other.org/page.html",
    ]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)

    data = yaml.safe_load(queue_path.read_text())
    assert len(data["documents"]) == 3
    assert all(d["status"] == "pending" for d in data["documents"])


def test_get_domain_stats():
    queue = {
        "documents": [
            {"url": "https://a.com/1", "status": "pending"},
            {"url": "https://a.com/2", "status": "completed"},
            {"url": "https://b.com/3", "status": "pending"},
        ]
    }
    stats = get_domain_stats(queue)
    assert stats["a.com"]["pending"] == 1
    assert stats["a.com"]["completed"] == 1
    assert stats["b.com"]["pending"] == 1


def test_create_queue_deduplicates_urls(tmp_path):
    urls = ["https://example.com/doc.pdf", "https://example.com/doc.pdf"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)
    data = yaml.safe_load(queue_path.read_text())
    assert len(data["documents"]) == 1
```

- [ ] **Step 2: Run to verify fails**
- [ ] **Step 3: Implement `fetch_queue_manager.py`**

Key functions: `create_queue(urls, path)`, `process_queue(queue_path, fetcher, output_dir, batch_size=10)`, `get_domain_stats(queue)`, `main()`.

CLI: `--create-from <url-list-file>`, `--process <queue.yaml>`, `--output-dir <dir>`, `--batch-size N`, `--stats <queue.yaml>`.

- [ ] **Step 4: Run tests, then commit**

```bash
git add scripts/data/doc_intelligence/fetch_queue_manager.py scripts/data/doc_intelligence/tests/test_fetch_queue_manager.py
git commit -m "feat(WRK-1202): fetch queue manager with resume and domain throttling"
git push
```

---

## Chunk 2: Tier 2 — Engineering Extraction Heuristics

### Task 4: `extract_engineering_constants.py`

**Files:**
- Create: `scripts/data/doc_intelligence/extract_engineering_constants.py`
- Test: `scripts/data/doc_intelligence/tests/test_extract_engineering_constants.py`

**Context:** Extracts engineering constants (material properties, safety factors, environmental parameters) from manifest sections and tables. Deterministic Layer 1 extraction from `doc-extraction/SKILL.md`.

Heuristic: constants are rows in tables where one column is a parameter name, another is a numeric value, and optionally a unit column. Also extracts inline constants like "yield strength f_y = 450 MPa".

- [ ] **Step 1: Write failing tests**

```python
def test_extract_constants_from_table():
    table = {
        "columns": ["Parameter", "Value", "Unit"],
        "rows": [
            ["Yield strength", "450", "MPa"],
            ["Young's modulus", "207000", "MPa"],
            ["Poisson's ratio", "0.3", "-"],
        ],
    }
    constants = extract_constants_from_table(table)
    assert len(constants) == 3
    assert constants[0]["name"] == "Yield strength"
    assert constants[0]["value"] == 450.0
    assert constants[0]["unit"] == "MPa"


def test_extract_constants_from_text():
    text = "The yield strength f_y = 450 MPa and modulus E = 207 GPa."
    constants = extract_constants_from_text(text)
    assert len(constants) >= 2
```

- [ ] **Step 2: Run to verify fails**
- [ ] **Step 3: Implement extraction heuristics**
- [ ] **Step 4: Run tests, commit**

```bash
git add scripts/data/doc_intelligence/extract_engineering_constants.py scripts/data/doc_intelligence/tests/test_extract_engineering_constants.py
git commit -m "feat(WRK-1202): engineering constants extractor with TDD"
git push
```

---

### Task 5: `normalize_units.py`

**Files:**
- Create: `scripts/data/doc_intelligence/normalize_units.py`
- Test: `scripts/data/doc_intelligence/tests/test_normalize_units.py`

**Context:** Normalizes between SI, Imperial, and field units. Common conversions: psi↔MPa, ft↔m, bbl↔m³, °F↔°C, lb/ft³↔kg/m³, ksi→MPa, inches→mm.

- [ ] **Step 1: Write failing tests**

```python
def test_normalize_pressure_psi_to_mpa():
    assert normalize("psi", "MPa", 1000.0) == pytest.approx(6.8948, rel=1e-3)

def test_normalize_length_ft_to_m():
    assert normalize("ft", "m", 100.0) == pytest.approx(30.48, rel=1e-4)

def test_normalize_unknown_unit_raises():
    with pytest.raises(ValueError, match="Unknown unit"):
        normalize("furlongs", "m", 1.0)

def test_detect_unit_system():
    assert detect_system("MPa") == "SI"
    assert detect_system("psi") == "Imperial"
    assert detect_system("bbl/d") == "Field"
```

- [ ] **Step 2-4: Implement, test, commit**

Lookup table approach (no external unit library needed). Cover the ~30 most common O&G engineering units.

```bash
git commit -m "feat(WRK-1202): unit normalization script with TDD"
git push
```

---

### Task 6: `parse_standard_reference.py`

**Files:**
- Create: `scripts/data/doc_intelligence/parse_standard_reference.py`
- Test: `scripts/data/doc_intelligence/tests/test_parse_standard_reference.py`

**Context:** Parses standard references like "DNV-RP-C205 Section 4.3.2" or "API RP 2A-WSD 22nd Ed., Section 6.7" into structured YAML: `{body: "DNV", code: "RP-C205", section: "4.3.2", edition: null}`.

- [ ] **Step 1: Write failing tests**

```python
def test_parse_dnv_reference():
    ref = parse_reference("DNV-RP-C205 Section 4.3.2")
    assert ref["body"] == "DNV"
    assert ref["code"] == "RP-C205"
    assert ref["section"] == "4.3.2"

def test_parse_api_reference():
    ref = parse_reference("API RP 2A-WSD 22nd Ed.")
    assert ref["body"] == "API"
    assert ref["code"] == "RP 2A-WSD"
    assert ref["edition"] == "22nd"

def test_parse_iso_reference():
    ref = parse_reference("ISO 19901-1:2015")
    assert ref["body"] == "ISO"
    assert ref["code"] == "19901-1"
    assert ref["year"] == 2015
```

- [ ] **Step 2-4: Implement, test, commit**

```bash
git commit -m "feat(WRK-1202): standard reference parser with TDD"
git push
```

---

### Task 7: `validate_naval_architecture.py`

**Files:**
- Create: `scripts/data/doc_intelligence/validate_naval_architecture.py`
- Test: `scripts/data/doc_intelligence/tests/test_validate_naval_architecture.py`

**Context:** From `naval-architecture/SKILL.md` — validates extracted naval architecture data against IMO stability criteria and hull coefficient ranges (Cb 0.5-0.85 for cargo, Cw 0.65-0.95, etc.).

- [ ] **Step 1: Write failing tests**

```python
def test_validate_block_coefficient_cargo():
    result = validate_hull_coefficients(Cb=0.82, vessel_type="cargo")
    assert result["valid"] is True

def test_validate_block_coefficient_out_of_range():
    result = validate_hull_coefficients(Cb=0.95, vessel_type="cargo")
    assert result["valid"] is False
    assert "Cb" in result["errors"][0]

def test_validate_imo_stability_criteria():
    result = validate_imo_stability(
        GZ_area_0_30=0.060,  # m·rad, min 0.055
        GZ_area_0_40=0.095,  # m·rad, min 0.090
        GZ_max_angle=35,     # degrees, must be > 25
        GM0=0.20,            # m, min 0.15
    )
    assert result["pass"] is True
```

- [ ] **Step 2-4: Implement, test, commit**

```bash
git commit -m "feat(WRK-1202): naval architecture validation with TDD"
git push
```

---

## Chunk 3: Tier 3 — Online Document Parsing Infrastructure

**MCP Assessment (2026-03-14):** No external MCP or paid service needed. Uses `UrlFetcher` (already has robots.txt, SSRF protection, rate limiting, disk cache) + `beautifulsoup4` for link extraction. For REST APIs (BSEE/EIA), uses `httpx` (already a dependency in digitalmodel/worldenergydata).

### Task 8: `crawl_and_enqueue.py`

**Files:**
- Create: `scripts/data/doc_intelligence/crawl_and_enqueue.py`
- Test: `scripts/data/doc_intelligence/tests/test_crawl_and_enqueue.py`
- Reuse: `scripts/data/doc_intelligence/fetcher.py`

**Context:** Given seed URLs, fetch each page, extract all linked document URLs (PDF, DOCX, XLSX), filter by domain allowlist, respect robots.txt, and output a URL list or directly create a fetch queue.

- [ ] **Step 1: Write failing tests**

```python
def test_extract_document_links_from_html():
    html = """
    <html><body>
        <a href="/docs/report.pdf">Report</a>
        <a href="https://example.com/data.xlsx">Data</a>
        <a href="/page.html">Page</a>
        <a href="mailto:test@test.com">Email</a>
    </body></html>
    """
    links = extract_document_links(html, base_url="https://example.com")
    assert len(links) == 2  # .pdf and .xlsx only
    assert any(l.endswith("report.pdf") for l in links)
    assert any(l.endswith("data.xlsx") for l in links)


def test_filter_by_domain():
    urls = [
        "https://allowed.com/doc.pdf",
        "https://blocked.com/doc.pdf",
    ]
    filtered = filter_by_domain(urls, allowed_domains=["allowed.com"])
    assert len(filtered) == 1
```

- [ ] **Step 2-4: Implement, test, commit**

```bash
git commit -m "feat(WRK-1202): crawl-and-enqueue with link extraction and domain filtering"
git push
```

---

### Task 9: `fetch_from_api.py`

**Files:**
- Create: `scripts/data/doc_intelligence/fetch_from_api.py`
- Test: `scripts/data/doc_intelligence/tests/test_fetch_from_api.py`

**Context:** REST API document fetcher for BSEE Data Center, EIA API, and IMO GISIS. Handles auth (API keys via env vars), pagination, and rate limiting. Outputs fetched documents to disk + updates fetch queue.

Target APIs are defined in `scripts/data/document-index/config.yaml` under `api_metadata`:
- BSEE: `https://www.data.bsee.gov/Main/` (no auth)
- EIA: `https://api.eia.gov/v2/` (API key via `EIA_API_KEY`)
- IMO GISIS: `https://gisis.imo.org/` (session auth)

- [ ] **Step 1: Write failing tests**

```python
def test_build_bsee_url():
    url = build_api_url("bsee", endpoint="production", params={"year": 2024})
    assert "data.bsee.gov" in url
    assert "year=2024" in url

def test_build_eia_url_includes_api_key():
    url = build_api_url("eia", endpoint="petroleum/summary", api_key="test123")
    assert "api.eia.gov" in url
    assert "api_key=test123" in url

def test_paginate_returns_all_pages():
    # Mock a paginated response
    pages = list(paginate_results(
        mock_fetcher,
        url="https://api.example.com/data",
        page_size=10,
        max_pages=3,
    ))
    assert len(pages) <= 3
```

- [ ] **Step 2-4: Implement, test, commit**

```bash
git commit -m "feat(WRK-1202): REST API fetcher for BSEE/EIA/IMO with pagination"
git push
```

---

### Task 10: `end_to_end_online_extraction.py` (AC3 — 2 of 3 Tier 3 scripts)

**Files:**
- Create: `scripts/data/doc_intelligence/end_to_end_online_extraction.py`
- Test: `scripts/data/doc_intelligence/tests/test_end_to_end_extraction.py`

**Context:** Orchestrates the full pipeline: crawl seed URLs → fetch documents → extract content → deduplicate → optionally archive to dark-intelligence. Composes Tasks 8, 9, 3, 2, and 1.

- [ ] **Step 1: Write failing tests for pipeline orchestration**
- [ ] **Step 2-4: Implement, test, commit**

```bash
git commit -m "feat(WRK-1202): end-to-end online extraction pipeline"
git push
```

---

## Chunk 4: Tier 4 — Quality & Audit

### Task 11: `audit_extractions.py`

**Files:**
- Create: `scripts/data/doc_intelligence/audit_extractions.py`
- Test: `scripts/data/doc_intelligence/tests/test_audit_extractions.py`

**Context:** Generates extraction statistics report from a directory of manifests: total documents, sections/tables/figures counts, error rates, format breakdown, domain distribution. Outputs YAML report.

- [ ] **Step 1: Write failing tests**

```python
def test_audit_counts_manifests(tmp_path):
    # Create 2 test manifests
    for name in ["a.manifest.yaml", "b.manifest.yaml"]:
        (tmp_path / name).write_text(yaml.dump({
            "version": "1.0.0", "tool": "test", "domain": "test",
            "metadata": {"filename": name, "format": "pdf", "size_bytes": 100},
            "sections": [{"heading": "X", "level": 1, "text": "t", "source": {}}],
            "tables": [], "figure_refs": [],
            "extraction_stats": {"sections": 1, "tables": 0, "figure_refs": 0},
            "errors": [],
        }))
    report = audit_directory(tmp_path)
    assert report["total_manifests"] == 2
    assert report["total_sections"] == 2
```

- [ ] **Step 2-4: Implement, test, commit**

```bash
git commit -m "feat(WRK-1202): extraction audit report script"
git push
```

---

### Task 12: `validate_confidence.py`

**Files:**
- Create: `scripts/data/doc_intelligence/validate_confidence.py`
- Test: `scripts/data/doc_intelligence/tests/test_validate_confidence.py`

**Context:** Filters manifests by extraction quality heuristics: minimum section count, non-empty text, error count threshold. Outputs pass/fail per manifest + summary.

- [ ] **Step 1-4: TDD cycle, commit**

```bash
git commit -m "feat(WRK-1202): confidence validation filter for manifests"
git push
```

---

### Task 13: `generate_research_brief.py`

**Files:**
- Create: `scripts/data/doc_intelligence/generate_research_brief.py`
- Test: `scripts/data/doc_intelligence/tests/test_generate_research_brief.py`

**Context:** Automates research-literature skill Steps 1-4: query document index + standards ledger + capability map → produce structured research brief YAML. Deterministic replacement for LLM-driven research-literature discovery.

- [ ] **Step 1-4: TDD cycle, commit**

```bash
git commit -m "feat(WRK-1202): automated research brief generator"
git push
```

---

## Final Verification

- [ ] **Run full test suite**

```bash
uv run --no-project python -m pytest scripts/data/doc_intelligence/tests/ -v --tb=short
```

Expected: All 13 test modules pass.

- [ ] **Run legal scan**

```bash
bash scripts/legal/legal-sanity-scan.sh
```

Expected: Zero block-severity violations.

- [ ] **Verify CLI help for all scripts**

```bash
for script in manifest_to_archive deduplicate_manifests fetch_queue_manager \
    extract_engineering_constants normalize_units parse_standard_reference \
    validate_naval_architecture crawl_and_enqueue fetch_from_api \
    end_to_end_online_extraction audit_extractions validate_confidence \
    generate_research_brief; do
    echo "=== $script ==="
    uv run --no-project python scripts/data/doc_intelligence/${script}.py --help
done
```

- [ ] **Update WRK-1202 status to `completed`**
