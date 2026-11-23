Integrated the newly surfaced Gemini review findings for #2408 into the local plan draft.

Applied tightening:
- made the thin-adapter line-limit test source its limit from `.claude/rules/coding-style.md` rather than an implied magic number
- strengthened the canonical-anchor test to use concrete path assertions rather than vague “consistent references” language
- added an explicit test that the upgrade playbook references actionable workspace-hub operational paths (`scripts/_core/sync-agent-configs.sh`, `config/agents/`)

This reinforces the current recommendation:
- keep #2408 on the strict canonical-doc strategy
- keep provider-entrypoint normalization in follow-up issue #2421
- seek a fresh clean review rerun only after the review-tooling lane is stable
