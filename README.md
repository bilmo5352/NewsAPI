# 📰 News Aggregator API

A FastAPI-based REST API that scrapes financial news from multiple Indian sources (Groww and Pulse by Zerodha) in parallel and returns combined results.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

## ✨ Features

- 🚀 **Parallel Scraping** - Runs multiple scrapers simultaneously
- 📊 **Multi-Source** - Aggregates news from Groww and Pulse by Zerodha
- 🔄 **RESTful API** - Clean JSON responses
- 📚 **Auto Documentation** - Interactive Swagger UI
- 🐳 **Docker Ready** - Easy deployment with Docker
- ☁️ **Railway Deploy** - One-click deployment to Railway
- 🔍 **Selenium-based** - Reliable web scraping with Selenium
- ⚡ **Fast Response** - ~4 minutes for full aggregation

## 📋 What It Scrapes

### Groww (groww.in)
- Stock-specific news
- Company headlines
- Stock price changes
- News source and timestamp

### Pulse by Zerodha (pulse.zerodha.com)
- Market news articles
- Article summaries
- Source publications
- Relative timestamps
- Article URLs

## 🚀 Quick Start

### Option 1: Railway Deployment (Fastest - 5 minutes)

1. **Read the Quick Start Guide**
   ```bash
   # Open QUICKSTART.md for step-by-step instructions
   ```

