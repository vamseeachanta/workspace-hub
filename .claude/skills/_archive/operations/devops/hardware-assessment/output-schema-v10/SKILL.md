---
name: hardware-assessment-output-schema-v10
description: 'Sub-skill of hardware-assessment: Output Schema (v1.0).'
version: 1.1.0
category: operations
type: reference
scripts_exempt: true
---

# Output Schema (v1.0)

## Output Schema (v1.0)


Both scripts produce identical JSON structure:

```json
{
  "schema_version": "1.0",
  "script_version": "1.0.0",
  "platform": "linux|windows",
  "timestamp": "ISO-8601",
  "cpu": {
    "model": "Intel Xeon E5-2630 v3 @ 2.40GHz",
    "architecture": "x86_64",
    "sockets": 2,
    "cores_per_socket": 8,
    "total_cores": 16,
    "threads_per_core": 2,
    "total_threads": 32,
    "max_mhz": "3200.0000",
    "l3_cache": "40 MiB"
  },
  "memory": {
    "total_kb": 32810676,
    "total_gb": "31.3",
    "type": "DDR4",
    "speed": "2133 MT/s"
  },

*See sub-skills for full details.*
