# /mnt/ace Raw Reference Review for #2564 Yaw Moment Sweep

> Date: 2026-04-30
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2564
> Scope: find additional local raw references under `/mnt/ace` to support preliminary rudder-induced yaw-moment calculations for a typical ship.

## Result

This review was promoted into the naval-architecture LLM wiki on 2026-04-30. The preserved knowledge pack lives under `/mnt/local-analysis/workspace-hub/knowledge/wikis/naval-architecture/wiki/`:

- `concepts/yaw-moment-rudder-sweep.md`
- `concepts/rudder-force-modeling.md`
- `concepts/maneuvering-coordinate-conventions.md`
- `concepts/maneuvering-validation-metrics.md`
- `concepts/environmental-yaw-moment-coefficients.md`
- `comparisons/yaw-moment-source-extraction-2026-04-30.md`
- source pages for ABS, IMO, USCG, ShipMo3D, OrcaFlex, and OCIMF yaw coefficient figures

Validation: `uv run scripts/knowledge/llm_wiki.py lint --wiki naval-architecture` returned OK after ingestion.

## Method

- Used parallel subagents to scan `/mnt/ace` by filename, targeted text-searchable content, and naval-architecture reference collections.
- Verified the top candidates in the main session with `pdfinfo`, `pdftotext`, file existence/size checks, and direct markdown reads.
- No raw files were modified.

## Primary references to use in the plan

| Priority | Raw path | Verified evidence | Suggested use for #2564 |
|---|---|---|---|
| 1 | `/mnt/ace/O&G-Standards/SNAME/textbooks/Principles-of-Naval-Architecture-SecondRevision-Vol3-Motions-Controllability.pdf` | 357 pages. Text extraction shows `Analysis of Turning Ability`, `Hydrodynamics of Control Surfaces`, `Maneuvering Trials and Performance Requirements`, `Design of Rudder and Other Control Devices`, and yaw sign-convention content. | Primary naval-architecture reference for controllability framework, yaw/sway/rudder sign conventions, turning ability, and rudder/control-device design context. |
| 2 | `/mnt/ace/O&G-Standards/SNAME/hydrostatics-stability/Practical-Ship-Hydrodynamics-Bertram-2000.pdf` | Text extraction shows Chapter 5 `Ship manoeuvring`, `Force coefficients`, `Rudders`, `Fundamental hydrodynamic aspects of rudders and simple estimates`, `Interaction of rudder and propeller`, and `Interaction of rudder and ship hull`. | Best practical source for first-cut rudder force/yaw-moment modeling and for documenting hull/rudder/propeller interaction limitations. |
| 3 | `/mnt/ace/digitalmodel/docs/ship-design/literature/maneuvering_ship.pdf` | PDF title: *Simulation of Hydrodynamic Forces and Motions for a Freely Maneuvering Ship in a Seaway*. Subject metadata references hull maneuvering forces, propulsion, rudder-propeller interaction, and turning-circle comparisons. Text extraction shows `Hull Maneuvering Forces`, `Rudder Deflection Forces`, `FNrudder`, and `FNrudder = F2rudder cos Γrudder − F3rudder sin Γrudder`. | Implementation-oriented reference for force decomposition, rudder deflection forces, validation-style examples, and future maneuvering model expansion beyond the first lever-arm workflow. |
| 4 | `/mnt/ace/O&G-Standards/SNAME/textbooks/USNA-EN400-Principles-Ship-Performance-2020.pdf` | 484 pages. Text extraction shows Chapter 9 `Ship Maneuverability`, rudder dimensions, speed/rudder-angle dependence, turning-circle discussion, slow-speed maneuverability below ~5 kn, and ship DOF/yaw definitions. | Practical teaching reference for typical maneuverability parameters, rudder dimensions/speed/rudder-angle framing, and sanity-check ranges for sample YAML. |
| 5 | `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf` | 111 pages. Text extraction shows `Mathematical Model`, `Rudder Forces`, `Expressions for Rudder Forces`, and `Yawing Equation`; yawing equation snippet includes `Iz r_dot + m xcg [v_dot + u r] = N + NRd`. | Regulatory/design-guide context for maneuvering simulation, rudder-force terms, yawing equation structure, and acceptance framing. Do not overclaim class-rule compliance for the preliminary workflow. |
| 6 | `/mnt/ace/acma-codes/IMO/Maneouvrability/2002 MSC Circ.1053 Explanatory Notes to Manoeuvrability.pdf` | 40 pages. Text extraction shows steady turning with yaw rate ψ, speed V, drift angle β, `R = V/ψ`, equilibrium yaw-rate/rudder-angle relation, turning-circle and zig-zag tests. | External standards context for maneuverability outputs and future validation metrics, not primary formula derivation for this bounded yaw-moment sweep. |

