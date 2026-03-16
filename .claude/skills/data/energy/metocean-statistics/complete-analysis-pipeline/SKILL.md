---
name: metocean-statistics-complete-analysis-pipeline
description: 'Sub-skill of metocean-statistics: Complete Analysis Pipeline (+5).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Complete Analysis Pipeline (+5)

## Complete Analysis Pipeline


```python
import pandas as pd
import numpy as np
from scipy import stats
from datetime import date

async def run_extreme_analysis(station_id: str, start_year: int, end_year: int):
    """Complete extreme value analysis workflow."""

    # Import metocean module components

*See sub-skills for full details.*

## Monthly Statistics Calculation


```python
def calculate_monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate comprehensive monthly statistics for metocean parameters."""

    # Ensure datetime index
    df = df.copy()
    df['month'] = pd.to_datetime(df['observation_time']).dt.month

    # Define aggregation functions
    agg_funcs = {

*See sub-skills for full details.*

## Seasonal Statistics


```python
def calculate_seasonal_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate seasonal statistics for metocean parameters."""

    df = df.copy()
    df['time'] = pd.to_datetime(df['observation_time'])
    df['month'] = df['time'].dt.month

    # Define seasons
    season_map = {12: 'Winter', 1: 'Winter', 2: 'Winter',

*See sub-skills for full details.*

## Directional Analysis


```python
def calculate_directional_stats(
    df: pd.DataFrame,
    speed_col: str = 'wave_height_m',
    dir_col: str = 'wave_direction_deg',
    sectors: int = 16
) -> dict:
    """Calculate statistics by directional sector."""

    df = df.copy()

*See sub-skills for full details.*

## Joint Probability Distribution


```python
def calculate_joint_distribution(
    df: pd.DataFrame,
    var1: str = 'wave_height_m',
    var2: str = 'wave_period_s',
    bins1: int = 20,
    bins2: int = 20
) -> pd.DataFrame:
    """Calculate Hs-Tp joint distribution (scatter diagram)."""


*See sub-skills for full details.*

## Exceedance Duration Analysis


```python
def calculate_exceedance_duration(
    df: pd.DataFrame,
    parameter: str = 'wave_height_m',
    threshold: float = 2.5,
    time_col: str = 'observation_time'
) -> dict:
    """Calculate exceedance duration statistics."""

    df = df.copy()

*See sub-skills for full details.*
