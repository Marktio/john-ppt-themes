@echo off
rem Rebuilds manifest.json from the zips in this folder. Double-click it.
rem Safe with spaces/parentheses in the path. Needs Python (installs it for you if missing).
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py") else (
  where python >nul 2>nul
  if %errorlevel%==0 (set "PY=python") else (
    echo Python was not found. Installing it with winget...
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
    echo.
    echo Python installed. Close this window and double-click this file again.
    pause
    exit /b 1
  )
)

"%PY%" "%~dp0build_manifest.py" %*
if errorlevel 1 (
  echo.
  echo Something is wrong with one of the zips - see the message above.
  pause
  exit /b 1
)
echo.
echo Next: commit and push to GitHub (GitHub Desktop or: git add -A ^& git commit -m "update templates" ^& git push)
pause
