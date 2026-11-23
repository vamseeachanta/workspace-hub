# Reviewed lean source contracts

Use the existing workstation registry for membership. A local baseline profile
must cover every member of its selected required set exactly; it does not enroll
machines or replace role, data-owner or agent-readiness authorities.

`config/workstations/lean-core-profile.example.yaml` contains deliberately dummy
pins and digests. It cannot establish readiness. Build a private reviewed profile
from approved local source evidence; keep private origins, fleet mappings and
machine adapters outside public commits.

Run the read-only checker with an existing interpreter that has PyYAML:

```sh
python -B scripts/workstations/check-tier1-repo-baseline.py \
  --registry config/workstations/registry.yaml --machine REGISTRY_MACHINE \
  --repo-root /absolute/core --footprint-only \
  --core-profile /absolute/private-reviewed-profile.yaml \
  --footprint-environment /absolute/existing/environment
```

Selection derives from the profile's existing registry membership authority.
The target must match its registered hostname/alias and OS. Every selected
repository, Git store and explicitly supplied environment is measured. Missing
members, redirects, read failures and unknown allocation remain indeterminate.

Source equivalence checks reviewed revisions, direct-origin identity, every
required file's LF-normalized content digest and tracked state. Only an exact
unstaged modification with matching approved content can be accepted. Staged
changes fail. Repeated HEAD/status checks detect observed changes. Collection is
sequential, not atomic; keep inputs quiescent. Use the existing checkout owner's
account without changing trust settings or filesystem permissions.

Exit zero qualifies only this local source, identity and budget gate.
`agent_runtime_qualified` remains false. Runtime, actual skill selection, provider
behavior, licenses, GPU and exact owner data require their existing separate
readiness authorities. Presence and readability are not data qualification.

The existing clone helper accepts a reviewed profile and exact expected main pin:

```sh
python -B scripts/workstations/clone_profile.py REPOSITORY \
  --profile lean --destination /absolute/new-core/REPOSITORY \
  --registry config/workstations/registry.yaml \
  --repos-config /absolute/private-reviewed-origins.conf \
  --baseline-profile /absolute/private-reviewed-profile.yaml --dry-run
```

The parent must exist; destinations must be absent. Dry-run performs no Git call
or directory creation. Conflicting origins and moved main pins stop before clone;
a clone/preflight revision race stops before checkout and retains the destination.
Filtering is not a download byte cap. Select bounded named source and fixtures,
measure allocation and reuse separately verified existing environments.

`sanitized_existing_only` recipes block profile-based cold clone, including
dry-run planning. Where source Git history contains a known credential, reuse
approved already-present sanitized source with explicit provenance for a bounded
task. Report content/behavior acceptance separately from pinned Git equivalence.
Do not copy credential-bearing Git stores, rewrite history, or treat revocation
alone as authorization to transfer the original secret.

Keep original dirty work, unique commits, stashes and worktrees recoverable.
Reconciliation must use a new isolated task lane; no automatic pull/reset,
dependency hydration, bulk data ingestion or active-root replacement is included.
Reuse existing Foundation profiles, harness roles/state classes and provider
equality collectors for the remaining dimensions; no new machine registry or
service is introduced.
