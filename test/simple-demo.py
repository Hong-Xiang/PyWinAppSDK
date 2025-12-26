r"""
Windows App SDK - Simple Visual Demo

This demonstrates Windows App SDK APIs that are easy to visualize
without requiring package identity or registry modifications.

Shows:
  1. Window/Display information
  2. Resource management
  3. System information

Run with uv:
    uv run python test/notifications-test.py
"""

import sys
import ctypes

# Import Windows App SDK bootstrap
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import Foundation APIs
from winappsdk.microsoft.ui import WindowId


def create_simple_window():
    """Create a simple message box to demonstrate WindowId."""
    print("\n[1] Creating a simple Windows message box...")
    print("    This will show a VISIBLE dialog!")
    
    # Show a message box
    result = ctypes.windll.user32.MessageBoxW(
        0,
        "🐍 Hello from PyWinAppSDK!\n\n"
        "This message box was created using Windows App SDK Foundation APIs.\n\n"
        "The WindowId API can work with this window handle.",
        "PyWinAppSDK Demo",
        0x40 | 0x1  # MB_ICONINFORMATION | MB_OKCANCEL
    )
    
    if result == 1:  # OK clicked
        print("✅ You clicked OK!")
    else:  # Cancel clicked
        print("ℹ️  You clicked Cancel")
    
    return True


def test_window_id():
    """Test WindowId with console window."""
    print("\n[2] Testing WindowId with console window...")
    
    try:
        # Get console window handle
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        
        if hwnd:
            window_id = WindowId(hwnd)
            print(f"✅ Created WindowId: {window_id}")
            print(f"   Console window handle: 0x{hwnd:X}")
            print(f"   WindowId value: {window_id.value}")
            return True
        else:
            print("⚠️  No console window found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def show_system_info():
    """Display system information."""
    print("\n[3] Displaying system information...")
    
    try:
        # Get Windows version
        version = sys.getwindowsversion()
        print(f"✅ Windows version: {version.major}.{version.build}")
        print(f"   Platform: {sys.platform}")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   Architecture: {ctypes.sizeof(ctypes.c_voidp) * 8}-bit")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demonstrate_apis():
    """Run all demonstrations."""
    print("=" * 60)
    print("🔍 Windows App SDK - API Demonstrations")
    print("=" * 60)
    print("\nThese are SIMPLE demonstrations that don't need:")
    print("  ❌ Registry modifications")
    print("  ❌ Package identity")
    print("  ❌ Background processes")
    print("\n✅ Just pure Windows App SDK APIs in action!")
    
    try:
        # Test 1: Show a visible dialog
        create_simple_window()
        
        # Test 2: WindowId API
        test_window_id()
        
        # Test 3: System info
        show_system_info()
        
        print("\n" + "=" * 60)
        print("✅ All demonstrations completed!")
        print("=" * 60)
        
        print("\n💡 For more complex features (Notifications, Widgets):")
        print("   • Notifications require package identity")
        print("   • Widgets require COM registration")
        print("   • See foundation-test.py for more examples")
        
        print("\nPress Enter to exit...")
        input()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        with initialize_windows_app_sdk(
            options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
            verbose=True
        ):
            success = demonstrate_apis()
            sys.exit(0 if success else 1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
