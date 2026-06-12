---
name: crossprovider gemini qgis-csv-point-import-via-delimitedtext-driver-w
description: QGIS CSV point import via delimitedtext driver with field-based geometry
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [qgis, geospatial, data-import]
---

URI pattern `file://path.csv?delimiter=,&xField=longitude&yField=latitude&crs=EPSG:4326` loads CSV as point layer without manual iteration. QGIS infers geometry from field names; order-independent. Rapid well-location plotting from field CSV.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
