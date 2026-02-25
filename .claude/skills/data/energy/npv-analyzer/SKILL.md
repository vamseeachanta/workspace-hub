---
name: npv-analyzer
<<<<<<< HEAD
description: Perform NPV analysis and economic evaluation for oil & gas assets. Use for cash flow modeling, price scenario analysis, Monte Carlo simulation, P10/P50/P90 probabilistic analysis, working interest calculations, and financial metrics (IRR, payback, NPV) for field development projects.
=======
description: Perform NPV analysis and economic evaluation for oil & gas assets. Use for cash flow modeling, price scenario analysis, working interest calculations, and financial metrics (IRR, payback, NPV) for field development projects.
>>>>>>> origin/main
capabilities: []
requires: []
see_also: []
---

# NPV Analyzer

<<<<<<< HEAD
Perform comprehensive Net Present Value (NPV) analysis and economic evaluation for oil & gas development projects, including cash flow modeling, price scenarios, Monte Carlo simulation for probabilistic analysis, and financial metrics.
=======
Perform comprehensive Net Present Value (NPV) analysis and economic evaluation for oil & gas development projects, including cash flow modeling, price scenarios, and financial metrics.
>>>>>>> origin/main

## When to Use

- Calculating NPV for field development projects
- Modeling cash flows with production forecasts
- Running oil/gas price scenario analysis (low/mid/high)
<<<<<<< HEAD
- **Monte Carlo simulation for P10/P50/P90 NPV estimates**
- **Probabilistic risk analysis with multiple input distributions**
- Applying working interest and royalty calculations
- Evaluating different development types (subsea, platform, FPSO)
- Computing IRR, payback period, and profitability index
- **Calculating Value at Risk (VaR) and Expected Shortfall**
=======
- Applying working interest and royalty calculations
- Evaluating different development types (subsea, platform, FPSO)
- Computing IRR, payback period, and profitability index
>>>>>>> origin/main
- Comparing economic outcomes across multiple scenarios

## Core Pattern

```
Production Forecast → Price Assumptions → Cash Flow Model → Discount → Metrics
```

## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Tuple
from enum import Enum
import numpy as np
import pandas as pd

class DevelopmentType(Enum):
    """Field development concepts."""
    SUBSEA_TIEBACK = "subsea_tieback"
    FIXED_PLATFORM = "fixed_platform"
    FPSO = "fpso"
    SPAR = "spar"
    TLP = "tlp"
    SEMI = "semi_submersible"

class PriceScenario(Enum):
    """Oil/gas price scenarios."""
    LOW = "low"
    MID = "mid"
    HIGH = "high"
    STRIP = "strip"  # Forward curve prices
    CUSTOM = "custom"

@dataclass
class PriceAssumptions:
    """Oil and gas price assumptions."""
    scenario: PriceScenario = PriceScenario.MID
    oil_price_usd_bbl: float = 70.0
    gas_price_usd_mmbtu: float = 3.50
    ngl_price_usd_bbl: float = 35.0

    # Price escalation
    annual_escalation_pct: float = 2.0

    # Price deck for forward curve
    price_deck: Optional[Dict[int, Tuple[float, float]]] = None  # year: (oil, gas)

    def get_prices(self, year: int, base_year: int = None) -> Tuple[float, float]:
        """Get escalated prices for a specific year."""
        if self.price_deck and year in self.price_deck:
            return self.price_deck[year]

        base_year = base_year or date.today().year
        years_forward = year - base_year

        escalation = (1 + self.annual_escalation_pct / 100) ** years_forward
        oil_price = self.oil_price_usd_bbl * escalation
        gas_price = self.gas_price_usd_mmbtu * escalation

        return oil_price, gas_price

@dataclass
class FiscalTerms:
    """Fiscal and ownership terms."""
    working_interest: float = 1.0  # Fraction (0-1)
    net_revenue_interest: float = 0.875  # After royalty
    royalty_rate: float = 0.125  # 12.5% federal royalty
    state_severance_tax: float = 0.0  # Varies by state
    federal_income_tax: float = 0.21  # Corporate rate
    ad_valorem_tax: float = 0.0

    # Cost recovery (for PSC contracts)
    cost_recovery_limit: float = 1.0  # 100% for typical US
    profit_oil_share: float = 1.0  # 100% for typical US

    def net_revenue_factor(self) -> float:
        """Calculate combined net revenue factor."""
        return self.working_interest * self.net_revenue_interest

@dataclass
class CapexSchedule:
    """Capital expenditure schedule."""
    drilling_per_well: float = 0.0  # USD millions
    completion_per_well: float = 0.0
    facilities: float = 0.0
    subsea_equipment: float = 0.0
    pipeline: float = 0.0
    other_capex: float = 0.0

    # Timing (years from sanction)
    schedule: Dict[int, float] = field(default_factory=dict)  # year: capex

    @property
    def total_capex(self) -> float:
        """Total capital expenditure."""
        return (self.drilling_per_well + self.completion_per_well +
                self.facilities + self.subsea_equipment +
                self.pipeline + self.other_capex)

@dataclass
class OpexAssumptions:
    """Operating expenditure assumptions."""
    fixed_opex_usd_year: float = 0.0  # Annual fixed costs
    variable_opex_usd_boe: float = 0.0  # Per BOE
    workover_budget: float = 0.0  # Annual workover allowance
    insurance: float = 0.0
    g_and_a: float = 0.0  # General & administrative

    # Abandonment
    abandonment_cost: float = 0.0
    abandonment_year: Optional[int] = None

@dataclass
class ProductionForecast:
    """Production forecast by year."""
    year: int
    oil_mbbls: float = 0.0  # Thousand barrels
    gas_mmcf: float = 0.0  # Million cubic feet
    ngl_mbbls: float = 0.0
    water_mbbls: float = 0.0

    @property
    def boe(self) -> float:
        """Barrels of oil equivalent (6:1 gas)."""
        return self.oil_mbbls + self.ngl_mbbls + (self.gas_mmcf / 6.0)

    @property
    def gas_mmbtu(self) -> float:
        """Gas in MMBTU (assuming 1 MCF = 1 MMBTU)."""
        return self.gas_mmcf * 1000  # Convert MMCF to MMBTU

@dataclass
class CashFlowYear:
    """Annual cash flow calculation."""
    year: int

    # Revenue
    gross_oil_revenue: float = 0.0
    gross_gas_revenue: float = 0.0
    gross_ngl_revenue: float = 0.0
    total_gross_revenue: float = 0.0
    net_revenue: float = 0.0

    # Costs
    capex: float = 0.0
    opex: float = 0.0
    severance_tax: float = 0.0
    ad_valorem_tax: float = 0.0
    abandonment: float = 0.0

    # Taxes
    taxable_income: float = 0.0
    income_tax: float = 0.0

    # Cash flows
    before_tax_cash_flow: float = 0.0
    after_tax_cash_flow: float = 0.0
    cumulative_cash_flow: float = 0.0
    discounted_cash_flow: float = 0.0
