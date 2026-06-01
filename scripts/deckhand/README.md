# Deckhand setup scripts

Reusable, **config-driven** setup tooling so a new machine/client doesn't reinvent
anything. The single source of truth is [`config/deckhand/scopes.yml`](../../config/deckhand/scopes.yml) —
these scripts derive the repo list and per-scope PAT env-var mapping from it.
Onboard a new client = add a scope section to `scopes.yml`; the scripts then cover it.

## `protect-and-verify.sh`

Repository protection + token verification. Requires `gh` (authenticated) + `python3`/`pyyaml`.

```bash
scripts/deckhand/protect-and-verify.sh protect      # ruleset per scope repo: block force-push + deletion (idempotent)
scripts/deckhand/protect-and-verify.sh verify       # list rulesets per scope repo
scripts/deckhand/protect-and-verify.sh verify-pat   # confirm each PAT reaches ONLY its scope repos (reads ~/.hermes/.env; never prints secrets)
scripts/deckhand/protect-and-verify.sh unprotect    # remove the deckhand ruleset (reversal)
scripts/deckhand/protect-and-verify.sh deploy-detective        # dry-run install plan for destructive-event alarm workflow
scripts/deckhand/protect-and-verify.sh deploy-detective --apply # install/update the workflow in each scope repo
scripts/deckhand/protect-and-verify.sh verify-detective        # check workflow presence per scope repo
```

- `protect` enforces, on each repo's default branch, a ruleset (`deckhand-protect-default`,
  `enforcement: active`) with `deletion` + `non_fast_forward` rules — the server-side
  no-destructive guarantee that a `Contents: write` PAT cannot provide on its own.
- `deploy-detective` installs
  [`scripts/deckhand/templates/deckhand-destructive-alarm.yml`](templates/deckhand-destructive-alarm.yml)
  as `.github/workflows/deckhand-destructive-alarm.yml` in every concrete repo listed in
  `scopes.yml`. It prints a dry-run plan by default and only mutates repos with `--apply`.
- `verify-detective` reports whether that workflow is present in every concrete scope repo.
- The destructive alarm is a DETECTIVE compensating control: it opens an issue when a
  force-push or branch/tag deletion is detected, but it does not prevent the event. This
  exists because GitHub Free does not provide private-repo server-side branch protection
  for the Deckhand scope repos.
- `verify-pat` does a positive check (token reaches its own repos) and a negative check
  (warns if a token is over-broad and reaches out-of-scope repos). It loads
  `DECKHAND_PAT_*` from `~/.hermes/.env`. Secrets are never printed.

## PAT provisioning (manual, owner-only)

Fine-grained PAT per scope (`pat_env` in `scopes.yml`): Repository access = only that
scope's repos; Permissions = Contents R/W + Pull requests R/W + Metadata R; **no
Administration**. Store the token in `~/.hermes/.env` under its `pat_env` name — never in git.

Note: a single fine-grained PAT applies one permission level across all its repos, so a
`reference` (read-only) repo in a scope (e.g. `doris`) is held read-only by the engine
(`repository_flags: read_only`) + branch protection, not by the token. For token-level
read-only on a reference repo, issue it a separate read PAT.
