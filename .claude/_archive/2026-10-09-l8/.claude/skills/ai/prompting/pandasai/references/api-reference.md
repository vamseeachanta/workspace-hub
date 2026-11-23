# PandasAI API Reference

Full code examples, integration patterns, best practices, and troubleshooting for the PandasAI skill.

## Core Capabilities — Full Examples

### 1. Basic Natural Language Queries

**Simple DataFrame Conversations:**
```python
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

def create_smart_dataframe(
    df: pd.DataFrame,
    model: str = "gpt-4",
    temperature: float = 0.0
) -> SmartDataframe:
    llm = OpenAI(model=model, temperature=temperature)
    return SmartDataframe(
        df,
        config={"llm": llm, "verbose": True, "enable_cache": True, "conversational": False}
    )

def query_dataframe(smart_df: SmartDataframe, question: str) -> any:
    try:
        return smart_df.chat(question)
    except Exception as e:
        print(f"Query error: {e}")
        return None
```

**Aggregation and Statistical Queries:**
```python
def create_analytics_interface(df: pd.DataFrame) -> SmartDataframe:
    llm = OpenAI(model="gpt-4", temperature=0)
    return SmartDataframe(
        df,
        config={
            "llm": llm,
            "verbose": False,
            "enable_cache": True,
            "custom_whitelisted_dependencies": ["scipy", "numpy"]
        }
    )

# Example statistical questions
statistical_questions = [
    "What is the average salary by department?",
    "Calculate the correlation between experience_years and salary",
    "What is the standard deviation of performance scores?",
    "Find the median projects completed by department",
    "Which department has the highest variance in salary?",
    "Show the salary distribution statistics (mean, median, std, min, max)"
]
```

### 2. Chart Generation and Visualization

```python
from pathlib import Path

def create_visualization_interface(
    df: pd.DataFrame,
    save_charts: bool = True,
    charts_path: str = "./charts"
) -> SmartDataframe:
    llm = OpenAI(model="gpt-4", temperature=0)
    Path(charts_path).mkdir(parents=True, exist_ok=True)
    return SmartDataframe(
        df,
        config={
            "llm": llm,
            "save_charts": save_charts,
            "save_charts_path": charts_path,
            "verbose": False
        }
    )

# Example chart prompts
chart_queries = [
    "Create a bar chart showing total revenue by product",
    "Plot a line chart of daily sales over time",
    "Show a pie chart of market share by region",
    "Create a scatter plot of units_sold vs revenue",
    "Generate a heatmap of sales by product and region"
]
```

### 3. Code Explanation and Generation

```python
def query_with_explanation(smart_df: SmartDataframe, question: str) -> dict:
    result = smart_df.chat(question)
    last_code = smart_df.last_code_generated
    explanation_prompt = f"Explain what this code does in simple terms:\n```python\n{last_code}\n```"
    explanation = smart_df.chat(explanation_prompt)
    return {"question": question, "result": result, "code": last_code, "explanation": explanation}

def generate_analysis_code(df: pd.DataFrame, analysis_description: str) -> str:
    llm = OpenAI(model="gpt-4", temperature=0)
    smart_df = SmartDataframe(df, config={"llm": llm, "verbose": True, "response_parser": None})
    smart_df.chat(analysis_description)
    return smart_df.last_code_generated
```

### 4. Multiple LLM Backends

