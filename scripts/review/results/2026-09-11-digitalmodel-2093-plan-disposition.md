# Digitalmodel 2093 plan review disposition

Scope: one mooring-buoy configuration-to-native-results workflow, with operational acceptance separated from numerical/physical qualification. Plan revision 3 remains pending user approval.

- [Codex actual review](../../../docs/reports/2026-09-11-digitalmodel-2093-codex-plan-review.md): REQUEST_CHANGES, one MAJOR. Main verified the existing harness closes its Job handle and waits only for root exit.
- [Claude actual review](../../../docs/reports/2026-09-11-digitalmodel-2093-claude-plan-review.md): MAJOR, Haiku low, 89.96 seconds, exit 0. Packet review of revision 1 and actual source; no native execution.

Main revised the plan inline, preserving actual provider verdicts rather than asserting consensus on the final revision:

| Finding | Disposition |
| --- | --- |
| Root exit does not prove whole-job drain before independent readback | Accepted. Revision 2 requires retained queryable handle, bounded termination and ActiveProcesses=0 plus root exit; query failure/drain timeout blocks subsequent phases. Root-exited/descendant-active RED coverage is explicit. [2095](https://github.com/vamseeachanta/digitalmodel/issues/2095) promotes the generalizable audit. |
| Empty-script value unspecified | Clarified: Python empty string, quoted empty YAML string. Explicit null/nonempty overrides fail this case's preflight; unrelated nulls remain preserved. Source inspection proves serialization risk, not a fresh native failure. |
| Model-mode interface unspecified | Clarified: extend existing PowerShell wrapper with Mode/Manifest, preserve Smoke default; dispatch a new thin CLI with solve/readback phases. No fixed-smoke CLI rewrite or new queue. |
| Readback tolerance and required output set unclear | Accepted. Six dynamic histories and all stated static outputs are required, with no fallback subset. Saved-result values/counts/times require exact equality. Independent main-stage time-grid validation uses predeclared 1e-9-second representation tolerance only. Original comparisons remain descriptive, without a numerical parity verdict. |
| Manifest schema and seed enforcement unclear | Accepted. Versioned tracked YAML case contract and private JSON run manifest have required identity/hash/selection/resource fields and strict failure rules. Wrapper sets seed before each child; bytes are rechecked around native use. |
| 300-second limit lacks measured runtime | Rejected as an approval prerequisite: no native timing has been measured. The plan defines an exposure cap, not a runtime prediction. Timeout is incomplete qualification and never permission to shorten input or increase the cap. |
| Existing smoke script lacks planned value comparator | Existing-code limitation confirmed; not a separate implementation defect. New model-mode tests and comparator are explicit deliverables. |
| Reference comparison timing and damping provenance | Clarified: offline differences before first solve; preflight consumes no attempt. Guide and source YAML are separate provenance records, not calibrated numerical oracles. |

The plan author checked source snippets, local artifact existence and primary Orcina result definitions. No code, model data, native execution, deployment or approval label changed. Implementation/code review and physical qualification remain separate gates. The user will approve the concrete bounded scope before implementation or native invocation.
