"""
Test Client for Deployed Railway API
=====================================

Script to test the API deployed on Railway.

Usage:
    python test_railway_api.py
"""

import requests
import json
import time
from datetime import datetime


def get_api_url():
    """Get the Railway API URL from user"""
    print("\n" + "=" * 80)
    print("RAILWAY API TESTER")
    print("=" * 80)
    print("\nEnter your Railway API URL")
    print("Example: https://your-app.railway.app")
    print("(or press Enter to use localhost for testing)")
    
    url = input("\nAPI URL: ").strip()
    
    if not url:
        url = "http://localhost:8000"
        print(f"Using local URL: {url}")
    elif not url.startswith('http'):
        url = f"https://{url}"
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    return url


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")


def test_health_check(api_url):
    """Test the health check endpoint"""
    print_header("Testing Health Check")
    
    try:
        print(f"GET {api_url}/health")
        response = requests.get(f"{api_url}/health", timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.Timeout:
        print("❌ Request timed out")
        return False
    except requests.ConnectionError:
        print("❌ Connection error - Is the API running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_root(api_url):
    """Test the root endpoint"""
    print_header("Testing Root Endpoint")
    
    try:
        print(f"GET {api_url}/")
        response = requests.get(f"{api_url}/", timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_scrape_combined(api_url):
    """Test the combined scrape endpoint"""
    print_header("Testing Combined Scrape")
    
    print("⚠️  This will take approximately 4-5 minutes")
    print("The scrapers are running on the Railway server in headless mode")
    
    proceed = input("\nProceed? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Skipped")
        return False
    
    try:
        print(f"\nGET {api_url}/scrape")
        print("Waiting for response... (timeout: 7 minutes)")
        
        start_time = time.time()
        response = requests.get(f"{api_url}/scrape", timeout=420)  # 7 min timeout
        end_time = time.time()
        
        duration = end_time - start_time
        
        print(f"\n✅ Request completed in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print summary
            print("\n" + "-" * 80)
            print("SUMMARY")
            print("-" * 80)
            print(f"API Duration: {data.get('duration_seconds', 0):.2f} seconds")
            print(f"Groww Success: {data.get('sources', {}).get('groww', {}).get('success', False)}")
            print(f"Pulse Success: {data.get('sources', {}).get('pulse', {}).get('success', False)}")
            print(f"Total Groww Items: {data.get('summary', {}).get('total_groww_items', 0)}")
            print(f"Total Pulse Articles: {data.get('summary', {}).get('total_pulse_articles', 0)}")
            print(f"Total Items: {data.get('summary', {}).get('total_items', 0)}")
            
            # Save response
            filename = f"railway_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Full response saved to: {filename}")
            
            # Show sample data
            if data.get('sources', {}).get('groww', {}).get('success'):
                print("\n" + "-" * 80)
                print("SAMPLE GROWW NEWS (First 2 items)")
                print("-" * 80)
                items = data['sources']['groww']['data']['news_items'][:2]
                for i, item in enumerate(items, 1):
                    print(f"\n{i}. {item.get('headline', 'N/A')}")
                    print(f"   Stock: {item.get('stock_name', 'N/A')} ({item.get('stock_change', 'N/A')})")
                    print(f"   Source: {item.get('source', 'N/A')} | {item.get('time', 'N/A')}")
            
            if data.get('sources', {}).get('pulse', {}).get('success'):
                print("\n" + "-" * 80)
                print("SAMPLE PULSE ARTICLES (First 2 items)")
                print("-" * 80)
                articles = data['sources']['pulse']['data']['articles'][:2]
                for i, article in enumerate(articles, 1):
                    print(f"\n{i}. {article.get('headline', 'N/A')}")
                    print(f"   Source: {article.get('source', 'N/A')} | {article.get('time', 'N/A')}")
                    print(f"   Content: {article.get('content', 'N/A')[:100]}...")
            
            return True
        else:
            print(f"❌ Error response:")
            print(response.text)
            return False
            
    except requests.Timeout:
        print("❌ Request timed out (took longer than 7 minutes)")
        print("This could mean:")
        print("  - The scrapers are taking longer than expected")
        print("  - The Railway instance may have limited resources")
        print("  - Network connectivity issues")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scrape_pulse(api_url):
    """Test the Pulse-only endpoint"""
    print_header("Testing Pulse Scraper Only")
    
    print("⚠️  This will take approximately 1-2 minutes")
    proceed = input("\nProceed? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Skipped")
        return False
    
    try:
        print(f"\nGET {api_url}/scrape/pulse")
        print("Waiting for response...")
        
        start_time = time.time()
        response = requests.get(f"{api_url}/scrape/pulse", timeout=180)
        end_time = time.time()
        
        duration = end_time - start_time
        
        print(f"\n✅ Request completed in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                articles = data.get('data', {}).get('articles', [])
                print(f"Total Articles: {len(articles)}")
                
                if articles:
                    print("\nFirst article:")
                    print(json.dumps(articles[0], indent=2))
            else:
                print(f"Error: {data.get('error')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("RAILWAY DEPLOYMENT TESTER")
    print("News Aggregator API")
    print("=" * 80)
    
    # Get API URL
    api_url = get_api_url()
    
    # Test connection first
    print_header("Checking API Connection")
    try:
        response = requests.get(api_url, timeout=10)
        print(f"✅ Successfully connected to: {api_url}")
    except:
        print(f"❌ Cannot connect to: {api_url}")
        print("\nPlease check:")
        print("  1. The URL is correct")
        print("  2. The Railway app is deployed and running")
        print("  3. You have internet connectivity")
        return
    
    # Menu
    while True:
        print("\n" + "-" * 80)
        print("Select test to run:")
        print("-" * 80)
        print("1. Health Check (quick)")
        print("2. Root/Info Endpoint (quick)")
        print("3. Scrape Both Sources - ~4-5 minutes ⚠️")
        print("4. Scrape Pulse Only - ~1-2 minutes")
        print("5. Change API URL")
        print("6. Exit")
        print("-" * 80)
        print(f"\nCurrent API: {api_url}")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            test_health_check(api_url)
        elif choice == '2':
            test_root(api_url)
        elif choice == '3':
            test_scrape_combined(api_url)
        elif choice == '4':
            test_scrape_pulse(api_url)
        elif choice == '5':
            api_url = get_api_url()
        elif choice == '6':
            print("\nGoodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()

