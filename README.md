# PyWinAppSDK

Python projection for the [Windows App SDK](https://github.com/microsoft/WindowsAppSDK) based on [PyWinRT](https://github.com/microsoft/pywinrt).

This project provides a modular, high-performance Python binding for Windows App SDK APIs, allowing Python developers to build modern Windows applications with features like WinUI 3, Windowing, App Lifecycle, and AI.

## Installation

Currently packages is not published to PyPI yet for waiting it to be more polished. You can download the latest wheels from the [GitHub Releases](https://github.com/Hong-Xiang/PyWinAppSDK/releases).
Put it into local wheel folder. and samples/tests folder would work since pyproject.toml is configured to use local wheel folder as extra index in `[tool.uv]`.

## Usage

All components share the unified `winappsdk` namespace.

```python
from winappsdk.microsoft.ui.windowing import AppWindow
from winappsdk.microsoft.windows.applifecycle import AppInstance

# Use Windows App SDK APIs
app_instance = AppInstance.get_current()
```

## Development

### Build All Components
To build all wheels and NuGet packages locally:
```powershell
.\scripts\rebuildAll.ps1
```

### Run Tests
```powershell
.\scripts\testAll.ps1
```

### Download Pre-built Wheels
To download the latest wheels from GitHub Releases:
```powershell
.\scripts\download-wheels.ps1
```
