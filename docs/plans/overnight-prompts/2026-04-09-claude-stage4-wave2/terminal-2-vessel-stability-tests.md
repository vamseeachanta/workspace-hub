We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2059 — Real Vessel Stability Test Cases (Sleipnir, Thialf, Balder)
Status: Not started. All infrastructure is complete — this is test-only work.

Tasks:
1. Read existing test patterns:
   - digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
2. Read the vessel CSV:
   - head -20 worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv
3. Add BALDER_RECORD fixture dict matching CSV columns.
4. Add TestCSVBulkRegistration with:
   - test_register_17_vessels
   - test_all_have_required_keys
5. Add TestThreeVesselStabilityPipeline parametrized over Sleipnir, Thialf, Balder with tests for:
   - register and compute GZ curve
   - positive metacentric height
   - draft_estimated=True for Sleipnir and Balder
6. Add docstrings noting assumed vs measured parameters.
7. Run tests:
   - cd digitalmodel && uv run pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short
8. Post a gh issue comment on #2059 summarizing test coverage added.
9. Request Codex cross-review on the changed files after implementation.

Allowed write paths:
- digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
- digitalmodel/tests/naval_architecture/conftest.py

Negative write boundaries:
- digitalmodel/src/
- worldenergydata/ (read-only for CSV)
- scripts/
- .claude/
- docs/

Verification:
- cd digitalmodel && uv run pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short 2>&1 | tail -20
- cd digitalmodel && grep -c "def test_" tests/naval_architecture/test_vessel_fleet_adapter.py
