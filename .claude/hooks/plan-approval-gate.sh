#!/usr/bin/env bash
# Retired plan-marker gate; compatibility entry point for existing callers.
# User-authorized policy change: workspace-hub#3943.
# Task authority remains with the orchestrator; other controls remain active.
printf "%s\n" "[plan-gate] RETIRED: no separate plan approval is required for authorized implementation." >&2
exit 0
