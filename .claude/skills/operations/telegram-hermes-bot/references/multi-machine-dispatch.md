# Multi-machine Telegram + Hermes dispatch pattern

Use this reference when extending a single-host Telegram-Hermes deployment into a multi-computer operator surface. This is a class-level pattern, with issue #2720 as the first concrete planning exemplar.

## Core rule

Telegram is the dispatch and notification plane, not the synchronization layer.

Canonical synchronization belongs in:
- GitHub issues, labels, comments, and approval state
- git-backed repo state, branches, commits, and pushed handoff artifacts
- repo-backed Hermes/agent config templates and external skill dirs
- explicit job/host routing records with idempotency guards

Do not rely on Telegram message history as source of truth for what work is active, approved, completed, or synced.

## Operator surface

Account for both:
- Telegram mobile, for approval and quick status checks
- Telegram Desktop across Windows and Linux machines, for day-to-day dispatch ergonomics

Desktop-first designs need clear host identity in responses so the operator can distinguish which Hermes instance is acting.

## Host identity and registry

Use the existing workstation registry as the host source of truth. For workspace-hub this means extending `config/workstations/registry.yaml`; do not invent a second Telegram-specific machine registry.

Each host entry should support:
- stable hostname / operator-facing alias
- OS / platform class
- reachable repo roots and Hermes home paths
- available providers / licensed tools
- safe working directories for job execution
- capability labels used for routing (`linux`, `windows`, `licensed`, `gpu`, etc.)
- last-seen / readiness evidence if a scheduler needs host freshness

## Dispatch lease pattern

For duplicate prevention across machines, prefer a git-backed lease primitive rather than Telegram-message state.

Recommended shape:
1. `/dispatch <issue> --host <host|auto>` validates issue gate state and host readiness.
2. Dispatcher attempts to create/update a git remote lease ref such as `refs/hermes-dispatch/<issue>/<job-id>` with compare-and-swap semantics.
3. Winning lease is mirrored back to the issue as a comment for human traceability.
4. Losing dispatchers fail closed and report the existing lease/job link.
5. Job completion writes durable output back to GitHub/git, then clears or closes the lease according to the policy.

The lease record should include issue URL, requested host, resolved host, repo/worktree path, branch/ref, start timestamp, command class, and callback/log locations. Do not store secrets in the lease.

## Architecture decision points

Before implementation, decide:
1. Single coordinator bot vs per-host bots/profiles.
2. How host identity and capabilities are registered (`ace-linux-1`, `ace-linux-2`, Windows workstation, licensed machines, etc.).
3. How `/dispatch` maps to GitHub issues, labels, worktrees, and provider/machine routing.
4. How duplicate work is prevented when the same issue is requested from multiple clients.
5. How dirty worktrees, unpushed commits, unavailable hosts, missing approval labels, and stale leases fail closed.
6. How results are written back: issue comment, session handoff, pushed branch/commit, status label.
7. How readiness paths are resolved without split-brain config.

## Readiness and path convergence

Multi-machine dispatch should use existing readiness infrastructure rather than another host/path table. For workspace-hub, reconcile path metadata through `scripts/readiness/harness-config.yaml` plus the workstation registry. The goal is one computable path story:
- registry: who/what/where the machine is
- harness-config: how readiness checks resolve paths and command probes
- issue/dispatch layer: what work is allowed to run there

Acceptance tests should include a fixture or probe proving that a host path change is reflected in dispatch readiness and does not require editing two competing registries.

## Minimum command contract

Recommended MVP commands:
- `/status` — host availability, dirty repos, active jobs, provider headroom.
- `/dispatch <issue-or-task> --host <host|auto>` — launch only if workflow gates allow it.
- `/jobs` — list active/recent jobs with issue/log/branch links.
- `/sync` — perform safe repo/config sync checks; never blind destructive cleanup.

## Operator-facing selector pitfalls

- Registry keys are stable internal IDs (`dev-primary`), while humans usually type hostnames (`ace-linux-1`) or aliases. Telegram commands, readiness CLIs, and smoke checks should accept all three and render the resolved canonical host ID in output.
- If implementation intentionally accepts only registry keys, CLI help and docs must say `--host <host-id>` and examples must use registry keys. Do not leave examples using hostnames if the parser rejects them.
- Add TDD coverage for hostname/alias lookup before patching selector code; a passing `unknown host_id` test alone is not enough for operator usability.

## Safety constraints

