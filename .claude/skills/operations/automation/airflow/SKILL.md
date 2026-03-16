---
name: airflow
version: 1.0.0
description: Python DAG workflow orchestration using Apache Airflow for data pipelines,
  ETL processes, and scheduled task automation
author: workspace-hub
category: operations
type: skill
capabilities:
- dag_authoring
- task_orchestration
- scheduling
- sensors
- operators
- hooks
- xcoms
- variables
- connections
- kubernetes_deployment
- docker_deployment
tools:
- airflow-cli
- docker
- kubernetes
- helm
tags:
- airflow
- dag
- workflow
- orchestration
- etl
- data-pipeline
- scheduling
- python
- automation
platforms:
- linux
- macos
- docker
- kubernetes
related_skills:
- yaml-configuration
- python-scientific-computing
- pandas-data-processing
scripts_exempt: true
see_also:
- airflow-2-advanced-operators
---

# Airflow

## When to Use This Skill

### USE when:

- Building complex data pipelines with task dependencies
- Orchestrating ETL/ELT workflows
- Scheduling recurring batch jobs
- Managing workflows with retries and error handling
- Coordinating tasks across multiple systems
- Need visibility into workflow execution history
- Requiring audit trails and lineage tracking
- Building ML pipeline orchestration
### DON'T USE when:

- Real-time streaming data (use Kafka, Flink)
- Simple cron jobs (use systemd timers, crontab)
- CI/CD pipelines (use GitHub Actions, Jenkins)
- Low-latency requirements (Airflow has scheduler overhead)
- Simple single-task automation (overkill)
- Need visual workflow design for non-developers (use n8n)

## Prerequisites

### Installation Options

**Option 1: pip (Development)**
```bash
# Create virtual environment
python -m venv airflow-env
source airflow-env/bin/activate

# Set Airflow home
export AIRFLOW_HOME=~/airflow

# Install Airflow with constraints

*See sub-skills for full details.*
### Development Setup

```bash
# Install development dependencies
pip install apache-airflow[dev,postgres,celery,kubernetes]

# Install testing tools
pip install pytest pytest-airflow

# Install linting
pip install ruff
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive workflow patterns |

## Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Airflow Helm Chart](https://airflow.apache.org/docs/helm-chart/stable/index.html)
- [Astronomer Guides](https://www.astronomer.io/guides/)
- [Airflow Providers](https://airflow.apache.org/docs/apache-airflow-providers/)

---

*This skill provides production-ready patterns for Apache Airflow workflow orchestration, tested across enterprise data pipelines.*

## Sub-Skills

- [1. Basic DAG Structure](1-basic-dag-structure/SKILL.md)
- [Integration with AWS Services](integration-with-aws-services/SKILL.md)
- [1. DAG Design Principles (+3)](1-dag-design-principles/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)

## Sub-Skills

- [2. Advanced Operators (+6)](2-advanced-operators/SKILL.md)
