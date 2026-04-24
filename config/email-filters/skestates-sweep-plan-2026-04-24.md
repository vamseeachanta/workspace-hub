# Skestates Gmail Sweep — Pre-Session Plan

**Date:** 2026-04-24
**Method:** Same as ace sweep (see `docs/sessions/2026-04-24-gmail-ace-sweep.md`)
**Account:** skestatesinc@gmail.com
**Status:** Draft — user must confirm decisions below before filter install

## Hypothesis about inbox composition

Low-volume operating LLC for Family Dollar Store #30150, 15645 Westpark (#1969, #1967). Routing-yaml SKEstates block + 25-contact CSV:

- **Tenant** — @familydollar.com (TX_Rents, leaseadministration, MFINCHAM, estoppelfd), @dollartree.com (claims, vendormaintenance)
- **Insurance** — @marsh.com, @crowninsuranceagency.net, @insureon.com
- **Title** — @independencetitle.com
- **HOA / prop mgmt** — @fsresidential.com
- **Vendors** — @phfmservices.com, @clhelt.com, @gdsincorporated.com, @partneresi.com (PCA)
- **Finance** — @firstbilling.com

All legitimate business. Per sweep checklist Part C: low-volume, noise unlikely. CRE/Industry/AutoNoise expected near-empty.

## Proposed filter set

### CRE filter
**N/A.** Operating-LLC mailbox, not a CRE tracker. CRE listings flow to ace (449 historical). Skip.

### AutoNoise filter
**Likely 0-3 domains.** Nothing flagged DELETE/REVIEW for this account. Cautious seed:

```
from:(@info.tatacapital.co.in OR @cincsystems.net)
```

`tatacapital` = cross-noise (see `feedback_email_cross_noise.md`); `cincsystems.net` = HOA-mgmt marketing. Add only if inbox scan shows hits.

### Industry filter
**N/A.** Skip.

### VIP filter — Operations
**From clause** (routing-yaml SKEstates block, all 11 domains):

```
from:(@familydollar.com OR @dollartree.com OR @marsh.com OR @independencetitle.com OR @fsresidential.com OR @phfmservices.com OR @clhelt.com OR @firstbilling.com OR @crowninsuranceagency.net OR @insureon.com OR @gdsincorporated.com OR @partneresi.com)
```

**Action:** Star + Mark important + Never to Spam + Apply to existing. Do NOT Skip Inbox — these are actionable, not archival.

### Operations label
Recommend **single `Operations` label** alongside VIP star. Per-category (Tenant/Insurance/Title/HOA/Vendor) = 5 filters for <20 msg/week — low ROI. User can split later.

## Decisions user must make before filter install

1. **Label granularity** — single `Operations` OR per-category (`Tenant`/`Insurance`/`Title`/`HOA`/`Vendor`)?
2. **VIP action scope** — Star only, OR Star + Mark Important (ace pattern), OR also route to a priority section?
3. **Noise domains** — any spam/marketing actually reaching this inbox? Confirm AutoNoise seed (tatacapital, cincsystems) or drop if no hits.
4. **S1 override-filters flip** — apply the ace lesson ("Don't override filters") here too? Recommend YES.
5. **Subdomains on familydollar/dollartree** — filter on `@familydollar.com` catches all subdomains; confirm functional inboxes (`estoppelfd@`, `LLChangeRequestfd@`, `vendormaintenance@dollartree.com`) match.
6. **1099 / tax-season flag** — separate filter for `subject:(1099 OR W-9)` from tenant domains (per #1969 reconciliation follow-up)?

## Gaps where live inbox scan is needed

- Whether noise has accumulated (low prior; routing-yaml shows none today)
- New senders outside the 11 routing-yaml domains (new vendors, new tenant contacts, attorney, CPA)
- Unread baseline (starting # — success metric)
- Whether the 1099 discrepancy thread (#1969) has live follow-up

## Estimated time savings

Lower than achantav and ace because volume is low and filter set is simple. With decisions pre-confirmed and VIP domain list already in routing-yaml, browser work ≈ **10-15 min**. Most of that is "Apply to existing conversations" runtime for the Operations filter.
