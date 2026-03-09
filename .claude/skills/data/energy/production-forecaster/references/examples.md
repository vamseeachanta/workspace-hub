# Production Forecaster — Reference Examples

Full implementation code, YAML templates, and usage examples extracted from SKILL.md v2.0.0.

---

## Data Models

```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Any
from enum import Enum
import numpy as np
import pandas as pd


class DeclineType(Enum):
    EXPONENTIAL = "exponential"
    HYPERBOLIC = "hyperbolic"
    HARMONIC = "harmonic"
    MODIFIED_HYPERBOLIC = "modified"
    DUONG = "duong"
    STRETCHED_EXP = "stretched"


class NormalizationMethod(Enum):
    PEAK = "peak"
    FIRST_MONTH = "first_month"
    IP_30 = "30_day_ip"
    IP_90 = "90_day_ip"
    MOVING_AVG = "moving_average"
    CUMULATIVE = "cumulative_at_time"


class TypeCurveBinType(Enum):
    FORMATION = "formation"
    COMPLETION = "completion"
    WATER_DEPTH = "water_depth"
    LATERAL_LENGTH = "lateral_length"
    PROPPANT = "proppant"
    VINTAGE = "vintage"


class ProductionPhase(Enum):
    BUILDUP = "buildup"
    PLATEAU = "plateau"
    DECLINE = "decline"
    ABANDONMENT = "abandonment"


@dataclass
class DeclineParameters:
    qi: float           # Initial rate (bbls/day or mcf/day)
    di: float           # Initial decline rate (fraction/year)
    b: float            # Decline exponent
    decline_type: DeclineType = DeclineType.HYPERBOLIC
    min_rate: float = 0.0
    max_time: float = 50.0
    d_min: Optional[float] = None   # Terminal decline rate
    a: Optional[float] = None       # Duong intercept
    m: Optional[float] = None       # Duong slope
    tau: Optional[float] = None     # Stretched exp time constant
    n: Optional[float] = None       # Stretched exp parameter

    def __post_init__(self):
        if self.a is not None and self.m is not None:
            self.decline_type = DeclineType.DUONG
        elif self.tau is not None and self.n is not None:
            self.decline_type = DeclineType.STRETCHED_EXP
        elif self.d_min is not None and self.b > 0:
            self.decline_type = DeclineType.MODIFIED_HYPERBOLIC
        elif self.b == 0:
            self.decline_type = DeclineType.EXPONENTIAL
        elif self.b == 1:
            self.decline_type = DeclineType.HARMONIC
        else:
            self.decline_type = DeclineType.HYPERBOLIC


@dataclass
class TypeCurveBin:
    bin_type: TypeCurveBinType
    bin_name: str
    criteria: Dict[str, Any] = field(default_factory=dict)
    wells: List[str] = field(default_factory=list)

    def matches(self, well_metadata: Dict[str, Any]) -> bool:
        for key, value in self.criteria.items():
            if key not in well_metadata:
                return False
            well_value = well_metadata[key]
            if isinstance(value, tuple):
                if not (value[0] <= well_value <= value[1]):
                    return False
            elif isinstance(value, list):
                if well_value not in value:
                    return False
            else:
                if well_value != value:
                    return False
        return True


@dataclass
class TypeCurveResult:
    months: List[int]
    p10_rates: List[float]
    p50_rates: List[float]
    p90_rates: List[float]
    mean_rates: List[float]
    well_counts: List[int]
    p10_params: Optional[DeclineParameters] = None
    p50_params: Optional[DeclineParameters] = None
    p90_params: Optional[DeclineParameters] = None
    r_squared: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    eur_p10: Optional[float] = None
    eur_p50: Optional[float] = None
    eur_p90: Optional[float] = None

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({
            'month': self.months,
            'P10': self.p10_rates,
            'P50': self.p50_rates,
            'P90': self.p90_rates,
            'mean': self.mean_rates,
            'well_count': self.well_counts
        })


@dataclass
class ProductionRecord:
    date: date
    oil_rate: float = 0.0
    gas_rate: float = 0.0
    water_rate: float = 0.0
    days_on: int = 30

    @property
    def oil_volume(self) -> float:
        return self.oil_rate * self.days_on

    @property
    def gas_volume(self) -> float:
        return self.gas_rate * self.days_on

    @property
    def gor(self) -> float:
        return self.gas_rate / self.oil_rate if self.oil_rate > 0 else 0.0


@dataclass
class ForecastResult:
    dates: List[date]
    oil_rates: List[float]
    gas_rates: List[float]
    cumulative_oil: List[float]
    cumulative_gas: List[float]
    parameters: DeclineParameters
    eur_oil: float = 0.0
    eur_gas: float = 0.0
    remaining_oil: float = 0.0
    remaining_gas: float = 0.0

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({
            'date': self.dates,
            'oil_rate': self.oil_rates,
            'gas_rate': self.gas_rates,
            'cumulative_oil': self.cumulative_oil,
            'cumulative_gas': self.cumulative_gas
        })
```

