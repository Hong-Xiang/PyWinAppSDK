"""Minimal test to verify Windows App SDK initialization and picker creation."""
import ctypes
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions
from winappsdk.microsoft.ui import WindowId
from winappsdk.microsoft.windows.storage.pickers import FileOpenPicker

with initialize_windows_app_sdk(options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI):
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    window_id = WindowId(hwnd)
    picker = FileOpenPicker(window_id)
    picker.file_type_filter.append("*")
    print("✅ Picker created successfully")
