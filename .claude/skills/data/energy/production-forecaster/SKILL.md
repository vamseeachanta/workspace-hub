---
name: production-forecaster
description: Forecast oil & gas well production using decline curve analysis. Use for EUR estimation, type curve generation, production modeling, and reserve calculations with Arps decline models (exponential, hyperbolic, harmonic).
<<<<<<< HEAD
version: 2.0.0
last_updated: 2026-01-18
=======
version: 1.0.0
last_updated: 2025-12-30
>>>>>>> origin/main
capabilities: []
requires: []
see_also: []
---

# Production Forecaster

Forecast oil and gas production using industry-standard decline curve analysis methods. Supports Arps decline models, type curve generation, and EUR (Estimated Ultimate Recovery) calculations for reserve estimation.

## When to Use

- Forecasting future production for oil and gas wells
- Estimating EUR (Estimated Ultimate Recovery)
- Generating type curves for field development planning
- Fitting decline parameters to historical production data
- Comparing well performance across different fields
- Supporting reserve booking and economic evaluation
- Analyzing production trends and anomalies

## Core Pattern

```
Historical Production → Decline Curve Fit → Parameter Estimation → Forecast → EUR
```

## Decline Curve Models

### Arps Decline Equations

**Exponential Decline (b = 0):**
```
q(t) = qi * exp(-Di * t)
```

**Hyperbolic Decline (0 < b < 1):**
```
q(t) = qi / (1 + b * Di * t)^(1/b)
```

**Harmonic Decline (b = 1):**
```
q(t) = qi / (1 + Di * t)
```

Where:
- `q(t)` = Production rate at time t
- `qi` = Initial production rate
- `Di` = Initial decline rate
- `b` = Decline exponent (b-factor)
- `t` = Time

<<<<<<< HEAD
### Modified Hyperbolic Decline

For long-term forecasts, use terminal decline rate to prevent over-optimistic recoveries:

```
q(t) = qi / (1 + b * Di * t)^(1/b)     when D(t) > D_min
q(t) = q_switch * exp(-D_min * t')     when D(t) <= D_min
```

Where `D_min` is the terminal decline rate (typically 5-8%/year) and `t'` is time from switch point.

### Duong Decline Model (Unconventional)

For unconventional wells with transient linear flow:

```
q(t) = q1 * t^(-m) * exp(-a/(1-m) * (t^(1-m) - 1))
```

Where:
- `q1` = Rate at t=1 day
- `a` = Intercept (controls EUR)
- `m` = Slope (controls decline steepness)

### Stretched Exponential Decline

Alternative for unconventional with varying flow regimes:

```
q(t) = qi * exp(-(t/τ)^n)
```

Where:
- `τ` = Characteristic time constant
- `n` = Stretch parameter (0 < n < 1)

## Type Curve Analysis Framework

### Normalization Methods

| Method | Description | Best For |
|--------|-------------|----------|
| `peak` | Normalize to peak rate | Wells with clear IP |
| `first_month` | Normalize to first month average | Consistent start-up |
| `30_day_ip` | Average of first 30 days | Standard IP definition |
| `90_day_ip` | Average of first 90 days | More stable baseline |
| `moving_average` | Rolling 30-day average | Noisy production data |
| `cumulative_at_time` | Cum at specific time | Reserve comparisons |

### Type Curve Bins

Group wells for representative type curves:

| Bin Type | Common Groupings |
|----------|------------------|
| Formation | Wilcox, Miocene, Lower Tertiary |
| Completion | Subsea, TLP, Spar, Floater |
| Water Depth | Shallow (<1000ft), Deep (1000-5000ft), Ultra-deep (>5000ft) |
| Lateral Length | Short (<5000ft), Medium, Long (>8000ft) |
| Proppant Loading | Low, Medium, High intensity |
| Vintage | By year of first production |

### Type Curve Confidence Intervals

| Percentile | Description | Use Case |
|------------|-------------|----------|
| P10 | 90% probability of exceedance | Optimistic / Upside |
| P50 | 50% probability (median) | Most likely case |
| P90 | 10% probability of exceedance | Conservative / Downside |

=======
>>>>>>> origin/main
## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Tuple
from enum import Enum
import numpy as np
import pandas as pd

class DeclineType(Enum):
<<<<<<< HEAD
    """Decline curve types."""
    EXPONENTIAL = "exponential"       # b = 0
    HYPERBOLIC = "hyperbolic"         # 0 < b < 1
    HARMONIC = "harmonic"             # b = 1
    MODIFIED_HYPERBOLIC = "modified"  # Hyperbolic with terminal decline
    DUONG = "duong"                   # Unconventional transient
    STRETCHED_EXP = "stretched"       # Stretched exponential

class NormalizationMethod(Enum):
    """Type curve normalization methods."""
    PEAK = "peak"
    FIRST_MONTH = "first_month"
    IP_30 = "30_day_ip"
    IP_90 = "90_day_ip"
    MOVING_AVG = "moving_average"
    CUMULATIVE = "cumulative_at_time"

class TypeCurveBinType(Enum):
    """Type curve binning categories."""
    FORMATION = "formation"
    COMPLETION = "completion"
    WATER_DEPTH = "water_depth"
    LATERAL_LENGTH = "lateral_length"
    PROPPANT = "proppant"
    VINTAGE = "vintage"
=======
    """Arps decline curve types."""
    EXPONENTIAL = "exponential"  # b = 0
    HYPERBOLIC = "hyperbolic"    # 0 < b < 1
    HARMONIC = "harmonic"        # b = 1
>>>>>>> origin/main

class ProductionPhase(Enum):
    """Well production phases."""
    BUILDUP = "buildup"
    PLATEAU = "plateau"
    DECLINE = "decline"
    ABANDONMENT = "abandonment"

@dataclass
class DeclineParameters:
    """Decline curve parameters."""
    qi: float  # Initial rate (bbls/day or mcf/day)
    di: float  # Initial decline rate (fraction/year)
    b: float   # Decline exponent
    decline_type: DeclineType = DeclineType.HYPERBOLIC

    # Optional constraints
    min_rate: float = 0.0  # Economic limit
    max_time: float = 50.0  # Years
    d_min: Optional[float] = None  # Terminal decline rate

<<<<<<< HEAD
    # Duong model parameters (unconventional)
    a: Optional[float] = None  # Duong intercept
    m: Optional[float] = None  # Duong slope

    # Stretched exponential parameters
    tau: Optional[float] = None  # Time constant
    n: Optional[float] = None    # Stretch parameter

    def __post_init__(self):
        """Validate parameters and set decline type."""
        if self.a is not None and self.m is not None:
            self.decline_type = DeclineType.DUONG
        elif self.tau is not None and self.n is not None:
            self.decline_type = DeclineType.STRETCHED_EXP
        elif self.d_min is not None and self.b > 0:
            self.decline_type = DeclineType.MODIFIED_HYPERBOLIC
        elif self.b == 0:
=======
    def __post_init__(self):
        """Validate parameters and set decline type."""
        if self.b == 0:
>>>>>>> origin/main
            self.decline_type = DeclineType.EXPONENTIAL
        elif self.b == 1:
            self.decline_type = DeclineType.HARMONIC
        else:
            self.decline_type = DeclineType.HYPERBOLIC

@dataclass
<<<<<<< HEAD
class TypeCurveBin:
    """Type curve bin definition for well grouping."""
    bin_type: TypeCurveBinType
    bin_name: str
    criteria: Dict[str, Any] = field(default_factory=dict)
    wells: List[str] = field(default_factory=list)

    def matches(self, well_metadata: Dict[str, Any]) -> bool:
        """Check if well matches bin criteria."""
        for key, value in self.criteria.items():
            if key not in well_metadata:
                return False
            well_value = well_metadata[key]
            if isinstance(value, tuple):
                # Range check (min, max)
                if not (value[0] <= well_value <= value[1]):
                    return False
            elif isinstance(value, list):
                # In list check
                if well_value not in value:
                    return False
            else:
                # Exact match
                if well_value != value:
                    return False
        return True

