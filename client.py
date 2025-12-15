"""
News Aggregator API Client
==========================

Simple client to fetch news from the deployed Railway API.

Usage:
    python client.py
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional


class NewsAPIClient:
    """Client for News Aggregator API"""
    
    def __init__(self, base_url: str):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the API (e.g., https://your-app.railway.app)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 600  # 10 minutes for scraping
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is healthy - {data.get('timestamp', '')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error connecting to API: {e}")
            return False
    
    def get_all_news(self) -> Optional[dict]:
        """
        Get news from both sources (parallel scraping)
        
        Returns:
            dict: Combined news data or None if error
        """
        print("\n" + "=" * 80)
        print("FETCHING NEWS FROM ALL SOURCES")
        print("=" * 80)
        print("⏳ This will take approximately 4 minutes...")
        print("   (Both scrapers running in parallel)")
        print()
        
        try:
            response = self.session.get(f"{self.base_url}/scrape")
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            print("❌ Request timed out (took longer than 10 minutes)")
            return None
        except requests.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            if e.response:
                try:
                    error_data = e.response.json()
                    print(f"   Details: {error_data}")
                except:
                    print(f"   Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_groww_news(self) -> Optional[dict]:
        """
        Get news from Groww only
        
        Returns:
            dict: Groww news data or None if error
        """
        print("\n" + "=" * 80)
        print("FETCHING NEWS FROM GROWW")
        print("=" * 80)
        print("⏳ This will take approximately 4 minutes...")
        print()
        
        try:
            response = self.session.get(f"{self.base_url}/scrape/groww")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_pulse_news(self) -> Optional[dict]:
        """
        Get news from Pulse only
        
        Returns:
            dict: Pulse news data or None if error
        """
        print("\n" + "=" * 80)
        print("FETCHING NEWS FROM PULSE")
        print("=" * 80)
        print("⏳ This will take approximately 1-2 minutes...")
        print()
        
        try:
            response = self.session.get(f"{self.base_url}/scrape/pulse")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def display_news(self, data: dict, source: str = "all"):
        """Display news in a readable format"""
        if not data:
            print("❌ No data to display")
            return
        
        print("\n" + "=" * 80)
        print(f"NEWS RESULTS - {source.upper()}")
        print("=" * 80)
        
        if source == "all":
            # Combined results
            if data.get('success'):
                summary = data.get('summary', {})
                print(f"\n📊 Summary:")
                print(f"   Total Duration: {data.get('duration_seconds', 0):.2f} seconds")
                print(f"   Groww Items: {summary.get('total_groww_items', 0)}")
                print(f"   Pulse Articles: {summary.get('total_pulse_articles', 0)}")
                print(f"   Total Items: {summary.get('total_items', 0)}")
                
                sources = data.get('sources', {})
                
                # Display Groww news
                groww_data = sources.get('groww', {})
                if groww_data.get('success'):
                    print("\n" + "-" * 80)
                    print("GROWW NEWS")
                    print("-" * 80)
                    news_items = groww_data.get('data', {}).get('news_items', [])
                    for i, item in enumerate(news_items, 1):
                        print(f"\n{i}. {item.get('headline', 'N/A')}")
                        print(f"   Stock: {item.get('stock_name', 'N/A')} ({item.get('stock_change', 'N/A')})")
                        print(f"   Source: {item.get('source', 'N/A')} | {item.get('time', 'N/A')}")
                else:
                    print(f"\n⚠️  Groww: {groww_data.get('error', 'Failed')}")
                
                # Display Pulse news
                pulse_data = sources.get('pulse', {})
                if pulse_data.get('success'):
                    print("\n" + "-" * 80)
                    print("PULSE ARTICLES")
                    print("-" * 80)
                    articles = pulse_data.get('data', {}).get('articles', [])
                    for i, article in enumerate(articles, 1):
                        print(f"\n{i}. {article.get('headline', 'N/A')}")
                        print(f"   Source: {article.get('source', 'N/A')} | {article.get('time', 'N/A')}")
                        content = article.get('content', '')
                        if content:
                            print(f"   {content[:150]}...")
                else:
                    print(f"\n⚠️  Pulse: {pulse_data.get('error', 'Failed')}")
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
        
        elif source == "groww":
            # Groww only
            if data.get('success'):
                news_items = data.get('data', {}).get('news_items', [])
                print(f"\n📰 Found {len(news_items)} news items\n")
                for i, item in enumerate(news_items, 1):
                    print(f"{i}. {item.get('headline', 'N/A')}")
                    print(f"   Stock: {item.get('stock_name', 'N/A')} ({item.get('stock_change', 'N/A')})")
                    print(f"   Source: {item.get('source', 'N/A')} | {item.get('time', 'N/A')}")
                    print()
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
        
        elif source == "pulse":
            # Pulse only
            if data.get('success'):
                articles = data.get('data', {}).get('articles', [])
                print(f"\n📰 Found {len(articles)} articles\n")
                for i, article in enumerate(articles, 1):
                    print(f"{i}. {article.get('headline', 'N/A')}")
                    print(f"   Source: {article.get('source', 'N/A')} | {article.get('time', 'N/A')}")
                    content = article.get('content', '')
                    if content:
                        print(f"   {content[:150]}...")
                    print()
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 80)
    
    def save_to_file(self, data: dict, filename: Optional[str] = None):
        """Save news data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"news_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Data saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("NEWS AGGREGATOR API CLIENT")
    print("=" * 80)
    
    # Get API URL
    print("\nEnter your Railway API URL")
    print("Example: https://newsapi-production-7bb4.up.railway.app")
    
    default_url = "https://newsapi-production-7bb4.up.railway.app"
    url_input = input(f"\nAPI URL (or press Enter for {default_url}): ").strip()
    
    if not url_input:
        url_input = default_url
    
    # Remove trailing slash
    api_url = url_input.rstrip('/')
    
    # Initialize client
    client = NewsAPIClient(api_url)
    
    # Health check
    print(f"\n🔍 Checking API health at: {api_url}")
    if not client.health_check():
        print("\n❌ API is not responding. Please check:")
        print("   1. The URL is correct")
        print("   2. The Railway app is deployed and running")
        print("   3. You have internet connectivity")
        sys.exit(1)
    
    # Menu
    while True:
        print("\n" + "-" * 80)
        print("SELECT OPTION:")
        print("-" * 80)
        print("1. Get all news (Groww + Pulse) - ~4 minutes")
        print("2. Get Groww news only - ~4 minutes")
        print("3. Get Pulse news only - ~1-2 minutes")
        print("4. Health check")
        print("5. Change API URL")
        print("6. Exit")
        print("-" * 80)
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            data = client.get_all_news()
            if data:
                client.display_news(data, "all")
                save = input("\n💾 Save to file? (y/n): ").strip().lower()
                if save == 'y':
                    client.save_to_file(data)
        
        elif choice == '2':
            data = client.get_groww_news()
            if data:
                client.display_news(data, "groww")
                save = input("\n💾 Save to file? (y/n): ").strip().lower()
                if save == 'y':
                    client.save_to_file(data)
        
        elif choice == '3':
            data = client.get_pulse_news()
            if data:
                client.display_news(data, "pulse")
                save = input("\n💾 Save to file? (y/n): ").strip().lower()
                if save == 'y':
                    client.save_to_file(data)
        
        elif choice == '4':
            client.health_check()
        
        elif choice == '5':
            new_url = input("\nEnter new API URL: ").strip()
            if new_url:
                api_url = new_url.rstrip('/')
                client = NewsAPIClient(api_url)
                print(f"✅ API URL updated to: {api_url}")
        
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


