# Workspace Hub Root / Harness / Worktree Review

Date: 2026-05-20T13:42:14-05:00
Repo: `/mnt/local-analysis/workspace-hub`
Mode: planning/review only — no destructive cleanup performed.

## Evidence consulted

- `AGENTS.md` — hard gates, tier-1 workflow, `uv run`, commit/push policy.
- `docs/standards/PARALLEL_FIRST_EXECUTION.md` — active `single-lane` / `parallel-readonly` / `parallel-worktree` execution contract.
- `config/workstations/registry.yaml` — workstation registry and current repo placement hints.
- `scripts/agents/tier1-repos.sh` — canonical tier-1 repo manifest.
- `docs/ops/machine-inventory.md` — machine inventory and path placeholders.
- `docs/reports/fleet-harness-status.md` — current fleet harness status surface.
- `docs/plans/2026-05-19-issue-2751-cross-platform-harness-setup.md` — cross-platform harness plan context.
- `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md` — worktree-aware tier-1 gate plan context.
- `docs/sessions/2026-05-01-session-closeout-worktree-pr-sweep.md` and `docs/sessions/2026-05-02-worktree-branch-closeout-ledger.md` — closeout debt and cleanup lessons.
- `scripts/cron/harness-update.sh` and `scripts/readiness/harness-config.yaml` — harness readiness/update conventions.
- Fresh root inventory via `git ls-files`, `git status --short --untracked-files=normal`, and root filesystem scan.

## Current live state snapshot

- Current branch: `main`.
- Known HEAD from fresh `git worktree list --porcelain`: `277a855ee9a1534145a346a8b38bcb2b9faf7e69`.
- Registered worktrees: only `/mnt/local-analysis/workspace-hub` on `main` in this checkout.
- Working tree is dirty with unrelated modified/untracked state. Do not treat this report as a cleanup commit boundary.

## Recommended harness/reference architecture

### Core decision

`workspace-hub` should be the canonical control-plane/harness repo. Tier-1 sibling repos should consume it by stable repo-tracked contracts, not by duplicating runtime state or copying hidden folders ad hoc.

### Tier-1 repo manifest authority

Use `scripts/agents/tier1-repos.sh` as the canonical repo list until replaced by a richer machine-aware registry. Current manifest:

- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `worldenergydata`
- `assethold`
- `aceengineer-website`
- `llm-wiki`

### Per-machine placement authority

Use the machine-specific issues as the decision records:

- `#2754` — `ace-linux-1`
- `#2755` — `ace-linux-2`
- `#2756` — `licensed-win-1`
- `#2757` — `licensed-win-2`

Each machine issue should decide:

1. Which tier-1 repos exist locally.
2. Which repos are write-capable vs reference-only on that machine.
3. Which machine-specific data mounts are required.
4. Whether the repo checkout is primary, mirror/reference, or absent.
5. How the harness is connected: symlink, config entry, wrapper script, or read-only reference.

### Sibling repo harness contract

Recommended shape:

1. `workspace-hub` owns canonical agent skills, standards, planning docs, review scripts, dispatch scripts, workstation registry, and harness readiness scripts.
2. Sibling repos keep their own source/tests/docs, but reference `workspace-hub` for shared governance and agent harness behavior.
3. Runtime/provider-local state stays outside sibling repos unless explicitly promoted as durable evidence.
4. Secrets and machine-specific credentials stay local only (`~/.hermes`, OS credential store, env vars), never under repo-tracked sibling state.
5. Machine-local placement is resolved by the per-machine issues before cloning/moving/deleting sibling repos.

### Path convention

Use sibling checkouts under a common parent, not nested checkouts inside `workspace-hub`:

- Linux preferred: `/mnt/local-analysis/<repo>`
- Current `workspace-hub`: `/mnt/local-analysis/workspace-hub`
- Worktrees: use an external worktree parent such as `/mnt/local-analysis/agent-worktrees/<repo>-issue-<NNN>-<slug>` or a clearly governed repo-local `.worktrees/` only after policy approval.

Do not place tier-1 sibling repo checkouts under `workspace-hub/` subfolders. That is the main confusion point captured by issue `#2758`.

## Recommended work execution lifecycle

### Up-front execution classification

Before work starts, classify as one of:

1. `single-lane` — tight/shared files, small fix, or high merge-conflict risk.
2. `parallel-readonly` — discovery/review/recon only; no writes.
3. `parallel-worktree` — approved implementation with disjoint owned paths.

Implementation still requires issue plan approval and TDD.

### Worktree lane contract

For any write-capable `parallel-worktree` lane, the prompt/issue plan must include:

- issue number and approved plan path;
- worktree absolute path;
- branch name;
- owned paths;
- read-only paths;
- forbidden paths;
- test/validation commands;
- handoff artifact path;
- explicit local commit permission or prohibition.

### Closeout transaction

Issue/PR closeout should be atomic, under a lock such as `.git/agent-closeout.lock`:

1. Revalidate issue/PR state and branch ancestry.
2. Run required tests/checks or verify GitHub checks are green.
3. Commit intended durable evidence/artifacts only.
4. Push to origin.
5. Merge only if GitHub reports clean/mergeable and checks pass.
6. Delete merged local and remote branch.
7. Remove owned worktree.
8. Verify `HEAD == origin/main`, ahead/behind `0/0`, clean status, and remaining worktrees.
9. Only then close/mark the issue complete.

