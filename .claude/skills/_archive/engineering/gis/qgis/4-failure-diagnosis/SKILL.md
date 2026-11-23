---
name: qgis-4-failure-diagnosis
description: 'Sub-skill of qgis: 4. FAILURE DIAGNOSIS.'
version: 1.0.0
category: engineering/gis
type: reference
scripts_exempt: true
---

# 4. FAILURE DIAGNOSIS

## 4. FAILURE DIAGNOSIS


| Error | Cause | Fix |
|-------|-------|-----|
| `Layer is not valid` | Wrong path, unsupported driver, malformed file | Check path; verify with `ogrinfo`; inspect CRS |
| `QgsApplication not initialized` | Missing `initQgis()` call | Call `qgs.initQgis()` before any QGIS operation |
| `QGIS prefix path not set` | Missing env setup | Set `QgsApplication.setPrefixPath("/usr", True)` or use default |
| `No module named 'qgis'` | QGIS Python not on PYTHONPATH | Run inside QGIS Python console or set `PYTHONPATH` |
| `CRS is not valid / unknown` | EPSG code not found | Use `QgsCoordinateReferenceSystem.fromEpsgId(4326)` |
| Processing `OUTPUT is None` | Algorithm failed silently | Check `feedback.pushWarning()` output; validate inputs |
| `offscreen` platform error | Qt platform missing | Install `libqt5gui5`; set `QT_QPA_PLATFORM=offscreen` |
| Shapefile truncated field names | Shapefile 10-char limit | Export to GeoPackage instead |

---
