"""
Fixed Groww Scraper - Works with actual page structure
Tested and working version
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options


class GrowwScraperFixed:
    """Fixed version that actually works with Groww's structure"""
    
    def __init__(self, headless: bool = False):
        self.url = "https://groww.in/share-market-today"
        self.driver = None
        self.headless = headless
        self.data = {}
    
    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(3)
        
        print("✓ Driver initialized")
    
    def load_page(self):
        """Load page and wait"""
        print(f"Loading: {self.url}")
        self.driver.get(self.url)
        
        # Wait longer for the dynamic content
        time.sleep(5)
        
        # Scroll to load lazy content
        for i in range(3):
            self.driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(1)
        
        # Scroll back to top
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        print("✓ Page loaded and scrolled")
    
    def scrape_indices(self) -> List[Dict]:
        """Scrape indices - this one works, keep it"""
        print("\n🔍 Scraping indices...")
        indices = []
        
        try:
            # Find divs that contain index names
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            
            index_keywords = ['NIFTY', 'BANKNIFTY', 'SENSEX', 'FINNIFTY', 'MIDCPNIFTY', 'BANKEX']
            
            for keyword in index_keywords:
                for div in all_divs:
                    try:
                        text = div.text.strip()
                        if keyword in text and len(text) > len(keyword) and len(text) < 200:
                            lines = text.split('\n')
                            if len(lines) >= 2 and keyword == lines[0]:
                                indices.append({
                                    "name": lines[0],
                                    "value": lines[1] if len(lines) > 1 else "",
                                    "change": lines[2] if len(lines) > 2 else ""
                                })
                                break  # Found this index, move to next
                    except:
                        continue
            
            print(f"✓ Found {len(indices)} indices")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        return indices
    
    def scrape_news_fixed(self) -> List[Dict]:
        """Scrape news with correct approach"""
        print("\n🔍 Scraping news...")
        news_items = []
        
        try:
            # Scroll to news area (middle of page)
            self.driver.execute_script("window.scrollTo(0, 2000);")
            time.sleep(2)
            
            # Get page source and find news patterns
            page_source = self.driver.page_source
            
            # Look for all divs
            all_elements = self.driver.find_elements(By.TAG_NAME, "div")
            
            seen_headlines = set()
            
            for elem in all_elements:
                try:
                    text = elem.text.strip()
                    
                    # Skip if too short or too long
                    if not text or len(text) < 30 or len(text) > 500:
                        continue
                    
                    # Check if it looks like a news item (has source, time pattern)
                    if '·' in text and ('hour' in text.lower() or 'ago' in text.lower()):
                        lines = text.split('\n')
                        
                        # Find the line with source and time
                        source_line_idx = -1
                        for i, line in enumerate(lines):
                            if '·' in line and ('ago' in line or 'hour' in line):
                                source_line_idx = i
                                break
                        
                        if source_line_idx == -1:
                            continue
                        
                        # Extract source and time
                        source_time = lines[source_line_idx]
                        parts = source_time.split('·')
                        source = parts[0].strip()
                        time_ago = parts[1].strip() if len(parts) > 1 else ""
                        
                        # Headline is usually next line
                        headline = ""
                        if source_line_idx + 1 < len(lines):
                            headline = lines[source_line_idx + 1].strip()
                        
                        # Stock info (has %)
                        stock_info = ""
                        for line in lines:
                            if '%' in line and any(c.isdigit() for c in line):
                                stock_info = line.strip()
                                break
                        
                        # Skip duplicates or invalid
                        if not headline or len(headline) < 15 or headline in seen_headlines:
                            continue
                        
                        seen_headlines.add(headline)
                        
                        # Parse stock
                        stock_name = ""
                        stock_change = ""
                        if stock_info:
                            # Extract percentage
                            pct_match = re.search(r'([-+]?\d+\.?\d*%)', stock_info)
                            if pct_match:
                                stock_change = pct_match.group(1)
                                stock_name = stock_info.replace(stock_change, '').strip()
                        
                        news_item = {
                            "source": source,
                            "time_ago": time_ago,
                            "headline": headline,
                            "related_stock": stock_name,
                            "stock_change": stock_change
                        }
                        
                        news_items.append(news_item)
                        
                        if len(news_items) >= 15:
                            break
                
                except:
                    continue
            
            print(f"✓ Found {len(news_items)} news items")
        
        except Exception as e:
            print(f"✗ Error: {e}")
        
        return news_items
    
    def scrape_stock_section(self, section_title: str, scroll_position: int = 1500) -> List[Dict]:
        """Generic scraper for stock sections"""
        print(f"\n🔍 Scraping {section_title}...")
        stocks = []
        
        try:
            # Scroll to section
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(1)
            
            # Find all clickable elements (links)
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    text = link.text.strip()
                    
                    # Check if it's a stock (has ₹ or %)
                    if ('₹' in text or '%' in text) and '\n' in text:
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        
                        if len(lines) >= 2:
                            name = lines[0]
                            
                            # Skip if name is too long (probably not a stock card)
                            if len(name) > 50:
                                continue
                            
                            # Extract price and change
                            price = ""
                            change = ""
                            
                            for line in lines[1:]:
                                if '₹' in line and not price:
                                    price = line
                                elif '%' in line or (any(c in line for c in ['-', '+']) and any(c.isdigit() for c in line)):
                                    change = line
                            
                            if name and (price or change):
                                stocks.append({
                                    "name": name,
                                    "price": price,
                                    "change": change
                                })
                            
                            if len(stocks) >= 10:
                                break
                
                except:
                    continue
            
            # Remove duplicates
            unique_stocks = []
            seen_names = set()
            for stock in stocks:
                if stock['name'] not in seen_names:
                    seen_names.add(stock['name'])
                    unique_stocks.append(stock)
            
            print(f"✓ Found {len(unique_stocks)} stocks")
            return unique_stocks[:10]
        
        except Exception as e:
            print(f"✗ Error: {e}")
            return []
    
    def scrape_all(self) -> Dict:
        """Scrape everything"""
        print("\n" + "="*70)
        print("🚀 GROWW SCRAPER - FIXED VERSION")
        print("="*70)
        
        try:
            self.setup_driver()
            self.load_page()
            
            # Scrape data
            self.data = {
                "metadata": {
                    "url": self.url,
                    "scraped_at": datetime.now().isoformat(),
                    "version": "fixed-1.0"
                },
                "indices": self.scrape_indices(),
                "news": self.scrape_news_fixed(),
                "top_gainers": self.scrape_stock_section("Top Gainers", 1200),
                "top_losers": self.scrape_stock_section("Top Losers", 1400),
                "most_bought": self.scrape_stock_section("Most Bought", 1000),
                "most_traded": self.scrape_stock_section("Most Traded", 1100),
            }
            
            print("\n" + "="*70)
            print("✅ SCRAPING COMPLETE")
            print("="*70)
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n✓ Browser closed")
        
        return self.data
    
    def save(self, filename: str = None) -> str:
        """Save data"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"groww_data_fixed_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved: {filename}")
        return filename
    
    def print_summary(self):
        """Print summary"""
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        
        print(f"Indices: {len(self.data.get('indices', []))}")
        print(f"News: {len(self.data.get('news', []))}")
        print(f"Top Gainers: {len(self.data.get('top_gainers', []))}")
        print(f"Top Losers: {len(self.data.get('top_losers', []))}")
        print(f"Most Bought: {len(self.data.get('most_bought', []))}")
        
        # Show sample news
        if self.data.get('news'):
            print(f"\n📰 Sample News:")
            for i, news in enumerate(self.data['news'][:3], 1):
                print(f"{i}. {news['headline'][:60]}...")
                print(f"   {news['source']} · {news['time_ago']}")
                if news.get('related_stock'):
                    print(f"   📈 {news['related_stock']} {news.get('stock_change', '')}")


def main():
    """Run scraper"""
    scraper = GrowwScraperFixed(headless=False)  # Set True for headless
    
    data = scraper.scrape_all()
    filename = scraper.save()
    scraper.print_summary()
    
    return data, filename


if __name__ == "__main__":
    main()

