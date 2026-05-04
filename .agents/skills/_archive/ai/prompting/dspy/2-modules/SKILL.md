---
name: dspy-2-modules
description: 'Sub-skill of dspy: 2. Modules.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 2. Modules

## 2. Modules


**ChainOfThought for Complex Reasoning:**
```python
class TechnicalQA(dspy.Signature):
    """Answer technical engineering questions with reasoning."""

    context = dspy.InputField(desc="Technical context and background")
    question = dspy.InputField(desc="Technical question to answer")
    answer = dspy.OutputField(desc="Detailed technical answer")

# ChainOfThought adds reasoning before answering
class TechnicalExpert(dspy.Module):
    def __init__(self):
        super().__init__()
        self.answer_question = dspy.ChainOfThought(TechnicalQA)

    def forward(self, context, question):
        result = self.answer_question(context=context, question=question)
        return result

# Usage
expert = TechnicalExpert()

result = expert(
    context="""
    Catenary mooring systems use the weight of the chain to provide
    restoring force. The touchdown point moves as the vessel offsets.
    Line tension is a function of the catenary geometry and pretension.
    """,
    question="How does water depth affect mooring line tension?"
)

print(f"Reasoning: {result.rationale}")
print(f"Answer: {result.answer}")
```

**Multi-Stage Pipeline Module:**
```python
class DocumentSummary(dspy.Signature):
    """Summarize a technical document."""
    document = dspy.InputField()
    summary = dspy.OutputField()

class KeyPointExtraction(dspy.Signature):
    """Extract key points from a summary."""
    summary = dspy.InputField()
    key_points = dspy.OutputField(desc="List of 3-5 key points")

class ActionItemGeneration(dspy.Signature):
    """Generate action items from key points."""
    key_points = dspy.InputField()
    action_items = dspy.OutputField(desc="List of actionable next steps")

class DocumentProcessor(dspy.Module):
    """Multi-stage document processing pipeline."""

    def __init__(self):
        super().__init__()
        self.summarize = dspy.ChainOfThought(DocumentSummary)
        self.extract_points = dspy.Predict(KeyPointExtraction)
        self.generate_actions = dspy.Predict(ActionItemGeneration)

    def forward(self, document):
        # Stage 1: Summarize
        summary_result = self.summarize(document=document)

        # Stage 2: Extract key points
        points_result = self.extract_points(summary=summary_result.summary)

        # Stage 3: Generate actions
        actions_result = self.generate_actions(key_points=points_result.key_points)

        return dspy.Prediction(
            summary=summary_result.summary,
            key_points=points_result.key_points,
            action_items=actions_result.action_items
        )

# Usage
processor = DocumentProcessor()
result = processor(document="[Long engineering document text...]")

print(f"Summary: {result.summary}")
print(f"Key Points: {result.key_points}")
print(f"Actions: {result.action_items}")
```

**ReAct Module for Tool Use:**
```python
class CalculateTension(dspy.Signature):
    """Calculate mooring line tension."""
    depth = dspy.InputField(desc="Water depth in meters")
    line_length = dspy.InputField(desc="Line length in meters")
    pretension = dspy.InputField(desc="Pretension in kN")
    result = dspy.OutputField(desc="Tension calculation result")

class SearchStandards(dspy.Signature):
    """Search engineering standards database."""
    query = dspy.InputField(desc="Search query")
    standards = dspy.OutputField(desc="Relevant standards found")

class EngineeringReActAgent(dspy.Module):
    """Agent that can reason and act using tools."""

    def __init__(self):
        super().__init__()
        self.react = dspy.ReAct(
            signature="question -> answer",
            tools=[self.calculate_tension, self.search_standards]
        )

    def calculate_tension(self, depth: float, line_length: float, pretension: float) -> str:
        """Calculate approximate mooring line tension."""
        import math
        suspended = math.sqrt(line_length**2 - depth**2)
        tension = pretension * (1 + depth / suspended * 0.1)
        return f"Estimated tension: {tension:.1f} kN"

    def search_standards(self, query: str) -> str:
        """Search for relevant engineering standards."""
        standards_db = {
            "mooring": ["API RP 2SK", "DNV-OS-E301", "ISO 19901-7"],
            "fatigue": ["DNV-RP-C203", "API RP 2A-WSD"],
            "structural": ["AISC 360", "API RP 2A-WSD"]
        }
        for key, value in standards_db.items():
            if key in query.lower():
                return f"Relevant standards: {', '.join(value)}"
        return "No specific standards found for query"

    def forward(self, question):
        return self.react(question=question)

# Usage
agent = EngineeringReActAgent()
result = agent(
    question="What is the tension for a 350m line in 100m depth with 500kN pretension?"
)
print(result.answer)
```
