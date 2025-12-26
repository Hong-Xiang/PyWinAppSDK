r"""
Test for Windows App SDK Machine Learning APIs.

This uses custom wheels built from PyWinAppSDK:
    winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl
    winappsdk_ml-3.2.1-cp312-cp312-win_amd64.whl

Run with uv (from project root):
    uv run --with wheels/winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl \
           --with wheels/winappsdk_ml-3.2.1-cp312-cp312-win_amd64.whl \
           --no-project \
           python test/ml-test.py

Note: The winrt-runtime and winrt-Windows.* packages are declared as dependencies
in the wheel packages and will be installed automatically by pip/uv.

Requirements:
    - Windows App SDK runtime installed (or the bootstrap DLL bundled in the package)
    - NPU or DirectML compatible GPU for ML inference
"""

import sys

# Import Windows App SDK bootstrap (bundled with Foundation package)
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import ML APIs
from winappsdk.microsoft.windows.ai.machinelearning import (
    LearningModel,
    LearningModelDevice,
    LearningModelDeviceKind,
)


def test_ml_device():
    """Test basic ML device enumeration and creation."""
    
    try:
        # Try to create a DirectML device (requires GPU)
        device = LearningModelDevice(LearningModelDeviceKind.DIRECT_ML)
        print(f"✓ Created DirectML device: {device}")
        print(f"  Device Kind: {LearningModelDeviceKind.DIRECT_ML}")
        
        # Also try CPU device as fallback
        cpu_device = LearningModelDevice(LearningModelDeviceKind.CPU)
        print(f"✓ Created CPU device: {cpu_device}")
        print(f"  Device Kind: {LearningModelDeviceKind.CPU}")
        
        print("✅ ML device creation successful")
        return True
        
    except Exception as e:
        print(f"❌ Error testing ML devices: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ml_types():
    """Test that ML types are properly imported."""
    
    try:
        # Just verify the types are importable
        print(f"✓ LearningModel type: {LearningModel}")
        print(f"✓ LearningModelDevice type: {LearningModelDevice}")
        print(f"✓ LearningModelDeviceKind type: {LearningModelDeviceKind}")
        
        # Check enum values
        print(f"  Available device kinds:")
        print(f"    - CPU: {LearningModelDeviceKind.CPU}")
        print(f"    - DirectML: {LearningModelDeviceKind.DIRECT_ML}")
        print(f"    - DirectML HighPerformance: {LearningModelDeviceKind.DIRECT_ML_HIGH_PERFORMANCE}")
        print(f"    - DirectML MinPower: {LearningModelDeviceKind.DIRECT_ML_MIN_POWER}")
        
        print("✅ ML types imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error importing ML types: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Windows App SDK Machine Learning Test")
    print("=" * 60)
    
    try:
        with initialize_windows_app_sdk(
            options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
            verbose=True
        ):
            print("\n[1] Testing ML Types...")
            test1 = test_ml_types()
            
            print("\n[2] Testing ML Device Creation...")
            test2 = test_ml_device()
            
            if test1 and test2:
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
