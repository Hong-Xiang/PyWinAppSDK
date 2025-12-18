# PyWinAppSDK - Development Roadmap & Technical Specifications

## Overview

This document outlines the technical design and implementation plan for PyWinAppSDK, focusing on package organization, dependency resolution, and Python binding generation for Windows App SDK components.

## Core Design Principles

1. **WindowsAppSDK Focus**: Pure WindowsAppSDK packages without Windows Platform SDK coupling
2. **Component Separation**: Support self-contained deployment with installable component packages
3. **Unified Namespace**: Clean `winappsdk.microsoft.windows.*` imports directly (no re-export layer!)
4. **PEP 420 Namespace Packages**: Multiple wheels contribute to same `winappsdk/` namespace root
5. **No PyWinRT Modifications**: Use same `winappsdk` PyPackage for all components

---

## ✅ CONFIRMED ARCHITECTURE

### Key Insight: Dual Package Structure

**Component packages generate Python namespace modules in a shared `winappsdk/` folder, while keeping binaries in component-specific `winappsdk_<Component>/` folders.**

This means:
- Generated code imports from `winappsdk.microsoft.*` directly
- No metapackage re-export layer needed!
- Python namespace modules (`.py` files) go to shared `winappsdk/` folder
- Type stubs (`.pyi`) and native extensions (`.pyd`) stay in `winappsdk_<Component>/` folder
- Native extensions have unique names (based on full namespace)

### Two-Layer Package Architecture (Simplified!)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: Component Packages (per NuGet) - PEP 420 Namespace Packages    │
│                                                                         │
│ Distribution: winappsdk-Foundation                                      │
│   └── winappsdk/microsoft/windows/applifecycle/                        │
│   └── winappsdk/microsoft/windows/applicationmodel/                    │
│   └── _winappsdk_microsoft_windows_applifecycle.pyd                    │
│                                                                         │
│ Distribution: winappsdk-AI                                              │
│   └── winappsdk/microsoft/windows/ai/                                  │
│   └── _winappsdk_microsoft_windows_ai.pyd                              │
│                                                                         │
│ All share same `winappsdk/` namespace root!                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓ installed together
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: Installed in site-packages (merged by pip)                     │
│                                                                         │
│ site-packages/winappsdk/                                                │
│   └── microsoft/windows/applifecycle/  (from winappsdk-Foundation)     │
│   └── microsoft/windows/ai/            (from winappsdk-AI)             │
│   └── _winappsdk_microsoft_windows_applifecycle.pyd                    │
│   └── _winappsdk_microsoft_windows_ai.pyd                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Import Pattern (Same Regardless of Which Wheel!)

```python
# These imports work the same whether user installed:
# - pip install winappsdk-Foundation
# - pip install winappsdk-InteractiveExperiences  
# - pip install winappsdk (metapackage with all dependencies)

from winappsdk.microsoft.windows.applifecycle import AppInstance
from winappsdk.microsoft.windows.ai import AIFeatureReadyResult
from winappsdk.microsoft.ui.composition import Compositor
from winappsdk.microsoft.ui.windowing import AppWindow

# Or 
from winrt.microsoft.windows.applifecycle import AppInstance
from winrt.microsoft.windows.ai import AIFeatureReadyResult
from winrt.microsoft.ui.composition import Compositor
from winrt.microsoft.ui.windowing import AppWindow
```

instead of 
```python
# OLD (requires component package name prefix, or metapackage re-export layer to unify)
from winappsdk_Foundation.microsoft.windows.applifecycle import AppInstance
```

### Why This Works

1. **PyWinRT generates unique native extensions**: `_winappsdk_microsoft_windows_ai.pyd`
2. **Namespace directories don't conflict**: Each namespace is unique
3. **No intermediate `__init__.py`**: PyWinRT only creates `__init__.py` at leaf namespaces
4. **PEP 420 implicit namespace packages**: Python merges multiple packages into one namespace

---

## 1. Build Configuration Changes Required

### Current Configuration (To Be Updated)

```xml
<!-- Current: Uses component-specific PyPackage names -->
<InputWinMD Include="$(PkgMicrosoft_WindowsAppSDK_AI)\metadata">
  <PyPackageName>winappsdk-AI</PyPackageName>  <!-- WRONG -->
</InputWinMD>

<ReferenceWinMD Include="$(PkgMicrosoft_WindowsAppSDK_Foundation)\metadata">
  <PyPackageName>winappsdk-Foundation</PyPackageName>  <!-- WRONG -->
</ReferenceWinMD>
```

### New Configuration (Unified PyPackage)

