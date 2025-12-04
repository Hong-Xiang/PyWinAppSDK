r"""
Test for Windows Storage Pickers using custom PyWinRT build.

This uses custom wheels built from PyWinAppSDK:
    winappsdk_foundation-3.2.1-cp313-cp313-win_amd64.whl
    winappsdk_interactiveexperiences-3.2.1-cp313-cp313-win_amd64.whl

Run with uv (from project root):
    uv run --with wheels/winappsdk_foundation-3.2.1-cp313-cp313-win_amd64.whl \
           --with wheels/winappsdk_interactiveexperiences-3.2.1-cp313-cp313-win_amd64.whl \
           --no-project \
           python test/storage-picker-test.py

Note: The winrt-runtime and winrt-Windows.* packages are declared as dependencies
in the wheel packages and will be installed automatically by pip/uv.

Requirements:
    - Windows App SDK runtime installed (or NuGet packages restored)
    - The bootstrap DLL from the Windows App SDK Foundation package
"""

import asyncio
import ctypes
from ctypes import wintypes
from contextlib import contextmanager
import os

# Windows App SDK Bootstrap API
# https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/win32/mddbootstrap/

# Bootstrap options flags
class MddBootstrapInitializeOptions:
    NONE = 0
    ON_NO_MATCH_SHOW_UI = 0x00000001
    ON_PACKAGE_IDENTITY_SHOW_UI = 0x00000002
    ON_ERROR_SHOW_UI = ON_NO_MATCH_SHOW_UI | ON_PACKAGE_IDENTITY_SHOW_UI


class PackageVersion(ctypes.Structure):
    """PACKAGE_VERSION structure"""
    _fields_ = [
        ("Revision", wintypes.USHORT),
        ("Build", wintypes.USHORT),
        ("Minor", wintypes.USHORT),
        ("Major", wintypes.USHORT),
    ]
    
    @classmethod
    def from_string(cls, version_str: str) -> "PackageVersion":
        """Create from version string like '1.8.0.0' or '8000.0.0.0'"""
        parts = version_str.split(".")
        while len(parts) < 4:
            parts.append("0")
        return cls(
            Revision=int(parts[3]),
            Build=int(parts[2]),
            Minor=int(parts[1]),
            Major=int(parts[0]),
        )


def find_bootstrap_dll():
    """Find the Windows App SDK bootstrap DLL."""
    import platform
    
    # Determine architecture
    arch = platform.machine().lower()
    if arch in ("amd64", "x86_64"):
        arch_folder = "win-x64"
    elif arch == "arm64":
        arch_folder = "win-arm64"
    else:
        arch_folder = "win-x86"
    
    # Common locations for the bootstrap DLL
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    possible_paths = [
        # NuGet package location (from project packages folder)
        os.path.join(project_root, "packages", "microsoft.windowsappsdk.foundation", "1.8.251104000", "runtimes", arch_folder, "native", "Microsoft.WindowsAppRuntime.Bootstrap.dll"),
        # Alternative NuGet package location
        os.path.join(project_root, "packages", "microsoft.windowsappsdk", "1.8.251106002", "build", "native", arch_folder, "Microsoft.WindowsAppRuntime.Bootstrap.dll"),
    ]
    
    # Try to find in PATH
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for path_dir in path_dirs:
        possible_paths.append(os.path.join(path_dir, "Microsoft.WindowsAppRuntime.Bootstrap.dll"))
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Debug: print what we tried
    print("Searched for bootstrap DLL in:")
    for path in possible_paths[:3]:
        print(f"  - {path} (exists: {os.path.exists(path)})")
    
    return None


