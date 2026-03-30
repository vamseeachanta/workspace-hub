---
name: oil-and-gas-core-libraries
description: 'Sub-skill of oil-and-gas: Core Libraries (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Core Libraries (+1)

## Core Libraries


```python
import pandas as pd
import numpy as np
import scipy.optimize

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

import lasio      # LAS file reading
import welly      # Well log analysis
import striplog   # Lithology and stratigraphy
```

## worldenergydata Custom Modules


```python
from worldenergydata.decline_curves import arps_decline
from worldenergydata.pvt import standing_correlation
from worldenergydata.material_balance import tank_model
from worldenergydata.economics import npv_analysis
```