```xml
<!-- New: All use same PyPackage name -->
<InputWinMD Include="$(PkgMicrosoft_WindowsAppSDK_AI)\metadata">
  <PyPackageName>winappsdk</PyPackageName>  <!-- CORRECT -->
</InputWinMD>

<ReferenceWinMD Include="$(PkgMicrosoft_WindowsAppSDK_Foundation)\metadata">
  <PyPackageName>winappsdk</PyPackageName>  <!-- CORRECT -->
</ReferenceWinMD>
```

### Build Output Changes

**Before** (current):
```
obj/gen/winappsdk-AI-Microsoft.Windows.AI/
└── winappsdk_AI/                           ← Component-specific module root
    └── microsoft/windows/ai/__init__.py

obj/pkg/winappsdk_AI/                        ← Component-specific package
    └── microsoft/windows/ai/__init__.py
```

**After** (new):
```
obj/gen/winappsdk-Microsoft.Windows.AI/
└── winappsdk/                              ← UNIFIED module root!
    └── microsoft/windows/ai/__init__.py

obj/pkg/winappsdk/                           ← UNIFIED package root
    └── microsoft/windows/ai/__init__.py
```

---

## 2. Component Package Structure (PEP 420)

### Distribution Package: winappsdk-Foundation

```
winappsdk-Foundation/                        # PyPI distribution name
├── pyproject.toml
├── setup.py
├── py.Microsoft.Windows.AppLifecycle.cpp    # C++ source
├── py.Microsoft.Windows.ApplicationModel.Resources.cpp
|---winappsdk_Foundation/
|   ├── native extensions
└── winappsdk/                               # NO __init__.py at root! (PEP 420)
    ├── _winappsdk_microsoft_windows_applifecycle.pyi
    ├── _winappsdk_microsoft_windows_applicationmodel_resources.pyi
    └── microsoft/                           # NO __init__.py (PEP 420)
        └── windows/                         # NO __init__.py (PEP 420)
            ├── applifecycle/
            │   └── __init__.py              # HAS content (leaf namespace)
            └── applicationmodel/
                └── resources/
                    └── __init__.py          # HAS content (leaf namespace)
```

### Distribution Package: winappsdk-AI

```
winappsdk-AI/                                # PyPI distribution name
├── pyproject.toml
├── setup.py
├── py.Microsoft.Windows.AI.cpp
└── winappsdk/                               # Same namespace root as Foundation!
    ├── _winappsdk_microsoft_windows_ai.pyi
    └── microsoft/
        └── windows/
            └── ai/
                └── __init__.py              # HAS content (leaf namespace)
```

### Installed Together (pip merges them)

```
site-packages/
└── winappsdk/                               # Merged from all installed packages
    ├── _winappsdk_microsoft_windows_applifecycle.pyd   # From Foundation
    ├── _winappsdk_microsoft_windows_ai.pyd             # From AI
    └── microsoft/
        └── windows/
            ├── applifecycle/                # From Foundation
            │   └── __init__.py
            ├── applicationmodel/            # From Foundation
            │   └── resources/
            │       └── __init__.py
            └── ai/                          # From AI
                └── __init__.py
```

---

## 3. Required Changes Summary

### 3.1 MSBuild Project Files

Update all `.proj` files to use `winappsdk` as PyPackageName:

| File | Change |
|------|--------|
| `Foundation/PyWinRT.Microsoft.WindowsAppSDK.Foundation.proj` | `<PyPackageName>winappsdk</PyPackageName>` |
| `AI/PyWinRT.Microsoft.WindowsAppSDK.AI.proj` | `<PyPackageName>winappsdk</PyPackageName>` |
| `InteractiveExperiences/PyWinRT.Microsoft.WindowsAppSDK.InteractiveExperiences.proj` | `<PyPackageName>winappsdk</PyPackageName>` |

Also update all `<ReferenceWinMD>` entries to use `<PyPackageName>winappsdk</PyPackageName>`.

### 3.2 generate-package.py Script

Update to NOT create root `__init__.py` (required for PEP 420):

```python
# OLD (breaks PEP 420):
init_file = package_dir / "__init__.py"
if not init_file.exists():
    init_file.write_text("# Auto-generated package\n", encoding="utf-8")

# NEW (PEP 420 compatible):
# Don't create __init__.py at namespace root - let pip handle it
```

### 3.3 pyproject.toml Template

Update to handle namespace packages:

```toml
[project]
name = "winappsdk-Foundation"  # Distribution name (for PyPI)
# ...

[tool.setuptools.packages.find]
where = ["."]
include = ["winappsdk_Foundation", "winappsdk"]       # Find all winappsdk.* packages

# For namespace package support
[tool.setuptools.package-dir]
"" = "."
```

