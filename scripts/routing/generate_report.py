
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Configuration
LOG_FILE = 'scripts/routing/logs/provider_recommendations.jsonl'
REPORT_FILE = 'reports/orchestration_report.html'

def load_data():
    if not os.path.exists(LOG_FILE):
        return None
    
    data = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            entry = json.loads(line)
            # Flatten some fields
            row = {
                'timestamp': entry['timestamp'],
                'provider': entry['recommendation']['provider'],
                'cost': float(entry['recommendation']['cost_estimate']),
                'primary': entry['task_classification']['primary_provider'],
                'reason': entry['recommendation']['reason']
            }
            data.append(row)
    return pd.DataFrame(data)

def generate_report():
    df = load_data()
    if df is None or df.empty:
        print("No data found to generate report.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "domain"}, {"type": "xy"}],
               [{"type": "xy"}, {"type": "xy"}]],
        subplot_titles=("Provider Distribution", "Cost Over Time", 
                        "Primary vs Fallback", "Daily Task Volume")
    )

    # 1. Provider Distribution
    provider_counts = df['provider'].value_counts()
    fig.add_trace(
        go.Pie(labels=provider_counts.index, values=provider_counts.values, name="Providers"),
        row=1, col=1
    )

    # 2. Cost Over Time
    df_sorted = df.sort_values('timestamp')
    fig.add_trace(
        go.Scatter(x=df_sorted['timestamp'], y=df_sorted['cost'].cumsum(), name="Cumulative Cost", fill='tozeroy'),
        row=1, col=2
    )

    # 3. Primary vs Fallback
    df['is_fallback'] = df['reason'].apply(lambda x: "Fallback" if "fallback" in x.lower() else "Primary")
    fallback_counts = df['is_fallback'].value_counts()
    fig.add_trace(
        go.Bar(x=fallback_counts.index, y=fallback_counts.values, name="Success Mode"),
        row=2, col=1
    )

    # 4. Daily Volume
    daily_volume = df.groupby(df['timestamp'].dt.date).size()
    fig.add_trace(
        go.Bar(x=daily_volume.index, y=daily_volume.values, name="Daily Volume"),
        row=2, col=2
    )

    # Layout updates
    fig.update_layout(
        height=800, 
        showlegend=True,
        title_text="Multi-Provider Orchestration Monitoring Dashboard",
        template="plotly_dark"
    )

    # Ensure reports directory exists
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    
    fig.write_html(REPORT_FILE)
    print(f"Report generated: {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
