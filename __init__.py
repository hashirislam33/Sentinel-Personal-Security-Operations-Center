"""
Sentinel - Personal Security Operations Center

A self-hosted, modular SOC platform for real-time security monitoring,
threat detection, and incident analysis.
"""

__version__ = "1.0.0"
__author__ = "Sentinel Team"

"""Configuration module initialization."""

from .settings import Settings, settings, get_settings

__all__ = ["Settings", "settings", "get_settings"]
