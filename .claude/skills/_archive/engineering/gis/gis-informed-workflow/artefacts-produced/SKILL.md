---
name: gis-informed-workflow-artefacts-produced
description: 'Sub-skill of gis-informed-workflow: Artefacts Produced.'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# Artefacts Produced

## Artefacts Produced


| File | Format | Consumer |
|------|--------|----------|
| `route_depth_profile.csv` | CSV chainage + depth | digitalmodel |
| `metocean_site.csv` | CSV time series | digitalmodel |
| `models/environment.yml` | OrcaFlex YAML | OrcaFlex model generator |
| `wells_map.html` | Folium interactive | QA / reporting |
| `site_bathy_500m.tif` | GeoTIFF | QGIS / rasterio |
| `pipeline_route.gpkg` | GeoPackage | QGIS / GeoPandas |

---