@dataclass
class TypeCurveResult:
    """Type curve analysis results."""
    months: List[int]
    p10_rates: List[float]
    p50_rates: List[float]
    p90_rates: List[float]
    mean_rates: List[float]
    well_counts: List[int]

    # Fitted parameters for each percentile
    p10_params: Optional[DeclineParameters] = None
    p50_params: Optional[DeclineParameters] = None
    p90_params: Optional[DeclineParameters] = None

    # Validation metrics
    r_squared: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None

    # EUR estimates
    eur_p10: Optional[float] = None
    eur_p50: Optional[float] = None
    eur_p90: Optional[float] = None

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame."""
        return pd.DataFrame({
            'month': self.months,
            'P10': self.p10_rates,
            'P50': self.p50_rates,
            'P90': self.p90_rates,
            'mean': self.mean_rates,
            'well_count': self.well_counts
        })

@dataclass
=======
>>>>>>> origin/main
class ProductionRecord:
    """Single production record."""
    date: date
    oil_rate: float = 0.0      # bbls/day
    gas_rate: float = 0.0      # mcf/day
    water_rate: float = 0.0    # bbls/day
    days_on: int = 30          # Days producing

    @property
    def oil_volume(self) -> float:
        """Monthly oil volume in barrels."""
        return self.oil_rate * self.days_on

    @property
    def gas_volume(self) -> float:
        """Monthly gas volume in mcf."""
        return self.gas_rate * self.days_on

    @property
    def gor(self) -> float:
        """Gas-oil ratio (mcf/bbl)."""
        if self.oil_rate > 0:
            return self.gas_rate / self.oil_rate
        return 0.0

@dataclass
class ForecastResult:
    """Production forecast results."""
    dates: List[date]
    oil_rates: List[float]
    gas_rates: List[float]
    cumulative_oil: List[float]
    cumulative_gas: List[float]

    # Decline parameters used
    parameters: DeclineParameters

    # Key metrics
    eur_oil: float = 0.0       # Estimated Ultimate Recovery (bbls)
    eur_gas: float = 0.0       # EUR gas (mcf)
    remaining_oil: float = 0.0  # Remaining reserves
    remaining_gas: float = 0.0

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame."""
        return pd.DataFrame({
            'date': self.dates,
            'oil_rate': self.oil_rates,
            'gas_rate': self.gas_rates,
            'cumulative_oil': self.cumulative_oil,
            'cumulative_gas': self.cumulative_gas
        })
```

### Decline Curve Analyzer

```python
import numpy as np
from scipy.optimize import curve_fit, minimize
from typing import Tuple, Optional
import pandas as pd

class DeclineCurveAnalyzer:
    """
    Analyze and fit decline curves to production data.
    """

    def __init__(self, production_data: pd.DataFrame):
        """
        Initialize with production data.

        Args:
            production_data: DataFrame with 'date' and 'rate' columns
        """
        self.data = production_data.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prepare data for analysis."""
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.sort_values('date')

        # Calculate time from first production
        first_date = self.data['date'].min()
        self.data['time_years'] = (
            (self.data['date'] - first_date).dt.days / 365.25
        )

    @staticmethod
    def exponential_decline(t: np.ndarray, qi: float, di: float) -> np.ndarray:
        """Exponential decline model."""
        return qi * np.exp(-di * t)

    @staticmethod
    def hyperbolic_decline(t: np.ndarray, qi: float, di: float,
                          b: float) -> np.ndarray:
        """Hyperbolic decline model."""
        return qi / np.power(1 + b * di * t, 1/b)

    @staticmethod
    def harmonic_decline(t: np.ndarray, qi: float, di: float) -> np.ndarray:
        """Harmonic decline model."""
        return qi / (1 + di * t)

    def fit_exponential(self) -> DeclineParameters:
        """Fit exponential decline curve."""
        t = self.data['time_years'].values
        q = self.data['rate'].values

        # Initial guesses
        qi_guess = q[0]
        di_guess = 0.3

        try:
            popt, _ = curve_fit(
                self.exponential_decline,
                t, q,
                p0=[qi_guess, di_guess],
                bounds=([0, 0], [qi_guess * 2, 2.0]),
                maxfev=5000
            )
            return DeclineParameters(qi=popt[0], di=popt[1], b=0.0)
        except:
            return DeclineParameters(qi=qi_guess, di=di_guess, b=0.0)

    def fit_hyperbolic(self, b_range: Tuple[float, float] = (0.1, 0.9)
                      ) -> DeclineParameters:
        """Fit hyperbolic decline curve."""
        t = self.data['time_years'].values
        q = self.data['rate'].values

        # Initial guesses
        qi_guess = q[0]
        di_guess = 0.3
        b_guess = 0.5

        try:
            popt, _ = curve_fit(
                self.hyperbolic_decline,
                t, q,
                p0=[qi_guess, di_guess, b_guess],
                bounds=(
                    [0, 0, b_range[0]],
                    [qi_guess * 2, 2.0, b_range[1]]
                ),
                maxfev=5000
            )
            return DeclineParameters(qi=popt[0], di=popt[1], b=popt[2])
        except:
            return DeclineParameters(qi=qi_guess, di=di_guess, b=b_guess)

<<<<<<< HEAD
    @staticmethod
    def duong_decline(t: np.ndarray, q1: float, a: float,
                     m: float) -> np.ndarray:
        """Duong decline model for unconventional wells."""
        # Avoid t=0 issues
        t = np.maximum(t, 1e-6)
        return q1 * np.power(t, -m) * np.exp(-a / (1 - m) * (np.power(t, 1 - m) - 1))

    @staticmethod
    def stretched_exponential(t: np.ndarray, qi: float, tau: float,
                             n: float) -> np.ndarray:
        """Stretched exponential decline model."""
        return qi * np.exp(-np.power(t / tau, n))

    @staticmethod
    def modified_hyperbolic(t: np.ndarray, qi: float, di: float,
                           b: float, d_min: float) -> np.ndarray:
        """Modified hyperbolic with terminal decline rate."""
        result = np.zeros_like(t)
        for i, ti in enumerate(t):
            # Current decline rate
            d_t = di / (1 + b * di * ti)
            if d_t > d_min:
                # Still in hyperbolic phase
                result[i] = qi / np.power(1 + b * di * ti, 1/b)
            else:
                # Switch to exponential at d_min
                t_switch = (di / d_min - 1) / (b * di)
                q_switch = qi / np.power(1 + b * di * t_switch, 1/b)
                result[i] = q_switch * np.exp(-d_min * (ti - t_switch))
        return result

    def fit_duong(self, t_range: Tuple[float, float] = (0.5, 3.0)
                 ) -> DeclineParameters:
        """Fit Duong decline model (unconventional)."""
        t = self.data['time_years'].values
        q = self.data['rate'].values

        # Convert to days for Duong
        t_days = t * 365.25 + 1  # Add 1 to avoid t=0

        # Initial guesses
        q1_guess = q[0]
        a_guess = 1.0
        m_guess = 1.2

        try:
            popt, _ = curve_fit(
                self.duong_decline,
                t_days, q,
                p0=[q1_guess, a_guess, m_guess],
                bounds=(
                    [0, 0.1, 0.5],
                    [q1_guess * 3, 5.0, 2.0]
                ),
                maxfev=10000
            )
            return DeclineParameters(
                qi=popt[0], di=0, b=0,
                a=popt[1], m=popt[2],
                decline_type=DeclineType.DUONG
            )
        except:
            return DeclineParameters(
                qi=q1_guess, di=0, b=0,
                a=a_guess, m=m_guess,
                decline_type=DeclineType.DUONG
            )

    def fit_modified_hyperbolic(self, d_min: float = 0.06
                               ) -> DeclineParameters:
        """Fit modified hyperbolic with terminal decline."""
        t = self.data['time_years'].values
        q = self.data['rate'].values

        # First fit standard hyperbolic
        hyp_params = self.fit_hyperbolic()

        # Use those as starting point
        try:
            def mod_hyp_fixed_dmin(t, qi, di, b):
                return self.modified_hyperbolic(t, qi, di, b, d_min)

            popt, _ = curve_fit(
                mod_hyp_fixed_dmin,
                t, q,
                p0=[hyp_params.qi, hyp_params.di, hyp_params.b],
                bounds=(
                    [0, 0, 0.1],
                    [hyp_params.qi * 2, 2.0, 1.5]
                ),
                maxfev=5000
            )
            return DeclineParameters(
                qi=popt[0], di=popt[1], b=popt[2],
                d_min=d_min,
                decline_type=DeclineType.MODIFIED_HYPERBOLIC
            )
        except:
            return DeclineParameters(
                qi=hyp_params.qi, di=hyp_params.di, b=hyp_params.b,
                d_min=d_min,
                decline_type=DeclineType.MODIFIED_HYPERBOLIC
            )

    def fit_stretched_exponential(self) -> DeclineParameters:
        """Fit stretched exponential decline model."""
        t = self.data['time_years'].values
        q = self.data['rate'].values

        # Initial guesses
        qi_guess = q[0]
        tau_guess = 1.0
        n_guess = 0.7

        try:
            popt, _ = curve_fit(
                self.stretched_exponential,
                t, q,
                p0=[qi_guess, tau_guess, n_guess],
                bounds=(
                    [0, 0.1, 0.1],
                    [qi_guess * 2, 20.0, 1.0]
                ),
                maxfev=5000
            )
            return DeclineParameters(
                qi=popt[0], di=0, b=0,
                tau=popt[1], n=popt[2],
                decline_type=DeclineType.STRETCHED_EXP
            )
        except:
            return DeclineParameters(
                qi=qi_guess, di=0, b=0,
                tau=tau_guess, n=n_guess,
                decline_type=DeclineType.STRETCHED_EXP
            )

    def fit_best_model(self, include_unconventional: bool = False
                      ) -> Tuple[DeclineParameters, str]:
        """
        Fit all models and return best fit.

        Args:
            include_unconventional: Include Duong and stretched exp models

