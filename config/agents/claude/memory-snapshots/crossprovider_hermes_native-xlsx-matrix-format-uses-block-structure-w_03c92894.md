---
name: crossprovider hermes native-xlsx-matrix-format-uses-block-structure-w
description: Native xlsx matrix format uses block structure with frequency headers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [xlsx, data-format, orcawave]
---

OrcaWave native xlsx (e.g., L00_test01.xlsx): Frequency blocks separated by 'Added mass for frequency X.X rad/s' header rows; each 6×6 matrix has DOF row labels (1-6) and body name column; heading changes mid-column (e.g., 0.0→27.0 at row 60). Pipeline format (test01_unit_box.xlsx) uses clean DOF_Mag/Phase columns instead.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
