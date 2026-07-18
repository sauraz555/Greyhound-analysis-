@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ================================================
echo  Racing Form Extractor
echo ================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo ERROR: Python was not found on this computer.
        echo Install Python 3.9 or newer from https://www.python.org/downloads/
        echo and make sure "Add Python to PATH" is checked during setup.
        echo.
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)

echo Checking required packages...
%PYTHON% -m pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages. Check your internet connection.
    pause
    exit /b 1
)

if not exist "input" mkdir "input"
if not exist "output" mkdir "output"

echo.
echo Looking for PDFs in the "input" folder...
echo.

%PYTHON% scripts\process_folder.py input output
set RESULT=%errorlevel%

echo.
if %RESULT% neq 0 (
    echo One or more files failed - see the messages above for details.
) else (
    echo Done. Check the "output" folder for your Excel workbooks.
)
echo.
pause
