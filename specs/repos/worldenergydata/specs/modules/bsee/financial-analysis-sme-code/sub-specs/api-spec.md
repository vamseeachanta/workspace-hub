# API Specification

This is the API specification for the spec detailed in @specs/modules/bsee/financial-analysis-sme-code/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Python API

### Main Module Interface

```python
from worldenergydata.bsee.analysis.sme_financial import FinancialAnalyzer

# Initialize analyzer
analyzer = FinancialAnalyzer(config_path="config.yaml")

# Run analysis
results = analyzer.analyze(
    input_data_path="path/to/data",
    output_path="output/financial_analysis.xlsx"
)
```

### Core Classes and Methods

#### FinancialAnalyzer

```python
class FinancialAnalyzer:
    def __init__(self, config_path: str = None, config_dict: dict = None):
        """
        Initialize the financial analyzer.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Configuration dictionary (alternative to file)
        """
        
    def analyze(self, 
                input_data_path: str = None,
                exec_summary_df: pd.DataFrame = None,
                cf_debug_df: pd.DataFrame = None,
                output_path: str = "financial_analysis.xlsx") -> dict:
        """
        Run complete financial analysis.
        
        Args:
            input_data_path: Path to input Excel file with required sheets
            exec_summary_df: Executive summary DataFrame (optional)
            cf_debug_df: Cash flow debug DataFrame (optional)
            output_path: Path for output Excel file
            
        Returns:
            Dictionary with analysis results and metrics
        """
        
    def process_leases(self, lease_data: pd.DataFrame) -> pd.DataFrame:
        """
        Process individual lease data.
        
        Args:
            lease_data: DataFrame with lease production and cost data
            
        Returns:
            Processed DataFrame with calculated metrics
        """
```

#### LeaseProcessor

```python
class LeaseProcessor:
    def __init__(self, group_mapping: dict):
        """
        Initialize lease processor with group mappings.
        
        Args:
            group_mapping: Dictionary mapping lease names to groups
        """
        
    def apply_grouping(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply lease grouping to DataFrame.
        
        Args:
            df: DataFrame with LEASE_NAME column
            
        Returns:
            DataFrame with added GROUP_AS column
        """
        
    def aggregate_by_group(self, df: pd.DataFrame, 
                          group_col: str = "GROUP_AS",
                          agg_cols: list = None) -> pd.DataFrame:
        """
        Aggregate data by lease groups.
        
        Args:
            df: DataFrame to aggregate
            group_col: Column name for grouping
            agg_cols: Columns to aggregate (sum by default)
            
        Returns:
            Aggregated DataFrame
        """
```

#### CashFlowCalculator

```python
class CashFlowCalculator:
    def __init__(self, tax_rate: float = 0.35, discount_rate: float = 0.10):
        """
        Initialize cash flow calculator.
        
        Args:
            tax_rate: Tax rate for calculations
            discount_rate: Discount rate for NPV
        """
        
    def calculate_monthly_cash_flow(self, 
                                   production: np.array,
                                   prices: np.array,
                                   opex: np.array,
                                   capex_drilling: np.array,
                                   capex_completion: np.array) -> dict:
        """
        Calculate monthly cash flows.
        
        Args:
            production: Monthly production volumes
            prices: Monthly commodity prices
            opex: Monthly operating expenses
            capex_drilling: Monthly drilling capital expenses
            capex_completion: Monthly completion capital expenses
            
        Returns:
            Dictionary with cash flow components
        """
        
    def calculate_npv(self, cash_flows: np.array, 
                     discount_rate: float = None) -> float:
        """
        Calculate Net Present Value.
        
        Args:
            cash_flows: Array of cash flows
            discount_rate: Override default discount rate
            
        Returns:
            NPV value
        """
```

#### ReportGenerator

