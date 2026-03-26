---
status: complete
phase: 03-gtm-and-marketing-aceengineer-website
source: 03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-03-SUMMARY.md
started: 2026-03-26T22:10:00Z
updated: 2026-03-26T22:20:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Site Navigation
expected: Nav bar shows a "Calculators" link (between Energy Data and Case Studies) and a "Request Pricing" CTA button instead of the old "Get a Quote" button.
result: pass

### 2. Landing Page Hero
expected: Homepage hero section shows "Engineering Calculations You Can Trust" heading with "single source of truth" messaging and call-to-action buttons.
result: pass

### 3. Calculator Showcase on Landing Page
expected: Landing page has a calculator showcase section below the hero highlighting 3 tools (pipeline stability, wall thickness, fatigue life) with "Try Calculator" links to their pages.
result: pass

### 4. Pricing Page
expected: Navigating to /pricing loads a page with 3 tiers (Free, Professional, Enterprise), each showing a feature checklist and a CTA button. No payment forms — display only.
result: pass

### 5. Pricing CTAs Route to Contact
expected: Clicking any pricing tier CTA button (e.g., "Get Started" or "Contact Sales") navigates to the contact page (contact.html).
result: pass

### 6. Contact Form — Request Pricing Option
expected: Contact page form has "Request Pricing" as one of the subject/topic dropdown options.
result: pass

### 7. Footer Pricing Link
expected: Footer Quick Links section includes a "Pricing" link that navigates to the pricing page.
result: pass

### 8. Calculator Index
expected: /calculators/ page lists all 5 calculators (NPV, Fatigue Life, On-Bottom Stability, Wall Thickness, and one more) with descriptions and links.
result: pass

### 9. OBS Calculator — Inputs and Calculation
expected: On-bottom stability calculator page loads with ~13 input fields (pipe diameter, wall thickness, current velocity, wave height, etc.). Entering values and clicking Calculate produces stability results and a Plotly velocity sweep chart with green/red zones.
result: pass

### 10. Wall Thickness Calculator — Inputs and Calculation
expected: Wall thickness calculator page loads with input fields (pipe OD, wall thickness, design pressure, material grade, etc.). Clicking Calculate shows burst and collapse check results with a bar chart comparing applied vs allowable values.
result: pass

## Summary

total: 10
passed: 10
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
