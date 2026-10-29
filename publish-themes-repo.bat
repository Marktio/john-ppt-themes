@echo off
rem One click: creates (or updates) the PUBLIC GitHub repo "john-ppt-themes" from this folder.
rem Needs: GitHub CLI (gh) signed in, and git. Safe to run again any time you add templates.
rem Safe with spaces and parentheses in the folder path.
setlocal
cd /d "%~dp0"
set "REPO=john-ppt-themes"

where gh >nul 2>nul
if errorlevel 1 goto no_gh
where git >nul 2>nul
if errorlevel 1 goto no_git

set "GHUSER="
for /f "delims=" %%U in ('gh api user --jq .login 2^>nul') do set "GHUSER=%%U"
if not defined GHUSER goto no_auth
echo Signed in to GitHub as %GHUSER%

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py"
if defined PY goto have_python
where python >nul 2>nul
if not errorlevel 1 set "PY=python"
if defined PY goto have_python
echo Python was not found. Installing it with winget...
winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
echo Python installed. Close this window and double-click this file again.
pause
exit /b 1

:have_python
echo.
echo === Rebuilding manifest.json ===
"%PY%" "%~dp0build_manifest.py" --owner %GHUSER%
if errorlevel 1 goto bad_zip

echo.
echo === Committing ===
if not exist ".git" git init -b main
git branch -M main
git add -A
git -c user.name="%GHUSER%" -c user.email="%GHUSER%@users.noreply.github.com" commit -m "Update templates"
rem (a "nothing to commit" message above is fine)

echo.
echo === Publishing ===
gh repo view "%GHUSER%/%REPO%" >nul 2>nul
if errorlevel 1 goto create_repo

git remote get-url origin >nul 2>nul
if errorlevel 1 git remote add origin "https://github.com/%GHUSER%/%REPO%.git"
git push -u origin main
if errorlevel 1 goto push_failed
goto done

:create_repo
gh repo create "%REPO%" --public --source=. --remote=origin --push
if errorlevel 1 goto push_failed

:done
echo.
echo Done. Your template list should be live at:
echo   https://cdn.jsdelivr.net/gh/%GHUSER%/%REPO%@main/manifest.json
echo (If it shows an old copy, open: https://purge.jsdelivr.net/gh/%GHUSER%/%REPO%@main/manifest.json )
start "" "https://cdn.jsdelivr.net/gh/%GHUSER%/%REPO%@main/manifest.json"
pause
exit /b 0

:no_gh
echo GitHub CLI (gh) was not found. Install it with:  winget install --id GitHub.cli -e
echo Then run:  gh auth login   and double-click this file again.
pause
exit /b 1

:no_git
echo git was not found. Install it with:  winget install --id Git.Git -e
echo Then close this window and double-click this file again.
pause
exit /b 1

:no_auth
echo You are not signed in to GitHub. Run:  gh auth login   then double-click this file again.
pause
exit /b 1

:bad_zip
echo.
echo One of the template zips is invalid - see the message above. Nothing was published.
pause
exit /b 1

:push_failed
echo.
echo Publishing failed - see the message above.
pause
exit /b 1