## Secondary supporting references

| Raw path | Evidence / use |
|---|---|
| `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Manoeuvringload.md` | Plain-text OrcaFlex manoeuvring-load reference with `fx, fy, fz, mx, my, mz` equations from low-frequency added mass, plus explicit double-counting warning for Munk moment/current-load combinations. Use as a guardrail if future scope mixes rudder moment with added-mass/current yaw terms. |
| `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Currentandwindloads.md` | Supporting context for current/wind load yaw terms and sway-yaw interactions. Useful to avoid double-counting when adding environmental yaw loads later. |
| `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Referencesandlinks.md` | Bibliography leads including Lamb (1932), Wichers (1979/1988), and OCIMF load prediction references. |
| `/mnt/ace/acma-codes/USCG/NVIC's/1995 NVIC 6-95 Maneuvering Standards.pdf` | USCG/IMO maneuvering standards context; useful for compliance framing, not direct rudder/yaw formula derivation. |
| `/mnt/ace/acma-codes/USCG/NVIC's/1990 NVIC 7-89 Maneuvering Information.pdf` | Potentially relevant maneuvering-information circular; quick text extraction was poor/scanned, so OCR would be needed for use. |
| `/mnt/ace/acma-codes/OCIMF/Figures/A11, Current Yaw Moment Coefficient (Cxyc) - Loaded Tanker.pdf` | One-page yaw moment coefficient figure for current loads on loaded tanker; useful future comparison only, not rudder-induced yaw moment. |
| `/mnt/ace/acma-codes/OCIMF/Figures/A14, Current Yaw Moment Coefficient {Cxyc) - Ballasted Tanker.pdf` | One-page yaw moment coefficient figure for ballasted tanker; useful future comparison only. |
| `/mnt/ace/acma-codes/OCIMF/Figures/A19, Wind Yaw Moment Coefficient (Cxvw) - Gas Carrier.pdf` | Wind yaw-moment coefficient figure; future environmental yaw load reference. |

## Findings that should change or strengthen the #2564 plan

1. **Add a raw-reference stack to Resource Intelligence:** PNA Vol. III, Bertram, McTaggart/ShipMo3D report, USNA EN400, ABS Guide, IMO MSC/Circ.1053.
2. **Keep first implementation bounded:** raw references support much richer maneuvering models; #2564 should remain preliminary `rudder normal force × lever arm` and explicitly defer MMG/turning-circle dynamics.
3. **Strengthen sign-convention work:** PNA Vol. III and USNA EN400 should be used to document axes/DOFs/signs before finalizing positive rudder-angle interpretation.
4. **Use Bertram + McTaggart for rudder-force caveats:** both support the need to state that propeller slipstream, hull interaction, cross-flow, and full maneuvering derivatives are excluded in first pass.
5. **Use ABS/IMO only for context:** they can guide future acceptance metrics (turning circle, zig-zag, yaw-rate/rudder-angle relationship), but the first yaw-moment sweep must not claim ABS/IMO compliance.
6. **Preserve strict citation separation:** these are raw/local references. Unless a standard-derived constant is copied from a resolvable wiki page with required frontmatter, the implementation should emit literature/provenance metadata, not fabricate strict `Citation` objects.

## Recommended plan insertion

Add to #2564 plan Resource Intelligence:

```text
/mnt/ace raw references reviewed:
- PNA Vol. III — controllability, yaw/sway/rudder sign convention, turning ability, rudder/control-device design.
- Practical Ship Hydrodynamics (Bertram) — manoeuvring force coefficients, rudder simple estimates, rudder/propeller/hull interaction caveats.
- McTaggart ShipMo3D maneuvering report — hull maneuvering forces, rudder deflection forces, rudder-propeller interaction, turning-circle comparisons.
- USNA EN400 — ship maneuverability chapter, rudder dimensions, speed/rudder angle dependence, DOF/yaw definitions.
- ABS Vessel Maneuverability Guide + IMO MSC/Circ.1053 — maneuvering simulation/yawing equation and external maneuverability criteria context.
```

## Follow-up extraction tasks if implementation needs more fidelity

- Extract and cite exact pages/sections from PNA Vol. III for sign convention and control surface hydrodynamics.
- Extract exact Bertram section pages around 5.4.2 for rudder simple estimates and 5.4.4/5.4.5 for interaction exclusions.
- Extract McTaggart equations around rudder deflection forces (`FNrudder`) if planning a second-stage maneuvering model.
- OCR NVIC 7-89 only if maneuvering-information requirements become part of deliverables.
