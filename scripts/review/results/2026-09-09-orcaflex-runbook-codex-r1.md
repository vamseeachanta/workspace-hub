# OrcaFlex runbook and skill routing — Codex code review

Date: 2026-09-09
Scope: the new execution runbook, solver README, OrcaFlex root/batch skills,
and OrcaWave/OrcaFlex readiness-audit skill under issue
[3831](https://github.com/vamseeachanta/workspace-hub/issues/3831).

Initial verdict: MINOR. Post-correction verdict: APPROVE for documentation.
This verdict does not certify solver repair, task deployment, or remote execution.

## Evidence checked

- Compared runbook flags with the actual Deckhand
  `scripts/deckhand/licensed-run-ops.py` parser: policy/scopes/queue options
  precede subcommands; preflight has no host option; dispatch accepts explicit
  host and commit; watch accepts a run ID and timeout.
- Checked the three skill-to-runbook relative links and the runbook's local
  strategy, native-proof protocol and evidence-template targets on disk.
- Compared planned/deployed wording with the execution plan and dated evidence.
- Reviewed all five documentation/skill changes; historical scheduler and
  high-worker examples are explicitly non-operational references.

## Findings and dispositions

1. Queue placeholder was ambiguous and path placeholders were unquoted.
   Corrected: QUEUE is explicitly the clone's queue/ subdirectory; path
   placeholders retain double quotes for Windows paths containing spaces.
2. Rollback omitted the process-absence prerequisite from the reviewed plan.
   Corrected: configuration restoration does not authorize reactivation;
   uncertain ownership or an unkillable tree leaves both consumers disabled.
3. Readiness guidance required repository-qualified issues but retained bare
   historical numbers. Corrected: these are explicitly unresolved historical
   references, not verified issue IDs or dispatch authority; repository and
   title resolution is required before use.
4. Text called the following content non-executable syntax immediately before
   command templates. Corrected: that distinction now refers to the operations
   table; the templates require verification against the pinned interface.

The main session will verify file existence and complete final rendering,
legal scan and cleanup checks. No runtime commands, queue submissions, task
changes, or external notifications were performed by this review.
