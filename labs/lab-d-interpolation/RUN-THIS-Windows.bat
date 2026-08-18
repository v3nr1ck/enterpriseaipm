@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Lab D - The interpolation walk

echo ============================================================
echo   Lab D - The interpolation walk
echo ============================================================
echo.
echo   Reuses Lab C's setup if you have already run Lab C.
echo.

REM Lab D uses exactly what Lab C uses. If Lab C is already set up, borrow it
REM rather than downloading another 4GB.
if exist "..\lab-c-denoising\.venv\Scripts\python.exe" (
  echo   Found Lab C's setup - reusing it, no download needed.
  "..\lab-c-denoising\.venv\Scripts\python.exe" interpolate.py
  goto END
)

set PY=
where py >nul 2>&1 && set PY=py
if "!PY!"=="" where python >nul 2>&1 && set PY=python
if "!PY!"=="" goto NOPYTHON

if not exist ".venv\Scripts\python.exe" (
  echo   First run - building this lab's own private Python setup...
  !PY! -m venv .venv
  if errorlevel 1 goto VENVFAIL
)

echo   Checking this lab has what it needs...
".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
if errorlevel 1 goto PIPFAIL

echo.
echo ------------------------------------------------------------
echo.
".venv\Scripts\python.exe" interpolate.py
goto END

:VENVFAIL
echo.
echo   Could not create the Python environment.
echo   Most often this means Python was installed without the
echo   "Add Python to PATH" box ticked. Reinstall from
echo   https://www.python.org/downloads/ with that box ticked.
echo.
goto END

:PIPFAIL
echo.
echo   The download failed part way through.
echo.
echo   Usually this is the network, or a company firewall blocking it.
echo   Try again - it picks up where it left off. If you are on a work
echo   laptop behind a proxy, use the Colab notebook instead
echo   (colab.ipynb) which needs nothing installed.
echo.
goto END

:NOPYTHON
echo.
echo   Python is not installed on this computer.
echo.
echo   1. Go to    https://www.python.org/downloads/
echo   2. Click the big yellow "Download Python" button, run the installer.
echo   3. IMPORTANT: on the very first installer screen, tick the box that
echo      says "Add Python to PATH". It is easy to miss and nothing works
echo      without it.
echo   4. Restart this computer, then double-click this file again.
echo.
goto END


:END
echo.
echo ============================================================
echo   Finished. Press any key to close this window.
echo ============================================================
pause >nul
