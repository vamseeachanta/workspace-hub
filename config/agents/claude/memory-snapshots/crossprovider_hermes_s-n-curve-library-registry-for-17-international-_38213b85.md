---
name: crossprovider hermes s-n-curve-library-registry-for-17-international-
description: S-N curve library registry for 17+ international standards
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-patterns, fatigue-analysis]
---

221 curves across DNV-RP-C203, API RP 2A, BS 7608, IIW, Eurocode 3, ASME, NORSOK, etc. requires catalog/registry pattern with metadata (standard, environment, class, slope, intercept). List seawater/air/CP variants separately; can't hardcode all—need programmatic search. Used in fatigue module as sn_library.py with get_catalog(), search_curves() methods.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
