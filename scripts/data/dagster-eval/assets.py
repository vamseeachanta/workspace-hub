"""Dagster evaluation — software-defined assets for engineering data pipeline.

Models a realistic O&G engineering data flow:
  raw_well_data → validated_wells → production_summary

Demonstrates:
  - Software-defined assets with type annotations
  - Asset dependencies (lineage)
  - Metadata logging for observability
  - Config for parameterized assets
  - Testability (assets are plain Python functions)

Issue: #1456
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dagster import (
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    asset,
    Definitions,
    define_asset_job,
    ScheduleDefinition,
)


# ---------------------------------------------------------------------------
# Asset 1: Raw well data (simulates extraction)
# ---------------------------------------------------------------------------
@asset(
    description="Simulated raw well data — stands in for an API fetch or file read.",
    group_name="engineering_data",
    compute_kind="python",
)
def raw_well_data(context: AssetExecutionContext) -> list[dict[str, Any]]:
    """Simulate extracting raw well records (would be API/file in production)."""
    records = [
        {"well_id": "W-001", "field": "GOM-A", "depth_ft": 8500, "status": "producing", "bopd": 1200.0},
        {"well_id": "W-002", "field": "GOM-A", "depth_ft": 9200, "status": "producing", "bopd": 850.5},
        {"well_id": "W-003", "field": "GOM-B", "depth_ft": 7100, "status": "shut-in", "bopd": 0.0},
        {"well_id": "W-004", "field": "GOM-B", "depth_ft": 11000, "status": "producing", "bopd": 2100.0},
        {"well_id": "W-005", "field": "GOM-C", "depth_ft": None, "status": "drilling", "bopd": None},
        {"well_id": "W-006", "field": "GOM-C", "depth_ft": 6800, "status": "producing", "bopd": 450.0},
    ]
    context.log.info(f"Extracted {len(records)} raw well records")
    return records


# ---------------------------------------------------------------------------
# Asset 2: Validated wells (transform — depends on raw_well_data)
# ---------------------------------------------------------------------------
@asset(
    description="Validated well records — nulls removed, schema checked.",
    group_name="engineering_data",
    compute_kind="python",
)
def validated_wells(
    context: AssetExecutionContext,
    raw_well_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate and clean well records.

    Drops records missing critical fields (depth_ft, bopd).
    Mirrors the Transformer pattern from scripts/data/pipeline/base.py.
    """
    valid = []
    dropped = 0
    for rec in raw_well_data:
        if rec.get("depth_ft") is None or rec.get("bopd") is None:
            dropped += 1
            context.log.warning(f"Dropped {rec['well_id']}: missing depth or production")
            continue
        valid.append(rec)

    context.log.info(f"Validated {len(valid)} wells, dropped {dropped}")
    return valid


# ---------------------------------------------------------------------------
# Asset 3: Production summary (aggregate — depends on validated_wells)
# ---------------------------------------------------------------------------
@asset(
    description="Per-field production summary aggregated from validated wells.",
    group_name="engineering_data",
    compute_kind="python",
)
def production_summary(
    context: AssetExecutionContext,
    validated_wells: list[dict[str, Any]],
) -> MaterializeResult:
    """Aggregate production by field and write summary JSON.

    Demonstrates MaterializeResult with rich metadata for UI observability.
    """
    from collections import defaultdict

    field_agg: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"well_count": 0, "total_bopd": 0.0, "max_depth_ft": 0}
    )

    for rec in validated_wells:
        f = rec["field"]
        field_agg[f]["well_count"] += 1
        field_agg[f]["total_bopd"] += rec["bopd"]
        field_agg[f]["max_depth_ft"] = max(field_agg[f]["max_depth_ft"], rec["depth_ft"])

    summary = dict(field_agg)

    # Write output alongside this script (gitignored)
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "production_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))

    context.log.info(f"Wrote summary for {len(summary)} fields to {out_path}")

    return MaterializeResult(
        metadata={
            "field_count": MetadataValue.int(len(summary)),
            "total_wells": MetadataValue.int(sum(v["well_count"] for v in summary.values())),
            "total_bopd": MetadataValue.float(sum(v["total_bopd"] for v in summary.values())),
            "output_path": MetadataValue.path(str(out_path)),
            "generated_at": MetadataValue.text(datetime.now(timezone.utc).isoformat()),
        }
    )


# ---------------------------------------------------------------------------
# Job + Schedule definitions
# ---------------------------------------------------------------------------
engineering_pipeline_job = define_asset_job(
    name="engineering_pipeline_job",
    selection=["raw_well_data", "validated_wells", "production_summary"],
    description="Materialize the full engineering data pipeline.",
)

daily_schedule = ScheduleDefinition(
    job=engineering_pipeline_job,
    cron_schedule="0 6 * * *",  # 6 AM daily
    description="Daily materialization of engineering data assets.",
)


# ---------------------------------------------------------------------------
# Dagster Definitions (entry point)
# ---------------------------------------------------------------------------
defs = Definitions(
    assets=[raw_well_data, validated_wells, production_summary],
    jobs=[engineering_pipeline_job],
    schedules=[daily_schedule],
)
