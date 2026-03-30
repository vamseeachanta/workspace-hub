---
name: marine-offshore-engineering-5-regulatory-framework
description: 'Sub-skill of marine-offshore-engineering: 5. Regulatory Framework (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 5. Regulatory Framework (+1)

## 5. Regulatory Framework


**Classification Societies:**
- **DNV** (Det Norske Veritas) - Norwegian
- **ABS** (American Bureau of Shipping) - American
- **Lloyd's Register** - British
- **Bureau Veritas** - French

**Key Standards:**
```yaml
standards:
  structural:
    - DNV-OS-C101: Design of Offshore Steel Structures
    - API RP 2A-WSD: Fixed Offshore Platforms
    - ISO 19902: Fixed Steel Structures

  floating:
    - DNV-OS-C103: Floating Structures
    - API RP 2FPS: Planning, Designing, Constructing Floating Production Systems

  mooring:
    - DNV-OS-E301: Position Mooring
    - API RP 2SK: Stationkeeping Systems
    - ISO 19901-7: Stationkeeping Systems

  subsea:
    - API 17D: Subsea Wellhead and Christmas Tree Equipment
    - API 17J: Unbonded Flexible Pipe
    - DNV-OS-F101: Submarine Pipeline Systems

  operations:
    - DNV-RP-H103: Modelling and Analysis of Marine Operations
    - ISO 19901-6: Marine Operations
```


## 6. Marine Operations


**Installation Methods:**
- **Heavy Lift** - Crane vessels for topsides
- **Float-over** - Deck floated over substructure
- **Pipelaying** - S-lay, J-lay, reel-lay methods

**Weather Windows:**
```python
def calculate_weather_window(
    sea_states: list,
    operation_limit: dict,
    duration_required: float  # hours
) -> list:
    """
    Identify suitable weather windows for marine operations.

    Args:
        sea_states: List of sea state forecasts
        operation_limit: Limits (Hs_max, Tp_range, current_max)
        duration_required: Required continuous calm period

    Returns:
        List of suitable time windows
    """
    windows = []
    current_window_start = None
    current_window_duration = 0

    for i, state in enumerate(sea_states):
        # Check if conditions are suitable
        suitable = (
            state['Hs'] <= operation_limit['Hs_max'] and
            state['current'] <= operation_limit['current_max']
        )

        if suitable:
            if current_window_start is None:
                current_window_start = i
            current_window_duration += state['time_step']

            # Check if window is long enough
            if current_window_duration >= duration_required:
                windows.append({
                    'start': current_window_start,
                    'duration': current_window_duration,
                    'conditions': 'suitable'
                })
        else:
            # Window ended
            current_window_start = None
            current_window_duration = 0

    return windows
```
