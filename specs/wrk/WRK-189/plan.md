# WRK-189: Daily Stock Analysis & Position Strategy

> Route C spec — requires user approval before implementation begins.
> Work item: `.claude/work-queue/working/WRK-189.md`

---

## 1. Problem Statement

The `achantas-data/_finance/fidelity` directory holds **transaction history** CSVs (2022–2025) for
three accounts. There is no daily decision-support tool that answers: *"For each holding I own today,
should I add more, hold, or start trimming?"*

The goal is a repeatable, automated daily analysis loop that reconstructs current positions from
transaction history, fetches fresh market signals, scores each position, and outputs a human-readable
strategy report.

---

## 2. Data Reality (from exploration)

| Item | Finding |
|------|---------|
| Data format | Fidelity transaction-history CSVs, **not** position snapshots |
| Accounts | Individual-TOD (X78707567), Traditional IRA (224886419), Cencora Employee INV (82897) |
| Holdings (active tickers) | BRKB, RIG, XOM, VOO; SPAXX = cash sweep (skip) |
| Columns in CSV | Run Date, Account, Account Number, Action, Symbol, Description, Type, Price ($), Quantity, Commission ($), Fees ($), Accrued Interest ($), Amount ($), Settlement Date |
| Existing parser | `modules/stocks/portfolio.py::Portfolio.portfolio_value()` — reads CSVs but only sums Amount ($), does **not** compute net shares |

> **Key insight**: to know what we own today, we must sum `Quantity` per (Account, Symbol) across all
> buy/sell transactions in all four CSVs. Buys have positive Quantity, sells have negative Quantity.

---

## 3. Architecture

```
achantas-data/_finance/fidelity/*.csv
        │
        ▼
┌───────────────────┐
│  FidelityLoader   │  Parse all CSVs → net shares held per (account, ticker)
└────────┬──────────┘
         │  List[Position]
         ▼
┌───────────────────┐
│ MarketDataFetcher │  Extend StockDataSource → also fetch .info (P/E, 52-wk range)
└────────┬──────────┘
         │  Dict[ticker, MarketSnapshot]
         ▼
┌───────────────────┐
│   SignalEngine    │  Score each position → Build/Hold/Trim + rationale
└────────┬──────────┘
         │  List[PositionSignal]
         ▼
┌────────────────────────┐
│  DailyStrategyReport   │  Render Markdown report → reports/daily-strategy/YYYY-MM-DD.md
└────────────────────────┘
```

---

## 4. Module Layout

New code lives entirely within `src/assethold/analysis/daily_strategy/`:

```
src/assethold/analysis/
├── __init__.py              (new)
└── daily_strategy/
    ├── __init__.py          (exports: run_daily_strategy)
    ├── loader.py            (FidelityLoader)
    ├── fetcher.py           (MarketDataFetcher wrapping StockDataSource)
    ├── signals.py           (SignalEngine, scoring weights)
    ├── report.py            (DailyStrategyReport → Markdown)
    └── __main__.py          (CLI entry: python -m assethold.analysis.daily_strategy)

tests/unit/analysis/
└── daily_strategy/
    ├── __init__.py
    ├── test_loader.py       (~15 tests)
    ├── test_fetcher.py      (~10 tests)
    ├── test_signals.py      (~20 tests)
    └── test_report.py       (~8 tests)
```

No changes to existing files except:
- `src/assethold/analysis/__init__.py` (new, empty)
- `reports/daily-strategy/` directory created on first run

---

## 5. Implementation Phases

### Phase 1 — FidelityLoader (`loader.py`)

**Responsibility**: Read all Fidelity CSVs → reconstruct current holdings as net shares per ticker.

**Key logic**:
```
net_shares[account][ticker] = Σ Quantity for (YOU BOUGHT | REINVESTMENT) rows
                             - Σ |Quantity| for (YOU SOLD) rows
```

**Skip rules**:
- Rows where `Symbol` is blank or `SPAXX` or `QPIGQ` (cash / money-market sweeps)
- Rows where `Action` contains `DIVIDEND`, `INTEREST`, `Electronic Funds Transfer`,
  `RECORDKEEPING FEE`, `Change In Market Value` — these are not share movements
- Employee account (82897): `Symbol` is blank → use `Description` as fund name, mark as `non_tradeable`

**Output dataclass**:
```python
@dataclass
class Position:
    account: str
    account_number: str
    ticker: str
    shares: float
    tradeable: bool  # False for employee funds with no ticker
    avg_cost_basis: float | None  # computed if possible
```

**Cost basis**: compute as `Σ Amount($) for buys / total shares bought` (simple average, not FIFO).

