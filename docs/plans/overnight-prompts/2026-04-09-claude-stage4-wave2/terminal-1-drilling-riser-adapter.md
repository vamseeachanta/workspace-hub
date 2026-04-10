We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2063 — Wire Drilling Riser Components into Analysis
Status: Not started. All prerequisites met. This is a green-field adapter following the proven pattern at digitalmodel/src/digitalmodel/naval_architecture/ship_data.py:150.

Tasks:
1. Read the existing adapter pattern:
   - digitalmodel/src/digitalmodel/naval_architecture/ship_data.py lines 140-200
2. Read the CSV schema:
   - head -5 worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv
3. Create digitalmodel/src/digitalmodel/drilling_riser/adapter.py:
   - normalize_riser_component_record(row: dict) -> dict
   - register_riser_components(csv_path: Path) -> list[dict]
   - compute_riser_string_weight_kn(components: list[dict], lengths_m: list[float]) -> float
4. Update digitalmodel/src/digitalmodel/drilling_riser/__init__.py with 3 new exports.
5. Create digitalmodel/tests/drilling_riser/test_adapter_integration.py with tests for:
   - normalize single record
   - register loads CSV (expect 36)
   - normalized schema keys
   - string weight basic case
   - empty list returns 0.0
   - missing field behavior
6. Update digitalmodel/tests/drilling_riser/conftest.py with a fixture loading raw CSV rows.
7. Run tests:
   - cd digitalmodel && uv run pytest tests/drilling_riser/ -v --tb=short
8. Post a gh issue comment on #2063 summarizing implementation.
9. Request Codex cross-review on the changed files after implementation.

Allowed write paths:
- digitalmodel/src/digitalmodel/drilling_riser/adapter.py
- digitalmodel/src/digitalmodel/drilling_riser/__init__.py
- digitalmodel/tests/drilling_riser/test_adapter_integration.py
- digitalmodel/tests/drilling_riser/conftest.py

Negative write boundaries:
- digitalmodel/src/digitalmodel/drilling_riser/riser_analysis.py
- digitalmodel/src/digitalmodel/drilling_riser/stress.py
- digitalmodel/src/digitalmodel/naval_architecture/
- worldenergydata/ (read-only for CSV)
- scripts/
- .claude/
- docs/

Verification:
- cd digitalmodel && uv run pytest tests/drilling_riser/test_adapter_integration.py -v
- cd digitalmodel && uv run python -c "from digitalmodel.drilling_riser import normalize_riser_component_record, register_riser_components, compute_riser_string_weight_kn; print('All 3 exports OK')"
- cd digitalmodel && wc -l src/digitalmodel/drilling_riser/adapter.py
