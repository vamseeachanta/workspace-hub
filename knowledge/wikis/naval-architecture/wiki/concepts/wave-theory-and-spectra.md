---
title: "Wave Theory and Spectra"
tags: ["wave-theory", "spectra", "jonswap", "pierson-moskowitz", "ittc", "linear-waves"]
sources:
  - naval-architecture-resources
added: 2026-05-02
last_updated: 2026-05-02
see_also:
  - concepts/seakeeping.md
  - concepts/hydrostatics.md
---

# Wave Theory and Spectra

## Scope

This page summarizes linear surface-wave theory and the standard spectral families used to describe ocean wave climates as inputs to seakeeping and structural analyses. It is the wave-input companion to `concepts/seakeeping.md` (which covers the ship-response side). Nonlinear and breaking-wave theories, slamming kinematics, and design-wave selection for fatigue are out of scope and reserved for separate pages.

## Key Concepts

- **Linear (Airy) wave theory** — small-amplitude, sinusoidal free-surface solution to Laplace's equation; basis for transfer-function methods.
- **Dispersion relation** — relates wave frequency to wavenumber and water depth; deep, intermediate, and shallow regimes.
- **Wave kinematics** — orbital velocities and accelerations decay exponentially with depth in deep water.
- **Stokes higher-order theory** — series expansion for steeper waves; captures non-symmetric crests and troughs.
- **Wave energy spectrum (S(omega))** — distribution of variance over frequency; significant wave height Hs and peak period Tp characterize a sea state.
- **Pierson-Moskowitz (PM)** — fully developed open-ocean spectrum; one-parameter form (wind speed) or two-parameter (Hs, Tp).
- **JONSWAP** — fetch-limited spectrum with peakedness parameter gamma; standard for North Sea design and a basis for many class-society fatigue analyses.
- **ITTC two-parameter spectrum** — towing-tank-community variant of PM, parameterized by Hs and mean period.
- **Bretschneider / ISSC** — modified two-parameter forms used in offshore and ship-design practice.
- **Directional spreading** — angular distribution of wave energy about the mean direction; cosine-power spreading common.
- **Short-term vs long-term statistics** — spectra characterize a stationary 3-hour sea state; long-term distributions aggregate scatter-diagram occurrences.

## Standards / References

- ITTC — Recommended Procedures, environmental modeling section (https://ittc.info/).
- IMO — environmental conditions referenced in operational stability and seakeeping guidance.
- SNAME — *Principles of Naval Architecture*, Volume III — *Motions in Waves and Controllability*.

## Cross-References

- [Seakeeping and Ship Motions](seakeeping.md) — RAO-based response evaluation that consumes these spectra.
- [Ship Hydrostatics](hydrostatics.md) — restoring properties used in linear-response models.
- **Cross-wiki (engineering)**: [Wave Theory for Offshore Engineering](../../../engineering/wiki/concepts/wave-theory-offshore.md) -- similar slugs (65%); shared tags: jonswap, pierson-moskowitz, spectra, wave-theory; shared keywords: cross-references, jonswap, spectra, spectrum, statistics; shared entities: JONSWAP
