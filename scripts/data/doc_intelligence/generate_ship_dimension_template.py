"""Generate ship dimension template YAML for manual data entry.

Reads ship-plans-index.yaml and creates a template with null dimension
fields for every drawing-only plan (has_text: false).
"""

from datetime import datetime, timezone


DIMENSION_FIELDS = [
    "length_overall_ft",
    "beam_ft",
    "draft_ft",
    "depth_ft",
    "displacement_lt",
    "speed_kts",
]


def build_dimension_entries(plans: list[dict]) -> list[dict]:
    """Build template entries from plan records, skipping text-extractable."""
    entries = []
    for plan in plans:
        if plan.get("has_text", False):
            continue
        entries.append({
            "stem": plan["stem"],
            "hull_code": plan["hull_code"],
            "hull_number": plan["hull_number"],
            "vessel_type": plan["vessel_type"],
            "source_plan": plan["filename"],
            "entry_status": "pending",
            "dimensions": {k: None for k in DIMENSION_FIELDS},
        })
    return entries


def build_template_document(plans: list[dict]) -> dict:
    """Build the full template document from plan records."""
    entries = build_dimension_entries(plans)
    return {
        "version": "1.0.0",
        "description": "Ship dimension template for manual data entry",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(entries),
        "entries": entries,
    }
