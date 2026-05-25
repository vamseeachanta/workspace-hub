---
name: reference-ocimf-annex-a-graphic-style
description: "Canonical graphical conventions for OCIMF MEG3/MEG4 Annex A ship-force schematics — hull rendering, arrow weight, label placement, caption pattern, color scheme"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ea3c0fbd-33d7-41f3-a92e-42b0026c13c7
---

# OCIMF MEG3/MEG4 Annex A schematic style

Researched 2026-05-22 (workspace-hub #2760 Pass G; full agent transcript with sources at `/tmp/claude-1000/.../tasks/aee789e5d3de06dc8.output`). Verified against OCIMF 2010 *Estimating The Environmental Loads On Anchoring Systems* which reproduces MEG3/Annex A "Figure 1: Sign Convention" verbatim.

## Hull rendering
- **Solid filled silhouette** in single muted color (terracotta/rust-brown `#b87060` in OCIMF 2010 reproduction)
- **NOT transparent** — flat fill, no fill-opacity tricks
- Hairline stroke: 0.5–0.75 pt
- Top-down (plan) view, aspect ratio elongated (~6:1, more than true VLCC ~5.5:1)
- No deck detail or superstructure on the sign-convention figure itself — just clean closed hull

## Force arrows
- Stroke-width ~1.5 pt (not 5 px — fine, single-headed)
- Slim arrowheads ~3–4 px in print
- Symbols-only labels on figure: `+F_X`, `+F_Y`, `+M_XY` (yaw curved arrow)
- All three at CoG; never single resultant + angle — always decomposed into X/Y components

## Coordinate axes & heading angle
- **NOT shown as an arc on the hull**
- Cardinal numeral labels at frame edges: `0°` at stern, `180°` at bow, `90°` at starboard-beam, `270°` at port-beam
- Angle of attack `θ` (or `ψ` for heading) is defined in a **separate inset** — small cluster of parallel arrows captioned `θ — Angle of Wind or Current Attack`

## Color scheme
- Hull fill: terracotta/muted brown `#b87060`
- Lines, axes, text: dark navy `#1a2a4a`
- Alternative: all-monochrome (black/white)
- Avoid high-contrast or saturated arrow colors — OCIMF style is muted

## Labels & legend pattern
- Figure carries **symbols only** (`F_X`, `F_Y`, `M_XY`, `θ`)
- Full English mapping ("F_X = longitudinal current force on hull", etc.) goes in a **caption block BELOW the figure**
- Coefficient curve plots use small inline text-label-with-leader on each curve (not boxed legend overlay)
- For multi-curve plots, small "Legend" block at lower-right when 2+ curves coexist

## Coefficient curve plots (Annex A Figures A5-A19)
- Pure 2D Cartesian plots, no ship rendered
- x-axis `θ_C` reversed: 180° on left → 0° on right
- y-axis `C_Xw` or similar with subscripts
- Maximum 2 curves per plot
- Curve labels next to line with short leader stroke

## Concrete SVG/CSS recommendations for matching OCIMF style

```css
.ship-hull-ocimf {
  fill: #b87060;
  fill-opacity: 1;          /* or 0.6 if light-bg compromise needed */
  stroke: #1a2a4a;
  stroke-width: 0.75;
}
.ocimf-arrow {
  stroke: #1a2a4a;
  stroke-width: 1.5;
  fill: none;
  /* marker-end: small triangle ~3-4px */
}
.ocimf-label {
  font: 600 11px serif;     /* or sans-serif; small */
  fill: #1a2a4a;
}
```

## Decision rules when feedback says "arrows too bold / too crowded"
1. Drop arrow stroke from any-px to ~1.5px
2. Replace adjacent English labels with symbol set `{F_X, F_Y, M_XY, θ}` on-figure
3. Move full English mapping to caption block under each SVG
4. This is the OCIMF house style and what marine-engineering reviewers subconsciously expect

## Three canonical figure patterns to mimic
1. **Figure A1 / Sign Convention**: solid hull silhouette + 3 small arrows (+F_X, +F_Y) and curved +M_XY at CoG + cardinal degree labels at frame edges + θ inset
2. **Figure A5 (loaded tanker Cxc curve)**: pure x-y plot, no ship; θ_C reversed; inline text-label-with-leader per curve
3. **Figure 1.2 (resultant decomposition)**: ship plan view with 2 straight arrows (F_X centerline, F_Y perpendicular) + small curved yawing moment arrow — NEVER single resultant + angle

Related: [[reference-ocimf-meg4-citation-style]] for citation convention.
