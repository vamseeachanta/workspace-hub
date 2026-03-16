---
name: qa-closure
description: "Automated QA closure for AI agent work items \u2014 generates paired\
  \ HTML reports (input \u2192 process \u2192 output \u2192 QA verdict), invokes SME\
  \ verification skills, runs data quality checks (unit validation, range checks),\
  \ and emits a final PASS / WARN / FAIL verdict before a WRK item may be marked complete.\n"
version: 1.0.0
category: workspace-hub
last_updated: 2026-02-24
wrk_ref: WRK-229
invoke: /qa-closure
trigger: pre-complete
auto_execute: false
related_skills:
- ecosystem-health
- tool-readiness
- orcaflex-specialist
- hydrodynamic-analysis
- mooring-analysis
- orcawave-analysis
tags:
- qa
- verification
- html-report
- sme
- data-quality
- work-item-lifecycle
platforms:
- all
capabilities: []
requires: []
see_also:
- qa-closure-usage
- qa-closure-agent-completion-gate
- qa-closure-step-1-identify-output-type
- qa-closure-step-2-generate-html-report
- qa-closure-step-3-invoke-domain-sme-skill
- qa-closure-step-4-run-data-quality-checks
- qa-closure-step-5-emit-qa-verdict
- qa-closure-html-report-template
- qa-closure-integration-with-work-item-lifecycle
- qa-closure-related
---

# Qa Closure

## Sub-Skills

- [Usage](usage/SKILL.md)
- [Agent Completion Gate](agent-completion-gate/SKILL.md)
- [Step 1 — Identify Output Type](step-1-identify-output-type/SKILL.md)
- [Step 2 — Generate HTML Report](step-2-generate-html-report/SKILL.md)
- [Step 3 — Invoke Domain SME Skill](step-3-invoke-domain-sme-skill/SKILL.md)
- [Step 4 — Run Data Quality Checks](step-4-run-data-quality-checks/SKILL.md)
- [Step 5 — Emit QA Verdict](step-5-emit-qa-verdict/SKILL.md)
- [HTML Report Template](html-report-template/SKILL.md)
- [Integration with Work Item Lifecycle](integration-with-work-item-lifecycle/SKILL.md)
- [Related](related/SKILL.md)
