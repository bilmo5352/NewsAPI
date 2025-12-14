"""
Simple News API Client - Quick Example
=======================================

Minimal example to fetch news from Railway API.

Usage:
    python simple_client.py YOUR_RAILWAY_URL
"""

import requests
import json
import sys


def get_news(api_url: str):
    """Fetch and display news"""
    api_url = api_url.rstrip('/')
    
    print(f"Fetching news from: {api_url}")
    print("⏳ This will take ~4 minutes...\n")
    
    try:
        response = requests.get(f"{api_url}/scrape", timeout=300)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            summary = data.get('summary', {})
            print(f"✅ Success! Found {summary.get('total_items', 0)} items")
            print(f"   Duration: {data.get('duration_seconds', 0):.2f} seconds")
            print(f"   Groww: {summary.get('total_groww_items', 0)} items")
            print(f"   Pulse: {summary.get('total_pulse_articles', 0)} articles")
            
            # Save to file
            filename = f"news_{data.get('timestamp', 'latest').replace(':', '-')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved to: {filename}")
            
            # Show sample
            sources = data.get('sources', {})
            if sources.get('groww', {}).get('success'):
                items = sources['groww']['data']['news_items'][:3]
                print("\n📰 Sample Groww News:")
                for item in items:
                    print(f"   • {item.get('headline', '')[:60]}...")
            
            if sources.get('pulse', {}).get('success'):
                articles = sources['pulse']['data']['articles'][:3]
                print("\n📰 Sample Pulse Articles:")
                for article in articles:
                    print(f"   • {article.get('headline', '')[:60]}...")
        else:
            print("❌ Scraping failed")
            print(data)
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter Railway API URL: ").strip()
    
    if not url:
        print("❌ URL required")
        sys.exit(1)
    
    get_news(url)

