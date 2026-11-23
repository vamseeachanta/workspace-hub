"""Tests for Dagster evaluation assets.

Demonstrates Dagster's built-in testability — assets are plain Python
functions that can be unit-tested without spinning up infrastructure.

Issue: #1456
"""

from dagster import build_asset_context, materialize

from assets import raw_well_data, validated_wells, production_summary, defs


def test_raw_well_data_returns_records():
    """Raw extraction should return a non-empty list of dicts."""
    context = build_asset_context()
    result = raw_well_data(context)
    assert isinstance(result, list)
    assert len(result) == 6
    assert all("well_id" in r for r in result)


def test_validated_wells_drops_incomplete():
    """Validation should drop records with missing depth or production."""
    context = build_asset_context()
    raw = raw_well_data(context)
    valid = validated_wells(context, raw)
    # W-005 has None depth and bopd — should be dropped
    assert len(valid) == 5
    well_ids = {r["well_id"] for r in valid}
    assert "W-005" not in well_ids


def test_production_summary_aggregation():
    """Summary should aggregate by field correctly."""
    context = build_asset_context()
    raw = raw_well_data(context)
    valid = validated_wells(context, raw)
    result = production_summary(context, valid)
    # MaterializeResult has metadata
    assert result.metadata["field_count"].value == 3  # GOM-A, GOM-B, GOM-C
    assert result.metadata["total_wells"].value == 5


def test_full_pipeline_materialize():
    """End-to-end materialization through Dagster's API."""
    result = materialize(
        [raw_well_data, validated_wells, production_summary],
    )
    assert result.success


def test_definitions_loadable():
    """Verify Definitions object loads without errors (Dagster requirement)."""
    assert defs is not None
    job = defs.get_job_def("engineering_pipeline_job")
    assert job is not None
