---
name: crossprovider hermes contact-csv-data-quality-email-as-name-wrapping-
description: Contact CSV data quality: email-as-name wrapping, duplicates, spam domains need normalization
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-quality, contact-management]
---

Outlook-export CSVs (64 columns) frequently have email addresses in First Name field (angle-bracket wrapped, e.g. '<email@domain.com>'). aceengineer_contacts: 1,295 rows, 30% missing names, 7 spam entries. achantav_contacts: 1,140 rows, 36% missing names, 13 spam entries including craigslist.org. Cross-file: 132 email duplicates. Normalize via character stripping + spam domain purge before bulk operations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
