# WRK-133: Update OrcaFlex License Agreement

## Context

The mkt-a-AceEngineer OrcaFlex agreement (`aceengineer-admin/admin/orcaflex/mkt-a-aceengineer-orcaflex.md`) needs updates for addresses, Orcina T&C compliance, 3rd-party clarification, and a mooring project conflict-of-interest clause.

**Critical compliance finding**: The Orcina T&Cs (signed Oct 17, 2024) define "Affiliate" as parent/subsidiary only (Clause 1a), prohibit sublicensing (6a), and bar third-party access (7e(v)). AceEngineer is NOT an Affiliate of mkt-a — the current agreement's "grants non-exclusive right to use" language reads as a sublicense and likely violates the Orcina Agreement.

**Solution**: Reframe as a **Consultant/Contractor Access Agreement** — AceEngineer personnel access OrcaFlex as mkt-a's consultants on mkt-a-authorized systems, not as independent licensees. This is supported by Orcina Clause 7a (use at any location) and 15a (sharing with consultants).

## Plan

### File to modify
- `D:\workspace-hub\aceengineer-admin\admin\orcaflex\mkt-a-aceengineer-orcaflex.md`

### Changes (full rewrite of the markdown)

**1. Title rename**: "OrcaFlex License Sharing Agreement" → "OrcaFlex Software Access Agreement"
- Avoids "sharing"/"sublicense" language

**2. Add both addresses in header**:
- mkt-a: 565 S. Mason Road #395, Katy, Texas 77450
- AceEngineer: 11511 Piping Rock Dr., Houston, TX 77077 (fix period after "Dr")

**3. Add Recitals section** establishing:
- mkt-a holds the Orcina license (dated Oct 14, 2024)
- AceEngineer is mkt-a's consultant/associate
- This is NOT a sublicense — it's consultant access authorization
- AceEngineer personnel access OrcaFlex on mkt-a-authorized systems under mkt-a's control

**4. Rewrite Section 1 (Software Access and Purpose)**:
- Replace "grants non-exclusive right to use" with "authorizes personnel to access as consultants"
- Explicit "This Agreement is not a sublicense" statement
- Access rights tied to mkt-a-authorized systems and mkt-a-associated projects
- Restrictions matching Orcina clauses (no sublicensing, no reverse engineering, LPK stays on mkt-a systems)
- Define "Third Party" = any entity other than mkt-a and AceEngineer
- Define "mkt-a-authorized systems"

**5. Rewrite Section 2 (Responsibilities and Terms)**:
- mkt-a: maintain license, designate systems, sole Orcina contact, right to revoke access
- AceEngineer: use only for mkt-a-associated work, comply with Orcina T&Cs, route support through mkt-a, not represent independent license ownership
- Orcina compliance clause: Orcina Agreement prevails on conflict; mkt-a may seek Orcina written consent
- Financial arrangement (unchanged): mkt-a covers MUS, cost-sharing negotiable
- Confidentiality: cover Orcina credentials, LPK info, Orcina-supplied Information

**6. Rewrite Section 3 (General Terms)**:
- Termination: 30 days notice + immediate termination if Orcina objects or AceEngineer breaches
- Upon termination: cease access, return/delete all software and credentials
- Indemnification: AceEngineer indemnifies mkt-a for breaches causing Orcina claims
- **NEW: Mooring Project Conflict-of-Interest clause**: All mooring-related projects won by AceEngineer shall be disclosed to mkt-a and mutually agreed to have no conflict of interest, on a case-by-case basis, before OrcaFlex is used on such projects
- Project terms (strengthened): work under mkt-a umbrella, mkt-a provides oversight on AceEngineer projects using OrcaFlex
- Governing law: State of Texas
- No assignment without written consent
- Electronic signatures valid

**7. Signature block**: Add addresses under each party name

### Risk note to include in the agreement
Recommend mkt-a send a brief email to Orcina (Hannah Ineson, Commercial & Licensing) confirming AceEngineer's consultant access arrangement. This converts the "medium risk" contractual interpretation into explicit authorization per Orcina Clause 12a.

### Address discrepancy note
The Orcina Quotation lists mkt-a at "2929 Briarpark Dr, Suite 220, Houston, TX 77042." The user-specified address is different (565 S. Mason Road #395, Katy, TX 77450). If mkt-a has relocated, mkt-a should notify Orcina of the address change.

## Verification
- Read updated markdown and confirm all 4 acceptance criteria addressed
- Verify no "sublicense," "grant," or "license sharing" language remains
- Verify both addresses present
- Verify Third Party definition present
- Verify mooring project conflict-of-interest clause present
- Verify Orcina compliance language present
- The `.docx` version will need manual update from the markdown (not automated)
