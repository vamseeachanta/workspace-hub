---
name: langchain-2-agent-with-tools
description: 'Sub-skill of langchain: 2. Agent with Tools.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 2. Agent with Tools

## 2. Agent with Tools


**ReAct Agent with Custom Tools:**
```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool
from langchain import hub
from typing import Optional
import requests
import json

@tool
def calculate_mooring_tension(
    depth: float,
    line_length: float,
    pretension: float,
    offset: float
) -> str:
    """
    Calculate approximate mooring line tension given parameters.

    Args:
        depth: Water depth in meters
        line_length: Mooring line length in meters
        pretension: Initial pretension in kN
        offset: Horizontal vessel offset in meters

    Returns:
        Tension calculation result
    """
    # Simplified catenary calculation
    import math

    suspended_length = math.sqrt(line_length**2 - depth**2)
    stretch_factor = 1 + (offset / suspended_length) * 0.1
    tension = pretension * stretch_factor

    return json.dumps({
        "horizontal_tension_kN": round(tension, 2),
        "vertical_tension_kN": round(tension * (depth / line_length), 2),
        "line_angle_deg": round(math.degrees(math.asin(depth / line_length)), 1)
    })

@tool
def get_wave_data(location: str, date: Optional[str] = None) -> str:
    """
    Get wave condition data for a location.

    Args:
        location: Location name or coordinates
        date: Date in YYYY-MM-DD format (optional)

    Returns:
        Wave data including Hs, Tp, direction
    """
    # Simulated data - replace with actual API call
    wave_data = {
        "location": location,
        "significant_wave_height_m": 2.5,
        "peak_period_s": 8.5,
        "wave_direction_deg": 225,
        "data_source": "simulated"
    }
    return json.dumps(wave_data)

@tool
def search_engineering_database(query: str) -> str:
    """
    Search the engineering standards database.

    Args:
        query: Search query for standards/specifications

    Returns:
        Relevant standards and references
    """
    # Simulated database - replace with actual search
    results = {
        "query": query,
        "results": [
            {"standard": "API RP 2SK", "title": "Design and Analysis of Stationkeeping Systems"},
            {"standard": "DNV-OS-E301", "title": "Position Mooring"},
            {"standard": "ISO 19901-7", "title": "Stationkeeping systems"}
        ]
    }
    return json.dumps(results)

def create_engineering_agent():
    """
    Create an agent with engineering-specific tools.
    """
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    # Define tools
    tools = [
        calculate_mooring_tension,
        get_wave_data,
        search_engineering_database
    ]

    # Get ReAct prompt from hub
    prompt = hub.pull("hwchase17/react")

    # Create agent
    agent = create_react_agent(llm, tools, prompt)

    # Create executor with error handling
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent_executor

# Usage
agent = create_engineering_agent()

response = agent.invoke({
    "input": """
    I need to analyze a mooring system in 100m water depth.
    The lines are 350m long with 500kN pretension.
    What would be the tension if the vessel offset is 15m?
    Also, what standards should I reference?
    """
})

print(response["output"])
```

**Tool Agent with Structured Output:**
```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List

class AnalysisResult(BaseModel):
    """Structured analysis result."""
    summary: str = Field(description="Brief summary of findings")
    key_findings: List[str] = Field(description="List of key findings")
    recommendations: List[str] = Field(description="List of recommendations")
    risk_level: str = Field(description="Risk level: low, medium, or high")

@tool
def analyze_document(document_path: str) -> str:
    """
    Analyze an engineering document and extract key information.

    Args:
        document_path: Path to the document

    Returns:
        Extracted information from document
    """
    # Simulated document analysis
    return """
    Document: Mooring Analysis Report
    Key findings:
    - Maximum tension: 2500 kN (within limits)
    - Safety factor: 1.8 (above minimum 1.67)
    - Fatigue life: 45 years (design life: 25 years)
    Recommendations:
    - Monitor chain condition at fairlead
    - Consider dynamic analysis for extreme conditions
    """

def create_structured_agent():
    """Create agent that returns structured output."""

    llm = ChatOpenAI(model="gpt-4", temperature=0)

    tools = [analyze_document]

    system_prompt = """You are an engineering analysis assistant.
    Use the available tools to analyze documents and provide structured insights.
    Always provide your final answer in a structured format with:
    - summary
    - key_findings (list)
    - recommendations (list)

*Content truncated — see parent skill for full reference.*
