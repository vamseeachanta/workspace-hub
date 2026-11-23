# Branch Protection Rollout — 2026-06-07

Ecosystem-wide pass to protect `main` (the key branch) across all vamseeachanta repos, triggered by GitHub's "Your main branch isn't protected" banner on deckhand.

## Design: tiered protection via repo rulesets

| Tier | Rules | Intent |
|---|---|---|
| **A — PR-only** | `deletion` + `non_fast_forward` + `pull_request` (0 approvals, self-merge OK; merge/squash/rebase allowed) | Shared/library repos with PR-flow convention |
| **B — basic** | `deletion` + `non_fast_forward` | Direct pushes to main stay allowed; only force-push and branch deletion blocked |

All rulesets target `~DEFAULT_BRANCH`, no bypass actors (applies to admins too).

## Applied state (verified via `/rules/branches/<default>` API)

### Tier A — PR required
| Repo | Ruleset | Notes |
|---|---|---|
| worldenergydata | `protect_repo` (pre-existing, active) | Also enforces 13 strict status checks |
| digitalmodel | `protect-main` 17369753 (new) | **No status checks** — main CI baseline is red (engine + native segfault); requiring checks would deadlock merges |
| assetutilities | `main_protect` 295352 (re-enabled + PR rule added) | Was disabled |
| deckhand-sandbox | `deckhand-protect-default` 17366924 (PR rule added) | Already used PR flow |
| hobbies | classic branch protection (pre-existing) | PR-required, untouched |

### Tier B — force-push/delete blocked
workspace-hub (17369764), teamresumes (17369765), raw-to-knowledge-playbook (17369766), assethold (17369767), kaggle-rogii-2026 (17369768), worldenergydata-wiki (17369770), pdf-large-reader (17369771, default `master`), aceengineer-website (`protect_default` 6704008 re-enabled).

### Unprotected — paywalled
All 22 private repos (deckhand, llm-wiki-*, aceengineer-strategy, aceengineer-admin, client repos, achantas-*, etc.). Branch protection/rulesets on private repos require **GitHub Pro** on a personal account — API returns 403 "Upgrade to GitHub Pro or make this repository public".

## Plan findings (2026-06-07)
- Personal account `vamseeachanta`: **Free** (403 message is definitive).
- Org `aceengineer` (user is admin): **Free** plan, 1 seat, 0 private repos — also can't protect private repos.
- The existing annual GitHub-ish payment is likely Copilot Individual (no branch protection included). Confirm at github.com/settings/billing.

## Open items
1. **Decide**: GitHub Pro ($4/mo personal) vs. do-nothing for private repos (solo-owned; main risk is self/agent force-push).
2. If Pro: replicate Tier A on deckhand + aceengineer-strategy, Tier B on remaining private repos. Template payloads are in this doc's tier definitions; create via `gh api -X POST repos/vamseeachanta/<repo>/rulesets`.
3. Optional free stopgap: git-guardrails Claude Code hook to block destructive git commands agent-side.

## Operational impact
- Tier-A repos: commit on `chore/...`/topic branches, open PR, self-merge allowed (digitalmodel: user merges per convention).
- Tier-B repos incl. workspace-hub: direct push workflow unchanged.
- Multi-repo sync scripts must not force-push anywhere (now hard-blocked on all public repos).