```

### NPV Calculator

```python
from typing import List, Dict, Optional
import numpy as np
import numpy_financial as npf

class NPVCalculator:
    """
    Calculate NPV and related economic metrics for oil & gas projects.
    """

    def __init__(self,
                 production: List[ProductionForecast],
                 prices: PriceAssumptions,
                 fiscal: FiscalTerms,
                 capex: CapexSchedule,
                 opex: OpexAssumptions,
                 discount_rate: float = 0.10):
        """
        Initialize NPV calculator.

        Args:
            production: List of annual production forecasts
            prices: Price assumptions
            fiscal: Fiscal and ownership terms
            capex: Capital expenditure schedule
            opex: Operating expenditure assumptions
            discount_rate: Annual discount rate (default 10%)
        """
        self.production = sorted(production, key=lambda x: x.year)
        self.prices = prices
        self.fiscal = fiscal
        self.capex = capex
        self.opex = opex
        self.discount_rate = discount_rate

        self._cash_flows: Optional[List[CashFlowYear]] = None
        self._base_year: Optional[int] = None

    @property
    def base_year(self) -> int:
        """Get or set base year for discounting."""
        if self._base_year is None:
            self._base_year = min(p.year for p in self.production)
        return self._base_year

    @base_year.setter
    def base_year(self, value: int):
        self._base_year = value
        self._cash_flows = None  # Reset calculations

    def calculate_cash_flows(self) -> List[CashFlowYear]:
        """Calculate annual cash flows."""
        if self._cash_flows is not None:
            return self._cash_flows

        cash_flows = []
        cumulative = 0.0

        for prod in self.production:
            cf = CashFlowYear(year=prod.year)

            # Get prices for year
            oil_price, gas_price = self.prices.get_prices(prod.year, self.base_year)
            ngl_price = self.prices.ngl_price_usd_bbl * (
                (1 + self.prices.annual_escalation_pct / 100) **
                (prod.year - self.base_year)
            )

            # Gross revenue (in thousands USD, since production in Mbbls/MMCF)
            cf.gross_oil_revenue = prod.oil_mbbls * oil_price * 1000
            cf.gross_gas_revenue = prod.gas_mmbtu * gas_price / 1000  # MMBTU to $ thousands
            cf.gross_ngl_revenue = prod.ngl_mbbls * ngl_price * 1000
            cf.total_gross_revenue = (cf.gross_oil_revenue +
                                     cf.gross_gas_revenue +
                                     cf.gross_ngl_revenue)

            # Net revenue (apply WI and NRI)
            cf.net_revenue = cf.total_gross_revenue * self.fiscal.net_revenue_factor()

            # Capital expenditure
            cf.capex = self.capex.schedule.get(prod.year, 0.0) * 1e6  # Convert to $

            # Operating expenditure
            cf.opex = (
                self.opex.fixed_opex_usd_year +
                self.opex.variable_opex_usd_boe * prod.boe * 1000 +
                self.opex.workover_budget +
                self.opex.insurance +
                self.opex.g_and_a
            )

            # Abandonment
            if (self.opex.abandonment_year and
                prod.year == self.opex.abandonment_year):
                cf.abandonment = self.opex.abandonment_cost

            # Severance tax (on gross revenue before NRI)
            cf.severance_tax = (cf.total_gross_revenue *
                               self.fiscal.working_interest *
                               self.fiscal.state_severance_tax)

            # Ad valorem tax
            cf.ad_valorem_tax = (cf.total_gross_revenue *
                                self.fiscal.working_interest *
                                self.fiscal.ad_valorem_tax)

            # Before tax cash flow
            cf.before_tax_cash_flow = (cf.net_revenue -
                                       cf.capex -
                                       cf.opex -
                                       cf.severance_tax -
                                       cf.ad_valorem_tax -
                                       cf.abandonment)

            # Taxable income (simplified - no DD&A or intangible drilling)
            cf.taxable_income = max(0, cf.before_tax_cash_flow)
            cf.income_tax = cf.taxable_income * self.fiscal.federal_income_tax

            # After tax cash flow
            cf.after_tax_cash_flow = cf.before_tax_cash_flow - cf.income_tax

            # Cumulative cash flow
            cumulative += cf.after_tax_cash_flow
            cf.cumulative_cash_flow = cumulative

            # Discounted cash flow
            years_from_base = prod.year - self.base_year
            discount_factor = 1 / (1 + self.discount_rate) ** years_from_base
            cf.discounted_cash_flow = cf.after_tax_cash_flow * discount_factor

            cash_flows.append(cf)

        self._cash_flows = cash_flows
        return cash_flows

    def npv(self) -> float:
        """Calculate Net Present Value."""
        cash_flows = self.calculate_cash_flows()
        return sum(cf.discounted_cash_flow for cf in cash_flows)

    def irr(self) -> Optional[float]:
        """Calculate Internal Rate of Return."""
        cash_flows = self.calculate_cash_flows()
        cf_values = [cf.after_tax_cash_flow for cf in cash_flows]

        try:
            return npf.irr(cf_values)
        except:
            return None

    def payback_period(self) -> Optional[float]:
        """Calculate payback period in years."""
        cash_flows = self.calculate_cash_flows()

        for i, cf in enumerate(cash_flows):
            if cf.cumulative_cash_flow >= 0:
                if i == 0:
                    return 0.0

                # Interpolate
                prev_cf = cash_flows[i - 1]
                fraction = (-prev_cf.cumulative_cash_flow /
                           (cf.cumulative_cash_flow - prev_cf.cumulative_cash_flow))
                return (cf.year - cash_flows[0].year - 1) + fraction

        return None  # Never pays back

    def discounted_payback(self) -> Optional[float]:
        """Calculate discounted payback period."""
        cash_flows = self.calculate_cash_flows()
        cumulative_dcf = 0.0

        for i, cf in enumerate(cash_flows):
            cumulative_dcf += cf.discounted_cash_flow

            if cumulative_dcf >= 0:
                if i == 0:
                    return 0.0

                prev_cumulative = cumulative_dcf - cf.discounted_cash_flow
                fraction = (-prev_cumulative / cf.discounted_cash_flow)
                return (cf.year - cash_flows[0].year - 1) + fraction

        return None

    def profitability_index(self) -> float:
        """Calculate profitability index (PI = NPV / Investment + 1)."""
        cash_flows = self.calculate_cash_flows()
        total_investment = sum(cf.capex for cf in cash_flows)

        if total_investment == 0:
            return float('inf')

        return (self.npv() / total_investment) + 1

    def investment_efficiency(self) -> float:
        """Calculate investment efficiency (NPV per $ invested)."""
        cash_flows = self.calculate_cash_flows()
        total_investment = sum(cf.capex for cf in cash_flows)

        if total_investment == 0:
            return float('inf')

        return self.npv() / total_investment

    def breakeven_price(self, commodity: str = 'oil',
                        tolerance: float = 0.01) -> Optional[float]:
        """
        Calculate breakeven price for NPV = 0.

        Args:
            commodity: 'oil' or 'gas'
            tolerance: NPV tolerance for convergence
        """
        from scipy.optimize import brentq

        original_prices = self.prices

        def npv_at_price(price):
            if commodity == 'oil':
                self.prices = PriceAssumptions(
                    oil_price_usd_bbl=price,
                    gas_price_usd_mmbtu=original_prices.gas_price_usd_mmbtu
                )
            else:
                self.prices = PriceAssumptions(
                    oil_price_usd_bbl=original_prices.oil_price_usd_bbl,
                    gas_price_usd_mmbtu=price
                )
            self._cash_flows = None
            return self.npv()

        try:
            # Search between $10 and $200 for oil, $1 and $20 for gas
            if commodity == 'oil':
                breakeven = brentq(npv_at_price, 10, 200)
            else:
                breakeven = brentq(npv_at_price, 1, 20)
        except:
            breakeven = None
        finally:
            self.prices = original_prices
            self._cash_flows = None

        return breakeven

    def to_dataframe(self) -> pd.DataFrame:
        """Export cash flows to DataFrame."""
        cash_flows = self.calculate_cash_flows()

        data = []
        for cf in cash_flows:
            data.append({
                'year': cf.year,
                'gross_revenue': cf.total_gross_revenue,
                'net_revenue': cf.net_revenue,
                'capex': cf.capex,
                'opex': cf.opex,
                'taxes': cf.severance_tax + cf.ad_valorem_tax + cf.income_tax,
                'btcf': cf.before_tax_cash_flow,
                'atcf': cf.after_tax_cash_flow,
                'cumulative': cf.cumulative_cash_flow,
                'dcf': cf.discounted_cash_flow
            })

        return pd.DataFrame(data)

    def summary(self) -> Dict:
        """Generate summary of economic metrics."""
        cash_flows = self.calculate_cash_flows()

        return {
            'npv_mm': self.npv() / 1e6,
            'irr_pct': (self.irr() or 0) * 100,
            'payback_years': self.payback_period(),
            'discounted_payback_years': self.discounted_payback(),
            'profitability_index': self.profitability_index(),
            'investment_efficiency': self.investment_efficiency(),
            'total_capex_mm': sum(cf.capex for cf in cash_flows) / 1e6,
            'total_opex_mm': sum(cf.opex for cf in cash_flows) / 1e6,
            'total_revenue_mm': sum(cf.net_revenue for cf in cash_flows) / 1e6,
            'cumulative_production_mmboe': sum(p.boe for p in self.production) / 1000,
            'discount_rate_pct': self.discount_rate * 100
        }
