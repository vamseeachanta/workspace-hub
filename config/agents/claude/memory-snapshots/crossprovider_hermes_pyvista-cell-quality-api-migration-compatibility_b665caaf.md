---
name: crossprovider hermes pyvista-cell-quality-api-migration-compatibility
description: PyVista cell_quality() API migration compatibility
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pyvista, api-compatibility, deprecation, mesh-quality]
---

PyVista 0.47.1 deprecates compute_cell_quality() but both old and new APIs may coexist. The incompatibility: old API returns cell_data['CellQuality'], new API uses the measure name as key (e.g., cell_data['scaled_jacobian']). Use hasattr() detection to handle both APIs when supporting multiple versions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
