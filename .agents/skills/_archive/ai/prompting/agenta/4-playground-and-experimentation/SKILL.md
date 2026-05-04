---
name: agenta-4-playground-and-experimentation
description: 'Sub-skill of agenta: 4. Playground and Experimentation.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 4. Playground and Experimentation

## 4. Playground and Experimentation


**Creating Interactive Playground:**
```python
"""
Build an interactive playground for prompt experimentation.
"""
import agenta as ag
from agenta import Agenta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ExperimentRun:
    """Single experiment run."""
    run_id: str
    prompt: str
    parameters: Dict[str, Any]
    output: str
    metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


class Playground:
    """
    Interactive playground for prompt experimentation.
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.client = Agenta()
        self.experiments: List[ExperimentRun] = []
        self.current_prompt = ""
        self.current_params = {}

    def set_prompt(self, prompt: str) -> 'Playground':
        """Set the current prompt template."""
        self.current_prompt = prompt
        return self

    def set_parameters(self, **params) -> 'Playground':
        """Set LLM parameters."""
        self.current_params.update(params)
        return self

    def run(self, input_data: str) -> ExperimentRun:
        """
        Run the current prompt with input.

        Args:
            input_data: Input to format into prompt

        Returns:
            ExperimentRun with results
        """
        import time
        import uuid

        # Format prompt
        formatted_prompt = self.current_prompt.format(input=input_data)

        # Run with timing
        start_time = time.time()
        response = ag.llm.complete(
            prompt=formatted_prompt,
            **self.current_params
        )
        latency = time.time() - start_time

        # Create run record
        run = ExperimentRun(
            run_id=str(uuid.uuid4())[:8],
            prompt=formatted_prompt,
            parameters=self.current_params.copy(),
            output=response.text,
            metrics={
                "latency": latency,
                "output_length": len(response.text),
                "tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
        )

        self.experiments.append(run)

        return run

    def compare(
        self,
        prompts: List[str],
        test_input: str,
        parameters: Dict = None
    ) -> List[ExperimentRun]:
        """
        Compare multiple prompts with same input.

        Args:
            prompts: List of prompt templates
            test_input: Input to test
            parameters: Shared parameters

        Returns:
            List of ExperimentRuns
        """
        runs = []
        original_prompt = self.current_prompt
        original_params = self.current_params.copy()

        if parameters:
            self.set_parameters(**parameters)

        for prompt in prompts:
            self.set_prompt(prompt)
            run = self.run(test_input)
            runs.append(run)

        # Restore original state
        self.current_prompt = original_prompt
        self.current_params = original_params

        return runs

    def parameter_sweep(
        self,
        param_name: str,
        values: List[Any],
        test_input: str
    ) -> List[ExperimentRun]:
        """
        Sweep over parameter values.

        Args:
            param_name: Parameter to sweep
            values: List of values to try
            test_input: Input for testing

        Returns:
            List of ExperimentRuns
        """
        runs = []
        original_value = self.current_params.get(param_name)

        for value in values:
            self.current_params[param_name] = value
            run = self.run(test_input)
            runs.append(run)

        # Restore original value
        if original_value is not None:
            self.current_params[param_name] = original_value
        else:
            self.current_params.pop(param_name, None)

        return runs

    def get_history(self, limit: int = 10) -> List[ExperimentRun]:
        """Get recent experiment history."""
        return self.experiments[-limit:]

    def export_experiments(self, filepath: str) -> None:
        """Export experiments to JSON file."""
        data = []
        for exp in self.experiments:
            data.append({
                "run_id": exp.run_id,
                "prompt": exp.prompt,
                "parameters": exp.parameters,
                "output": exp.output,
                "metrics": exp.metrics,
                "timestamp": exp.timestamp.isoformat()
            })

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def find_best_run(self, metric: str = "latency", minimize: bool = True) -> Optional[ExperimentRun]:
        """
        Find the best run based on a metric.

        Args:
            metric: Metric to optimize
            minimize: Whether to minimize (True) or maximize (False)

        Returns:
            Best ExperimentRun or None

*Content truncated — see parent skill for full reference.*
