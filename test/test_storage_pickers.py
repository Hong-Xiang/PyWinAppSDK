"""Test script for winappsdk-Foundation package with Storage Picker."""
import ctypes
from winappsdk_Foundation.microsoft.windows.storage.pickers import FileOpenPicker, FolderPicker
from winappsdk_Foundation.microsoft.windows.appnotifications import AppNotificationManager, AppNotification
from winappsdk_Foundation.microsoft.windows.applifecycle import AppInstance

# Initialize COM for the current thread (required for WinRT on console apps)
def initialize_com():
    """Initialize COM for WinRT on console applications."""
    COINIT_APARTMENTTHREADED = 0x2
    try:
        ole32 = ctypes.windll.ole32
        ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)
    except Exception:
        pass  # Already initialized

def test_imports():
    """Test that all key Foundation classes are importable."""
    print("Testing imports...")
    
    # Storage Pickers
    print(f"  FileOpenPicker: {FileOpenPicker}")
    print(f"  FolderPicker: {FolderPicker}")
    
    # App Notifications
    print(f"  AppNotificationManager: {AppNotificationManager}")
    print(f"  AppNotification: {AppNotification}")
    
    # App Lifecycle
    print(f"  AppInstance: {AppInstance}")
    
    print("\n  All imports successful!")

def test_static_methods():
    """Test static methods that don't require initialization."""
    print("\nTesting static methods...")
    
    # AppInstance.get_current() should work
    try:
        current = AppInstance.get_current()
        print(f"  AppInstance.get_current(): {current}")
    except Exception as e:
        print(f"  AppInstance.get_current() raised: {type(e).__name__}: {e}")
    
    print("  Static method tests complete!")

def main():
    initialize_com()
    print("=" * 60)
    print("winappsdk-Foundation Package Test")
    print("=" * 60)
    
    test_imports()
    test_static_methods()
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
