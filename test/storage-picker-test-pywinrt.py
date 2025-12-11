r"""
Test for Windows Storage Pickers using PyWinRT's official bootstrap.

This uses custom wheels built from PyWinAppSDK and the official PyWinRT
bootstrap package (winui3-Microsoft.Windows.ApplicationModel.DynamicDependency.Bootstrap).

Run with uv (from project root):
    uv run --with wheels/winappsdk_foundation-3.2.1-cp313-cp313-win_amd64.whl \
           --with wheels/winappsdk_interactiveexperiences-3.2.1-cp313-cp313-win_amd64.whl \
           --with winui3-Microsoft.Windows.ApplicationModel.DynamicDependency.Bootstrap \
           --no-project \
           python test/storage-picker-test-pywinrt.py

Note: The winrt-runtime and winrt-Windows.* packages are declared as dependencies
in the wheel packages and will be installed automatically by pip/uv.

Requirements:
    - Windows App SDK runtime installed
    - winui3-Microsoft.Windows.ApplicationModel.DynamicDependency.Bootstrap package
"""

import asyncio
import ctypes

# Import the official PyWinRT bootstrap module
from winui3.microsoft.windows.applicationmodel.dynamicdependency.bootstrap import (
    initialize,
    InitializeOptions,
)

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
    
    print("Testing Windows App SDK Storage Pickers (using PyWinRT bootstrap)...")
    print()
    
    # Verify imports work
    print("✅ Imports successful!")
    print(f"  - WindowId: {WindowId}")
    print(f"  - FileOpenPicker: {FileOpenPicker}")
    print(f"  - initialize: {initialize}")
    print(f"  - InitializeOptions: {InitializeOptions}")
    print()
    
    try:
        # Use the official PyWinRT bootstrap - it's a context manager
        # ON_NO_MATCH_SHOW_UI: Show UI if runtime not found
        print("Initializing Windows App SDK using PyWinRT bootstrap...")
        with initialize(options=InitializeOptions.ON_NO_MATCH_SHOW_UI):
            print("✅ Windows App SDK initialized successfully!")
            print()
            print("Opening file picker...")
            file = asyncio.run(pick_single_file())
            
            if file:
                print(f"\n✅ Success! Selected: {file.path}")
            else:
                print("\n✅ Picker opened successfully (no file selected)")
                
    except OSError as e:
        print(f"❌ Bootstrap failed: {e}")
        if hasattr(e, 'winerror'):
            print(f"   HRESULT: 0x{e.winerror & 0xFFFFFFFF:08X}")
            
            # Check for common errors
            if e.winerror == -2147009196:  # ERROR_NOT_SUPPORTED from original store python issue
                print("\n⚠️  This error typically occurs when using Python from the Microsoft Store.")
                print("   The Microsoft Store version of Python is a 'packaged' app which doesn't")
                print("   support the dynamic dependency bootstrapping approach.")
                print("   Try using a Python installation from python.org instead.")
            elif e.winerror == -2147024846:  # 0x80070032 ERROR_NOT_SUPPORTED
                print("\n⚠️  This error (ERROR_NOT_SUPPORTED) may occur when:")
                print("   - Running x64 Python under ARM64 emulation")
                print("   - The bootstrap API is not supported in this context")
                print("   Consider using ARM64 native Python on ARM64 Windows.")
            elif e.winerror == -2147221164:  # 0x80040154 REGDB_E_CLASSNOTREG
                print("\n⚠️  Class not registered. The Windows App SDK runtime may not be")
                print("   properly initialized or the required DLLs are not loaded.")
        
        print("\nTo install Windows App SDK, run:")
        print("  winget install Microsoft.WindowsAppSDK.1.8")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
