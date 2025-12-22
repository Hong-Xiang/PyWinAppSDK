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
    - Windows App SDK runtime installed (or the bootstrap DLL bundled in the package)
"""

import asyncio
import ctypes

# Import Windows App SDK bootstrap (bundled with Foundation package)
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import Windows App SDK types
from winappsdk.microsoft.ui import WindowId
from winappsdk.microsoft.windows.storage.pickers import FileOpenPicker


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
                options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
                verbose=True
            ):
                print("\nOpening file picker...")
                file = asyncio.run(pick_single_file())
                
                if file:
                    print(f"\n✅ Success! Selected: {file.path}")
                    
        except FileNotFoundError as e:
            print(f"❌ {e}")
                
        except OSError as e:
            print(f"❌ Bootstrap failed: {e}")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
    
    finally:
        sys.stderr.flush()
        sys.stdout.flush()