### 3.4 Dependencies Between Components

```toml
# winappsdk-AI/pyproject.toml
[project]
name = "winappsdk-AI"
dependencies = [
    "winappsdk-Foundation>=1.8.0",     # Depends on Foundation
    "winappsdk-InteractiveExperiences>=1.8.0",
    "winrt-runtime",
    "winrt-Windows.Foundation",
]
```

---

## 4. Optional Metapackage (Convenience Only)

The metapackage is now **much simpler** - just dependencies, no re-export code:

```toml
# winappsdk/pyproject.toml
[project]
name = "winappsdk"
version = "1.8.0"
description = "Python bindings for Windows App SDK (metapackage)"
dependencies = [
    "winappsdk-Foundation>=1.8.0",
    "winappsdk-AI>=1.8.0",
    "winappsdk-InteractiveExperiences>=1.8.0",
]

[project.optional-dependencies]
full = [
    "winappsdk-Foundation>=1.8.0",
    "winappsdk-AI>=1.8.0",
    "winappsdk-InteractiveExperiences>=1.8.0",
    "winappsdk-Widgets>=1.8.0",
]
```

**No Python code needed in metapackage!** It's purely a dependency aggregator.

### User Installation Patterns

```bash
# Install everything
pip install winappsdk

# Install specific component only (self-contained mode)
pip install winappsdk-Foundation

# Install with optional extras
pip install winappsdk[full]
```

---

## 5. Self-Contained Deployment

With the unified `winappsdk` namespace, self-contained mode is simple:

```bash
# User only needs Foundation
pip install winappsdk-Foundation
```

```python
# This works directly - no metapackage needed!
from winappsdk.microsoft.windows.applifecycle import AppInstance

# This would fail with ImportError (AI not installed)
from winappsdk.microsoft.windows.ai import AIFeatureReadyResult
```

Users get clear error messages when a component isn't installed.

---

## 6. Implementation Priorities

### Phase 1: Update Build Configuration (✅ COMPLETED for InteractiveExperiences)
- [✅] Remove `GenerateCppWinRT` dependency from build targets (headers now from winappsdk_headers)
- [✅] Create `scripts/copy-python-namespace.ps1` to extract and copy namespace modules
- [✅] Update `Directory.Build.targets` to use dual-folder structure
- [✅] Update `generate-package.py` to handle both `winappsdk/` and `winappsdk_<Component>/`
- [✅] Test building InteractiveExperiences with new configuration
- [✅] Verify imports work: `from winappsdk.microsoft.ui.windowing import AppWindow`
- [✅] Test with uv: `uv run --with winappsdk_interactiveexperiences-3.2.1-cp313-cp313-win_amd64.whl python test_import.py`

### Phase 2: Multi-Component Testing (\u2705 COMPLETED - December 16, 2025)
- [\u2705] Apply same refactoring to Foundation package
- [\u2705] Apply same refactoring to AI package  
- [\u2705] Build AI with Foundation as reference
- [\u2705] Updated Directory.Build.targets to remove microsoft folder from component packages after copying to shared namespace
- [\u2705] Test Foundation imports: `from winappsdk.microsoft.windows.applifecycle import AppInstance`
- [\u2705] Successfully built wheels for Foundation and AI with dual-folder structure
- [ ] Test installing all three wheels together and verify namespace merging
- [ ] Verify native extensions don't conflict
- [ ] Test cross-component imports in integrated environment

### Phase 3: Distribution (PLANNED)
- [ ] Create metapackage (pure dependency aggregator)
- [ ] Update `winappsdk_headers` to use unified structure
- [ ] Test on PyPI (test.pypi.org)
- [ ] Document installation patterns
- [ ] Create migration guide from old structure

---

## 7. Technical Notes

### Native Extension Naming

PyWinRT generates unique native extension names based on full namespace:

```
_winappsdk_microsoft_windows_applifecycle.pyd     # From Foundation
_winappsdk_microsoft_windows_ai.pyd               # From AI
_winappsdk_microsoft_ui_composition.pyd           # From InteractiveExperiences
```

These are placed in the `winappsdk/` root and don't conflict.

### PEP 420 Namespace Package Rules

For PEP 420 to work:
1. **NO** `__init__.py` at `winappsdk/`
2. **NO** `__init__.py` at `winappsdk/microsoft/`
3. **NO** `__init__.py` at `winappsdk/microsoft/windows/`
4. **YES** `__init__.py` at leaf namespaces (e.g., `winappsdk/microsoft/windows/ai/`)

