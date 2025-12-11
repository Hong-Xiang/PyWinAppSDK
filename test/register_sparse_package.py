"""
Sparse package registration helper for Windows AI APIs testing.

This script registers a sparse MSIX package to provide package identity
for the Python interpreter, allowing access to Windows AI APIs.

Usage:
    python register_sparse_package.py register   - Register the sparse package
    python register_sparse_package.py unregister - Unregister the sparse package
    python register_sparse_package.py run <script> [args] - Run script with package identity
"""

import os
import sys
import ctypes
from ctypes import wintypes
import subprocess
import tempfile
import shutil


def is_admin():
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_script_dir():
    """Get the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))


def create_sparse_package_structure(target_dir: str, python_path: str):
    """
    Create the sparse package structure with required assets.
    
    Args:
        target_dir: Directory to create the package structure
        python_path: Path to the Python interpreter
    """
    # Create Assets directory
    assets_dir = os.path.join(target_dir, "Assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create minimal PNG files (1x1 transparent PNG)
    # This is a valid 1x1 transparent PNG file
    minimal_png = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # 8-bit RGBA
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
        0x42, 0x60, 0x82
    ])
    
    # Create required asset files
    asset_files = [
        "StoreLogo.png",
        "Square150x150Logo.png",
        "Square44x44Logo.png",
        "Wide310x150Logo.png"
    ]
    
    for asset in asset_files:
        asset_path = os.path.join(assets_dir, asset)
        with open(asset_path, "wb") as f:
            f.write(minimal_png)
    
    # Copy AppxManifest.xml
    manifest_src = os.path.join(get_script_dir(), "sparse-package", "AppxManifest.xml")
    manifest_dst = os.path.join(target_dir, "AppxManifest.xml")
    shutil.copy2(manifest_src, manifest_dst)
    
    # Copy python_launcher.cmd
    launcher_src = os.path.join(get_script_dir(), "sparse-package", "python_launcher.cmd")
    launcher_dst = os.path.join(target_dir, "python_launcher.cmd")
    if os.path.exists(launcher_src):
        shutil.copy2(launcher_src, launcher_dst)
    
    print(f"✅ Created sparse package structure at: {target_dir}")
    return target_dir


def register_sparse_package(external_location: str = None):
    """
    Register a sparse package to provide package identity.
    
    Args:
        external_location: Path where external content (Python) is located
    """
    script_dir = get_script_dir()
    sparse_pkg_dir = os.path.join(script_dir, "sparse-package")
    
    if external_location is None:
        # Use the Python installation directory
        external_location = os.path.dirname(sys.executable)
    
    # Create temporary directory for the package structure
    temp_dir = os.path.join(tempfile.gettempdir(), "PyWinAppSDK_SparsePackage")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Create package structure
    create_sparse_package_structure(temp_dir, sys.executable)
    
    manifest_path = os.path.join(temp_dir, "AppxManifest.xml")
    
    print(f"Registering sparse package...")
    print(f"  Manifest: {manifest_path}")
    print(f"  External location: {external_location}")
    
    # Use PowerShell to register the sparse package
    ps_script = f'''
    $manifest = "{manifest_path}"
    $externalLocation = "{external_location}"
    
    try {{
        Add-AppxPackage -Path $manifest -ExternalLocation $externalLocation -Register
        Write-Host "✅ Sparse package registered successfully!"
    }} catch {{
        Write-Host "❌ Failed to register sparse package: $_"
        exit 1
    }}
    '''
    
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def unregister_sparse_package():
    """Unregister the sparse package."""
    print("Unregistering sparse package...")
    
    ps_script = '''
    $packageName = "PyWinAppSDK.AITest"
    
    try {
        $pkg = Get-AppxPackage -Name $packageName
        if ($pkg) {
            Remove-AppxPackage -Package $pkg.PackageFullName
            Write-Host "✅ Sparse package unregistered successfully!"
        } else {
            Write-Host "Package not found - already unregistered."
        }
    } catch {
        Write-Host "❌ Failed to unregister sparse package: $_"
        exit 1
    }
    '''
    
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def run_with_package_identity(script_path: str, args: list = None):
    """
    Run a Python script with package identity.
    
    This uses the Windows Application Model API to activate the app
    with package identity.
    """
    if args is None:
        args = []
    
    # First, ensure the package is registered
    ps_script = '''
    $packageName = "PyWinAppSDK.AITest"
    $pkg = Get-AppxPackage -Name $packageName
    if ($pkg) {
        Write-Host $pkg.PackageFullName
    } else {
        Write-Host "NOT_FOUND"
    }
    '''
    
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    
    package_name = result.stdout.strip()
    
    if package_name == "NOT_FOUND" or not package_name:
        print("❌ Sparse package not registered. Please run 'register' first.")
        return False
    
    print(f"Found package: {package_name}")
    print(f"Running script: {script_path}")
    print(f"Arguments: {args}")
    
    # Unfortunately, running Python with package identity from another Python process
    # is complex. The package identity is tied to the process activation.
    # 
    # For now, we'll use a workaround: create a launcher script that
    # can be invoked via the package's activation.
    
    print("\n⚠️  Direct execution with package identity requires special activation.")
    print("The sparse package provides identity, but the Python interpreter")
    print("needs to be launched through the package activation mechanism.")
    print("\nAlternative: Run Python directly after registering the package.")
    
    # Try running Python directly - sometimes the package identity
    # is inherited if the package is registered for the current user
    cmd = [sys.executable, script_path] + args
    print(f"\nTrying direct execution: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCurrent Python:", sys.executable)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "register":
        external_loc = sys.argv[2] if len(sys.argv) > 2 else None
        success = register_sparse_package(external_loc)
        sys.exit(0 if success else 1)
        
    elif command == "unregister":
        success = unregister_sparse_package()
        sys.exit(0 if success else 1)
        
    elif command == "run":
        if len(sys.argv) < 3:
            print("Usage: python register_sparse_package.py run <script> [args]")
            sys.exit(1)
        script = sys.argv[2]
        args = sys.argv[3:]
        success = run_with_package_identity(script, args)
        sys.exit(0 if success else 1)
        
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
