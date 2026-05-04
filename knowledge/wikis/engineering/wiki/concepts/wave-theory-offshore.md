---
title: "Wave Theory for Offshore Engineering"
tags: [waves, wave-theory, spectra, jonswap, pierson-moskowitz, wave-statistics, irregular-seas]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# Wave Theory for Offshore Engineering

Foundation of all offshore hydrodynamic analysis. Covers wave spectra, statistics, irregular seas, kinematics, transformation (shoaling, refraction, diffraction), and extreme value estimation.

## Core Topics

1. **Regular wave theory** — linear (Airy) and nonlinear (Stokes, stream function) solutions
2. **Wave spectra** — JONSWAP, Pierson-Moskowitz, scatter diagrams for fatigue and extreme analysis
3. **Wave statistics** — Significant wave height (Hs), spectral moments (m0, m1, m2, m4), zero-crossing period (Tz)
4. **Time series generation** — Inverse FFT from spectra with random phases for time-domain simulation
5. **Extreme value analysis** — Return period estimation, Weibull/Gumbel fits, contour methods

## JONSWAP Spectrum

The Joint North Sea Wave Project spectrum is the standard for fetch-limited seas:

`S(f) = alpha * g^2 / (16 * pi^4 * f^5) * exp(-5/4 * (fp/f)^4) * gamma^r`

where `r = exp(-(f-fp)^2 / (2*sigma^2*fp^2))`, sigma = 0.07 (f < fp) or 0.09 (f > fp).

Peak enhancement factor gamma typically 1.0 (Pierson-Moskowitz) to 7.0 (fetch-limited North Sea), default 3.3.

## Long-Period Swell

Long-period swell (T > 15s) is a critical driver of mooring failures at LNG terminals. Even very small amplitudes (~50mm) can excite resonant vessel motions through second-order difference frequency forces. This phenomenon is documented extensively in the [NW Shelf LNG mooring investigation](../entities/nws-lng-mooring-investigation.md).

## Cross-References

- **Related concept**: [VIV Riser Fatigue](../concepts/viv-riser-fatigue.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related standard**: [DNV-RP-C205](../standards/dnv-rp-c205.md)
- **Related concept**: [Mooring Line Failure Physics](../concepts/mooring-line-failure-physics.md)
- **Cross-wiki (marine-engineering)**: [Long-Period Swell & Resonance](../../../marine-engineering/wiki/concepts/long-period-swell-resonance.md) — long-period swell spectra and second-order forces driving resonant mooring failures at LNG terminals
- **Cross-wiki (marine-engineering)**: [LNG Carrier Mooring](../../../marine-engineering/wiki/entities/lng-carrier-mooring.md) — wave environment (swell, JONSWAP spectra) as primary design driver for LNG terminal moorings
- **Cross-wiki (naval-architecture)**: [Seakeeping and Ship Motions](../../../naval-architecture/wiki/concepts/seakeeping.md) — wave spectra (JONSWAP, Pierson-Moskowitz) as fundamental input to vessel motion prediction
- **Cross-wiki (naval-architecture)**: [Wave Theory and Spectra](../../../naval-architecture/wiki/concepts/wave-theory-and-spectra.md) -- similar slugs (65%); shared tags: jonswap, pierson-moskowitz, spectra, wave-theory; shared keywords: cross-references, jonswap, spectra, spectrum, statistics; shared entities: JONSWAP
