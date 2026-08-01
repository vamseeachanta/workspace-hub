# Session handoff — ace-win-1 ecosystem reconcile + equality publish + PII remediation

- **Date:** 2026-06-28
- **Box:** `ace-win-1` (Windows; reformatted and renamed since its original build). Checkout: `D:\ws\workspace-hub`.
- **Scope:** ran `/reconcile-ecosystem` flow (pull → plan → apply → equality), published this box's equality column, then discovered + remediated a client-PII collision in the box's new hostname.

> NOTE: the box's current OS hostname collides with a private client codename and is deliberately **kept out of this doc** (and out of all tracked files). Refer to it as `ace-win-1` — the canonical role alias. Its prior public hostname is likewise kept out of tracked files.

## Outcome (state at exit)
- `main` is **synced with origin/main** (behind 0 / ahead 0), working tree clean except 3 pre-existing untracked nested-repo dirs (`acma-projects/`, `doris/`, `seanation/`).
- This box's equality column is **live as `ace-win-1`** and **token-clean on origin/main HEAD** (verified `git grep` = 0).
- No work was discarded. The pre-session dirty tree is preserved as a stash (see Preserved state).

## What was done
1. **Get current** — pre-session tree was dirty (modified `.claude/state/session-signals`, deleted `heavyequipemnt-rag`, ~40 untracked `.diag_*/.sr_*/.fix_*` temp files). Stashed (not discarded) → `stash@{...}: reconcile-prep ace-win 2026-06-26_1051`. Then `git pull --ff-only` (was 2186 behind). Added `safe.directory` (checkout owned by a different local account than the session user).
2. **Reconcile plan (read-only)** — AUTO-SAFE: 0. NEEDS-APPROVAL: `llm-wiki` 49k dirty, workspace-hub 10 stashes, workspace-hub untracked dirs. OPERATOR-ONLY: `uv` missing.
3. **Apply AUTO-SAFE** — no-op (AUTO-SAFE was 0); nothing destructive ran.
4. **Tooling** — installed `uv` (0.11.25) via **winget** (`astral-sh.uv`); it self-provisions CPython, so no system Python/jq needed for the matrix. (Binary under `…\WinGet\Packages\astral-sh.uv_…\uv.exe`.)
5. **Equality** — collected this box's column on clean `main` (`ahead 0/behind 0`, else the matrix grades STALE-CHECKOUT per `build-equality-matrix.py:is_stale`) and published the column + rebuilt matrix to `main`. Verdicts for `ace-win-1`: compute/data_access **CONFORMS**; solvers **BELOW-BASELINE** (orcawave absent); harness/kanban/memory **NO-MAJORITY**, skills/behavior/scheduler **DIVERGES**; session_curation / skill_currency / memory_freshness / skill_link_health + 12 provider-capability cells **MISSING-EVIDENCE**.
6. **PII discovery + remediation** — the convenience host-map change (register the box's hostname → `ace-win-1`) tripped the **Client-PII Gate**: the new hostname matches a private client codename (false positive — it's own infra, but the gate is authoritative). The same string had also ridden into the published `equality-ace-win-1.yaml` (direct push bypasses the PR-only gate). Remediation:
   - Sanitized the YAML host fields to the box's canonical role alias `ace-win-1` and pushed (HEAD now token-clean).
   - **Closed PR #3279** (host-map change can't be public) and **deleted both pushed branches** to clear the token from origin refs.
   - The Windows cp1252 matrix-write crash the branch also fixed is **already on main** via **#3278 / #2998** — no action needed.
   - Set persistent **`RECONCILE_MACHINE=ace-win-1`** (User env) so reconcile autodetects this box with no hostname in tracked code; `collect-equality.ps1` uses `-Machine ace-win-1`.

## External actions taken (this session)
- Pushed to `origin/main`: equality publish (`43871a875`, later **sanitized** by `727a2b892`).
- Created then **closed** PR **#3279**; deleted both pushed branches (the host-map branch and a redundant UTF-8 branch) to clear the token from origin refs.
- No issues opened/closed beyond #3279; no other repos pushed.

## Preserved state (intentional — not discarded)
- `stash@{...} reconcile-prep ace-win 2026-06-26_1051` — the pre-session dirty tree. Restore with `git stash apply` (use the matching ref from `git stash list`); review before dropping.
- 9 older stashes (pre-existing, not from this session) — still NEEDS-APPROVAL to inspect/drop.
- `llm-wiki` ~49,110 dirty paths — **untouched**; NEEDS-APPROVAL.
- Untracked `acma-projects/ doris/ seanation/` (nested repos) and local branches `chore/wrk-470-windows-merge-fix`, `merge-main` — pre-existing, not mine; left as-is.

## Caveat
- The colliding hostname remains in **git history** (from the original `43871a875` publish). A purge rewrites shared history / force-push — destructive and not worth it for a false-positive infra hostname. Recommend leaving it.
- Future equality publishes from this box re-leak the hostname (collector writes `host: <COMPUTERNAME>`) until the durable fix lands. This box's equality cron is **not** enabled (`job_count: 0`), so no automation will trip it; don't run a raw publish/`-RefreshMatrix` here until then.

## Next steps
1. **Durable PII fix — chosen path: allowlist** (user-owned, off-repo). The redactor map (`scripts/legal/redact-client-pii.py`) has no allowlist primitive — tighten the one rule whose `pattern` matches the hostname (e.g. add a negative lookaround for the `acma-…-ace-win-1` context; note `word_bound` only guards letter-flanking, not hyphen/digit). Update the `LEGAL_CLIENT_MAP_SECRET` CI secret.
2. **Verify before re-landing** — drop the updated map at `config/agents/.client-codename-map.local.yaml` (gitignored) and run, against a scratch file containing the hostname: `uv run --with pyyaml python scripts/legal/redact-client-pii.py --map <map> --dry-run <scratch>` (goal: 0 replacements), then `check-client-pii.py --strict` (PASS) — locally, before any public push.
3. **Reland host-map natively** once green: re-add the host→`ace-win-1` mapping in the 4 maps, fresh PR, confirm Client-PII gate green, merge. Then native autodetect + publishing work; the `RECONCILE_MACHINE` override can be dropped (harmless to keep).
4. **Residual reconcile items** (unchanged): `llm-wiki` 49k dirty, 10 stashes, `orcawave` licence probe (PR #2850); MISSING-EVIDENCE provider-capability + audit cells need a provider-harness collection run on this box.
