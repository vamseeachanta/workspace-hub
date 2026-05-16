# Codex Provider Delta
> Inherits identity, gates, and must-fire rules from [`../SHARED_SOUL.md`](../SHARED_SOUL.md). This file carries only Codex-specific operating-model differences.
> **Operational runtime artifact**: [`./AGENTS.runtime.md`](./AGENTS.runtime.md) — `~/.codex/AGENTS.md` symlinks to this. Verified 2026-05-16 (Phase 5): Codex CLI base instructions explicitly cite `AGENTS.md` as the loaded surface.
> Reference artifact: [`./SOUL.runtime.md`](./SOUL.runtime.md) — built for review parity; NOT loaded by Codex CLI.

# Codex-Specific Operating Model

## Sandbox Capability — Inspect, Don't Assume

**Codex runtime capabilities vary by session.** Do NOT hardcode universal "NO shell exec" or "NO local filesystem writes" rules. Before performing local writes or shell exec:

1. Inspect the active `sandbox_mode` declared by the environment (e.g., `workspace-write` exposes both shell exec and bounded filesystem writes; tighter modes may block both).
2. Inspect the tool list actually available in the current session.
3. If shell exec is available, use it. If blocked (typical symptom: `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`), fall back to `js_repl` + GitHub MCP connector for file/issue access.

Do NOT generalize a single-session sandbox failure to a permanent constraint. (`feedback_codex_sandbox_no_execution`, `feedback_codex_sandbox_fallback_paths`)

## Pre-Exec Pushed-Artifact Requirement

Codex `exec` (and the Codex GitHub connector) cannot read local files outside the sandbox. Before invoking `codex exec` on a plan or artifact:

- **Push the plan/issue to GitHub first.** Codex's GH connector can fetch tracked content; local-only files are invisible. (`feedback_codex_needs_pushed_artifact`)
- For inline-prompt review, the prompt body itself may be passed via `codex exec "$PROMPT"`; this works without push.

## Authentication and Quota

- Verify Codex/OpenAI subscription auth status before load planning. Don't assume parallel paid seats without machine-specific auth evidence.
- `~/.codex/auth.json` carries the active token; `~/.codex/auth.lock` indicates active session.
- Quota exhaustion produces specific exit codes; `submit-to-codex.sh` exits 3 on quota → triggers Opus fallback in `cross-review.sh`.

## Known CLI Regressions

- **CLI 0.124, 0.130** — periodic upstream regressions in `codex exec` stdin handling. Symptoms: `UNAVAILABLE (codex CLI failed, rc=0: Reading additional input from stdin)`. (`feedback_codex_cli_0_124_upstream_regression`)
- Check `codex --version` against `feedback_codex_cli_*` memory files before assuming a new bug.

## Adversarial Review Posture

- Sustained-MAJOR loop hazard: if Codex returns MAJOR for 3+ rounds while Claude/Gemini land at MINOR by v3, surface as consensus-vs-minority — do not auto-cycle blindly. (`feedback_codex_sustained_major_loop`)
- Codex reviews via GitHub connector when local shell is blocked. Connector-derived evidence (file existence, line contents, link resolution) MUST be locally re-verified before applying as a fix. (`feedback_cross_provider_review_payoff`, `feedback_r1_review_trust_hazard`)
- Codex review iteration cap: 3 per WRK/non-WRK plan; `submit-to-codex.sh` enforces via `review-iteration.yaml` for WRK-scoped work.

## Skill Loader

- `~/.codex/skills/` is currently empty on this machine; `.codex/skills/` symlinks to `.claude/skills/` (workspace-hub canonical).
- Codex roles vs skills mapping: `.claude/docs/codex-roles-vs-skills.md`.
- Parity audit: `specs/architecture/work-queue-codex-parity.md`.

## Required Gates (Codex-specific extensions to SHARED_SOUL Hard Gates)

Beyond the SHARED_SOUL.md Hard Gates, Codex sessions additionally enforce:

1. **Every implementation task maps to a WRK-* in `.claude/work-queue/`** OR a GitHub issue per the broader workspace `feedback_no_reserved_wrk_ids` rule. Codex's `submit-to-codex.sh` Stage-5 gate validates WRK evidence when `--wrk-id` is supplied.
2. **Workflow lifecycle skills are mandatory**: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` + `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` for WRK-mode work.
3. **Coding style guardrails**: max 400 lines/file, max 50 lines/function, snake_case Python, camelCase JS — see `.claude/rules/coding-style.md`.
4. **Git workflow**: conventional commits, branch prefixes (`feature/`, `bugfix/`, `chore/`) — see `.claude/rules/git-workflow.md`.

## Bootstrap Hazard — `~/.codex/AGENTS.md` Untracked Generator

`~/.codex/AGENTS.md` on this machine contains a `sed`-derived copy of `~/.claude/CLAUDE.md` with `s/claude/Codex/g` substitutions (broken — should have been `s/claude/codex/g`). Resulting `.Codex/memory/` path is wrong (capital C). The generator is NOT in any tracked script. (`feedback_codex_bootstrap_untracked_sed_origin` — write-time pending)

The fix is `scripts/agents/install-soul-runtime.sh` (per [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719) Phase 4) which symlinks `~/.codex/AGENTS.md` to the committed `config/agents/codex/AGENTS.runtime.md` artifact, bypassing the broken sed pattern entirely.
