# WRK-664 Plan HTML Review Draft

- wrk_id: WRK-664
- status: draft
- purpose: review draft contract for multi-agent and multi-workstation planning/execution
- primary_decision_needed: keep parked vs activate now

## Executive Summary

WRK-664 defines deterministic stage-level agent and workstation assignment so work can be planned and executed reliably across single or multiple machines.

## Key Checks Added

1. stage assignment matrix by agent and machine
2. machine-readiness gate before execution
3. claim-time routing + quota evidence
4. handoff evidence when machine switches occur
5. pause/fallback policy for remote coordination gaps

## User Review Focus

1. are stage assignments realistic for your current machine topology
2. should remote coordination be strict-blocking or allow limited override
3. keep parked or activate now
