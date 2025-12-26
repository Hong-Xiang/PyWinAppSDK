"""
Windows App SDK Bootstrap initialization.

This module provides Pythonic access to the Windows App SDK Bootstrap API,
which is required to initialize the Windows App SDK runtime for unpackaged apps.

Example:
    from winappsdk.bootstrap import initialize_windows_app_sdk
    
    with initialize_windows_app_sdk():
        # Use Windows App SDK APIs
        picker = FileOpenPicker(window_id)
"""

from winappsdk.bootstrap._bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

__all__ = ["initialize_windows_app_sdk", "BootstrapInitializeOptions"]
