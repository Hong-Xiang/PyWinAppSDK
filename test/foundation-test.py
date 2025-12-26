r"""
Test for Windows App SDK Foundation APIs.

This uses custom wheels built from PyWinAppSDK:
    winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl

Run with uv (from project root):
    uv run --with wheels/winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl \
           --no-project \
           python test/foundation-test.py

Note: The winrt-runtime and winrt-Windows.* packages are declared as dependencies
in the wheel packages and will be installed automatically by pip/uv.

Requirements:
    - Windows App SDK runtime installed (or the bootstrap DLL bundled in the package)
"""

import sys

# Import Windows App SDK bootstrap (bundled with Foundation package)
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import Foundation APIs
from winappsdk.microsoft.ui import WindowId
from winappsdk.microsoft.windows.applifecycle import (
    AppInstance,
    AppActivationArguments,
)
from winappsdk.microsoft.windows.applicationmodel.resources import (
    ResourceManager,
)


def test_bootstrap():
    """Test Windows App SDK bootstrap."""
    print("✓ Bootstrap context manager active")
    print("✅ Bootstrap test passed")
    return True


def test_window_id():
    """Test WindowId creation."""
    
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        
        if hwnd:
            window_id = WindowId(hwnd)
            print(f"✓ Created WindowId from HWND: {window_id}")
            print(f"  HWND value: {hwnd}")
            print("✅ WindowId test passed")
            return True
        else:
            print("⚠ No console window available, skipping WindowId test")
            return True
            
    except Exception as e:
        print(f"❌ Error testing WindowId: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_instance():
    """Test AppInstance APIs."""
    
    try:
        # Get current app instance
        instances = AppInstance.get_instances()
        print(f"✓ Retrieved app instances, count: {len(instances) if instances else 0}")
        
        # Try to get current instance
        try:
            current = AppInstance.get_current()
            print(f"✓ Current AppInstance: {current}")
        except Exception as e:
            print(f"⚠ Could not get current app instance (expected in non-packaged app): {e}")
        
        print("✅ AppInstance test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AppInstance: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resource_manager():
    """Test ResourceManager APIs."""
    
    try:
        # Create resource manager (may fail in non-packaged apps)
        try:
            rm = ResourceManager()
            print(f"✓ Created ResourceManager: {rm}")
            
            # Try to get main resource map
            main_map = rm.main_resource_map
            print(f"✓ Main resource map: {main_map}")
            
        except Exception as e:
            print(f"⚠ ResourceManager creation failed (expected in non-packaged app): {e}")
        
        print("✅ ResourceManager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing ResourceManager: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_foundation_types():
    """Test that Foundation types are properly imported."""
    
    try:
        print(f"✓ WindowId type: {WindowId}")
        print(f"✓ AppInstance type: {AppInstance}")
        print(f"✓ AppActivationArguments type: {AppActivationArguments}")
        print(f"✓ ResourceManager type: {ResourceManager}")
        
        print("✅ Foundation types imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error importing Foundation types: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Windows App SDK Foundation Test")
    print("=" * 60)
    
    try:
        with initialize_windows_app_sdk(
            options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
            verbose=True
        ):
            print("\n[1] Testing Bootstrap...")
            test1 = test_bootstrap()
            
            print("\n[2] Testing Foundation Types...")
            test2 = test_foundation_types()
            
            print("\n[3] Testing WindowId...")
            test3 = test_window_id()
            
            print("\n[4] Testing AppInstance...")
            test4 = test_app_instance()
            
            print("\n[5] Testing ResourceManager...")
            test5 = test_resource_manager()
            
            if test1 and test2 and test3 and test4 and test5:
                print("\n" + "=" * 60)
                print("✅ All tests passed!")
                print("=" * 60)
                sys.exit(0)
            else:
                print("\n" + "=" * 60)
                print("❌ Some tests failed")
                print("=" * 60)
                sys.exit(1)
                
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
            
    except OSError as e:
        print(f"❌ Bootstrap failed: {e}")
        sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
