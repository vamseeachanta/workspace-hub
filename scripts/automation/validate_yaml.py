#!/usr/bin/env python3
"""
ABOUTME: YAML configuration validation tool for workspace-hub
ABOUTME: Validates YAML files against comprehensive schema standards
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import yaml
import jsonschema
from jsonschema import Draft7Validator, validators

# YAML Configuration Schema
YAML_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Workspace Hub Module Configuration",
    "type": "object",
    "required": ["module", "execution", "inputs", "outputs", "logging"],
    "properties": {
        "module": {
            "type": "object",
            "required": ["name", "version", "description"],
            "properties": {
                "name": {"type": "string", "pattern": "^[a-z0-9_-]+$"},
                "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                "description": {"type": "string", "minLength": 10}
            }
        },
        "execution": {
            "type": "object",
            "required": ["memory_limit_mb", "timeout_seconds"],
            "properties": {
                "memory_limit_mb": {"type": "integer", "minimum": 128, "maximum": 32768},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
                "max_retries": {"type": "integer", "minimum": 0, "maximum": 10},
                "parallel": {"type": "boolean"},
                "max_workers": {"type": "integer", "minimum": 1, "maximum": 64}
            }
        },
        "inputs": {
            "type": "object",
            "properties": {
                "required": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "description"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["string", "integer", "float", "boolean", "array", "object"]},
                            "description": {"type": "string"},
                            "validation": {"type": "string"}
                        }
                    }
                },
                "optional": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "default"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "default": {},
                            "choices": {"type": "array"}
                        }
                    }
                }
            }
        },
        "outputs": {
            "type": "object",
            "properties": {
                "primary": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "path"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "format": {"type": "string"},
                            "path": {"type": "string"}
                        }
                    }
                },
                "secondary": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "path"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "path": {"type": "string"}
                        }
                    }
                }
            }
        },
        "logging": {
            "type": "object",
            "required": ["level", "format"],
            "properties": {
                "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                "format": {"type": "string"},
                "handlers": {"type": "object"}
            }
        },
        "performance": {
            "type": "object",
            "properties": {
                "benchmarks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["metric", "threshold_seconds", "action_on_exceed"],
                        "properties": {
                            "metric": {"type": "string"},
                            "threshold_seconds": {"type": "number"},
                            "threshold_mb": {"type": "number"},
                            "action_on_exceed": {"type": "string", "enum": ["log_warning", "raise_error", "abort"]}
                        }
                    }
                }
            }
        },
        "error_handling": {
            "type": "object",
            "required": ["strategy"],
            "properties": {
                "strategy": {"type": "string", "enum": ["fail_fast", "continue_with_warnings", "retry"]},
                "on_error": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        },
        "validation": {
            "type": "object",
            "properties": {
                "pre_execution": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "post_execution": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
}


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Failed to load YAML file: {e}", file=sys.stderr)
        sys.exit(1)


def validate_schema(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate configuration against schema."""
    validator = Draft7Validator(YAML_SCHEMA)
    errors = []

    for error in sorted(validator.iter_errors(config), key=str):
        errors.append(f"{'.'.join(str(p) for p in error.path)}: {error.message}")

    return len(errors) == 0, errors


def validate_file_paths(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate that referenced file paths exist."""
    errors = []

    # Check input file paths if specified
    inputs = config.get("inputs", {})
    for input_list in [inputs.get("required", []), inputs.get("optional", [])]:
        for inp in input_list:
            if "path" in inp and not Path(inp["path"]).exists():
                errors.append(f"Input path does not exist: {inp['path']}")

    return len(errors) == 0, errors


def validate_resource_limits(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate resource limits are reasonable."""
    errors = []
    execution = config.get("execution", {})

    # Check memory limit
    memory_mb = execution.get("memory_limit_mb", 0)
    if memory_mb > 16384:
        errors.append(f"WARNING: High memory limit: {memory_mb}MB (>16GB)")

    # Check timeout
    timeout_sec = execution.get("timeout_seconds", 0)
    if timeout_sec > 3600:
        errors.append(f"WARNING: Long timeout: {timeout_sec}s (>1 hour)")

    return len(errors) == 0, errors


def validate_logging_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate logging configuration."""
    errors = []
    logging = config.get("logging", {})

    # Ensure logging level is valid
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    level = logging.get("level")
    if level not in valid_levels:
        errors.append(f"Invalid logging level: {level}. Must be one of {valid_levels}")

    # Check format string
    if "format" not in logging:
        errors.append("Missing logging format string")

    return len(errors) == 0, errors


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate YAML configuration files against workspace-hub standards"
    )
    parser.add_argument(
        "config_file",
        type=Path,
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Only validate against schema, skip additional checks"
    )
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if not args.config_file.exists():
        print(f"ERROR: Configuration file not found: {args.config_file}", file=sys.stderr)
        return 1

    # Load configuration
    if args.verbose:
        print(f"Loading configuration from: {args.config_file}")

    config = load_yaml(args.config_file)

    # Run validations
    all_valid = True
    all_errors = []

    # 1. Schema validation
    print("Validating schema...")
    schema_valid, schema_errors = validate_schema(config)
    if not schema_valid:
        all_valid = False
        all_errors.extend(["SCHEMA ERROR: " + e for e in schema_errors])
    else:
        print("✓ Schema validation passed")

    if args.schema_only:
        if all_valid:
            print("\n✓ Configuration is valid")
            return 0
        else:
            print("\n✗ Configuration validation failed:")
            for error in all_errors:
                print(f"  - {error}")
            return 1

    # 2. File path validation
    print("Validating file paths...")
    paths_valid, path_errors = validate_file_paths(config)
    if not paths_valid:
        all_errors.extend(["PATH ERROR: " + e for e in path_errors])
        if not args.warnings_as_errors:
            print("⚠ File path warnings (not blocking)")
    else:
        print("✓ File path validation passed")

    # 3. Resource limit validation
    print("Validating resource limits...")
    resources_valid, resource_errors = validate_resource_limits(config)
    if not resources_valid:
        all_errors.extend(resource_errors)
        if not args.warnings_as_errors:
            print("⚠ Resource limit warnings (not blocking)")
    else:
        print("✓ Resource limit validation passed")

    # 4. Logging configuration validation
    print("Validating logging configuration...")
    logging_valid, logging_errors = validate_logging_config(config)
    if not logging_valid:
        all_valid = False
        all_errors.extend(["LOGGING ERROR: " + e for e in logging_errors])
    else:
        print("✓ Logging configuration validation passed")

    # Print summary
    print("\n" + "="*50)
    if all_valid:
        print("✓ Configuration validation PASSED")
        print(f"  File: {args.config_file}")
        print(f"  Module: {config.get('module', {}).get('name', 'unknown')}")
        print(f"  Version: {config.get('module', {}).get('version', 'unknown')}")
        return 0
    else:
        print("✗ Configuration validation FAILED")
        print(f"\n{len(all_errors)} error(s) found:")
        for error in all_errors:
            print(f"  - {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
