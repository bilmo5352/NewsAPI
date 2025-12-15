"""
News Aggregator API
===================

FastAPI server that runs Groww and Pulse scrapers in parallel
and returns combined news data.

Usage:
    uvicorn news_api:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    GET /scrape - Triggers both scrapers and returns combined results
    GET /health - Health check endpoint
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
from typing import Dict, Any
import os

# Import scraper classes
from groww_scraper_fixed import GrowwScraperFixed
from pulse_zerodha_scraper import PulseZerodhaScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="News Aggregator API",
    description="API that scrapes news from Groww and Pulse by Zerodha",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for running scrapers
SCRAPE_PARALLEL = os.getenv("SCRAPE_PARALLEL", "0").strip().lower() in {"1", "true", "yes", "y"}
# Railway free tier often can't support 2 concurrent headless Chromes reliably.
# Default to sequential (1 worker). Set SCRAPE_PARALLEL=1 to opt into parallel.
executor = ThreadPoolExecutor(max_workers=2 if SCRAPE_PARALLEL else 1)


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    import os
    logger.info("=" * 80)
    logger.info("NEWS AGGREGATOR API - STARTING")
    logger.info("=" * 80)
    logger.info(f"Port: {os.getenv('PORT', '8000')}")
    logger.info(f"Chrome Binary: {os.getenv('CHROME_BIN', 'Not set')}")
    logger.info(f"Python version: {__import__('sys').version}")
    logger.info("Application started successfully!")
    logger.info("=" * 80)


def run_groww_scraper() -> Dict[str, Any]:
    """
    Run Groww scraper in headless mode
    
    Returns:
        dict: Scraped news data or error dict
    """
    try:
        logger.info("Starting Groww scraper...")
        scraper = GrowwScraperFixed(headless=True)
        
        # Scrape all data (includes setup, load, and cleanup)
        data = scraper.scrape_all()
        
        # Check if we got data
        if data and data.get('news'):
            logger.info(f"Groww scraper completed: {len(data['news'])} news items")
            
            # Format to match expected API response structure
            formatted_data = {
                'scraped_at': data.get('metadata', {}).get('scraped_at'),
                'url': data.get('metadata', {}).get('url'),
                'news_items': data.get('news', []),  # Map 'news' to 'news_items' for compatibility
                'indices': data.get('indices', []),
                'top_gainers': data.get('top_gainers', []),
                'top_losers': data.get('top_losers', []),
                'most_bought': data.get('most_bought', []),
                'most_traded': data.get('most_traded', [])
            }
            
            return {
                'success': True,
                'source': 'groww',
                'data': formatted_data
            }
        else:
            logger.warning("Groww scraper returned no items")
            return {
                'success': False,
                'source': 'groww',
                'error': 'No news items found',
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in Groww scraper: {e}", exc_info=True)
        return {
            'success': False,
            'source': 'groww',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def run_pulse_scraper() -> Dict[str, Any]:
    """
    Run Pulse by Zerodha scraper in headless mode
    
    Returns:
        dict: Scraped news data or error dict
    """
    try:
        logger.info("Starting Pulse scraper...")
        scraper = PulseZerodhaScraper(headless=True)
        
        # Initialize driver
        if not scraper._init_driver():
            logger.error("Failed to initialize Pulse driver")
            return {
                'error': 'Failed to initialize browser',
                'source': 'pulse',
                'timestamp': datetime.now().isoformat()
            }
        
        # Navigate to page
        if not scraper.navigate_to_page():
            logger.error("Failed to load Pulse page")
            scraper.cleanup()
            return {
                'error': 'Failed to load page',
                'source': 'pulse',
                'timestamp': datetime.now().isoformat()
            }
        
        # Scrape news
        news_data = scraper.scrape_all_news()
        
        # Cleanup
        scraper.cleanup()
        
        if news_data and news_data.get('articles'):
            logger.info(f"Pulse scraper completed: {len(news_data['articles'])} items")
            return {
                'success': True,
                'source': 'pulse',
                'data': news_data
            }
        else:
            logger.warning("Pulse scraper returned no articles")
            return {
                'success': False,
                'source': 'pulse',
                'error': 'No articles found',
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in Pulse scraper: {e}", exc_info=True)
        return {
            'success': False,
            'source': 'pulse',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "News Aggregator API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape": "Trigger both scrapers and get combined results",
            "/health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/scrape")
async def scrape_news():
    """
    Scrape news from both Groww and Pulse in parallel
    
    Returns:
        JSONResponse: Combined results from both scrapers
        
    Note: This endpoint takes approximately 4 minutes to complete
    (limited by Groww scraper which takes ~4 min)
    """
    start_time = datetime.now()
    logger.info("Received scrape request, starting both scrapers in parallel...")
    
    try:
        # Create event loop to run both scrapers in parallel
        loop = asyncio.get_event_loop()
        
        # Run both scrapers concurrently using thread pool
        groww_future = loop.run_in_executor(executor, run_groww_scraper)
        pulse_future = loop.run_in_executor(executor, run_pulse_scraper)
        
        # Wait for both to complete
        logger.info("Waiting for both scrapers to complete...")
        groww_result, pulse_result = await asyncio.gather(groww_future, pulse_future)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Both scrapers completed in {duration:.2f} seconds")
        
        # Prepare combined response
        response = {
            'success': True,
            'timestamp': end_time.isoformat(),
            'duration_seconds': round(duration, 2),
            'sources': {
                'groww': {
                    'success': groww_result.get('success', False),
                    'data': groww_result.get('data'),
                    'error': groww_result.get('error')
                },
                'pulse': {
                    'success': pulse_result.get('success', False),
                    'data': pulse_result.get('data'),
                    'error': pulse_result.get('error')
                }
            },
            'summary': {
                'total_groww_items': len(groww_result.get('data', {}).get('news_items', [])) if groww_result.get('success') else 0,
                'total_pulse_articles': len(pulse_result.get('data', {}).get('articles', [])) if pulse_result.get('success') else 0,
                'total_items': (
                    len(groww_result.get('data', {}).get('news_items', [])) +
                    len(pulse_result.get('data', {}).get('articles', []))
                ) if (groww_result.get('success') or pulse_result.get('success')) else 0
            }
        }
        
        # Save combined results to file
        try:
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"combined_news_{timestamp_str}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            logger.info(f"Combined results saved to: {filename}")
            response['saved_to'] = filename
        except Exception as e:
            logger.error(f"Error saving combined results: {e}")
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        )


@app.get("/scrape/groww")
async def scrape_groww_only():
    """
    Scrape news from Groww only
    
    Returns:
        JSONResponse: Groww scraper results
    """
    logger.info("Received Groww-only scrape request...")
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_groww_scraper)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error during Groww scraping: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'source': 'groww',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        )


@app.get("/scrape/pulse")
async def scrape_pulse_only():
    """
    Scrape news from Pulse only
    
    Returns:
        JSONResponse: Pulse scraper results
    """
    logger.info("Received Pulse-only scrape request...")
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_pulse_scraper)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error during Pulse scraping: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'source': 'pulse',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        )


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    
    print("\n" + "=" * 80)
    print("NEWS AGGREGATOR API")
    print("=" * 80)
    print("\nStarting server...")
    print(f"API will be available at: http://localhost:{port}")
    print("\nEndpoints:")
    print("  - GET /scrape       - Run both scrapers in parallel")
    print("  - GET /scrape/groww - Run Groww scraper only")
    print("  - GET /scrape/pulse - Run Pulse scraper only")
    print("  - GET /health       - Health check")
    print(f"\nDocumentation: http://localhost:{port}/docs")
    print("=" * 80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)

