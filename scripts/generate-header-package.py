"""
Generate a header-only Python package for WindowsAppSDK.

This script creates a Python package that contains CppWinRT and PyWinRT headers,
allowing component packages to easily reference them during compilation.
"""

import argparse
import sys
from pathlib import Path

PYPROJECT_TOML_TEMPLATE = """\
# WARNING: Please don't edit this file. It was automatically generated.

[build-system]
requires = ["setuptools>=78"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "{version}"
description = "Header files for WindowsAppSDK Python bindings"
readme = "README.md"
license = "MIT"
classifiers = [
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Intended Audience :: Developers",
    "Development Status :: 4 - Beta",
]
requires-python = ">=3.9"
dependencies = []

[project.urls]
Repository = "https://github.com/user/PyWinAppSDK"

[tool.setuptools]
packages = ["{safe_name}"]

[tool.setuptools.package-data]
"{safe_name}" = [
    "include/**/*.h",
    "include/**/*.hpp",
]
"""

INIT_PY_TEMPLATE = '''\
"""
{package_name} - Header files for WindowsAppSDK Python bindings.

This package provides CppWinRT and PyWinRT headers for building
WindowsAppSDK Python extension modules.

Usage:
    from {safe_name} import get_include_dirs
    
    # In setup.py Extension:
    Extension(
        "mymodule",
        sources=["mymodule.cpp"],
        include_dirs=get_include_dirs(),
        ...
    )
"""

from pathlib import Path

__version__ = "{version}"

_PACKAGE_DIR = Path(__file__).parent


def get_include_dir() -> Path:
    """Return the path to the include directory containing all headers."""
    return _PACKAGE_DIR / "include"


def get_cppwinrt_include_dir() -> Path:
    """Return the path to CppWinRT headers."""
    return _PACKAGE_DIR / "include" / "cppwinrt"


def get_pywinrt_include_dir() -> Path:
    """Return the path to PyWinRT headers."""
    return _PACKAGE_DIR / "include" / "pywinrt"


def get_include_dirs() -> list[str]:
    """
    Return all include directories needed for building extensions.
    
    This returns paths as strings for direct use in setuptools Extension().
    """
    base = _PACKAGE_DIR / "include"
    return [
        str(base / "cppwinrt"),
        str(base / "pywinrt"),
    ]
'''

README_TEMPLATE = """\
# {package_name}

Header files for building WindowsAppSDK Python extension modules.

## Overview

This package provides pre-generated C++ headers for the Windows App SDK,
including both CppWinRT and PyWinRT projections. Component packages
(like `winappsdk-Foundation`, `winappsdk-AI`, etc.) use these headers
when building their Python extension modules.

## Installation

```bash
pip install {package_name}
```

## Usage

In your `setup.py`:

```python
from setuptools import Extension, setup
from {safe_name} import get_include_dirs

ext = Extension(
    "mypackage._mymodule",
    sources=["src/mymodule.cpp"],
    include_dirs=get_include_dirs(),
    libraries=["windowsapp"],
)

setup(ext_modules=[ext])
```

## Available Functions

- `get_include_dirs()` - Returns list of include directories (CppWinRT + PyWinRT)
- `get_cppwinrt_include_dir()` - Returns path to CppWinRT headers only
- `get_pywinrt_include_dir()` - Returns path to PyWinRT headers only
- `get_include_dir()` - Returns base include directory

## Contents

This package includes headers for:
- Windows App SDK Foundation APIs
- Windows App SDK AI APIs  
- Windows App SDK Interactive Experiences APIs
- WinUI 3 APIs
- WebView2 APIs
- And all transitive dependencies

## Version

{version}
"""


def generate_header_package(
    output_dir: Path,
    package_name: str,
    version: str,
):
    """Generate a header-only Python package."""
    
    # Normalize package name for Python module
    safe_name = package_name.replace('-', '_')
    
    print(f"Generating header package '{package_name}' v{version}")
    print(f"  Output: {output_dir}")
    print(f"  Python module: {safe_name}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create package directory
    package_dir = output_dir / safe_name
    package_dir.mkdir(exist_ok=True)
    
    # Generate pyproject.toml
    pyproject_content = PYPROJECT_TOML_TEMPLATE.format(
        package_name=package_name,
        safe_name=safe_name,
        version=version,
    )
    (output_dir / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")
    print("  [OK] pyproject.toml")
    
    # Generate __init__.py
    init_content = INIT_PY_TEMPLATE.format(
        package_name=package_name,
        safe_name=safe_name,
        version=version,
    )
    (package_dir / "__init__.py").write_text(init_content, encoding="utf-8")
    print("  [OK] __init__.py")
    
    # Generate README.md
    readme_content = README_TEMPLATE.format(
        package_name=package_name,
        safe_name=safe_name,
        version=version,
    )
    (output_dir / "README.md").write_text(readme_content, encoding="utf-8")
    print("  [OK] README.md")
    
    # Ensure include directory exists (headers should be copied separately)
    include_dir = package_dir / "include"
    include_dir.mkdir(exist_ok=True)
    
    print(f"\nPackage structure created at {output_dir}")
    print(f"NOTE: Copy headers to {include_dir}/cppwinrt and {include_dir}/pywinrt")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a header-only Python package for WindowsAppSDK."
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Output directory for the package"
    )
    parser.add_argument(
        "--package-name",
        required=True,
        help="Package name (e.g., 'winapp-headers')"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Package version"
    )
    
    args = parser.parse_args()
    
    generate_header_package(
        args.output_dir,
        args.package_name,
        args.version,
    )


if __name__ == "__main__":
    main()
