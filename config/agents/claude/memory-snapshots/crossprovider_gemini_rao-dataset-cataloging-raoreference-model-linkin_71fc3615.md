---
name: crossprovider gemini rao-dataset-cataloging-raoreference-model-linkin
description: RAO dataset cataloging: RaoReference model linking solver/draft/condition to hull panel
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-model, hydrodynamics, cataloging]
---

Dataclass fields: solver, draft_m, loading_condition, headings_deg, n_frequencies, date, file_path, benchmark_revision. All optional except solver and draft_m. Use to_dict(exclude_none=True) for serialization. Linked to PanelCatalogEntry via raos list for multi-dataset hull entries.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
