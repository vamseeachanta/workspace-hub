# Session handoff — CLAUDE.md retirement, auto-load restore, harness enforcement

**Date:** 2026-08-01
**Scope:** workspace-hub + 25 sibling repos
**Outcome:** complete for everything reachable from this machine; 2 issues blocked on on-box/owner input

---

## What was done

### 1. CLAUDE.md harness surfaces retired (owner decision)

All three CLAUDE.md surfaces deleted. **AGENTS.md is now the sole canonical contract.**

- `CLAUDE.md` (repo adapter), `.claude/global/CLAUDE.md` (orphaned; mandated a `Task` tool that no longer exists), `~/.claude/CLAUDE.md` (generated machine stub)
- Verified before deleting: all 8 governance tokens (`SHARED_SOUL.md`, `issue-planning-mode`, `_template-issue-plan.md`, `Adversarial Review`, `USER APPROVES`, `status:plan-approved`, `status:plan-review`, `TDD`) present in AGENTS.md — the *content* survived; only Claude's auto-load path was removed
- **Three regenerators guarded**, else the deletion silently reverses: `bootstrap-machine.sh` (now *removes* a stale stub), `generate_agent_adapters.sh` (every mode called `update_repo $WORKSPACE_ROOT`), `propagate-slash-commands.sh` (seeded Agent-OS-era content)

**Siblings:** of 38 non-archived repos, **27** had a CLAUDE.md → 22 deleted directly, 3 via merged PR, **2 retained by owner decision**:
- `llm-wiki` — carries the agent-context privacy firewall + concurrent-agent claim protocol + codes/standards routing. Real policy, not boilerplate.
- `gmail-archive` — genuine repo documentation.

### 2. Claude auto-load restored — as a symlink

`~/.claude/CLAUDE.md` → `config/agents/claude/SOUL.runtime.md`, installed by `install-soul-runtime.sh`, same shape as `~/.hermes/SOUL.md` / `~/.codex/AGENTS.md`.

Deleting the adapter had left Claude the **only** provider whose runtime never reached its sessions. The symlink is *better coverage than the original*: the old repo `@import` only fired when cwd was inside workspace-hub; the machine link loads in every cwd.

`install-soul-runtime.sh` is now OS-aware — under MSYS a bare `ln -s` **copies** instead of linking, which would have silently reintroduced duplicate content that never tracks rebuilds. It now forces `winsymlinks:nativestrict`, verifies with `-L`, removes stray copies (guarded to plain files, never a reparse point), and exits non-zero.

Self-heal widened from 2 → 4 machines (added `gpu-claw`, `macbook-portable`).

### 3. Latent defects found and fixed

