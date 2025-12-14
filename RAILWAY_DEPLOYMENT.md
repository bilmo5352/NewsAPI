# 🚂 Railway Deployment Guide

Complete guide to deploy the News Aggregator API to Railway.

## Prerequisites

- A [Railway](https://railway.app/) account (free tier available)
- Git installed on your computer
- GitHub account (for connecting to Railway)

## 📋 Deployment Steps

### Step 1: Prepare Your Repository

1. **Initialize Git (if not already done)**
```bash
git init
git add .
git commit -m "Initial commit - News Aggregator API"
```

2. **Create GitHub Repository**
   - Go to [GitHub](https://github.com/new)
   - Create a new repository (e.g., `news-aggregator-api`)
   - Don't initialize with README (we already have files)

3. **Push to GitHub**
```bash
git remote add origin https://github.com/YOUR_USERNAME/news-aggregator-api.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway

#### Option A: Deploy via GitHub (Recommended)

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app/)
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your repositories
   - Select your `news-aggregator-api` repository

3. **Configure Deployment**
   - Railway will auto-detect the `Dockerfile`
   - It will automatically start building and deploying
   - Wait for the build to complete (~5-10 minutes first time)

4. **Generate Domain**
   - Go to your project settings
   - Click "Generate Domain" under the service
   - Copy the generated URL (e.g., `https://news-aggregator-api-production.up.railway.app`)

#### Option B: Deploy via Railway CLI

1. **Install Railway CLI**
```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh
```

2. **Login and Deploy**
```bash
railway login
railway init
railway up
```

3. **Generate Domain**
```bash
railway domain
```

### Step 3: Verify Deployment

1. **Check Health**
```bash
curl https://YOUR_APP.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-14T20:30:00.123456"
}
```

2. **View Documentation**
Visit: `https://YOUR_APP.railway.app/docs`

3. **Test the API**
```bash
python test_railway_api.py
```
Enter your Railway URL when prompted.

## 🔧 Configuration

### Environment Variables (Optional)

If needed, add environment variables in Railway:

1. Go to your project in Railway
2. Click on "Variables"
3. Add variables:
   - `PORT` (Railway sets this automatically)
   - `LOG_LEVEL` = `INFO`
   - Any custom settings

### Resource Limits

**Free Tier Limits:**
- 500 hours of execution time per month
- 512 MB RAM
- 1 GB Disk
- Shared CPU

**Note**: Scrapers are resource-intensive. Consider:
- Upgrading to Pro tier ($5/month) for better performance
- The free tier should work but may be slower

## 📊 Monitoring

### View Logs

**Via Railway Dashboard:**
1. Go to your project
2. Click "Deployments"
3. Click on the latest deployment
4. View real-time logs

**Via CLI:**
```bash
railway logs
```

### Check Metrics

In Railway dashboard:
- CPU usage
- Memory usage
- Network traffic
- Response times

## 🔍 Troubleshooting

### Build Fails

**Issue**: Docker build fails  
**Solution**:
```bash
# Test build locally first
docker build -t news-api .
docker run -p 8000:8000 news-api
```

### ChromeDriver Issues

**Issue**: Scraper fails with ChromeDriver errors  
**Solution**: The Dockerfile includes Chrome installation. If issues persist:
- Check Railway logs for specific errors
- May need to increase memory allocation (upgrade tier)

### Timeout Issues

**Issue**: API times out during scraping  
**Solution**:
1. Railway has a 10-minute request timeout on free tier
2. Both scrapers should complete within ~4 minutes
3. If timeouts persist, check logs for memory issues

### Memory Issues

**Issue**: Out of memory errors  
**Solution**:
- Free tier has 512 MB RAM
- Running both scrapers in parallel may exceed this
- Consider:
  - Upgrading to Pro tier (2 GB RAM)
  - Running scrapers sequentially instead of parallel
  - Using separate services for each scraper

## 🚀 API Endpoints

Once deployed, your API will have these endpoints:

| Endpoint | Method | Description | Time |
|----------|--------|-------------|------|
| `/` | GET | API information | < 1s |
| `/health` | GET | Health check | < 1s |
| `/docs` | GET | Interactive documentation | < 1s |
| `/scrape` | GET | Scrape both sources | ~4 min |
| `/scrape/groww` | GET | Scrape Groww only | ~4 min |
| `/scrape/pulse` | GET | Scrape Pulse only | ~1 min |

## 📱 Using the Deployed API

### From Python

```python
import requests

API_URL = "https://YOUR_APP.railway.app"

# Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# Scrape news (wait ~4 minutes)
response = requests.get(f"{API_URL}/scrape", timeout=300)
data = response.json()
print(f"Total items: {data['summary']['total_items']}")
```

### From JavaScript

```javascript
const API_URL = 'https://YOUR_APP.railway.app';

// Health check
fetch(`${API_URL}/health`)
  .then(response => response.json())
  .then(data => console.log(data));

// Scrape news
fetch(`${API_URL}/scrape`)
  .then(response => response.json())
  .then(data => {
    console.log('Total items:', data.summary.total_items);
    console.log('Groww:', data.sources.groww.data.news_items);
    console.log('Pulse:', data.sources.pulse.data.articles);
  });
```

### From cURL

```bash
# Health check
curl https://YOUR_APP.railway.app/health

# Scrape all sources
curl https://YOUR_APP.railway.app/scrape
```

## 💰 Cost Estimation

### Free Tier
- **Cost**: $0
- **Limits**: 500 hours/month, 512 MB RAM
- **Best for**: Testing, low traffic

### Pro Tier ($5/month)
- **Cost**: $5/month + usage
- **Resources**: 2 GB RAM, better CPU
- **Best for**: Production use

**Estimated monthly cost for production**:
- Base: $5/month
- Usage: ~$0-5 depending on traffic
- **Total**: $5-10/month

## 🔄 Updates and Redeployment

### Automatic Deployments

Railway automatically redeploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update: Added new feature"
git push origin main

# Railway will automatically rebuild and redeploy
```

### Manual Redeployment

Via Railway Dashboard:
1. Go to your project
2. Click "Deployments"
3. Click "Redeploy" on any deployment

Via CLI:
```bash
railway up
```

## 📝 Best Practices

1. **Use Environment Variables**
   - Store sensitive data in Railway Variables
   - Never commit secrets to GitHub

2. **Monitor Logs**
   - Check logs regularly for errors
   - Set up alerts in Railway for failures

3. **Test Before Deploying**
   - Test locally with Docker first
   - Use `test_railway_api.py` after deployment

4. **Version Control**
   - Tag releases: `git tag v1.0.0`
   - Use branches for development

5. **Scale Gradually**
   - Start with free tier
   - Upgrade when needed based on usage

## 🆘 Support

### Railway Support
- [Railway Docs](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Railway Twitter](https://twitter.com/Railway)

### Application Issues
- Check Railway logs first
- Test locally with Docker
- Review error messages in detail

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Selenium Docker Guide](https://www.selenium.dev/documentation/grid/components/docker/)

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] GitHub repo connected to Railway
- [ ] Build completed successfully
- [ ] Domain generated
- [ ] Health check passes
- [ ] Documentation accessible at `/docs`
- [ ] Test scraping endpoint
- [ ] Logs showing no errors
- [ ] Save Railway URL for future use

## 🎉 Success!

Once deployed, your API will be accessible at:
```
https://YOUR_APP.railway.app
```

Share this URL with your team or integrate it into your applications!

---

**Need help?** Open an issue on GitHub or check Railway documentation.

