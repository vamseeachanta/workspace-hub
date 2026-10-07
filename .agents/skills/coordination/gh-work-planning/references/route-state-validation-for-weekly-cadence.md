# Route-state validation for weekly cadence/report generators

Use when planning fixes for weekly freshness reports, OSS watchlists, roadmap boards, or other generated artifacts that route findings to GitHub issues.

## Durable lesson

A validator that only detects closed issue targets is not enough. If normal offline report generation can still render a closed issue as the recommended update/action target, the defect remains in the user-facing workflow.

Plans for route-map/reporting defects must require both:
1. runtime prevention in the normal generation path, and
2. live-state validation for closeout/future drift detection.

## Planning checks

During resource intelligence, inspect all routing sources:
- committed route-map data files
- hardcoded fallback/default route constants in generator scripts
- helper functions that apply route-map values to rendered rows
- prior generated reports that show the bad route in user-facing output
- live GitHub state for the referenced issue numbers

During plan drafting, require tests for:
- missing route-map/default fallback behavior
- slug/entity-specific closed route behavior
- normal offline rendered output safety
- live validator behavior against GitHub issue state, when applicable

## Safe target behavior

If a child issue is closed and no new open child owns the lane, route generated update actions to the open roadmap/umbrella anchor instead of the closed child issue. The plan should name the anchor issue explicitly and verify it is open.

## Anti-pattern caught by adversarial review

Weak plan shape:
- add a validator that flags closed routes
- leave report generation itself unchanged
- update only route-map data while scripts still contain closed hardcoded defaults

Strong plan shape:
- change route maps and generator defaults
- normalize closed routes before rendering normal output
- add a live validator for future drift
- prove with TDD that normal offline output cannot point users at closed issues by default