**Data path config**: read from env var `FIDELITY_DATA_DIR`, fallback to
`achantas-data/_finance/fidelity` relative to workspace root.

**File**: `src/assethold/analysis/daily_strategy/loader.py`

**Tests** (`test_loader.py`):
- `test_net_shares_buy_only` — pure buys → positive shares
- `test_net_shares_with_sells` — buys + sells → correct net
- `test_skip_cash_rows` — SPAXX, QPIGQ rows are skipped
- `test_skip_dividend_rows` — dividend rows don't affect shares
- `test_employee_account_nontradeable` — Cencora fund rows marked non_tradeable
- `test_multi_file_aggregation` — two CSVs with same ticker → combined net
- `test_zero_position_excluded` — tickers with zero net shares not in output
- `test_avg_cost_basis` — correctly averages buy prices
- `test_missing_dir_raises` — raises FileNotFoundError if data dir missing
- (+ ~5 more edge cases)

---

### Phase 2 — MarketDataFetcher (`fetcher.py`)

**Responsibility**: Fetch OHLCV + fundamentals for each tradeable ticker.

**Wraps**: `StockDataSource` for price history. Adds `yfinance.Ticker.info` call for fundamentals.

**Output dataclass**:
```python
@dataclass
class MarketSnapshot:
    ticker: str
    current_price: float
    week52_high: float
    week52_low: float
    pe_ratio: float | None       # trailingPE from yfinance info
    price_to_book: float | None  # priceToBook
    rsi_14: float                # calculated via indicators.calculate_rsi()
    sma_50: float | None         # calculated via indicators.calculate_sma(window=50)
    sma_200: float | None        # calculated via indicators.calculate_sma(window=200)
    pct_from_52w_low: float
    pct_from_52w_high: float
```

**Implementation details**:
- Fetch 252 trading days (~1 year) of price history for RSI + SMA calculations
- Reuse `StockDataSource` caching — TTL 4 hours for intraday freshness
- Separate `info` dict cached in a JSON sidecar file (TTL 24 hours — fundamentals change slowly)
- Skip tickers where `tradeable=False`

**File**: `src/assethold/analysis/daily_strategy/fetcher.py`

**Tests** (`test_fetcher.py`): all use mock yfinance; test info parsing, RSI/SMA calculation,
52-week percentages, cache hit/miss behaviour, graceful handling of missing P/E.

---

### Phase 3 — SignalEngine (`signals.py`)

**Responsibility**: Score each position → one of 5 signals.

**Scoring model** — weighted sum of sub-signals, each in [-1.0, +1.0]:

| Sub-signal | Weight | Logic |
|------------|--------|-------|
| RSI momentum | 25% | RSI<30 → +1.0 (oversold/build), RSI>70 → -1.0 (overbought/trim), else linear interpolation |
| 52-week position | 20% | % from 52w low / 52w range → near low = +1.0, near high = -1.0 |
| Price vs SMA-50 | 20% | Below SMA-50 → +0.5 (potential value), above → -0.5 |
| Price vs SMA-200 | 15% | Below SMA-200 → +0.75 (deep discount), above → -0.5 |
| P/E vs sector | 10% | Not implemented in v1 (requires sector data) → 0.0, noted |
| Portfolio weight | 10% | Position weight vs target_weight from config; over-weight → negative |

**Score → Signal mapping**:

| Score range | Signal |
|-------------|--------|
| > 0.5 | STRONG BUILD |
| 0.2 to 0.5 | BUILD |
| -0.2 to 0.2 | HOLD |
| -0.5 to -0.2 | TRIM |
| < -0.5 | STRONG TRIM |

**Output dataclass**:
```python
@dataclass
class PositionSignal:
    position: Position
    snapshot: MarketSnapshot
    score: float
    signal: str        # STRONG BUILD | BUILD | HOLD | TRIM | STRONG TRIM
    rationale: list[str]  # human-readable bullet points explaining key drivers
```

**Config file** (`config/daily_strategy.yaml`):
```yaml
scoring:
  rsi_oversold: 30
  rsi_overbought: 70
targets:
  # BRKB and VOO are core equal-weight ETF/holding — actively build/hold/trim
  BRKB: { target_weight: 25.0, mode: managed }
  VOO:  { target_weight: 25.0, mode: managed }
  # XOM and RIG are individual stocks held for opportunity/risk — HOLD or TRIM only
  # No positive build signal from weight drift; trim if oversized
  XOM:  { max_weight: 15.0, mode: trim_only }
  RIG:  { max_weight: 10.0, mode: trim_only }
```