```python
from typing import Optional

def create_openai_backend(model: str = "gpt-4", temperature: float = 0.0, api_key: Optional[str] = None):
    from pandasai.llm import OpenAI
    return OpenAI(model=model, temperature=temperature, api_key=api_key)

def create_anthropic_backend(model: str = "claude-3-opus-20240229", temperature: float = 0.0, api_key: Optional[str] = None):
    from pandasai.llm import Anthropic
    return Anthropic(model=model, temperature=temperature, api_key=api_key)

def create_google_backend(model: str = "gemini-pro", temperature: float = 0.0, api_key: Optional[str] = None):
    from pandasai.llm import GoogleGemini
    return GoogleGemini(model=model, temperature=temperature, api_key=api_key)

def create_azure_openai_backend(deployment_name: str, api_base: str, api_version: str = "2024-02-15-preview", api_key: Optional[str] = None):
    from pandasai.llm import AzureOpenAI
    return AzureOpenAI(deployment_name=deployment_name, api_base=api_base, api_version=api_version, api_key=api_key)

def create_local_backend(model_path: str, model_type: str = "llama"):
    from pandasai.llm import LocalLLM
    return LocalLLM(model_path=model_path, model_type=model_type)


class MultiBackendAnalyzer:
    """Analyzer supporting multiple LLM backends with fallback."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.backends = {}
        self.current_backend = None

    def add_backend(self, name: str, llm):
        self.backends[name] = llm
        if self.current_backend is None:
            self.current_backend = name

    def set_backend(self, name: str):
        if name not in self.backends:
            raise ValueError(f"Backend '{name}' not found")
        self.current_backend = name

    def query(self, question: str, backend: str = None) -> any:
        backend_name = backend or self.current_backend
        llm = self.backends[backend_name]
        smart_df = SmartDataframe(self.df, config={"llm": llm, "verbose": False})
        return smart_df.chat(question)

    def query_with_fallback(self, question: str, backend_order: list = None) -> tuple:
        backends_to_try = backend_order or list(self.backends.keys())
        for backend_name in backends_to_try:
            try:
                return self.query(question, backend_name), backend_name
            except Exception as e:
                print(f"Backend '{backend_name}' failed: {e}")
        raise RuntimeError("All backends failed")
```

**Backend summary table:**

| Provider | Class | Env Var | Default Model |
|----------|-------|---------|---------------|
| OpenAI | `OpenAI` | `OPENAI_API_KEY` | `gpt-4` |
| Anthropic | `Anthropic` | `ANTHROPIC_API_KEY` | `claude-3-opus-20240229` |
| Google | `GoogleGemini` | `GOOGLE_API_KEY` | `gemini-pro` |
| Azure OpenAI | `AzureOpenAI` | `AZURE_OPENAI_API_KEY` | deployment-specific |
| Local (Ollama) | `LocalLLM` | — | model_path arg |

### 5. Multi-DataFrame Analysis

```python
from pandasai import SmartDatalake

def create_smart_datalake(dataframes: dict, model: str = "gpt-4") -> SmartDatalake:
    llm = OpenAI(model=model, temperature=0)
    df_list = []
    for name, df in dataframes.items():
        df.name = name
        df_list.append(df)
    return SmartDatalake(df_list, config={"llm": llm, "verbose": True, "enable_cache": True})

# Cross-DataFrame query examples
cross_df_queries = [
    "What is the total revenue by customer segment?",
    "Which products are most popular among Enterprise customers?",
    "Show the monthly order trend by product category",
    "Find customers who have never ordered",
    "What is the average order value by region?",
    "Which product category has the highest profit margin?"
]
```

**DataWarehouseInterface — full pattern:**
```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TableSchema:
    name: str
    description: str
    columns: Dict[str, str]
    primary_key: str
    foreign_keys: Dict[str, str] = None


class DataWarehouseInterface:
    def __init__(self, model: str = "gpt-4"):
        self.llm = OpenAI(model=model, temperature=0)
        self.tables: Dict[str, pd.DataFrame] = {}
        self.schemas: Dict[str, TableSchema] = {}
        self.datalake: Optional[SmartDatalake] = None

    def add_table(self, name: str, df: pd.DataFrame, schema: TableSchema = None):
        df.name = name
        self.tables[name] = df
        if schema:
            self.schemas[name] = schema
        self._rebuild_datalake()

    def _rebuild_datalake(self):
        if self.tables:
            self.datalake = SmartDatalake(
                list(self.tables.values()),
                config={"llm": self.llm, "verbose": True, "enable_cache": True}
            )

    def query(self, question: str) -> any:
        if not self.datalake:
            raise ValueError("No tables loaded")
        return self.datalake.chat(question)
```

### 6. Privacy and Security Modes

```python
import hashlib

def anonymize_column(series: pd.Series, method: str = "hash") -> pd.Series:
    """
    Anonymize a column. Methods: 'hash', 'mask', 'generalize'.
    """
    if method == "hash":
        return series.apply(lambda x: hashlib.md5(str(x).encode()).hexdigest()[:8] if pd.notna(x) else x)
    elif method == "mask":
        return series.apply(lambda x: str(x)[:2] + "*" * (len(str(x)) - 2) if pd.notna(x) and len(str(x)) > 2 else "**")
    elif method == "generalize":
        if pd.api.types.is_numeric_dtype(series):
            return pd.cut(series, bins=5, labels=["Very Low", "Low", "Medium", "High", "Very High"])
        return series
    raise ValueError(f"Unknown method: {method}")


def create_privacy_safe_interface(
    df: pd.DataFrame,
    sensitive_columns: list,
    anonymization_method: str = "hash"
) -> SmartDataframe:
    safe_df = df.copy()
    for col in sensitive_columns:
        if col in safe_df.columns:
            safe_df[col] = anonymize_column(safe_df[col], anonymization_method)
    llm = OpenAI(model="gpt-4", temperature=0)
    return SmartDataframe(
        safe_df,
        config={"llm": llm, "verbose": False, "enforce_privacy": True, "enable_cache": False}
    )
```

