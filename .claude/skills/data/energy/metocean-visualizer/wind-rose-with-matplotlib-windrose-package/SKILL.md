---
name: metocean-visualizer-wind-rose-with-matplotlib-windrose-package
description: 'Sub-skill of metocean-visualizer: Wind Rose with Matplotlib (windrose
  package).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Wind Rose with Matplotlib (windrose package)

## Wind Rose with Matplotlib (windrose package)


```python
from windrose import WindroseAxes
import matplotlib.pyplot as plt
import numpy as np


def plot_wind_rose_matplotlib(
    speeds: np.ndarray,
    directions: np.ndarray,
    output_path: Optional[str] = None,
    title: str = 'Wind Rose'
) -> plt.Figure:
    """Create wind rose diagram using windrose package."""
    fig = plt.figure(figsize=(10, 10))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(
        directions, speeds,
        normed=True, opening=0.8,
        bins=np.arange(0, 25, 5),
        cmap=plt.cm.viridis
    )
    ax.set_legend(title='Speed (m/s)')
    ax.set_title(title)

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
    return fig
```