If cleanup is not safe, preserve explicitly and record why in a session ledger or issue comment.

## Root classification

### Keep at root / canonical root entries

These are acceptable at root based on current repo role or common tooling conventions:

- Agent/provider config or canonical harness folders: `.agents`, `.claude`, `.codex`, `.gemini`, `.hermes`, `.planning`
- Git/tool config: `.cz.toml`, `.gitattributes`, `.github`, `.gitignore`, `.gitleaks.toml`, `.jscpd.json`, `.large-files-exclusions.yaml`, `.legal-deny-list.yaml`, `.mcp.json`, `.pre-commit-config.yaml`
- Top-level agent docs: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `MEMORY.md`, `README.md`
- Source/package/test/docs: `src`, `tests`, `scripts`, `docs`, `config`, `templates`, `docker`, `assets`, `examples`, `pylib`, `pyproject.toml`, `uv.lock`
- Current domain/control folders that need later architecture review but should not be deleted in a cleanup sweep: `_archive`, `admin`, `analysis`, `coordination`, `knowledge`, `queue`, `state`, `tools`

### Relocate/archive tracked root artifacts

These are tracked and should not be deleted blindly. They should be moved via a reviewed cleanup issue/plan into `docs/archive/`, `docs/reports/`, `docs/sessions/`, `logs/`, or domain-specific folders as appropriate:

- Broken/accidental zero-byte markdown-fragment filenames: `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Status:**`, `Defines`, `Planning`
- Runtime/prototype tracked folders that need owner decision: `.hive-mind`, `.nightly-results`, `.SLASH_COMMAND_ECOSYSTEM`, `.swarm`, `.tmp-inspect-2348`, `.venv`, `claude_unattended_test_accept`, `generated`, `knowledge-base`, `logs`, `monitoring-dashboard`, `notes`, `output`, `reports`, `specs`
- Temporary tracked scripts/artifacts: `.tmp-build-commit.py`, `claude_smoke_prompt.txt`, `nohup.out`
- April Gmail/email artifacts: `ace_cfp_sending_kit_2026-04-09.md`, `ace_gmail_triage_2026-04-09.txt`, `daily_gmail_action_digest_2026-04-09.md`, `draft_ace_api_cfp_note.md`, `draft_skestates_1099_followup_email.md`, `draft_skestates_hoa_transfer_email.md`, `draft_skestates_pest_exteriors_followup.md`, `final_skestates_1099_followup_email.md`, `final_skestates_hoa_transfer_email.md`, `final_skestates_pest_exteriors_followup.md`, `gmail_copy_paste_packet_2026-04-09.md`, `gmail_operator_packet_2026-04-09.md`, `gmail_presend_checklist_2026-04-09.md`, `gmail_sendready_status_2026-04-09.md`, `gmail_thread_reply_map_2026-04-09.md`, `personal_gmail_triage_2026-04-09.txt`, `sendready_skestates_1099_email.md`, `sendready_skestates_hoa_email.md`, `sendready_skestates_pest_email.md`, `skestates_gmail_triage_2026-04-09.md`
- Historical issue/review artifacts at root: `issue-1839-gh-comment.md`, `issue-1839-impl.diff`, `issue-1839-next-slice-impl.diff`, `issue-1839-next-slice-review.md`, `issue-1839-review.md`, `issue-1858-impl.diff`, `issue-1858-review.md`, `terminal-2-impl.diff`, `terminal-2-review.md`
- Media/transcript artifacts: `transcript_raw.json`, `video_summary.txt`, `youtube_summary.txt`
- Root docs candidate: `docs-reorg-assessment.md`

### Delete after explicit confirmation — untracked generated/cache only

These are untracked generated/cache/build artifacts and are cleanup candidates after one final `git status` and secret-sensitive inspection where relevant:

- `.baseline-cache`
- `.cache`
- `.coverage`
- `.mypy_cache`
- `.pytest_cache`
- `.ruff_cache`
- `.test_performance.db`
- `.uv-cache`
- `.venv-manim`
- `.venv-test`
- `claude_smoke.log`
- `dist`
- `node_modules`
- `prompts`
- `tmp`
- `workspace_hub.egg-info`

### Needs special handling

- `.env` — local secret/config; keep local, ensure ignored, never commit.
- `.env.example` — tracked template; keep at root unless config architecture moves templates under `config/`.
- `.ops`, `.sync-reports`, `.vscode`, `.worktrees` — untracked but inspect before deleting; `.worktrees` may become policy-relevant.
- `data` — tracked and substantial. Do not move/delete in a root cleanup sweep; requires data-governance and repo-location decision because workspace-hub has explicit raw/private/public data routing concerns.

## Recommended next action

Create a dedicated cleanup plan issue before moving tracked root artifacts. Split into two transactions:

1. **Safe untracked cleanup**: remove confirmed cache/build artifacts and patch `.gitignore` gaps.
2. **Tracked root relocation**: move historical artifacts into durable archive/report/session locations with `git mv`, update references, and verify no root clutter remains.

Do not combine this with machine repo-placement decisions. Machine placement issues decide where repos live; root cleanup decides how `workspace-hub` itself is organized.