```

### Scenario Analyzer

```python
from typing import List, Dict
from dataclasses import replace
import pandas as pd

class ScenarioAnalyzer:
    """
    Run multiple NPV scenarios with different price assumptions.
    """

    # Standard price scenarios
    PRICE_SCENARIOS = {
        PriceScenario.LOW: PriceAssumptions(
            scenario=PriceScenario.LOW,
            oil_price_usd_bbl=50.0,
            gas_price_usd_mmbtu=2.50
        ),
        PriceScenario.MID: PriceAssumptions(
            scenario=PriceScenario.MID,
            oil_price_usd_bbl=70.0,
            gas_price_usd_mmbtu=3.50
        ),
        PriceScenario.HIGH: PriceAssumptions(
            scenario=PriceScenario.HIGH,
            oil_price_usd_bbl=90.0,
            gas_price_usd_mmbtu=5.00
        )
    }

    def __init__(self,
                 production: List[ProductionForecast],
                 fiscal: FiscalTerms,
                 capex: CapexSchedule,
                 opex: OpexAssumptions,
                 discount_rate: float = 0.10):
        """Initialize scenario analyzer."""
        self.production = production
        self.fiscal = fiscal
        self.capex = capex
        self.opex = opex
        self.discount_rate = discount_rate

    def run_price_scenarios(self) -> pd.DataFrame:
        """Run standard price scenarios and compare results."""
        results = []

        for scenario, prices in self.PRICE_SCENARIOS.items():
            calc = NPVCalculator(
                production=self.production,
                prices=prices,
                fiscal=self.fiscal,
                capex=self.capex,
                opex=self.opex,
                discount_rate=self.discount_rate
            )

            summary = calc.summary()
            summary['scenario'] = scenario.value
            summary['oil_price'] = prices.oil_price_usd_bbl
            summary['gas_price'] = prices.gas_price_usd_mmbtu
            results.append(summary)

        return pd.DataFrame(results)

    def sensitivity_analysis(self,
                            base_prices: PriceAssumptions,
                            variable: str,
                            range_pct: float = 0.30,
                            steps: int = 11) -> pd.DataFrame:
        """
        Run sensitivity analysis on a single variable.

        Args:
            base_prices: Base case prices
            variable: Variable to vary ('oil_price', 'gas_price', 'capex', 'opex', 'discount_rate')
            range_pct: Range as percentage of base value
            steps: Number of steps
        """
        results = []

        # Get base value
        if variable == 'oil_price':
            base_value = base_prices.oil_price_usd_bbl
        elif variable == 'gas_price':
            base_value = base_prices.gas_price_usd_mmbtu
        elif variable == 'capex':
            base_value = 1.0  # Multiplier
        elif variable == 'opex':
            base_value = 1.0  # Multiplier
        elif variable == 'discount_rate':
            base_value = self.discount_rate
        else:
            raise ValueError(f"Unknown variable: {variable}")

        # Generate range
        min_val = base_value * (1 - range_pct)
        max_val = base_value * (1 + range_pct)
        values = np.linspace(min_val, max_val, steps)

        for val in values:
            # Modify parameter
            if variable == 'oil_price':
                prices = replace(base_prices, oil_price_usd_bbl=val)
                capex = self.capex
                opex = self.opex
                discount = self.discount_rate
            elif variable == 'gas_price':
                prices = replace(base_prices, gas_price_usd_mmbtu=val)
                capex = self.capex
                opex = self.opex
                discount = self.discount_rate
            elif variable == 'capex':
                prices = base_prices
                # Scale capex schedule
                capex = replace(self.capex,
                               schedule={y: c * val for y, c in self.capex.schedule.items()})
                opex = self.opex
                discount = self.discount_rate
            elif variable == 'opex':
                prices = base_prices
                capex = self.capex
                opex = replace(self.opex,
                              fixed_opex_usd_year=self.opex.fixed_opex_usd_year * val,
                              variable_opex_usd_boe=self.opex.variable_opex_usd_boe * val)
                discount = self.discount_rate
            elif variable == 'discount_rate':
                prices = base_prices
                capex = self.capex
                opex = self.opex
                discount = val

            # Calculate NPV
            calc = NPVCalculator(
                production=self.production,
                prices=prices,
                fiscal=self.fiscal,
                capex=capex,
                opex=opex,
                discount_rate=discount
            )

            results.append({
                'variable': variable,
                'value': val,
                'pct_change': (val - base_value) / base_value * 100,
                'npv_mm': calc.npv() / 1e6,
                'irr_pct': (calc.irr() or 0) * 100
            })

        return pd.DataFrame(results)

    def tornado_chart_data(self, base_prices: PriceAssumptions,
                          range_pct: float = 0.20) -> pd.DataFrame:
        """Generate data for tornado sensitivity chart."""
        variables = ['oil_price', 'gas_price', 'capex', 'opex', 'discount_rate']
        results = []

        # Calculate base case
        base_calc = NPVCalculator(
            production=self.production,
            prices=base_prices,
            fiscal=self.fiscal,
            capex=self.capex,
            opex=self.opex,
            discount_rate=self.discount_rate
        )
        base_npv = base_calc.npv() / 1e6

        for var in variables:
            sensitivity = self.sensitivity_analysis(base_prices, var, range_pct, steps=3)
            low = sensitivity.iloc[0]['npv_mm']
            high = sensitivity.iloc[-1]['npv_mm']

            results.append({
                'variable': var,
                'low_npv': low,
                'high_npv': high,
                'base_npv': base_npv,
                'range': abs(high - low)
            })

        return pd.DataFrame(results).sort_values('range', ascending=False)
