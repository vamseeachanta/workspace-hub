# Machine-identity file — provisioning a box whose hostname stays out of this repo

Some boxes run under an OS hostname that must never appear in this public repository
(client-codename collision; `legal-client-pii-gate` is authoritative — see the closed
PR #3279 and issue #3571). The equality/reconcile tooling resolves such a box's fleet
identity from an **off-repo, gitignored identity file** instead of the hardcoded host
maps.

## Provisioning (once per box)

1. Look up the box's logical label in the **private client machine registry**
   (`docs/operations/machine-equality-hosts.yml` in the relevant private client
   repository). Copy only the label — never copy the hostname into anything tracked
   here.
2. Create `~/.config/workspace-hub/machine-identity.yaml`
   (override location via `WORKSPACE_HUB_MACHINE_IDENTITY`):

   ```yaml
   machine: "ace-win-1"            # required — the logical equality label
   public_host: "ace-win-1"        # optional — serialized as evidence `host:`; defaults to machine
   expected_hostname: "<this-box>" # optional but recommended — the file fails loud on any other box
   ```

3. Verify: `bash scripts/readiness/collect-equality.sh --stdout | head -5` should show
   the label with no `--machine` flag needed.

## Semantics

- Precedence everywhere: explicit `--machine` / `-Machine` / `RECONCILE_MACHINE` /
  `EQ_MACHINE` → hardcoded hostname map → identity file → fail loud. The file is
  consulted **only** when the hostname resolves nowhere in the map, so a stale or
  copied file can never override a correctly-mapped host.
- A malformed file (missing `machine:`, unknown label) or a file whose
  `expected_hostname` mismatches the box fails loud — it never silently falls
  through, because a bad file could otherwise publish evidence under the wrong
  fleet column.
- `public_host` is what gets serialized into tracked equality evidence; the OS
  hostname never is.

Consumers: `scripts/readiness/collect-equality.sh` (+ `equality-matrix-cron.sh` via
`EQ_MACHINE`), `scripts/readiness/reconcile-ecosystem.sh`,
`scripts/windows/equality-report.ps1`. Shared bash helper:
`scripts/readiness/lib/machine-identity.sh`.
