"""
Test Client for News Aggregator API
====================================

Simple script to test the API endpoints.

Usage:
    python test_api.py
"""

import requests
import json
import time
from datetime import datetime


API_BASE_URL = "http://localhost:8000"


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")


def test_health_check():
    """Test the health check endpoint"""
    print_header("Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_scrape_combined():
    """Test the combined scrape endpoint"""
    print_header("Testing Combined Scrape Endpoint (This will take ~4 minutes)")
    
    try:
        print("Sending request...")
        start_time = time.time()
        
        response = requests.get(f"{API_BASE_URL}/scrape", timeout=300)  # 5 min timeout
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Request completed in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "-" * 80)
            print("SUMMARY:")
            print("-" * 80)
            print(f"Total Duration: {data.get('duration_seconds', 0):.2f} seconds")
            print(f"Groww Items: {data.get('summary', {}).get('total_groww_items', 0)}")
            print(f"Pulse Articles: {data.get('summary', {}).get('total_pulse_articles', 0)}")
            print(f"Total Items: {data.get('summary', {}).get('total_items', 0)}")
            
            # Save response to file
            filename = f"api_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\nFull response saved to: {filename}")
            
            # Display sample items
            print("\n" + "-" * 80)
            print("SAMPLE GROWW NEWS:")
            print("-" * 80)
            groww_items = data.get('sources', {}).get('groww', {}).get('data', {}).get('news_items', [])
            for i, item in enumerate(groww_items[:3], 1):
                print(f"\n{i}. {item.get('headline', 'N/A')[:70]}...")
                print(f"   Stock: {item.get('stock_name', 'N/A')} ({item.get('stock_change', 'N/A')})")
            
            print("\n" + "-" * 80)
            print("SAMPLE PULSE ARTICLES:")
            print("-" * 80)
            pulse_articles = data.get('sources', {}).get('pulse', {}).get('data', {}).get('articles', [])
            for i, article in enumerate(pulse_articles[:3], 1):
                print(f"\n{i}. {article.get('headline', 'N/A')[:70]}...")
                print(f"   Source: {article.get('source', 'N/A')} | {article.get('time', 'N/A')}")
            
            return True
        else:
            print(f"❌ Error response: {response.text}")
            return False
            
    except requests.Timeout:
        print("❌ Request timed out (took longer than 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scrape_groww_only():
    """Test the Groww-only scrape endpoint"""
    print_header("Testing Groww-Only Scrape Endpoint")
    
    try:
        print("Sending request... (This will take ~4 minutes)")
        start_time = time.time()
        
        response = requests.get(f"{API_BASE_URL}/scrape/groww", timeout=300)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Request completed in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                items = data.get('data', {}).get('news_items', [])
                print(f"Total Items: {len(items)}")
                
                if items:
                    print("\nSample item:")
                    print(json.dumps(items[0], indent=2))
            else:
                print(f"Error: {data.get('error')}")
            return True
        else:
            print(f"❌ Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_scrape_pulse_only():
    """Test the Pulse-only scrape endpoint"""
    print_header("Testing Pulse-Only Scrape Endpoint")
    
    try:
        print("Sending request... (This will take ~1 minute)")
        start_time = time.time()
        
        response = requests.get(f"{API_BASE_URL}/scrape/pulse", timeout=120)
        
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
                    print("\nSample article:")
                    print(json.dumps(articles[0], indent=2))
            else:
                print(f"Error: {data.get('error')}")
            return True
        else:
            print(f"❌ Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("NEWS AGGREGATOR API - TEST CLIENT")
    print("=" * 80)
    
    # Check if API is running
    print("\nChecking if API is running...")
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        print("✅ API is running!\n")
    except:
        print("❌ API is not running. Please start it with:")
        print("   python news_api.py")
        print("   or")
        print("   uvicorn news_api:app --reload")
        return
    
    # Menu
    while True:
        print("\n" + "-" * 80)
        print("Select test to run:")
        print("-" * 80)
        print("1. Health Check (quick)")
        print("2. Scrape Both (Groww + Pulse) - ~4 minutes")
        print("3. Scrape Groww Only - ~4 minutes")
        print("4. Scrape Pulse Only - ~1 minute")
        print("5. Exit")
        print("-" * 80)
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            test_health_check()
        elif choice == '2':
            test_scrape_combined()
        elif choice == '3':
            test_scrape_groww_only()
        elif choice == '4':
            test_scrape_pulse_only()
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()

