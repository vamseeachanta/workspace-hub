# Registry-Driven Connection Helpers — Design Specification

**Date:** 2026-07-15  
**Issue:** [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549)  
**Parent:** [#3547](https://github.com/vamseeachanta/workspace-hub/issues/3547)  
**Dependency:** [#3548](https://github.com/vamseeachanta/workspace-hub/issues/3548), integration [PR #3553](https://github.com/vamseeachanta/workspace-hub/pull/3553)  
**Approved architecture:** Public registry policy plus machine-local verified fallback overlay

## Context

The repository has multiple Bash, PowerShell, and Tabby connection surfaces that
independently encode workstation addresses and operator identities. Those values
have drifted. Some helpers also interpret a failed SSH authentication probe as a
reason to switch destinations, which can turn host-key, authorization, or policy
failures into silent fallback behavior.

The canonical remote-access runbook establishes this authority order:

1. `config/workstations/registry.yaml` — machine identity and connection policy;
2. `docs/ops/remote-linux-access.md` — operational and security policy;
3. connection helpers — executable convenience only;
4. machine-local state — observed addresses, attestations, credentials, and keys.

The design must remove tracked endpoint duplication without moving sensitive
infrastructure metadata into another public file.

## Decision

One strict Python connection resolver will own registry parsing, validation,
route selection, dry-run rendering, and process launch. The public registry will
hold canonical machine identity, the preferred MagicDNS/SSH hostname, connection
policy, and an opaque fallback reference. A gitignored machine-local overlay will
hold any fallback address and its verification attestation.

Bash and PowerShell entry points will remain thin wrappers. They will pass only
validated options to the Python command and will never parse YAML, concatenate a
destination command, or inspect a failed SSH session to select another route.

## Alternatives Considered

### Public registry stores fallback addresses

This is the smallest implementation and most literal reading of “registry-driven,”
but it permanently publishes point-in-time infrastructure metadata in the Git
tree and history. It conflicts with the #3548 rule that helpers and shared
artifacts must not publish observed endpoints. Rejected.

### Public policy plus machine-local verified overlay

The registry remains authoritative for logical identity and policy while the
overlay contains observed endpoint state. Missing or stale overlay data disables
only explicit fallback; hostname access remains available. This adds a small
provisioning step but preserves the durable-versus-local knowledge boundary.
Selected.

### Generated local immutable manifest

A generator could combine the registry and overlay into a digest-bound JSON
manifest for runtime use. That would strengthen offline reproducibility but add
generation, atomic replacement, permission, and staleness lifecycle machinery.
It is disproportionate for the current two-host scope. Deferred unless offline
operation becomes a requirement.

## Components

### Registry connection policy

Each governed machine will have a strict, versioned connection-policy object.
It will identify:

- the canonical MagicDNS/SSH hostname;
- whether fallback is permitted;
- an opaque fallback reference, never an address;
- the expected overlay schema version;
- the maximum accepted attestation age.

Connection fields will have explicit types and a closed schema. A custom safe
loader will reject duplicate mapping keys before construction; unknown fields,
wrong YAML types, empty values, and conflicting identifiers will fail closed.
Machine keys, hostnames, aliases, and SSH identifiers will be globally unique
after case folding.

Existing unverified address fields will not become usable through migration.
They will be removed or replaced by policy metadata without guessing a live
value.

### Machine-local fallback overlay

The overlay will be outside the repository, so repository ignore rules will not
govern it. Its path will use the documented POSIX default with an explicit
override for tests and managed installations.

Each fallback record will contain:

- schema version and machine key;
- the opaque registry reference;
- a Tailscale address parsed by the standard IP library;
- verification state and non-secret evidence reference;
- verification and expiry timestamps;
- the digest of the selected machine's canonical connection-policy projection.

The resolver will accept only an address within Tailscale-owned ranges. Missing,
malformed, expired, unverified, machine-mismatched, reference-mismatched, or
connection-policy-digest-mismatched records will fail before any client process
starts.

Timestamps will be RFC-3339 UTC seconds. Acceptance requires
`verified_at <= now < expires_at`, `expires_at > verified_at`, and
`expires_at - verified_at <= policy.max_age_seconds`; future verification,
reversed/equal bounds, and policy-overlong validity will fail closed.

The overlay will contain no keys, tokens, passwords, or authentication material.
Documentation will define restrictive POSIX permissions and an equivalent
Windows ACL expectation.

### Shared resolver and launcher

The existing `WorkstationPathResolver` will remain the only registry parser.
A dedicated connection module will build on it while adding strict schema and
ambiguity checks rather than using its current permissive `field_for` behavior.

A thin CLI under `scripts/operations/connection/` will accept a machine
identifier, route policy, dry-run flag, registry path, and optional overlay path.
The command will:

1. read the registry once;
2. validate that immutable snapshot completely;
3. resolve a globally unambiguous machine identity;
4. select the canonical hostname by default;
5. load and validate the overlay only for an explicitly requested fallback;
6. render redacted deterministic output for dry-run, or launch OpenSSH with an
   argument vector and no intermediate shell.

The resolver will never attempt a second destination after DNS failure, timeout,
host-key failure, authentication rejection, or any other OpenSSH exit. Fallback
will be a separate explicit operator action.

### Bash and PowerShell wrappers

Wrappers will expose aligned machine, route, and dry-run options and forward them
as argument arrays. They will not receive a resolved address through stdout,
environment variables, string interpolation, `eval`, or `Invoke-Expression`.

Interactive OpenSSH will remain supported. Address-coupled Tabby profiles and
PowerShell command-string launch modes will be retired. If a terminal application
opens OpenSSH, it must do so without owning connection identity or endpoint data.

## Governed Surface

The implementation plan will govern these target-bearing SSH surfaces:

- `connect-workspace-tailscale.sh`;
- `connect-workspace-tailscale.ps1`;
- `ssh-dev-secondary.sh`;
- `connect-workspace-linux.sh`;
- `connect-workspace-windows.ps1`;
- `config/tabby/config.yaml`.

It will also govern the shared resolver/CLI, registry schema, focused tests, and
directly affected helper documentation.

`vnc-ace-linux-2.sh` is explicitly excluded because [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550)
owns VNC and secondary-machine capability reconciliation. Sync helpers without
connection literals will remain unchanged unless Tabby template handling requires
a narrowly scoped update.

## Exact Runtime Contract

The registry connection object will be closed and versioned:

```yaml
connection:
  schema_version: 1
  preferred_route: ssh
  fallback:
    kind: tailscale_ip
    reference: <machine-key>-tailscale
    attestation_issue: <rollout-issue-number>
    max_age_seconds: 604800
```

The existing top-level `ssh` value will remain the canonical hostname. Reference
values will use lower-case letters, digits, and hyphens; maximum age will be an
integer from 300 through 2592000 seconds. One case-folded identifier may occur
more than once inside the same machine record, but it may not belong to two
different machines.

The local overlay will be an OS-owner assertion, not a signed attestation:

```yaml
schema_version: 1
records:
  <machine-key>-tailscale:
    machine: <machine-key>
    address: <machine-local-observed-value>
    status: verified
    evidence: https://github.com/vamseeachanta/workspace-hub/issues/<rollout-issue>#issuecomment-<id>
    verified_at: <RFC-3339-UTC-seconds>
    expires_at: <RFC-3339-UTC-seconds>
    connection_policy_sha256: <64-lowercase-hex>
```

The digest input will be a versioned projection containing exactly the canonical
machine key, canonical SSH hostname, and every closed `connection` policy field.
It will exclude other machines and unrelated capability or scheduling fields:

```json
{"connection":{"fallback":{"attestation_issue":0,"kind":"tailscale_ip","max_age_seconds":0,"reference":"<opaque-reference>"},"preferred_route":"ssh","schema_version":1},"format":"workspace-hub-connection-policy-v1","machine":"<canonical-machine-key>","ssh":"<canonical-ssh-hostname>"}
```

Validated runtime values will replace the typed placeholders. Canonical bytes
will be `json.dumps(projection, sort_keys=True, separators=(",", ":"),
ensure_ascii=True).encode("ascii")`, with no BOM, indentation, or trailing
newline; the stored digest will be lowercase SHA-256 hexadecimal. Nulls, floats,
Unicode, implicit YAML coercions, missing/unknown fields, legacy
`registry_sha256`, and multiple digest fields will fail before hashing. The full
registry will still be validated before projection, so malformed unrelated
records and cross-machine collisions remain hard errors. Any projection change
will require a new `format` value and re-attestation.

On POSIX, the default will be
`${XDG_CONFIG_HOME:-${HOME}/.config}/workspace-hub/connection-overlay.yaml`.
The immediate directory and file will be real, current-user-owned objects; the
file will be a regular non-symlink with mode no broader than `0600`, and the
directory will have no group/world write bits. An explicit overlay path will
retain every check and will be rejected inside the Git worktree. Live issuance
will belong to rollout issues #3550/#3551; #3549 will load only synthetic test
records. Windows hostname mode will be supported, while fallback will return the
documented unsupported exit until a native ACL validator is separately reviewed.

The shared command will require `uv` and will expose machine, fallback, dry-run,
user, registry-path, and overlay-path options. Generic wrappers will require an
explicit machine; the secondary-named wrapper will retain its fixed machine ID.
Removed terminal-method options will fail as usage errors rather than silently
selecting another launch path.

Fallback OpenSSH argv will keep the canonical hostname as its positional
destination. Fixed options will override only `HostName` with the verified local
address, bind `HostKeyAlias` to the canonical hostname, and force
`StrictHostKeyChecking=yes`. This preserves the canonical SSH `Host` block and
known-host identity. Caller-supplied SSH options will not be accepted.

| Exit | Contract |
|---:|---|
| 0 | Dry-run or SSH succeeds |
| 2 | Usage, legacy option, or unknown machine |
| 3 | Registry schema or cross-machine ambiguity |
| 4 | Fallback unavailable, unsafe, stale, unverified, or unsupported on the OS |
| 5 | Digest or local-file integrity failure |
| 126 | Selected executable cannot run |
| 127 | Required uv/Python/OpenSSH runtime is missing |
| Other | OpenSSH exit code; operator interrupt is 130 |

Resolver and dry-run diagnostics will remain redacted. Interactive OpenSSH will
inherit the terminal streams, and its own local diagnostics may display its
destination; those bytes are outside the durable-log redaction boundary.

The staged/CI guard will use a checked governed-path manifest. It will include
the registry policy, connection core and CLI, all migrated wrappers, Tabby
configuration, endpoint-prohibited docs, and an explicit deferred VNC row. Local
mode will read exact staged blobs; CI mode will read exact head-commit blobs.
Hook installation will resolve the hooks directory with
`git rev-parse --git-path hooks`. A new idempotent
`--connection-endpoint-only` mode will install only this guard and will work in
normal and linked worktrees; broad legacy installer conversion remains #3435.

## Output and Error Contract

Dry-run output will be deterministic JSON containing only logical machine ID,
route class, verification state, connection-policy digest, and a redacted
argument shape.
It will not reveal hostname, address, operator identity, rejected raw values,
environment contents, overlay contents, or authentication state.

Errors will name the field path and stable error class without echoing the bad
value. Exit codes will distinguish:

- caller or unknown-machine errors;
- malformed or ambiguous registry state;
- unavailable, stale, or unverified fallback state;
- connection-policy/overlay digest mismatch;
- missing client or client-launch failure.

Dry-run will perform no ping, DNS probe, Tailscale command, SSH attempt, Tabby
launch, or other external process execution.

## Security Invariants

- Host-key checking will remain enabled; null known-hosts files and insecure
  overrides will be rejected.
- Operator usernames will remain in local OpenSSH configuration or a separately
  validated explicit option, not the public registry.
- Registry and overlay values will never become shell source or command strings.
- The registry and overlay will each be read once per invocation; execution will
  use the validated in-memory snapshot.
- Current-tree endpoint removal will not be represented as Git-history removal.
  Any history purge will require separate explicit authorization.
- An exact governed-helper manifest will back every coverage claim.
- A staged-blob scanner will inspect added and modified governed files with
  NUL-safe filename handling. Forensic fixtures will use narrow sentinels, never
  blanket file exemptions.

Closeout will use Gitleaks v8.30.1 from its official GitHub release, not the
repository's ruleless custom configuration. It will verify the downloaded
`gitleaks_8.30.1_checksums.txt` against pinned SHA-256
`061476c21adaf5441516f96f185c1a4706a83cd6329b9b38762271b3d4a52fae`, verify
the selected Linux x64/arm64 archive through that manifest, require the installed
version to equal `8.30.1`, and use a temporary `[extend] useDefault = true`
configuration. A runtime-assembled synthetic leak will have to produce dedicated
exit 23 before `gitleaks dir --redact --exit-code 24` scans the exact frozen
`git write-tree` object exported with `git archive`. Unsupported architectures,
manifest corruption, missing/duplicate entries, archive corruption, or a failed
positive control will stop closeout. Source:
<https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1>.

## Test Strategy

TDD will begin with focused failing tests covering:

1. duplicate-key rejection, strict connection schema, and global collisions;
2. canonical key, hostname, alias, and SSH-identifier resolution;
3. hostname-first behavior with exactly one OpenSSH invocation;
4. no implicit fallback after every major OpenSSH failure class;
5. explicit fallback rejection for missing, malformed, duplicate, out-of-range,
   future-dated, reversed, overlong, stale, unverified, or mismatched records;
6. one successful synthetic verified-fallback fixture;
7. injection and Unicode-confusable target corpora with no side effects;
8. deterministic redacted dry-run and secret-safe diagnostics;
9. single-read snapshot, canonical per-machine digest stability/mutation, legacy
   digest rejection, and connection-policy mismatch handling;
10. Bash and PowerShell argument/exit-code parity;
11. complete governed-helper inventory, deletion of both tracked `.fuse_hidden*`
    connection residues, and rejection of any future tracked residue;
12. exact staged-blob address and secret scanning with positive controls.

Pytest will drive Python and Bash behavior with temporary registries, overlays,
and fake executables. Static PowerShell contract tests will run on Linux. Native
PowerShell behavior must pass on a Windows or PowerShell-capable runner before
the implementation can claim full cross-platform parity; otherwise closeout will
state the supported-platform boundary explicitly.

## Delivery Gates

1. [PR #3553](https://github.com/vamseeachanta/workspace-hub/pull/3553) will land the #3548 authority before implementation begins.
2. A future-tense #3549 issue plan will be written from this design.
3. The plan will receive adversarial multi-provider review.
4. The user will explicitly apply `status:plan-approved`; the agent will not
   self-approve.
5. Implementation will follow red-green-refactor TDD.
6. Code/artifact review, legal/security scans, issue summary, completeness
   verification, and cleanup audit will precede closeout.

## Success Criteria

- Tracked SSH helpers and Tabby configuration contain no independently maintained
  endpoint or operator defaults.
- Canonical hostname access resolves from strict registry policy.
- Address fallback is possible only through an explicit, current, verified local
  overlay.
- Missing, ambiguous, stale, conflicting, or unsafe data fails before process
  launch.
- Bash and PowerShell expose the same logical behavior or a verified platform
  boundary is documented.
- Dry-run and errors reveal no endpoint, identity, secret, or raw rejected value.
- Tests and staged-content enforcement prevent recurrence.
