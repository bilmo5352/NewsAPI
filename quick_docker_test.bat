@echo off
echo Quick Docker Test (No Build - Just Run)
echo ========================================
echo.

REM Check if image exists
docker images news-api-test -q > nul 2>&1
if errorlevel 1 (
    echo Image not found! Building first...
    docker build -t news-api-test .
    if errorlevel 1 (
        echo Build failed!
        pause
        exit /b 1
    )
)

echo Starting container...
docker run -d -p 8000:8000 --name news-api-test news-api-test

if errorlevel 1 (
    echo Failed to start! Cleaning up old container...
    docker rm news-api-test 2>nul
    docker run -d -p 8000:8000 --name news-api-test news-api-test
)

echo.
echo Waiting for API to start...
timeout /t 5 /nobreak > nul

echo.
echo Testing health endpoint...
curl http://localhost:8000/health

echo.
echo.
echo API is running at: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.
echo To stop: docker stop news-api-test
echo To view logs: docker logs -f news-api-test
echo.
pause

