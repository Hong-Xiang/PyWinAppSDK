# winappsdk-Foundation

Python bindings for Microsoft.WindowsAppSDK.Foundation APIs.

## Installation

```bash
pip install winappsdk-Foundation
```

## Features

This package provides Python bindings for:

- `Microsoft.Windows.Storage` - File storage APIs
- `Microsoft.Windows.Storage.Pickers` - File/folder picker dialogs
- `Microsoft.Windows.AppLifecycle` - App lifecycle management
- `Microsoft.Windows.AppNotifications` - Toast notifications
- And more Foundation APIs

## Example: File Picker

```python
import asyncio
from winrt.windows.foundation import IAsyncOperation
from winappsdk_foundation.microsoft.windows.storage.pickers import FileOpenPicker

async def pick_file():
    picker = FileOpenPicker()
    picker.file_type_filter.append("*")
    file = await picker.pick_single_file_async()
    if file:
        print(f"Selected: {file.path}")

asyncio.run(pick_file())
```

## Dependencies

- `winapp-sdk` - Windows App SDK headers
- `winrt-Windows.Foundation` - Windows Runtime Foundation types
- `winrt-Windows.Storage` - Windows Storage types
