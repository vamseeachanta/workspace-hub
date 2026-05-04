---
name: espp-stock-sale-entry-freetaxusa
description: Workflow for entering ESPP stock sales in FreeTaxUSA with unknown acquisition dates and basis adjustments
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["tax", "espp", "stock-sales", "freetaxusa", "basis-reporting"]
---

# ESPP Stock Sale Entry in FreeTaxUSA

When entering ESPP sales with unknown acquisition dates: (1) Select "Yes" to ESPP question to trigger ESPP-specific flow; (2) Choose "No" for known acquisition date, then select "Various Dates Acquired - One Year or Less" (short-term conservative default); (3) Enter sale proceeds and date; (4) Set cost basis to $0 if no supplemental statement available and W-2 Box 14 shows $0 ESPP income; (5) Select "No" for basis reported unless Box 12 is checked on 1099-B. This preserves the full gain for reporting and avoids understating tax liability.