=======
    def fit_best_model(self) -> Tuple[DeclineParameters, str]:
        """
        Fit all models and return best fit.

>>>>>>> origin/main
        Returns:
            Tuple of (best parameters, model name)
        """
        models = {
            'exponential': self.fit_exponential(),
            'hyperbolic': self.fit_hyperbolic(),
        }

<<<<<<< HEAD
        if include_unconventional:
            models['duong'] = self.fit_duong()
            models['stretched'] = self.fit_stretched_exponential()

=======
>>>>>>> origin/main
        t = self.data['time_years'].values
        q = self.data['rate'].values

        best_model = None
        best_rmse = float('inf')
        best_params = None

        for name, params in models.items():
            if name == 'exponential':
                predicted = self.exponential_decline(t, params.qi, params.di)
<<<<<<< HEAD
            elif name == 'duong':
                predicted = self.duong_decline(t * 365.25 + 1, params.qi, params.a, params.m)
            elif name == 'stretched':
                predicted = self.stretched_exponential(t, params.qi, params.tau, params.n)
=======
>>>>>>> origin/main
            else:
                predicted = self.hyperbolic_decline(
                    t, params.qi, params.di, params.b
                )

            rmse = np.sqrt(np.mean((q - predicted) ** 2))

            if rmse < best_rmse:
                best_rmse = rmse
                best_model = name
                best_params = params

        return best_params, best_model

