# Claude agent-team prompt: session-log portability transfer

Use this prompt as a single self-contained handoff to Claude Code for implementation.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Session-Log Auditor
3. Cross-Machine Knowledge Curator
4. Adversarial Reviewer / Integrator

Do not ask the user any questions.

Objective:
Review/analyze session logs available on this machine, identify durable learnings that should travel to other machines/users, and transfer those learnings into the repo ecosystem in a conservative, reusable way.

Core intent:
- Use real session artifacts, not guesses.
- Promote only durable, reusable learnings.
- Prefer repo-tracked docs/memory surfaces over machine-local notes.
- Avoid broad refactors; make focused portability improvements.

Important current context:
- The repo already has provider-session export/audit infrastructure.
- Current audit artifacts include:
  - `analysis/provider-session-ecosystem-audit.json`
  - `docs/reports/provider-session-ecosystem-audit.md`
  - `logs/orchestrator/README.md`
- Relevant local native session stores may exist at:
  - `~/.codex/sessions/`
  - `~/.gemini/tmp/`
  - `~/.hermes/`
  - repo-local `logs/orchestrator/<provider>/session_*.jsonl`
- The repo has unrelated dirty/untracked files already present. Do not touch them.

Allowed write paths for this run only:
- `docs/reports/2026-04-11-session-log-portability-transfer.md`
- `logs/orchestrator/README.md`
- `.claude/memory/KNOWLEDGE.md`
- `.claude/memory/topics/session-log-portability.md`

Read-only context paths you should inspect as needed:
- `analysis/provider-session-ecosystem-audit.json`
- `docs/reports/provider-session-ecosystem-audit.md`
- `logs/orchestrator/README.md`
- `docs/ops/legacy-claude-reference-map.md`
- `.claude/memory/agents.md`
- `.claude/memory/templates/agents-template.md`
- `.claude/memory/KNOWLEDGE.md`
- `.claude/memory/topics/*.md`
- `scripts/memory/bridge-hermes-claude.sh`
- local native session paths under the home directory if needed for grounding

Forbidden paths:
- any path not listed in Allowed write paths
- `scripts/**`
- `tests/**`
- `config/**`
- `.planning/**`
- `docs/plans/**`
- `.claude/state/**`
- any unrelated dirty or untracked file already in the worktree

Critical correction from prior run:
- A previous attempt drifted into `docs/plans/README.md`, which is OUT OF SCOPE.
- If that file is currently modified by your prior attempt, do not touch it further and do not include it in any commit.
- This run must complete using ONLY the allowed write paths above.

Success condition:
By the end of this run, the repo should contain a concise, durable transfer package that helps other machines/users understand and reuse the high-value session-log learnings from this machine.

Required outcomes:
1. Create a focused transfer report at `docs/reports/2026-04-11-session-log-portability-transfer.md`.
2. Update `logs/orchestrator/README.md` if the session-log review reveals missing or unclear operator guidance about what should be exported, audited, or promoted.
3. Update `.claude/memory/KNOWLEDGE.md` with only the most durable, high-signal, cross-machine learnings that belong in institutional memory.
4. Create/update `.claude/memory/topics/session-log-portability.md` with the richer operational guidance that is too detailed for `KNOWLEDGE.md`.
5. Keep all changes tightly scoped and immediately useful to future agents on other machines.

Quality bar for what counts as a transferable learning:
- durable across sessions/machines
- operationally useful to future agents/users
- specific enough to change behavior
- grounded in observed session artifacts or the current audit
- not just a one-off task outcome

Examples of likely good learning categories:
- what artifacts are local-only vs repo-tracked
- which audit/export outputs are canonical
- how stale-path drift should be interpreted
- what native provider stores exist and why they matter
- how to convert machine-local observations into repo-portable guidance

Examples of bad learning categories:
- temporary TODOs
- one-off issue status
- raw counts without interpretation
- transient execution logs copied into memory

Execution steps:

STEP 1 — Ground in actual artifacts
- Read the current provider audit JSON/Markdown and `logs/orchestrator/README.md`.
- Inspect enough native/local session evidence to confirm the repo artifacts reflect real machine-local sources.
- Identify the highest-value durable learnings and the biggest portability gaps.

STEP 2 — Curate transfer-worthy learnings
- Separate:
  - durable institutional knowledge
  - detailed operational guidance
  - ephemeral observations that should NOT be promoted
- Be conservative: fewer strong learnings are better than many weak ones.

STEP 3 — Implement the transfer package
- Write the transfer report with:
  1. scope and sources reviewed
  2. durable learnings selected for promotion
  3. portability gaps found
  4. exactly where each promoted learning was placed in the repo ecosystem
  5. residual non-portable items that intentionally remain local-only
- Update README/memory/topic files only where this improves future reuse.

STEP 4 — Adversarial review before finalizing
- Challenge each promoted learning:
  - Is it truly durable?
  - Is it grounded?
  - Does it belong in that target file?
  - Would another machine/user benefit from it?
- Remove anything too local, too noisy, or too speculative.

Git safety rules:
- First inspect `git status --short`.
- Do not modify or stage unrelated dirty/untracked files.
- Stage only the allowed write paths explicitly by file path.
- Never use `git add .` or broad globs.
- If the worktree is too dirty to proceed safely, stop and report that clearly.

Verification required before finishing:
- confirm only allowed write paths changed
- confirm promoted learnings are grounded in audited session artifacts
- confirm `KNOWLEDGE.md` remains concise and institutional
- confirm the new topic file adds detail without duplicating the short memory entry verbatim
- confirm the transfer report explains what was promoted and why

Git discipline:
- If changes are made, stage only the allowed paths.
- Commit message:
  - `docs(memory): transfer durable session-log learnings into repo ecosystem`
- Push to `origin main` after commit.

Final response format in the Claude run:
1. Sources reviewed
2. Durable learnings promoted
3. Exact files changed
4. Verification performed
5. Commit SHA
6. Residual local-only observations not promoted
