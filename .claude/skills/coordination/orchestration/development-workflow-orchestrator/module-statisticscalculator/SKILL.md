---
name: development-workflow-orchestrator-module-statisticscalculator
description: 'Sub-skill of development-workflow-orchestrator: Module: StatisticsCalculator.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Module: StatisticsCalculator

## Module: StatisticsCalculator


```
FUNCTION calculate_statistics(data, config):
  statistics = empty_dictionary

  FOR EACH statistic_type IN config.statistics_types:
    CASE statistic_type:
      WHEN "mean":
        statistics["mean"] = CALCULATE_MEAN(data)
      WHEN "median":
        statistics["median"] = CALCULATE_MEDIAN(data)
      WHEN "std":
        statistics["std"] = CALCULATE_STD(data)
      WHEN "quantiles":
        statistics["quantiles"] = CALCULATE_QUANTILES(data, [0.25, 0.5, 0.75])

  RETURN statistics
```
