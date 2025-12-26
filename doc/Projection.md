# PyWinAppSDK Projection

Leverage PyWinRT to generate projections,
but need special handling for packaging and dependencies.

PyWinRT requires following arguments:

```
pywinrt 
--input <input-namespace-prefix>;<input-winmd-paths> 
--ref <ref-winmd-prefix>;<ref-winmd-paths>
```

And will generate both cpp header files and cpp source files for python native extension module.

Generated header files is required for both input winmd and referenced winmd,
and generated header file are same when put in input position and ref position. 
Only input winmd will generate cpp source files.

Generated header/cpp files have namespace in their name, 
e.g.
`py.Microsoft.Windows.ApplicationModel.Background.cpp`
and 
`py.Microsoft.Windows.ApplicationModel.Background.h`.
As showing above, it is only using namespace part, however the `<namespace-prefix>` existing in the content of header file:
```
    template<>
    struct py_type<winrt::Microsoft::Graphics::DirectX::DirectXAlphaMode>
    {
        static constexpr std::string_view qualified_name = "winappsdk.microsoft.graphics.directx.DirectXAlphaMode";
        static constexpr const char* module_name = "winappsdk.microsoft.graphics.directx";
        static constexpr const char* type_name = "DirectXAlphaMode";
    };
```
thus if we want to properly mirror the component nuget package structure in python projection package structure, and want to share a common root namespace `winappsdk`,
a special handling is needed to adjust the `<namespace-prefix>` accordingly.

PyWinRT does not allow same prefix for both input and ref winmds, thus we need to adjust the ref winmd namespace prefix to avoid conflict.

Since those namespace prefixes are not generated cpp files,
current strategy is to adjust them in the packaging step,
first generate a (build time only) header package for all winappsdk component packages, all winmd are merged together, the header package is never published,
and won't be listed in runtime dependency list.

Then in each component package, we adjust the ref namespace prefix to point to the header package namespace prefix.
Thus the generate component package would have a proper component package name prefix on its native extension package's name,
but all its native types are listed under winappsdk namespace,
and we also move its generated python interface files under its component package folder to common winappsdk folder,
and leveraging python's namespace package feature to allow importing from winappsdk root namespace.

## Discussions

### Why not just generate full winappsdk package and add some meta package to adjust namespace?
Because we are moving towards more flexible composition of winappsdk component package versions, although currently we havn't enable self-contained mode in python yet,
but we want to move towards that direction in future.
Thus always bundling a specific combination of component package versions is not desired.

### Why not just package each namespace into separate python package directly?
Ideally it would work for versioning problem, but in that case, due to python not support "namespace" in file, it only support file system folder as namespace,
then we need 2 level of namespace mapping:
namespace map to the python package name,
and then namespace map to in package's folder structure,
it would cause 2 occurrences of namespace in the import path,
e.g.
```
winappsdk-Foundation.Microsoft.Windows.Storage.Pickers/winappsdk/Foundation/Microsoft/Windows/Storage/Pickers/__init__.py <-- the real module file>
```
and in WinAppSDK, we have some namespaces with long names, e.g. `winappsdk-Foundation-Microsoft.Windows.ApplicationModel.Background.UniversalBGTask`,
2 times of that occurrence would make it likely to exceed path length limit on Windows,
which we already encountered in local builds,
and since users would use python package frequently in the venv folder, which itself may already have arbitrary path length, we need to try to reduce the path not to trigger highly likely path length issue.
