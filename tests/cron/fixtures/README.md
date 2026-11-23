# Cron crontab fixtures

Point-in-time captures of installed crontabs, committed so that classification and cutover regression
tests are reproducible offline — without `crontab -l` and without access to the machine.

Provenance lives **here**, never inside a fixture: tests assert exact `(location, index)` pairs, so a
header comment inside a fixture would shift every index.

| Fixture | Host | `machine_id` | Captured | Lines | Redactions |
|---|---|---|---|---|---|
| `ace1-crontab-2026-07-30.txt` | `ace-linux-1` | `dev-primary` | 2026-07-30 | 73 | 0 |
| `ace2-crontab-2026-07-30.txt` | `ace-linux-2` | `dev-secondary` | 2026-07-30 | 40 | 3 |

Captured with `crontab -l` (read-only). Repo HEAD at capture: `3fe934da9`.

## Recorded classification

Measured with `cron_line_model.classify_line_detail(..., ownership_context=...)` at `3fe934da9`.
`tests/cron/test_cron_fixtures.py` pins these.

### `ace1-crontab-2026-07-30.txt` — role `control-plane`

```
parse: before=11 managed=51 after=9  error=None
by class      : {cataloged: 11, ignore: 12, preserved_external: 1, uncataloged: 47}
by (loc,class): before:ignore=10  before:preserved_external=1
                managed:cataloged=4  managed:uncataloged=47
                after:cataloged=7   after:ignore=2
duplicates    : notification-purge line at (managed,31) and (after,7)
                deckhand-api-presence-sync line at (after,1) and (after,8)
```

All 47 `uncataloged` lines sit inside the managed block — the defect #3709 exists to fix.

### `ace2-crontab-2026-07-30.txt` — role `comms-dispatch+sim-worker`

```
parse: before=14 managed=14 after=10  error=None
by class      : {cataloged: 3, ignore: 15, preserved_external: 9, uncataloged: 11}
by (loc,class): before:ignore=10  before:preserved_external=4
                managed:cataloged=3  managed:uncataloged=11
                after:ignore=5      after:preserved_external=5
```

## Sanitisation rule

Applied in precedence order. A fixture that misreports its own classification is worse than no
fixture, so class preservation outranks redaction.

1. **Classification-load-bearing bytes are preserved verbatim.** Every byte that can change
   `classify_line_detail`'s output — the whole of every non-comment cron line, and both managed-block
   markers — is copied exactly. In particular `/mnt/local-analysis/workspace-hub` is **not** rewritten:
   `config/workstations/registry.yaml` already declares it publicly and every `canonical-exact-line`
   identity match depends on it.
2. **Redaction only where it cannot change a class.** The one permitted rewrite is user home
   directories → `$HOME`, regex `/home/(?!linuxbrew/)[A-Za-z0-9._-]+`. It is semantically identical
   under cron and already the dominant style in these crontabs. Well-known **system** accounts are
   exempt by name (`linuxbrew`) because they are not user-identifying.
3. **Secret-shaped content is a rejection, not a redaction.** If the deny-scan below matches, the
   capture is aborted and no fixture is committed — redacting a match would alter that line's class.
4. **Provenance lives in this file**, never in a fixture.
5. **Class preservation is verified, not assumed.** Each capture is classified before and after
   redaction; the full `(location, index, class)` sequence must be identical.

### Deny-scan patterns

`MAILTO=` · `[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|APIKEY|API_KEY|ACCESS_KEY)=` · `Bearer <token>` ·
`ghp_|gho_|ghu_|ghs_|ghr_|github_pat_` · `sk-|sk-ant-` · `AKIA[0-9A-Z]{16}` · `AIza[…]{35}` ·
`xox[abprs]-` · PEM private-key header · e-mail address · `/home/<user>` · `/Users/<user>` ·
IPv4 literal · `ssh|scp|rsync user@host`

### Result at capture

```
ace1 : 0 matches            -> committed byte-identical to `crontab -l`
ace2 : 4 matches            -> /home/linuxbrew x1 (exempt, rule 2); /home/vamsee x3 -> $HOME
       residual /home hits  : ['/home/linuxbrew']
       class-preserving     : True  (40/40 identical (location, index, class))
```

ace1 required zero redactions, so rule 2 acted as a gate the capture passed rather than a
transformation applied.

## Maintenance

These are **regression fixtures, not a live mirror**. They will drift from installed state; the
filename carries the capture date. Refreshing one means re-running the deny-scan, re-running the
class-preservation check, and updating the recorded classification above in the same commit — the
recorded numbers are assertions in `tests/cron/test_cron_fixtures.py`, so a silent refresh turns
those tests red.

Related: [#3709](https://github.com/vamseeachanta/workspace-hub/issues/3709),
[#3708](https://github.com/vamseeachanta/workspace-hub/issues/3708),
[#3711](https://github.com/vamseeachanta/workspace-hub/issues/3711).
