---
name: crossprovider hermes skill-lookup-can-fail-when-skill-is-available-vi
description: Skill lookup can fail when skill is available via other paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, environment, fallback]
---

`skill_view({"name":"business.gtm-parametric-demo-reports"})` fails with 'not found' despite skill being invokable. When skill lookup fails, fall back to direct terminal/tool invocation rather than assuming skill is unavailable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
