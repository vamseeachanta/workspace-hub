# assethold Calculation Audit

> Generated: 2026-03-13 | WRK-1179 Stream B Task 2

## Existing Calculations by Module

### risk_metrics.py (11 functions)
- `historical_var` -- Historical Value at Risk (95%/99%)
- `historical_cvar` -- Conditional VaR / Expected Shortfall
- `parametric_var` -- Parametric (normal-distribution) VaR
- `sharpe_ratio` -- Annualised Sharpe ratio
- `sortino_ratio` -- Annualised Sortino ratio (downside deviation)
- `max_drawdown` -- Peak-to-trough maximum drawdown
- `max_drawdown_with_dates` -- Drawdown with peak/trough date labels
- `calmar_ratio` -- Annualised return / |max drawdown|
- `position_risk` -- All metrics for a single return series
- `PortfolioRisk.compute` -- Weighted multi-asset portfolio risk
- `PortfolioRisk.report` -- Formatted text risk summary

### fundamentals.py (9 functions)
- `score_pe_ratio` -- P/E ratio value scoring (0-10 bands)
- `score_pb_ratio` -- Price-to-book value scoring
- `score_ev_ebitda` -- EV/EBITDA value scoring
- `fetch_fundamentals` -- Fetch P/E, P/B, EV/EBITDA, forward EPS, sector, dividend yield via yfinance
- `FundamentalsScorer.score` -- Weighted composite valuation score
- `FundamentalsScorer.rank` -- Sort holdings by composite score
- `FundamentalsScorer.fetch_and_rank` -- Fetch + rank as DataFrame
- `SectorPeerRanker.add_sector_percentiles` -- Per-sector percentile ranks + deep-value flag
- `FundamentalsReport` -- CSV and console output rendering

### options/covered_call.py (7 functions)
- `calculate_premium_yield_annual` -- Annualised premium yield
- `calculate_downside_protection` -- Absolute downside protection
- `calculate_break_even` -- Break-even price after premium
- `calculate_if_called_return_annual` -- Annualised if-called return
- `filter_option_chain` -- DTE/premium/delta filters
- `build_covered_call_table` -- Per-strike metrics DataFrame
- `analyse_covered_calls` -- Full covered call opportunity analysis

### portfolio/sector_tracker.py (5 functions)
- `classify_holding` -- GICS sector classification via yfinance
- `SectorTracker.build_breakdown` -- Market-value-weighted sector exposure
- `SectorTracker.rebalancing_suggestions` -- Sector-level rebalancing actions
- `SectorTracker.format_table` -- Console table with OVERWEIGHT flags
- `SectorTracker.render_sector_section` -- Markdown sector report

### stocks/indicators.py (7 functions)
- `calculate_sma` -- Simple Moving Average
- `calculate_ema` -- Exponential Moving Average
- `calculate_rsi` -- Relative Strength Index
- `calculate_macd` -- MACD line, signal, histogram
- `calculate_bollinger_bands` -- Bollinger Bands (middle, upper, lower, width)
- `calculate_obv` -- On-Balance Volume
- `calculate_all_indicators` -- Batch calculation of all indicators

### stocks/trend_detector.py (5 functions)
- `detect_ma_crossover` -- Golden cross / death cross detection
- `detect_support_resistance_break` -- Support/resistance level breaks
- `detect_volume_spike` -- Volume spikes (std-dev threshold)
- `detect_rsi_transition` -- RSI overbought/oversold zone entries
- `TrendDetector.analyze` -- Orchestrated trend analysis

### stocks/insider_tracker.py (5 functions)
- `parse_form4_xml` -- SEC Form 4 XML parsing
- `compute_insider_benchmarks` -- Insider transaction statistics
- `flag_unusual_activity` -- Flag unusual insider trades
- `transactions_to_dataframe` -- Insider transactions as DataFrame
- `analyze` -- Full insider analysis pipeline

### stocks/alert_engine.py (5 functions)
- `build_alerts` -- Generate alerts from watchlist + market data
- `run_watchlist` -- Run alert engine on full watchlist
- `AlertReport.to_json` -- JSON serialisation
- `AlertReport.write_json_report` -- Write JSON report
- `AlertReport.write_markdown_report` -- Write Markdown report

