# Plan for #3582: equality-matrix-cron.sh on Windows must collect via the CIM overlay

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-07-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3582
> **Client:** N/A
> **Project:** —
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-18-plan-3582-claude.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/readiness/equality-matrix-cron.sh:25` — collection step is a bare `bash collect-equality.sh`, on every OS.
- Found: `scripts/readiness/collect-equality.ps1` — the sanctioned Windows collector is a THIN CIM overlay: it computes the five Windows-hard compute fields, exports `EQ_*` overrides + `EQ_PUBLIC_HOST`, prepends uv's real python to PATH (so provider-harness probes don't fall to the Store stub), then **delegates to the .sh**. Chain `cron → ps1 → sh` is recursion-free by construction (the .sh never calls the ps1).
- Found: `scripts/readiness/collect-equality.ps1:100-108` — `Resolve-EqualityMachineLabel` still throws on hosts absent from the hardcoded map; it did NOT receive the #3571 identity-file layer (only `equality-report.ps1` did).
- Found (live incident, 2026-07-18): the no-arg cron on ace-win-1 published `ram_total_mib: unknown` + MISSING-EVIDENCE provider dims twice (`ca687df16`, `6be40190d`), overwriting the good CIM-backed report; remediated manually via the ps1 + publish (`2a5ea1cb3`).
- Found: `tests/readiness/test_equality_matrix_cron_deps.py` (cron contract tests), `tests/readiness/test_collect_equality.py::test_identity_label_set_single_sourced_across_mirrors` (pins `equality-report.ps1`'s label set to the bash lib — does not yet cover `collect-equality.ps1`).
- Gap: no Windows branch in the cron's collect step; no identity-file fallback in the collector ps1; the single-source label test covers only one of the two ps1 mirrors.

### Standards
Not applicable (harness/infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages.

## Design

1. **`equality-matrix-cron.sh` — OS-conditional collect step.** On `uname -s` matching `MINGW*|MSYS*|CYGWIN*` AND `powershell.exe` resolvable, the collect step will run
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/readiness/collect-equality.ps1` (appending `-Machine "$EQ_MACHINE"` when `EQ_MACHINE` is set, preserving the reconcile-printed remediation contract from #3571). All other platforms keep the bash collector byte-for-byte. If powershell.exe is absent on a Windows host, the cron FAILS loud via its existing `fail()` (notify + nonzero) — a bash-collector fallback would re-publish exactly the degraded evidence this issue exists to prevent, and every supported Windows host ships powershell.exe (r1 finding 1).
   Behavior change, intended: routing through the ps1 adds its freshness fail-fast preflight to the Windows cron path — a behind/stale checkout now refuses to collect instead of collecting silently, matching how the SessionCuration wrapper already behaves on this host (r1 finding 2).
2. **`collect-equality.ps1` — identity-file fallback.** `Resolve-EqualityMachineLabel`'s default branch will consult the #3571 machine-identity file (same semantics as `equality-report.ps1`: `WORKSPACE_HUB_MACHINE_IDENTITY` override, `machine`/`expected_hostname` keys, known-label validation, fail-loud on malformed/foreign files) before throwing. Explicit `-Machine` continues to short-circuit the function entirely.
3. **Label-set single-sourcing.** `test_identity_label_set_single_sourced_across_mirrors` will additionally parse `collect-equality.ps1`'s known-label set and assert equality with `scripts/readiness/lib/machine-identity.sh` — both ps1 mirrors pinned to the one bash source.

## Implementation (TDD — tests first)

1. Tests:
   - `tests/readiness/test_equality_matrix_cron_deps.py`: static contract — the cron contains the `MINGW*|MSYS*|CYGWIN*` branch invoking `collect-equality.ps1`, passes `-Machine` under `EQ_MACHINE`, and retains the bash fallback with a stderr marker.
   - `tests/readiness/test_collect_equality_ps1_schema.py` (or the ps1-contract style test): `collect-equality.ps1` contains the identity-file fallback (`Get-MachineIdentityFromFile`-equivalent) in the default branch only, after the map.
   - Extend `test_identity_label_set_single_sourced_across_mirrors` to cover both ps1 files.
2. Implement the cron branch and the ps1 fallback.
3. Live AC on ace-win-1: no-arg `bash scripts/readiness/equality-matrix-cron.sh` (no `EQ_MACHINE`, identity file present) produces a report with numeric `ram_total_mib` AND populated provider-harness dims, and publishes with the `ace-win-1` subject.

## Acceptance criteria

1. New/extended tests green; touched suites keep their baseline state on ace-win-1 (baseline-diff, not absolute green — this box carries known environment failures).
2. Live AC (step 3 above) verified on ace-win-1; the published yaml's `compute.static.ram_total_mib` is numeric.
3. `rg -i` over the diff for private hostname tokens returns nothing; `legal-sanity-scan.sh --diff-only` PASS.
4. Linux path provably untouched: the cron's non-Windows branch is textually the existing `bash collect-equality.sh` invocation.

## Risks

- **PowerShell 5.1 vs 7 differences in the ps1 fallback:** mirror the exact code shape already shipped in `equality-report.ps1` (StrictMode-safe, `Get-Content`-based parsing) rather than new idioms.
- **Cron under Task Scheduler vs interactive Git Bash:** `powershell.exe` resolution differs by PATH; the branch uses `command -v powershell.exe` and falls back loudly rather than assuming.
- **Wrapper double-delegation:** `curate-session-memory.ps1` and `equality-report.ps1` already call the ps1 collector directly — they never invoke the cron's collect step, so no double-collection is introduced.
