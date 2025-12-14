# News Aggregator API

FastAPI-based REST API that scrapes financial news from Groww and Pulse by Zerodha in parallel.

## Features

- Parallel scraping from multiple sources
- RESTful API with automatic OpenAPI documentation
- Docker containerized with Chrome/ChromeDriver
- Ready for Railway deployment
- Headless browser execution
- ~4 minute response time for full aggregation

## Data Sources

**Groww** - Stock news, company headlines, price changes  
**Pulse** - Market articles, summaries, publication sources

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python news_api.py

# Access at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Docker

```bash
docker-compose up -d
```

### Railway Deployment

1. Push code to GitHub
2. Create new project on [Railway](https://railway.app/)
3. Connect GitHub repository
4. Railway auto-detects Dockerfile and deploys
5. Generate domain in settings

## API Endpoints

| Endpoint | Description | Response Time |
|----------|-------------|---------------|
| `GET /` | API information | < 1s |
| `GET /health` | Health check | < 1s |
| `GET /docs` | Swagger documentation | < 1s |
| `GET /scrape` | Scrape both sources (parallel) | ~4 min |
| `GET /scrape/groww` | Groww only | ~4 min |
| `GET /scrape/pulse` | Pulse only | ~1 min |

### Example

```bash
curl https://your-app.railway.app/scrape
```

```json
{
  "success": true,
  "duration_seconds": 245.67,
  "sources": {
    "groww": { "success": true, "data": {...} },
    "pulse": { "success": true, "data": {...} }
  },
  "summary": {
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