```python
class ReportGenerator:
    def __init__(self, version: str = "V18_011"):
        """
        Initialize report generator.
        
        Args:
            version: Version tag for reports
        """
        
    def create_workbook(self, 
                       data: dict,
                       output_path: str,
                       include_readme: bool = True) -> None:
        """
        Create Excel workbook with analysis results.
        
        Args:
            data: Dictionary with analysis data by lease group
            output_path: Path for output Excel file
            include_readme: Whether to include README sheet
        """
        
    def add_summary_sheet(self, writer: pd.ExcelWriter, 
                         summary_data: pd.DataFrame) -> None:
        """
        Add executive summary sheet.
        
        Args:
            writer: Excel writer object
            summary_data: Summary DataFrame
        """
        
    def format_workbook(self, workbook_path: str) -> None:
        """
        Apply formatting to Excel workbook.
        
        Args:
            workbook_path: Path to Excel file to format
        """
```

## Command-Line Interface

### Main Command

```bash
# Run financial analysis
python -m worldenergydata.bsee.analysis.sme_financial \
    --input data/input.xlsx \
    --output results/financial_analysis.xlsx \
    --config config.yaml
```

### CLI Arguments

```
usage: sme_financial [-h] [--input INPUT] [--output OUTPUT] 
                     [--config CONFIG] [--verbose]
                     [--lease-filter LEASE] [--date-range START END]

BSEE SME Financial Analysis Tool

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         Input data file path (Excel)
  --output OUTPUT       Output file path (default: financial_analysis.xlsx)
  --config CONFIG       Configuration file path (YAML)
  --verbose             Enable verbose logging
  --lease-filter LEASE  Filter to specific lease(s)
  --date-range START END  Date range for analysis (YYYY-MM-DD)
```

## Integration Examples

### Example 1: Basic Analysis

```python
from worldenergydata.bsee.analysis.sme_financial import FinancialAnalyzer

# Run with default configuration
analyzer = FinancialAnalyzer()
results = analyzer.analyze(
    input_data_path="data/bsee_production.xlsx",
    output_path="output/analysis.xlsx"
)

print(f"Analysis complete. NPV: ${results['total_npv']:,.2f}")
```

### Example 2: Custom Configuration

```python
from worldenergydata.bsee.analysis.sme_financial import FinancialAnalyzer

# Custom configuration
config = {
    "lease_groups": {
        "Field_A": "Group_1",
        "Field_B": "Group_1",
        "Field_C": "Group_2"
    },
    "calculations": {
        "tax_rate": 0.30,
        "discount_rate": 0.08
    }
}

analyzer = FinancialAnalyzer(config_dict=config)
results = analyzer.analyze(
    input_data_path="data/custom_data.xlsx",
    output_path="output/custom_analysis.xlsx"
)
```

### Example 3: Programmatic Data Processing

```python
import pandas as pd
from worldenergydata.bsee.analysis.sme_financial import (
    LeaseProcessor, CashFlowCalculator
)

# Load data
data = pd.read_excel("data.xlsx")

# Process leases
processor = LeaseProcessor(group_mapping={"Lease1": "Group1"})
grouped_data = processor.apply_grouping(data)

# Calculate cash flows
calculator = CashFlowCalculator(tax_rate=0.35)
cash_flows = calculator.calculate_monthly_cash_flow(
    production=grouped_data['production'].values,
    prices=grouped_data['price'].values,
    opex=grouped_data['opex'].values,
    capex_drilling=grouped_data['drilling_cost'].values,
    capex_completion=grouped_data['completion_cost'].values
)

npv = calculator.calculate_npv(cash_flows['net_cash_flow'])
print(f"NPV: ${npv:,.2f}")
```

## Error Responses

### Python Exceptions

```python
# Invalid input data
FinancialAnalysisError: "Missing required column: 'Oil_Bbl'"

# Configuration error
ConfigurationError: "Invalid lease group mapping"

# Processing error
ProcessingError: "Unable to calculate NPV: insufficient data"

# File I/O error
FileNotFoundError: "Input file not found: data.xlsx"
```

### CLI Error Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Input data error
- `4`: Processing error
- `5`: Output error