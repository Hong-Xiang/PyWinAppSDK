"""
PyWinAppSDK AI Test Entry Point

This script is automatically run when Python is launched with package identity.
It reads the config file to determine which script to run.
"""

import os
import sys
import tempfile


def main():
    config_file = os.path.join(tempfile.gettempdir(), "pywinappsdk_run_config.txt")
    
    if os.path.exists(config_file):
        # Read the command from config
        with open(config_file, 'r') as f:
            cmd_line = f.read().strip()
        
        # Delete config file
        os.remove(config_file)
        
        print("=" * 60)
        print("PyWinAppSDK AI Test - Running with Package Identity")
        print("=" * 60)
        print(f"Command: {cmd_line}")
        print()
        
        # Parse the command line and run
        import shlex
        args = shlex.split(cmd_line)
        
        if args:
            script_path = args[0]
            script_args = args[1:]
            
            # Set up sys.argv for the script
            sys.argv = [script_path] + script_args
            
            # Add script directory to path
            script_dir = os.path.dirname(os.path.abspath(script_path))
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            
            # Execute the script
            with open(script_path, 'r') as f:
                code = f.read()
            
            exec(compile(code, script_path, 'exec'), {'__name__': '__main__', '__file__': script_path})
    else:
        print("=" * 60)
        print("PyWinAppSDK AI Test Launcher")
        print("=" * 60)
        print()
        print("This Python environment has package identity for Windows AI APIs.")
        print()
        print("To run a script with package identity, use:")
        print("  python simple_launcher.py your_script.py [args...]")
        print()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