<<<<<<< HEAD
    def calculate_validation_metrics(self, params: DeclineParameters
                                    ) -> Dict[str, float]:
        """
        Calculate validation metrics for fitted parameters.

        Returns:
            Dict with R², RMSE, MAE, MAPE
        """
        t = self.data['time_years'].values
        q = self.data['rate'].values

        # Calculate predicted values
        if params.decline_type == DeclineType.EXPONENTIAL:
            predicted = self.exponential_decline(t, params.qi, params.di)
        elif params.decline_type == DeclineType.DUONG:
            predicted = self.duong_decline(t * 365.25 + 1, params.qi, params.a, params.m)
        elif params.decline_type == DeclineType.STRETCHED_EXP:
            predicted = self.stretched_exponential(t, params.qi, params.tau, params.n)
        elif params.decline_type == DeclineType.MODIFIED_HYPERBOLIC:
            predicted = self.modified_hyperbolic(t, params.qi, params.di, params.b, params.d_min)
        else:
            predicted = self.hyperbolic_decline(t, params.qi, params.di, params.b)

        # R-squared
        ss_res = np.sum((q - predicted) ** 2)
        ss_tot = np.sum((q - np.mean(q)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # RMSE
        rmse = np.sqrt(np.mean((q - predicted) ** 2))

        # MAE
        mae = np.mean(np.abs(q - predicted))

        # MAPE (Mean Absolute Percentage Error)
        mask = q > 0
        mape = np.mean(np.abs((q[mask] - predicted[mask]) / q[mask])) * 100

        return {
            'r_squared': r_squared,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }

=======
>>>>>>> origin/main
    def calculate_eur(self, params: DeclineParameters,
                     economic_limit: float = 10.0,
                     max_years: float = 50.0) -> float:
        """
        Calculate Estimated Ultimate Recovery.

        Args:
            params: Decline parameters
            economic_limit: Minimum economic rate
            max_years: Maximum forecast period
        """
        if params.b == 0:
            # Exponential: EUR with economic limit and time cap
            # If already below economic limit, no recoverable reserves
            if params.qi <= economic_limit:
                return 0.0
            # Time to reach economic limit: t = ln(qi/q_limit) / di
            t_econ = np.log(params.qi / economic_limit) / params.di
            t_max = min(max_years, max(0.0, t_econ))
            # Cumulative: Np = (qi/di) * (1 - exp(-di*t))
            return params.qi * 365.25 / params.di * (1 - np.exp(-params.di * t_max))
        elif params.b == 1:
            # Harmonic: EUR is infinite, use time limit
            # Cumulative = qi/di * ln(1 + di*t)
            t_max = min(max_years, (params.qi / economic_limit - 1) / params.di)
            return params.qi * 365.25 / params.di * np.log(1 + params.di * t_max)
        else:
            # Hyperbolic
            # Cumulative = qi^b / (di * (1-b)) * (qi^(1-b) - q_limit^(1-b))
            q_limit = max(economic_limit, 0.1)
            factor = params.qi ** params.b / (params.di * (1 - params.b))
            cum = factor * (params.qi ** (1 - params.b) - q_limit ** (1 - params.b))
            return cum * 365.25
```

### Production Forecaster

```python
from datetime import date, timedelta
from typing import List, Optional
import numpy as np
import pandas as pd

class ProductionForecaster:
    """
    Generate production forecasts using decline curve analysis.
    """

    def __init__(self, parameters: DeclineParameters,
                 start_date: date = None,
                 cumulative_to_date: float = 0.0):
        """
        Initialize forecaster.

        Args:
            parameters: Decline curve parameters
            start_date: Forecast start date
            cumulative_to_date: Production already recovered
        """
        self.params = parameters
        self.start_date = start_date or date.today()
        self.cum_to_date = cumulative_to_date

    def _calculate_rate(self, t: float) -> float:
        """Calculate rate at time t (years)."""
        if self.params.b == 0:
            return self.params.qi * np.exp(-self.params.di * t)
        elif self.params.b == 1:
            return self.params.qi / (1 + self.params.di * t)
        else:
            return self.params.qi / np.power(
                1 + self.params.b * self.params.di * t,
                1 / self.params.b
            )

    def _calculate_cumulative(self, t: float) -> float:
        """Calculate cumulative production at time t (years)."""
        if self.params.b == 0:
            # Exponential
            return self.params.qi / self.params.di * (
                1 - np.exp(-self.params.di * t)
            ) * 365.25
        elif self.params.b == 1:
            # Harmonic
            return self.params.qi / self.params.di * np.log(
                1 + self.params.di * t
            ) * 365.25
        else:
            # Hyperbolic
            q_t = self._calculate_rate(t)
            factor = self.params.qi ** self.params.b / (
                self.params.di * (1 - self.params.b)
            )
            return factor * (
                self.params.qi ** (1 - self.params.b) -
                q_t ** (1 - self.params.b)
            ) * 365.25

    def forecast(self, years: float = 30.0,
                interval_months: int = 1,
                economic_limit: float = 10.0,
                gor: float = 1.0) -> ForecastResult:
        """
        Generate production forecast.

        Args:
            years: Forecast period in years
            interval_months: Output interval in months
            economic_limit: Minimum economic rate (bbls/day or mcf/day)
            gor: Gas-oil ratio for gas calculation

        Returns:
            ForecastResult with forecast data
        """
        dates = []
        oil_rates = []
        gas_rates = []
        cumulative_oil = []
        cumulative_gas = []

        current_date = self.start_date
        total_months = int(years * 12)

        for month in range(0, total_months, interval_months):
            t = month / 12.0  # Time in years

            rate = self._calculate_rate(t)

            # Check economic limit
            if rate < economic_limit:
                break

            cum = self._calculate_cumulative(t) + self.cum_to_date

            dates.append(current_date)
            oil_rates.append(rate)
            gas_rates.append(rate * gor)
            cumulative_oil.append(cum)
            cumulative_gas.append(cum * gor)

            # Advance date by interval_months
            new_month = current_date.month + interval_months
            new_year = current_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            current_date = date(new_year, new_month, 1)

        # Calculate EUR
        analyzer = DeclineCurveAnalyzer.__new__(DeclineCurveAnalyzer)
        eur_oil = analyzer.calculate_eur(
            self.params, economic_limit, years
        ) + self.cum_to_date

        return ForecastResult(
            dates=dates,
            oil_rates=oil_rates,
            gas_rates=gas_rates,
            cumulative_oil=cumulative_oil,
            cumulative_gas=cumulative_gas,
            parameters=self.params,
            eur_oil=eur_oil,
            eur_gas=eur_oil * gor,
            remaining_oil=eur_oil - self.cum_to_date,
            remaining_gas=(eur_oil - self.cum_to_date) * gor
        )

    def to_dataframe(self, forecast: ForecastResult) -> pd.DataFrame:
        """Convert forecast to DataFrame."""
        return forecast.to_dataframe()
```

### Type Curve Generator

```python
<<<<<<< HEAD
from typing import List, Dict, Optional, Tuple, Callable
import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
=======
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
>>>>>>> origin/main

class TypeCurveGenerator:
    """
    Generate type curves from multiple well production histories.
<<<<<<< HEAD
    Supports multiple normalization methods, binning, and probabilistic analysis.
    """

    # Standard water depth bins for GOM
    WATER_DEPTH_BINS = {
        'shallow': (0, 1000),
        'deep': (1000, 5000),
        'ultra_deep': (5000, 15000)
    }

    def __init__(self, wells: List[pd.DataFrame],
                 metadata: Optional[List[Dict]] = None):
=======
    """

    def __init__(self, wells: List[pd.DataFrame]):
>>>>>>> origin/main
        """
        Initialize with list of well production DataFrames.

        Args:
            wells: List of DataFrames with 'date' and 'rate' columns
<<<<<<< HEAD
            metadata: Optional list of metadata dicts per well
        """
        self.wells = wells
        self.metadata = metadata or [{} for _ in wells]
        self.normalized_wells = []
        self.normalization_factors = []
        self.bins = {}

    def normalize_wells(self, method: NormalizationMethod = NormalizationMethod.PEAK,
                       time_reference: int = 30) -> List[pd.DataFrame]:
=======
        """
        self.wells = wells
        self.normalized_wells = []

    def normalize_wells(self, normalize_to: str = 'peak') -> List[pd.DataFrame]:
>>>>>>> origin/main
        """
        Normalize wells for type curve generation.

        Args:
<<<<<<< HEAD
            method: Normalization method to use
            time_reference: Days for IP calculation or cumulative reference
        """
        normalized = []
        self.normalization_factors = []
=======
            normalize_to: 'peak' or 'first_month'
        """
        normalized = []
>>>>>>> origin/main

        for well in self.wells:
            df = well.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

<<<<<<< HEAD
            # Calculate days and months from start
            first_date = df['date'].min()
            df['days'] = (df['date'] - first_date).dt.days
            df['month'] = (df['days'] / 30.44).astype(int)

            # Calculate normalization factor based on method
            if method == NormalizationMethod.PEAK:
                norm_factor = df['rate'].max()
            elif method == NormalizationMethod.FIRST_MONTH:
                norm_factor = df[df['month'] == 0]['rate'].mean()
            elif method == NormalizationMethod.IP_30:
                mask = df['days'] <= 30
                norm_factor = df[mask]['rate'].mean() if mask.sum() > 0 else df['rate'].iloc[0]
            elif method == NormalizationMethod.IP_90:
                mask = df['days'] <= 90
                norm_factor = df[mask]['rate'].mean() if mask.sum() > 0 else df['rate'].iloc[0]
            elif method == NormalizationMethod.MOVING_AVG:
                df['rate_smooth'] = df['rate'].rolling(window=30, min_periods=1).mean()
                norm_factor = df['rate_smooth'].max()
            elif method == NormalizationMethod.CUMULATIVE:
                # Normalize so all wells have same cumulative at reference time
                ref_cum = df[df['days'] <= time_reference]['rate'].sum()
                norm_factor = ref_cum / time_reference if ref_cum > 0 else df['rate'].iloc[0]
            else:
                norm_factor = df['rate'].max()

            # Avoid division by zero
            norm_factor = max(norm_factor, 0.1)

            df['normalized_rate'] = df['rate'] / norm_factor
            self.normalization_factors.append(norm_factor)
=======
            # Calculate months from start
            first_date = df['date'].min()
            df['month'] = ((df['date'] - first_date).dt.days / 30.44).astype(int)

            # Normalize rate
            if normalize_to == 'peak':
                peak_rate = df['rate'].max()
            else:
                peak_rate = df['rate'].iloc[0]

            df['normalized_rate'] = df['rate'] / peak_rate
>>>>>>> origin/main

            normalized.append(df)

        self.normalized_wells = normalized
        return normalized

<<<<<<< HEAD
    def create_bins(self, bin_type: TypeCurveBinType,
                   custom_bins: Optional[Dict[str, Any]] = None) -> Dict[str, TypeCurveBin]:
        """
        Create type curve bins based on well metadata.

        Args:
            bin_type: Type of binning to apply
            custom_bins: Optional custom bin definitions
        """
        bins = {}

        if bin_type == TypeCurveBinType.WATER_DEPTH:
            bin_defs = custom_bins or self.WATER_DEPTH_BINS
            for name, (min_wd, max_wd) in bin_defs.items():
                bins[name] = TypeCurveBin(
                    bin_type=bin_type,
                    bin_name=name,
                    criteria={'water_depth_ft': (min_wd, max_wd)}
                )

        elif bin_type == TypeCurveBinType.FORMATION:
            # Extract unique formations from metadata
            formations = set()
            for meta in self.metadata:
                if 'formation' in meta:
                    formations.add(meta['formation'])
            for formation in formations:
                bins[formation] = TypeCurveBin(
                    bin_type=bin_type,
                    bin_name=formation,
                    criteria={'formation': formation}
                )

        elif bin_type == TypeCurveBinType.VINTAGE:
            # Bin by year of first production
            for i, well in enumerate(self.wells):
                df = well.copy()
                df['date'] = pd.to_datetime(df['date'])
                year = df['date'].min().year
                year_str = str(year)
                if year_str not in bins:
                    bins[year_str] = TypeCurveBin(
                        bin_type=bin_type,
                        bin_name=year_str,
                        criteria={'vintage_year': year}
                    )

        # Assign wells to bins
        for i, meta in enumerate(self.metadata):
            for name, bin_def in bins.items():
                if bin_def.matches(meta):
                    bin_def.wells.append(i)

        self.bins[bin_type] = bins
        return bins

    def generate_type_curve(self,
                           percentiles: List[float] = [10, 50, 90],
                           min_wells: int = 3,
                           well_indices: Optional[List[int]] = None
                           ) -> TypeCurveResult:
=======
    def generate_type_curve(self,
                           percentiles: List[float] = [10, 50, 90]
                           ) -> pd.DataFrame:
>>>>>>> origin/main
        """
        Generate type curve with percentile ranges.

        Args:
            percentiles: Percentiles to calculate (P10, P50, P90)
<<<<<<< HEAD
            min_wells: Minimum wells required per month
            well_indices: Optional subset of well indices to use

        Returns:
            TypeCurveResult with percentile curves
=======

        Returns:
            DataFrame with type curves
>>>>>>> origin/main
        """
        if not self.normalized_wells:
            self.normalize_wells()

<<<<<<< HEAD
        # Select wells
        if well_indices:
            wells_to_use = [self.normalized_wells[i] for i in well_indices]
        else:
            wells_to_use = self.normalized_wells

        # Find maximum months
        max_months = max(df['month'].max() for df in wells_to_use)
=======
        # Find maximum months across all wells
        max_months = max(df['month'].max() for df in self.normalized_wells)
>>>>>>> origin/main

        # Collect rates by month
        monthly_rates = {m: [] for m in range(int(max_months) + 1)}

<<<<<<< HEAD
        for df in wells_to_use:
=======
        for df in self.normalized_wells:
>>>>>>> origin/main
            for _, row in df.iterrows():
                month = int(row['month'])
                if month in monthly_rates:
                    monthly_rates[month].append(row['normalized_rate'])

<<<<<<< HEAD
        # Calculate percentiles and statistics
        months = []
        p10_rates, p50_rates, p90_rates = [], [], []
        mean_rates, well_counts = [], []

        for month in sorted(monthly_rates.keys()):
            rates = monthly_rates[month]
            if len(rates) >= min_wells:
                months.append(month)
                # Note: P10 = high side, P90 = low side (exceedance)
                p10_rates.append(np.percentile(rates, 90))
                p50_rates.append(np.percentile(rates, 50))
                p90_rates.append(np.percentile(rates, 10))
                mean_rates.append(np.mean(rates))
                well_counts.append(len(rates))

        return TypeCurveResult(
            months=months,
            p10_rates=p10_rates,
            p50_rates=p50_rates,
            p90_rates=p90_rates,
            mean_rates=mean_rates,
            well_counts=well_counts
        )

    def fit_type_curve(self, percentile: float = 50,
                      model: DeclineType = DeclineType.HYPERBOLIC,
                      well_indices: Optional[List[int]] = None
                      ) -> Tuple[DeclineParameters, Dict[str, float]]:
=======
        # Calculate percentiles
        type_curve_data = []
        for month in sorted(monthly_rates.keys()):
            rates = monthly_rates[month]
            if len(rates) >= 3:  # Need minimum wells
                row = {'month': month}
                for p in percentiles:
                    row[f'P{p}'] = np.percentile(rates, 100 - p)
                row['mean'] = np.mean(rates)
                row['well_count'] = len(rates)
                type_curve_data.append(row)

        return pd.DataFrame(type_curve_data)

    def fit_type_curve(self, percentile: float = 50) -> DeclineParameters:
>>>>>>> origin/main
        """
        Fit decline curve to type curve percentile.

        Args:
<<<<<<< HEAD
            percentile: Percentile to fit (10, 50, or 90)
            model: Decline model type to fit
            well_indices: Optional subset of wells

        Returns:
            Tuple of (fitted parameters, validation metrics)
        """
        result = self.generate_type_curve([percentile], well_indices=well_indices)

        # Get rate column
        if percentile == 10:
            rates = result.p10_rates
        elif percentile == 90:
            rates = result.p90_rates
        else:
            rates = result.p50_rates

        # Create analyzer with type curve data
        tc_df = pd.DataFrame({
            'date': pd.date_range(start='2020-01-01',
                                  periods=len(result.months), freq='MS'),
            'rate': rates
        })

        analyzer = DeclineCurveAnalyzer(tc_df)

        if model == DeclineType.EXPONENTIAL:
            params = analyzer.fit_exponential()
        elif model == DeclineType.HYPERBOLIC:
            params = analyzer.fit_hyperbolic()
        elif model == DeclineType.DUONG:
            params = analyzer.fit_duong()
        elif model == DeclineType.MODIFIED_HYPERBOLIC:
            params = analyzer.fit_modified_hyperbolic()
        else:
            params, _ = analyzer.fit_best_model()

        # Calculate validation metrics
        t = np.array(result.months) / 12.0
        if params.decline_type == DeclineType.EXPONENTIAL:
            predicted = analyzer.exponential_decline(t, params.qi, params.di)
        elif params.decline_type == DeclineType.DUONG:
            predicted = analyzer.duong_decline(t * 365.25, params.qi, params.a, params.m)
        else:
            predicted = analyzer.hyperbolic_decline(t, params.qi, params.di, params.b)

        actual = np.array(rates)
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        mae = np.mean(np.abs(actual - predicted))

        metrics = {
            'r_squared': r_squared,
            'rmse': rmse,
            'mae': mae
        }

        return params, metrics

    def generate_bin_type_curves(self, bin_type: TypeCurveBinType
                                ) -> Dict[str, TypeCurveResult]:
        """
        Generate type curves for each bin.

        Args:
            bin_type: Type of binning to use

        Returns:
            Dict mapping bin name to TypeCurveResult
        """
        if bin_type not in self.bins:
            self.create_bins(bin_type)

        results = {}
        for name, bin_def in self.bins[bin_type].items():
            if len(bin_def.wells) >= 3:
                results[name] = self.generate_type_curve(
                    well_indices=bin_def.wells
                )

        return results

    def scale_type_curve(self, type_curve: TypeCurveResult,
                        target_ip: float,
                        percentile: str = 'P50') -> pd.DataFrame:
        """
        Scale a normalized type curve to a target initial production rate.

        Args:
            type_curve: TypeCurveResult to scale
            target_ip: Target initial production rate
            percentile: Which percentile to scale (P10, P50, P90)

        Returns:
            DataFrame with scaled production rates
        """
        tc_df = type_curve.to_dataframe()

        # Get the rate column for the percentile
        rate_col = percentile

        # Scale to target IP
        first_rate = tc_df[rate_col].iloc[0]
        scale_factor = target_ip / first_rate if first_rate > 0 else target_ip

        scaled_df = pd.DataFrame({
            'month': tc_df['month'],
            f'{rate_col}_scaled': tc_df[rate_col] * scale_factor,
            'well_count': tc_df['well_count']
        })

        return scaled_df

    def calculate_eur_distribution(self, economic_limit: float = 10.0,
                                   max_years: float = 30.0
                                   ) -> Dict[str, float]:
        """
        Calculate EUR distribution (P10/P50/P90) from type curves.

        Args:
            economic_limit: Minimum economic rate
            max_years: Maximum forecast period

        Returns:
            Dict with P10, P50, P90 EUR estimates
        """
        eur_values = []

        for i, well in enumerate(self.normalized_wells):
            # De-normalize to get actual rates
            norm_factor = self.normalization_factors[i]
            actual_rates = well['normalized_rate'] * norm_factor

            # Fit decline and calculate EUR
            well_df = pd.DataFrame({
                'date': well['date'],
                'rate': actual_rates
            })
            analyzer = DeclineCurveAnalyzer(well_df)
            params, _ = analyzer.fit_best_model()
            eur = analyzer.calculate_eur(params, economic_limit, max_years)
            eur_values.append(eur)

        return {
            'P10': np.percentile(eur_values, 90),  # High side
            'P50': np.percentile(eur_values, 50),
            'P90': np.percentile(eur_values, 10),  # Low side
            'mean': np.mean(eur_values),
            'std': np.std(eur_values)
        }
=======
            percentile: Percentile to fit (e.g., 50 for P50)
        """
        type_curve = self.generate_type_curve([percentile])

        # Create analyzer with type curve data
        tc_df = pd.DataFrame({
            'date': pd.date_range(start='2020-01-01', periods=len(type_curve), freq='MS'),
            'rate': type_curve[f'P{percentile}'].values
        })

        analyzer = DeclineCurveAnalyzer(tc_df)
        params, _ = analyzer.fit_best_model()

        return params
>>>>>>> origin/main
```

### Report Generator

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import pandas as pd

class ProductionReportGenerator:
    """Generate interactive HTML reports for production forecasts."""

    def __init__(self, forecast: ForecastResult,
                 historical_data: pd.DataFrame = None):
        """
        Initialize report generator.

        Args:
            forecast: Forecast results
            historical_data: Optional historical production data
        """
        self.forecast = forecast
        self.historical = historical_data

    def generate_report(self, output_path: Path,
                       well_name: str = "Well") -> Path:
        """Generate comprehensive production forecast report."""

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Production Rate Forecast',
                'Cumulative Production',
                'Decline Curve Analysis',
                'Forecast Summary'
            ),
            specs=[
                [{'type': 'scatter'}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'table'}]
            ]
        )

        forecast_df = self.forecast.to_dataframe()

        # Production Rate Plot
        if self.historical is not None:
            fig.add_trace(
                go.Scatter(
                    x=self.historical['date'],
                    y=self.historical['rate'],
                    mode='markers',
                    name='Historical',
                    marker=dict(color='blue', size=6)
                ),
                row=1, col=1
            )

        fig.add_trace(
            go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['oil_rate'],
                mode='lines',
                name='Forecast',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )

        # Cumulative Production
        fig.add_trace(
            go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['cumulative_oil'],
                fill='tozeroy',
                name='Cumulative Oil',
                line=dict(color='green')
            ),
            row=1, col=2
        )

        # Add EUR line
        fig.add_hline(
            y=self.forecast.eur_oil,
            line_dash='dash',
            line_color='orange',
            annotation_text=f'EUR: {self.forecast.eur_oil/1e6:.2f} MMbbls',
            row=1, col=2
        )

        # Decline Curve (semi-log)
        fig.add_trace(
            go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['oil_rate'],
                mode='lines',
                name='Rate (log)',
                line=dict(color='purple')
            ),
            row=2, col=1
        )
        fig.update_yaxes(type='log', row=2, col=1)

        # Summary Table
        params = self.forecast.parameters
        summary_data = {
            'Parameter': [
                'Initial Rate (qi)',
                'Decline Rate (Di)',
                'b-factor',
                'Decline Type',
                'EUR Oil',
                'EUR Gas',
                'Remaining Oil',
                'Remaining Gas'
            ],
            'Value': [
                f'{params.qi:.1f} bbl/d',
                f'{params.di*100:.1f} %/year',
                f'{params.b:.3f}',
                params.decline_type.value,
                f'{self.forecast.eur_oil/1e6:.2f} MMbbl',
                f'{self.forecast.eur_gas/1e6:.2f} MMmcf',
                f'{self.forecast.remaining_oil/1e6:.2f} MMbbl',
                f'{self.forecast.remaining_gas/1e6:.2f} MMmcf'
            ]
        }

        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Parameter', 'Value'],
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=[summary_data['Parameter'], summary_data['Value']],
                    fill_color='lavender',
                    align='left'
                )
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text=f'{well_name} - Production Forecast',
            showlegend=True
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))

        return output_path
```

## YAML Configuration

### Forecast Configuration

```yaml
# config/production_forecast.yaml

metadata:
  well_name: "Well A-1"
  field: "Deepwater GOM"
  analyst: "Engineering Team"
  date: "2025-01-15"

historical_data:
  source: "file"
  file_path: "data/production/well_a1_history.csv"
  date_column: "date"
  rate_column: "oil_rate"

decline_parameters:
  # Auto-fit from historical data
  auto_fit: true

  # Or manual parameters
  # qi: 5000  # Initial rate (bbl/day)
  # di: 0.35  # Initial decline (fraction/year)
  # b: 0.8    # Decline exponent

  # Constraints
  b_range: [0.3, 1.2]  # Typical for unconventional

forecast:
  start_date: "2025-01-01"
  years: 30
  economic_limit: 25  # bbl/day
  interval: "monthly"

gas:
  gor: 2.5  # mcf/bbl
  gor_trend: "constant"  # or "increasing", "decreasing"

output:
  csv_path: "data/results/well_a1_forecast.csv"
  report_path: "reports/well_a1_forecast.html"
```

### Type Curve Configuration

```yaml
# config/type_curve.yaml

metadata:
  field: "Lower Tertiary"
  formation: "Wilcox"
  analyst: "Reservoir Team"

wells:
  source: "directory"
  path: "data/production/lower_tertiary/"
  pattern: "*.csv"

  # Or explicit list
  # files:
  #   - "well_1.csv"
  #   - "well_2.csv"

<<<<<<< HEAD
  # Well metadata for binning
  metadata_file: "data/production/well_metadata.csv"

normalization:
  method: "30_day_ip"  # peak, first_month, 30_day_ip, 90_day_ip, moving_average
  time_reference: 30   # Days for IP or cumulative reference
=======
normalization:
  method: "peak"  # or "first_month", "30_day_ip"
>>>>>>> origin/main

type_curve:
  percentiles: [10, 50, 90]
  min_wells_per_month: 5

<<<<<<< HEAD
  # Binning configuration
  binning:
    enabled: true
    bin_type: "water_depth"  # formation, completion, water_depth, vintage
    custom_bins:
      shallow: [0, 1500]
      deep: [1500, 5000]
      ultra_deep: [5000, 15000]

fit:
  model: "hyperbolic"  # exponential, hyperbolic, duong, modified_hyperbolic
  b_range: [0.5, 1.5]
  d_min: 0.06  # Terminal decline for modified hyperbolic
  include_unconventional: false

eur:
  economic_limit: 25  # bbl/day
  max_years: 40
  calculate_distribution: true
=======
fit:
  model: "hyperbolic"
  b_range: [0.5, 1.5]
>>>>>>> origin/main

output:
  type_curve_csv: "data/results/lower_tertiary_type_curve.csv"
  report_path: "reports/lower_tertiary_type_curves.html"
<<<<<<< HEAD
  export_fits: true
```

### Multi-Field Type Curve Comparison

```yaml
# config/type_curve_comparison.yaml

metadata:
  project: "GOM Deepwater Comparison"
  analyst: "Reservoir Engineering"

fields:
  - name: "Lower Tertiary"
    path: "data/production/lower_tertiary/"
    formation: "Wilcox"

  - name: "Miocene"
    path: "data/production/miocene/"
    formation: "Miocene"

  - name: "Norphlet"
    path: "data/production/norphlet/"
    formation: "Norphlet"

analysis:
  normalization: "30_day_ip"
  percentiles: [10, 50, 90]
  min_wells: 5
  time_horizon_months: 120

  # Statistical comparison
  compare_eur: true
  compare_decline_rates: true
  compare_b_factors: true

benchmarking:
  reference_field: "Lower Tertiary"
  metrics:
    - "eur_p50"
    - "di_p50"
    - "b_factor"
    - "first_year_recovery"

output:
  report_path: "reports/field_type_curve_comparison.html"
  csv_export: "data/results/type_curve_comparison.csv"
=======
>>>>>>> origin/main
```

## CLI Usage

```bash
# Fit decline curve to historical data
python -m production_forecaster fit \
    --data data/production/well_history.csv \
    --model hyperbolic

<<<<<<< HEAD
# Fit unconventional decline models
python -m production_forecaster fit \
    --data data/production/shale_well.csv \
    --model duong \
    --output reports/duong_fit.html

=======
>>>>>>> origin/main
# Generate forecast
python -m production_forecaster forecast \
    --config config/production_forecast.yaml \
    --output reports/forecast.html

<<<<<<< HEAD
# Generate type curves with binning
python -m production_forecaster type-curve \
    --wells data/production/*.csv \
    --percentiles 10 50 90 \
    --normalize 30_day_ip \
    --bin-by water_depth \
    --output reports/type_curves.html

# Generate type curves from config
python -m production_forecaster type-curve \
    --config config/type_curve.yaml

# Calculate EUR with distribution
python -m production_forecaster eur \
    --qi 5000 --di 0.35 --b 0.8 \
    --limit 25 \
    --distribution  # Calculate P10/P50/P90

# Scale type curve to target IP
python -m production_forecaster scale-type-curve \
    --type-curve data/results/lower_tertiary_type_curve.csv \
    --target-ip 8000 \
    --percentile P50 \
    --output reports/scaled_forecast.html

# Compare wells against type curve
python -m production_forecaster compare \
    --wells well1.csv well2.csv well3.csv \
    --type-curve data/results/field_type_curve.csv \
    --normalize 30_day_ip \
    --output reports/comparison.html

# Compare multiple field type curves
python -m production_forecaster compare-fields \
    --config config/type_curve_comparison.yaml

# Validate decline fit
python -m production_forecaster validate \
    --data data/production/well_history.csv \
    --model hyperbolic \
    --holdout 0.2  # Hold out 20% for validation
=======
# Generate type curves
python -m production_forecaster type-curve \
    --wells data/production/*.csv \
    --percentiles 10 50 90 \
    --output reports/type_curves.html

# Calculate EUR
python -m production_forecaster eur \
    --qi 5000 --di 0.35 --b 0.8 \
    --limit 25

# Compare wells
python -m production_forecaster compare \
    --wells well1.csv well2.csv well3.csv \
    --normalize peak \
    --output reports/comparison.html
>>>>>>> origin/main
```

## Usage Examples

### Example 1: Fit and Forecast Single Well

```python
from production_forecaster import (
    DeclineCurveAnalyzer, ProductionForecaster,
    ProductionReportGenerator
)
import pandas as pd
from pathlib import Path

# Load historical production
historical = pd.read_csv('data/production/well_a1.csv')

# Fit decline curve
analyzer = DeclineCurveAnalyzer(historical)
params, model_type = analyzer.fit_best_model()

print(f"Best fit: {model_type}")
print(f"qi = {params.qi:.1f} bbl/d")
print(f"Di = {params.di*100:.1f} %/year")
print(f"b = {params.b:.3f}")

# Generate forecast
forecaster = ProductionForecaster(
    params,
    cumulative_to_date=historical['cumulative'].iloc[-1]
)
forecast = forecaster.forecast(years=30, economic_limit=25)

print(f"\nEUR: {forecast.eur_oil/1e6:.2f} MMbbl")
print(f"Remaining: {forecast.remaining_oil/1e6:.2f} MMbbl")

# Generate report
reporter = ProductionReportGenerator(forecast, historical)
reporter.generate_report(
    Path('reports/well_a1_forecast.html'),
    well_name='Well A-1'
)
```

<<<<<<< HEAD
### Example 2: Generate Type Curves with Binning

```python
from production_forecaster import (
    TypeCurveGenerator, NormalizationMethod, TypeCurveBinType
)
import glob
import pandas as pd

# Load all well data with metadata
well_files = glob.glob('data/production/field_x/*.csv')
wells = [pd.read_csv(f) for f in well_files]

# Load well metadata
metadata = pd.read_csv('data/production/well_metadata.csv')
well_metadata = metadata.to_dict('records')

# Generate type curves with 30-day IP normalization
generator = TypeCurveGenerator(wells, metadata=well_metadata)
generator.normalize_wells(method=NormalizationMethod.IP_30)

# Create water depth bins
generator.create_bins(TypeCurveBinType.WATER_DEPTH)

# Generate type curves for each bin
bin_results = generator.generate_bin_type_curves(TypeCurveBinType.WATER_DEPTH)

for bin_name, result in bin_results.items():
    print(f"\n{bin_name} Type Curve ({result.well_counts[0]} wells):")
    tc_df = result.to_dataframe()
    print(tc_df.head(12))

# Fit P50 with validation metrics
p50_params, metrics = generator.fit_type_curve(percentile=50)
=======
### Example 2: Generate Type Curves

```python
from production_forecaster import TypeCurveGenerator
import glob
import pandas as pd

# Load all well data
well_files = glob.glob('data/production/field_x/*.csv')
wells = [pd.read_csv(f) for f in well_files]

# Generate type curves
generator = TypeCurveGenerator(wells)
type_curve = generator.generate_type_curve(percentiles=[10, 50, 90])

print("Type Curve (first 12 months):")
print(type_curve.head(12))

# Fit P50 type curve
p50_params = generator.fit_type_curve(percentile=50)
>>>>>>> origin/main
print(f"\nP50 Type Curve Parameters:")
print(f"qi = {p50_params.qi:.3f} (normalized)")
print(f"Di = {p50_params.di*100:.1f} %/year")
print(f"b = {p50_params.b:.3f}")
<<<<<<< HEAD
print(f"R² = {metrics['r_squared']:.4f}")
print(f"RMSE = {metrics['rmse']:.4f}")

# Calculate EUR distribution
eur_dist = generator.calculate_eur_distribution(economic_limit=25)
print(f"\nEUR Distribution:")
print(f"P10: {eur_dist['P10']/1e6:.2f} MMbbl")
print(f"P50: {eur_dist['P50']/1e6:.2f} MMbbl")
print(f"P90: {eur_dist['P90']/1e6:.2f} MMbbl")
```

### Example 3: Fit Unconventional Decline Models

```python
from production_forecaster import DeclineCurveAnalyzer, DeclineType
import pandas as pd

# Load unconventional well production
df = pd.read_csv('data/production/shale_well.csv')

analyzer = DeclineCurveAnalyzer(df)

# Fit Duong model
duong_params = analyzer.fit_duong()
print(f"Duong Model:")
print(f"q1 = {duong_params.qi:.1f} bbl/d")
print(f"a = {duong_params.a:.3f}")
print(f"m = {duong_params.m:.3f}")

# Fit stretched exponential
se_params = analyzer.fit_stretched_exponential()
print(f"\nStretched Exponential:")
print(f"qi = {se_params.qi:.1f} bbl/d")
print(f"tau = {se_params.tau:.3f} years")
print(f"n = {se_params.n:.3f}")

# Compare all models
best_params, best_model = analyzer.fit_best_model(include_unconventional=True)
metrics = analyzer.calculate_validation_metrics(best_params)

print(f"\nBest Model: {best_model}")
print(f"R² = {metrics['r_squared']:.4f}")
print(f"MAPE = {metrics['mape']:.1f}%")
```

### Example 4: Scale Type Curve for New Well Forecast

```python
from production_forecaster import (
    TypeCurveGenerator, ProductionForecaster, ProductionReportGenerator
)
from datetime import date
import pandas as pd
import glob

# Load existing wells and generate type curve
well_files = glob.glob('data/production/lower_tertiary/*.csv')
wells = [pd.read_csv(f) for f in well_files]

generator = TypeCurveGenerator(wells)
generator.normalize_wells()
type_curve = generator.generate_type_curve()

# Fit P50 type curve
p50_params, _ = generator.fit_type_curve(percentile=50)

# Scale to new well target IP
target_ip = 8500  # Expected IP for new well

# De-normalize parameters
avg_norm_factor = sum(generator.normalization_factors) / len(generator.normalization_factors)
scaled_params = DeclineParameters(
    qi=p50_params.qi * target_ip,
    di=p50_params.di,
    b=p50_params.b
)

# Generate forecast
forecaster = ProductionForecaster(
    scaled_params,
    start_date=date(2026, 3, 1)
)
forecast = forecaster.forecast(years=30, economic_limit=25, gor=2.0)

print(f"New Well Forecast (P50):")
print(f"Target IP: {target_ip} bbl/d")
print(f"EUR: {forecast.eur_oil/1e6:.2f} MMbbl")
print(f"EUR Gas: {forecast.eur_gas/1e9:.2f} Bcf")

# Generate report
reporter = ProductionReportGenerator(forecast)
reporter.generate_report(
    Path('reports/new_well_p50_forecast.html'),
    well_name='Lower Tertiary Prospect A'
)
```

### Example 5: Multi-Well Comparison Against Type Curve

```python
from production_forecaster import (
    DeclineCurveAnalyzer, TypeCurveGenerator, NormalizationMethod
)
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import glob

# Load reference wells for type curve
ref_wells = [pd.read_csv(f) for f in glob.glob('data/production/reference/*.csv')]
generator = TypeCurveGenerator(ref_wells)
generator.normalize_wells(method=NormalizationMethod.IP_30)
type_curve = generator.generate_type_curve()

# Wells to compare
=======
```

### Example 3: Multi-Well Comparison

```python
from production_forecaster import DeclineCurveAnalyzer, ProductionForecaster
import pandas as pd
import plotly.graph_objects as go

>>>>>>> origin/main
wells = ['well_a.csv', 'well_b.csv', 'well_c.csv']
results = []

for well_file in wells:
    df = pd.read_csv(f'data/production/{well_file}')

    analyzer = DeclineCurveAnalyzer(df)
<<<<<<< HEAD
    params, model = analyzer.fit_best_model()
    metrics = analyzer.calculate_validation_metrics(params)

    # Calculate 30-day IP for normalization
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    first_30 = df.head(30)
    ip_30 = first_30['rate'].mean()

    results.append({
        'well': well_file.replace('.csv', ''),
        'ip_30': ip_30,
        'qi': params.qi,
        'di': params.di * 100,
        'b': params.b,
        'model': model,
        'r_squared': metrics['r_squared'],
        'eur_mmbbl': analyzer.calculate_eur(params, 25, 30) / 1e6
=======
    params, _ = analyzer.fit_best_model()

    forecaster = ProductionForecaster(params)
    forecast = forecaster.forecast(years=20)

    results.append({
        'well': well_file,
        'qi': params.qi,
        'di': params.di,
        'b': params.b,
        'eur': forecast.eur_oil
>>>>>>> origin/main
    })

# Create comparison table
comparison = pd.DataFrame(results)
<<<<<<< HEAD
print(comparison.to_string(index=False))

# Plot wells against type curve
fig = go.Figure()

# Add type curve bands
tc_df = type_curve.to_dataframe()
fig.add_trace(go.Scatter(
    x=tc_df['month'], y=tc_df['P10'],
    mode='lines', line=dict(color='green', dash='dash'),
    name='P10'
))
fig.add_trace(go.Scatter(
    x=tc_df['month'], y=tc_df['P50'],
    mode='lines', line=dict(color='blue', width=2),
    name='P50 Type Curve'
))
fig.add_trace(go.Scatter(
    x=tc_df['month'], y=tc_df['P90'],
    mode='lines', line=dict(color='red', dash='dash'),
    name='P90'
))

# Add individual wells (normalized)
for well_file in wells:
    df = pd.read_csv(f'data/production/{well_file}')
    df['date'] = pd.to_datetime(df['date'])
    first_date = df['date'].min()
    df['month'] = ((df['date'] - first_date).dt.days / 30.44).astype(int)
    ip_30 = df[df['month'] == 0]['rate'].mean()
    df['normalized'] = df['rate'] / ip_30

    fig.add_trace(go.Scatter(
        x=df['month'], y=df['normalized'],
        mode='markers', marker=dict(size=4),
        name=well_file.replace('.csv', '')
    ))

fig.update_layout(
    title='Well Performance vs Type Curve',
    xaxis_title='Months on Production',
    yaxis_title='Normalized Rate (q/IP)',
    yaxis_type='log'
)
fig.write_html('reports/well_vs_type_curve.html')
```

### Example 6: Multi-Field Type Curve Comparison

```python
from production_forecaster import TypeCurveGenerator, NormalizationMethod
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob

fields = {
    'Lower Tertiary': 'data/production/lower_tertiary/*.csv',
    'Miocene': 'data/production/miocene/*.csv',
    'Norphlet': 'data/production/norphlet/*.csv'
}

field_results = {}

for field_name, pattern in fields.items():
    wells = [pd.read_csv(f) for f in glob.glob(pattern)]
    if len(wells) < 3:
        continue

    generator = TypeCurveGenerator(wells)
    generator.normalize_wells(method=NormalizationMethod.IP_30)
    tc = generator.generate_type_curve()

    # Fit P50
    params, metrics = generator.fit_type_curve(percentile=50)

    # EUR distribution
    eur_dist = generator.calculate_eur_distribution(economic_limit=25)

    field_results[field_name] = {
        'type_curve': tc,
        'params': params,
        'metrics': metrics,
        'eur': eur_dist,
        'well_count': len(wells)
    }

# Print comparison table
print("Field Type Curve Comparison\n")
print(f"{'Field':<20} {'Wells':<8} {'Di (%/yr)':<12} {'b-factor':<10} {'EUR P50 (MMbbl)':<15} {'R²':<8}")
print("-" * 75)
for field, data in field_results.items():
    p = data['params']
    print(f"{field:<20} {data['well_count']:<8} {p.di*100:<12.1f} {p.b:<10.3f} {data['eur']['P50']/1e6:<15.2f} {data['metrics']['r_squared']:<8.4f}")

# Create comparison plot
fig = make_subplots(rows=1, cols=2,
                   subplot_titles=['Normalized Type Curves', 'EUR Distribution'])

colors = {'Lower Tertiary': 'blue', 'Miocene': 'green', 'Norphlet': 'red'}

for field, data in field_results.items():
    tc_df = data['type_curve'].to_dataframe()

    fig.add_trace(go.Scatter(
        x=tc_df['month'], y=tc_df['P50'],
        mode='lines', name=f'{field} P50',
        line=dict(color=colors.get(field, 'gray'))
    ), row=1, col=1)

# EUR box plot
fig.add_trace(go.Bar(
    x=list(field_results.keys()),
    y=[d['eur']['P50']/1e6 for d in field_results.values()],
    error_y=dict(
        type='data',
        symmetric=False,
        array=[(d['eur']['P10'] - d['eur']['P50'])/1e6 for d in field_results.values()],
        arrayminus=[(d['eur']['P50'] - d['eur']['P90'])/1e6 for d in field_results.values()]
    ),
    name='EUR P50'
), row=1, col=2)

fig.update_layout(height=500, title_text='GOM Deepwater Field Comparison')
fig.update_xaxes(title_text='Months', row=1, col=1)
fig.update_yaxes(title_text='Normalized Rate', type='log', row=1, col=1)
fig.update_xaxes(title_text='Field', row=1, col=2)
fig.update_yaxes(title_text='EUR (MMbbl)', row=1, col=2)

fig.write_html('reports/field_type_curve_comparison.html')
=======
print(comparison)
>>>>>>> origin/main
```

## Best Practices

### Data Quality
- Clean production data before analysis (remove outliers, handle gaps)
- Use at least 6-12 months of decline data for reliable fits
- Account for operational events (workovers, chokes, shut-ins)

### Model Selection
- Exponential (b=0): Mature fields, conventional reservoirs
- Hyperbolic (b<1): Most common for unconventional wells
- High b-factors (>1): Unconventional with extended linear flow

### Forecasting
- Validate forecasts against analogous wells
- Consider terminal decline rate for long-term forecasts
- Update forecasts quarterly with new production data

### Uncertainty
- Generate P10/P50/P90 forecasts for reserve booking
- Use Monte Carlo simulation for uncertainty quantification
- Document assumptions and limitations

## Related Skills

<<<<<<< HEAD
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic evaluation with Monte Carlo simulation
- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - Extract production, WAR, and APD data
- [field-analyzer](../field-analyzer/SKILL.md) - Field-level production analysis
- [well-production-dashboard](../well-production-dashboard/SKILL.md) - Production visualization
- [api12-drilling-analyzer](../api12-drilling-analyzer/SKILL.md) - Drilling performance analysis
- [hse-risk-analyzer](../hse-risk-analyzer/SKILL.md) - Safety-informed economic analysis
=======
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic evaluation using production forecasts
- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - Extract historical production data
- [field-analyzer](../field-analyzer/SKILL.md) - Field-level production analysis
- [well-production-dashboard](../well-production-dashboard/SKILL.md) - Production visualization
>>>>>>> origin/main

---

## Version History

- **1.0.0** (2025-12-30): Initial release with Arps decline models, type curves, and forecasting
