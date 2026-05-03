---
title: "Ship Resistance Components"
tags: ["resistance", "frictional", "wave-making", "form", "ittc", "froude"]
sources:
  - naval-architecture-resources
added: 2026-05-02
last_updated: 2026-05-02
see_also:
  - concepts/resistance-propulsion.md
  - concepts/propeller-theory.md
---

# Ship Resistance Components

## Scope

This page enumerates the physical components of total ship resistance and the canonical decomposition used in towing-tank scaling. It is the resistance-side complement to `concepts/propeller-theory.md` and `concepts/marine-propulsors.md`; the parent index page is `concepts/resistance-propulsion.md`. It does NOT cover propulsor selection (see propulsors page) and does NOT enumerate ITTC procedure-specific formulas (those will live in a future standards page).

## Key Concepts

- **Frictional resistance (Rf)** — viscous shear over the wetted surface; scaled by a friction-line coefficient.
- **Wave-making resistance (Rw)** — energy radiated as the free-surface wave pattern; strongly Froude-number dependent.
- **Form (viscous-pressure) resistance** — pressure drag from the boundary-layer thickening at the stern; captured via a form factor (1+k).
- **Appendage resistance** — additional drag from rudder, bilge keels, shaft brackets, bossings, fin stabilizers.
- **Air resistance** — aerodynamic drag on superstructure and exposed hull above the waterline.
- **Roughness allowance** — added correlation allowance for hull-coating texture and fouling state.
- **Froude number (Fn = V / sqrt(g*L))** — non-dimensional speed governing wave-making; basis for geometric similitude.
- **Reynolds number (Rn = V*L/nu)** — governs frictional regime; cannot be matched simultaneously with Fn at model scale.
- **ITTC scaling decomposition** — total coefficient Ct decomposed into frictional + residuary; residuary scaled by Froude similarity.

## Standards / References

- ITTC — Recommended Procedures for resistance prediction; ITTC 1957 model-ship correlation friction line (procedure numbers to be verified at codification time; see https://ittc.info/).
- SNAME — *Principles of Naval Architecture*, Volume II — *Resistance, Propulsion and Vibration* (resistance chapters).
- Bertram — *Practical Ship Hydrodynamics*, resistance chapter.

## Cross-References

- [Ship Resistance and Propulsion](resistance-propulsion.md) — parent router page.
- [Propeller Theory](propeller-theory.md) — companion page on thrust generation.
