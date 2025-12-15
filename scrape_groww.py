"""
Simple Groww scraper that actually works
Usage: python scrape_groww.py
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def setup_driver(headless=False):
    """Setup Chrome driver"""
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    return driver


def scrape_groww(headless=False):
    """Scrape Groww share market page"""
    driver = setup_driver(headless)
    data = {
        "scraped_at": datetime.now().isoformat(),
        "indices": [],
        "news": [],
        "stocks": []
    }
    
    try:
        print("Loading page...")
        driver.get("https://groww.in/share-market-today")
        time.sleep(5)  # Wait for page to load
        
        # Scroll to load content
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 1000});")
            time.sleep(1)
        
        print("\n✓ Page loaded")
        
        # Get all text elements
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        
        # Extract indices
        print("\n📊 Scraping indices...")
        index_names = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'FINNIFTY', 'MIDCPNIFTY']
        for elem in all_elements:
            try:
                text = elem.text.strip()
                for idx_name in index_names:
                    if text.startswith(idx_name) and '\n' in text:
                        lines = text.split('\n')
                        if len(lines) >= 2:
                            data['indices'].append({
                                "name": lines[0],
                                "value": lines[1],
                                "change": lines[2] if len(lines) > 2 else ""
                            })
                            index_names.remove(idx_name)
                            break
            except:
                pass
        
        print(f"  Found: {len(data['indices'])} indices")
        
        # Extract news
        print("\n📰 Scraping news...")
        for elem in all_elements:
            try:
                text = elem.text.strip()
                # News items have "·" and time patterns
                if '·' in text and 'ago' in text.lower() and 30 < len(text) < 300:
                    lines = text.split('\n')
                    source_line = [l for l in lines if '·' in l and 'ago' in l.lower()]
                    
                    if source_line and len(lines) >= 2:
                        source_time = source_line[0].split('·')
                        headline_candidates = [l for l in lines if l not in source_line and len(l) > 20]
                        
                        if headline_candidates:
                            news_item = {
                                "source": source_time[0].strip(),
                                "time": source_time[1].strip() if len(source_time) > 1 else "",
                                "headline": headline_candidates[0]
                            }
                            
                            # Check if not duplicate
                            if not any(n['headline'] == news_item['headline'] for n in data['news']):
                                data['news'].append(news_item)
            except:
                pass
        
        print(f"  Found: {len(data['news'])} news items")
        
        # Extract stocks (with price and %)
        print("\n📈 Scraping stocks...")
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            try:
                text = link.text.strip()
                if '₹' in text and '\n' in text:
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    if len(lines) >= 2 and len(lines[0]) < 50:
                        data['stocks'].append({
                            "name": lines[0],
                            "price": lines[1] if '₹' in lines[1] else "",
                            "change": lines[2] if len(lines) > 2 else ""
                        })
            except:
                pass
        
        # Remove duplicates
        seen = set()
        unique_stocks = []
        for stock in data['stocks']:
            if stock['name'] not in seen:
                seen.add(stock['name'])
                unique_stocks.append(stock)
        data['stocks'] = unique_stocks[:20]
        
        print(f"  Found: {len(data['stocks'])} stocks")
        
    finally:
        driver.quit()
    
    return data


def main():
    """Main function"""
    print("="*60)
    print("GROWW SCRAPER")
    print("="*60)
    
    data = scrape_groww(headless=False)
    
    # Save to JSON
    filename = f"groww_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved: {filename}")
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Indices: {len(data['indices'])}")
    print(f"News: {len(data['news'])}")
    print(f"Stocks: {len(data['stocks'])}")
    
    if data['news']:
        print("\nLatest news:")
        for i, news in enumerate(data['news'][:3], 1):
            print(f"  {i}. {news['headline'][:60]}...")


if __name__ == "__main__":
    main()

