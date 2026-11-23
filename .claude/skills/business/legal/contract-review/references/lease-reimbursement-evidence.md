# Lease reimbursement evidence pattern

Use this reference when a user asks whether a lease supports billing/reimbursement of taxes, HOA/POA, CAM, insurance, maintenance, or other pass-through charges.

## Workflow

1. Establish the primary lease document and metadata: document title, lease date, parties, property, and section number/title.
2. Extract/search the full lease text, preferably preserving page/line references. For PDFs, use `pdftotext -layout` first; OCR only if extraction is incomplete.
3. When the user needs to send or visually verify the clause, export only the cover page and operative clause page from the PDF. Example: `pdftoppm -f 12 -l 12 -png -singlefile lease.pdf /tmp/lease_page_12`; this avoids wrestling with browser PDF viewers and gives a clean image for confirmation.
4. Search for exact and umbrella terms:
   - exact: HOA, POA, homeowners, association, assessment, CAM, insurance, reimbursement
   - umbrella: taxes, assessments, charges, Real Estate Taxes, common area, evidence of payment, invoice, caps, partial year, due date, penalty, interest
4. Quote only operative language needed for the counterparty, plus conditions/deadlines. Do not over-explain legal conclusions.
5. Distinguish recurring charges from one-time fees:
   - Annual/recurring assessment language normally supports annual assessment reimbursement.
   - One-time transfer/admin/setup fees require separate lease support; flag as uncertain if not expressly included.
6. Draft a send-ready note with:
   - document name and date
   - section number/title
   - quoted controlling language
   - invoice/payment evidence to attach
   - reimbursement amount requested and any excluded/held-back amounts

## Example: Family Dollar HOA reimbursement

Facts found in a SKE Estates review:

- Document: `FD Westpark Dr Lease.pdf`
- Lease date: May 14, 2012
- Parties: Clodine West Park Riverside Development, LLC (Landlord) and Family Dollar Stores of Texas, LLC (Tenant)
- Property: 15645 Westpark Drive / Westpark & Addicks Clodine, Houston, TX
- Controlling section: Section 13 — TAXES

Operative language:

> "Landlord will timely pay all taxes, assessments and other charges that may be levied, assessed or charged against the Demised Premises (including the annual homeowners' association fees as set forth below) ('Real Estate Taxes')..."

> "Provided that the Demised Premises are a separately assessed tax parcel, then beginning on the rent commencement date, Tenant will reimburse Landlord for Real Estate Taxes — (including annual homeowners' association fees) on the Demised Premises within 90 days of receipt of invoice and evidence of payment."

> "For the first year after Tenant opens for business, Tenant's reimbursement of the annual homeowners' association fees to Landlord will not exceed $475.00..."

> "Landlord will provide Tenant with a copy of the Real Estate Tax bill, including a statement showing the annual homeowners' association fees, with evidence of Landlord's payment..."

> "In no event will Tenant be responsible for reimbursing Landlord for any Real Estate Taxes or annual homeowners' association fees unless Tenant has received a copy of the tax bill and homeowners' association statement with evidence of payment and a written request for reimbursement from Landlord within 180 days after the last day the taxes were due without penalty or interest."

Conclusion pattern: annual HOA/POA assessment is reimbursable if documentation and timing conditions are met. A one-time transfer fee should be excluded or separately flagged unless the lease contains broader language clearly covering it.
