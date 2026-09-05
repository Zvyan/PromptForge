@echo off
title PromptForge Web Launcher
cd /d "%~dp0"

echo ======================================================================
echo    PromptForge - Multi-Platform Agent Prompt Framework
echo ======================================================================
echo.

set "PYTHON_CMD="

:: 1. Check if 'python' is available
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto found_python
)

:: 2. Check if 'py' launcher is available
where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto found_python
)

:: 3. Check known local installation path
if exist "D:\Python\python.exe" (
    set "PYTHON_CMD=D:\Python\python.exe"
    goto found_python
)

:: 4. Check AppData local python installations
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto found_python
    )
)

:: 5. Check Program Files python installations
for /d %%D in ("%ProgramFiles%\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto found_python
    )
)

:found_python
if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python 3 not found in PATH or standard installation directories.
    echo Please install Python 3.10+ from https://www.python.org and ensure
    echo 'Add python.exe to PATH' is checked during installation.
    echo.
    pause
    exit /b 1
)

echo [*] Using Python: %PYTHON_CMD%
echo [*] Starting PromptForge Web UI on http://127.0.0.1:8000 ...
echo [*] The browser will open automatically once ready.
echo.
echo Press Ctrl+C in this window to stop the server.
echo ----------------------------------------------------------------------
echo.

%PYTHON_CMD% run.py web

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PromptForge stopped with exit code: %errorlevel%
    pause
)
