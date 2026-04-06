---
name: contact-manager
description: Normalize, classify, and manage contact databases across 3 Gmail accounts. Clean CSV exports, deduplicate, tag categories, flag touchbase/unsubscribe candidates.
version: 1.0.0
author: vamsee
tags: [email, contacts, CRM, classification, data-cleanup]
related_skills: [gmail-multi-account, gmail-triage, gmail-touchbase, gmail-unsubscribe]
metadata:
  hermes:
    tags: [email, contacts, CRM, classification]
    related_skills: [gmail-multi-account]
---

# Contact Manager

Normalize and classify contact databases for multi-account Gmail management.

## Contact Sources

| Account | Source Path | Format | Entries |
|---|---|---|---|
| ace | aceengineer-admin/admin/contacts/aceengineer_contacts.csv | Outlook CSV export | ~1,306 |
| personal | aceengineer-admin/admin/contacts/achantav_contacts.csv | Outlook CSV export | ~1,157 |
| skestates | sabithaandkrishnaestates/admin/contacts/ | Manual (from key_contacts.md) | ~20 |

## Normalization Steps

### Step 1: Parse and clean CSV

Known issues in the raw CSVs:
- Email addresses wrapped in angle brackets: `<email@domain.com>`
- Empty name fields with only email
- Duplicate entries (same person, multiple rows)
- Craigslist/spam entries mixed in
- Malformed CSV escaping (quotes inside fields)

### Step 2: Create normalized schema

Output format (per account): `contacts_normalized.csv`

```csv
email,first_name,last_name,company,category,touchbase_cadence,notes
```

### Step 3: Category classification

Categories:
- `vip` — high-value, always-respond contacts
- `client` — current or past clients
- `prospect` — GTM pipeline targets
- `colleague` — current/former colleagues
- `vendor` — service providers, suppliers
- `recruiter` — staffing, job-related
- `personal` — friends, family
- `newsletter` — subscriptions, marketing lists
- `spam` — junk, craigslist, unknown bulk
- `government` — tax, legal, regulatory
- `financial` — banks, insurance, investment

Classification heuristics:
1. Domain-based: @ril.com, @dorisgroup.com, @mcdermott.com → client/colleague
2. Name-based: known family names (achanta*) → personal
3. Pattern-based: craigslist, @sale., unsubscribe → spam
4. Role-based: "Accounts Payable", "HR" in name → vendor/colleague
5. Manual override: VIP list maintained by user

### Step 4: Deduplication

Rules:
- Same email → merge (keep most complete record)
- Same name, different email → keep both, flag for review
- No name, only email → keep but mark as "incomplete"

## Scripts

### Contact normalizer (run with uv)
```bash
uv run scripts/email/contact-normalizer.py \
  --input aceengineer-admin/admin/contacts/aceengineer_contacts.csv \
  --output aceengineer-admin/admin/contacts/aceengineer_normalized.csv \
  --account ace
```

### Contact classifier
```bash
uv run scripts/email/contact-classifier.py \
  --input aceengineer-admin/admin/contacts/aceengineer_normalized.csv \
  --output aceengineer-admin/admin/contacts/aceengineer_classified.csv
```

### SKEstates contact builder
```bash
uv run scripts/email/skestates-contact-builder.py \
  --key-contacts sabithaandkrishnaestates/investments/cre/fd_15645_westpark/due_diligence/key_contacts.md \
  --maintenance sabithaandkrishnaestates/investments/cre/fd_15645_westpark/maintenance/fd_corporate_contact_maintenance.md \
  --output sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv
```

## File Locations (post-normalization)

| Account | Normalized CSV | Classified CSV |
|---|---|---|
| ace | aceengineer-admin/admin/contacts/aceengineer_normalized.csv | aceengineer-admin/admin/contacts/aceengineer_classified.csv |
| personal | aceengineer-admin/admin/contacts/achantav_normalized.csv | aceengineer-admin/admin/contacts/achantav_classified.csv |
| skestates | sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv | (small enough to classify manually) |

## Pitfalls

1. Raw CSVs have Outlook export quirks — angle brackets, BOM, Windows line endings
2. Some entries have email in the "First Name" field (malformed export)
3. Don't delete raw CSVs — keep originals, create normalized copies alongside
4. Legal: contact data is PII — never commit to public repos, .gitignore if needed
5. The personal CSV has craigslist/talkmatch spam entries — auto-classify as spam
6. Company field often empty — try to infer from email domain