---

## Integration Examples

### Streamlit Dashboard

```python
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

def create_streamlit_dashboard():
    st.title("Conversational Data Analysis")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())

        api_key = st.sidebar.text_input("OpenAI API Key", type="password")
        if api_key:
            llm = OpenAI(api_key=api_key, model="gpt-4", temperature=0)
            smart_df = SmartDataframe(df, config={"llm": llm, "verbose": False})

            query = st.text_area("Your question:", placeholder="e.g., What is total sales by region?")
            if st.button("Ask") and query:
                with st.spinner("Analyzing..."):
                    try:
                        result = smart_df.chat(query)
                        if isinstance(result, pd.DataFrame):
                            st.dataframe(result)
                        else:
                            st.write(result)
                        with st.expander("View Generated Code"):
                            st.code(smart_df.last_code_generated, language="python")
                    except Exception as e:
                        st.error(f"Error: {e}")

# Run with: streamlit run dashboard.py
```

### FastAPI Service

```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import io

app = FastAPI(title="PandasAI Query Service", version="1.0.0")

datasets: Dict[str, pd.DataFrame] = {}
smart_dfs: Dict[str, SmartDataframe] = {}


class QueryRequest(BaseModel):
    dataset_id: str
    question: str
    include_code: bool = False


@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...), dataset_id: Optional[str] = None):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported")
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    dataset_id = dataset_id or file.filename.replace(".csv", "")
    datasets[dataset_id] = df
    llm = OpenAI(model="gpt-4", temperature=0)
    smart_dfs[dataset_id] = SmartDataframe(df, config={"llm": llm, "verbose": False})
    return {"dataset_id": dataset_id, "message": "Dataset uploaded successfully"}


@app.post("/query")
async def query_dataset(request: QueryRequest):
    if request.dataset_id not in smart_dfs:
        raise HTTPException(404, f"Dataset '{request.dataset_id}' not found")
    try:
        result = smart_dfs[request.dataset_id].chat(request.question)
        result_type = "dataframe" if isinstance(result, pd.DataFrame) else "number" if isinstance(result, (int, float)) else "text"
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        return {"result": result, "result_type": result_type}
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")

# Run with: uvicorn api:app --reload
```

### Jupyter Notebook

```python
from IPython.display import display, Markdown

class JupyterPandasAI:
    def __init__(self, df: pd.DataFrame, model: str = "gpt-4"):
        self.df = df
        self.smart_df = SmartDataframe(
            df,
            config={"llm": OpenAI(model=model, temperature=0), "verbose": False,
                    "save_charts": True, "save_charts_path": "./notebook_charts"}
        )
        self.history = []

    def ask(self, question: str, show_code: bool = True) -> any:
        display(Markdown(f"**Question:** {question}"))
        result = self.smart_df.chat(question)
        self.history.append({"question": question, "result": result, "code": self.smart_df.last_code_generated})
        display(result)
        if show_code:
            display(Markdown(f"```python\n{self.smart_df.last_code_generated}\n```"))
        return result

    def explain(self, question: str) -> str:
        result = self.smart_df.chat(question)
        explanation = self.smart_df.chat(f"Explain in detail how you calculated: {question}")
        display(Markdown(f"**Result:** {result}\n\n**Explanation:** {explanation}"))
        return explanation

# Usage: jpa = JupyterPandasAI(df); jpa.ask("What is the average sales by region?")
```

---

## Best Practices

### Query Optimization

```python
# DO: Be specific
good_queries = [
    "What is the total revenue for Q1 2024?",
    "Show the top 5 products by units sold",
    "Calculate the average order value by customer segment"
]

# DON'T: Use vague questions
bad_queries = ["Tell me about the data", "What's interesting?", "Analyze everything"]

# DO: Break complex questions into steps
def multi_step_analysis(smart_df, questions):
    results = {}
    for i, q in enumerate(questions, 1):
        results[f"step_{i}"] = smart_df.chat(q)
    return results
```

