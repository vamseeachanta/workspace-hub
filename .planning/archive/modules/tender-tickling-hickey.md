# WRK-1148 Plan: Propeller-Rudder Interaction — Literature Survey

## Context

WRK-1148 is child-a of feature WRK-1147 (propeller-rudder hydrodynamic interaction study).
The goal is to gather and synthesise the key naval architecture literature on
propeller-rudder interaction, producing a structured reference document that WRK-1149
(method selection) will consume. No implementation code is produced in this WRK.

## Scripts-over-LLM Audit

All operations are one-off document synthesis. No scripted operations required.
The 25% recurrence threshold is not met for any step.

## Acceptance Criteria (testable)

1. ≥8 references identified and summarised — verified by counting `##` headings in output file
2. Each reference entry contains: title, authors, year, key contribution, key formulae
3. Parameter definitions aligned across sources (t, w, C_L, J defined consistently)
4. Applicability ranges noted per method (J range, propeller loading, ship type)
5. Output file `digitalmodel/docs/domains/hydrodynamics/propeller-rudder-literature.md` exists and is readable

**Note on output path:** WRK spec says `docs/hydrodynamics/` but the repo pattern
is `docs/domains/hydrodynamics/`. Using the existing repo pattern.

## Sources to Cover

Two relevant PDFs already exist in the repo (can be read directly):
- `digitalmodel/docs/domains/openfoam/naval_architecture/propeller_hull_interaction.pdf`
- `digitalmodel/docs/domains/ship-design/maneuvering_ship.pdf` (McTaggart — ShipMo3D;
  metadata confirms rudder-propeller interaction content)

Additional sources (require WebSearch/WebFetch or knowledge synthesis):
1. Actuator-disk / Rankine-Froude momentum theory (textbook standard)
2. Holtrop & Mennen (1982, 1984) — ITTC semi-empirical resistance/propulsion
3. Söding (1998) / Brix (1993) "Manoeuvring Technical Manual"
4. Molland & Turnock "Marine Rudders and Control Surfaces" (2007)
5. ITTC maneuvering and propulsion test procedures
6. RANS/CFD validation studies 2010–2024

## Implementation Steps

1. **Read existing PDFs** — Extract key formulae, parameter definitions, applicability limits
   from `propeller_hull_interaction.pdf` and `maneuvering_ship.pdf`

2. **Synthesise standard theory** — Actuator-disk, Rankine-Froude, slipstream velocity
   at rudder plane (Va, Vt formulae). These are textbook — synthesise from knowledge
   and cite standard references (Carlton, "Marine Propellers and Propulsion"; Breslin
   & Andersen "Hydrodynamics of Ship Propellers")

3. **Holtrop-Mennen rudder factors** — Extract interaction coefficients from H&M
   1982/1984 papers; tabulate corrections for wake fraction w and thrust deduction t

4. **Söding/Brix methods** — Rudder-in-slipstream formulations; axial and tangential
   velocity components at rudder plane; lift augmentation factor

5. **Molland & Turnock** — Systematic RANS data; C_L vs angle-of-attack in slipstream

6. **ITTC procedures** — Relevant coefficients defined in propulsion test procedures

7. **RANS review** — Key validation data from 2010–2024 (e.g. Shen, Greco, Felli)

8. **Write output document** — Structured markdown at
   `digitalmodel/docs/domains/hydrodynamics/propeller-rudder-literature.md`

## Output Document Structure

```markdown
# Propeller-Rudder Hydrodynamic Interaction — Literature Survey
## Parameter Definitions (canonical cross-source table)
## 1. Actuator-Disk / Momentum Theory
## 2. Holtrop & Mennen (1982, 1984)
## 3. Söding (1998) / Brix (1993)
## 4. Molland & Turnock (2007)
## 5. McTaggart — ShipMo3D Maneuvering Library
## 6. Propeller-Hull Interaction PDF (repo)
## 7. ITTC Procedures
## 8. RANS/CFD Validation Studies (2010–2024)
## Applicability Summary Table
## References
```

## Pseudocode (document generation)

```
read propeller_hull_interaction.pdf → extract: Va formula, Vt formula, thrust deduction
read maneuvering_ship.pdf → extract: rudder-propeller model, interaction coefficients
synthesise actuator-disk: Va = V∞(1 + a), a = (sqrt(1+CT) - 1)/2
extract H&M 1982 corrections: w_R = f(J, D/R, geometry)
tabulate Söding axial/tangential velocity: Va_R, Vt_R at rudder mid-span
collect Molland CL data: CL = f(alpha, Va_R/V, AR)
write markdown with formulae in LaTeX/code blocks, tables, applicability ranges
```

## Test Plan

| What | Scenario | Expected |
|------|----------|----------|
| Reference count | Count `## [0-9]` headings in output | ≥8 headers |
| Parameter table | Check `J =`, `C_L =`, `t =`, `w =` in canonical table | All 4 present |
| Applicability ranges | Search for "J range" or "applies" in each section | ≥5 sections contain range info |
| Formula presence | Check for `Va` and `Vt` formulae | Both present in actuator-disk section |
| No client refs | `scripts/legal/legal-sanity-scan.sh` | exit 0 |

## Files to Create

- `digitalmodel/docs/domains/hydrodynamics/propeller-rudder-literature.md` (primary output)

## Verification

```bash
# Count references
grep -c "^## [0-9]" digitalmodel/docs/domains/hydrodynamics/propeller-rudder-literature.md

# Legal scan
bash scripts/legal/legal-sanity-scan.sh digitalmodel/docs/domains/hydrodynamics/

# Check parameter table present
grep -E "J\s*=" digitalmodel/docs/domains/hydrodynamics/propeller-rudder-literature.md
```
