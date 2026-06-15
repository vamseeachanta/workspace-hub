---
name: crossprovider codex public-database-service-endpoint-discovery-patte
description: Public database service endpoint discovery pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [reconnaissance, web-api, database-probing]
---

ABS-style search services expose JSON endpoints (`/services/V1/...`) that respond to blank/minimal queries with result counts and detail pages. Services include export controls (CSV/PDF) in the browser UI, not always in the API. Test unauthenticated access with payload `{}` or `facilityId=0` to classify exportability before attempting large-scale collection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
