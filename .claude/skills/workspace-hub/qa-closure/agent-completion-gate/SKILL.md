---
name: qa-closure-agent-completion-gate
description: 'Sub-skill of qa-closure: Agent Completion Gate.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Agent Completion Gate

## Agent Completion Gate


Agents MUST NOT mark a WRK item complete until all of the following pass:

- [ ] Output artefacts exist and are readable
- [ ] At least one automated QA check has run and returned PASS or WARN
- [ ] HTML report generated at `.claude/state/qa-reports/WRK-NNN-qa.html`
- [ ] QA verdict recorded in the WRK item frontmatter (`qa_verdict:`)

---
