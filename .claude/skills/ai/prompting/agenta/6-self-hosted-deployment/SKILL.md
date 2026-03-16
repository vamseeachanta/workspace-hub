---
name: agenta-6-self-hosted-deployment
description: 'Sub-skill of agenta: 6. Self-Hosted Deployment.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 6. Self-Hosted Deployment

## 6. Self-Hosted Deployment


**Setting Up Self-Hosted Agenta:**
```python
"""
Configure and manage self-hosted Agenta deployment.
"""
import agenta as ag
from agenta import Agenta
from typing import Dict, Any, Optional
import os
import requests
from dataclasses import dataclass

@dataclass
class DeploymentConfig:
    """Configuration for self-hosted deployment."""
    host: str
    port: int
    api_key: Optional[str]
    database_url: str
    redis_url: Optional[str]
    enable_tracing: bool = True


class SelfHostedManager:
    """
    Manage self-hosted Agenta deployment.
    """

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}"
        self.client = None

    def initialize(self) -> bool:
        """
        Initialize connection to self-hosted instance.

        Returns:
            True if successful
        """
        try:
            # Set environment for SDK
            os.environ["AGENTA_HOST"] = self.base_url
            if self.config.api_key:
                os.environ["AGENTA_API_KEY"] = self.config.api_key

            # Initialize Agenta
            ag.init()
            self.client = Agenta()

            # Test connection
            response = requests.get(f"{self.base_url}/api/health")
            return response.status_code == 200

        except Exception as e:
            print(f"Initialization failed: {e}")
            return False

    def create_app(
        self,
        name: str,
        description: str = ""
    ) -> Dict:
        """
        Create a new application.

        Args:
            name: Application name
            description: Application description

        Returns:
            Created application details
        """
        return self.client.create_app(
            name=name,
            description=description
        )

    def deploy_variant(
        self,
        app_name: str,
        variant_name: str,
        environment: str = "production"
    ) -> Dict:
        """
        Deploy a variant to an environment.

        Args:
            app_name: Application name
            variant_name: Variant to deploy
            environment: Target environment

        Returns:
            Deployment details
        """
        # Get variant
        variants = self.client.list_variants(app_name=app_name)
        variant = next((v for v in variants if v.name == variant_name), None)

        if not variant:
            raise ValueError(f"Variant '{variant_name}' not found")

        # Deploy
        return self.client.deploy_variant(
            variant_id=variant.id,
            environment=environment
        )

    def get_deployment_status(self, app_name: str) -> Dict:
        """
        Get deployment status for an application.

        Args:
            app_name: Application name

        Returns:
            Deployment status
        """
        response = requests.get(
            f"{self.base_url}/api/apps/{app_name}/deployments",
            headers={"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}
        )

        return response.json()

    def configure_observability(
        self,
        tracing_endpoint: str = None,
        metrics_endpoint: str = None
    ) -> None:
        """
        Configure observability endpoints.

        Args:
            tracing_endpoint: Endpoint for traces (e.g., Jaeger)
            metrics_endpoint: Endpoint for metrics (e.g., Prometheus)
        """
        config = {}

        if tracing_endpoint:
            config["tracing"] = {
                "enabled": True,
                "endpoint": tracing_endpoint
            }

        if metrics_endpoint:
            config["metrics"] = {
                "enabled": True,
                "endpoint": metrics_endpoint
            }

        response = requests.post(
            f"{self.base_url}/api/config/observability",
            json=config,
            headers={"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to configure observability: {response.text}")


def generate_docker_compose(config: DeploymentConfig) -> str:
    """
    Generate docker-compose.yml for self-hosted deployment.

    Args:
        config: Deployment configuration

    Returns:
        Docker compose YAML content
    """
    compose = f"""version: '3.8'

services:
  agenta-backend:
    image: ghcr.io/agenta-ai/agenta-backend:latest
    ports:
      - "{config.port}:8000"
    environment:
      - DATABASE_URL={config.database_url}
      - REDIS_URL={config.redis_url or "redis://redis:6379"}
      - ENABLE_TRACING={str(config.enable_tracing).lower()}
    depends_on:
      - postgres

*Content truncated — see parent skill for full reference.*
