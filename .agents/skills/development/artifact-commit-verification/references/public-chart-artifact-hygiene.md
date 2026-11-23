# Public Chart Artifact Hygiene

Session source: workspace-hub #2555 vessel capability / brochure chart artifact execution.

## Reusable lesson

Generated chart/report packs often include sidecars (manifest JSON, per-chart metadata, provenance blocks) that are easier to overlook than the visible PNG/SVG/PDF/HTML. Those sidecars are still public artifact surface when they are committed or attached to a GTM/report deliverable.

## Verification pattern

1. Enumerate every generated artifact, including manifests and per-chart metadata.
2. Run the task's focused tests and render smoke.
3. Search generated artifacts for environment/client leakage, for example:
   - absolute local roots: `/mnt/`, `/tmp/`, home directories
   - staging/worktree names
   - confidential repo buckets or client identifiers
   - project names that should remain internal
4. Visually inspect at least one representative rendered chart for readability and corruption, not just file existence.
5. If leakage is found, fix the generator to emit repo-relative/artifact-relative paths. Do not hand-edit only the current manifest unless the task is a one-off manual artifact with no generator.
6. Record evidence in the closeout/handoff: tests, smoke command, scan command, visual QA, and exact committed paths.

## Why this matters

In #2555, adversarial review returned MINOR because generated chart metadata serialized absolute/local paths. The durable fix was to change the renderer so future manifests and sidecars avoid local path disclosure, then rerun tests/smoke/scan before push and closeout.
