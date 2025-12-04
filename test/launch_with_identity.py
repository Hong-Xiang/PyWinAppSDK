"""
Launch Python with package identity using Windows Application Model.

This script creates a proper activation context for the sparse package
so that the Python process has package identity.
"""

import os
import sys
import ctypes
from ctypes import wintypes, POINTER, byref, c_void_p, c_wchar_p, c_uint32
import subprocess


# Windows API types and functions
kernel32 = ctypes.windll.kernel32

# ACTCTX structure
class ACTCTXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.ULONG),
        ("dwFlags", wintypes.DWORD),
        ("lpSource", wintypes.LPCWSTR),
        ("wProcessorArchitecture", wintypes.USHORT),
        ("wLangId", wintypes.LANGID),
        ("lpAssemblyDirectory", wintypes.LPCWSTR),
        ("lpResourceName", wintypes.LPCWSTR),
        ("lpApplicationName", wintypes.LPCWSTR),
        ("hModule", wintypes.HMODULE),
    ]

# Activation context flags
ACTCTX_FLAG_PROCESSOR_ARCHITECTURE_VALID = 0x00000001
ACTCTX_FLAG_LANGID_VALID = 0x00000002
ACTCTX_FLAG_ASSEMBLY_DIRECTORY_VALID = 0x00000004
ACTCTX_FLAG_RESOURCE_NAME_VALID = 0x00000008
ACTCTX_FLAG_SET_PROCESS_DEFAULT = 0x00000010
ACTCTX_FLAG_APPLICATION_NAME_VALID = 0x00000020
ACTCTX_FLAG_HMODULE_VALID = 0x00000080

# Function prototypes
CreateActCtxW = kernel32.CreateActCtxW
CreateActCtxW.argtypes = [POINTER(ACTCTXW)]
CreateActCtxW.restype = wintypes.HANDLE

ActivateActCtx = kernel32.ActivateActCtx
ActivateActCtx.argtypes = [wintypes.HANDLE, POINTER(c_void_p)]
ActivateActCtx.restype = wintypes.BOOL

DeactivateActCtx = kernel32.DeactivateActCtx
DeactivateActCtx.argtypes = [wintypes.DWORD, c_void_p]
DeactivateActCtx.restype = wintypes.BOOL

ReleaseActCtx = kernel32.ReleaseActCtx
ReleaseActCtx.argtypes = [wintypes.HANDLE]
ReleaseActCtx.restype = None

INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value


def get_package_path():
    """Get the path to the sparse package manifest."""
    # Check if package is registered
    ps_script = '''
    $packageName = "PyWinAppSDK.AITest"
    $pkg = Get-AppxPackage -Name $packageName
    if ($pkg) {
        Write-Host $pkg.InstallLocation
    } else {
        Write-Host "NOT_FOUND"
    }
    '''
    
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    
    path = result.stdout.strip()
    if path == "NOT_FOUND" or not path:
        return None
    return path


def run_with_activation_context(manifest_path: str, script_path: str, args: list = None):
    """
    Run a Python script with an activation context from the manifest.
    """
    if args is None:
        args = []
    
    # Create activation context
    actctx = ACTCTXW()
    actctx.cbSize = ctypes.sizeof(ACTCTXW)
    actctx.dwFlags = 0
    actctx.lpSource = manifest_path
    
    handle = CreateActCtxW(byref(actctx))
    
    if handle == INVALID_HANDLE_VALUE:
        error = ctypes.get_last_error()
        print(f"❌ Failed to create activation context: {ctypes.WinError(error)}")
        return False
    
    print(f"✅ Created activation context from: {manifest_path}")
    
    # Activate the context
    cookie = c_void_p()
    if not ActivateActCtx(handle, byref(cookie)):
        error = ctypes.get_last_error()
        print(f"❌ Failed to activate context: {ctypes.WinError(error)}")
        ReleaseActCtx(handle)
        return False
    
    print("✅ Activation context activated")
    
    try:
        # Now run the Python script in this context
        # Note: The activation context only affects the current process
        # We need to exec directly, not spawn a subprocess
        
        # For testing, let's try importing and running directly
        import importlib.util
        
        # Add script directory to path
        script_dir = os.path.dirname(os.path.abspath(script_path))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # Set sys.argv for the script
        old_argv = sys.argv
        sys.argv = [script_path] + args
        
        try:
            # Load and execute the script
            spec = importlib.util.spec_from_file_location("__main__", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        finally:
            sys.argv = old_argv
            
    finally:
        # Deactivate and release
        DeactivateActCtx(0, cookie)
        ReleaseActCtx(handle)
        print("Activation context deactivated")


def main():
    if len(sys.argv) < 2:
        print("Usage: python launch_with_identity.py <script.py> [args...]")
        print("\nThis launcher runs a Python script with package identity")
        print("using the registered sparse package.")
        sys.exit(1)
    
    script_path = sys.argv[1]
    args = sys.argv[2:]
    
    if not os.path.exists(script_path):
        # Try relative to test directory
        test_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(test_dir, script_path)
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)
    
    # Get package installation path
    package_path = get_package_path()
    
    if not package_path:
        print("❌ Sparse package not registered.")
        print("Run: python register_sparse_package.py register")
        sys.exit(1)
    
    print(f"Package path: {package_path}")
    
    # The manifest should be in the package path
    manifest_path = os.path.join(package_path, "AppxManifest.xml")
    
    if not os.path.exists(manifest_path):
        # Try temp location
        import tempfile
        manifest_path = os.path.join(
            tempfile.gettempdir(), 
            "PyWinAppSDK_SparsePackage", 
            "AppxManifest.xml"
        )
    
    if not os.path.exists(manifest_path):
        print(f"❌ Manifest not found: {manifest_path}")
        sys.exit(1)
    
    print(f"Using manifest: {manifest_path}")
    print(f"Running script: {script_path}")
    print(f"Arguments: {args}")
    print()
    
    success = run_with_activation_context(manifest_path, script_path, args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
