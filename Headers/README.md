# PySDK - WindowsAppSDK Header Collection Package

## Overview

PySDK is a header-only package that collects all transitive WinMD files from WindowsAppSDK packages and generates CppWinRT headers. It serves as a base dependency for component packages (Foundation, AI, InteractiveExperiences, etc.), providing a complete set of headers for compilation without duplicating header generation across packages.

## Purpose

- **Transitive WinMD Resolution**: Automatically discovers all WinMD files from WindowsAppSDK packages using the `ResolveWinMDReferences` build task
- **Centralized Header Generation**: Generates CppWinRT headers once for all WindowsAppSDK components
- **Dependency Management**: Downstream packages reference PySDK to get all necessary headers without re-generating them

## Build Process

When building PySDK, the following steps occur:

1. **WinMD Resolution** (`ResolveAllWinMDs` target):
   - Uses `ResolveWinMDReferences` task to discover all WinMD files from NuGet packages
   - Separates direct dependencies (InputWinMD) from transitive dependencies (ReferencedWinMD)
   - Manually adds WebView2 WinMD (located in `lib` folder instead of standard `metadata` folder)

2. **Header Generation**:
   - **CppWinRT**: Generates C++/WinRT projection headers for all discovered WinMDs
   - **PyWinRT**: Skipped (see "Why PyWinRT is Skipped" section below)

3. **Output**:
   - CppWinRT headers: `obj/pkg/include/cppwinrt/`

## Discovered WindowsAppSDK Components

PySDK automatically resolves WinMDs from these packages:

### Direct Dependencies (Input WinMDs)
- Microsoft.WindowsAppSDK.Foundation
- Microsoft.WindowsAppSDK.InteractiveExperiences  
- Microsoft.WindowsAppSDK

### Transitive Dependencies (Referenced WinMDs)
- Microsoft.WindowsAppSDK.AI
- Microsoft.WindowsAppSDK.ML
- Microsoft.WindowsAppSDK.Widgets
- Microsoft.WindowsAppSDK.WinUI
- Microsoft.Web.WebView2 (manually added)

## Why PyWinRT Header Generation is Skipped

PyWinRT header generation is intentionally skipped for PySDK because:

1. **Package Name Conflict**: PyWinRT does not allow the same package name for both `--input` and `--reference` arguments
2. **Circular References**: PySDK collects all WinMDs transitively, which would cause circular package references in PyWinRT
3. **Component-Specific Generation**: Component packages (Foundation, AI, etc.) generate their own PyWinRT headers specific to their namespaces, while referencing PySDK's CppWinRT headers for transitive dependencies

This design allows component packages to:
- Generate PyWinRT bindings for their specific APIs
- Reference PySDK for complete CppWinRT header coverage
- Avoid duplicate header generation and circular dependencies

## Usage in Component Packages

Component packages like Foundation should:

1. **Reference PySDK** (as ProjectReference or PackageReference when packaged)
2. **Generate their own PyWinRT headers** for their specific namespaces
3. **Reference PySDK's CppWinRT headers** in their ReferenceWinMD items:

```xml
<ReferenceWinMD Include="...">
  <PyPackageName>other-package</PyPackageName>
  <HeaderPath>$(PySDKHeaderPath)\cppwinrt</HeaderPath>
</ReferenceWinMD>
```

## Build Configuration

### Key Properties
- `PackageName`: `winapp-sdk`
- `CppWinRTOutputPath`: `obj/pkg/include/cppwinrt`
- `GeneratePyWinAppSDK`: `false` (does not generate Python wheels)

### NuGet Dependencies
- Microsoft.Windows.SDK.CPP (build tools)
- Microsoft.Windows.CppWinRT (code generator)
- Microsoft.WindowsAppSDK (all components)
- Microsoft.Web.WebView2 (WinUI dependency)
- PyWinAppSDK.Build.Tasks (WinMD resolution)

## Integration with Build System

PySDK integrates with the PyWinAppSDK build system through:

- **Directory.Build.props**: Provides common properties and paths
- **Directory.Build.targets**: Provides shared build targets (though PySDK overrides most of them)
- **PyWinAppSDK.Build.Tasks**: Provides the `ResolveWinMDReferences` task

## Future Improvements

- Package PySDK as a NuGet package for easier consumption by component packages
- Automate detection of packages like WebView2 that store WinMDs in non-standard locations
- Consider generating a manifest file listing all resolved WinMDs for downstream reference
