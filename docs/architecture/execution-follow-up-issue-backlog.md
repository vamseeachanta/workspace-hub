# Execution Follow-up Issue Backlog (#2728)

These are body/command drafts only. They are not self-approved implementation work.

## Execution manifest validator

```bash
gh issue create --title "feat(execution): implement execution manifest validator for #2728" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/execution-manifest-validator.md
```

Body draft: build a validator for `docs/architecture/execution-manifest.schema.yaml` and fail closed on missing source IDs, missing evidence, inline raw data, or public output without promotion gates. Parent: #2728.

## runtime enforcement

```bash
gh issue create --title "feat(execution): enforce report handoff gates at runtime" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/execution-runtime-enforcement.md
```

Body draft: connect execution manifests to report handoff checks so `report_eligible` cannot be asserted without tests, legal scan, checksums, review artifacts, and output-residency compatibility. Parent: #2728.

## Machine/provider routing registry adapter

```bash
gh issue create --title "feat(execution): add machine/provider routing registry adapter" --label enhancement --label domain:infrastructure --label cat:operations --body-file docs/architecture/follow-up-bodies/execution-routing-registry-adapter.md
```

Body draft: expose a read-only adapter over `config/workstations/registry.yaml` for routing decisions while leaving #2119/#1838/#2089 as open policy dependencies. Parent: #2728.

## Registry/source gap adapter

```bash
gh issue create --title "feat(execution): block unresolved repo/client/wiki source paths until #2731/#2732 registry exists" --label enhancement --label domain:workflow --label cat:documentation --body-file docs/architecture/follow-up-bodies/execution-source-registry-gap.md
```

Body draft: fail closed on unregistered repo/client/wiki paths and require source registry references before execution manifests can become report eligible. Parent: #2728.
