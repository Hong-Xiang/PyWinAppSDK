"""
Windows App SDK Python bindings - Foundation package.

This package provides Python bindings for Windows App SDK Foundation APIs.
"""

from winappsdk._bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

__all__ = ["initialize_windows_app_sdk", "BootstrapInitializeOptions"]
