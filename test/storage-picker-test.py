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
    import struct
    import sys
    
    # Determine architecture based on Python's bitness, not hardware
    # This is important for x64 Python running on ARM64 via emulation
    pointer_size = struct.calcsize("P") * 8
    
    # Check if Python is x64, x86, or ARM64
    if pointer_size == 64:
        # Check sys.version which has the architecture info
        if "AMD64" in sys.version:
            arch_folder = "win-x64"
        elif "ARM64" in sys.version:
            arch_folder = "win-arm64"
        else:
            # Default to x64 for 64-bit if unclear
            arch_folder = "win-x64"
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
    
    # Find and add the Windows App Runtime framework DLLs to PATH
    # These are installed via the runtime package, not the NuGet package
    old_path = os.environ.get('PATH', '')
    try:
        import subprocess
        import platform
        import struct
        import sys
        
        # Match runtime architecture to Python architecture
        pointer_size = struct.calcsize("P") * 8
        if pointer_size == 64:
            # Check sys.version which has the architecture info
            if "AMD64" in sys.version:
                runtime_arch = "X64"
            elif "ARM64" in sys.version:
                runtime_arch = "ARM64"
            else:
                runtime_arch = "X64"  # Default to x64
        else:
            runtime_arch = "X86"
            
        print(f"Looking for {runtime_arch} runtime package...")
        
        # Get the runtime package location
        result = subprocess.run(
            ['powershell', '-Command', 
             f'Get-AppxPackage -Name "*WindowsAppRuntime.1.8*" | Where-Object {{ $_.Architecture -eq "{runtime_arch}" }} | Select-Object -First 1 -ExpandProperty InstallLocation'],
            capture_output=True,
            text=True,
            check=True
        )
        runtime_path = result.stdout.strip()
        if runtime_path and os.path.exists(runtime_path):
            print(f"Found runtime DLLs: {runtime_path}")
            dll_dir = os.path.dirname(dll_path)
            os.environ['PATH'] = runtime_path + os.pathsep + dll_dir + os.pathsep + old_path
        else:
            print(f"⚠️  Could not find installed Windows App Runtime 1.8 {runtime_arch} package")
            dll_dir = os.path.dirname(dll_path)
            os.environ['PATH'] = dll_dir + os.pathsep + old_path
    except Exception as e:
        print(f"⚠️  Could not locate runtime DLLs: {e}")
        dll_dir = os.path.dirname(dll_path)
        os.environ['PATH'] = dll_dir + os.pathsep + old_path
    
    try:
        # Set error mode to prevent crash dialogs
        import ctypes.wintypes
        kernel32 = ctypes.windll.kernel32
        SEM_FAILCRITICALERRORS = 0x0001
        old_mode = kernel32.SetErrorMode(SEM_FAILCRITICALERRORS)
        
        bootstrap = ctypes.CDLL(dll_path)
        
        # Restore error mode
        kernel32.SetErrorMode(old_mode)
    except OSError as e:
        # Restore original PATH on error
        os.environ['PATH'] = old_path
        print(f"❌ Failed to load bootstrap DLL: {e}")
        if hasattr(e, 'winerror'):
            print(f"   HRESULT: 0x{e.winerror & 0xFFFFFFFF:08X}")
        print("\nThis might be due to missing dependencies. Try:")
        print("  1. Install Windows App SDK runtime: winget install Microsoft.WindowsAppSDK.1.8")
        print("  2. Or add the Framework DLLs to PATH")
        raise
    
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
    print(f"  majorMinor: 0x{major_minor:08X}")
    print(f"  minVersion: {pkg_version.Major}.{pkg_version.Minor}.{pkg_version.Build}.{pkg_version.Revision}")
    print(f"  options: {options}")
    
    try:
        hr = MddBootstrapInitialize2(major_minor, None, pkg_version, options)
    except Exception as e:
        print(f"❌ Exception during MddBootstrapInitialize2: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    print(f"  HRESULT: 0x{hr & 0xFFFFFFFF:08X}")
    
    if hr < 0:
        error = ctypes.WinError(hr)
        print(f"❌ MddBootstrapInitialize2 failed with HRESULT: 0x{hr & 0xFFFFFFFF:08X}")
        raise error
    
    print("✅ Windows App SDK initialized successfully!")
    
    try:
        yield
    finally:
        print("Shutting down Windows App SDK...")
        MddBootstrapShutdown()
        # Restore original PATH
        os.environ['PATH'] = old_path


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
    import sys
    
    # Enable better error output
    sys.stderr.flush()
    sys.stdout.flush()
    
    print("Testing Windows App SDK Storage Pickers...")
    print()
    
    # Verify imports work
    print("✅ Imports successful!")
    print(f"  - WindowId: {WindowId}")
    print(f"  - FileOpenPicker: {FileOpenPicker}")
    print()
    
    # Try WITHOUT bootstrap first - it might just work since runtime is installed
    print("Attempting to use Windows App SDK without bootstrap initialization...")
    print("(This works if the runtime is already available in the system)")
    print()
    
    try:
        print("Opening file picker...")
        file = asyncio.run(pick_single_file())
        
        if file:
            print(f"\n✅ Success! Selected: {file.path}")
        else:
            print("\n✅ Picker opened successfully (no file selected)")
            
    except Exception as e:
        print(f"\n❌ Failed without bootstrap: {e}")
        print("\nNow trying WITH bootstrap initialization...")
        print()
        
        # If that fails, try with bootstrap
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
    
    finally:
        sys.stderr.flush()
        sys.stdout.flush()
