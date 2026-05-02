<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcaWave/Content/APIOverview.htm -->

# OrcaWave API

The OrcaWave API allows scripted control of OrcaWave analyses.

## Loading a Model

```
import OrcaWaveAPI
model = OrcaWaveAPI.Model('vessel.dat')
model.Run()
```

## Accessing Results

RAOs are accessed via the [RAO result object](APIReference.htm).

```
rao = model.GetRAO('Surge', heading=0.0)
amplitudes = rao.Amplitude
periods = rao.Period
```

### Exporting to OrcaFlex

Use the [export method](ExportMethod.htm) to write OrcaFlex-compatible files:

```
model.ExportToOrcaFlex('vessel_rao.yml')
```
