@echo off
echo Stopping and removing Docker container...
docker stop news-api-test 2>nul
docker rm news-api-test 2>nul
docker rmi news-api-test 2>nul
echo Done!
pause

