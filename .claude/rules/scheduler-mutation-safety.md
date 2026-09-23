# Scheduler Mutation Safety

- Every repo-tracked scheduler mutator and transitive entrypoint must be registered in `config/scheduled-tasks/mutation-surfaces.yaml`.
- Registry inclusion is audit evidence, not authorization to mutate live cron, systemd, or Windows Task Scheduler state.
- Destructive ownership must use parsed or exact identity. Descriptive metadata and arbitrary substring matches cannot certify compliance.
- Every operation must declare its exact scheduler identity, target kind, and execution-host binding. `physical-local` binds mutation to the physical current host; remote mutation requires declared `explicit-remote-transport` and must never be inferred from a workspace path or machine alias.
- A compliant mutation requires a baseline snapshot, durable backup, pre-write compare-and-swap, exact post-write verification, and compare-and-swap rollback under the declared lock.
- Unsupported indirection, unknown authority, incomplete operations, or failed source attestations/content
  checks fail closed when artifacts disagree with trusted git-index sources. These checks do not certify
  the physical truth of registry source bytes; registry-root semantics remain the job of cheap structural
  guards plus code review.
- `migration-required` rows must retain their exact non-self disposition coordinate until the governed source changes and the checker derives compliance.
- Before merging scheduler-related changes, stage the intended tree and run the complete captured `all` bootstrap from `.github/workflows/scheduler-mutation-main.yml`, substituting only `git --no-replace-objects write-tree` for the landed-commit `rev-parse` command. Direct canonical checker commands intentionally fail closed because they cannot attest one immutable index snapshot.
