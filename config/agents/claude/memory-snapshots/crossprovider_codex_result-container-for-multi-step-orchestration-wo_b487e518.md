---
name: crossprovider codex result-container-for-multi-step-orchestration-wo
description: Result container for multi-step orchestration workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [orchestration, error-handling, results-tracking, dataclass]
---

Use dataclass with optional intermediate fields (solver_results, report, plot_paths, report_json_path, hydro_data_yaml_path, report_html_path) to track outputs from each orchestration step. Wrap core logic in try/except to populate error_message + success flag, allowing caller to inspect partial results on failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
