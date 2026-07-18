---
name: reference_family_us_passport_locations
description: "Where current US passport scans live in achantas-data + booking-critical facts (expiries, Sabitha surname trap, Devakrishna 6-month-rule constraint)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: cbae393b-ec54-4eee-9307-5203c71281b2
  modified: 2026-07-18T07:18:12.217Z
---

# Family US passports — canonical scan locations (verified 2026-07-18)

Raw numbers stay in the scans per [[project_family_data_two_repo_curation]] (raw PII → achantas-data only). Read the PDF when a number is needed; verify against the MRZ lines (each field carries a check digit).

| Person | Current scan (in `/mnt/local-analysis/achantas-data/`) | Expires |
|---|---|---|
| Vamsee | `va/2022-VA_US_PP.pdf` | 11 Sep 2032 |
| Sabitha | `sd/ID/2021-SD_US_PP.pdf` | 22 Jul 2031 |
| Devakrishna | `da/DA_Passport.pdf` | **22 Jun 2027** |

**Booking traps (both verified against the data pages):**
- **Sabitha's passport surname is DEEPTHIMAHANTI, not Achanta** — tickets must match the passport exactly.
- **Devakrishna's passport is the family travel constraint**: 6-month validity rule makes it tight for travel after ~late Dec 2026 → renew first ([[project_devakrishna_passport_renewal]]).

Older/cancelled copies live in per-person `superseded/` folders and `sd/ID/other_legal/` — do NOT use those (e.g. `2017-Sabitha_Passport_Cancelled.pdf`).

Search tip: `_health/` folders are medical only; passports are under each person's top-level folder (`va/`, `sd/ID/`, `da/`). Grepping all of `/mnt/local-analysis/workspace-hub` for "passport" is slow (NTFS-FUSE) and finds nothing useful — go straight to `achantas-data`.