### stocks/dashboard.py (5 functions)
- `build_price_chart` -- Price chart with SMA overlays
- `build_rsi_chart` -- RSI chart
- `build_macd_chart` -- MACD chart
- `build_insider_timeline` -- Insider transaction timeline chart
- `save_chart` -- Chart export

### analysis/daily_strategy/signals.py (3 functions)
- `SignalEngine.score` -- Multi-factor position scoring (RSI, 52w, SMA, weight, insider)
- `SignalEngine.score_batch` -- Batch position scoring
- Signal labels: STRONG BUILD / BUILD / HOLD / TRIM / STRONG TRIM

### property/valuation.py (3 functions)
- `ValuationEngine.estimate` -- Spatial-factor property valuation range
- Confidence band determination (high/medium/low)
- Spatial adjustment from composite GIS score

### modules/multifamily/multifamily_analysis.py (20+ functions)
- NOI, GPR, Cap Rate, IRR, equity multiple
- Cash flow metrics, loan metrics, waterfall structure
- Renovation costs, vacancy, property management
- Charts: IRR, equity multiple, cash flow

### modules/stocks/ (legacy, 30+ functions)
- `investment_value.py` -- Single/multiple investment returns, compound interest
- `stock_analysis.py` -- Breakout trend analysis (Minervini-style screen)
- `get_stock_data.py` -- Data router: daily data, options, SEC filings, insider data
- `get_SEC_data.py` -- SEC EDGAR parsing (13F-HR, SC-13D/G, Form 4)
- `insider_analysis.py` -- Insider summary, call/put evaluation
- `portfolio.py` -- Simple portfolio value aggregation

### modules/fixed_interest/fd.py (stub)
- `calculate_interest` -- Simple/compound interest (NOT implemented, body is dead code)

### modules/appliances/ (5 functions)
- `lifecycle_calculator.py` -- Total cost of ownership, annual cost, replacement projection

### modules/gis/ (10+ functions)
- NDVI change detection, geocoding, KML export, timeline building, projection

### modules/net_lease/ (model only)
- `NetLeaseModel` -- NOI, net income, lease term calculations

## Total Existing Calculation Functions: ~130

## Identified Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| Portfolio beta vs energy benchmark (XLE, XOP) | HIGH | No beta calculation exists anywhere; needed for energy-sector portfolio context |
| Dividend yield forecasting | HIGH | `fetch_fundamentals` returns current yield but no projection/growth model |
| Factor model (Fama-French 3/5-factor) | MEDIUM | No factor decomposition; would explain alpha vs market/size/value |
| Fixed deposit calculator | MEDIUM | Stub exists at `modules/fixed_interest/fd.py` -- body is dead code after `pass` |
| ESG scoring integration | LOW | No ESG data source or scoring; market relevance growing |
| GICS sector auto-classification (offline) | LOW | Currently relies on live yfinance calls; no offline/cached fallback table |
| Portfolio correlation matrix | MEDIUM | Risk metrics compute per-position and weighted portfolio, but no correlation heatmap |
| Dividend reinvestment (DRIP) modelling | MEDIUM | Investment value module has compound interest but no DRIP-specific logic |

### Already Implemented (NOT gaps)
- VaR, CVaR (historical + parametric) -- `risk_metrics.py`
- Sharpe, Sortino, Calmar ratios -- `risk_metrics.py`
- Max drawdown with dates -- `risk_metrics.py`
- Options pricing (covered call) -- `options/covered_call.py` (WRK-325 complete)
- Portfolio optimization (sector-level rebalancing) -- `portfolio/sector_tracker.py`
- GICS sector classification (live) -- `portfolio/sector_tracker.py`
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger, OBV) -- `stocks/indicators.py`

## Test Coverage Summary

```
12 failed, 996 passed, 30 warnings, 5 errors in 72.40s
```

- 996 tests passing (17 deselected `live_data` markers in normal runs)
- 12 failures: legacy modules requiring live API calls (stocks data, portfolio AI)
- 5 errors: smoke tests with missing fixture dependencies
- All new modules (risk_metrics, fundamentals, covered_call, sector_tracker,
  indicators, trend_detector, insider_tracker, alert_engine) have dedicated
  test suites with full offline coverage
