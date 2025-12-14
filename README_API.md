# News Aggregator API

A FastAPI-based REST API that scrapes news from multiple sources (Groww and Pulse by Zerodha) in parallel and returns combined results.

## Features

- ✅ Runs multiple scrapers in parallel for faster response times
- ✅ RESTful API with automatic documentation
- ✅ Combines results from multiple news sources
- ✅ Saves results to JSON files
- ✅ Error handling and logging
- ✅ CORS enabled for web applications

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Scrapers Work

Test individual scrapers first:

```bash
# Test Groww scraper (~4 minutes)
python grownews.py

# Test Pulse scraper (~1 minute)
python pulse_zerodha_scraper.py
```

## Usage

### Starting the Server

#### Method 1: Using Python directly

```bash
python news_api.py
```

#### Method 2: Using Uvicorn

```bash
uvicorn news_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### API Endpoints

#### 1. **GET /** - Root/Info
Returns API information and available endpoints.

```bash
curl http://localhost:8000/
```

#### 2. **GET /health** - Health Check
Quick health check endpoint.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-14T20:10:16.123456"
}
```

#### 3. **GET /scrape** - Scrape All Sources (Main Endpoint)
Runs both scrapers in parallel and returns combined results.

**⚠️ Takes ~4 minutes** (limited by Groww scraper)

```bash
curl http://localhost:8000/scrape
```

Response structure:
```json
{
  "success": true,
  "timestamp": "2025-12-14T20:15:30.123456",
  "duration_seconds": 245.67,
  "sources": {
    "groww": {
      "success": true,
      "data": {
        "scrape_timestamp": "...",
        "url": "https://groww.in/share-market-today",
        "total_news_items": 9,
        "news_items": [...]
      }
    },
    "pulse": {
      "success": true,
      "data": {
        "scrape_timestamp": "...",
        "url": "https://pulse.zerodha.com/",
        "total_articles": 26,
        "articles": [...]
      }
    }
  },
  "summary": {
    "total_groww_items": 9,
    "total_pulse_articles": 26,
    "total_items": 35
  },
  "saved_to": "combined_news_20251214_201530.json"
}
```

#### 4. **GET /scrape/groww** - Scrape Groww Only
Runs only the Groww scraper.

**⚠️ Takes ~4 minutes**

```bash
curl http://localhost:8000/scrape/groww
```

#### 5. **GET /scrape/pulse** - Scrape Pulse Only
Runs only the Pulse scraper.

**⚠️ Takes ~1 minute**

```bash
curl http://localhost:8000/scrape/pulse
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

Use the provided test client to test all endpoints:

```bash
python test_api.py
```

The test client provides an interactive menu to test each endpoint.

## Response Times

| Endpoint | Duration | Description |
|----------|----------|-------------|
| `/health` | < 1 second | Health check |
| `/scrape/pulse` | ~1 minute | Pulse scraper only |
| `/scrape/groww` | ~4 minutes | Groww scraper only |
| `/scrape` | ~4 minutes | **Both scrapers in parallel** |

**Note**: Running both scrapers in parallel takes ~4 minutes (not 5 minutes), because they run simultaneously. The total time is limited by the slowest scraper (Groww).

## Data Structure

### Groww News Item
```json
{
  "source": "Business Standard",
  "time": "4 hours ago",
  "headline": "Godrej Properties sells homes worth ₹2,600 cr...",
  "stock_name": "Godrej Properties",
  "stock_change": "1.94%"
}
```

### Pulse Article
```json
{
  "headline": "Enforcement Directorate aims to end legacy FERA cases...",
  "content": "The criminal sections-loaded FERA of 1973 was replaced...",
  "source": "The Hindu Business",
  "time": "55 minutes ago",
  "article_url": "https://www.thehindu.com/news/..."
}
```

## Production Deployment

### Using Gunicorn with Uvicorn workers

```bash
gunicorn news_api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 600
```

### Environment Variables

You can configure the following (optional):

```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export LOG_LEVEL=INFO
```

## Error Handling

The API includes comprehensive error handling:

- **500 Internal Server Error**: If scrapers fail
- **Partial Success**: If one scraper succeeds and one fails, you'll still get the successful data
- Each source result includes a `success` field and an optional `error` field

Example error response:
```json
{
  "success": false,
  "source": "groww",
  "error": "Failed to load page",
  "timestamp": "2025-12-14T20:10:16.123456"
}
```

## Logging

Logs are written to console with timestamps:

```
2025-12-14 20:10:16 - INFO - Received scrape request
2025-12-14 20:10:16 - INFO - Starting Groww scraper...
2025-12-14 20:10:16 - INFO - Starting Pulse scraper...
2025-12-14 20:11:30 - INFO - Pulse scraper completed: 26 items
2025-12-14 20:14:45 - INFO - Groww scraper completed: 9 items
2025-12-14 20:14:45 - INFO - Both scrapers completed in 269.12 seconds
```

## Notes

- Both scrapers run in **headless mode** (no browser window)
- Results are automatically saved to JSON files with timestamps
- The API runs scrapers in separate threads to avoid blocking
- CORS is enabled for all origins (configure for production)

## Troubleshooting

### ChromeDriver Issues
If you get ChromeDriver errors, update it:
```bash
pip install --upgrade webdriver-manager
```

### Timeout Issues
If requests timeout, increase the timeout in your client:
```python
response = requests.get(url, timeout=600)  # 10 minutes
```

### Memory Issues
If running multiple requests simultaneously, consider:
- Increasing system memory
- Running scrapers sequentially instead of in parallel
- Using a queue system (Celery, RQ) for background tasks

## License

MIT License

