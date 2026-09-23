# Research: standards — 2026-07-13

## Key Findings

- **ISO 24656:2022 — Offshore Wind Cathodic Protection (FIRST dedicated standard):** ISO 24656:2022 is the inaugural international standard specifically for offshore wind cathodic protection, applicable to both fixed and floating structures (monopiles, jackets, floating hulls, spars, semi-submersibles). It is increasingly specified in new-project tenders across Europe/Asia and commonly paired with DNV recommended practices. This is the most recent marine CP standard and directly replaces project-specific engineering for wind applications that previously lacked a unified benchmark.

- **API 579-1/ASME FFS-1 Part 16 under development — Fiber Reinforced Polymer (FRP) Equipment:** A 2026 technical update is underway for a new Part 16 assessment procedures for composite/FRP equipment fitness-for-service. The 4th Edition of API 579-1/ASME FFS-1 (published December 2021) addressed metal equipment; Part 16 extends FFS methodology to composite risers, spools, and vessel components — addressing the material shift in subsea equipment design.

- **ABS Offshore Structural Health Monitoring Notation (SMART/SHM) launched:** ABS introduced a new notation for continuous structural health monitoring and physics-based prediction on drilling/maritime assets. The notation pairs with updated Fatigue Assessment of Offshore Structures guidance (incorporates new S-N curves + fracture-mechanics fatigue approaches). Addresses real-time structural prognosis, not just design-phase analysis.

- **DNV-RP-F105 (Free Spanning Pipelines) scope expanded 2025–26:** The revised DNV-RP-F105 now applies beyond free spans to jumpers, spools, goosenecks, doglegs, manifold piping, and flex-loops. This is a material expansion of the VIV/bending assessment practice for dynamic risers and interconnects — it effectively raises the de-facto standard of riser/jumper design scrutiny.

- **ISO/DIS 8351 proposed — Galvanic anodes for marine (Zn/Al/Mg) testing and composition:** A draft standard under ISO Development now specifies chemical makeup, electrochemical properties, size accuracy, and inspection methods for cast galvanic anode alloys used in seawater cathodic protection. Targets standardization of CP anode performance across suppliers.

---

## Relevance to Project

| Finding | Affected Package | Impact on Workflow | Recommendation |
|---------|------------------|-------------------|-----------------|
| **ISO 24656:2022 marine CP** | `digitalmodel.cathodic_protection` | If you model CP systems (e.g., fixed jacket, floating unit CP design), ISO 24656:2022 is now the **required reference** for offshore wind. Existing CP modules may reference older ISO 12473 (general seawater) or DNV; ISO 24656 is stricter/more specific. | Audit existing CP calc modules for ISO 24656 compliance; update citations in `digitalmodel.citations` sidecar to source ISO 24656 where applicable for offshore wind / floating-structure CP work. |
| **API 579-1 Part 16 (FRP)** | `digitalmodel.fitness_for_service` | If `digitalmodel` FFS assessment (wall thickness, crack-like flaws, metal loss per API 579) is extended to **composite risers or pressure vessels**, Part 16 will be **required**. Currently only metal. | Monitor API 579 Part 16 release date (likely 2026–27); when published, create a `digitalmodel.ffs_composite` module if client demand includes fiber-wrapped or composite tubulars. File a tracking issue now. |
| **ABS SMART/SHM Notation** | `digitalmodel` + `aceengineer-website` | ABS SHM Notation represents a **competitive shift** — clients will increasingly ask for real-time structural health monitoring recommendations, not just design-phase analysis. This is a market-positioning question, not an immediate calc-module need. | Promote to PROJECT.md under "Market Position" section: ABS SHM positioning raises client expectations for **prognosis** (predicted remaining life, threshold alerting) alongside **analysis** (safety factor, fatigue). Consider how `digitalmodel` could supply prognosis-ready outputs (residual strength, monitoring thresholds) as a future v1.2 roadmap item. |
| **DNV-RP-F105 scope expansion (jumpers, flex-loops)** | `digitalmodel.flexible_pipe` and riser VIV modules | If your OrcaWave/riser work includes **jumpers or flex-loops**, DNV-RP-F105 is now the governing standard for bending, VIV, buckling checks. Previously, these were ad-hoc or bundled into larger riser analysis. | Confirm whether v1.1 OrcaWave automation targets **jumpers and flex-loops** or risers only. If yes, update the scope/cited standard in Phase 7 plans. Cite DNV-RP-F105 (revised) in citations for any jumper VIV / buckling checks. |
| **ISO/DIS 8351 (anode composition & testing)** | `digitalmodel.cathodic_protection` (CP anode design/sizing) | If CP module includes **galvanic anode sizing or supplier specs**, ISO/DIS 8351 will standardize anode material properties (yield, electrochemical efficiency, cost curve). Low impact if module is design-only (uses nominal anode properties); high impact if module surfaces **supplier selection**. | Low priority for v1.1 OrcaWave. Flag for v1.2+ if CP anode design/sourcing is a client deliverable. Monitor ISO/DIS 8351 publication date (draft → published ~2026–27). |

---

## Recommended Actions

