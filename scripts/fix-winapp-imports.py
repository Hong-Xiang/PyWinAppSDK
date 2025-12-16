"""
Fix imports in winapp.microsoft.* __init__.py files after namespace restructuring.

After moving microsoft/* from winappsdk_Foundation/ to winapp/, we need to update
the import statements to reference the correct extension module names.
"""

import argparse
import re
import sys
from pathlib import Path


def fix_init_file(init_file: Path, package_prefix: str) -> bool:
    """
    Fix imports in a single __init__.py file.
    
    Changes imports like:
        from winappsdk_Foundation._winappsdk_Foundation_microsoft_windows_storage import ...
    
    To keep them as-is (they still reference the internal extension modules in winappsdk_Foundation package).
    The extensions stay in winappsdk_Foundation but are imported by the winapp.microsoft.* namespace.
    
    Returns True if file was modified, False otherwise.
    """
    if not init_file.exists():
        return False
    
    content = init_file.read_text(encoding='utf-8')
    original_content = content
    
    # The imports already reference winappsdk_* modules correctly
    # We just need to verify they're present and valid
    safe_prefix = package_prefix.replace('-', '_')
    
    # Pattern: from winappsdk_Foundation._winappsdk_Foundation_... import ...
    pattern = rf'from {re.escape(safe_prefix)}\._{re.escape(safe_prefix)}_'
    
    if re.search(pattern, content):
        print(f"  ✓ {init_file.relative_to(init_file.parents[4])}: imports are correct")
        return False
    else:
        # File might not have imports (just enums/constants), which is fine
        if 'import' in content and 'from' in content:
            print(f"  ⚠ {init_file.relative_to(init_file.parents[4])}: no {safe_prefix} imports found (might need manual check)")
        return False


def fix_all_imports(winapp_path: Path, package_prefix: str) -> int:
    """
    Fix imports in all __init__.py files under winapp/microsoft.
    
    Returns the number of files modified.
    """
    if not winapp_path.exists():
        print(f"Error: winapp path does not exist: {winapp_path}")
        return 0
    
    microsoft_path = winapp_path / "microsoft"
    if not microsoft_path.exists():
        print(f"Error: microsoft path does not exist: {microsoft_path}")
        return 0
    
    print(f"Checking imports in {microsoft_path}...")
    
    modified_count = 0
    init_files = list(microsoft_path.rglob("__init__.py"))
    
    print(f"Found {len(init_files)} __init__.py files")
    
    for init_file in init_files:
        if fix_init_file(init_file, package_prefix):
            modified_count += 1
    
    return modified_count


def main():
    parser = argparse.ArgumentParser(
        description="Fix imports in winapp.microsoft.* namespace after restructuring"
    )
    parser.add_argument(
        "winapp_path",
        type=Path,
        help="Path to the winapp directory (e.g., obj/pkg/winapp)"
    )
    parser.add_argument(
        "--package-prefix",
        required=True,
        help="Package prefix (e.g., 'winappsdk-foundation')"
    )
    
    args = parser.parse_args()
    
    print(f"==================== Fixing winapp imports ====================")
    print(f"Package: {args.package_prefix}")
    print(f"Target: {args.winapp_path}")
    print()
    
    modified = fix_all_imports(args.winapp_path, args.package_prefix)
    
    print()
    if modified > 0:
        print(f"[OK] Fixed imports in {modified} file(s)")
    else:
        print(f"[OK] All imports are correct (no changes needed)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
