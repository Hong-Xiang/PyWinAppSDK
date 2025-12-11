# PyWinAppSDK
Python Projection For WinAppSDK Packages

`winappsdk-Foundation\winappsdk-Foundation-Microsoft.Windows.ApplicationModel.Background.UniversalBGTask\py.Microsoft.Windows.ApplicationModel.Background.UniversalBGTask.cpp` generation is skipped as currently there is a HACK on ITask added `https://github.com/pywinrt/pywinrt/commit/a57d450cea4bc5c23f15e721e9908adb4fab805e`, for fixing a WinAppSDK bug, which WinAppSDK solved in `https://github.com/microsoft/WindowsAppSDK/pull/5313/files#diff-ebf7d33e48a6c2024157772d824105c404d00ce05e52619001a75a40ffe71b21`.

# Projection Package Generation Design

## SDK Package
Contains header files generated from cppwinrt and pywinrt.

Header files are generated in a monolithic way, meaning all component packages are generated into a single SDK package.

The reason for this is that referenced component packages's headers need to be used in consuming component packages,
but pywinrt gener


## Component Package