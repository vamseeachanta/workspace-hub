---
phase: 4
slug: client-acquisition-3-5-clients-broad-individual-user-base
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Jest 30.2.0 (JS) + pytest (Python) |
| **Config file** | `aceengineer-website/package.json` (jest config inline) |
| **Quick run command** | `cd aceengineer-website && npm test` |
| **Full suite command** | `cd aceengineer-website && npm test && cd .. && python -m pytest aceengineer-website/tests/python/ -x` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd aceengineer-website && npm test`
- **After every plan wave:** Run `cd aceengineer-website && npm test && cd .. && python -m pytest aceengineer-website/tests/python/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| D-12 | TBD | TBD | Page enhancements | unit | `cd aceengineer-website && npm test` | Yes | ⬜ pending |
| D-15 | TBD | TBD | GA4 events | grep | `grep -r "gtag('event'" aceengineer-website/content/ \| wc -l` | N/A | ⬜ pending |
| D-04 | TBD | TBD | Case studies | unit | `cd aceengineer-website && npm test` | Yes | ⬜ pending |
| D-09 | TBD | TBD | Funnel flow | manual | Visual verification in browser | N/A | ⬜ pending |
| D-13 | TBD | TBD | GitHub pipeline | smoke | `gh issue list --label pipeline:contacted --state all` | N/A | ⬜ pending |
| D-XX | TBD | TBD | Contact form enhancement | manual | Submit test form, verify project_type field | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* Existing Jest build tests validate structural integrity of HTML enhancements. New case study pages validated by existing build.test.js which processes all HTML files in `content/`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GA4 events fire correctly | D-15 | Requires browser Realtime report | Open page, trigger events, check GA4 Realtime |
| Enterprise funnel flow | D-09 | Multi-page visual navigation path | Navigate calculator → case study → contact form |
| Contact form project type | D-XX | Requires live form submission | Submit test form, verify web3forms email has project_type |
| GA4 custom dimensions | D-15 | Requires GA4 Admin console | Register dimensions in GA4 Admin, verify in reports |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
