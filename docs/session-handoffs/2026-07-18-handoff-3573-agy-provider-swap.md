# Session handoff — #3573: agy replaces gemini as the third worker/reviewer provider

> **Date:** 2026-07-17 → 2026-07-18 · **Lane:** lane:claude (Fable 5, interactive) · **Status:** ✅ COMPLETE — issue closed, all PRs merged

## What shipped

User directive: *"use agy instead of gemini as the worker, reviewer, etc."* Landed in three phases, each planned → adversarially reviewed → user-approved → merged:

| Phase | PR | Merge commit | Scope |
|---|---|---|---|
| Plan | [#3573](https://github.com/vamseeachanta/workspace-hub/issues/3573) | — | T3 plan in issue body; reviews: Claude r1 MINOR, **Agy r2 MAJOR (4 findings, all folded in)**, Codex UNAVAILABLE ×2 (→ #3578) |
| 1 | [#3574](https://github.com/vamseeachanta/workspace-hub/pull/3574) | `a03d1a9` | Routing SSoT (`routing-config.yaml` + regenerated `tier_router.sh`), review gate `[codex, agy]`, fanout/cross-review dispatch via `submit-to-agy.sh`, provider tuples in 9 `scripts/ai` tools, tests |
| 2 | [#3575](https://github.com/vamseeachanta/workspace-hub/pull/3575) | `331cd23` | `model-registry` + `provider-capabilities` + `drift-policy` + `sync-items`; `config/agents/agy/` SOUL delta + runtime; SHARED_SOUL cross-review = **Claude + Codex + Agy**; cost-ceiling policy |
| 3 | [#3576](https://github.com/vamseeachanta/workspace-hub/pull/3576) | `3e8edba` | Readiness probes (`agy --version`), cost tracker, statusline row = agy; parity comment fixes |

**Ops applied outside PRs:** `agent:agy` label created; 5 open `agent:gemini` issues migrated (#1962 #2003 #2005 #2006 #2733); `agent:gemini` marked DEPRECATED.

## Key semantics (for future sessions)

- `agy` is a **first-class provider token**. `TOKEN_TO_CLI: copilot → agy`. `"gemini"` survives only as a deprecated alias (run_agent wrapper map, cross-review reviewer arg) and as legacy-audit registry sections.
- **Reviewer-lane hardening** (from Agy's own adversarial review of the plan): `AGY_REVIEW_MODE=1` makes oversize payloads FAIL (exit 3) instead of truncating — a truncated diff can false-APPROVE. A parseable-artifact failure is `INVALID_OUTPUT` and **blocks**; only provider-UNAVAILABLE degrades T3 → T2.
- agy contract: prompt rides `--print` (argv, 1 MB cap), no JSON mode, verdict via tolerant `VERDICT:` trailer parsing; settings at `~/.gemini/antigravity-cli/settings.json` (display-label model, pinned by #3086 script).
- **Equality/parity row key stays `gemini`** (denotes the Gemini surface incl. agy) — per-host snapshot schema; rename is the #3579 migration.

## Verification evidence

- Suites: `tests/ai` 175✓ · `scripts/ai/tests` 98✓ (exec-bit failure fixed in Phase 2) · parity 20/20 · fanout bash 25/25 · tier-table drift guard ✓.
- **Live smoke:** real agy dispatch through the new lane caught a planted bug → `VERDICT: MAJOR` parsed by `normalize-verdicts.sh`; oversize dispatch exits 3 with reason.
- Merges content-verified on `origin/main` (`git show origin/main:<path>`), not via merge-commit reachability.

## Traps hit and banked

1. **NTFS-FUSE working copies cannot store exec bits** → scripts/mocks committed 100644; on ext4 checkouts PATH-mocks silently fell through to REAL provider CLIs and `[[ -x ]]` gates skipped. Spot-fixed in scope; repo-wide sweep = [#3577](https://github.com/vamseeachanta/workspace-hub/issues/3577).
2. **`submit-to-codex.sh` stdin-hang** (exit 124, "Reading additional input from stdin...") twice despite the #3294 mitigation → [#3578](https://github.com/vamseeachanta/workspace-hub/issues/3578). Cross-review degraded T3→T2 both times — quietly weakens the gate.
3. Both standing PR CI reds (`strict-scan/authority` empty AUTH_ENVELOPE; Scheduler Mutation Surface Guard stale digest) are **pre-existing fleet-wide** — they fail on every recent branch and are not required checks.
4. Working method for this repo on ace-linux-1: porcelain git hangs on the FUSE mount → do implementation in an **ext4 sparse clone** (`git clone --filter=blob:none --sparse` into session scratch, `sparse-checkout set scripts config tests .github .claude docs/...`), push branches from there.

## Open follow-ons (all filed, none dangling)

- [#3577](https://github.com/vamseeachanta/workspace-hub/issues/3577) exec-bit audit + Level-2 CI guard
- [#3578](https://github.com/vamseeachanta/workspace-hub/issues/3578) submit-to-codex stdin-hang regression
- [#3579](https://github.com/vamseeachanta/workspace-hub/issues/3579) equality/parity `gemini` → `agy` row rename (cross-machine snapshot migration; after soak)
- [#3580](https://github.com/vamseeachanta/workspace-hub/issues/3580) gemini CLI uninstall decision (~2026-08-01, after 2-week agy soak; `~/.gemini/` homedir must survive — agy lives under it)

## Repo/machine state at exit

- `origin/main` @ `3e8edba` carries all three phases; no unmerged branches for this work (feature branches deleted at merge).
- Canonical FUSE checkout `/mnt/local-analysis/workspace-hub`: untouched by this session (reads only), on `main`; will pick up changes on next pull/auto-sync.
- Session scratch clone `/tmp/claude-1000/.../scratchpad/wh-3573`: disposable; contains no unpushed work beyond this handoff commit.
- No external/outward actions taken beyond GitHub (PRs, issue ops, label migration) — no emails, no deploys.
- Equality matrix: not manually rebuilt (cron self-heals; #3579 owns the row rename).
