---
name: api-integration-1-api-availability-checking
description: 'Sub-skill of api-integration: 1. API Availability Checking (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. API Availability Checking (+2)

## 1. API Availability Checking


```python
def check_api_availability(api_type: str) -> tuple[bool, str]:
    """
    Check if API is available and return status.

    Args:
        api_type: Type of API to check

    Returns:
        Tuple of (is_available, message)

    Example:
        >>> available, msg = check_api_availability('orcaflex')
        >>> if available:
        ...     print("OrcaFlex API is ready")
        >>> else:
        ...     print(f"Using mock: {msg}")
    """
    if api_type == 'orcaflex':
        try:
            import OrcFxAPI
            return True, "OrcaFlex API available"
        except ImportError:
            return False, "OrcaFlex not installed, using mock API"

    elif api_type == 'aqwa':
        # AQWA typically accessed via ANSYS Workbench
        # Check if ANSYS is available
        return False, "AQWA integration via ANSYS Workbench (mock mode)"

    else:
        return False, f"Unknown API type: {api_type}"
```


## 2. Configuration Management


```python
import yaml
from dataclasses import dataclass, asdict

@dataclass
class APIConfiguration:
    """Configuration for API integration."""
    api_type: str
    model_file: Optional[Path]
    output_dir: Path
    simulation_settings: dict
    retry_settings: dict

    def save_to_yaml(self, file_path: Path) -> None:
        """Save configuration to YAML file."""
        with open(file_path, 'w') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)

    @classmethod
    def load_from_yaml(cls, file_path: Path) -> 'APIConfiguration':
        """Load configuration from YAML file."""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        # Convert Path strings back to Path objects
        if 'model_file' in data and data['model_file']:
            data['model_file'] = Path(data['model_file'])
        data['output_dir'] = Path(data['output_dir'])
        return cls(**data)
```


## 3. Logging and Monitoring


```python
import logging
from datetime import datetime

def setup_api_logging(
    log_dir: Path,
    api_type: str
) -> logging.Logger:
    """
    Setup logging for API operations.

    Args:
        log_dir: Directory for log files
        api_type: Type of API

    Returns:
        Configured logger
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"{api_type}_api_{timestamp}.log"

    logger = logging.getLogger(f"{api_type}_api")
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
```
