@echo off
REM Deploy Voice Inventory Manager to GitHub
REM This script will push the new project to GitHub

echo ============================================================
echo  Deploying Voice Inventory Manager to GitHub
echo ============================================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
)

REM Add remote if not exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Adding remote repository...
    git remote add origin https://github.com/vyassoham/voice-inventory-manager.git
    echo.
)

REM Show current status
echo Current Git Status:
git status
echo.

REM Prompt user to continue
echo.
echo WARNING: This will replace all content in the GitHub repository!
echo Press Ctrl+C to cancel, or
pause

REM Add all files
echo.
echo Adding all files...
git add .
echo.

REM Commit
echo Creating commit...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Complete Voice Inventory Manager v1.0.0 - Production Ready

git commit -m "%commit_msg%"
echo.

REM Push to GitHub (force push to replace everything)
echo.
echo Pushing to GitHub...
echo This will REPLACE all existing content in the repository.
echo.
pause

git push -f origin main
if errorlevel 1 (
    echo.
    echo Push failed. Trying 'master' branch...
    git push -f origin master
)

echo.
echo ============================================================
echo  Deployment Complete!
echo ============================================================
echo.
echo Your repository has been updated at:
echo https://github.com/vyassoham/voice-inventory-manager
echo.
pause
