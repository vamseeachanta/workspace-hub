# Draft child-issue pack for #2567

Parent issue: <https://github.com/vamseeachanta/workspace-hub/issues/2567>

Status: **draft only** — this file proposes bounded follow-up issues. It does **not** create live GitHub child issues.

## Child issue candidate 1

- **Title:** Extract and promote steering-gear regulatory requirements from SOLAS II-1 Reg. 29
- **Readiness:** partial
- **Why now:** local clause text is available and already verified during #2567.
- **Scope:**
  - create or update standards/source pages for SOLAS steering-gear definitions and Reg. 29 requirement buckets
  - record exact locators for definitions, timing requirements, control-system separation, alarms, and alternate power provisions
  - explicitly distinguish requirement statements from formulas
- **Required clause citations:**
  - SOLAS 2020 Chapter II-1 Part C Regulation 29
  - SOLAS 2020 Chapter II-1 Part C Regulation 3 definitions (items 1-4, 13)
  - SOLAS 2020 Chapter II-1 Part A-1 Regulation 3-1
- **Exclusions:**
  - no machinery sizing formulas
  - no class scantling calculations
  - no compliance pass/fail engine

## Child issue candidate 2

- **Title:** Extract DNV TS414 steering-gear design-torque and actuator-load clauses into clause-ready wiki/source pages
- **Readiness:** partial
- **Why now:** local DNV PDF is present and design-torque sections are verified.
- **Scope:**
  - capture exact clause text/locators for Pt.4 Ch.14 Sec.1 item 1119 and adjacent definitions
  - map variables, units, and assumptions without implementing formulas in production code
  - document edition caveats from the 2010 archive / amended text
- **Required clause citations:**
  - DNV TS414 Pt.4 Ch.14 Sec.1 item 1119
  - adjacent variable definitions and amendment notes in the same section
- **Exclusions:**
  - no code implementation
  - no claim that this is the final governing class edition for all vessels

## Child issue candidate 3

- **Title:** Extract DNV TS414 steering-gear-to-rudder-stock connection capacity requirements
- **Readiness:** partial
- **Why now:** local extraction already confirms items 1201-1215 and torque-capacity criteria.
- **Scope:**
  - clause extraction for keyed, keyless, frictional, and split-hub connection checks
  - create a vocabulary page or standards subsection for `Tdes`, rule rudder torque, friction torque, key stress, and connection capacity
  - document which pieces belong to connection design rather than stock scantling proper
- **Required clause citations:**
  - DNV TS414 Pt.4 Ch.14 Sec.1 items 1201-1215
- **Exclusions:**
  - no automatic pass/fail checker
  - no extrapolation to ABS/IACS equivalence without source capture

## Child issue candidate 4

- **Title:** Extract DNV TS414 rudder-stock diameter / safety-factor / combined-load clauses
- **Readiness:** source-gap-to-partial
- **Why now:** headings are verified, but exact formula extraction still needs focused capture.
- **Scope:**
  - identify exact rudder-stock diameter and safety-factor clauses from TS414
  - separate stock scantling formulas from steering-gear actuator formulas
  - record load-combination assumptions and where bending moments enter through actuator interaction
- **Required clause citations:**
  - DNV TS414 Pt.4 Ch.14 Sec.1 headings/clauses for rudder stock diameter and safety factor for rudder stock
  - any cross-referenced rudder-force / rule rudder torque clauses explicitly relied upon
- **Exclusions:**
  - no stock-sizing code until clauses are fully captured
  - no material allowables guessed from secondary references

## Child issue candidate 5

- **Title:** Capture ABS Part 4 steering-gear / rudder-stock clause locators for cross-class comparison
- **Readiness:** source-gap
- **Why now:** ABS is an explicit portal anchor in the registry, but the exact chapter/section was not locally captured.
- **Scope:**
  - obtain exact ABS Part 4 chapter/section references for steering gear, actuator sizing, and rudder-stock related requirements
  - update the crosswalk with exact locators and source status
  - decide whether ABS should remain a portal-only comparison source or become a promoted implementation source
- **Required clause citations:**
  - ABS Marine Vessel Rules Part 4 (2024) exact chapter / section once captured
- **Exclusions:**
  - no implementation based on portal memory
  - no claim of ABS/DNV equivalence without explicit clause comparison

## Child issue candidate 6

- **Title:** Capture steering-specific IACS UR/UI references cited by SOLAS / class-rule sources
- **Readiness:** source-gap
- **Why now:** SOLAS local extracts explicitly reference steering-related IACS interpretations, but the actual documents were not locally captured in #2567.
- **Scope:**
  - locate steering-specific IACS interpretations / unified requirements cited by SOLAS or class-rule documents
  - record exact document identifiers and applicability boundaries
  - update the source map and crosswalk
- **Required clause citations:**
  - steering-specific IACS UR/UI identifiers discovered during follow-up
- **Exclusions:**
  - no assumption that generic IACS portal access is enough
  - no implementation without local clause capture

## Recommended execution order

1. SOLAS requirement extraction
2. DNV TS414 design torque extraction
3. DNV TS414 connection-capacity extraction
4. DNV TS414 rudder-stock scantling extraction
5. ABS locator capture
6. IACS steering-specific locator capture

## Parent-issue completion note

If all that is needed from #2567 is the source map + concept boundaries + standards crosswalk + draft issue pack, then the parent issue can be considered complete without opening any of the above child issues.
