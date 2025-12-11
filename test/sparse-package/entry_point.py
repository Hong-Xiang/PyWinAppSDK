"""
Entry point script for PyWinAppSDK AI Test.

This script can be run in two ways:
1. As a module: python -m entry_point <script.py> [args...]
2. Via exec(): exec(open(r"path/to/entry_point.py", encoding="utf-8").read())
"""

import os
import sys
import tempfile
import traceback

# Log file for debugging
LOG_FILE = os.path.join(tempfile.gettempdir(), "pywinappsdk_entry_point.log")


def log(msg):
    """Write to both stdout and log file."""
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def wait_for_exit(exit_code):
    """Always pause before exiting so user can see output."""
    print()
    print("=" * 60)
    print(f"Exit code: {exit_code}")
    print("=" * 60)
    try:
        input("Press Enter to exit...")
    except:
        pass
    return exit_code


def run_from_args():
    """Run script passed as command line arguments."""
    print("=" * 60)
    print("PyWinAppSDK AI Test - Entry Point")
    print("=" * 60)
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print(f"sys.argv: {sys.argv}")
    print(f"Working dir: {os.getcwd()}")
    print()
    
    if len(sys.argv) < 2:
        print("No script provided in arguments.")
        print("Usage: python entry_point.py <script.py> [args...]")
        return 1
    
    script_path = sys.argv[1]
    script_args = sys.argv[2:]
    
    print(f"Script: {script_path}")
    print(f"Args: {script_args}")
    print()
    
    if not os.path.exists(script_path):
        print(f"ERROR: Script not found: {script_path}")
        return 1
    
    # Update sys.argv for the target script
    sys.argv = [script_path] + script_args
    
    # Add script directory to path
    script_dir = os.path.dirname(os.path.abspath(script_path))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Execute the script
    print("-" * 60)
    print(f"Executing: {script_path}")
    print("-" * 60)
    print()
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        exec(compile(code, script_path, 'exec'), {'__name__': '__main__', '__file__': script_path})
        return 0
    except SystemExit as e:
        # Allow sys.exit() to propagate
        return e.code if e.code is not None else 0
    except Exception as e:
        print(f"\nERROR: {e}")
        traceback.print_exc()
        return 1


def run_from_config():
    """Run script from config file (for exec() mode)."""
    config_file = os.path.join(tempfile.gettempdir(), "pywinappsdk_run_config.txt")
    
    print("=" * 60)
    print("PyWinAppSDK AI Test - Running with Package Identity")
    print("=" * 60)
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print(f"Config file: {config_file}")
    print()
    
    if not os.path.exists(config_file):
        print("No script configured. Use run_with_identity.py to set up a script.")
        return 1
    
    # Read the command from config
    with open(config_file, 'r', encoding='utf-8') as f:
        cmd_line = f.read().strip()
    
    # Delete config file
    os.remove(config_file)
    
    print(f"Command: {cmd_line}")
    print()
    
    # Parse the command line
    import shlex
    args = shlex.split(cmd_line)
    
    if not args:
        print("No script specified in config.")
        return 1
    
    script_path = args[0]
    script_args = args[1:]
    
    if not os.path.exists(script_path):
        print(f"ERROR: Script not found: {script_path}")
        return 1
    
    # Set up sys.argv for the script
    sys.argv = [script_path] + script_args
    
    # Add script directory to path
    script_dir = os.path.dirname(os.path.abspath(script_path))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Execute the script
    print(f"Running: {script_path}")
    print(f"Args: {script_args}")
    print("-" * 60)
    print()
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        exec(compile(code, script_path, 'exec'), {'__name__': '__main__', '__file__': script_path})
        return 0
    except SystemExit as e:
        return e.code if e.code is not None else 0
    except Exception as e:
        print(f"\nERROR: {e}")
        traceback.print_exc()
        return 1


def main():
    """Main entry point with top-level exception handling."""
    # Check if there's a config file (written by run_with_identity.py)
    config_file = os.path.join(tempfile.gettempdir(), "pywinappsdk_run_config.txt")
    
    if os.path.exists(config_file):
        # Config file exists - run from there (more reliable)
        return run_from_config()
    elif len(sys.argv) > 1:
        # Arguments provided - run from args
        return run_from_args()
    else:
        # No config, no args - show help
        print("=" * 60)
        print("PyWinAppSDK AI Test - Entry Point")
        print("=" * 60)
        print(f"Python: {sys.executable}")
        print(f"Version: {sys.version}")
        print(f"sys.argv: {sys.argv}")
        print()
        print("No script configured.")
        print("Use run_with_identity.py to launch scripts with package identity.")
        return 1


# Top-level exception handler - ALWAYS pause before exit
if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception as e:
        print()
        print("=" * 60)
        print("FATAL ERROR in entry_point.py:")
        print("=" * 60)
        print(f"{e}")
        traceback.print_exc()
        exit_code = 1
    
    sys.exit(wait_for_exit(exit_code))
else:
    # Being exec()'d
    try:
        exit_code = run_from_config()
    except Exception as e:
        print()
        print("=" * 60)
        print("FATAL ERROR in entry_point.py:")
        print("=" * 60)
        print(f"{e}")
        traceback.print_exc()
        exit_code = 1
    
    wait_for_exit(exit_code)
