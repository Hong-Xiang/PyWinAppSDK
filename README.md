# PyWinAppSDK

Python projection for Windows App SDK using a **unified namespace** (`winappsdk.*`) with **modular component wheels**.

## Architecture

### Dual-Folder Structure

To support PEP 420 namespace packages and avoid binary conflicts:

| Folder | Contents | Purpose |
|--------|----------|---------|
| `winappsdk/` | Python modules (`.py`) | Shared namespace, merged by pip |
| `winappsdk_<Component>/` | Native extensions (`.pyd`), type stubs (`.pyi`) | Component-specific binaries |

### Package Hierarchy

```
site-packages/
├── winappsdk/                                    # Merged namespace (PEP 420)
│   └── microsoft/
│       ├── ui/windowing/                         # From InteractiveExperiences
│       ├── ui/composition/                       # From InteractiveExperiences
│       ├── windows/applifecycle/                 # From Foundation
│       ├── windows/applicationmodel/resources/   # From Foundation
│       └── windows/ai/                           # From AI
├── winappsdk_InteractiveExperiences/             # Native binaries
├── winappsdk_Foundation/                         # Native binaries
└── winappsdk_AI/                                 # Native binaries
```

### Components

| Component | Description | Dependencies |
|-----------|-------------|--------------|
| **Headers** | Shared C++ headers from cppwinrt/pywinrt | — |
| **InteractiveExperiences** | UI, Windowing, Composition | Headers |
| **Foundation** | App lifecycle, Resources | Headers |
| **AI** | Machine Learning, OCR | Headers, Foundation |

## Usage

### Basic Imports

```python
from winappsdk.microsoft.ui.windowing import AppWindow
from winappsdk.microsoft.ui.composition import Compositor
from winappsdk.microsoft.windows.applifecycle import AppInstance
from winappsdk.microsoft.windows.applicationmodel.resources import ResourceManager
from winappsdk.microsoft.windows.ai import AIFeatureReadyResult
```

### Bootstrap Initialization

For applications using Windows App SDK features, initialize the runtime first:

```python
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Initialize Windows App SDK runtime
with initialize_windows_app_sdk(
    options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
    verbose=True
):
    # Your Windows App SDK code here
    from winappsdk.microsoft.ui import WindowId
    from winappsdk.microsoft.windows.storage.pickers import FileOpenPicker
    
    # Use Windows App SDK features
    picker = FileOpenPicker(window_id)
    # ...
```

## Building

### Quick Build & Test

```powershell
.\rebuild_and_test.ps1
```

### Manual Build

```powershell
# 1. Build the MSBuild tasks (required first, provides WinMD resolution)
cd PyWinAppSDK.Build.Tasks
dotnet build -c Release

# 2. Build order matters: Headers → InteractiveExperiences → Foundation → AI
cd ..
dotnet build Headers
dotnet build InteractiveExperiences
dotnet build Foundation
dotnet build AI
```

### Run Tests Only

```powershell
cd test
uv sync
uv run test_integration.py
```

## Technical Notes

- **PEP 420**: No `__init__.py` in `winappsdk/` or `winappsdk/microsoft/` to allow namespace merging
- **Native Naming**: Extensions use unique names like `_winappsdk_<comp>_microsoft_...pyd`
- **Build Tooling**: Uses `uv` for wheel compilation
- **Bootstrap**: The Foundation package includes `Microsoft.WindowsAppRuntime.Bootstrap.dll` for all architectures (x64, x86, arm64) to initialize the Windows App SDK runtime

## Known Limitations

- **Background Task**: `Microsoft.Windows.ApplicationModel.Background.UniversalBGTask` generation is skipped due to a WinAppSDK bug with `ITask`. See [pywinrt workaround](https://github.com/pywinrt/pywinrt/commit/a57d450cea4bc5c23f15e721e9908adb4fab805e) and [WinAppSDK fix](https://github.com/microsoft/WindowsAppSDK/pull/5313).