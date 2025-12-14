@echo off
echo ================================================================================
echo Docker Local Testing
echo ================================================================================
echo.
echo This will build and test your Docker container locally
echo Make sure Docker Desktop is running!
echo.
echo NOTE: First build takes 5-10 minutes (downloading Chrome)
echo.
pause

echo.
echo Step 1: Building Docker image (this may take several minutes)...
echo ================================================================================
docker build --progress=plain -t news-api-test .

if errorlevel 1 (
    echo.
    echo ❌ Docker build failed!
    echo Make sure Docker Desktop is running
    pause
    exit /b 1
)

echo.
echo ✅ Docker image built successfully!
echo.
echo Step 2: Starting container...
echo ================================================================================
docker run -d -p 8000:8000 --name news-api-test news-api-test

if errorlevel 1 (
    echo.
    echo ❌ Failed to start container!
    pause
    exit /b 1
)

echo.
echo ✅ Container started!
echo.
echo Waiting for API to be ready...
timeout /t 10 /nobreak > nul

echo.
echo Step 3: Testing health endpoint...
echo ================================================================================
curl http://localhost:8000/health

echo.
echo.
echo ================================================================================
echo ✅ Docker container is running!
echo ================================================================================
echo.
echo Your API is available at: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.
echo To view logs: docker logs news-api-test
echo To stop: docker stop news-api-test
echo To remove: docker rm news-api-test
echo.
echo Press any key to view logs (Ctrl+C to exit logs)...
pause > nul

docker logs -f news-api-test