---

## DeclineCurveAnalyzer

```python
import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple, Optional, Dict
import pandas as pd


class DeclineCurveAnalyzer:
    def __init__(self, production_data: pd.DataFrame):
        self.data = production_data.copy()
        self._prepare_data()

    def _prepare_data(self):
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.sort_values('date')
        first_date = self.data['date'].min()
        self.data['time_years'] = (self.data['date'] - first_date).dt.days / 365.25

    @staticmethod
    def exponential_decline(t, qi, di):
        return qi * np.exp(-di * t)

    @staticmethod
    def hyperbolic_decline(t, qi, di, b):
        return qi / np.power(1 + b * di * t, 1 / b)

    @staticmethod
    def harmonic_decline(t, qi, di):
        return qi / (1 + di * t)

    @staticmethod
    def duong_decline(t, q1, a, m):
        t = np.maximum(t, 1e-6)
        return q1 * np.power(t, -m) * np.exp(-a / (1 - m) * (np.power(t, 1 - m) - 1))

    @staticmethod
    def stretched_exponential(t, qi, tau, n):
        return qi * np.exp(-np.power(t / tau, n))

    @staticmethod
    def modified_hyperbolic(t, qi, di, b, d_min):
        result = np.zeros_like(t)
        for i, ti in enumerate(t):
            d_t = di / (1 + b * di * ti)
            if d_t > d_min:
                result[i] = qi / np.power(1 + b * di * ti, 1 / b)
            else:
                t_switch = (di / d_min - 1) / (b * di)
                q_switch = qi / np.power(1 + b * di * t_switch, 1 / b)
                result[i] = q_switch * np.exp(-d_min * (ti - t_switch))
        return result

    def fit_exponential(self) -> DeclineParameters:
        t, q = self.data['time_years'].values, self.data['rate'].values
        try:
            popt, _ = curve_fit(self.exponential_decline, t, q,
                                p0=[q[0], 0.3], bounds=([0, 0], [q[0] * 2, 2.0]),
                                maxfev=5000)
            return DeclineParameters(qi=popt[0], di=popt[1], b=0.0)
        except Exception:
            return DeclineParameters(qi=q[0], di=0.3, b=0.0)

    def fit_hyperbolic(self, b_range: Tuple[float, float] = (0.1, 0.9)) -> DeclineParameters:
        t, q = self.data['time_years'].values, self.data['rate'].values
        try:
            popt, _ = curve_fit(self.hyperbolic_decline, t, q,
                                p0=[q[0], 0.3, 0.5],
                                bounds=([0, 0, b_range[0]], [q[0] * 2, 2.0, b_range[1]]),
                                maxfev=5000)
            return DeclineParameters(qi=popt[0], di=popt[1], b=popt[2])
        except Exception:
            return DeclineParameters(qi=q[0], di=0.3, b=0.5)

    def fit_duong(self, t_range: Tuple[float, float] = (0.5, 3.0)) -> DeclineParameters:
        t, q = self.data['time_years'].values, self.data['rate'].values
        t_days = t * 365.25 + 1
        try:
            popt, _ = curve_fit(self.duong_decline, t_days, q,
                                p0=[q[0], 1.0, 1.2],
                                bounds=([0, 0.1, 0.5], [q[0] * 3, 5.0, 2.0]),
                                maxfev=10000)
            return DeclineParameters(qi=popt[0], di=0, b=0,
                                     a=popt[1], m=popt[2],
                                     decline_type=DeclineType.DUONG)
        except Exception:
            return DeclineParameters(qi=q[0], di=0, b=0, a=1.0, m=1.2,
                                     decline_type=DeclineType.DUONG)

    def fit_modified_hyperbolic(self, d_min: float = 0.06) -> DeclineParameters:
        t, q = self.data['time_years'].values, self.data['rate'].values
        hyp_params = self.fit_hyperbolic()
        try:
            def mod_hyp_fixed_dmin(t, qi, di, b):
                return self.modified_hyperbolic(t, qi, di, b, d_min)

            popt, _ = curve_fit(mod_hyp_fixed_dmin, t, q,
                                p0=[hyp_params.qi, hyp_params.di, hyp_params.b],
                                bounds=([0, 0, 0.1], [hyp_params.qi * 2, 2.0, 1.5]),
                                maxfev=5000)
            return DeclineParameters(qi=popt[0], di=popt[1], b=popt[2],
                                     d_min=d_min, decline_type=DeclineType.MODIFIED_HYPERBOLIC)
        except Exception:
            return DeclineParameters(qi=hyp_params.qi, di=hyp_params.di, b=hyp_params.b,
                                     d_min=d_min, decline_type=DeclineType.MODIFIED_HYPERBOLIC)

    def fit_stretched_exponential(self) -> DeclineParameters:
        t, q = self.data['time_years'].values, self.data['rate'].values
        try:
            popt, _ = curve_fit(self.stretched_exponential, t, q,
                                p0=[q[0], 1.0, 0.7],
                                bounds=([0, 0.1, 0.1], [q[0] * 2, 20.0, 1.0]),
                                maxfev=5000)
            return DeclineParameters(qi=popt[0], di=0, b=0, tau=popt[1], n=popt[2],
                                     decline_type=DeclineType.STRETCHED_EXP)
        except Exception:
            return DeclineParameters(qi=q[0], di=0, b=0, tau=1.0, n=0.7,
                                     decline_type=DeclineType.STRETCHED_EXP)

    def fit_best_model(self, include_unconventional: bool = False) -> Tuple[DeclineParameters, str]:
        models = {
            'exponential': self.fit_exponential(),
            'hyperbolic': self.fit_hyperbolic(),
        }
        if include_unconventional:
            models['duong'] = self.fit_duong()
            models['stretched'] = self.fit_stretched_exponential()

        t, q = self.data['time_years'].values, self.data['rate'].values
        best_model, best_rmse, best_params = None, float('inf'), None

        for name, params in models.items():
            if name == 'exponential':
                predicted = self.exponential_decline(t, params.qi, params.di)
            elif name == 'duong':
                predicted = self.duong_decline(t * 365.25 + 1, params.qi, params.a, params.m)
            elif name == 'stretched':
                predicted = self.stretched_exponential(t, params.qi, params.tau, params.n)
            else:
                predicted = self.hyperbolic_decline(t, params.qi, params.di, params.b)

            rmse = np.sqrt(np.mean((q - predicted) ** 2))
            if rmse < best_rmse:
                best_rmse, best_model, best_params = rmse, name, params

        return best_params, best_model

    def calculate_validation_metrics(self, params: DeclineParameters) -> Dict[str, float]:
        t, q = self.data['time_years'].values, self.data['rate'].values
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

        ss_res = np.sum((q - predicted) ** 2)
        ss_tot = np.sum((q - np.mean(q)) ** 2)
        mask = q > 0
        return {
            'r_squared': 1 - (ss_res / ss_tot) if ss_tot > 0 else 0,
            'rmse': np.sqrt(np.mean((q - predicted) ** 2)),
            'mae': np.mean(np.abs(q - predicted)),
            'mape': np.mean(np.abs((q[mask] - predicted[mask]) / q[mask])) * 100
        }

    def calculate_eur(self, params: DeclineParameters,
                      economic_limit: float = 10.0,
                      max_years: float = 50.0) -> float:
        if params.b == 0:
            if params.qi <= economic_limit:
                return 0.0
            t_econ = np.log(params.qi / economic_limit) / params.di
            t_max = min(max_years, max(0.0, t_econ))
            return params.qi * 365.25 / params.di * (1 - np.exp(-params.di * t_max))
        elif params.b == 1:
            t_max = min(max_years, (params.qi / economic_limit - 1) / params.di)
            return params.qi * 365.25 / params.di * np.log(1 + params.di * t_max)
        else:
            q_limit = max(economic_limit, 0.1)
            factor = params.qi ** params.b / (params.di * (1 - params.b))
            cum = factor * (params.qi ** (1 - params.b) - q_limit ** (1 - params.b))
            return cum * 365.25
```

