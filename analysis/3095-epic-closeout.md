# Epic #3095 — Public-repo client-PII remediation: closeout (counts only)

Closeout record for epic [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095). **Counts only — no client identifiers.** The named inventory + client→codename maps live in the private `aceengineer-strategy` repo (the deny-list paradox: a public file naming the clients would itself be the leak).

## Final state

Repo-wide sweep with the authoritative engine (`scripts/legal/check-client-pii.py --all`, which reuses the redactor so guard ≡ redactor) over the integrated end-state of every remediation PR:

> **✓ 0 client identifiers across 21,350 tracked files.**

This is the live state once the CTA-B PRs (#3164–#3167) merge; it was verified on a local octopus-merge of all four branches (no conflicts).

## Sub-issues

| Sub-issue | Scope | State |
|---|---|---|
| [#3096](https://github.com/vamseeachanta/workspace-hub/issues/3096) | full multi-client sweep + categorization | assessment done (corrected to the full 9-client + 2-project registry scope) |
| [#3097](https://github.com/vamseeachanta/workspace-hub/issues/3097) | generated-artifact / session-log policy + remediation | **merged** ([#3102](https://github.com/vamseeachanta/workspace-hub/pull/3102)); see `analysis/3097-generated-pii-remediation.md` |
| [#3098](https://github.com/vamseeachanta/workspace-hub/issues/3098) | hand-authored docs/scripts scrub | **complete** — prose/data/config (P1–P3c, merged) + CTA-A/B below |
| [#3099](https://github.com/vamseeachanta/workspace-hub/issues/3099) | prevention hardening | **merged** ([#3108](https://github.com/vamseeachanta/workspace-hub/pull/3108)) |

## #3098 final tranche (this closeout)

### CTA-B — 14 functional dev-ops scripts ([#3165](https://github.com/vamseeachanta/workspace-hub/pull/3165), [#3166](https://github.com/vamseeachanta/workspace-hub/pull/3166), [#3167](https://github.com/vamseeachanta/workspace-hub/pull/3167))

These scripts hardcoded **client repo names** in lists/maps/routing tables they then commit / push / `cd` / route into — so a blind codename-rename would break them (the renamed name no longer matches the real sibling dir). **Verified-safe pattern:** change only *how the list is acquired* (source from a gitignored per-host file), leave commit/push/route logic **byte-identical** → verifiable without running the destructive code.

| Group | Files | Externalized to |
|---|---:|---|
| bash, coordination/git | 3 | `config/.sibling-repos.local` (+ dynamic fallback) / `config/.branch-cleanup.local` |
| bash, automation | 2 | `config/.repo-types.local` / usage-example only |
| python, automation | 4 | `config/.sibling-repos.local` via new `_sibling_repos.py` |
| python, ace CLI router | 1 | `config/.ace-routes.local` (client routes merged at import) |
| Windows batch | 4 | `config/.windows-repos.local` (read via `for /f`) |
| **CTA-B total** | **14** | |

### Closeout-sweep residuals ([#3164](https://github.com/vamseeachanta/workspace-hub/pull/3164))

Five identifiers **outside** the 14 scripts, surfaced only by the repo-wide sweep:

| File | Residual | Treatment |
|---|---|---:|
| `.planning/research/PITFALLS.md` | bare token in a referenced filename | codename-redacted |
| `data/document-index/shards/shard-00.json` | bare token in a path leaf | codename-redacted |
| `scripts/readiness/compare-harness-state.sh` | `check_acma()` fn | renamed `check_ace_win_1()` (host-accurate) |
| `scripts/email/gmail-digest.py` | client email domain in VIP set | externalized → `config/.vip-domains.local` |
| `config/quality/no-abs-paths-baseline.txt` | 7 stale pre-rename entries | refreshed to current filename |

### Engine precision fix (private map)

The redactor's `hdic` rule was tightened to an inline **alphanumeric** boundary so digit-adjacent hash fragments (e.g. a HuggingFace CDN id) stop false-matching, with no loss of any real reference. Map-only change (private + gitignored); the public engine and its `word_bound` semantics are unchanged.

## Prevention layer (#3099, live)

- `scripts/legal/check-client-pii.py` — name-agnostic guard (reuses the redactor engine; never echoes matched values into public CI logs).
- `.github/workflows/legal-client-pii-gate.yml` — strict CI gate reading the `LEGAL_CLIENT_MAP` repo secret.
- Pre-commit hook + `.claude/docs/client-pii-prevention.md`.

## Per-host provisioning

The real lists live **only** in gitignored `config/.*.local` files (one gitignore glob covers all). Committed PII-free `config/*.local.example` templates document each format. Canonical copies + a provisioning README are in private `aceengineer-strategy/pii-remediation/3098-provisioning/`.

| Provision file | Consumer |
|---|---|
| `.sibling-repos.local` | git batch/resolve/submodule scripts + automation syncs |
| `.branch-cleanup.local` | `merge_and_cleanup_branches.sh` |
| `.repo-types.local` | `install_factory_enhanced.sh` |
| `.ace-routes.local` | `src/ace/router.py` |
| `.windows-repos.local` | `scripts/windows/*.bat` |
| `.vip-domains.local` | `scripts/email/gmail-digest.py` |

## Out of scope

- **Git-history scrub** — HEAD-only remediation accepted; historical commits still carry identifiers.
- **Operator follow-up:** re-set the `LEGAL_CLIENT_MAP` CI secret + refresh the ace-linux-1 cron-host local map to pick up the `hdic` boundary fix (non-blocking — no normal PR touches the only digit-adjacent instances, two vendored reference docs).
