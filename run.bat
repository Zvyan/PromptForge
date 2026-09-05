@echo off
title PromptForge Interactive Console
cd /d "%~dp0"

set "PYTHON_CMD="

where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto found_python
)

where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto found_python
)

if exist "D:\Python\python.exe" (
    set "PYTHON_CMD=D:\Python\python.exe"
    goto found_python
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto found_python
    )
)

:found_python
if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python 3 not found in PATH.
    pause
    exit /b 1
)

%PYTHON_CMD% run.py %*

if %errorlevel% neq 0 (
    pause
)