---

## ProductionForecaster

```python
from datetime import date
import numpy as np
import pandas as pd


class ProductionForecaster:
    def __init__(self, parameters: DeclineParameters,
                 start_date: date = None,
                 cumulative_to_date: float = 0.0):
        self.params = parameters
        self.start_date = start_date or date.today()
        self.cum_to_date = cumulative_to_date

    def _calculate_rate(self, t: float) -> float:
        if self.params.b == 0:
            return self.params.qi * np.exp(-self.params.di * t)
        elif self.params.b == 1:
            return self.params.qi / (1 + self.params.di * t)
        else:
            return self.params.qi / np.power(
                1 + self.params.b * self.params.di * t, 1 / self.params.b)

    def _calculate_cumulative(self, t: float) -> float:
        if self.params.b == 0:
            return self.params.qi / self.params.di * (
                1 - np.exp(-self.params.di * t)) * 365.25
        elif self.params.b == 1:
            return self.params.qi / self.params.di * np.log(
                1 + self.params.di * t) * 365.25
        else:
            q_t = self._calculate_rate(t)
            factor = self.params.qi ** self.params.b / (
                self.params.di * (1 - self.params.b))
            return factor * (
                self.params.qi ** (1 - self.params.b) -
                q_t ** (1 - self.params.b)) * 365.25

    def forecast(self, years: float = 30.0, interval_months: int = 1,
                 economic_limit: float = 10.0, gor: float = 1.0) -> ForecastResult:
        dates, oil_rates, gas_rates, cumulative_oil, cumulative_gas = [], [], [], [], []
        current_date = self.start_date
        total_months = int(years * 12)

        for month in range(0, total_months, interval_months):
            t = month / 12.0
            rate = self._calculate_rate(t)
            if rate < economic_limit:
                break
            cum = self._calculate_cumulative(t) + self.cum_to_date
            dates.append(current_date)
            oil_rates.append(rate)
            gas_rates.append(rate * gor)
            cumulative_oil.append(cum)
            cumulative_gas.append(cum * gor)
            new_month = current_date.month + interval_months
            new_year = current_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            current_date = date(new_year, new_month, 1)

        analyzer = DeclineCurveAnalyzer.__new__(DeclineCurveAnalyzer)
        eur_oil = analyzer.calculate_eur(self.params, economic_limit, years) + self.cum_to_date

        return ForecastResult(
            dates=dates, oil_rates=oil_rates, gas_rates=gas_rates,
            cumulative_oil=cumulative_oil, cumulative_gas=cumulative_gas,
            parameters=self.params,
            eur_oil=eur_oil, eur_gas=eur_oil * gor,
            remaining_oil=eur_oil - self.cum_to_date,
            remaining_gas=(eur_oil - self.cum_to_date) * gor
        )
```

