---
name: orcaflex-vessel-setup-1-fpso-with-aqwa-hydrodynamics
description: 'Sub-skill of orcaflex-vessel-setup: 1. FPSO with AQWA Hydrodynamics
  (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. FPSO with AQWA Hydrodynamics (+2)

## 1. FPSO with AQWA Hydrodynamics


```python
# Import FPSO hydrodynamics from AQWA
vessel_type = import_vessel_from_aqwa(
    model=model,
    aqwa_file="fpso_aqwa.lis",
    vessel_name="FPSO_Type",
    import_config={
        "displacement_raos": True,
        "load_raos": True,
        "qtfs": True,

*See sub-skills for full details.*

## 2. Shuttle Tanker Approach


```python
# Shuttle tanker at offset position
vessel = model.CreateObject(OrcFxAPI.otVessel, "Shuttle_Tanker")
vessel.VesselType = "Shuttle_Type"
vessel.InitialPosition = [80, 0, 0]  # 80m offset from FPSO
vessel.InitialHeading = 180  # Stern-to-stern
```

## 3. Barge for Installation


```python
# Installation barge
vessel = model.CreateObject(OrcFxAPI.otVessel, "Installation_Barge")
vessel.VesselType = "Barge_Type"
vessel.PrimaryMotion = OrcFxAPI.vmPrescribed  # Follow prescribed motion
```