@contextmanager
def initialize_windows_app_sdk(major_minor_version: str = "1.8", min_version: str = None, options: int = MddBootstrapInitializeOptions.NONE):
    """
    Initialize the Windows App SDK runtime using MddBootstrapInitialize.
    
    Args:
        major_minor_version: Version like "1.8" or "1.7"
        min_version: Minimum version like "8000.0.0.0" (optional)
        options: MddBootstrapInitializeOptions flags
    
    Usage:
        with initialize_windows_app_sdk("1.8"):
            # Use Windows App SDK APIs here
            picker = FileOpenPicker(window_id)
    """
    # Find the bootstrap DLL
    dll_path = find_bootstrap_dll()
    if not dll_path:
        raise FileNotFoundError(
            "Could not find Microsoft.WindowsAppRuntime.Bootstrap.dll. "
            "Please install the Windows App SDK or add it to PATH."
        )
    
    print(f"Loading bootstrap DLL: {dll_path}")
    bootstrap = ctypes.CDLL(dll_path)
    
    # MddBootstrapInitialize2 function signature:
    # HRESULT MddBootstrapInitialize2(
    #     UINT32 majorMinorVersion,
    #     PCWSTR versionTag,
    #     PACKAGE_VERSION minVersion,
    #     MddBootstrapInitializeOptions options
    # )
    MddBootstrapInitialize2 = bootstrap.MddBootstrapInitialize2
    MddBootstrapInitialize2.argtypes = [
        wintypes.UINT,      # majorMinorVersion
        wintypes.LPCWSTR,   # versionTag
        PackageVersion,     # minVersion
        wintypes.UINT,      # options
    ]
    MddBootstrapInitialize2.restype = ctypes.HRESULT
    
    MddBootstrapShutdown = bootstrap.MddBootstrapShutdown
    MddBootstrapShutdown.argtypes = []
    MddBootstrapShutdown.restype = None
    
    # Parse major.minor version
    parts = major_minor_version.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    major_minor = (major << 16) | minor
    
    # Parse minimum version
    if min_version:
        pkg_version = PackageVersion.from_string(min_version)
    else:
        pkg_version = PackageVersion(0, 0, 0, 0)
    
    # Initialize
    print(f"Initializing Windows App SDK {major_minor_version}...")
    hr = MddBootstrapInitialize2(major_minor, None, pkg_version, options)
    
    if hr < 0:
        raise ctypes.WinError(hr)
    
    print("✅ Windows App SDK initialized successfully!")
    
    try:
        yield
    finally:
        print("Shutting down Windows App SDK...")
        MddBootstrapShutdown()


# Now import the Windows App SDK types
from winappsdk_InteractiveExperiences.microsoft.ui import WindowId
from winappsdk_Foundation.microsoft.windows.storage.pickers import FileOpenPicker


async def pick_single_file():
    """Open a file picker dialog and let user select a single file."""
    
    # Get the current window handle (console window)
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    
    # Create a WindowId from the HWND
    window_id = WindowId(hwnd)
    
    # Create the file picker with the window ID
    picker = FileOpenPicker(window_id)
    
    # Set file type filters
    picker.file_type_filter.append("*")  # Allow all file types
    
    # Show the picker and get the selected file result
    result = await picker.pick_single_file_async()
    
    if result and result.path:
        print(f"Selected file: {result.path}")
        return result
    else:
        print("No file was selected.")
        return None


if __name__ == "__main__":
    print("Testing Windows App SDK Storage Pickers...")
    print()
    
    # Verify imports work
    print("✅ Imports successful!")
    print(f"  - WindowId: {WindowId}")
    print(f"  - FileOpenPicker: {FileOpenPicker}")
    print()
    
    # Try to initialize and use the file picker
    try:
        with initialize_windows_app_sdk(
            "1.8", 
            options=MddBootstrapInitializeOptions.ON_ERROR_SHOW_UI
        ):
            print("\nOpening file picker...")
            file = asyncio.run(pick_single_file())
            
            if file:
                print(f"\n✅ Success! Selected: {file.path}")
                
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nTo install Windows App SDK, run:")
        print("  winget install Microsoft.WindowsAppSDK.1.8")
        
    except OSError as e:
        print(f"❌ Bootstrap failed: {e}")
        if hasattr(e, 'winerror'):
            print(f"   HRESULT: 0x{e.winerror & 0xFFFFFFFF:08X}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
