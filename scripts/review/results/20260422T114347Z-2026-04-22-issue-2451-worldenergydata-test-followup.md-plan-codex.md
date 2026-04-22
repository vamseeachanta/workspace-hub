### Verdict: MAJOR

### Summary
The plan is well-researched, but two blocking problems remain: its default Cluster C path is still not actually executable to closure, and Cluster A's diagnosis logic does not collect the evidence needed to distinguish package-install failure from pytest-plugin registration failure. Those gaps make the implementation path ambiguous and likely to stall or drift in scope.

### Issues Found
- [P1] Cluster C is still internally contradictory at the execution level. The plan says the default implementation path is C-skip for stabilization, but it also says #2451 cannot close unless a supported non-legacy NPV assertion is added; the resource-intel section simultaneously states no non-legacy replacement entry point was identified during planning. That means the default path is not a real closure path and will likely force a mid-execution replan. Either make C-skip explicitly a non-closing stabilization-only branch up front, or require entry-point discovery before approval.
- [P1] Cluster A lacks a decisive verification step for pytest plugin registration. `import pytest_benchmark` under `uv run --all-extras` only proves the package is importable, not that pytest loaded the plugin or exposed the `benchmark` fixture. Without an explicit check such as `pytest --fixtures`, `pytest --trace-config`, or equivalent runner-log evidence, the A1a vs A1b branch decision can still be made on incomplete evidence.
- [P2] The RED/GREEN commands for Cluster C do not line up cleanly with the documented failure mode. The plan's Step 0 uses `--collect-only` and greps for `ModuleNotFoundError|ImportError`, but the resource summary says `test_current_npv_implementation.py` is legacy-API-bound throughout and `test_cash_flow_components.py` may already skip via `skipif`. That leaves a gap between the documented runtime regression and the proposed baseline proof, making it hard to know when Cluster C is actually fixed versus merely no longer failing collection.
- [P2] Scope is drifting from CI-unblock into product-behavior revalidation. Requiring a new supported-path automated NPV assertion before closure may be desirable, but it is materially broader than the issue statement of removing the three runtime-test failure clusters. If that broader requirement is intentional, the plan should say the issue scope has expanded; otherwise it should move that work to a follow-up tracker and keep #2451 focused on the failing test surface.
- [P3] Several acceptance criteria still bundle delivery with repo-administration mechanics, especially branch naming, push topology, issue creation, and PR workflow. Those controls are useful, but they obscure the actual technical done-state and make review harder because a technically correct fix could still fail the plan for process reasons unrelated to the regression itself.
- [P3] The benchmark branch does not define what evidence is sufficient from the failing CI log if historical logs are truncated or incomplete. The fallback mentions one temporary diagnostic CI run, but the exact outputs needed to choose A1a versus A1b are not specified, which weakens reproducibility for whoever executes the plan.

### Suggestions
- Make Cluster C a hard up-front decision: either require non-legacy NPV entry-point discovery before approval, or explicitly downgrade C-skip to a stabilization-only outcome that must open a separate follow-up and does not pretend to close the coverage question.
- Add a direct pytest-plugin verification step for Cluster A, for example checking fixture availability or plugin registration in the same execution mode used by CI, before allowing any workflow-file edit.
- Tighten Cluster C baseline and acceptance commands so they prove the actual failing behavior described in the issue, not just collection safety.
- Trim acceptance criteria down to observable technical outcomes, and move branch/PR/issue-administration rules into workflow notes only.

### Questions for Author
- Is #2451 intended to be a pure CI-unblock issue, or is it intentionally expanded to require restoring supported NPV-path automated coverage before closure? The plan currently mixes both goals.
- What exact command or CI evidence will be treated as authoritative for 'pytest-benchmark plugin loaded' versus merely 'pytest_benchmark package installed' on the runner?
