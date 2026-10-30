"""Fail-closed projections of privately owned identity records."""

from .policy import ExposureError, RegistryRecord, Surface, expose
from .registry import load_registry

__all__ = ["ExposureError", "RegistryRecord", "Surface", "expose", "load_registry"]
