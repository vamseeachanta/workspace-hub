Another focused #2045 patch wave landed locally after Codex rereview11:

- made #2046/#2047 exemplar handling explicitly read-only under #2045
- added `docs/standards/HARD-STOP-POLICY.md` and `.claude/hooks/plan-approval-gate.sh` into the retrieval/intel story
- strengthened exemplar validation from structural-only to structural + semantic checks
- rewrote the operational workflow test around allowed policy states (pre-approval vs post-approval)
- added an explicit note that missing `gh` auth must be treated as an environment-precondition code, not a workflow failure
- clarified why `.codex/config.toml` may remain validation-only while `.codex/CODEX.md` is in implementation scope

Launching another focused Codex rerun now.
