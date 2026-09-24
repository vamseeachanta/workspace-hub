---
name: crossprovider gemini qa-closure-gate-5-section-html-report-sme-verifi
description: QA closure gate: 5-section HTML report + SME verification + data checks
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [qa, verification, html-report, sme-dispatch, data-quality, completion-gate]
---

Before marking a WRK complete, invoke `qa-closure` which generates a paired HTML report (sections: inputs, process, outputs, QA checks, verdict), dispatches SME verification skill based on output type (rao-diffraction→hydrodynamic-analysis, mooring-analysis→mooring-design, etc.), and runs automated data checks (NaN/Inf, unit validation, range checks). Gate blocks until PASS or WARN is issued.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
