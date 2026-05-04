---
name: xlsx-to-python-dark-intelligence-archive-generation
description: 'Sub-skill of xlsx-to-python: Dark Intelligence Archive Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Dark Intelligence Archive Generation

## Dark Intelligence Archive Generation


Convert extraction results to the canonical archive YAML:

```python
def formula_manifest_to_archive(
    formula_cells: list[dict],
    named_ranges: list[dict],
    classification: dict,
    category: str,
    subcategory: str,
) -> dict:
    """Convert XLSX extraction to dark-intelligence archive YAML."""
    name_map = {
        f"{nr['sheet']}!{nr['cell_ref']}": nr["name"]
        for nr in named_ranges
    }

    archive = {
        "source_type": "excel",
        "source_description": f"{category}/{subcategory} calculation",
        "extracted_date": datetime.now().strftime("%Y-%m-%d"),
        "legal_scan_passed": False,  # Must be set after legal scan
        "category": category,
        "subcategory": subcategory,
        "equations": [],
        "inputs": [],
        "outputs": [],
        "worked_examples": [],
        "assumptions": [],
        "references": [],
    }

    # Map input cells
    for input_ref in classification["inputs"]:
        cell = next(
            (c for c in formula_cells
             if f"{c['sheet']}!{c['ref']}" == input_ref),
            None,
        )
        name = name_map.get(input_ref, input_ref)
        archive["inputs"].append({
            "name": name,
            "symbol": name,
            "unit": "",  # Must be filled manually or from column headers
            "test_value": cell["value"] if cell else None,
        })

    # Map formula cells as equations
    for cell in formula_cells:
        cell_id = f"{cell['sheet']}!{cell['ref']}"
        if cell_id in classification["inputs"]:
            continue
        archive["equations"].append({
            "name": name_map.get(cell_id, cell["ref"]),
            "excel_formula": cell["formula"],
            "latex": "",  # TODO: formula-to-LaTeX translation
            "description": f"Cell {cell['ref']} in {cell['sheet']}",
        })

    # Map output cells
    for output_ref in classification["outputs"]:
        cell = next(
            (c for c in formula_cells
             if f"{c['sheet']}!{c['ref']}" == output_ref),
            None,
        )
        if cell and cell["value"] is not None:
            name = name_map.get(output_ref, output_ref)
            archive["outputs"].append({
                "name": name,
                "symbol": name,
                "unit": "",
                "test_expected": cell["value"],
                "tolerance": 1e-6,
            })

    return archive
```