**`mode` field in SignalEngine**:
- `managed`: full signal range (Strong Build → Strong Trim) driven by all sub-signals
- `trim_only`: build sub-signals from RSI/SMA/52-week are suppressed; score is clamped to ≤ 0 unless
  weight is within bounds. Net effect: these positions can only signal HOLD or TRIM.

**File**: `src/assethold/analysis/daily_strategy/signals.py`

**Tests** (`test_signals.py`): ~20 tests covering all boundary conditions, weight drift scenarios,
missing P/E graceful handling, rationale string generation.

---

### Phase 4 — Report & CLI

**`report.py`** — `DailyStrategyReport`:
- Takes list of `PositionSignal`, renders a Markdown report with **two sections**:
  1. **Per-account sections** — Individual-TOD, Traditional IRA, Cencora Employee INV each get their
     own table showing positions, shares, current value, signal
  2. **Combined portfolio section** — all accounts merged, showing combined shares + market value per
     ticker, overall portfolio weights, and the final signal (signals are account-agnostic — the same
     ticker gets the same score regardless of which account holds it)
- Header: date, combined portfolio total value
- Signals sorted: Strong Build → Build → Hold → Trim → Strong Trim
- Per-ticker rationale: 2–4 bullet points explaining key drivers
- Footer: methodology note + data currency warning if CSVs are stale

**Output path**: `assethold/reports/daily-strategy/YYYY-MM-DD.md`
- Directory auto-created on first run
- Terminal echo: compact combined table only (per-account detail in file)

**`__main__.py`** — CLI:
```
python -m assethold.analysis.daily_strategy [--accounts all|individual|ira] [--date YYYY-MM-DD] [--no-cache]
```

**Tests** (`test_report.py`): test Markdown structure, empty-portfolio edge case, date formatting.

---

## 6. Cross-Cutting Concerns

### Non-tradeable positions (employee account)
- Included in portfolio value totals
- Shown in report with `HOLD (non-tradeable)` — no signal generated
- Not passed to `SignalEngine`

### tickers with partial data
- If yfinance returns no P/E: exclude that sub-signal, renormalize weights
- If RSI cannot be calculated (< 14 days data): use 52-week position only
- Log warnings via `loguru` (already a dependency)

### Data currency warning
- If any CSV is older than 30 days past its latest date: warn in report header
- Report date = today; data may be stale note if run on weekend/holiday

---

## 7. Test Strategy

```
PYTHONPATH=src python3 -m pytest tests/unit/analysis/ -v --tb=short --noconftest
```

- All external calls (yfinance, network) mocked
- No real market data required for unit tests
- Target: ≥80% coverage on new modules
- Integration test (manual): `python -m assethold.analysis.daily_strategy` with live yfinance

---

## 8. File Change Summary

| File | Action | Notes |
|------|--------|-------|
| `src/assethold/analysis/__init__.py` | New | Empty package marker |
| `src/assethold/analysis/daily_strategy/__init__.py` | New | Exports `run_daily_strategy` |
| `src/assethold/analysis/daily_strategy/loader.py` | New | `FidelityLoader` |
| `src/assethold/analysis/daily_strategy/fetcher.py` | New | `MarketDataFetcher` |
| `src/assethold/analysis/daily_strategy/signals.py` | New | `SignalEngine` |
| `src/assethold/analysis/daily_strategy/report.py` | New | `DailyStrategyReport` |
| `src/assethold/analysis/daily_strategy/__main__.py` | New | CLI entry |
| `config/daily_strategy.yaml` | New | Signal thresholds + target weights |
| `tests/unit/analysis/daily_strategy/test_loader.py` | New | ~15 tests |
| `tests/unit/analysis/daily_strategy/test_fetcher.py` | New | ~10 tests |
| `tests/unit/analysis/daily_strategy/test_signals.py` | New | ~20 tests |
| `tests/unit/analysis/daily_strategy/test_report.py` | New | ~8 tests |
| `README.md` | Edit | Add "Daily Strategy" section |

**Zero changes** to existing files except README.

---

## 9. Implementation Sequence

1. **Phase 1**: `loader.py` + `test_loader.py` — get holdings from transaction history
2. **Phase 2**: `fetcher.py` + `test_fetcher.py` — market snapshots
3. **Phase 3**: `signals.py` + `test_signals.py` — scoring engine
4. **Phase 4**: `report.py`, `__main__.py`, `test_report.py`, `config/daily_strategy.yaml`
5. **Phase 5**: Integration smoke test (live run) + README update

---

## 10. Review Log

| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| — | — | — | — | — | — |

---

*Plan generated: 2026-02-17*
*Spec source: WRK-189 exploration of assethold + achantas-data/_finance/fidelity*
