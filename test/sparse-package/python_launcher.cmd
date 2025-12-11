@echo off
REM Wrapper script for launching Python AI tests with package identity
REM This script is the entry point for the sparse package

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Python interpreter (ARM64 venv)
set "PYTHON_EXE=C:\Users\leilzh\Documents\work\PyWinAppSDK\.venv-arm64\Scripts\python.exe"

echo ============================================================
echo PyWinAppSDK AI Test - Package Identity Launcher
echo ============================================================
echo Python: %PYTHON_EXE%
echo Arguments: %*
echo.

REM If arguments were passed directly (via IApplicationActivationManager)
if not "%~1"=="" (
    echo Running script from command line arguments...
    echo Script: %*
    echo.
    
    "%PYTHON_EXE%" %*
    
    set "EXIT_CODE=!ERRORLEVEL!"
    echo.
    echo ============================================================
    echo Exit code: !EXIT_CODE!
    echo ============================================================
    pause
    exit /b !EXIT_CODE!
)

REM Check for config file with script to run
set "CONFIG_FILE=%TEMP%\pywinappsdk_run_config.txt"

if exist "%CONFIG_FILE%" (
    REM Read the script path and args from config
    set /p SCRIPT_PATH=<"%CONFIG_FILE%"
    
    echo ============================================================
    echo PyWinAppSDK AI Test - Running with Package Identity
    echo ============================================================
    echo Python: %PYTHON_EXE%
    echo Script: !SCRIPT_PATH!
    echo.
    
    REM Run the script
    "%PYTHON_EXE%" !SCRIPT_PATH!
    
    set "EXIT_CODE=!ERRORLEVEL!"
    echo.
    echo ============================================================
    echo Exit code: !EXIT_CODE!
    echo ============================================================
    
    REM Delete the config file after use
    del "%CONFIG_FILE%" 2>nul
    
    pause
    exit /b !EXIT_CODE!
) else (
    echo ============================================================
    echo PyWinAppSDK AI Test Launcher
    echo ============================================================
    echo.
    echo This is a packaged Python environment for testing Windows AI APIs.
    echo.
    echo To run a script, use the simple_launcher.py helper:
    echo   python simple_launcher.py your_script.py [args...]
    echo.
    pause
    exit /b 0
)