```

<<<<<<< HEAD
### Monte Carlo Simulator

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum
import numpy as np
import pandas as pd

class DistributionType(Enum):
    """Probability distribution types for Monte Carlo inputs."""
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    TRIANGULAR = "triangular"
    UNIFORM = "uniform"
    PERT = "pert"

@dataclass
class DistributionParams:
    """Parameters for probability distributions."""
    distribution: DistributionType = DistributionType.TRIANGULAR
    min_value: float = 0.0
    mode_value: float = 0.0  # Most likely (for triangular/PERT)
    max_value: float = 0.0
    mean: Optional[float] = None  # For normal/lognormal
    std_dev: Optional[float] = None

    def sample(self, n_samples: int, rng: np.random.Generator = None) -> np.ndarray:
        """Generate random samples from the distribution."""
        if rng is None:
            rng = np.random.default_rng()

        if self.distribution == DistributionType.UNIFORM:
            return rng.uniform(self.min_value, self.max_value, n_samples)

        elif self.distribution == DistributionType.TRIANGULAR:
            return rng.triangular(self.min_value, self.mode_value, self.max_value, n_samples)

        elif self.distribution == DistributionType.NORMAL:
            mean = self.mean or self.mode_value
            std = self.std_dev or (self.max_value - self.min_value) / 6
            samples = rng.normal(mean, std, n_samples)
            return np.clip(samples, self.min_value, self.max_value)

        elif self.distribution == DistributionType.LOGNORMAL:
            mean = self.mean or self.mode_value
            std = self.std_dev or 0.2
            samples = rng.lognormal(np.log(mean), std, n_samples)
            return np.clip(samples, self.min_value, self.max_value)

        elif self.distribution == DistributionType.PERT:
            # PERT uses Beta distribution with shape parameters
            alpha = 1 + 4 * (self.mode_value - self.min_value) / (self.max_value - self.min_value)
            beta = 1 + 4 * (self.max_value - self.mode_value) / (self.max_value - self.min_value)
            samples = rng.beta(alpha, beta, n_samples)
            return self.min_value + samples * (self.max_value - self.min_value)

        raise ValueError(f"Unknown distribution: {self.distribution}")

@dataclass
class MonteCarloConfig:
    """Configuration for Monte Carlo simulation."""
    n_iterations: int = 1000
    random_seed: Optional[int] = None

    # Price distributions
    oil_price: Optional[DistributionParams] = None
    gas_price: Optional[DistributionParams] = None

    # Cost multiplier distributions (1.0 = base case)
    capex_multiplier: Optional[DistributionParams] = None
    opex_multiplier: Optional[DistributionParams] = None

    # Production multiplier distribution (1.0 = base case)
    production_multiplier: Optional[DistributionParams] = None

    # Discount rate distribution
    discount_rate: Optional[DistributionParams] = None

    # Correlation matrix (optional, for correlated variables)
    correlations: Optional[Dict[str, Dict[str, float]]] = None

@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation."""
    npv_values: np.ndarray
    irr_values: np.ndarray
    payback_values: np.ndarray

    # Percentiles
    p10_npv: float = 0.0  # 10th percentile (pessimistic)
    p50_npv: float = 0.0  # 50th percentile (median)
    p90_npv: float = 0.0  # 90th percentile (optimistic)

    p10_irr: float = 0.0
    p50_irr: float = 0.0
    p90_irr: float = 0.0

    # Statistics
    mean_npv: float = 0.0
    std_npv: float = 0.0
    prob_positive_npv: float = 0.0

    # Input samples (for correlation analysis)
    input_samples: Optional[pd.DataFrame] = None

    def summary(self) -> Dict:
        """Generate summary statistics."""
        return {
            'mean_npv_mm': self.mean_npv / 1e6,
            'std_npv_mm': self.std_npv / 1e6,
            'p10_npv_mm': self.p10_npv / 1e6,
            'p50_npv_mm': self.p50_npv / 1e6,
            'p90_npv_mm': self.p90_npv / 1e6,
            'p10_irr_pct': self.p10_irr * 100,
            'p50_irr_pct': self.p50_irr * 100,
            'p90_irr_pct': self.p90_irr * 100,
            'prob_positive_npv_pct': self.prob_positive_npv * 100,
            'n_iterations': len(self.npv_values)
        }

class MonteCarloSimulator:
    """
    Run Monte Carlo simulations for probabilistic NPV analysis.

    Supports:
    - Multiple probability distributions (normal, triangular, PERT, uniform, lognormal)
    - Correlated input variables
    - P10/P50/P90 output generation
    - Risk analysis and probability of success
    """

    def __init__(self,
                 production: List[ProductionForecast],
                 base_prices: PriceAssumptions,
                 fiscal: FiscalTerms,
                 capex: CapexSchedule,
                 opex: OpexAssumptions,
                 base_discount_rate: float = 0.10):
        """
        Initialize Monte Carlo simulator.

        Args:
            production: Base case production forecast
            base_prices: Base case price assumptions
            fiscal: Fiscal terms (fixed)
            capex: Base case capital expenditure
            opex: Base case operating expenditure
            base_discount_rate: Base case discount rate
        """
        self.production = production
        self.base_prices = base_prices
        self.fiscal = fiscal
        self.capex = capex
        self.opex = opex
        self.base_discount_rate = base_discount_rate

    def run_simulation(self, config: MonteCarloConfig) -> MonteCarloResult:
        """
        Run Monte Carlo simulation.

        Args:
            config: Simulation configuration with distributions

        Returns:
            MonteCarloResult with NPV distribution and statistics
        """
        rng = np.random.default_rng(config.random_seed)
        n = config.n_iterations

        # Generate input samples
        samples = self._generate_samples(config, n, rng)

        # Run iterations
        npv_values = np.zeros(n)
        irr_values = np.zeros(n)
        payback_values = np.zeros(n)

        for i in range(n):
            # Build modified inputs for this iteration
            prices = self._modify_prices(samples, i)
            modified_capex = self._modify_capex(samples, i)
            modified_opex = self._modify_opex(samples, i)
            modified_production = self._modify_production(samples, i)
            discount = samples.get('discount_rate', [self.base_discount_rate] * n)[i]

            # Calculate NPV for this iteration
            calc = NPVCalculator(
                production=modified_production,
                prices=prices,
                fiscal=self.fiscal,
                capex=modified_capex,
                opex=modified_opex,
                discount_rate=discount
            )

            npv_values[i] = calc.npv()
            irr_values[i] = calc.irr() or 0.0
            payback_values[i] = calc.payback_period() or float('inf')

        # Calculate statistics
        result = MonteCarloResult(
            npv_values=npv_values,
            irr_values=irr_values,
            payback_values=payback_values,
            p10_npv=np.percentile(npv_values, 10),
            p50_npv=np.percentile(npv_values, 50),
            p90_npv=np.percentile(npv_values, 90),
            p10_irr=np.percentile(irr_values, 10),
            p50_irr=np.percentile(irr_values, 50),
            p90_irr=np.percentile(irr_values, 90),
            mean_npv=np.mean(npv_values),
            std_npv=np.std(npv_values),
            prob_positive_npv=np.sum(npv_values > 0) / n,
            input_samples=pd.DataFrame(samples)
        )

        return result

    def _generate_samples(self, config: MonteCarloConfig, n: int,
                         rng: np.random.Generator) -> Dict[str, np.ndarray]:
        """Generate random samples for all input variables."""
        samples = {}

        if config.oil_price:
            samples['oil_price'] = config.oil_price.sample(n, rng)
        else:
            samples['oil_price'] = np.full(n, self.base_prices.oil_price_usd_bbl)

        if config.gas_price:
            samples['gas_price'] = config.gas_price.sample(n, rng)
        else:
            samples['gas_price'] = np.full(n, self.base_prices.gas_price_usd_mmbtu)

        if config.capex_multiplier:
            samples['capex_mult'] = config.capex_multiplier.sample(n, rng)
        else:
            samples['capex_mult'] = np.ones(n)

        if config.opex_multiplier:
            samples['opex_mult'] = config.opex_multiplier.sample(n, rng)
        else:
            samples['opex_mult'] = np.ones(n)

        if config.production_multiplier:
            samples['prod_mult'] = config.production_multiplier.sample(n, rng)
        else:
            samples['prod_mult'] = np.ones(n)

        if config.discount_rate:
            samples['discount_rate'] = config.discount_rate.sample(n, rng)
        else:
            samples['discount_rate'] = np.full(n, self.base_discount_rate)

        return samples

    def _modify_prices(self, samples: Dict, index: int) -> PriceAssumptions:
        """Create modified price assumptions for iteration."""
        return PriceAssumptions(
            oil_price_usd_bbl=samples['oil_price'][index],
            gas_price_usd_mmbtu=samples['gas_price'][index],
            ngl_price_usd_bbl=self.base_prices.ngl_price_usd_bbl,
            annual_escalation_pct=self.base_prices.annual_escalation_pct
        )

    def _modify_capex(self, samples: Dict, index: int) -> CapexSchedule:
        """Create modified CAPEX for iteration."""
        mult = samples['capex_mult'][index]
        return replace(self.capex,
                      schedule={y: c * mult for y, c in self.capex.schedule.items()})

    def _modify_opex(self, samples: Dict, index: int) -> OpexAssumptions:
        """Create modified OPEX for iteration."""
        mult = samples['opex_mult'][index]
        return replace(self.opex,
                      fixed_opex_usd_year=self.opex.fixed_opex_usd_year * mult,
                      variable_opex_usd_boe=self.opex.variable_opex_usd_boe * mult)

    def _modify_production(self, samples: Dict, index: int) -> List[ProductionForecast]:
        """Create modified production forecast for iteration."""
        mult = samples['prod_mult'][index]
        return [
            ProductionForecast(
                year=p.year,
                oil_mbbls=p.oil_mbbls * mult,
                gas_mmcf=p.gas_mmcf * mult,
                ngl_mbbls=p.ngl_mbbls * mult,
                water_mbbls=p.water_mbbls
            )
            for p in self.production
        ]

    def quick_simulation(self,
                        oil_range_pct: float = 0.30,
                        cost_range_pct: float = 0.20,
                        prod_range_pct: float = 0.15,
                        n_iterations: int = 1000) -> MonteCarloResult:
        """
        Run quick Monte Carlo with triangular distributions.

        Args:
            oil_range_pct: Price range as percent of base (e.g., 0.30 = ±30%)
            cost_range_pct: Cost range as percent of base
            prod_range_pct: Production range as percent of base
            n_iterations: Number of iterations

        Returns:
            MonteCarloResult with P10/P50/P90 values
        """
        base_oil = self.base_prices.oil_price_usd_bbl
        base_gas = self.base_prices.gas_price_usd_mmbtu

        config = MonteCarloConfig(
            n_iterations=n_iterations,
            oil_price=DistributionParams(
                distribution=DistributionType.TRIANGULAR,
                min_value=base_oil * (1 - oil_range_pct),
                mode_value=base_oil,
                max_value=base_oil * (1 + oil_range_pct)
            ),
            gas_price=DistributionParams(
                distribution=DistributionType.TRIANGULAR,
                min_value=base_gas * (1 - oil_range_pct),
                mode_value=base_gas,
                max_value=base_gas * (1 + oil_range_pct)
            ),
            capex_multiplier=DistributionParams(
                distribution=DistributionType.TRIANGULAR,
                min_value=1 - cost_range_pct * 0.5,  # CAPEX rarely comes in under
                mode_value=1.0,
                max_value=1 + cost_range_pct
            ),
            opex_multiplier=DistributionParams(
                distribution=DistributionType.TRIANGULAR,
                min_value=1 - cost_range_pct,
                mode_value=1.0,
                max_value=1 + cost_range_pct
            ),
            production_multiplier=DistributionParams(
                distribution=DistributionType.TRIANGULAR,
                min_value=1 - prod_range_pct,
                mode_value=1.0,
                max_value=1 + prod_range_pct * 0.5  # Production rarely exceeds forecast
            )
        )

        return self.run_simulation(config)

    def value_at_risk(self, result: MonteCarloResult,
                      confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR) for NPV.

        Args:
            result: Monte Carlo simulation result
            confidence: Confidence level (e.g., 0.95 for 95%)

        Returns:
            VaR value (maximum expected loss at confidence level)
        """
        percentile = (1 - confidence) * 100
        return np.percentile(result.npv_values, percentile)

    def conditional_value_at_risk(self, result: MonteCarloResult,
                                  confidence: float = 0.95) -> float:
        """
        Calculate Conditional VaR (Expected Shortfall).

        Args:
            result: Monte Carlo simulation result
            confidence: Confidence level

        Returns:
            CVaR value (average loss in worst cases beyond VaR)
        """
        var = self.value_at_risk(result, confidence)
        return np.mean(result.npv_values[result.npv_values <= var])
```

