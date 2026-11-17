@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: PixelPress - Dual Build Pipeline (Desktop Builder)
:: Builds:
::   [1] Portable Standalone EXE (Single-file)
::   [2] High-Performance Directory Bundle + Inno Setup Installer
::   [3] Both Targets
:: ============================================================

title PixelPress Desktop Builder
color 0B

echo.
echo  ==============================================================
echo   PixelPress Desktop - Professional Builder
echo  ==============================================================
echo.

:: ─── Check Python ───────────────────────────────────────────────────────────
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo        Found: %PYVER%

:: ─── Virtual Environment ──────────────────────────────────────────────────
echo.
echo [2/6] Verifying virtual environment...
if not exist "venv\" (
    echo        Creating new venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo        Virtual environment active.

:: ─── Dependencies ─────────────────────────────────────────────────────────
echo.
echo [3/6] Verifying build dependencies (pywebview, pillow, pyinstaller)...
pip install -r requirements-desktop.txt --quiet
if errorlevel 1 (
    echo [ERROR] Dependency check failed. Please check internet connection.
    pause
    exit /b 1
)
echo        All dependencies up to date.

:: ─── Version Info Generation ──────────────────────────────────────────────
echo.
echo [4/6] Generating Windows version metadata...
python -c "
content = '''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 1, 0, 0),
    prodvers=(2, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(u\"040904B0\", [
        StringStruct(u\"CompanyName\",      u\"Aman Vishwakarma\"),
        StringStruct(u\"FileDescription\",  u\"PixelPress - Professional Image Compressor\"),
        StringStruct(u\"FileVersion\",      u\"2.1.0\"),
        StringStruct(u\"InternalName\",     u\"PixelPress\"),
        StringStruct(u\"LegalCopyright\",   u\"Copyright 2026 Aman Vishwakarma\"),
        StringStruct(u\"OriginalFilename\", u\"PixelPress.exe\"),
        StringStruct(u\"ProductName\",      u\"PixelPress Desktop Pro\"),
        StringStruct(u\"ProductVersion\",   u\"2.1.0\"),
      ])
    ]),
    VarFileInfo([VarStruct(u\"Translation\", [1033, 1200])])
  ]
)'''
with open('version_info.txt', 'w') as f:
    f.write(content)
"
echo        Version metadata ready.

:: ─── Selection Menu ────────────────────────────────────────────────────────
echo.
echo  --------------------------------------------------------------
echo   Select Build Target:
echo  --------------------------------------------------------------
echo   [1] Portable Standalone EXE (Single-file PixelPress-Portable.exe)
echo   [2] Fast Directory Bundle + Inno Setup Installer
echo   [3] Build Both (Portable + Installer)
echo   [4] Exit
echo.

set /p TARGET="Choose option (1-4) [default=3]: "
if "%TARGET%"=="" set TARGET=3
if "%TARGET%"=="4" exit /b 0

:: Clean previous build artifacts
echo.
echo [5/6] Preparing clean build directories...
if not exist "dist\" mkdir dist

:: ─── Execute PyInstaller Build ─────────────────────────────────────────────
echo.
echo [6/6] Compiling with PyInstaller...

if "%TARGET%"=="1" goto BUILD_PORTABLE
if "%TARGET%"=="2" goto BUILD_ONEDIR
if "%TARGET%"=="3" goto BUILD_BOTH

:BUILD_PORTABLE
echo.
echo  ==^> Compiling Single-File Portable Executable...
pyinstaller PixelPress-Portable.spec --noconfirm --clean
if errorlevel 1 goto BUILD_ERROR
goto POST_BUILD

:BUILD_ONEDIR
echo.
echo  ==^> Compiling Fast Directory Bundle...
pyinstaller PixelPress.spec --noconfirm --clean
if errorlevel 1 goto BUILD_ERROR
goto RUN_INNO

:BUILD_BOTH
echo.
echo  ==^> Step A: Compiling Single-File Portable Executable...
pyinstaller PixelPress-Portable.spec --noconfirm --clean
if errorlevel 1 goto BUILD_ERROR

echo.
echo  ==^> Step B: Compiling Fast Directory Bundle...
pyinstaller PixelPress.spec --noconfirm --clean
if errorlevel 1 goto BUILD_ERROR
goto RUN_INNO

:RUN_INNO
:: Check for Inno Setup compiler across standard and user-level paths
set INNO=""
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set INNO="%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set INNO="C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set INNO="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not %INNO%=="" (
    echo.
    echo  Inno Setup detected: %INNO%
    echo  Building installer setup...
    %INNO% installer.iss
    if not errorlevel 1 (
        echo  [OK] Installer built: dist\PixelPress_Setup.exe
    ) else (
        echo  [WARN] Inno Setup compilation encountered a warning.
    )
) else (
    echo.
    echo  [INFO] Inno Setup 6 compiler not detected.
    echo         Directory bundle is ready in dist\PixelPress\
    echo         To build PixelPress_Setup.exe, install Inno Setup 6.
)

:POST_BUILD
echo.
echo  ==============================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo  ==============================================================
if exist "dist\PixelPress-Portable.exe" (
    echo   Portable EXE:  dist\PixelPress-Portable.exe
)
if exist "dist\PixelPress\PixelPress.exe" (
    echo   Installed App: dist\PixelPress\PixelPress.exe
)
if exist "dist\PixelPress_Setup.exe" (
    echo   Installer:     dist\PixelPress_Setup.exe
)
echo  ==============================================================
echo.
pause
exit /b 0

:BUILD_ERROR
echo.
echo  [ERROR] Build compilation failed. Please inspect logs above.
pause
exit /b 1