### Error Handling with Retry

```python
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

def safe_query(smart_df: SmartDataframe, question: str, max_retries: int = 3) -> Tuple[any, Optional[str]]:
    for attempt in range(max_retries):
        try:
            return smart_df.chat(question), None
        except Exception as e:
            logger.warning(f"Query attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                return None, str(e)
    return None, "Max retries exceeded"
```

### Caching Strategy

```python
import hashlib

class CachedPandasAI:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.smart_df = SmartDataframe(df, config={"enable_cache": True})
        self._result_cache = {}

    def _get_cache_key(self, question: str) -> str:
        df_hash = hashlib.md5(pd.util.hash_pandas_object(self.df).values.tobytes()).hexdigest()[:8]
        q_hash = hashlib.md5(question.encode()).hexdigest()[:8]
        return f"{df_hash}_{q_hash}"

    def query(self, question: str, use_cache: bool = True) -> any:
        key = self._get_cache_key(question)
        if use_cache and key in self._result_cache:
            return self._result_cache[key]
        result = self.smart_df.chat(question)
        self._result_cache[key] = result
        return result

    def clear_cache(self):
        self._result_cache.clear()
```

### Cost Management

```python
class CostAwarePandasAI:
    COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4.1-mini": {"input": 0.0015, "output": 0.002}
    }

    def __init__(self, df: pd.DataFrame, model: str = "gpt-4", budget: float = 10.0):
        self.model = model
        self.budget = budget
        self.total_cost = 0.0
        llm = OpenAI(model=model, temperature=0)
        self.smart_df = SmartDataframe(df, config={"llm": llm, "verbose": False})

    def estimate_cost(self, question: str) -> float:
        costs = self.COSTS.get(self.model, self.COSTS["gpt-4"])
        return (len(question) / 4 / 1000 * costs["input"] + 500 / 1000 * costs["output"])

    def query(self, question: str) -> any:
        estimated = self.estimate_cost(question)
        if self.total_cost + estimated > self.budget:
            raise ValueError(f"Would exceed budget. Spent: ${self.total_cost:.4f}, Budget: ${self.budget}")
        result = self.smart_df.chat(question)
        self.total_cost += estimated
        return result
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `API key not found` | Env var not set | `export OPENAI_API_KEY="sk-..."` or pass `api_key=` explicitly |
| `Out of memory` | Large DataFrame | Sample: `df.sample(n=10000, random_state=42)` before wrapping |
| `Incorrect results` | Ambiguous query | Inspect `smart_df.last_code_generated`; be more specific |
| `Charts not generating` | Missing deps or backend | `pip install matplotlib seaborn plotly`; check `plt.get_backend()` |
| `Slow queries` | No caching | Set `"enable_cache": True` in config |
| `Rate limit errors` | Too many requests | Add retry logic with backoff; use `CostAwarePandasAI` |

### Verify Chart Dependencies

```python
def diagnose_chart_issues():
    import matplotlib
    print(f"Matplotlib: {matplotlib.__version__}, backend: {matplotlib.pyplot.get_backend()}")
    from pathlib import Path
    Path("./charts").mkdir(parents=True, exist_ok=True)
```

### API Key Verification

```python
import os

def verify_api_key(provider: str = "openai") -> bool:
    env_vars = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "google": "GOOGLE_API_KEY"}
    key = os.getenv(env_vars.get(provider, "OPENAI_API_KEY"))
    if not key:
        print(f"Error: {env_vars[provider]} not set")
        return False
    return True
```

---

## SmartDataframe Config Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `llm` | LLM object | required | LLM backend instance |
| `verbose` | bool | `False` | Print generated code |
| `enable_cache` | bool | `True` | Cache query results |
| `conversational` | bool | `False` | Maintain conversation context |
| `enforce_privacy` | bool | `False` | Enable privacy mode |
| `save_charts` | bool | `False` | Save generated charts to disk |
| `save_charts_path` | str | `"./charts"` | Chart save directory |
| `max_retries` | int | `3` | Max LLM retry attempts |
| `custom_whitelisted_dependencies` | list | `[]` | Extra imports to allow |

---

## Resources

- **PandasAI Documentation**: https://docs.pandas-ai.com/
- **GitHub Repository**: https://github.com/gventuri/pandas-ai
- **PyPI Package**: https://pypi.org/project/pandasai/
- **Examples Gallery**: https://github.com/gventuri/pandas-ai/tree/main/examples
