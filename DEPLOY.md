# Deployment Guide

## Prerequisites
- GitHub account
- Railway account

## Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "News Aggregator API"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app/)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Wait for build (~5-10 minutes)
7. Click "Generate Domain" in Settings

### 3. Test Deployment
```bash
curl https://YOUR_APP.railway.app/health
```

Expected response:
```json
{"status":"healthy","timestamp":"..."}
```

### 4. Test Scraping
```bash
curl https://YOUR_APP.railway.app/scrape/pulse
```

Response time: ~1-2 minutes

## API Endpoints

- `GET /health` - Health check
- `GET /docs` - API documentation  
- `GET /scrape` - Scrape both sources (~4 min)
- `GET /scrape/groww` - Groww only (~4 min)
- `GET /scrape/pulse` - Pulse only (~1 min)

## Configuration

All configuration is handled automatically:
- **Dockerfile** - Contains all Chrome dependencies
- **railway.json** - Deployment settings
- **requirements.txt** - Python dependencies

Chrome runs in headless mode with proper container flags.

## Troubleshooting

### Build fails
Check Railway logs for specific errors.

### App doesn't respond
- Wait 30-40 seconds after build completes
- Check if domain was generated
- Verify health endpoint first

### Scraping fails
- Check Railway logs for Chrome errors
- Free tier may need upgrade for consistent performance

## Local Testing

```bash
# Install
pip install -r requirements.txt

# Run
python news_api.py

# Test
curl http://localhost:8000/health
```

## Docker Testing

```bash
docker-compose up -d
curl http://localhost:8000/health
```

## Notes

- First build: 5-10 minutes (Chrome download)
- Subsequent builds: 2-3 minutes
- Free tier: 500 hours/month
- Pro tier recommended for production ($5/month)

