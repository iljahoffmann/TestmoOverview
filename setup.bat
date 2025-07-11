@echo off
REM TestmoOverview Setup Script

REM Create virtual environment in .venv
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Could not create virtual environment.
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Could not activate virtual environment.
    exit /b 1
)

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Could not install required packages.
    exit /b 1
)


REM Build executable using pyinstaller
pyinstaller --onefile --testmo_overview.py
if errorlevel 1 (
    echo [ERROR] Could not build executable.
    exit /b 1
)

.\testmo_overview.exe

echo.
