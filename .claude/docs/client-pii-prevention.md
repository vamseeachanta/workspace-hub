# Client-PII prevention (epic #3095)

How the public `workspace-hub` repo is kept free of client identifiers, and why
the previous gate failed. This document is intentionally **PII-free** (it names
no clients) so it can live in the public repo without tripping its own guard.

## Why the old gate failed

`scripts/legal/legal-sanity-scan.sh --diff-only` ran at commit time but matched
only the patterns in the public `.legal-deny-list.yaml`. That list **lacked the
active clients**, so real client references passed straight through (see #3096).
Worse, the fix can't be "add the client names to the deny-list" — that file is
public, so listing the names there *is* the leak (the deny-list paradox).

## The model: private source, public-safe tooling

1. **Single private source of truth.** Client identifiers live only in
   `client-codename-map.yaml` in the **private** `aceengineer-strategy` repo
   (`pii-remediation/3097-2026-06-14/`). It maps each real identifier to a
   neutral codename and lists its `/mnt/ace/<bucket>/` path. The canonical client
   roster is `config/client-wikis.yml` (the registry); the map is built from it.

2. **Name-agnostic tooling.** Two scripts in `scripts/legal/` contain **no client
   names** — they read the private map by path:
   - `redact-client-pii.py` — replaces real identifiers with codenames (and
     renames bucket paths). Used for bulk remediation and by the learning cron.
   - `check-client-pii.py` — the guard: *"if running the redactor would change a
     file, that file still contains an un-redacted client identifier."* Guard and
     redactor share one engine, so they can never disagree. The guard **never
     prints a matched value** — only file + line — because public CI logs would
     otherwise leak it.

3. **Local provisioning.** Each host (and the learning cron) reads a gitignored
   local copy `config/agents/.client-codename-map.local.yaml`. Provision it once:
   ```bash
   cp <aceengineer-strategy>/pii-remediation/3097-2026-06-14/client-codename-map.yaml \
      config/agents/.client-codename-map.local.yaml
   ```
   If absent, tools degrade-open (warn, don't block) — the CI gate is the strict
   backstop.

## Enforcement layers (gradient per `.claude/rules/patterns.md`)

| Layer | Mechanism | Blocking? | Notes |
|---|---|---|---|
| Emit | `.gitignore` stop-commit of dump clusters + redaction step in `scripts/cron/commit-learning-artifacts.sh` | n/a | dumps can't re-enter; cron redacts curated state at source (#3097) |
| Local (files) | pre-commit hook `legal-client-pii` (`--staged`) | yes (bypassable) | fast feedback; reads local map, degrades-open |
| Local (commit msg) | pre-commit hook `legal-client-pii-commit-msg` on the `commit-msg` stage (`--message-file "$1"`) | yes (bypassable) | scans the **commit message** (#3169); auto-wired via `default_install_hook_types`; degrades-open |
| CI | `.github/workflows/legal-client-pii-gate.yml` | yes (strict) | **the real backstop**; scans the file diff **and** the PR title/body + each commit message in range (#3169); re-runs on PR `edited`; reads the private map from the `LEGAL_CLIENT_MAP` repo secret |

### Surfaces covered (#3169)

Client identifiers are kept out of **every public surface**, not just file content:
**tracked files**, **commit messages**, and **PR title/body**. The guard's text mode
(`--message-file` / `--stdin --source <label>`) feeds messages/metadata through the
same engine and **never prints the matched value** — only the source label.

**Squash-merge transient-token branches.** A merge-commit promotes a feature
branch's individual commit messages into `main`'s history; a squash-merge does not
(it uses the PR title/body). If a branch's commit messages might carry a transient
token (e.g. mid-remediation), **squash-merge** it so nothing reaches `main` history —
and remember git-history rewrites of `main` are out of scope (HEAD-only).

### Provisioning the CI secret (one-time)
```bash
gh secret set LEGAL_CLIENT_MAP \
  < <aceengineer-strategy>/pii-remediation/3097-2026-06-14/client-codename-map.yaml
```
Without the secret the CI job runs degrade-open (warns, non-blocking). On the
main repo the secret should always be set so the gate is strict.

## Keeping the client list current

When a client is added/renamed in `config/client-wikis.yml`, update the private
`client-codename-map.yaml`, re-`gh secret set LEGAL_CLIENT_MAP`, and refresh the
local copies. The guard then covers the new identifier automatically — no edit to
any public file is required (and none should name the client).

## Bypass

`LEGAL_PII_ALLOW=1` skips the guard (logged). Use only for a deliberate,
reviewed exception.

## Related
- Counts-only remediation record: `analysis/3097-generated-pii-remediation.md`
- Epic #3095; sub-issues #3096 (assessment), #3097 (generated remediation),
  #3098 (hand-authored scrub — incl. relocating `config/client-wikis.yml`),
  #3099 (this prevention layer).
