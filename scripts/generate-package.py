import argparse
import sys
from pathlib import Path

SETUP_PY_TEMPLATE = """\
# WARNING: Please don't edit this file. It was automatically generated.
# Merged package setup.py that builds ALL extensions in a single package
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from winrt_sdk import get_include_dirs as get_winrt_include_dirs
from winappsdk_headers import get_include_dirs as get_winappsdk_include_dirs
import glob
import os


class build_ext_ex(build_ext):
    def build_extension(self, ext):
        if self.compiler.compiler_type == "msvc":
            ext.extra_compile_args = ["/std:c++20", "/permissive-"]
        else:
            raise ValueError(f"Unsupported compiler: {{self.compiler.compiler_type}}")

        build_ext.build_extension(self, ext)


# Package configuration
PACKAGE_NAME = "{package_name}"

# Namespaces to build
NAMESPACES = {namespaces_list}

# Find all cpp files (PyWinRT may generate them in subdirectories)
cpp_files = glob.glob("py.*.cpp") + glob.glob("*/py.*.cpp")

# Generate extensions from found cpp files
# Extension modules use winappsdk_* naming internally (for PyWinRT compatibility)
# but are imported by winappsdk.* public namespace
extensions = []
for cpp_file in cpp_files:
    # Extract namespace from filename
    basename = os.path.basename(cpp_file)
    if basename.startswith("py.") and basename.endswith(".cpp"):
        namespace = basename[3:-4]  # Remove "py." and ".cpp"
        ext_name = f"{{PACKAGE_NAME}}._{{PACKAGE_NAME}}_{{namespace.lower().replace('.', '_')}}"
        
        extensions.append(Extension(
            ext_name,
            sources=[cpp_file],
            # Local headers first (from reference packages with correct module names),
            # then winappsdk-headers/winrt-sdk for any missing headers
            include_dirs=["include/cppwinrt", "include/pywinrt"] + get_winrt_include_dirs() + get_winappsdk_include_dirs(),
            libraries=["windowsapp"],
        ))

setup(
    cmdclass={{"build_ext": build_ext_ex}},
    ext_modules=extensions,
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


def namespace_to_ext_name(package_name: str, namespace: str) -> str:
    """Convert namespace to extension name: Microsoft.UI.Input -> winappsdk_Foundation._winappsdk_Foundation_microsoft_ui_input"""
    py_package = ".".join(avoid_keyword(x.lower()) for x in namespace.split("."))
    return f"{package_name}._{package_name}_{py_package.replace('.', '_')}"


def generate_merged_package(
    output_dir: Path,
    package_name: str,
    namespaces: list,
):
    """Generate setup.py for a merged package with all namespaces."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating merged package '{package_name}' with {len(namespaces)} namespace(s)...")
    
    # Format namespaces as Python list literal
    namespaces_list = "[\n"
    for namespace in sorted(namespaces):
        namespaces_list += f'    "{namespace}",\n'
    namespaces_list += "]"
    
    # Generate setup.py
    setup_py_content = SETUP_PY_TEMPLATE.format(
        package_name=package_name,
        namespaces_list=namespaces_list,
    )
    
    with open(output_dir / "setup.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(setup_py_content)
    
    # Create __init__.py for winappsdk_* package (extension container)
    package_dir = output_dir / package_name
    package_dir.mkdir(exist_ok=True)
    init_file = package_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Auto-generated package - internal extension modules\n", encoding="utf-8")
    
    # winappsdk package is the user-facing namespace
    # (the actual microsoft/* structure is moved here in post-processing)
    
    print(f"[OK] Generated setup.py in {output_dir}")
    print(f"  Package: {package_name}")
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
        help="Output directory for generated setup.py"
    )
    parser.add_argument(
        "--package-name",
        required=True,
        help="Package name with underscores (e.g., 'winappsdk_Foundation')"
    )
    parser.add_argument(
        "--namespace",
        action="append",
        dest="namespaces",
        required=True,
        help="Namespace to include (can be specified multiple times, e.g., 'Microsoft.UI', 'Microsoft.UI.Input')"
    )
    
    args = parser.parse_args()
    
    if not args.namespaces:
        print("Error: At least one namespace must be specified with --namespace")
        sys.exit(1)
    
    generate_merged_package(
        args.output_dir,
        args.package_name,
        args.namespaces,
    )


if __name__ == "__main__":
    main()
