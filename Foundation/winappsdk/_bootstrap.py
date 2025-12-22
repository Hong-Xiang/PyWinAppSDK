"""
Windows App SDK Bootstrap initialization.

This module provides Pythonic access to the Windows App SDK Bootstrap API,
which is required to initialize the Windows App SDK runtime for unpackaged apps.

Example:
    from winappsdk import initialize_windows_app_sdk
    
    with initialize_windows_app_sdk():
        # Use Windows App SDK APIs
        picker = FileOpenPicker(window_id)
"""

import ctypes
import os
import sys
import struct
from contextlib import contextmanager
from ctypes import wintypes
from typing import Optional


class BootstrapInitializeOptions:
    """Options for MddBootstrapInitialize."""
    NONE = 0
    ON_NO_MATCH_SHOW_UI = 0x00000001
    ON_PACKAGE_IDENTITY_SHOW_UI = 0x00000002
    ON_ERROR_SHOW_UI = ON_NO_MATCH_SHOW_UI | ON_PACKAGE_IDENTITY_SHOW_UI


class _PackageVersion(ctypes.Structure):
    """PACKAGE_VERSION structure for Windows App SDK."""
    _fields_ = [
        ("Revision", wintypes.USHORT),
        ("Build", wintypes.USHORT),
        ("Minor", wintypes.USHORT),
        ("Major", wintypes.USHORT),
    ]
    
    @classmethod
    def from_string(cls, version_str: str) -> "_PackageVersion":
        """Create from version string like '1.8.0.0'."""
        parts = version_str.split(".")
        while len(parts) < 4:
            parts.append("0")
        return cls(
            Revision=int(parts[3]),
            Build=int(parts[2]),
            Minor=int(parts[1]),
            Major=int(parts[0]),
        )


def _get_platform_architecture() -> str:
    """
    Determine the architecture folder name based on Python's bitness.
    
    Returns one of: 'win-x64', 'win-x86', 'win-arm64'
    """
    pointer_size = struct.calcsize("P") * 8
    
    if pointer_size == 64:
        # Check architecture from sys.version
        if "AMD64" in sys.version:
            return "win-x64"
        elif "ARM64" in sys.version:
            return "win-arm64"
        else:
            return "win-x64"  # Default to x64 for 64-bit
    else:
        return "win-x86"


