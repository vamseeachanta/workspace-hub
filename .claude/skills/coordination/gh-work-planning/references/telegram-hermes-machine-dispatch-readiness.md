# Telegram/Hermes Machine Dispatch Readiness

Use this reference when auditing whether a Telegram/Hermes multi-machine control plane is ready for dispatch or when triaging issue queues that mix architecture plans with machine-enablement plans.

## Durable pattern

Do not equate `status:plan-approved` with machine dispatch readiness. For operational dispatch work, verify four independent surfaces:

1. Live GitHub issue state and labels.
2. Local approval marker: `.planning/plan-approved/<issue>.md`.
3. Host/machine readiness probes, including host-local evidence for remote workers.
4. Worktree cleanliness in the execution checkout, not just in the orchestrator checkout.

If any surface fails, classify the issue as approved-but-not-execution-ready or governance drift, not dispatchable.

## Linux coordinator/worker sequencing

For a Linux Telegram/Hermes MVP, keep the sequence narrow:

1. Coordinator hardening on the primary/control host.
2. Worker enablement on the first remote Linux host.
3. Smoke and destructive-action canary validation.
4. Only then plan cross-platform parity for Windows/macOS.

Windows/macOS hosts should stay status-only/manual until a separate reviewed and approved parity plan proves service management, secrets storage, approval posture, host-local evidence, rollback, and promotion checks.

## Host-local evidence rule

Remote dispatch hosts need host-local readiness evidence. A coordinator-side registry check is not enough because it cannot prove remote env gates, local git state, service state, or local approval posture.

Minimum remote-worker evidence should prove, without printing secrets:

- expected env variable names are configured;
- unsafe allow-all settings are disabled;
- workspace root is clean/synced enough for dispatch;
- service/wrapper is installed or explicitly not yet installed;
- evidence is fresh, redacted, and bound to the expected hostname/registry identity.

## Machine identity drift check

Before routing work, compare machine labels against the canonical workstation registry. Treat physical hostnames as attributes unless the registry explicitly uses them as IDs.

Risk pattern:

- plans or GitHub labels use `machine:<hostname>`;
- queue/orchestrator code expects `machine:<registry-id>`;
- both appear valid to humans, but automated routing rejects or misroutes the issue.

When found, pause broad execution-layer planning until the label contract is reconciled. Narrow already-approved machine plans may proceed only if they do not claim to settle the broader routing contract.

## Architecture-plan interaction

If architecture-layer issues have stale approval labels but no local approval markers and fresh MAJOR reviews, do not let them authorize machine execution. Treat them as blocked planning work and keep machine MVP work under its narrower approved issue authority.

## Safe orchestrator actions during audit

Without implementation writes, safe actions are:

- read-only GitHub label/state audit;
- approval marker audit;
- readiness-script execution that does not mutate hosts;
- stale machine-label reference inventory;
- queue classification and sequencing recommendation;
- plan-revision prompt packaging for blocked architecture plans.

Avoid label changes or GitHub mutations unless explicitly taking ownership of governance cleanup and posting the evidence trail.