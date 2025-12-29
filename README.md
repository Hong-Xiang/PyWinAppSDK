# PyWinAppSDK

Python projection for the [Windows App SDK](https://github.com/microsoft/WindowsAppSDK) based on [PyWinRT](https://github.com/microsoft/pywinrt).

This project provides a modular, high-performance Python binding for Windows App SDK APIs, allowing Python developers to build modern Windows applications with features like WinUI 3, Windowing, App Lifecycle, and AI.

## Installation

You can install the components directly from this repository using `pip` or `uv`.

### Using `uv` (Recommended)

```bash
# Install specific components
uv add "git+https://github.com/Hong-Xiang/PyWinAppSDK.git#subdirectory=Foundation"
uv add "git+https://github.com/Hong-Xiang/PyWinAppSDK.git#subdirectory=InteractiveExperiences"
```

### Using `pip`

```bash
pip install "git+https://github.com/Hong-Xiang/PyWinAppSDK.git#subdirectory=Foundation"
```

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
.\rebuildAll.ps1
```

### Run Tests
```powershell
.\testAll.ps1
```

### Download Pre-built Wheels
To download the latest wheels from GitHub Releases:
```powershell
.\scripts\download-wheels.ps1
```
