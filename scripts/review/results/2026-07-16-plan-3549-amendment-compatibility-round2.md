# #3549 Implementation-Plan Amendment Compatibility Review — Round 2

**Verdict: MAJOR**

**Reviewed revision:** `7b658ce2c3a2809b92d5f7478245108d3bb52d5d`

## Blocking findings

1. **The changed-path map still cannot satisfy the stated 400-line guardrail.** The amendment calls the repository limit hard and promises that the split will keep the core and focused test files below it (`docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md`, Implementation Amendment item 1), but the canonical map also modifies `config/workstations/registry.yaml` and `docs/modules/cli/WORKSPACE_CLI.md`. At the reviewed tree those files are already 405 and 488 lines, respectively; the canonical plan itself is 490 lines. The current WIP increased the registry from 391 to 405 lines, and the plan contains no split, compaction, grandfathering rule, or line-gate disposition for these paths. This repeats the same structural defect that caused `scripts/workspace` to be deferred. **Required change:** either make every governed modified file comply, or cite the exact policy that limits the 400-line rule to a narrower file class and state which line gate will enforce that interpretation. The plan cannot currently claim that all planned files remain below 400 lines.

2. **The native PowerShell tests still do not specify exact argv or target identity.** Slice E says tests will “capture argv through the `.cmd` shim” and “prove hostname-mode quoting” (`docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md`, Implementation Sequence item 6), while the TDD table's PowerShell row requires only “argument arrays; hostname parity; native Windows proof.” Neither location gives the exact expected wrapper-to-CLI vector or the exact captured SSH vector for each of `connect-workspace-windows.ps1` and `connect-workspace-tailscale.ps1`; neither binds generic invocation to the caller-supplied machine ID. This is correctness-critical because the design requires generic wrappers to require an explicit machine (`docs/superpowers/specs/2026-07-15-3549-registry-connection-helpers-design.md:231-235`), and round 1 already found that confusing `dev-primary` with `dev-secondary` silently retargets callers. **Required change:** enumerate native test nodes and exact expected argv for both PowerShell wrappers, including a non-repository CWD, a copied checkout path containing spaces, an explicit distinct machine ID, hostname mode, and the fallback case returning 4 with zero `.cmd`/SSH launches.

## Verified checks

- `scripts/workspace` is absent from the canonical changed-path map, and live issue #3561 explicitly owns its split, nonexistent `scripts/connection/...` paths, explicit machine selection, Windows unsupported-fallback UX, and menu tests. The revised #3549 text no longer claims that deferring this already-broken caller preserves compatibility.
- The Windows contract remains fail-closed: the plan and HTML both require unsupported fallback to return exit 4, and Slice E requires that result before SSH launch.
- The direct-executable contract is real at plan level: it requires invocation without `sys.executable`, from a non-repository CWD, in a copied checkout path containing spaces. The tracked CLI mode is `100755` and its shebang is `#!/usr/bin/env python3`.
- The amendment names RED cases for `--fall`, `ENOEXEC`, child `-signal.SIGINT`, and overlay read `OSError`, plus negative controls for exact `--fallback`, missing executable 127, unchanged normal child status, and no second process. It also separates overlay exit 4/5 from registry exit 3.
- The final focused acceptance command includes `tests/workstations/test_connection_cli.py`.
- The diff from approved-plan merge `d9db0d7665c66736ae185e462213c92da9a65d82` through the reviewed revision contains only paths represented in the canonical map. A tracked-reference search found the deferred executable caller only at `scripts/workspace`; the unchanged `docs/ops/ace-linux-2-handoff-runbook.md` invokes the fixed secondary wrapper and does not require caller migration.
- The canonical Markdown and HTML at the reviewed commit match their working-tree blobs. The HTML reflects the revised deferral, exit mapping, paused lifecycle, and required direct-executable correction, though the Markdown remains the executable source for exact test commands.

The amendment must be revised and re-reviewed before renewed user approval.
