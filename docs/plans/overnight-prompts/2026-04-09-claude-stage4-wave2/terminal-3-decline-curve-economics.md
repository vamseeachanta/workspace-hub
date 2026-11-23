We are in /mnt/local-analysis/workspace-hub.

Issue: vamseeachanta/workspace-hub#2054 — Production Decline Curve to Economics Cashflow Model
Status: Not started. Single-file source change plus tests.

Tasks:
1. Read current state:
   - digitalmodel/src/digitalmodel/field_development/economics.py lines 1-50
   - digitalmodel/src/digitalmodel/field_development/economics.py lines 410-445
   - digitalmodel/src/digitalmodel/field_development/economics.py lines 610-640
2. Add DeclineType enum near the top: exponential, hyperbolic, harmonic, linear.
3. Add 3 optional fields to EconomicsInput:
   - decline_type: DeclineType = DeclineType.LINEAR
   - decline_rate: float = 0.0
   - b_factor: float = 0.5
4. Add __post_init__ validation:
   - hyperbolic requires 0 < b_factor < 1
   - non-linear decline requires decline_rate > 0
5. Extract _production_factors(economics_input, years) -> list[float].
6. Replace duplicated production factor logic in both annual cashflow builders with _production_factors().
7. Add tests in digitalmodel/tests/field_development/test_economics.py for:
   - enum members and defaults
   - decline factor shapes
   - validation errors
   - backward compatibility
8. Run tests:
   - cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v --tb=short
   - cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short
9. Post a gh issue comment on #2054 summarizing implementation.
10. Request Codex cross-review on the changed files after implementation.

Allowed write paths:
- digitalmodel/src/digitalmodel/field_development/economics.py
- digitalmodel/tests/field_development/test_economics.py

Negative write boundaries:
- digitalmodel/src/digitalmodel/field_development/benchmarks.py
- digitalmodel/src/digitalmodel/field_development/concept_selection.py
- worldenergydata/
- scripts/
- .claude/
- docs/

Verification:
- cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v --tb=short 2>&1 | tail -20
- cd digitalmodel && uv run python -c "from digitalmodel.field_development.economics import DeclineType, EconomicsInput; print(list(DeclineType)); print('OK')"
- cd digitalmodel && uv run pytest tests/field_development/ -v --tb=short 2>&1 | grep -E '(PASSED|FAILED|ERROR)' | tail -10