PyWinRT already follows this pattern - it only creates `__init__.py` at leaf namespaces.

### Header Sharing

Headers are still shared via `<ReferenceWinMD>` with `<HeaderPath>`:

```xml
<ReferenceWinMD Include="$(PkgMicrosoft_WindowsAppSDK_Foundation)\metadata">
  <PyPackageName>winappsdk</PyPackageName>  <!-- Same name! -->
  <HeaderPath>$(MSBuildProjectDirectory)\..\Foundation\obj\pkg\include</HeaderPath>
</ReferenceWinMD>
```

---

## 8. Comparison: Old vs New Architecture

| Aspect | Old (winappsdk_Component) | New (winappsdk) |
|--------|---------------------------|-----------------|
| Import pattern | `from winappsdk_AI.microsoft.windows.ai import X` | `from winappsdk.microsoft.windows.ai import X` |
| Metapackage complexity | Re-export code for every namespace | Just dependencies |
| PEP 420 | Not used | Required |
| Native extension names | `_winappsdk_AI_microsoft_windows_ai` | `_winappsdk_microsoft_windows_ai` |
| Namespace sharing | Not possible | Works via pip merge |
| PyPackage for PyWinRT | `winappsdk-AI`, `winappsdk-Foundation` | `winappsdk` for ALL |

---

## References

- [PEP 420 - Implicit Namespace Packages](https://peps.python.org/pep-0420/)
- [Setuptools Namespace Packages](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#finding-namespace-packages)
- [PyWinRT GitHub](https://github.com/pywinrt/pywinrt)
- [Windows App SDK Documentation](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/)

---

## Appendix A: Automatic WinMD Dependency Resolution

### Status: ✅ IMPLEMENTED (Test.WinMDResolution)

Use NuGet's official dependency graph (`project.assets.json`) to automatically resolve:
- **Direct references**: WindowsAppSDK WinMDs to generate bindings for (InputWinMD)
- **Transitive dependencies**: Other WindowsAppSDK WinMDs + Windows SDK WinMDs for type resolution (ReferenceWinMD)

**Location**: `Test.WinMDResolution/parse-nuget-graph.ps1`

---

## Appendix B: Headers Strategy

Headers are shared between component packages during build:
```xml
<ReferenceWinMD Include="...">
  <HeaderPath>$(MSBuildProjectDirectory)\..\Foundation\obj\pkg\include</HeaderPath>
</ReferenceWinMD>
```

Future optimization (if needed): Dedicated `winappsdk-headers` package.

---

## Appendix C: Native Dependencies & DLL Loading

Native DLLs (Bootstrap, etc.) are included in the NuGet packages and need to be distributed with Python wheels.

Future implementation:
```python
# winappsdk/__init__.py (or in leaf namespace __init__.py)
import os, sys

_lib_dir = os.path.join(os.path.dirname(__file__), ".libs")
if sys.platform == "win32" and os.path.exists(_lib_dir):
    os.add_dll_directory(_lib_dir)
```

---

## Appendix D: Demo Examples

### Basic Dynamic Dependencies (Foundation)
```python
from winappsdk.microsoft.windows.applicationmodel.dynamicdependency import Bootstrap

Bootstrap.Initialize(0x00010006)  # WindowsAppSDK 1.6
Bootstrap.Shutdown()
```

### App Lifecycle (Foundation)
```python
from winappsdk.microsoft.windows.applifecycle import AppInstance

instance = AppInstance.GetCurrent()
args = instance.GetActivatedEventArgs()
```

### AI Features (AI)
```python
from winappsdk.microsoft.windows.ai import AIFeatureReadyResult

# Check if AI features are available
result = AIFeatureReadyResult.GetAIFeatureReady()
```

### Composition (InteractiveExperiences)
```python
from winappsdk.microsoft.ui.composition import Compositor

compositor = Compositor()
visual = compositor.CreateContainerVisual()
```

---

## Appendix E: Historical Notes (Archived)

> **Note**: The following documents earlier design iterations that led to the current architecture.

### Earlier Approach: Component-Specific Module Names

An earlier design used `winappsdk_Foundation`, `winappsdk_AI` as module names, requiring 
a metapackage with re-export code. This was replaced with the unified `winappsdk` namespace 
approach using PEP 420, which is simpler and requires no re-export layer.

### Metapackage Re-export (Superseded)

The re-export pattern was:
```python
try:
    from winappsdk_Foundation.microsoft.windows.applifecycle import *
except ImportError:
    pass
```

This is no longer needed with the unified `winappsdk` PyPackage approach.

This is no longer needed with the unified `winappsdk` PyPackage approach.