# Disagreement report — plan #2675 (2026-05-12)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE (claude CLI failed, rc=124: SessionEnd hook [node \"${CLAUDE_PLUGIN_ROOT}/scripts/session-lifecycle-hook.mjs\" SessionEnd] failed: Hook cancelled ) |
| codex | UNAVAILABLE (codex CLI failed, rc=124: Reading additional input from stdin... ) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

(no findings unique to this provider)

### gemini

- Plan §Resource Intelligence Summary claims `config/agents/provider-capabilities.yaml` and `config/agents/routing-config.yaml` exist and quotes line excerpts. These files do not exist anywhere in the repository.
- Plan §Resource Intelligence Summary claims `config/ai-tools/agent-capability-scores.yaml`, `config/ai-tools/pricing.yaml`, and `config/ai-tools/subscriptions.yaml` exist. These files do not exist.
- Plan §Resource Intelligence Summary claims `scripts/review/` contains multiple `submit-to-*.sh` scripts, `cross-review.sh`, `attest-plan-claims.sh`, and 1,437 review result files. The scripts and the `scripts/review/` directory do not exist.
- Plan §Evidence claims `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` exist as root adapters. `AGENTS.md` and `GEMINI.md` do not exist, and `CLAUDE.md` does not exist at the repository root.
- Plan §Gaps Identified claims `config/agents/{codex,gemini,hermes}/` are empty skeleton directories. `list_directory` confirms these directories do not exist.
- Plan §Standards claims `docs/standards/CONTROL_PLANE_CONTRACT.md` and `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md` exist. These files do not exist.
- Plan §Documents consulted claims `docs/BUSINESS_BRAIN.md` and `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` exist with specific byte counts. These files do not exist.
- Plan §Risks and Open Questions claims "Memory files live under `~/.claude/projects/.../memory/` per machine". Verification shows the `feedback_*.md` files are actually located at `/tmp/llm-wiki/wikis/engineering/raw/papers/` within the repository.

