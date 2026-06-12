---
name: crossprovider hermes standards-mapping-requires-domain-classification
description: Standards mapping requires domain classification as prerequisite
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [standards-mapping, domain-classification, engineering-metadata]
---

Can't directly map engineering functions to standards (DNV-RP-C205, API RP 2A, ISO 19901, etc.) without first classifying by domain (hydrodynamics, structures, fatigue, geotechnical, metocean, pipeline, moorings, drilling). Mapping output structure: function_name, file, module, description, applicable_standard, standard_section, gap_flag, confidence. Identify domain from module path and docstring.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
