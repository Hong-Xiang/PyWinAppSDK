"""
Simple launcher for Python with package identity.

Uses explorer.exe shell:AppsFolder to launch the packaged Python.
"""

import os
import sys
import subprocess
import tempfile
import time


def get_package_info():
    """Get the sparse package info."""
    ps_script = '''
    $pkg = Get-AppxPackage -Name "PyWinAppSDK.AITest"
    if ($pkg) {
        $pkg.PackageFamilyName
    }
    '''
    result = subprocess.run(
        ["powershell", "-Command", ps_script],
        capture_output=True, text=True
    )
    pfn = result.stdout.strip()
    return pfn if pfn else None


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_launcher.py <script.py> [args...]")
        sys.exit(1)
    
    script = os.path.abspath(sys.argv[1])
    args = sys.argv[2:]
    
    pfn = get_package_info()
    if not pfn:
        print("❌ Package not registered. Run register_sparse_package.py register first.")
        sys.exit(1)
    
    app_id = f"{pfn}!PythonAITest"
    print(f"Package Family: {pfn}")
    print(f"App ID: {app_id}")
    
    # Write config file with the script and arguments
    config_file = os.path.join(tempfile.gettempdir(), "pywinappsdk_run_config.txt")
    cmd_line = f'"{script}"' + ''.join(f' "{a}"' for a in args)
    
    with open(config_file, 'w') as f:
        f.write(cmd_line)
    
    # Also write the entry point script path
    entry_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sparse-package", "entry_point.py")
    startup_file = os.path.join(tempfile.gettempdir(), "pywinappsdk_startup.py") 
    
    with open(startup_file, 'w') as f:
        f.write(f'exec(open(r"{entry_script}", encoding="utf-8").read())')
    
    print(f"\nConfig file: {config_file}")
    print(f"Command: {cmd_line}")
    print(f"Entry script: {entry_script}")
    
    # Set PYTHONSTARTUP to our entry script before launching
    # Unfortunately shell:AppsFolder doesn't let us set env vars
    
    # Alternative: Use protocol activation or just inform user
    print("\n" + "=" * 60)
    print("To run with package identity, execute in the launched Python:")
    print(f'  exec(open(r"{entry_script}", encoding="utf-8").read())')
    print("=" * 60)
    
    # Launch through explorer shell protocol
    shell_path = f"shell:AppsFolder\\{app_id}"
    print(f"\nLaunching: {shell_path}")
    
    # Start the packaged app
    os.startfile(shell_path)
    
    print("\n✅ App launched. Paste the exec command above in the Python window.")


if __name__ == "__main__":
    main()
