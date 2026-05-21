# Licensed/off-repo source resolution during issue execution

Use this reference when an approved issue was blocked by an unresolved source artifact and execution discovers the source lives outside the repo because of licensing, client confidentiality, or local-only corpus routing.

## Durable pattern

1. Treat the source discovery as strengthened resource intelligence, not implementation by itself.
2. Verify the source with deterministic evidence before updating the issue:
   - exact absolute path or controlled corpus route
   - artifact title/metadata where available
   - parser/report output count or other reproducible extraction proof
   - rendered/report artifact sanity check when the source feeds a generated explorer/report
3. Post a GitHub decision-ledger update that separates:
   - blocker resolved
   - source location and access boundary
   - generated/derived artifacts that are safe to track
   - licensed/raw artifacts that must not be committed
   - engineering interpretation limits
4. Patch the issue plan if it still says the source is unresolved.
5. Rerun focused plan review only if the source update materially changes execution scope, acceptance criteria, or validation path.
6. During implementation, fail closed if the required source/provenance/citation sidecar is missing.

## Pitfalls

- Do not commit licensed workbooks, PDFs, client files, or copied raw source tables into the repo.
- Do not overstate generic/reference data as asset-specific or client-specific coefficients.
- Do not let a generated HTML/report title be the only proof; pair it with extracted row/figure/section counts or parser evidence.
- Do not bury source-boundary decisions only in local notes; post the decision to the governing GitHub issue.

## Session example: SIROCCO OCIMF coefficients

In workspace-hub issue #2760, the unresolved `ocimf_coefficients_production.csv` blocker was resolved by finding the licensed workbook at `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx`. Safe tracked derivatives included an HTML explorer, corpus README, and parser prototype in `digitalmodel`; the raw workbook/PDFs remained off-repo. The GitHub comment recorded that the data is a generic/reference OCIMF tanker-current coefficient basis, not ship-specific SIROCCO coefficients, and that downstream calculations must fail closed if provenance/citation source is unavailable.
