# Member/package travel deal verification

Use this reference when the user asks to explore or price Costco Travel, member-only travel portals, guided-vacation packages, or package deals where public search snippets are incomplete.

## Trigger

- User asks to compare package deals, Costco Travel offers, guided vacations, or bundled hotel/resort/vacation products.
- The task is exploration/pricing, not a fully drafted single-trip itinerary.

## Workflow

1. **Start from the comparison issue tree.** Create or reuse a parent comparison issue and one child issue per serious option when multiple packages/destinations are in play. Keep vendor access confidence explicit.
2. **Use live member-session evidence for pricing.** Search snippets can identify leads, but package name, dates, price, inclusions, shop-card/credit amount, and cancellation/payment constraints must come from the live booking page or a quote.
3. **Distinguish package types.** Hotel/resort packages may have online date-driven pricing; guided-vacation/tour pages may be brochure-style and route to phone quote. Do not generalize one page's behavior to all Costco Travel inventory.
4. **If the page is phone-quote only, record that as the booking state.** Capture the visible CTA/phone number, valid travel season/date range, package ID if shown, included/excluded items, and which facts remain unknown until quote.
5. **Separate included land package from airfare.** Many guided vacations list lodging/meals/activities/internal transport but exclude optional add-ons or flights to/from the destination. State this explicitly before comparing to self-built trips.
6. **Preserve deal math as provisional until checkout/quote.** Digital shop cards, executive rewards, taxes, insurance, add-ons, and airfare may be calculated later. Use “quote required” or “all-in unverified,” not “total cost,” unless the payable amount is visible.
7. **When browser automation is partial, use a normal logged-in browser session if available.** If the accessible page text or copied UI is the only reliable evidence, quote only what was actually visible and avoid negative claims that the site/tool is categorically unusable.

## Evidence fields to capture in issues

```markdown
| Field | Evidence |
|---|---|
| Vendor/package | <name + URL> |
| Dates/season | <visible date range or selected dates> |
| Nights | <visible nights> |
| Online price status | priced online / phone quote / unavailable |
| Phone/CTA | <number or booking action if visible> |
| Included | lodging, meals, activities, internal transport, transfers, fees |
| Excluded/unknown | airfare, insurance, optional add-ons, taxes/fees, cancellation terms |
| Deal credit | shop card / rewards / promo, with calculation status |
| Booking confidence | verified online / quote required / lead only |
```

## Costco Travel guided-vacation example

A Costco Travel Adventures by Disney Peru page showed a live logged-in page with package name, 7-night Spring/Summer/Fall 2026 availability, included lodging/meals/activities/internal airfare when applicable, package ID, and `1-866-921-7925` as the Check Price & Availability outcome. It did not expose an online price in that UI path, so the correct issue state was “phone quote required; all-in price unverified,” not “no deal” or a fabricated package total.