---

## TypeCurveGenerator

```python
import numpy as np
import pandas as pd
from scipy import stats


class TypeCurveGenerator:
    WATER_DEPTH_BINS = {
        'shallow': (0, 1000),
        'deep': (1000, 5000),
        'ultra_deep': (5000, 15000)
    }

    def __init__(self, wells, metadata=None):
        self.wells = wells
        self.metadata = metadata or [{} for _ in wells]
        self.normalized_wells = []
        self.normalization_factors = []
        self.bins = {}

    def normalize_wells(self, method=NormalizationMethod.PEAK, time_reference=30):
        normalized = []
        self.normalization_factors = []
        for well in self.wells:
            df = well.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            first_date = df['date'].min()
            df['days'] = (df['date'] - first_date).dt.days
            df['month'] = (df['days'] / 30.44).astype(int)

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
                ref_cum = df[df['days'] <= time_reference]['rate'].sum()
                norm_factor = ref_cum / time_reference if ref_cum > 0 else df['rate'].iloc[0]
            else:
                norm_factor = df['rate'].max()

            norm_factor = max(norm_factor, 0.1)
            df['normalized_rate'] = df['rate'] / norm_factor
            self.normalization_factors.append(norm_factor)
            normalized.append(df)

        self.normalized_wells = normalized
        return normalized

    def create_bins(self, bin_type, custom_bins=None):
        bins = {}
        if bin_type == TypeCurveBinType.WATER_DEPTH:
            bin_defs = custom_bins or self.WATER_DEPTH_BINS
            for name, (min_wd, max_wd) in bin_defs.items():
                bins[name] = TypeCurveBin(bin_type=bin_type, bin_name=name,
                                          criteria={'water_depth_ft': (min_wd, max_wd)})
        elif bin_type == TypeCurveBinType.FORMATION:
            formations = {meta.get('formation') for meta in self.metadata if 'formation' in meta}
            for f in formations:
                bins[f] = TypeCurveBin(bin_type=bin_type, bin_name=f,
                                       criteria={'formation': f})
        elif bin_type == TypeCurveBinType.VINTAGE:
            for i, well in enumerate(self.wells):
                df = well.copy()
                df['date'] = pd.to_datetime(df['date'])
                year = str(df['date'].min().year)
                if year not in bins:
                    bins[year] = TypeCurveBin(bin_type=bin_type, bin_name=year,
                                              criteria={'vintage_year': int(year)})

        for i, meta in enumerate(self.metadata):
            for name, bin_def in bins.items():
                if bin_def.matches(meta):
                    bin_def.wells.append(i)

        self.bins[bin_type] = bins
        return bins

    def generate_type_curve(self, percentiles=None, min_wells=3, well_indices=None):
        if percentiles is None:
            percentiles = [10, 50, 90]
        if not self.normalized_wells:
            self.normalize_wells()
        wells_to_use = ([self.normalized_wells[i] for i in well_indices]
                        if well_indices else self.normalized_wells)

        max_months = max(df['month'].max() for df in wells_to_use)
        monthly_rates = {m: [] for m in range(int(max_months) + 1)}
        for df in wells_to_use:
            for _, row in df.iterrows():
                month = int(row['month'])
                if month in monthly_rates:
                    monthly_rates[month].append(row['normalized_rate'])

        months, p10_rates, p50_rates, p90_rates, mean_rates, well_counts = [], [], [], [], [], []
        for month in sorted(monthly_rates.keys()):
            rates = monthly_rates[month]
            if len(rates) >= min_wells:
                months.append(month)
                p10_rates.append(np.percentile(rates, 90))   # P10 = high exceedance
                p50_rates.append(np.percentile(rates, 50))
                p90_rates.append(np.percentile(rates, 10))   # P90 = low exceedance
                mean_rates.append(np.mean(rates))
                well_counts.append(len(rates))

        return TypeCurveResult(months=months, p10_rates=p10_rates, p50_rates=p50_rates,
                               p90_rates=p90_rates, mean_rates=mean_rates,
                               well_counts=well_counts)

    def generate_bin_type_curves(self, bin_type):
        if bin_type not in self.bins:
            self.create_bins(bin_type)
        return {name: self.generate_type_curve(well_indices=bin_def.wells)
                for name, bin_def in self.bins[bin_type].items()
                if len(bin_def.wells) >= 3}

    def calculate_eur_distribution(self, economic_limit=10.0, max_years=30.0):
        eur_values = []
        for i, well in enumerate(self.normalized_wells):
            norm_factor = self.normalization_factors[i]
            actual_rates = well['normalized_rate'] * norm_factor
            well_df = pd.DataFrame({'date': well['date'], 'rate': actual_rates})
            analyzer = DeclineCurveAnalyzer(well_df)
            params, _ = analyzer.fit_best_model()
            eur_values.append(analyzer.calculate_eur(params, economic_limit, max_years))
        return {
            'P10': np.percentile(eur_values, 90),
            'P50': np.percentile(eur_values, 50),
            'P90': np.percentile(eur_values, 10),
            'mean': np.mean(eur_values),
            'std': np.std(eur_values)
        }
```