def _find_bootstrap_dll() -> Optional[str]:
    """
    Find the Windows App SDK bootstrap DLL.
    
    Searches in the following order:
    1. Package-bundled DLL (in the same directory as this module)
    2. System PATH
    3. Installed Windows App Runtime package (via PowerShell)
    
    Returns:
        Path to the DLL, or None if not found.
    """
    arch = _get_platform_architecture()
    dll_name = "Microsoft.WindowsAppRuntime.Bootstrap.dll"
    
    # 1. Check package-bundled DLL (in winappsdk package directory)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_dll = os.path.join(module_dir, arch, dll_name)
    if os.path.exists(bundled_dll):
        return bundled_dll
    
    # 2. Check if it's in PATH
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        dll_path = os.path.join(path_dir, dll_name)
        if os.path.exists(dll_path):
            return dll_path
    
    # 3. Try to find installed runtime package
    try:
        import subprocess
        
        # Map architecture to runtime package architecture name
        runtime_arch = {
            "win-x64": "X64",
            "win-x86": "X86",
            "win-arm64": "ARM64",
        }.get(arch, "X64")
        
        result = subprocess.run(
            ['powershell', '-Command', 
             f'Get-AppxPackage -Name "*WindowsAppRuntime.1.8*" | '
             f'Where-Object {{ $_.Architecture -eq "{runtime_arch}" }} | '
             f'Select-Object -First 1 -ExpandProperty InstallLocation'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if result.returncode == 0:
            runtime_path = result.stdout.strip()
            if runtime_path and os.path.exists(runtime_path):
                dll_path = os.path.join(runtime_path, dll_name)
                if os.path.exists(dll_path):
                    return dll_path
    except Exception:
        pass  # Silently fail and return None
    
    return None


def _get_runtime_path() -> Optional[str]:
    """
    Get the Windows App Runtime framework DLLs path.
    
    Returns:
        Path to the runtime DLLs directory, or None if not found.
    """
    arch = _get_platform_architecture()
    
    # Map architecture to runtime package architecture name
    runtime_arch = {
        "win-x64": "X64",
        "win-x86": "X86",
        "win-arm64": "ARM64",
    }.get(arch, "X64")
    
    try:
        import subprocess
        
        result = subprocess.run(
            ['powershell', '-Command', 
             f'Get-AppxPackage -Name "*WindowsAppRuntime.1.8*" | '
             f'Where-Object {{ $_.Architecture -eq "{runtime_arch}" }} | '
             f'Select-Object -First 1 -ExpandProperty InstallLocation'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if result.returncode == 0:
            runtime_path = result.stdout.strip()
            if runtime_path and os.path.exists(runtime_path):
                return runtime_path
    except Exception:
        pass
    
    return None


@contextmanager
def initialize_windows_app_sdk(
    major_minor_version: str = "1.8",
    min_version: Optional[str] = None,
    options: int = BootstrapInitializeOptions.NONE,
    verbose: bool = False
):
    """
    Initialize the Windows App SDK runtime using MddBootstrapInitialize.
    
    This context manager initializes the Windows App SDK for unpackaged apps
    and automatically shuts it down when the context exits.
    
    Args:
        major_minor_version: Version like "1.8" or "1.7"
        min_version: Minimum version like "8000.0.0.0" (optional)
        options: BootstrapInitializeOptions flags
        verbose: Print detailed initialization information
    
    Raises:
        FileNotFoundError: If bootstrap DLL cannot be found
        OSError: If bootstrap initialization fails
    
    Example:
        with initialize_windows_app_sdk():
            picker = FileOpenPicker(window_id)
            file = await picker.pick_single_file_async()
    """
    # Find the bootstrap DLL
    dll_path = _find_bootstrap_dll()
    if not dll_path:
        raise FileNotFoundError(
            "Could not find Microsoft.WindowsAppRuntime.Bootstrap.dll. "
            "Please install the Windows App SDK runtime:\n"
            "  winget install Microsoft.WindowsAppSDK.1.8"
        )
    
    if verbose:
        print(f"Loading bootstrap DLL: {dll_path}")
    
    # Add runtime DLLs to PATH
    old_path = os.environ.get('PATH', '')
    runtime_path = _get_runtime_path()
    
    if runtime_path:
        dll_dir = os.path.dirname(dll_path)
        os.environ['PATH'] = runtime_path + os.pathsep + dll_dir + os.pathsep + old_path
        if verbose:
            print(f"Added runtime DLLs to PATH: {runtime_path}")
    else:
        dll_dir = os.path.dirname(dll_path)
        os.environ['PATH'] = dll_dir + os.pathsep + old_path
        if verbose:
            print(f"⚠️  Could not find installed Windows App Runtime package")
    
    try:
        # Set error mode to prevent crash dialogs during DLL loading
        kernel32 = ctypes.windll.kernel32
        SEM_FAILCRITICALERRORS = 0x0001
        old_mode = kernel32.SetErrorMode(SEM_FAILCRITICALERRORS)
        
        bootstrap = ctypes.CDLL(dll_path)
        
        # Restore error mode
        kernel32.SetErrorMode(old_mode)
    except OSError as e:
        # Restore original PATH on error
        os.environ['PATH'] = old_path
        error_msg = f"Failed to load bootstrap DLL: {e}"
        if hasattr(e, 'winerror'):
            error_msg += f"\n  HRESULT: 0x{e.winerror & 0xFFFFFFFF:08X}"
        error_msg += (
            "\n\nThis might be due to missing dependencies. Try:\n"
            "  1. Install Windows App SDK runtime: winget install Microsoft.WindowsAppSDK.1.8\n"
            "  2. Or add the Framework DLLs to PATH"
        )
        raise OSError(error_msg) from e
    
    # Define MddBootstrapInitialize2 function
    MddBootstrapInitialize2 = bootstrap.MddBootstrapInitialize2
    MddBootstrapInitialize2.argtypes = [
        wintypes.UINT,      # majorMinorVersion
        wintypes.LPCWSTR,   # versionTag
        _PackageVersion,    # minVersion
        wintypes.UINT,      # options
    ]
    MddBootstrapInitialize2.restype = ctypes.HRESULT

    MddBootstrapShutdown = bootstrap.MddBootstrapShutdown
    MddBootstrapShutdown.argtypes = []
    MddBootstrapShutdown.restype = None
    
    # Parse version
    parts = major_minor_version.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    major_minor = (major << 16) | minor
    
    # Parse minimum version
    pkg_version = _PackageVersion.from_string(min_version) if min_version else _PackageVersion(0, 0, 0, 0)
    
    if verbose:
        print(f"Initializing Windows App SDK {major_minor_version}...")
        print(f"  majorMinor: 0x{major_minor:08X}")
        print(f"  minVersion: {pkg_version.Major}.{pkg_version.Minor}.{pkg_version.Build}.{pkg_version.Revision}")
        print(f"  options: {options}")
    
    # Initialize
    try:
        hr = MddBootstrapInitialize2(major_minor, None, pkg_version, options)
    except Exception as e:
        os.environ['PATH'] = old_path
        raise OSError(f"Exception during MddBootstrapInitialize2: {e}") from e
    
    if verbose:
        print(f"  HRESULT: 0x{hr & 0xFFFFFFFF:08X}")
    
    if hr < 0:
        os.environ['PATH'] = old_path
        error = ctypes.WinError(hr)
        raise OSError(
            f"MddBootstrapInitialize2 failed with HRESULT: 0x{hr & 0xFFFFFFFF:08X}\n{error}"
        )
    
    if verbose:
        print("✅ Windows App SDK initialized successfully!")
    
    try:
        yield
    finally:
        if verbose:
            print("Shutting down Windows App SDK...")
        MddBootstrapShutdown()
        # Restore original PATH
        os.environ['PATH'] = old_path
