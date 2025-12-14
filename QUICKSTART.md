# 🚀 Quick Start Guide

Get your News Aggregator API deployed to Railway in 5 minutes!

## ⚡ Super Fast Deployment

### 1. Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### 2. Test Locally (Optional - 1 minute)

```bash
# Start the API
python news_api.py

# In another terminal, test it
python test_api.py
```

### 3. Push to GitHub (2 minutes)

**Option A: Use Helper Script (Windows)**
```bash
deploy_to_github.bat
```
Follow the prompts!

**Option B: Manual Commands**
```bash
# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Deploy News Aggregator API"

# Add your GitHub repo (create it first at github.com/new)
git remote add origin https://github.com/YOUR_USERNAME/news-aggregator-api.git

# Push
git branch -M main
git push -u origin main
```

### 4. Deploy to Railway (2 minutes)

1. **Go to [Railway](https://railway.app/)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your `news-aggregator-api` repository**
6. **Wait for build to complete** (~5 minutes)
7. **Generate domain**: Click "Settings" → "Generate Domain"
8. **Copy your URL**: `https://your-app.railway.app`

### 5. Test Your Deployment (1 minute)

```bash
# Run the test client
python test_railway_api.py

# Enter your Railway URL when prompted
# Example: https://news-aggregator-api-production.up.railway.app
```

## 🎯 That's It!

Your API is now live at: `https://YOUR_APP.railway.app`

## 📖 Quick API Reference

### Endpoints

```bash
# Health check (instant)
curl https://YOUR_APP.railway.app/health

# Get all news (~4 minutes)
curl https://YOUR_APP.railway.app/scrape

# Get Pulse news only (~1 minute)  
curl https://YOUR_APP.railway.app/scrape/pulse

# API documentation
# Visit: https://YOUR_APP.railway.app/docs
```

### Example Response

```json
{
  "success": true,
  "duration_seconds": 245.67,
  "summary": {
    "total_groww_items": 9,
    "total_pulse_articles": 26,
    "total_items": 35
  },
  "sources": {
    "groww": { "success": true, "data": {...} },
    "pulse": { "success": true, "data": {...} }
  }
}
```

## 🔧 Common Issues

### "Cannot connect to API"
- Check if Railway deployment is complete
- Verify the URL is correct
- Make sure the app is not sleeping (free tier sleeps after inactivity)

### "Request timeout"
- Normal! Scraping takes 4+ minutes
- Make sure your client timeout is set to at least 5 minutes
- Check Railway logs for any errors

### "Build failed on Railway"
- Check Railway logs for specific error
- Verify all files were pushed to GitHub
- Make sure Dockerfile is present

## 💡 Tips

1. **Save Your URL**: Bookmark your Railway app URL
2. **Check Logs**: Railway dashboard shows real-time logs
3. **Free Tier**: 500 hours/month is plenty for testing
4. **Upgrade**: If you need more performance, upgrade to Pro ($5/month)

## 📚 Documentation

- **Full Deployment Guide**: See `RAILWAY_DEPLOYMENT.md`
- **API Documentation**: Visit `https://YOUR_APP.railway.app/docs`
- **Railway Docs**: https://docs.railway.app/

## 🎉 Success Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Build completed (check Railway dashboard)
- [ ] Domain generated
- [ ] Health endpoint works
- [ ] Documentation accessible
- [ ] Scraping endpoint tested

## 🆘 Need Help?

1. Check `RAILWAY_DEPLOYMENT.md` for detailed troubleshooting
2. View Railway logs in the dashboard
3. Test locally first: `python news_api.py`
4. Use the test client: `python test_railway_api.py`

---

**Happy Scraping! 🚀**