---

## ProductionReportGenerator

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import pandas as pd


class ProductionReportGenerator:
    def __init__(self, forecast: ForecastResult, historical_data: pd.DataFrame = None):
        self.forecast = forecast
        self.historical = historical_data

    def generate_report(self, output_path: Path, well_name: str = "Well") -> Path:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Production Rate Forecast', 'Cumulative Production',
                            'Decline Curve Analysis', 'Forecast Summary'),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'scatter'}, {'type': 'table'}]]
        )
        forecast_df = self.forecast.to_dataframe()

        if self.historical is not None:
            fig.add_trace(go.Scatter(x=self.historical['date'], y=self.historical['rate'],
                                     mode='markers', name='Historical',
                                     marker=dict(color='blue', size=6)), row=1, col=1)

        fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['oil_rate'],
                                 mode='lines', name='Forecast',
                                 line=dict(color='red', width=2)), row=1, col=1)

        fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['cumulative_oil'],
                                 fill='tozeroy', name='Cumulative Oil',
                                 line=dict(color='green')), row=1, col=2)

        fig.add_hline(y=self.forecast.eur_oil, line_dash='dash', line_color='orange',
                      annotation_text=f'EUR: {self.forecast.eur_oil/1e6:.2f} MMbbls',
                      row=1, col=2)

        fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['oil_rate'],
                                 mode='lines', name='Rate (log)',
                                 line=dict(color='purple')), row=2, col=1)
        fig.update_yaxes(type='log', row=2, col=1)

        params = self.forecast.parameters
        fig.add_trace(go.Table(
            header=dict(values=['Parameter', 'Value'], fill_color='paleturquoise', align='left'),
            cells=dict(values=[
                ['Initial Rate (qi)', 'Decline Rate (Di)', 'b-factor', 'Decline Type',
                 'EUR Oil', 'EUR Gas', 'Remaining Oil', 'Remaining Gas'],
                [f'{params.qi:.1f} bbl/d', f'{params.di*100:.1f} %/year', f'{params.b:.3f}',
                 params.decline_type.value, f'{self.forecast.eur_oil/1e6:.2f} MMbbl',
                 f'{self.forecast.eur_gas/1e6:.2f} MMmcf', f'{self.forecast.remaining_oil/1e6:.2f} MMbbl',
                 f'{self.forecast.remaining_gas/1e6:.2f} MMmcf']
            ], fill_color='lavender', align='left')
        ), row=2, col=2)

        fig.update_layout(height=800, title_text=f'{well_name} - Production Forecast', showlegend=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))
        return output_path