| Defect | Fix |
|---|---|
| R5 context budget summed 3 of 7 files and passed — a *missing* file scored greener than a large one | Missing candidate now FAILS and names it (#3744) |
| 4 rules files deleted in `2fb3bdc7c` but every reference survived, incl. `SHARED_SOUL.md` Hard Gates 6/7 | 3 of 4 dropped, 1 re-pointed (#3745) |
| `strict-scan` delegated to a workflow needing a secret that **never existed** — it had never run a real check | Runs `legal-sanity-scan.sh` inline (#3747) |
| `Scheduler Mutation Surface Guard` red on every PR — a **true positive** ignored for weeks | Re-affirmed #3475 digest after review (#3748) |
| `harness-install-doctor` recorded OK when the installer linked nothing | Parses the summary; non-vacuous regression test (#3753) |
| `validate-schedule.py` ran in **neither CI nor pre-commit** | Wired into the enforcement gate (#3754) |

---

## Repo state at exit

| | |
|---|---|
| `origin/main` | `4cd0928b9` — **green** (`scheduler-mutation-main.yml` success) |
| local `main` | `72ca7aead` — **3 ahead / 5 behind**, diverged |
| Session branches | none — all deleted, remote and local |
| Open PRs from this session | none |

**The divergence is not from this session.** The 3 local commits are all `chore(sync): auto-sync 2026-08-01`, written by the auto-sync process. Fast-forward is blocked by modified cron-generated `.claude/state/*` files. This is the machine's normal steady state and self-heals; it was observed to reconcile twice during the session.

---

## Residue audit

**CLEAN** — no session branches, no worktrees, no uncommitted work of mine. Every PR verified MERGED by content (squash rewrites SHAs, so reachability proves nothing).

**EXPECTED** — local `main` diverged via auto-sync (above); modified `.claude/state/*` and `docs/reports/machine-equality-matrix.html` are cron-generated and owned by other processes; scratchpad holds backups of all 30 deleted CLAUDE.md files (session-scoped; git history is the durable copy).

**UNEXPECTED — needs attention:**
- **PR #3733 is superseded.** It touches only `docs/reports/issue-3475-command-identity-inventory.json` (last updated 2026-07-31) and is titled "partial — attestation bump needs owner re-verification". PR #3748 regenerated that exact file *and* bumped `source_digest` *and* re-rendered the HTML audit. #3733 should be closed as superseded, not merged — merging it would re-stale the digest chain.
- PRs #3732, #3739 remain open from prior sessions; untouched and unreviewed here.

---

## Open work

### #3750 — Windows Task Scheduler parity (BLOCKED, on-box)

Three independent blockers, any one fatal:

1. **The `scheduler: windows-task-scheduler` catalog entries are dead config.** `scripts/windows/scheduler-yaml.ps1` — the only YAML reader the applier has — contains **zero** `command` references. `setup-scheduler-tasks.ps1:291-295` requests 4 hardcoded ids, none of them the 5 `windows-task-scheduler` entries. All 5 carry a literal `/path/to/workspace-hub`. Two are shadowed by hardcoded tasks that behave differently.
2. **Structurally unobservable.** `collect-equality.sh:284-290` skips the scheduler probe on Windows, so those boxes report `job_count: unknown`. Nothing can detect the tasks don't exist.
3. **Registration is `physical-local`** per `.claude/rules/scheduler-mutation-safety.md` — must run **on** the box.

The only working mechanism is `windows_script:`, used by exactly one task (`equivalence-sentinel`).

**Owner decision required:** delete the 5 phantom entries (but `hermes-consistency-check.sh:168-179` asserts those `<id>-win` strings are *declared*, so that check breaks too), or wire the applier to read them (real PowerShell work, edits a `migration-required` mutation surface, turning a config PR into a registry PR).

### #3751 — RDS host onboarding (BLOCKED, owner input)

Not in `config/workstations/registry.yaml`, so it cannot appear in any task's `machines:` list. A read-only discovery prompt was supplied to the owner to gather identity/capability facts. Its hostname carries a client-org prefix — **must not enter tracked files, commit messages, or PR titles/bodies.**

---

## Traps worth carrying forward

1. **`--check-html` reads DISK on one side and the git INDEX on the other** (`check-scheduler-mutation-surfaces.py:347` vs `:88`). Local `main` on this box routinely lags, so it produces false "stale" verdicts. **Check the workflow's own conclusion for the SHA before claiming main is broken** — I got this wrong once this session.
2. **`digest_record_union` covers the CI workflows themselves** (`scheduler_mutation_contract.py:154-171`), including `enforcement-gate.yml`. Editing enforcement config stales the audit — deliberately, so enforcement cannot be silently weakened. Order: stage → `--render-html` → stage the HTML.
3. **`Client-PII Gate` scans commit MESSAGES and PR title/body**, not just changed files. Redacting the file is not enough; the commit object must be replaced. The matched value is withheld from public logs by design.
4. **`gh api <404> --jq` prints the error JSON to stdout** — a non-empty check treats `{"message":"Not Found"}` as valid data. Check exit status.
5. **This mount reports every file as `rwxrwxrwx`** — never derive git file mode from `os.stat()`; take it from the base tree. `git push` also stalls here; build tree/commit/ref via the GitHub Git Data API instead.

---

## No external actions taken

No emails, no Telegram, no client-facing communication. All changes are repo commits and GitHub issues/PRs in `vamseeachanta/*`.