=======
>>>>>>> origin/main
### Report Generator

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

class NPVReportGenerator:
    """Generate interactive HTML reports for NPV analysis."""

    def __init__(self, calculator: NPVCalculator,
<<<<<<< HEAD
                 scenario_analyzer: ScenarioAnalyzer = None,
                 monte_carlo_result: MonteCarloResult = None):
        """Initialize report generator."""
        self.calculator = calculator
        self.analyzer = scenario_analyzer
        self.mc_result = monte_carlo_result

    def generate_report(self, output_path: Path, project_name: str = "Project"):
        """Generate comprehensive NPV analysis report with Monte Carlo."""
        # Determine subplot layout based on Monte Carlo availability
        if self.mc_result:
            fig = make_subplots(
                rows=4, cols=2,
                subplot_titles=(
                    'Annual Cash Flows',
                    'Cumulative Cash Flow',
                    'Price Scenario NPV',
                    'Sensitivity Analysis',
                    'Monte Carlo NPV Distribution',
                    'P10/P50/P90 Summary',
                    'Production Profile',
                    'Revenue Breakdown'
                ),
                vertical_spacing=0.08,
                specs=[[{}, {}], [{}, {}], [{}, {}], [{}, {}]]
            )
        else:
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    'Annual Cash Flows',
                    'Cumulative Cash Flow',
                    'Price Scenario NPV',
                    'Sensitivity Analysis',
                    'Production Profile',
                    'Revenue Breakdown'
                ),
                vertical_spacing=0.10
            )
