@echo off
echo ================================================================================
echo Git Deployment Helper
echo ================================================================================
echo.
echo This script will help you push your code to GitHub
echo Make sure you've created a GitHub repository first!
echo.
pause
echo.

echo Step 1: Initializing Git (if not already done)...
git init
echo.

echo Step 2: Adding all files...
git add .
echo.

echo Step 3: Creating commit...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Deploy News Aggregator API

git commit -m "%commit_msg%"
echo.

echo Step 4: Setting up remote repository...
set /p repo_url="Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): "

git remote remove origin 2>nul
git remote add origin %repo_url%
echo.

echo Step 5: Pushing to GitHub...
git branch -M main
git push -u origin main
echo.

echo ================================================================================
echo ✅ Code pushed to GitHub successfully!
echo ================================================================================
echo.
echo Next steps:
echo 1. Go to https://railway.app/
echo 2. Click "New Project"
echo 3. Select "Deploy from GitHub repo"
echo 4. Choose your repository
echo 5. Railway will automatically detect Dockerfile and deploy
echo.
echo After deployment:
echo 1. Generate a domain in Railway settings
echo 2. Test with: python test_railway_api.py
echo.
pause

