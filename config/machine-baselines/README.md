# Machine baselines registry

Per-machine harness-parity status files, one per machine in the fleet. Issue #2751 G9.

## Files

Each machine in the fleet emits two files into this directory:

- `<token>.yaml` — machine-readable (control-plane aggregator parses)
- `<token>.md` — human-readable (operators paste as comment on operational tracker #2753)

## Hostname token policy

`<token>` is resolved per `feedback_hostname_publication_policy` (r1 m4):

1. If `config/agents/machines.yaml` contains `aliases: { <hostname>: <alias> }`, use the alias (e.g., `ace-linux-1`, `licensed-win-1`).
2. Otherwise, fall back to the first 8 hex chars of `sha256(<hostname>)`. This avoids PII leak via raw hostnames.

## How to emit (per machine)

```bash
bash scripts/setup/emit-machine-status.sh
git add config/machine-baselines/
git commit -m "chore(setup): refresh machine baseline"
git push
```

## How to aggregate (control plane — `ace-linux-1`)

```bash
git pull
bash scripts/setup/aggregate-machine-status.sh
# → docs/reports/fleet-harness-status.md
```

## Secret-scrub guarantee

All file contents pass through a 7-pattern redaction (per r2 C7) before write:

- `gh[opsu]_...` (classic GitHub PAT)
- `github_pat_...` (fine-grained PAT)
- `sk-...` (OpenAI)
- `sk-ant-...` (Anthropic)
- `AIza...` (Google API)
- `eyJ...` (JWT)
- `"refresh_token"` / `"access_token"` JSON field values

Any token-shaped string that ever ends up in a `--version` output, hostname, or environment variable is replaced with `[REDACTED_*]` before write.

## Cross-reference

- **Build issue**: #2751 (this gap-fill)
- **Operational tracker**: #2753 (post baselines here as comments)
- **Schema source**: `scripts/setup/lib/emit-machine-status.sh`
- **Aggregator**: `scripts/setup/aggregate-machine-status.sh`
- **Fleet report**: `docs/reports/fleet-harness-status.md` (generated)