```

---

## YAML Configuration Templates

### Single Well Forecast (`config/production_forecast.yaml`)

```yaml
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
  auto_fit: true
  b_range: [0.3, 1.2]

forecast:
  start_date: "2025-01-01"
  years: 30
  economic_limit: 25
  interval: "monthly"

gas:
  gor: 2.5
  gor_trend: "constant"

output:
  csv_path: "data/results/well_a1_forecast.csv"
  report_path: "reports/well_a1_forecast.html"
```

### Type Curve (`config/type_curve.yaml`)

```yaml
metadata:
  field: "Lower Tertiary"
  formation: "Wilcox"

wells:
  source: "directory"
  path: "data/production/lower_tertiary/"
  pattern: "*.csv"
  metadata_file: "data/production/well_metadata.csv"

normalization:
  method: "30_day_ip"
  time_reference: 30

type_curve:
  percentiles: [10, 50, 90]
  min_wells_per_month: 5
  binning:
    enabled: true
    bin_type: "water_depth"
    custom_bins:
      shallow: [0, 1500]
      deep: [1500, 5000]
      ultra_deep: [5000, 15000]

fit:
  model: "hyperbolic"
  b_range: [0.5, 1.5]
  d_min: 0.06

eur:
  economic_limit: 25
  max_years: 40
  calculate_distribution: true