=======
                 scenario_analyzer: ScenarioAnalyzer = None):
        """Initialize report generator."""
        self.calculator = calculator
        self.analyzer = scenario_analyzer

    def generate_report(self, output_path: Path, project_name: str = "Project"):
        """Generate comprehensive NPV analysis report."""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Annual Cash Flows',
                'Cumulative Cash Flow',
                'Price Scenario NPV',
                'Sensitivity Analysis',
                'Production Profile',
                'Revenue Breakdown'
            ),
            vertical_spacing=0.10
        )
>>>>>>> origin/main

        cf_df = self.calculator.to_dataframe()

        # Annual cash flows
        fig.add_trace(
            go.Bar(x=cf_df['year'], y=cf_df['atcf']/1e6,
                   name='After-Tax CF ($MM)', marker_color='green'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=cf_df['year'], y=-cf_df['capex']/1e6,
                   name='CAPEX ($MM)', marker_color='red'),
            row=1, col=1
        )

        # Cumulative cash flow
        fig.add_trace(
            go.Scatter(x=cf_df['year'], y=cf_df['cumulative']/1e6,
                      name='Cumulative CF', fill='tozeroy',
                      line=dict(color='blue')),
            row=1, col=2
        )
        fig.add_hline(y=0, line_dash='dash', line_color='gray', row=1, col=2)

        # Price scenarios
        if self.analyzer:
            scenarios = self.analyzer.run_price_scenarios()
            fig.add_trace(
                go.Bar(x=scenarios['scenario'], y=scenarios['npv_mm'],
                       name='NPV by Scenario',
                       marker_color=['#d62728', '#2ca02c', '#1f77b4']),
                row=2, col=1
            )

            # Tornado chart
            tornado = self.analyzer.tornado_chart_data(self.calculator.prices)
            for _, row_data in tornado.iterrows():
                fig.add_trace(
                    go.Bar(
                        y=[row_data['variable']],
                        x=[row_data['high_npv'] - row_data['base_npv']],
                        orientation='h',
                        name=f"{row_data['variable']} High",
                        marker_color='green',
                        showlegend=False
                    ),
                    row=2, col=2
                )
                fig.add_trace(
                    go.Bar(
                        y=[row_data['variable']],
                        x=[row_data['low_npv'] - row_data['base_npv']],
                        orientation='h',
                        name=f"{row_data['variable']} Low",
                        marker_color='red',
                        showlegend=False
                    ),
                    row=2, col=2
                )

<<<<<<< HEAD
        # Monte Carlo visualization (if available)
        mc_row = 3 if self.mc_result else None
        prod_row = 4 if self.mc_result else 3

        if self.mc_result:
            # NPV histogram
            fig.add_trace(
                go.Histogram(
                    x=self.mc_result.npv_values / 1e6,
                    nbinsx=50,
                    name='NPV Distribution',
                    marker_color='steelblue',
                    opacity=0.7
                ),
                row=3, col=1
            )

            # Add P10/P50/P90 lines
            for pct, val, color in [
                ('P10', self.mc_result.p10_npv, 'red'),
                ('P50', self.mc_result.p50_npv, 'orange'),
                ('P90', self.mc_result.p90_npv, 'green')
            ]:
                fig.add_vline(
                    x=val / 1e6, line_dash='dash', line_color=color,
                    annotation_text=pct, row=3, col=1
                )

            # P10/P50/P90 bar chart
            fig.add_trace(
                go.Bar(
                    x=['P10', 'P50', 'P90'],
                    y=[self.mc_result.p10_npv / 1e6,
                       self.mc_result.p50_npv / 1e6,
                       self.mc_result.p90_npv / 1e6],
                    marker_color=['red', 'orange', 'green'],
                    name='Percentiles'
                ),
                row=3, col=2
            )

            # Add probability annotation
            mc_summary = (
                f"<b>Monte Carlo Results</b><br>"
                f"Iterations: {len(self.mc_result.npv_values):,}<br>"
                f"Mean NPV: ${self.mc_result.mean_npv/1e6:.1f}MM<br>"
                f"Std Dev: ${self.mc_result.std_npv/1e6:.1f}MM<br>"
                f"P(NPV>0): {self.mc_result.prob_positive_npv*100:.1f}%"
            )
            fig.add_annotation(
                text=mc_summary,
                xref='paper', yref='paper',
                x=1.02, y=0.50,
                showarrow=False,
                font=dict(size=11),
                align='left',
                bgcolor='lightyellow',
                bordercolor='gray'
            )

