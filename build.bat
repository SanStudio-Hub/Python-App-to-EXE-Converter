@echo off
:: ╔══════════════════════════════════════════════════════════════════╗
:: ║           PythonEXEBuilder - Build Automation Script             ║
:: ║                  Developed By SANTHOSH A                         ║
:: ╚══════════════════════════════════════════════════════════════════╝

title PythonEXEBuilder - Developed By SANTHOSH A
color 0B

echo.
echo  ╔══════════════════════════════════════════════════════════════════╗
echo  ║           PythonEXEBuilder  v1.0.0                              ║
echo  ║                  Developed By SANTHOSH A                        ║
echo  ║          Python --^> Windows .exe  Packaging Tool               ║
echo  ╚══════════════════════════════════════════════════════════════════╝
echo.

:: ─────────────────────────────────────────────
::  1. Check Python is available
:: ─────────────────────────────────────────────
echo  [1/5]  Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR]  Python is not installed or not in PATH.
    echo           Please install Python 3.7+ from https://python.org
    echo           and make sure to check "Add Python to PATH".
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [OK]     %%v

:: ─────────────────────────────────────────────
::  2. Verify input/ folder has a .py file
:: ─────────────────────────────────────────────
echo.
echo  [2/5]  Checking input folder for Python source file...

if not exist "%~dp0input\" (
    mkdir "%~dp0input"
    echo  [WARN]   input/ folder was missing – created.
)

set "PY_FOUND=0"
for %%f in ("%~dp0input\*.py") do set "PY_FOUND=1"

if "%PY_FOUND%"=="0" (
    echo.
    echo  [ERROR]  No .py file found in the input/ folder!
    echo           Place your Python script inside the input/ folder and run again.
    echo.
    pause
    exit /b 1
)

for %%f in ("%~dp0input\*.py") do echo  [OK]     Source: %%~nxf

:: ─────────────────────────────────────────────
::  3. Ensure output/ folder exists
:: ─────────────────────────────────────────────
echo.
echo  [3/5]  Preparing output folder...
if not exist "%~dp0output\" mkdir "%~dp0output"
echo  [OK]     output/ folder ready

:: ─────────────────────────────────────────────
::  4. Install colorama for prettier output (optional)
:: ─────────────────────────────────────────────
echo.
echo  [4/5]  Installing build dependencies...
python -m pip install colorama --quiet --disable-pip-version-check
echo  [OK]     Dependencies ready

:: ─────────────────────────────────────────────
::  5. Run the builder
:: ─────────────────────────────────────────────
echo.
echo  [5/5]  Starting build process...
echo.
echo  ─────────────────────────────────────────────────────────────────
echo.

python "%~dp0builder.py"
set BUILD_RESULT=%ERRORLEVEL%

echo.
echo  ─────────────────────────────────────────────────────────────────
echo.

:: ─────────────────────────────────────────────
::  Result
:: ─────────────────────────────────────────────
if %BUILD_RESULT% EQU 0 (
    echo  [SUCCESS]  Build completed!
    echo             Your .exe is in the output/ folder.
    echo.
    echo             Opening output folder...
    explorer "%~dp0output"
) else (
    echo  [FAILED]   Build encountered errors.
    echo             Check the logs/ folder for detailed error information.
    echo.
)

echo.
echo  ══════════════════════════════════════════════════════════════════
echo    Developed By SANTHOSH A  ^|  PythonEXEBuilder v1.0.0
echo  ══════════════════════════════════════════════════════════════════
echo.
pause
exit /b %BUILD_RESULT%
