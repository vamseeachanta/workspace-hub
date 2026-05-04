---
name: signal-analysis-signal-quality
description: 'Sub-skill of signal-analysis: Signal Quality (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Signal Quality (+2)

## Signal Quality


1. **Check sampling rate** - Ensure Nyquist criterion for frequencies of interest
2. **Remove transients** - Skip build-up periods in OrcaFlex simulations
3. **Validate stationarity** - Use multiple segments for PSD estimation
4. **Handle gaps** - Interpolate or segment around missing data


## Rainflow Analysis


1. **Hysteresis filtering** - Remove small cycles (typically < 1-5% of range)
2. **Residual handling** - Choose appropriate method for incomplete cycles
3. **Cycle binning** - Use consistent bin sizes for histogram comparison
4. **S-N curve matching** - Ensure stress units match S-N curve units


## Performance Optimization


1. **Parallel processing** - Use batch extraction for multiple files
2. **Memory management** - Process long signals in chunks
3. **Downsampling** - Reduce sampling rate if high frequencies not needed
4. **Result caching** - Store intermediate results for reprocessing
