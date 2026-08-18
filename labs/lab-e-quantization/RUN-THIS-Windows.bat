@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Lab E - Watch it degrade

echo ============================================================
echo   Lab E - Watch it degrade
echo ============================================================
echo.
echo   Needs Ollama installed and running.
echo.

set PY=
where py >nul 2>&1 && set PY=py
if "!PY!"=="" where python >nul 2>&1 && set PY=python
if "!PY!"=="" goto NOPYTHON

where ollama >nul 2>&1
if errorlevel 1 goto NOOLLAMA

echo   Checking that Ollama is running...
curl -s -m 5 http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 goto NOTRUNNING

echo.
echo   This lab needs three versions of the same model downloaded first.
echo   That is about 16GB and is NOT automatic - see README.md.
echo.
!PY! compare_quants.py --tags llama3.1:8b-instruct-q8_0 llama3.1:8b-instruct-q4_K_M llama3.1:8b-instruct-q2_K
goto END

:NOOLLAMA
echo.
echo   Ollama is not installed. This lab needs it.
echo.
echo   1. Go to  https://ollama.com/download
echo   2. Install it, then open it once so it starts running.
echo   3. Double-click this file again.
echo.
goto END

:NOTRUNNING
echo.
echo   Ollama is installed but not running.
echo   Open the Ollama app from your Start menu, then run this again.
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
