# 🐳 Docker Build Fix Guide

## Problem

The Docker build was failing with:
```
/bin/sh: 1: apt-key: not found
```

This is because `apt-key` is deprecated in Debian Trixie (testing).

## ✅ Solution Applied

Updated the Dockerfile to use the modern GPG key management approach:

### Old Method (Deprecated)
```dockerfile
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
```

### New Method (Current)
```dockerfile
mkdir -p /etc/apt/keyrings
wget -q -O /etc/apt/keyrings/google-chrome.gpg https://dl-ssl.google.com/linux/linux_signing_key.pub
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] ..." > /etc/apt/sources.list.d/google-chrome.list
```

## 🧪 Test the Fix

### Option 1: Test Locally (Recommended)

```bash
# Build the image
docker build -t news-api-test .

# If successful, run it
docker run -p 8000:8000 news-api-test
```

### Option 2: Use Test Script (Windows)

```bash
# This will build and test automatically
test_docker.bat
```

### Option 3: Quick Test

```bash
# Just build without running
docker build --no-cache -t news-api-test .
```

## 🚀 Deploy to Railway

Once Docker builds successfully locally:

1. **Commit Changes**
   ```bash
   git add Dockerfile
   git commit -m "Fix: Update Chrome installation for Debian Trixie"
   git push origin main
   ```

2. **Railway Auto-Rebuild**
   - Railway will automatically detect the push
   - It will rebuild with the fixed Dockerfile
   - Check the build logs in Railway dashboard

## 🔍 Verify Build Success

### Local Verification

After successful build:
```bash
# Check image exists
docker images | grep news-api-test

# Run container
docker run -d -p 8000:8000 --name test-api news-api-test

# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"..."}

# Clean up
docker stop test-api
docker rm test-api
```

### Railway Verification

1. **Check Build Logs**
   - Go to Railway dashboard
   - Click on your project
   - Click "Deployments"
   - View latest build logs
   - Look for: "Successfully built..."

2. **Test Deployed API**
   ```bash
   curl https://YOUR_APP.railway.app/health
   ```

## 📋 Troubleshooting

### Build Still Fails

**If you still see errors:**

1. **Clear Docker cache**
   ```bash
   docker system prune -a
   docker build --no-cache -t news-api-test .
   ```

2. **Try alternative base image**
   ```bash
   # Use Python 3.10 bullseye (older Debian)
   # Edit Dockerfile first line to:
   FROM python:3.10-bullseye
   ```

3. **Check Docker version**
   ```bash
   docker --version
   # Should be >= 20.10
   ```

### Railway Build Timeout

If Railway build times out:
- This is normal for first build (~5-10 minutes)
- Chrome installation takes time
- Wait for completion
- Check logs for actual errors

### Runtime Errors

If build succeeds but app crashes:

1. **Check Railway logs**
   ```bash
   # Look for errors like:
   # - ChromeDriver not found
   # - Memory errors
   # - Permission errors
   ```

2. **Memory Issues**
   - Free tier: 512 MB RAM
   - May need Pro tier (2 GB) for reliable scraping
   - Consider running scrapers sequentially

## 🎯 Quick Fix Commands

### Rebuild Everything
```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove images
docker rmi $(docker images -q)

# Rebuild
docker build -t news-api-test .
```

### Test Without Railway
```bash
# Build
docker build -t news-api-test .

# Run with logs
docker run -p 8000:8000 news-api-test

# In another terminal, test
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

## ✅ Expected Output

### Successful Build
```
...
[+] Building 250.3s (10/10) FINISHED
 => [1/6] FROM python:3.10-slim
 => [2/6] WORKDIR /app
 => [3/6] RUN apt-get update && apt-get install...
 => [4/6] COPY requirements.txt .
 => [5/6] RUN pip install --no-cache-dir...
 => [6/6] COPY . .
 => exporting to image
 => => writing image sha256:...
 => => naming to docker.io/library/news-api-test
```

### Successful Run
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Railway Docs](https://docs.railway.app/)
- [Debian GPG Key Management](https://wiki.debian.org/DebianRepository/UseThirdParty)

## 🆘 Still Having Issues?

1. Check if Docker Desktop is running
2. Ensure you have sufficient disk space (>10 GB)
3. Try restarting Docker Desktop
4. Check Railway status page
5. Review detailed error messages in logs

---

**Need more help?** Check `RAILWAY_DEPLOYMENT.md` for detailed deployment guide.

