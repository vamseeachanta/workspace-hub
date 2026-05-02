# B1528 SIROCCO Output Review Fresh-Session Prompt

Date: 2026-05-01

Purpose: copy/paste this prompt into a fresh Hermes session when the goal is to review the already-published B1528 SIROCCO output results, not redo implementation.

## Fresh prompt

```text
Review the B1528 SIROCCO yaw-moment and time-trace output results that were already published to digitalmodel main.

Start from the exit handoff:
 /mnt/local-analysis/workspace-hub/docs/session-handoffs/2026-05-01-b1528-yaw-moment-time-trace-exit-handoff.md

Then verify/read the published digitalmodel artifacts on main:

Static yaw-moment report (#2570):
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/b1528_sirocco_yaw_moment_report.html
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/b1528_sirocco_yaw_moment_report.md
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/b1528_sirocco_yaw_moment_results.csv
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/b1528_sirocco_yaw_moment_provenance.json
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/b1528_sirocco_yaw_moment_manifest.json

Time-trace report (#2571):
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_report.html
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_report.md
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_results.csv
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_provenance.json
- /mnt/local-analysis/workspace-hub/digitalmodel/outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_manifest.json

Please summarize:
1. what cases were run,
2. the key yaw moment values,
3. the time-trace trends,
4. the engineering caveats,
5. whether the outputs match the source/provenance contract,
6. and what follow-up issues remain open.

Do not redo implementation unless a real missing artifact or regression is found.
```

## Manual review guide

Start with the two HTML reports for visual inspection:

```text
digitalmodel/outputs/b1528_sirocco/b1528_sirocco_yaw_moment_report.html
digitalmodel/outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_report.html
```

Then use the CSV files for numerical checks:

```text
digitalmodel/outputs/b1528_sirocco/b1528_sirocco_yaw_moment_results.csv
digitalmodel/outputs/b1528_sirocco/time_trace/b1528_sirocco_time_trace_results.csv
```

Key static yaw workbook-regression values to check:

| Case | Expected workbook-regression yaw moment |
|---|---:|
| `2.5 kn`, `+1 deg`, port factor `Cr=1.065` | `+112.158527 kN-m` |
| `2.5 kn`, `-1 deg`, starboard factor `Cr=0.935` | `-98.467815 kN-m` |

## Important caveat

The workbook-regression mode reproduces the legacy workbook's evaluated-cell behavior. It is not a full MMG simulation, incident reconstruction, IMO compliance assessment, or class compliance conclusion.
