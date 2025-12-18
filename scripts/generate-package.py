import argparse
import sys
from pathlib import Path
from typing import Optional

PYPROJECT_TOML_TEMPLATE = """\
# WARNING: Please don't edit this file. It was automatically generated.

[build-system]
requires = [
    "setuptools>=78", 
    "winrt-sdk",
    "winappsdk-headers",
]

build-backend = "setuptools.build_meta"

[project]
name = "{package_prefix}"
version = "{version}"
description = "Python projection of Windows Runtime (WinRT) APIs - Merged Package"
readme = "README.md"
license = "MIT"
classifiers = [
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Intended Audience :: Developers",
]
requires-python = ">=3.9"
dependencies = [
    "winrt-runtime",
{dependencies}]

[project.urls]
Documentation = "https://pywinrt.readthedocs.io"
Repository = "https://github.com/pywinrt/pywinrt"
Changelog = "https://github.com/pywinrt/pywinrt/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools.package-data]
"*" = ["*.pyi", "py.typed"]

[tool.cibuildwheel]
before-build = "uv pip install setuptools"
# don't build for PyPy
skip = "pp*"
# suppress warnings about ARM64 testing
test-skip = "*-win_arm64"

[tool.cibuildwheel.windows]
archs = ["x86", "AMD64", "ARM64"]
"""

SETUP_PY_TEMPLATE = """\
# WARNING: Please don't edit this file. It was automatically generated.
# Merged package setup.py that builds ALL extensions in a single package
from setuptools import Extension, setup, find_packages, find_namespace_packages
from setuptools.command.build_ext import build_ext
from winrt_sdk import get_include_dirs as get_winrt_include_dirs
from winappsdk_headers import get_include_dirs as get_winappsdk_include_dirs


class build_ext_ex(build_ext):
    def build_extension(self, ext):
        if self.compiler.compiler_type == "msvc":
            ext.extra_compile_args = ["/std:c++20", "/permissive-"]
        else:
            raise ValueError(f"Unsupported compiler: {{self.compiler.compiler_type}}")

        build_ext.build_extension(self, ext)


# Package configuration
PACKAGE_PREFIX = "{package_prefix}"
SAFE_PREFIX = "{safe_prefix}"

# Namespaces to build
NAMESPACES = {namespaces_list}

# Generate extensions from namespaces
# Extension modules use winappsdk_* naming internally (for PyWinRT compatibility)
# but are imported by winapp.* public namespace
extensions = [
    Extension(
        f"{{SAFE_PREFIX}}._{{SAFE_PREFIX}}_{{ns.lower().replace('.', '_')}}",
        sources=[f"py.{{ns}}.cpp"],
        # Local headers first (from reference packages with correct module names),
        # then winappsdk-headers/winrt-sdk for any missing headers
        include_dirs=["include/cppwinrt", "include/pywinrt"] + get_winrt_include_dirs() + get_winappsdk_include_dirs(),
        libraries=["windowsapp"],
    )
    for ns in NAMESPACES
]

setup(
    cmdclass={{"build_ext": build_ext_ex}},
    ext_modules=extensions,
    # Component-specific packages (regular packages)
    packages=(
        find_packages(where=".", include=["{safe_prefix}", "{safe_prefix}.*"]) +
        # Namespace packages (PEP 420) - allows multiple wheels to contribute to winappsdk.*
        find_namespace_packages(where=".", include=["winappsdk", "winappsdk.*"])
    ),
)
"""

PYTHON_KEYWORDS = {
    "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "finally", "for", "from",
    "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
    "or", "pass", "raise", "return", "try", "while", "with", "yield",
}


def avoid_keyword(name: str) -> str:
    return f"{name}_" if name in PYTHON_KEYWORDS else name


def namespace_to_ext_name(package_prefix: str, namespace: str) -> str:
    """Convert namespace to extension name: Microsoft.UI.Input -> winappixp._winappixp_microsoft_ui_input"""
    # Replace hyphens with underscores in package prefix for valid Python module name
    safe_prefix = package_prefix.replace('-', '_')
    py_package = ".".join(avoid_keyword(x.lower()) for x in namespace.split("."))
    return f"{safe_prefix}._{safe_prefix}_{py_package.replace('.', '_')}"


def generate_merged_package(
    output_dir: Path,
    package_prefix: str,
    namespaces: list,
    version: str,
    dependencies: Optional[list] = None
):
    """Generate setup.py and pyproject.toml for a merged package with all namespaces."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating merged package '{package_prefix}' with {len(namespaces)} namespace(s)...")
    
    # Replace hyphens with underscores for valid Python package name
    safe_prefix = package_prefix.replace('-', '_')
    
    # Format namespaces as Python list literal
    namespaces_list = "[\n"
    for namespace in sorted(namespaces):
        namespaces_list += f'    "{namespace}",\n'
    namespaces_list += "]"
    
    # Generate setup.py
    setup_py_content = SETUP_PY_TEMPLATE.format(
        package_prefix=package_prefix,
        safe_prefix=safe_prefix,
        namespaces_list=namespaces_list,
    )
    
    with open(output_dir / "setup.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(setup_py_content)
    
    # Create __init__.py for both winappsdk_* (extension container) and winapp (user-facing)
    # winappsdk_* package holds the C++ extensions
    package_dir = output_dir / safe_prefix
    package_dir.mkdir(exist_ok=True)
    init_file = package_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Auto-generated package - internal extension modules\n", encoding="utf-8")
    
    # winappsdk package is the user-facing namespace
    # (the actual microsoft/* structure is moved here in post-processing)
    
    # Format additional dependencies
    deps_str = ""
    if dependencies:
        for dep in sorted(dependencies):
            deps_str += f'    "{dep}",\n'
    
    # Generate pyproject.toml
    pyproject_content = PYPROJECT_TOML_TEMPLATE.format(
        package_prefix=package_prefix,
        version=version,
        dependencies=deps_str,
    )
    
    with open(output_dir / "pyproject.toml", "w", encoding="utf-8", newline="\n") as f:
        f.write(pyproject_content)
    
    print(f"[OK] Generated setup.py and pyproject.toml in {output_dir}")
    print(f"  Extensions: {len(namespaces)}")
    for ns in sorted(namespaces):
        print(f"    - {ns}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate merged Python package with multiple namespace extensions."
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Output directory for generated setup.py and pyproject.toml"
    )
    parser.add_argument(
        "--package-prefix",
        required=True,
        help="Package prefix (e.g., 'winappsdk-Foundation')"
    )
    parser.add_argument(
        "--namespace",
        action="append",
        dest="namespaces",
        required=True,
        help="Namespace to include (can be specified multiple times, e.g., 'Microsoft.UI', 'Microsoft.UI.Input')"
    )
    parser.add_argument(
        "--dependency",
        action="append",
        dest="dependencies",
        help="Additional dependency to include (can be specified multiple times, e.g., 'winrt-Windows.Foundation')"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Version of the SDK package"
    )
    
    args = parser.parse_args()
    
    if not args.namespaces:
        print("Error: At least one namespace must be specified with --namespace")
        sys.exit(1)
    
    generate_merged_package(
        args.output_dir,
        args.package_prefix,
        args.namespaces,
        args.version,
        args.dependencies
    )


if __name__ == "__main__":
    main()