output:
  type_curve_csv: "data/results/lower_tertiary_type_curve.csv"
  report_path: "reports/lower_tertiary_type_curves.html"
```

### Multi-Field Comparison (`config/type_curve_comparison.yaml`)

```yaml
metadata:
  project: "GOM Deepwater Comparison"

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
  compare_eur: true
  compare_decline_rates: true
  compare_b_factors: true

output:
  report_path: "reports/field_type_curve_comparison.html"
  csv_export: "data/results/type_curve_comparison.csv"
```

---

## Full CLI Reference

```bash
# Fit decline curve
python -m production_forecaster fit \
    --data data/production/well_history.csv --model hyperbolic

# Fit unconventional
python -m production_forecaster fit \
    --data data/production/shale_well.csv --model duong \
    --output reports/duong_fit.html

# Forecast from config
python -m production_forecaster forecast \
    --config config/production_forecast.yaml --output reports/forecast.html

# Type curves with binning
python -m production_forecaster type-curve \
    --wells data/production/*.csv \
    --percentiles 10 50 90 \
    --normalize 30_day_ip \
    --bin-by water_depth \
    --output reports/type_curves.html

# Type curves from config
python -m production_forecaster type-curve \
    --config config/type_curve.yaml

# EUR with distribution
python -m production_forecaster eur \
    --qi 5000 --di 0.35 --b 0.8 --limit 25 --distribution

# Scale type curve
python -m production_forecaster scale-type-curve \
    --type-curve data/results/lower_tertiary_type_curve.csv \
    --target-ip 8000 --percentile P50 \
    --output reports/scaled_forecast.html

# Compare wells vs type curve
python -m production_forecaster compare \
    --wells well1.csv well2.csv well3.csv \
    --type-curve data/results/field_type_curve.csv \
    --normalize 30_day_ip --output reports/comparison.html

# Multi-field comparison
python -m production_forecaster compare-fields \
    --config config/type_curve_comparison.yaml

# Validate with holdout
python -m production_forecaster validate \
    --data data/production/well_history.csv --model hyperbolic --holdout 0.2
```

---

## Usage Examples

### Example 1: Fit and Forecast Single Well

```python
from production_forecaster import DeclineCurveAnalyzer, ProductionForecaster, ProductionReportGenerator
import pandas as pd
from pathlib import Path

historical = pd.read_csv('data/production/well_a1.csv')

analyzer = DeclineCurveAnalyzer(historical)
params, model_type = analyzer.fit_best_model()
print(f"Best fit: {model_type} | qi={params.qi:.1f} bbl/d | Di={params.di*100:.1f}%/yr | b={params.b:.3f}")

forecaster = ProductionForecaster(params, cumulative_to_date=historical['cumulative'].iloc[-1])
forecast = forecaster.forecast(years=30, economic_limit=25)
print(f"EUR: {forecast.eur_oil/1e6:.2f} MMbbl | Remaining: {forecast.remaining_oil/1e6:.2f} MMbbl")

reporter = ProductionReportGenerator(forecast, historical)
reporter.generate_report(Path('reports/well_a1_forecast.html'), well_name='Well A-1')
```

### Example 2: Type Curves with Binning

```python
from production_forecaster import TypeCurveGenerator, NormalizationMethod, TypeCurveBinType
import glob, pandas as pd

wells = [pd.read_csv(f) for f in glob.glob('data/production/field_x/*.csv')]
metadata = pd.read_csv('data/production/well_metadata.csv').to_dict('records')

generator = TypeCurveGenerator(wells, metadata=metadata)
generator.normalize_wells(method=NormalizationMethod.IP_30)
generator.create_bins(TypeCurveBinType.WATER_DEPTH)

bin_results = generator.generate_bin_type_curves(TypeCurveBinType.WATER_DEPTH)
for bin_name, result in bin_results.items():
    print(f"{bin_name}: {result.well_counts[0]} wells")

p50_params, metrics = generator.fit_type_curve(percentile=50)
eur_dist = generator.calculate_eur_distribution(economic_limit=25)
print(f"P10: {eur_dist['P10']/1e6:.2f} | P50: {eur_dist['P50']/1e6:.2f} | P90: {eur_dist['P90']/1e6:.2f} MMbbl")
```

### Example 3: Unconventional Decline Models

```python
from production_forecaster import DeclineCurveAnalyzer
import pandas as pd

df = pd.read_csv('data/production/shale_well.csv')
analyzer = DeclineCurveAnalyzer(df)

duong_params = analyzer.fit_duong()
print(f"Duong: q1={duong_params.qi:.1f}, a={duong_params.a:.3f}, m={duong_params.m:.3f}")

se_params = analyzer.fit_stretched_exponential()
print(f"Stretched Exp: qi={se_params.qi:.1f}, tau={se_params.tau:.3f}, n={se_params.n:.3f}")

best_params, best_model = analyzer.fit_best_model(include_unconventional=True)
metrics = analyzer.calculate_validation_metrics(best_params)
print(f"Best: {best_model} | R²={metrics['r_squared']:.4f} | MAPE={metrics['mape']:.1f}%")
```

### Example 4: Scale Type Curve for New Well

```python
from production_forecaster import TypeCurveGenerator, ProductionForecaster, DeclineParameters
from datetime import date
import glob, pandas as pd

wells = [pd.read_csv(f) for f in glob.glob('data/production/lower_tertiary/*.csv')]
generator = TypeCurveGenerator(wells)
generator.normalize_wells()
p50_params, _ = generator.fit_type_curve(percentile=50)

target_ip = 8500
scaled_params = DeclineParameters(qi=p50_params.qi * target_ip, di=p50_params.di, b=p50_params.b)

forecaster = ProductionForecaster(scaled_params, start_date=date(2026, 3, 1))
forecast = forecaster.forecast(years=30, economic_limit=25, gor=2.0)
print(f"EUR: {forecast.eur_oil/1e6:.2f} MMbbl | Gas: {forecast.eur_gas/1e9:.2f} Bcf")
```

### Example 5: Multi-Well Comparison

```python
from production_forecaster import DeclineCurveAnalyzer, TypeCurveGenerator, NormalizationMethod
import pandas as pd, glob
import plotly.graph_objects as go

ref_wells = [pd.read_csv(f) for f in glob.glob('data/production/reference/*.csv')]
generator = TypeCurveGenerator(ref_wells)
generator.normalize_wells(method=NormalizationMethod.IP_30)
type_curve = generator.generate_type_curve()

results = []
for well_file in ['well_a.csv', 'well_b.csv', 'well_c.csv']:
    df = pd.read_csv(f'data/production/{well_file}')
    analyzer = DeclineCurveAnalyzer(df)
    params, model = analyzer.fit_best_model()
    metrics = analyzer.calculate_validation_metrics(params)
    results.append({
        'well': well_file.replace('.csv', ''),
        'di_pct': params.di * 100, 'b': params.b, 'model': model,
        'r_squared': metrics['r_squared'],
        'eur_mmbbl': analyzer.calculate_eur(params, 25, 30) / 1e6
    })

import pandas as pd
print(pd.DataFrame(results).to_string(index=False))
```

### Example 6: Multi-Field Type Curve Comparison

```python
from production_forecaster import TypeCurveGenerator, NormalizationMethod
import pandas as pd, glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    params, metrics = generator.fit_type_curve(percentile=50)
    eur_dist = generator.calculate_eur_distribution(economic_limit=25)
    field_results[field_name] = {'type_curve': tc, 'params': params,
                                  'metrics': metrics, 'eur': eur_dist, 'well_count': len(wells)}

print(f"{'Field':<20} {'Wells':<8} {'Di %/yr':<10} {'b':<8} {'EUR P50 MMbbl':<15} {'R²'}")
for field, data in field_results.items():
    p = data['params']
    print(f"{field:<20} {data['well_count']:<8} {p.di*100:<10.1f} {p.b:<8.3f} "
          f"{data['eur']['P50']/1e6:<15.2f} {data['metrics']['r_squared']:.4f}")
```
