---
name: dspy-1-signatures
description: 'Sub-skill of dspy: 1. Signatures.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Signatures

## 1. Signatures


**Basic Signatures:**
```python
import dspy

# Configure LLM
lm = dspy.OpenAI(model="gpt-4", max_tokens=1000)
dspy.settings.configure(lm=lm)

# Inline signature (simple)
classify = dspy.Predict("document -> category")
result = classify(document="The mooring line tension exceeded limits.")
print(result.category)

# Class-based signature (recommended)
class SentimentAnalysis(dspy.Signature):
    """Analyze the sentiment of engineering feedback."""

    feedback = dspy.InputField(desc="Engineering feedback or review text")
    sentiment = dspy.OutputField(desc="Sentiment: positive, negative, or neutral")
    confidence = dspy.OutputField(desc="Confidence score 0-1")

# Use signature
analyzer = dspy.Predict(SentimentAnalysis)
result = analyzer(feedback="The mooring design passed all safety checks.")
print(f"Sentiment: {result.sentiment}, Confidence: {result.confidence}")
```

**Complex Signatures with Multiple Fields:**
```python
class EngineeringAnalysis(dspy.Signature):
    """Analyze an engineering report and extract key insights."""

    report_text = dspy.InputField(
        desc="Full text of the engineering report"
    )
    domain = dspy.InputField(
        desc="Engineering domain (offshore, structural, mechanical)"
    )

    summary = dspy.OutputField(
        desc="Concise 2-3 sentence summary of findings"
    )
    key_metrics = dspy.OutputField(
        desc="List of key metrics mentioned with values"
    )
    risk_factors = dspy.OutputField(
        desc="Identified risk factors and concerns"
    )
    recommendations = dspy.OutputField(
        desc="Actionable recommendations from the report"
    )
    confidence_level = dspy.OutputField(
        desc="Overall confidence in analysis: high, medium, or low"
    )

# Create predictor
report_analyzer = dspy.Predict(EngineeringAnalysis)

# Analyze report
result = report_analyzer(
    report_text="""
    The mooring analysis for Platform Alpha shows maximum tensions
    of 2,450 kN under 100-year storm conditions. Safety factors
    range from 1.72 to 2.15 across all lines. Line 3 shows the
    lowest margin at the fairlead connection. Fatigue life estimates
    indicate 35-year service life, exceeding the 25-year requirement.
    Chain wear measurements show 8% diameter loss after 5 years.
    """,
    domain="offshore"
)

print(f"Summary: {result.summary}")
print(f"Key Metrics: {result.key_metrics}")
print(f"Risk Factors: {result.risk_factors}")
print(f"Recommendations: {result.recommendations}")
```
