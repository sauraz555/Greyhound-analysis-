@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ================================================
echo  Racing Form Extractor - PDF downloader
echo ================================================
echo.
echo This opens a real browser window. YOU log in and solve any
echo "Verify you are human" check yourself - this script does not
echo and will not do that step for you.
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo ERROR: Python was not found. Install it from https://www.python.org/downloads/
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

echo Checking Playwright browser (first run only, this can take a minute)...
%PYTHON% -m playwright install chromium

if not exist "scripts\meetings.txt" (
    echo.
    echo No scripts\meetings.txt found - copying the example template.
    echo Edit scripts\meetings.txt to list the meetings you want, then run this again.
    copy "scripts\meetings.example.txt" "scripts\meetings.txt" >nul
    notepad "scripts\meetings.txt"
    pause
    exit /b 0
)

%PYTHON% scripts\download_form_guides.py --list scripts\meetings.txt

echo.
echo Done. Downloaded PDFs are in the "input" folder.
echo Run run.bat next to turn them into spreadsheets.
echo.
pause
