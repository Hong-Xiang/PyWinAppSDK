"""Minimal test to isolate the winappsdk_headers error."""
import sys
print(f"Python: {sys.version}")
print(f"Path: {sys.path[:3]}")

try:
    print("\n1. Importing WindowId...")
    from winappsdk.microsoft.ui import WindowId
    print(f"   ✓ WindowId: {WindowId}")
    
    print("\n2. Importing FileOpenPicker...")
    from winappsdk.microsoft.windows.storage.pickers import FileOpenPicker
    print(f"   ✓ FileOpenPicker: {FileOpenPicker}")
    
    print("\n3. Creating WindowId...")
    import ctypes
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    window_id = WindowId(hwnd)
    print(f"   ✓ window_id created: {window_id}")
    
    print("\n4. Creating FileOpenPicker...")
    picker = FileOpenPicker(window_id)
    print(f"   ✓ picker created: {picker}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