- Telegram bot tokens never appear in issues, comments, shell history, logs, leases, or repo artifacts.
- `GATEWAY_ALLOW_ALL_USERS` remains disabled unless a separate multi-user security plan is approved.
- `approvals.mode` stays `manual` or explicitly justified `smart`; `off` is not acceptable for Telegram-driven terminal access.
- Dispatch must not bypass GitHub issue planning, user approval, TDD, or adversarial-review gates.
- Sync must be pull-before-work and push-after-work with clean/dirty evidence.
- Multi-agent commits should be pathspec-limited to avoid sweep contamination.
- Dirty worktrees, missing approval markers, unsafe allow-all gateway settings, token leakage, split-brain paths, and duplicate leases fail closed.

## Minimal implementation pattern

When turning the plan into code, keep the first implementation deliberately small and side-effect separated:

1. **Policy module first** — implement a side-effect-free dispatch policy module that accepts request + GitHub gate evidence + host readiness + repo state + lease state, then returns `accepted=false` with a machine-readable reason or `accepted=true` with the lease/idempotency metadata. The policy module should not create refs, start jobs, write comments, or mutate repos.
2. **Redaction module next** — centralize status rendering through a redaction helper before anything reaches Telegram, GitHub comments, logs, or handoff docs. Redact both secret-like keys and token/API-key-like values. Treat validation failures as public output and replace token material with `[REDACTED]`.
3. **Readiness collector** — add a JSON readiness command that reads the canonical workstation registry and emits secret-free per-host status. Fail closed on malformed registry, unsafe `GATEWAY_ALLOW_ALL_USERS`, missing workspace roots for dispatch-enabled hosts, or secret-like fields/values in registry metadata. The operator-facing host selector must resolve the stable registry key, `hostname`, and `hostname_aliases` (for example, `--host dev-primary`, `--host ace-linux-1`, and any configured alias should select the same record). A readiness smoke check that uses a real hostname and returns `unknown host_id` is a UX/API defect unless the CLI help and docs explicitly state host IDs only.
4. **Registry extension only** — add Telegram/Hermes dispatch metadata to the existing workstation registry; do not create a second host registry for Telegram.
5. **Bounded shell wrapper** — expose the readiness collector via a short `uv run python ...` wrapper so it fits existing readiness scripts without duplicating Python path assumptions.
6. **TDD fixture coverage** — cover approval-marker gating, label/status gating, malformed command rejection, dirty/ahead/behind repo rejection, missing data access, duplicate lease rejection, status-only hosts, not-onboarded hosts, and redaction of both keys and values.

Useful file-shape example for workspace-hub-style repos:

```text
scripts/telegram_dispatch/policy.py        # pure policy/evidence -> decision
scripts/telegram_dispatch/redaction.py     # public-output redaction helpers
scripts/readiness/telegram_hermes_readiness.py
scripts/readiness/telegram-hermes-readiness.sh
tests/telegram_dispatch/test_dispatch_policy.py
tests/telegram_dispatch/test_redaction.py
tests/readiness/test_telegram_hermes_readiness.py
```

Do not treat passing policy/readiness tests as closeout by itself. Before closing, finish registry/docs/readiness integration, run legal/security scan, run adversarial artifact review, then commit/push/comment/close only after clean-state proof.

## Planning issue template notes

For GitHub planning issues in this class, explicitly include:
- Existing single-host Telegram-Hermes issues/runbooks as related work.
- The phrase that Telegram is the control plane and git/GitHub/repo artifacts are the sync layer.
- Cross-OS Telegram Desktop requirement when the operator intends to use Windows and Linux clients.
- Acceptance criteria that force answers about routing, sync verification, canonical state, duplicate prevention, rollback, token rotation, registry integration, and readiness path convergence.
- A no-implementation-until-`status:plan-approved` statement when the plan is still in review.

## Verification checklist for a plan in this class

Before moving a multi-machine Telegram/Hermes issue to `status:plan-review`, verify the plan states:
- [ ] Telegram is command/notification only; git/GitHub/repo artifacts are canonical sync.
- [ ] Host metadata extends the existing workstation registry, not a new host table.
- [ ] Dispatch leases use an atomic git/GitHub-backed primitive and mirror to issue comments.
- [ ] Gate checks fail closed on missing approval labels, dirty worktrees, duplicate leases, or unsafe gateway config.
- [ ] Readiness paths converge through the existing harness config.
- [ ] Token rotation and token redaction are acceptance criteria.
- [ ] Work completion requires pushed artifacts plus issue comment evidence.
