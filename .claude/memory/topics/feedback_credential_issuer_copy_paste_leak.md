> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_credential_issuer_copy_paste_leak.md

---
name: Credential-issuer copy-paste leak
description: Never commit the raw "save this token" output from credential issuers (BotFather, AWS, Stripe, OAuth providers); commit only a pointer to a secret manager
type: feedback
originSessionId: 1e43bc03-a1cb-4927-8cd8-128369d7ded6
---
When a credential-issuance flow produces a "save this token / keep this secret / store it safely" message, do **NOT** copy-paste that message verbatim into a git-tracked docs file. Extract the credential into a secret manager (1Password / env var / `.env.local`-gitignored) and commit only a pointer to that location.

**Why:** 2026-05-04 incident on `aceengineer-admin` branch `codex/burn-20260427-issue-2493`, commit `bfe00da chore(admin): note telegram bot token in private admin doc`. Verbatim BotFather output landed in `admin/software.md` including the live token `8288748751:AAH58KoD6oRB2G9PIEWvz9ELBx5NUSSjoZM` and the warning text "Keep your token secure and store it safely, it can be used by anyone to control your bot." Token had to be revoked via BotFather `/revoke`, branch deleted from local + origin, and the commit purged from local pack to remove it from reachable storage. Repo was private so blast radius was contained, but the same anti-pattern in a public repo (or a private repo with leaked credentials) is a credential breach.

**How to apply:**

1. **Authoring docs**: any time you're about to paste output from a credential issuer (BotFather, `aws sts get-session-token`, Stripe dashboard "reveal secret", OAuth client-secret reveal, GitHub PAT creation page, etc.), pause. Extract the credential into a secret store. The doc should say something like `Bot API token: see 1Password "AceEngineerBot/api-token"` — pointer only.

2. **Reviewing diffs**: a paragraph that quotes the *issuer's* warning text ("Keep this secret", "store it safely", "you won't see this again") is a high-confidence smell that the actual secret is in the same paragraph. Flag for re-redaction before commit.

3. **Already-leaked recovery (from this incident)**:
   - **First** revoke the credential out-of-band (BotFather `/revoke`, AWS IAM rotate, Stripe rotate, etc.) — this is the load-bearing step. Once revoked, any future exposure of the historical token is harmless.
   - **Then** delete the branch from both local *and* origin. **Do not** create a recovery `archive/` tag — that would keep the leak commit reachable.
   - Locally purge unreachable storage: `git reflog expire --expire=now --expire-unreachable=now --all && git gc --prune=now --aggressive`. The `--expire-unreachable=now` flag is the load-bearing one — without it, the default reflog expiry (90 days) keeps the orphan commit in pack files. Verify with `git cat-file -e <leak-sha>` returning "Not a valid object name".
   - On origin (GitHub): branch deletion makes the commit unreachable from refs but GitHub keeps unreachable commits accessible by direct SHA URL for ~90 days. If belt-and-suspenders is needed, file a "Removing sensitive data" request with GitHub Support.

4. **Skip-list for "safe to paste"**: dummy/example tokens whose docs explicitly mark them as fake (`xoxb-EXAMPLE-...`, `sk_test_FAKE_...`); short-lived (<5min) demo tokens you generated solely to write a doc and revoked before commit. Otherwise treat every token-shaped string as live.