- [x] **Promote to PROJECT.md** — Add "Market Position" section: ABS SHM Notation + OpenFAST OSS + SACS cloud parallelization converge on one thesis — AceEngineer differentiators are **standards traceability + local-compute autonomy + riser/mooring/jumper specificity**. Reference the live `calc-citation-contract.md` pilot (API 579 + DNV-OS-E301) as proof-in-hand. Cite ISO 24656:2022 and DNV-RP-F105 (revised) as recent evidence that standards are tightening, not loosening.

- [ ] **Create GitHub issue** — `digitalmodel#TBD`: "FRP fitness-for-service (API 579-1 Part 16) tracking: monitor 2026 release, scope Phase 1.2 module if client demand emerges. Tag `lane:research` + `status:backlog`."

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "Standards research sync: ISO 24656:2022 marine CP, DNV-RP-F105 scope expansion (jumpers), ABS SHM Notation. Update PROJECT.md Market Position section with competitive thesis + proof artifacts."

- [ ] **Audit** — Verify that `digitalmodel.cathodic_protection` module (if it exists; unclear from codebase overview) cites **ISO 24656:2022** (not older ISO 12473) for offshore wind / floating-structure designs. If not yet implemented, plan as a citation-contract compliance task (per `.claude/rules/calc-citation-contract.md`).

- [ ] **Monitor** — SACS V12 cloud parallelization (Bentley) pricing announcements Q3/Q4 2026; OrcaFlex 2026-Q4 licensing/cloud updates. If OrcaFlex licensing shifts to cloud-only or cloud-primary, this changes v1.1 OrcaWave automation strategy (local API execution becomes a differentiator vs. cloud-lock competitors).

---

`★ Insight ─────────────────────────────────────`
**Standards are consolidating, not fragmenting.** ISO 24656 (marine CP), API 579 Part 16 (composite FFS), and DNV-RP-F105 expansion (jumper assessment) all signal that **engineering domains historically ad-hoc or fragmented are now unified into standardized practices**. This is a **tailwind for `digitalmodel`** — standards traceability (your competitive advantage per the prior synthesis) becomes more valuable, not less, as clients face more, tighter, and more-interdependent rules. The market is rewarding calculators that cite standards and explain "why this rule drove this output" — you're already doing it with the DNV-OS-E301 pilot. Expand that posture to new standards as they land.

**ABS SHM Notation represents a market-facing shift from design-time to operational-time thinking.** Competitors (SACS, ANSYS) are bundling real-time monitoring into their suite (GPU morphing, Sherlock reliability bundling). ABS is institutionalizing it via notation. This won't break `digitalmodel` (analysis tooling is orthogonal to monitoring), but it does mean clients will increasingly ask "how do I know when my design is degrading in the field?" — a question `digitalmodel` doesn't yet answer. Consider how outputs (e.g., "wall thickness above 8mm = safe; below 6mm = urgent") could feed a future monitoring dashboard. Not for v1.1, but worth naming as v1.2 strategic context.
`─────────────────────────────────────────────────`

---

**Sources:**
- [API 579 Fitness-For-Service – API](https://www.api.org/products-and-services/training/calendar/teduc-srlapi-579-fitness-for-service)
- [API 579-1/ASME FFS-1 Fitness-For-Service – ASME Learning](https://www.asme.org/learning-development/find-course/api-579-1-asme-ffs-1-fitness-service-evaluation)
- [API 579 Part 16 FRP Update – UTComp](https://utcomp.com/api-579-1-asme-ffs-1-update/api-579-part-16-assessment-levels-for-frp-assets/)
- [ISO 24656:2022 – Cathodic Protection for Offshore Wind Structures – ISO](https://www.iso.org/standard/67729.html)
- [ISO 12473:2017 General Principles Cathodic Protection in Seawater – ISO](https://www.iso.org/standard/67729.html)
- [ABS Launches Offshore Structural Health Monitoring Notation – Marine Link](https://www.marinelink.com/news/abs-launches-offshore-structural-health-509259)
- [ABS Updates Fatigue Assessment of Offshore Structures Guide – IIMS](https://www.iims.org.uk/abs-updates-fatigue-assessment-of-offshore-structures-guide/)
- [ABS Updates Fatigue Assessment – Safety4Sea](https://safety4sea.com/abs-updates-fatigue-assessment-of-offshore-structures-guide/)
- [DNV Vortex-Induced Vibration Analysis – Vivana](https://www.dnv.com/services/vortex-induced-vibration-analysis-vivana-89365/)
- [DNV Vortex-Induced Vibrations Training – Complex 3D Pipes](https://www.dnv.com/training/vortex-induced-vibrations-on-complex-3d-pipes-91637/)
- [ABS Guidance Notes on Cathodic Protection of Offshore Structures – ABS Eagle](https://ww2.eagle.org/content/dam/eagle/rules-and-guides/current/offshore/306-cathodicprotection-offshore-structures/cathodic-protection-offshore-gn-dec18.pdf)
- [ISO/DIS 8351 Draft Standard – Galvanic Anodes for Marine Applications – Institute of Corrosion](https://www.icorr.org/standards-development-cathodic-protection-isodis8351/)

**Next:** File the two GitHub issues, then confirm whether ISO 24656:2022 is already cited in any existing CP modules. One task — the standards audit.
