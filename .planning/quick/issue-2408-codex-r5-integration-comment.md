Integrated the latest Codex review result from `review-2408-codex-r5.out` into the planning record for #2408.

Latest Codex signal:
- still NOT approval-ready
- primary blocker remains discoverability from actual live entrypoints, not just canonical-doc references

Newly reinforced blocker points:
1. discoverability needs to be evaluated by entrypoint traversal, not phrase presence only
2. the plan still assumes canonical-doc anchors are sufficient even though live root adapters (`CLAUDE.md`, `GEMINI.md`) remain in the reading path
3. provider-entrypoint normalization pressure is still leaking back into #2408, which confirms the split to #2421 was the right boundary

Recommendation after this review:
- keep #2408 narrowly scoped
- do not ask for approval yet
- treat #2421 as the required normalization lane for entry-surface convergence
- next work should be either:
  a. prepare a cleaner review bundle for #2408 focused on entrypoint-traversal evidence, or
  b. plan #2421 so the normalization dependency is no longer implicit
