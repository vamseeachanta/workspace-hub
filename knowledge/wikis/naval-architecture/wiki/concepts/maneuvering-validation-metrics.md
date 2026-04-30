---
title: "Maneuvering Validation Metrics"
tags: [maneuvering, validation, imo, abs]
sources:
  - pna-vol-iii-motions-controllability
  - imo-msc-circ-1053-manoeuvrability-explanatory-notes
  - uscg-nvic-6-95-maneuvering-standards
  - abs-vessel-maneuverability-guide-2017
  - mctaggart-shipmo3d-maneuvering-2007
added: 2026-04-30
last_updated: 2026-04-30
---

# Maneuvering Validation Metrics

This page captures future validation metrics for [[yaw-moment-rudder-sweep]] and later maneuvering simulators.

## Turning-circle measures

PNA Vol. III and ShipMo3D define common turning-path metrics:

- **advance**: longitudinal displacement after rudder-command initiation
- **transfer**: lateral displacement
- **tactical diameter**: transfer at heading change of 180°
- **steady/final turning diameter**: diameter after transient turn stabilizes

Raw locators:

- PNA Vol. III, §6.1, PDF p.164 / printed p.209.
- ShipMo3D report, §3 / Figure 5, printed pp.7-9.

## IMO / USCG baseline criteria

IMO MSC/Circ.1053 explanatory notes and USCG NVIC 6-95 reproduce the baseline trial criteria:

- advance `<= 4.5 L`
- tactical diameter `<= 5 L`
- initial turning ability: with 10° rudder, travel `<= 2.5 L` before 10° heading change
- 10°/10° first overshoot:
  - `<= 10°` if `L/V < 10 s`
  - `<= 20°` if `L/V >= 30 s`
  - `<= 5 + 0.5(L/V)` degrees if `10 <= L/V < 30 s`
- 10°/10° second overshoot: `<= first-overshoot criterion + 15°`
- 20°/20° first overshoot: `<= 25°`
- full-astern stopping track reach: `<= 15 L`, with modification possible for very large ships

Raw locator: `/mnt/ace/acma-codes/USCG/NVIC's/1995 NVIC 6-95 Maneuvering Standards.pdf`, PDF p.8.

## Yaw-rate / rudder-angle relation

IMO describes steady turning with:

```text
R = V / psi_dot
```

and uses the equilibrium yaw-rate/rudder-angle relation (spiral loop curve) to diagnose dynamic instability. Positive-slope branches can indicate unstable equilibria; direct and reverse spiral tests can map stable and unstable branches.

Raw locator: `/mnt/ace/acma-codes/IMO/Maneouvrability/2002 MSC Circ.1053 Explanatory Notes to Manoeuvrability.pdf`, §1.2.2.1 and §1.2.2.7-1.2.2.8.

## ABS rating structure

ABS extends IMO pass/fail metrics into ratings:

```text
Rt = 0.25 * (Rtd + Rt_alpha + Rti + Rts)
```

where rating components cover tactical diameter, overshoot, initial turning, and stopping ability.

Raw locator: `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf`, Section 1-2 and Appendix 3.

## Compliance caveat

These metrics do not validate a simple rudder-force yaw-moment sweep by themselves. They are future simulation-level checks. IMO/USCG standard conditions assume deep, unconfined, sheltered water; near full-load/even-keel trial conditions; calm-weather corrections; and validated model/computer simulation when trials differ from full-load standard condition.

## Related pages

- [[yaw-moment-rudder-sweep]]
- [[rudder-force-modeling]]
- [[maneuvering-coordinate-conventions]]
