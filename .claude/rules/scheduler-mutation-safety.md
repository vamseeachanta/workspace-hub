# Scheduler Mutation Safety

- Every repo-tracked scheduler mutator and transitive entrypoint must be registered in `config/scheduled-tasks/mutation-surfaces.yaml`.
- Registry inclusion is audit evidence, not authorization to mutate live cron, systemd, or Windows Task Scheduler state.
- Destructive ownership must use parsed or exact identity. Descriptive metadata and arbitrary substring matches cannot certify compliance.
- A compliant mutation requires a baseline snapshot, durable backup, pre-write compare-and-swap, exact post-write verification, and compare-and-swap rollback under the declared lock.
- Unsupported indirection, unknown authority, incomplete operations, or failed source attestations fail closed.
- `migration-required` rows must retain their exact non-self disposition coordinate until the governed source changes and the checker derives compliance.
- Run `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` and `--check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` before merging scheduler-related changes.