=======
>>>>>>> origin/main
        # Production profile
        prod_df = pd.DataFrame([
            {'year': p.year, 'oil': p.oil_mbbls, 'gas': p.gas_mmcf/6, 'ngl': p.ngl_mbbls}
            for p in self.calculator.production
        ])

        fig.add_trace(
            go.Bar(x=prod_df['year'], y=prod_df['oil'],
                   name='Oil (Mbbls)', marker_color='green'),
<<<<<<< HEAD
            row=prod_row, col=1
=======
            row=3, col=1
>>>>>>> origin/main
        )
        fig.add_trace(
            go.Bar(x=prod_df['year'], y=prod_df['gas'],
                   name='Gas (BOE Mbbls)', marker_color='red'),
<<<<<<< HEAD
            row=prod_row, col=1
=======
            row=3, col=1
>>>>>>> origin/main
        )

        # Revenue breakdown
        cash_flows = self.calculator.calculate_cash_flows()
        total_oil_rev = sum(cf.gross_oil_revenue for cf in cash_flows)
        total_gas_rev = sum(cf.gross_gas_revenue for cf in cash_flows)
        total_ngl_rev = sum(cf.gross_ngl_revenue for cf in cash_flows)

        fig.add_trace(
            go.Pie(
                labels=['Oil', 'Gas', 'NGL'],
                values=[total_oil_rev, total_gas_rev, total_ngl_rev],
                marker_colors=['green', 'red', 'orange']
            ),
<<<<<<< HEAD
            row=prod_row, col=2
=======
            row=3, col=2
>>>>>>> origin/main
        )

        # Summary metrics annotation
        summary = self.calculator.summary()
        summary_text = (
            f"<b>Economic Summary</b><br>"
            f"NPV (10%): ${summary['npv_mm']:.1f}MM<br>"
            f"IRR: {summary['irr_pct']:.1f}%<br>"
            f"Payback: {summary['payback_years']:.1f} years<br>"
            f"PI: {summary['profitability_index']:.2f}"
        )

        fig.add_annotation(
            text=summary_text,
            xref='paper', yref='paper',
            x=1.02, y=0.98,
            showarrow=False,
            font=dict(size=12),
            align='left',
            bgcolor='white',
            bordercolor='gray'
        )

        fig.update_layout(
<<<<<<< HEAD
            height=1400 if self.mc_result else 1100,
            title_text=f"{project_name} - NPV Analysis" + (" (Monte Carlo)" if self.mc_result else ""),
=======
            height=1100,
            title_text=f"{project_name} - NPV Analysis",
>>>>>>> origin/main
            showlegend=True,
            barmode='relative'
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))

        return output_path
```

## YAML Configuration

### Project Configuration

```yaml
# config/npv_analysis.yaml

metadata:
  project_name: "Lower Tertiary Development"
  analyst: "Engineering Team"
  date: "2024-01-15"
  version: "1.0"

economics:
  discount_rate: 0.10  # 10%
  base_year: 2024
  project_life: 25  # years

prices:
  scenario: mid  # low, mid, high, strip
  oil_price_usd_bbl: 70.0
  gas_price_usd_mmbtu: 3.50
  ngl_price_usd_bbl: 35.0
  annual_escalation_pct: 2.0

fiscal:
  working_interest: 0.50  # 50% WI
  net_revenue_interest: 0.875  # 87.5% NRI (12.5% royalty)
  royalty_rate: 0.125
  state_severance_tax: 0.0  # Federal waters
  federal_income_tax: 0.21
  ad_valorem_tax: 0.0

capex:
  drilling_per_well: 120.0  # $MM per well
  completion_per_well: 40.0
  facilities: 500.0
  subsea_equipment: 300.0
  pipeline: 150.0
  other_capex: 50.0
  schedule:  # year: amount ($MM)
    2024: 200.0
    2025: 600.0
    2026: 360.0

opex:
  fixed_opex_usd_year: 25000000  # $25MM/year
  variable_opex_usd_boe: 8.0  # $8/BOE
  workover_budget: 5000000
  insurance: 3000000
  g_and_a: 2000000
  abandonment_cost: 150000000
  abandonment_year: 2049

production:
  source: "file"  # file, manual, decline_curve
  file_path: "data/production_forecast.csv"

  # Or manual entry:
  # manual:
  #   - year: 2027
  #     oil_mbbls: 5000
  #     gas_mmcf: 3000
  #   - year: 2028
  #     oil_mbbls: 8000
  #     gas_mmcf: 5000

output:
  cash_flow_csv: "data/results/cash_flows.csv"
  summary_json: "data/results/summary.json"
  report_html: "reports/npv_analysis.html"
```

### Scenario Comparison

```yaml
# config/scenario_comparison.yaml

scenarios:
  - name: "Base Case"
    oil_price: 70
    gas_price: 3.50
    capex_multiplier: 1.0

  - name: "Low Price"
    oil_price: 50
    gas_price: 2.50
    capex_multiplier: 1.0

  - name: "High Price"
    oil_price: 90
    gas_price: 5.00
    capex_multiplier: 1.0

  - name: "Cost Overrun"
    oil_price: 70
    gas_price: 3.50
    capex_multiplier: 1.25

  - name: "Fast Payout"
    oil_price: 80
    gas_price: 4.00
    capex_multiplier: 0.90

analysis:
  run_sensitivity: true
  sensitivity_range_pct: 0.30
  tornado_chart: true

output:
  comparison_csv: "data/results/scenario_comparison.csv"
  report_html: "reports/scenario_comparison.html"
```

<<<<<<< HEAD
### Monte Carlo Configuration

```yaml
# config/monte_carlo_analysis.yaml

metadata:
  project_name: "Lower Tertiary Development"
  analyst: "Risk Analysis Team"
  date: "2024-01-15"
  version: "1.0"

monte_carlo:
  n_iterations: 10000
  random_seed: 42  # For reproducibility

  # Oil price distribution (triangular: min, mode, max)
  oil_price:
    distribution: triangular
    min_value: 50.0
    mode_value: 70.0
    max_value: 100.0

  # Gas price distribution
  gas_price:
    distribution: triangular
    min_value: 2.50
    mode_value: 3.50
    max_value: 6.00

  # CAPEX multiplier (typically skewed toward overruns)
  capex_multiplier:
    distribution: pert
    min_value: 0.95
    mode_value: 1.00
    max_value: 1.30

  # OPEX multiplier
  opex_multiplier:
    distribution: triangular
    min_value: 0.85
    mode_value: 1.00
    max_value: 1.20

  # Production multiplier (typically skewed toward underperformance)
  production_multiplier:
    distribution: pert
    min_value: 0.70
    mode_value: 1.00
    max_value: 1.10

output:
  npv_distribution_csv: "data/results/npv_distribution.csv"
  percentiles_json: "data/results/percentiles.json"
  report_html: "reports/monte_carlo_analysis.html"
```

=======
>>>>>>> origin/main
## CLI Usage

```bash
# Run NPV analysis
python -m npv_analyzer run --config config/npv_analysis.yaml

# Quick NPV calculation
python -m npv_analyzer calculate \
    --production data/forecast.csv \
    --oil-price 70 \
    --gas-price 3.50 \
    --discount-rate 0.10

# Run scenario comparison
python -m npv_analyzer scenarios --config config/scenario_comparison.yaml

# Calculate breakeven price
python -m npv_analyzer breakeven --config config/npv_analysis.yaml --commodity oil

# Generate sensitivity tornado
python -m npv_analyzer sensitivity --config config/npv_analysis.yaml --range 0.30
<<<<<<< HEAD

# Run Monte Carlo simulation
python -m npv_analyzer montecarlo --config config/monte_carlo_analysis.yaml

