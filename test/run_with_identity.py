"""
Run Python script with package identity using Windows Package Manager APIs.

This uses the PackageManager to properly launch with package identity.
"""

import os
import sys
import subprocess
import tempfile


def check_package_registered():
    """Check if the sparse package is registered and get its info."""
    ps_script = '''
    $packageName = "PyWinAppSDK.AITest"
    $pkg = Get-AppxPackage -Name $packageName
    if ($pkg) {
        Write-Output "FOUND"
        Write-Output $pkg.PackageFullName
        Write-Output $pkg.PackageFamilyName
        Write-Output $pkg.InstallLocation
    } else {
        Write-Output "NOT_FOUND"
    }
    '''
    
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    
    lines = result.stdout.strip().split('\n')
    if lines[0] == "FOUND" and len(lines) >= 4:
        return {
            "found": True,
            "full_name": lines[1].strip(),
            "family_name": lines[2].strip(),
            "location": lines[3].strip()
        }
    return {"found": False}


def run_script_in_package_context(script_path: str, args: list = None):
    """
    Run a Python script using package identity.
    
    Uses IApplicationActivationManager to launch the packaged app.
    Since arguments don't always pass correctly through activation,
    we write the command to a config file that entry_point.py reads.
    """
    if args is None:
        args = []
    
    pkg_info = check_package_registered()
    
    if not pkg_info["found"]:
        print("Error: Sparse package not registered.")
        print("Run: python register_sparse_package.py register")
        return False
    
    print(f"Package: {pkg_info['full_name']}")
    print(f"Family:  {pkg_info['family_name']}")
    print(f"Location: {pkg_info['location']}")
    
    script_abs = os.path.abspath(script_path)
    
    # Write script and args to config file (more reliable than passing via activation)
    config_file = os.path.join(tempfile.gettempdir(), "pywinappsdk_run_config.txt")
    cmd_line = f'"{script_abs}"' + ''.join(f' "{a}"' for a in args)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(cmd_line)
    
    print(f"\nConfig file: {config_file}")
    print(f"Command: {cmd_line}")
    
    app_id = f"{pkg_info['family_name']}!PythonAITest"
    
    # Get the entry point script path
    entry_point = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sparse-package", "entry_point.py"
    )
    
    # Create a bootstrap script that Python will run
    # This script will exec the entry_point.py which reads the config
    bootstrap_script = os.path.join(tempfile.gettempdir(), "pywinappsdk_bootstrap.py")
    with open(bootstrap_script, 'w', encoding='utf-8') as f:
        f.write(f'''# PyWinAppSDK Bootstrap - Auto-generated
import sys
sys.argv = [r"{entry_point}"]
exec(open(r"{entry_point}", encoding="utf-8").read())
''')
    
    # Pass bootstrap script as argument
    arguments = f'"{bootstrap_script}"'
    
    print(f"\nApp ID: {app_id}")
    print(f"Bootstrap: {bootstrap_script}")
    print(f"Entry point: {entry_point}")
    print(f"Target script: {script_abs}")
    print(f"Script args: {args}")

    # Use PowerShell with IApplicationActivationManager to launch
    # Escape quotes for PowerShell
    arguments_escaped = arguments.replace('"', '""').replace("'", "''")
    
    ps_script = f'''
$ErrorActionPreference = "Stop"

$appId = "{app_id}"
$arguments = '{arguments}'

Write-Host "Activating: $appId"
Write-Host "Arguments: $arguments"

# Use CSharp code to call COM interface
$code = @"
using System;
using System.Runtime.InteropServices;

public class AppActivator {{
    [ComImport, Guid("2e941141-7f97-4756-ba1d-9decde894a3d"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IApplicationActivationManager {{
        int ActivateApplication([MarshalAs(UnmanagedType.LPWStr)] string appUserModelId, 
                               [MarshalAs(UnmanagedType.LPWStr)] string arguments, 
                               uint options, 
                               out uint processId);
    }}

    [ComImport, Guid("45BA127D-10A8-46EA-8AB7-56EA9078943C")]
    class ApplicationActivationManager {{ }}

    public static uint Activate(string appId, string args) {{
        var aam = (IApplicationActivationManager)new ApplicationActivationManager();
        uint pid;
        int hr = aam.ActivateApplication(appId, args, 0, out pid);
        if (hr != 0) {{
            throw new Exception("ActivateApplication failed with HRESULT: 0x" + hr.ToString("X8"));
        }}
        return pid;
    }}
}}
"@

Add-Type -TypeDefinition $code

try {{
    $processId = [AppActivator]::Activate($appId, $arguments)
    Write-Host "Launched with process ID: $processId"
    
    # Wait for the process to complete
    try {{
        $proc = Get-Process -Id $processId -ErrorAction Stop
        Write-Host "Waiting for process to complete..."
        $proc.WaitForExit()
        Write-Host "Process exited with code: $($proc.ExitCode)"
        exit $proc.ExitCode
    }} catch {{
        Write-Host "Process already exited or cannot be monitored"
        exit 0
    }}
}} catch {{
    Write-Error "Exception: $_"
    exit 1
}}
'''
    
    print("\nActivating packaged application...")
    print("-" * 60)
    
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=False  # Show output in real-time
    )
    
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_with_identity.py <script.py> [args...]")
        print("\nThis runs a Python script with package identity using")
        print("the registered sparse package.")
        print("\nThe sparse package must be registered first:")
        print("  python register_sparse_package.py register")
        sys.exit(1)
    
    script_path = sys.argv[1]
    args = sys.argv[2:]
    
    if not os.path.isabs(script_path):
        # Check current directory first
        if os.path.exists(script_path):
            script_path = os.path.abspath(script_path)
        else:
            # Try relative to test directory
            test_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(test_dir, script_path)
    
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("PyWinAppSDK - Run with Package Identity")
    print("=" * 60)
    print(f"Script: {script_path}")
    print(f"Arguments: {args}")
    print()
    
    success = run_script_in_package_context(script_path, args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
