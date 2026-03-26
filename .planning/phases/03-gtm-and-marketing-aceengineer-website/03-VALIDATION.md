---
phase: 3
slug: gtm-and-marketing-aceengineer-website
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | jest 29.x |
| **Config file** | `jest.config.js` (aceengineer-website repo) |
| **Quick run command** | `npm test` |
| **Full suite command** | `npm test -- --coverage` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `npm test`
- **After every plan wave:** Run `npm test -- --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | Landing page | visual + unit | `npm test` | ⬜ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | Calculator demos | integration | `npm test` | ⬜ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | SEO strategy | content check | `grep -r 'meta name' src/` | ✅ | ⬜ pending |
| 03-04-01 | 04 | 2 | Pricing/access model | visual + unit | `npm test` | ⬜ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Verify existing Jest config works with PostHTML build pipeline
- [ ] Verify calculator test stubs exist for on-bottom stability and wall thickness
- [ ] Verify landing page test infrastructure covers hero section and CTA

*Existing infrastructure covers most phase requirements — PostHTML, Jest, Plotly CDN already in place.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Calculator interactivity | Demo showcase | Requires browser interaction with Plotly charts | Load each calculator, enter sample inputs, verify chart renders |
| Mobile responsive layout | Landing page | Visual check across viewports | Check 375px, 768px, 1024px breakpoints |
| Contact form submission | Signup/contact flow | Requires Web3Forms integration test | Submit test form, verify email delivery |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
