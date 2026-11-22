"""Build and audit a synthetic projection; no remote data or engineering values.

Hand enumeration: two detail fields, two wells in the first field, no wells in
the second; three atlas rows in two countries, one row in each density tier.
The schema comes from the upstream exporter cited in the audit guide.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path


def _encode(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, allow_nan=False) + "\n").encode()


def build_example(output: Path) -> dict:
    """Write new synthetic inputs and return the audit report, refusing overwrite."""
    # Require a new directory so an example invocation cannot replace prior data.
    output.mkdir(parents=True, exist_ok=False)
    fields = {
        "field_a": {"id": "field_a", "provenance": "synthetic", "wellsCount": 2},
        "field_b": {"id": "field_b", "provenance": None, "wellsCount": 0},
    }
    wells = {
        "fields": {"field_a": {"display_name": "Synthetic A"}},
        "wells": [{"api": "well_x", "field_id": "field_a"},
                  {"api": "well_y", "field_id": "field_a"}],
    }
    atlas = {
        "countries": [{"country": "AA"}, {"country": "BB"}],
        "fields": [
            {"catalog_id": "a", "country": "AA", "density_tier": "rich"},
            {"catalog_id": "b", "country": "AA", "density_tier": "sample"},
            {"catalog_id": "c", "country": "BB", "density_tier": "roadmap"},
        ],
    }
    sources = []
    for role, path, value in (
        ("field_detail", "detail.json", {"fields": fields, "wells": wells}),
        ("global_funnel", "atlas.json", atlas),
    ):
        raw = _encode(value)
        (output / path).write_bytes(raw)
        sources.append({"role": role, "path": path,
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    bundle = {
        "schema_version": "1.0.0", "projection": "field_explorer_results",
        "hf_dataset": "worldenergydata", "sources": sources,
        "fields": fields, "wells": wells, "atlas": atlas,
        "field_provenance": {key: value["provenance"] for key, value in fields.items()},
        "record_counts": {"fields": 2, "wells": 2, "countries": 2, "atlas_fields": 3},
    }
    raw = _encode(bundle)
    path = output / "bundle.json"
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    (output / "bundle.sha256").write_text(digest + "\n", encoding="utf-8")
    implementation = Path(__file__).resolve().parents[1] / "scripts/hf/audit_field_explorer.py"
    audit = runpy.run_path(str(implementation))["audit_bundle"]
    return audit(path, output, digest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build_example(args.out), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
