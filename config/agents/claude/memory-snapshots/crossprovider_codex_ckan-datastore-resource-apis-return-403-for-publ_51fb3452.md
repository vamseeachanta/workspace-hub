---
name: crossprovider codex ckan-datastore-resource-apis-return-403-for-publ
description: CKAN datastore resource APIs return 403 for 'public' packages
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ckan, public-data, access-control]
---

UK data.gov.uk CKAN's `resource_show`, `datastore_search`, and related endpoints return 403 Forbidden even for packages marked public. This blocks common assumptions that CKAN metadata APIs are credential-free. Workaround: check HTML previews or external download links, or confirm access directly with the data provider.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
