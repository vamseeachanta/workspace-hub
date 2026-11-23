# Static / Geo-Modeling — 11 Common Mistakes

- **Source:** Lindsay Campillo (LinkedIn post)
- **URL:** https://www.linkedin.com/posts/lindsaygcampillo_geomodeling-reservoirmodeling-geology-ugcPost-7473821859873177600-2acH/
- **Domain:** reservoir / static (geo) modeling — relevant to BSEE reservoir analysis, worldenergydata
- **Captured:** 2026-06-22
- **Type:** practitioner methodology (named-author commentary, not a vendor standard)

## Core thesis

Most simulation problems originate in **static-modeling decisions**, not software limitations.
A good static model is **not the most complex one** — it is one that adequately represents the
geology while answering the business objective.

> "Workflows are reusable. Solutions are not."

## The 11 mistakes (and the corrective)

1. **Template solutions.** Each reservoir needs a unique approach. Reuse the *workflow*, not the *solution*.
2. **Ignoring data quality.** Wrong coordinates and inconsistent logs undermine the whole project. QC inputs first.
3. **Grid-first over geology-first.** Design the grid to accommodate the geological understanding — not the reverse.
4. **Unsupported faults.** Include only faults with genuine geological or seismic support.
5. **Conflating facies with flow units.** Facies describe geology; flow behavior depends on petrophysical properties.
6. **Skipping rock typing.** The same facies can behave differently during production.
7. **Single porosity–permeability correlation.** Apply *different* poro-perm relationships across depositional environments.
8. **Over-gridding.** Excessive cells add complexity without improving accuracy.
9. **Interpolation-only saturation.** Honor fluid contacts and capillary pressure — use physics, not just interpolation.
10. **No volume validation.** Calculated volumes must reconcile with geological understanding.
11. **Complexity for its own sake.** Build purpose-driven models that support development decisions and reserves estimation.

## Why it matters here

Directly applicable to the BSEE full-database reservoir work (field/well volumetrics, OGOR-A
production) and any digitalmodel reservoir tooling: the volume-validation (#10) and
geology-first (#3) points are the cheapest guards against headline-number errors.
