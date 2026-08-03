# Handover — finish PII epic #3095 (CTA-B functional scripts + CTA-C closeout)

**For a fresh session.** This is the entry prompt to finish the last of the public-repo client-PII remediation (epic [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095), sub-issue [#3098](https://github.com/vamseeachanta/workspace-hub/issues/3098)). **PII-free by construction** — no client names here; the names live only in the private maps below.

## State (as of 2026-06-15)
Epic is ~98% done and merged. Every client-PII surface is remediated **except 14 functional dev-ops scripts**: generated artifacts (#3097), prevention guard (#3099), registry relocation + prose + data + config (#3098 P1/P2/P3a), both coupled clusters (doc-index, registry), inert code, stray scratch, all client-named filenames, incidental code, and the first 2 git scripts (#3160) — all merged.

## Remaining work = 14 files (CTA-B) + closeout (CTA-C)

These 14 hardcode **repo-name lists / a routing table** they then commit/push/`cd`/route into — so a blind codename-rename breaks them (the renamed name no longer matches the real sibling dir). Verify the exact set first — **derive the client-name regex from the private map** (no names committed in this doc):
```
MAP=config/agents/.client-codename-map.local.yaml
PAT=$(grep -oE "pattern: '[^']+'" "$MAP" | sed "s/pattern: '//; s/'$//" | grep -vE '^/mnt|ansys|-ws' | paste -sd'|')
git grep -lI -iE "$PAT" -- . | grep -vE '\.local$'
```
Expected (group by structure):
- **bash, flat/array list** → `scripts/coordination/git/{resolve_repos,remove_assetutilities_submodule}.sh` (resolve_repos has a `diverged_repos=()` array; remove_assetutilities is a finished one-off — consider `git mv` to `_archive/` instead of refactor)
- **bash associative map** → `scripts/coordination/git/merge_and_cleanup_branches.sh` (`declare -A repos_with_branches` = repo→branch-pattern)
- **windows batch** → `scripts/windows/{claude_repo_switcher,daily_routine_repos,setup_claude_repos,verify_claude_setup}.bat` (read list from a file via `for /f`)
- **python list** → `scripts/automation/{install_factory_enhanced.sh,setup_agent_links.sh,setup_all_commands.py,sync_engineering_data_context.py,sync_enhanced_specs.py,sync_slash_command_ecosystem.py}`
- **python routing table** → `src/ace/router.py` (command→repo dict → externalize to a gitignored JSON)

## The verified, SAFE pattern (use this)
Only change **how the repo list is acquired** — leave the commit/push/route logic byte-identical. Then you can verify the list-acquisition in isolation and **never need to run the destructive commit/push code**.
- Source the list from a **gitignored** file, with a sensible fallback (dynamic sibling-discovery for "all-repos" scripts; hard error for specific-subset scripts). Pattern landed in `scripts/coordination/git/batch_commit_all.sh` (#3160) — copy it.
- Provision file already exists on dev hosts: **`config/.sibling-repos.local`** (gitignored, 23 repos, one per line). For the repo→branch map and the routing table, externalize to their own gitignored `.local`/JSON.

## Provisioning + private maps (present on ace-linux-1/2; gitignored)
- `config/agents/.client-codename-map.local.yaml` — hyphen codename map (string data)
- `aceengineer-strategy/pii-remediation/3097-2026-06-14/client-codename-map.code-safe.yaml` — **underscore** map (use for any client name that is a CODE IDENTIFIER, e.g. a function/variable name — hyphens are invalid in identifiers)
- `config/.client-wikis.local.yml`, `config/.sibling-repos.local`
- Canonical copies live in private `vamseeachanta/aceengineer-strategy`.

## Gotchas (all learned the hard way this epic)
1. **Hyphen vs underscore:** codenames use hyphens (`lng-a`, `client-a`, `mkt-a`, `proj-a`). Hyphens are fine in strings/keys/paths but **break Python/shell identifiers** → use the underscore map for identifier positions only.
2. **Machine-hostname collision:** the overloaded short marketing token also appears in dev-fleet **machine hostnames** (`…-ace-win-1`, `…-ace-win-2`). The refined map excludes those (`(?!-ansys|-ws)`); do NOT redact hostnames (functional, tied to real hardware). A prior over-redaction corrupted 85 files — fixed in #3149.
3. **Can't run commit/push scripts** to verify — that's why the pattern changes only list-acquisition.
4. **#3099 guard is live + strict** (CI `legal-client-pii-gate` + pre-commit). Run it on changed files before pushing:
   `uv run python scripts/legal/check-client-pii.py --map config/agents/.client-codename-map.local.yaml <files>` (it withholds matched values; reads the `LEGAL_CLIENT_MAP` secret in CI).
5. **Pre-existing test noise:** `tests/readiness` + `tests/workstations` have ~30 env-dependent failures on clean `main` — always diff against a clean-baseline run to isolate redaction-caused failures.
6. **`config/ai-tools/provider-*.json`** may be cron-regenerated — if it re-accumulates client names, fix its emitter (separate follow-up).

## Workflow per cluster
branch from `main` → externalize list-acquisition (copy #3160 pattern) → `bash -n`/`ast` syntax-check → run touched tests, diff vs clean baseline → guard-check changed files → commit (pathspec form) → PR → **user merges** (per-PR authorization; never self-merge public main).

## CTA-C — closeout (after the 14 land)
1. Full sweep proves **0 client identifiers repo-wide** (the PAT above + `\bacma\b` minus `-ansys|-ws`, minus `*.local`).
2. Write counts-only artifact under `analysis/`.
3. Comment + close **#3096, #3097, #3098, #3099** then the epic **#3095**.
4. Note `git`-history scrub is explicitly OUT of scope (HEAD-only accepted).

## Auto-memory
Full epic history + every decision is in `~/.claude/projects/-mnt-local-analysis/memory/public-repo-pii-epic-3095.md` — read it first.
