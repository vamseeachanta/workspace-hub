# Fresh-Session Handoff — Orchestrate Codex implementation of #2802

**Date:** 2026-05-26 · **For:** a fresh Claude Code session (avoid context rot from the originating session) · **Repo:** `/mnt/local-analysis/workspace-hub`

## Your mission (this session)

Delegate the implementation of **[#2802](https://github.com/vamseeachanta/workspace-hub/issues/2802)** (kanban auto-add reconciler) to **Codex** via the installed `codex` plugin's broker, monitor it, then run the code-stage adversarial review before handing the PR back to the user. **You orchestrate; Codex implements. You do NOT implement #2802 yourself, and you do NOT merge.**

## Background (what already happened — don't redo)

- #2795 (domain + machine/provider dispatch) is **merged (#2796, #2799) and CLOSED**. 1,485 issues were labeled (`machine:`/`dispatch:`/`domain:`/`ai:`). Adversarial review found + fixed a P1 (dispatch:ready re-add) post-merge.
- #2797 is the **open refinement track** (dev-primary rebalance, provider-cap vs machine-cap, `priority:` backfill, `bsee`/`hse` population). Not your job now.
- #2802 is **`status:plan-approved`** — plan v2 is reconciler-primary (scheduled GitHub Action, single committer, self-healing). Read the issue body for the full plan.
- A ready-to-use Codex prompt exists at `docs/session-handoffs/2026-05-26-codex-handoff-2802-kanban-reconciler.md` (rev 2).

## Preflight (run first)

```bash
cd /mnt/local-analysis/workspace-hub
gh issue view 2802 --repo vamseeachanta/workspace-hub --json state,labels   # confirm OPEN + status:plan-approved
node ~/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs status --all --json  # broker health
git branch --show-current   # likely fix/2795-... (a stale, already-merged local branch — see "Environment gotchas")
```

## Delegate to Codex (the supported, sandbox-safe path)

> **CORRECTION (2026-05-26, #2804):** the original claim "use the broker, app-server = no bwrap" was WRONG. The broker only avoids bwrap for *runtime boot*; Codex's *shell/tool calls* still invoke `/usr/bin/bwrap`, which fails nested under Claude on Ubuntu 24.04 (`bwrap: loopback`/`uid map`) because AppArmor blocks unprivileged user namespaces. The real fix is the one-time host setup in [`scripts/install/setup-codex-sandbox.sh`](../../scripts/install/setup-codex-sandbox.sh) (AppArmor `userns` grant for `/usr/bin/bwrap` + `network_access=true`). AFTER that setup, BOTH the broker and raw `codex exec` work. See [[feedback_codex_sandbox_write_blocked]] and #2804.

Once the #2804 setup is in place, use the plugin broker (Claude orchestrates async). `Bash(node:*)` is already allowlisted; `--write` lets Codex edit files; `--background` runs async.

```bash
PROMPT="$(sed -n '/^ROLE:/,/^PROMPT$/p' docs/session-handoffs/2026-05-26-codex-handoff-2802-kanban-reconciler.md | sed '$d')"
node ~/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs task --write --background "$PROMPT"
# capture the job id; then poll:
node ~/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs status --all --json
node ~/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/codex-companion.mjs result <job-id> --json
```
(Or simply read the rev-2 doc and pass its embedded prompt as the task text.)

## After Codex opens its PR

1. Verify it followed the gates: branch off main (local git, not API), TDD (tests before code), `Refs #2802` not `Closes`, no merge.
2. **Run the code-stage adversarial review** — the user invokes `/codex:adversarial-review --background` (user-only slash command; it's the clean app-server path), AND you can run a Claude adversarial subagent (`Agent` tool) on the diff. Surface findings; loop fixes through review.
3. Hand the reviewed PR to the **user to merge** (never self-merge; never self-apply `status:plan-approved`).

## Discipline (hard gates — non-negotiable)

- **Codex delegation = OpenAI spend.** Keep it explicit/user-triggered; one `task` per delegation, don't autonomously re-fire.
- **Never merge or self-approve.** User-in-loop is load-bearing.
- **Adversarial review before the user approves/merges** — both plan and code stage (`feedback_adversarial_review_before_user_approval`).

## Environment gotchas (will bite you otherwise)

- **Contaminated index:** the working tree has ~40 dirty files from parallel fleet sessions. NEVER `git add -A`. Use pathspec commits (`git commit -m .. -- <file>`). A pre-commit scanner blocks on the fleet's staged skill files; `commit --no-verify` is Iron-Law-banned.
- **Two uncommitted artifacts** (working-tree only, intentionally): the ai-orchestration board-YAML card add (#2795/#2797/#2802 cards, already loaded into local Hermes/dashboard) and the two handoff docs. They land when the index clears or #2802's reconciler supersedes them.
- **Stale local branch:** `fix/2795-dispatch-review-findings` is merged but still checked out; switching off it is blocked by the dirty tree. Delete after the tree clears.
- **Push:** the pre-push tier-1/coverage gate fails environmentally (sibling repos not checked out); `git push --no-verify` is sanctioned for that (push only — never commit). Post-commit autosync may push for you; verify `git rev-parse HEAD` vs `origin/<branch>` rather than retrying on `[rejected]`.
- **Codex CLI** hangs sometimes; the broker path avoids it, but if a raw codex call stalls, `</dev/null` or interactive session.

## Pointers
> **SUPERSEDED execution path (2026-05-26, #2804):** the canonical, route-correct broker prompt for executing #2802 now lives in the merged durable handoff **`docs/session-handoffs/2026-05-26-codex-pilot-2802.md`** (PR #2812) — broker dispatch + AppArmor setup + worktree abort-on-fail + commit-pinned TDD + provenance contract. Prefer it over the rev-2 `--dangerously-bypass` prompt referenced below (that approach was rejected; see #2804 review trail).
- Plan: #2802 body · Codex prompt (historical/superseded): `docs/session-handoffs/2026-05-26-codex-handoff-2802-kanban-reconciler.md`
- Dispatch tooling (reuse patterns): `scripts/dispatch/route.py`, `.claude/memory/kanban/{SCHEMA,domains,routing-rules,manifest}.yaml`
- Memory: `feedback_adversarial_review_before_user_approval`, `feedback_codex_needs_pushed_artifact`, `project_dispatch_provider_capacity`