# Quick Monte Carlo with default distributions
python -m npv_analyzer montecarlo --config config/npv_analysis.yaml \
    --iterations 5000 \
    --oil-range 0.30 \
    --cost-range 0.20

# Get P10/P50/P90 summary
python -m npv_analyzer percentiles --config config/monte_carlo_analysis.yaml
=======
>>>>>>> origin/main
```

## Usage Examples

### Example 1: Simple NPV Calculation

```python
from npv_analyzer import (
    NPVCalculator, ProductionForecast, PriceAssumptions,
    FiscalTerms, CapexSchedule, OpexAssumptions
)

# Define production forecast
production = [
    ProductionForecast(year=2027, oil_mbbls=3000, gas_mmcf=2000),
    ProductionForecast(year=2028, oil_mbbls=8000, gas_mmcf=5000),
    ProductionForecast(year=2029, oil_mbbls=10000, gas_mmcf=6500),
    ProductionForecast(year=2030, oil_mbbls=9000, gas_mmcf=6000),
    ProductionForecast(year=2031, oil_mbbls=7500, gas_mmcf=5000),
]

# Define economics
prices = PriceAssumptions(oil_price_usd_bbl=70, gas_price_usd_mmbtu=3.50)
fiscal = FiscalTerms(working_interest=0.50, net_revenue_interest=0.875)
capex = CapexSchedule(schedule={2024: 200, 2025: 600, 2026: 360})
opex = OpexAssumptions(fixed_opex_usd_year=25e6, variable_opex_usd_boe=8.0)

# Calculate NPV
calc = NPVCalculator(production, prices, fiscal, capex, opex, discount_rate=0.10)

print(f"NPV @ 10%: ${calc.npv()/1e6:.1f}MM")
print(f"IRR: {calc.irr()*100:.1f}%")
print(f"Payback: {calc.payback_period():.1f} years")
```

### Example 2: Scenario Analysis

```python
from npv_analyzer import ScenarioAnalyzer, NPVReportGenerator

# Create analyzer
analyzer = ScenarioAnalyzer(production, fiscal, capex, opex)

# Run price scenarios
scenarios = analyzer.run_price_scenarios()
print("\nPrice Scenario Results:")
print(scenarios[['scenario', 'npv_mm', 'irr_pct', 'payback_years']])

# Generate tornado chart data
tornado = analyzer.tornado_chart_data(prices)
print("\nSensitivity Ranking:")
print(tornado[['variable', 'range']])

# Generate report
reporter = NPVReportGenerator(calc, analyzer)
reporter.generate_report(
    Path("reports/npv_report.html"),
    project_name="Lower Tertiary Development"
)
```

<<<<<<< HEAD
### Example 3: Monte Carlo Simulation

```python
from npv_analyzer import (
    MonteCarloSimulator, MonteCarloConfig, DistributionParams,
    DistributionType, NPVReportGenerator
)

# Create Monte Carlo simulator
mc_sim = MonteCarloSimulator(
    production=production,
    base_prices=prices,
    fiscal=fiscal,
    capex=capex,
    opex=opex,
    base_discount_rate=0.10
)

# Quick simulation with default triangular distributions
result = mc_sim.quick_simulation(
    oil_range_pct=0.30,  # ±30% oil price variation
    cost_range_pct=0.20,  # ±20% cost variation
    prod_range_pct=0.15,  # ±15% production variation
    n_iterations=5000
)

# Print P10/P50/P90 results
print(f"\nMonte Carlo Results ({len(result.npv_values):,} iterations):")
print(f"P10 NPV: ${result.p10_npv/1e6:.1f}MM (pessimistic)")
print(f"P50 NPV: ${result.p50_npv/1e6:.1f}MM (median)")
print(f"P90 NPV: ${result.p90_npv/1e6:.1f}MM (optimistic)")
print(f"Probability of positive NPV: {result.prob_positive_npv*100:.1f}%")

# Custom distribution configuration
custom_config = MonteCarloConfig(
    n_iterations=10000,
    random_seed=42,  # For reproducibility
    oil_price=DistributionParams(
        distribution=DistributionType.TRIANGULAR,
        min_value=50, mode_value=70, max_value=100
    ),
    capex_multiplier=DistributionParams(
        distribution=DistributionType.PERT,
        min_value=0.95, mode_value=1.0, max_value=1.30
    ),
    production_multiplier=DistributionParams(
        distribution=DistributionType.LOGNORMAL,
        min_value=0.6, max_value=1.15, mean=1.0, std_dev=0.15
    )
)

result = mc_sim.run_simulation(custom_config)

# Calculate Value at Risk
var_95 = mc_sim.value_at_risk(result, confidence=0.95)
cvar_95 = mc_sim.conditional_value_at_risk(result, confidence=0.95)
print(f"\nRisk Metrics:")
print(f"VaR (95%): ${var_95/1e6:.1f}MM")
print(f"CVaR (95%): ${cvar_95/1e6:.1f}MM")

# Generate report with Monte Carlo visualization
reporter = NPVReportGenerator(calc, analyzer, monte_carlo_result=result)
reporter.generate_report(
    Path("reports/npv_montecarlo_report.html"),
    project_name="Lower Tertiary Development - Risk Analysis"
)
```

=======
>>>>>>> origin/main
## Best Practices

### Model Setup
- Use consistent units throughout (USD, bbls, MCF)
- Validate production forecasts against reservoir studies
- Document all assumptions in YAML configs
- Version control economic parameters

### Sensitivity Analysis
- Always run multiple price scenarios
- Include cost and schedule sensitivities
- Identify breakeven prices for investment decisions
- Document uncertainty ranges

### Reporting
- Include summary metrics prominently
- Show cash flow timing clearly
- Compare against investment criteria (hurdle rate, payback limits)
- Archive analysis with assumptions

<<<<<<< HEAD
### Monte Carlo Analysis
- Use 5,000-10,000 iterations for stable P10/P50/P90
- Choose appropriate distributions (PERT for expert estimates, triangular for simple ranges)
- CAPEX typically skewed toward overruns (use asymmetric distributions)
- Production typically skewed toward underperformance
- Set random seed for reproducible results
- Calculate VaR and CVaR for risk management
- Report probability of positive NPV for investment decisions

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - Production data for forecasts
- [hse-risk-analyzer](../hse-risk-analyzer/SKILL.md) - Risk-adjusted NPV with safety data
- [production-forecaster](../production-forecaster/SKILL.md) - Decline curve production forecasts
- [engineering-report-generator](/mnt/github/workspace-hub/.claude/skills/development/engineering-report-generator/SKILL.md) - Report generation
=======
## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - Production data for forecasts
- [engineering-report-generator](/mnt/github/workspace-hub/.claude/skills/development/engineering-report-generator/SKILL.md) - Report generation
- [data-pipeline-processor](/mnt/github/workspace-hub/.claude/skills/development/data-pipeline-processor/SKILL.md) - Data processing
>>>>>>> origin/main
