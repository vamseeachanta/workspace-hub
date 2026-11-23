# Session handoff — public-repo client-PII remediation (epic #3095)

**Date:** 2026-06-15 · **Host:** ace-linux-2 · **Scope:** epic [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095) (no client identifiers in the public `workspace-hub`).

This document is **PII-free by construction** (codenames/issue-numbers only — no client names). The named inventory + codename maps live in the private `aceengineer-strategy` repo.

## Merged this session (all on `main`)
| Sub-issue | PR | What landed |
|---|---|---|
| #3096 | — | Assessment corrected to the **full 9-client + 2-project** scope (source of truth: `config/client-wikis.yml`). |
| #3097 | #3102 | Generated-artifact remediation: stop-committed ~2,609 dump/inventory files, codename-redacted ~316 generated files. New name-agnostic `scripts/legal/redact-client-pii.py` + tests. |
| #3099 | #3108 | Prevention: `scripts/legal/check-client-pii.py` + `.github/workflows/legal-client-pii-gate.yml` (strict — `LEGAL_CLIENT_MAP` secret set) + pre-commit hook + `.claude/docs/client-pii-prevention.md`. |
| #3098 P1 | #3113 | Relocated `config/client-wikis.yml` private (public = pointer stub); consumers repointed; validator degrade-open on stub. |
| #3098 P2 | #3113 | Codename-redacted ~636 hand-authored prose files; git-mv 30 client-named files; relocated client sibling-repo ignores from `.gitignore` → local `.git/info/exclude`. |
| #3098 P3a | #3131 | Codename-redacted 153 functional **data + value-only-config** files. |

**Verification:** generated + prose + data scopes engine-verified **0 client identifiers**; JSON/YAML parse-clean; `main` test baseline green.

## Remaining work
- **#3098 Phase 3c — NOT done (scoped, validated approach):** ~86 code files (`.py/.sh`) + 2 behavior-coupled configs (`config/workstations/registry.yaml`, `scripts/data/document-index/config.yaml` — client names as mapping keys). A bulk redaction breaks ~87 tests (clean baseline = 0) because those tests **assert specific client values by design** — each cluster needs its **test expectations rewritten** to codenames, test-driven to green, one coupled cluster at a time. Code uses **underscore** codenames (identifier-safe); map preserved at `aceengineer-strategy/pii-remediation/3097-2026-06-14/client-codename-map.code-safe.yaml`. Demonstrated working on the document-index cluster (incl. renaming `*_wiki_unblock.py` to match redacted imports).
- **Git-history scrub:** out of scope (HEAD-only accepted).

## Per-host provisioning (required for the prevention layer)
Each dev/cron host needs three gitignored local files (provision from the private archive; see `.claude/docs/client-pii-prevention.md`):
- `config/agents/.client-codename-map.local.yaml` (redactor + pre-commit guard)
- `config/.client-wikis.local.yml` (registry consumers)
- client sibling-repo entries in `.git/info/exclude`
- CI: `LEGAL_CLIENT_MAP` repo secret (already set).

**Done:** ace-linux-2 (this host) + ace-linux-1 (cron host) both provisioned + verified (redactor + guard exercised).

## Repo states at exit
- **`workspace-hub` `main`:** `714cd9f66`, synced with origin (0 ahead / 0 behind), no tracked changes. Phase 3c reverted — `main` is green.
- **`aceengineer-strategy`:** clean, pushed (`e231d71`) — holds the named inventory, both codename maps (hyphen + underscore), the canonical registry, and the removed-content archive.
- **No open epic PRs.**

## Dirty exceptions / flags (nothing lost)
- **ace-linux-1 cron clone** is on feature branch `fix/cron-render-mkdir-and-flywheel-glob`, a few commits ahead with **unpushed cron-fix commits**; snapshot at `backup/ace1-presync-20260615`. → get it back on `main` + push those fixes.
- **ace-linux-2 stashes:** `stash@{0}` = recovered **mermaid-conventions skill-doc edit** (companion untracked dir `…/mermaid-conventions/references/`; not PII — review + commit separately); `stash@{1}` = old `network-mounts.jsonl` cron churn (droppable). Pre-resync snapshot at `backup/ace2-presync-20260615`.
- **Untracked on ace-linux-2:** `.local/` (stray) + the mermaid `references/` dir (pairs with `stash@{0}`).

## External actions taken (all operator-authorized)
- Merged #3102/#3108/#3113/#3131 via `gh pr merge` (per-PR authorization).
- Set the `LEGAL_CLIENT_MAP` repo secret.
- ssh ace-linux-1: synced the cron clone + provisioned local files (authorized "ssh + do needful").
- No other outward actions.

## Next steps
1. #3098 **Phase 3c** as a dedicated, per-cluster, test-driven pass (redact cluster → rewrite its test expectations → green → commit → next).
2. Restore the ace-linux-1 cron clone to `main` + push its cron fixes.
3. Review + commit the recovered mermaid edit (`stash@{0}`).