2. **Deploy to Railway**
   - Push code to GitHub
   - Connect to Railway
   - Automated deployment
   - Get your live URL

   📖 **Full guide**: See [QUICKSTART.md](QUICKSTART.md) and [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

### Option 2: Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API**
   ```bash
   python news_api.py
   ```

3. **Test It**
   ```bash
   # In another terminal
   python test_api.py
   ```

   API will be available at: http://localhost:8000

### Option 3: Docker (Local Testing)

1. **Build and Run**
   ```bash
   # Windows
   test_docker.bat

   # Or manually
   docker-compose up -d
   ```

2. **Access API**
   - URL: http://localhost:8000
   - Docs: http://localhost:8000/docs

## 📖 API Documentation

### Endpoints

| Endpoint | Method | Description | Time |
|----------|--------|-------------|------|
| `/` | GET | API information | < 1s |
| `/health` | GET | Health check | < 1s |
| `/docs` | GET | Interactive Swagger UI | < 1s |
| `/scrape` | GET | **Scrape both sources** | ~4 min |
| `/scrape/groww` | GET | Scrape Groww only | ~4 min |
| `/scrape/pulse` | GET | Scrape Pulse only | ~1 min |

### Example Usage

**Health Check**
```bash
curl https://your-app.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-14T20:30:00.123456"
}
```

**Scrape All Sources**
```bash
curl https://your-app.railway.app/scrape
```

Response:
```json
{
  "success": true,
  "timestamp": "2025-12-14T20:35:00.123456",
  "duration_seconds": 245.67,
  "sources": {
    "groww": {
      "success": true,
      "data": {
        "total_news_items": 9,
        "news_items": [
          {
            "headline": "Godrej Properties sells homes...",
            "stock_name": "Godrej Properties",
            "stock_change": "1.94%",
            "source": "Business Standard",
            "time": "4 hours ago"
          }
        ]
      }
    },
    "pulse": {
      "success": true,
      "data": {
        "total_articles": 26,
        "articles": [
          {
            "headline": "Enforcement Directorate aims...",
            "content": "The criminal sections-loaded...",
            "source": "The Hindu Business",
            "time": "55 minutes ago",
            "article_url": "https://..."
          }
        ]
      }
    }
  },
  "summary": {
    "total_groww_items": 9,
    "total_pulse_articles": 26,
    "total_items": 35
  }
}
```

## 🛠️ Project Structure

```
newsAPI/
├── grownews.py              # Groww scraper
├── pulse_zerodha_scraper.py # Pulse scraper
├── news_api.py              # FastAPI application
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose config
├── railway.json            # Railway deployment config
├── .gitignore             # Git ignore rules
├── .dockerignore          # Docker ignore rules
├── test_api.py            # Local API test client
├── test_railway_api.py    # Railway deployment tester
├── deploy_to_github.bat   # GitHub deployment helper
├── test_docker.bat        # Docker local testing
├── stop_docker.bat        # Docker cleanup
├── start_api.bat          # Quick start script
├── README.md              # This file
├── QUICKSTART.md          # Quick deployment guide
└── RAILWAY_DEPLOYMENT.md  # Detailed Railway guide
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | API server port (Railway sets automatically) |
| `LOG_LEVEL` | INFO | Logging level |

### Railway Configuration

Set in Railway dashboard → Variables:
- Automatically detects `PORT`
- Optional: Add custom variables

## 🐳 Docker

### Build Image
```bash
docker build -t news-api .
```

### Run Container
```bash
docker run -p 8000:8000 news-api
```

### Using Docker Compose
```bash
docker-compose up -d
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| Groww Scraper | ~4 minutes |
| Pulse Scraper | ~1 minute |
| **Both (Parallel)** | **~4 minutes** |
| Response Size | ~50-200 KB |
| Memory Usage | ~300-500 MB |

## 🧪 Testing

### Local Testing
```bash
# Start API
python news_api.py

# Run test client
python test_api.py
```

### Railway Testing
```bash
python test_railway_api.py
# Enter your Railway URL when prompted
```

### Docker Testing
```bash
# Windows
test_docker.bat

# Linux/Mac
docker-compose up
```

## 🚢 Deployment

### Railway (Recommended)

**Quick Deploy:**
1. Push to GitHub
2. Connect Railway
3. Auto-deploy
4. Get URL

**Detailed Guide:** [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

### Other Platforms

The Docker configuration works with:
- **Heroku**: Use `heroku.yml`
- **AWS ECS**: Use Dockerfile
- **Google Cloud Run**: Use Dockerfile
- **Azure**: Use Dockerfile
- **DigitalOcean**: Use Docker Compose

## 💰 Cost

### Railway
- **Free Tier**: $0 (500 hours/month)
- **Pro Tier**: $5/month + usage
- **Estimated**: $5-10/month for production

### Resources Required
- **CPU**: 1 core minimum
- **RAM**: 512 MB minimum (2 GB recommended)
- **Disk**: 1 GB

## 🔒 Security

- ✅ CORS enabled (configure origins in production)
- ✅ No sensitive data in responses
- ✅ Rate limiting recommended (add middleware)
- ✅ Environment variables for secrets
- ⚠️ Consider adding authentication for production

## 📝 Development

### Adding New Scrapers

1. Create scraper class (follow pattern in existing scrapers)
2. Add function in `news_api.py`:
   ```python
   def run_new_scraper():
       scraper = NewScraper(headless=True)
       # ... scraping logic
       return result
   ```
3. Add to parallel execution in `/scrape` endpoint
4. Create dedicated endpoint `/scrape/new`

### Modifying Scrapers

- Edit `grownews.py` for Groww changes
- Edit `pulse_zerodha_scraper.py` for Pulse changes
- Test locally before deploying

## 🐛 Troubleshooting

### Common Issues

**ChromeDriver Errors**
```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager
```

**Timeout Issues**
- Normal for scraping endpoints (~4 min)
- Increase client timeout to 5+ minutes
- Check Railway logs for errors

**Memory Issues**
- Upgrade Railway tier for more RAM
- Run scrapers sequentially instead of parallel
- Use separate services for each scraper

**Build Failures**
```bash
# Test Docker build locally
docker build -t news-api .
```

### Getting Help

1. Check Railway logs
2. Test locally first
3. Review error messages
4. Check documentation:
   - [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
   - [QUICKSTART.md](QUICKSTART.md)

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Fast deployment guide
- **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** - Detailed Railway guide
- **[README_API.md](README_API.md)** - API documentation (local)
- **[pulse_zerodha_analysis.md](pulse_zerodha_analysis.md)** - Pulse scraper analysis

## 🤝 Contributing

Contributions welcome! To add features:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use for any project!

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **Selenium** - Web automation
- **Railway** - Easy deployment platform
- **Groww & Pulse** - News sources

## 📞 Support

- 🐛 **Issues**: Open a GitHub issue
- 💬 **Questions**: Check existing documentation
- 🚀 **Railway**: [Railway Discord](https://discord.gg/railway)

## 🎉 Success Stories

Share how you're using this API:
- Stock analysis applications
- News aggregation dashboards
- Trading signals
- Market research tools

---

**Made with ❤️ for the Indian stock market community**

**Happy Scraping! 🚀📈**

