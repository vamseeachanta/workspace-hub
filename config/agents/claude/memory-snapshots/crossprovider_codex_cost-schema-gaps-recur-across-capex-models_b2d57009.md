---
name: crossprovider codex cost-schema-gaps-recur-across-capex-models
description: Cost schema gaps recur across CAPEX models
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, cost-modeling, capex]
---

CostDataPoint lacks contractor, award-date, asset-class, and work-package fields; CostType only supports well_cost/day_rate/total_capex (cannot distinguish host/SURF/trees/manifolds); V30 calculates subcomponents internally but emits only aggregate facilities_cost_usd. These gaps block reconciliation and detailed reporting across worldenergydata packages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
