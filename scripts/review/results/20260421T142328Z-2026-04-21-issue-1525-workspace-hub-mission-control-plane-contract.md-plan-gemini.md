### Verdict: APPROVE

### Summary
The plan is well-structured, feasible, and effectively addresses the identified gaps in the repository's mission control-plane contract. It successfully leverages strict scope boundaries and literal guardrail phrases to avoid preempting unresolved architectural decisions (like #2398) while consolidating the control-plane definition.

### Issues Found
- [P3] Minor: The plan defers the CI integration of the new validation script (`check_workspace_hub_mission_contract.py`) to an 'Open Question'. Not integrating the script into CI or pre-commit hooks immediately leaves the repo vulnerable to regression shortly after this PR merges.

### Suggestions
- Define an explicit starter list of the 'required' and 'forbidden' phrases directly in the plan so the implementation of `check_workspace_hub_mission_contract.py` is fully unambiguous.
- Resolve the open question regarding CI by explicitly creating a follow-up issue for CI integration and referencing it in the plan, or add CI integration to this plan's scope.
- Provide a concrete example or template for the 'mission pointer' that might be added to `AGENTS.md` to prevent scope creep during implementation.

### Questions for Author
- Will you create a follow-up issue for the CI integration of the validation script, or should it be incorporated into the acceptance criteria for this issue?
- What specific 'stale or overcommitting' forbidden phrases do you intend for the validation script to flag?
