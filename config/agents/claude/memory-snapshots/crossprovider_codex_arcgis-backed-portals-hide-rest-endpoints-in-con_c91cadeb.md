---
name: crossprovider codex arcgis-backed-portals-hide-rest-endpoints-in-con
description: ArcGIS-backed portals hide REST endpoints in config files, not web UI
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [geospatial-data, api-discovery, portal-assessment]
---

Many government GIS portals expose queryable REST/GeoJSON endpoints and feature granularity (per-well, per-field, per-licence) in configuration files (`config.xml`) or ArcGIS REST service roots, not advertised on the landing page. Inspect app bundle/client config to discover true capabilities before concluding a source is aggregate-only or portal-gated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
