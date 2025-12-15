"""
Simplified Groww Stock News Scraper
====================================

Streamlined scraper that directly targets the news section structure.
Much faster and more reliable than the complex fallback approach.

Usage:
    python groww_simplified_scraper.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
from datetime import datetime
import logging
import re
import tempfile
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrowwStockNewsScraper:
    """Simplified scraper for Groww Stock News section"""
    
    def __init__(self, headless=False):
        """Initialize the scraper"""
        self.url = "https://groww.in/share-market-today"
        self.headless = headless
        self.driver = None
        self.wait = None
        self._profile_dir = None
    
    def _init_driver(self):
        """Initialize web driver"""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless=new')
                options.add_argument('--disable-gpu')
            
            # Essential flags for containerized Chrome
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--no-zygote')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-features=VizDisplayCompositor')

            # Use a unique user-data-dir per run
            self._profile_dir = tempfile.mkdtemp(prefix="chrome-profile-")
            options.add_argument(f'--user-data-dir={self._profile_dir}')
            
            # Anti-bot detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--window-size=1280,720')

            service = Service()
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {e}")
            return False
    
    def navigate_to_page(self):
        """Navigate to Groww share market page"""
        try:
            logger.info(f"Navigating to: {self.url}")
            self.driver.get(self.url)
            
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            logger.info("Initial page load complete")
            
            # Wait for JavaScript to execute - longer wait for dynamic content
            logger.info("Waiting for dynamic content to load...")
            time.sleep(8)
            
            # Scroll to load content (lazy loading)
            logger.info("Scrolling to load content...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Wait for news content - be more flexible
            try:
                self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'ago')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'stocks')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'CNBC')]"))
                    )
                )
                logger.info("News content detected")
            except TimeoutException:
                logger.warning("Timeout waiting for news content, but continuing...")
                # Check if content exists anyway
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                if 'ago' in page_text.lower():
                    logger.info("Found 'ago' text in page, continuing...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading page: {e}")
            return False
    
    def find_news_section(self):
        """
        Find the 'Stocks in news' section - SIMPLIFIED but robust
        
        Returns:
            WebElement or None: The container element (None = search whole page)
        """
        try:
            logger.info("Finding 'Stocks in news' section...")
            
            # Try multiple patterns for the heading
            heading_patterns = [
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'stocks in news')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'stocks') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'news')]",
            ]
            
            heading = None
            for pattern in heading_patterns:
                try:
                    headings = self.driver.find_elements(By.XPATH, pattern)
                    for h in headings:
                        text = h.text.strip().lower()
                        if 'stocks' in text and 'news' in text:
                            heading = h
                            break
                    if heading:
                        break
                except:
                    continue
            
            if not heading:
                logger.warning("Could not find 'Stocks in news' heading - will search entire page")
                return None
            
            # Get parent container (try multiple levels)
            for level in [3, 4, 5]:
                try:
                    container = heading.find_element(By.XPATH, f"./ancestor::*[position()={level}]")
                    time_elements = container.find_elements(By.XPATH, ".//*[contains(text(), 'ago')]")
                    if len(time_elements) >= 2:
                        logger.info(f"Found news section with {len(time_elements)} time elements")
                        return container
                except:
                    continue
            
            logger.warning("Could not find news section container - will search entire page")
            return None
            
        except Exception as e:
            logger.warning(f"Error finding news section: {e} - will search entire page")
            return None
    
    def scrape_news_items(self, container=None):
        """
        Scrape all news items - SIMPLIFIED
        
        Args:
            container: Optional container element
            
        Returns:
            list: List of news item dictionaries
        """
        try:
            logger.info("Scraping news items...")
            
            news_items = []
            search_root = container if container else self.driver
            
            # SIMPLIFIED: Find all elements with "ago" text (these are time elements)
            # Use same pattern as working scraper
            time_elements = []
            try:
                elements = search_root.find_elements(By.XPATH, ".//*[contains(text(), 'ago')]")
                if elements:
                    time_elements = elements
                    logger.info(f"Found {len(elements)} elements with 'ago' text")
            except:
                pass
            
            # Fallback: if no elements found, search through all elements (like working scraper)
            if not time_elements:
                logger.info("Trying alternative method to find time elements...")
                all_elements = search_root.find_elements(By.XPATH, ".//*")
                checked = 0
                for elem in all_elements:
                    if checked > 500:  # Limit search
                        break
                    checked += 1
                    try:
                        text = elem.text or ""
                        if 'ago' in text.lower() and ('hour' in text.lower() or 'minute' in text.lower()):
                            time_elements.append(elem)
                            if len(time_elements) >= 20:  # Limit to 20
                                break
                    except:
                        continue
                logger.info(f"Found {len(time_elements)} time elements (alternative method)")
            
            if not time_elements:
                logger.warning("No time elements found")
                return news_items
            
            # Process each time element to find its news item container
            processed_containers = set()
            
            for idx, time_elem in enumerate(time_elements[:20], 1):  # Limit to 20
                try:
                    # Find the news item container (usually 3-5 levels up from time element)
                    for level in [4, 5, 6]:
                        try:
                            item_container = time_elem.find_element(By.XPATH, f"./ancestor::*[position()={level}]")
                            
                            # Get unique identifier
                            container_id = id(item_container)
                            if container_id in processed_containers:
                                continue
                            
                            # Check if this looks like a news item (has headline-like text and stock info)
                            item_text = item_container.text
                            if len(item_text) > 50 and ('%' in item_text or 'ago' in item_text):
                                processed_containers.add(container_id)
                                
                                # Extract news data
                                news_data = self._extract_news_from_item(item_container)
                                
                                if news_data and news_data.get('headline'):
                                    headline_key = news_data['headline'].lower().strip()
                                    # Check for duplicates
                                    if not any(item.get('headline', '').lower().strip() == headline_key for item in news_items):
                                        news_items.append(news_data)
                                        logger.info(f"✓ Extracted {len(news_items)}: {news_data.get('headline', '')[:60]}...")
                                        break
                        except:
                            continue
                    
                    if len(news_items) >= 15:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error processing time element {idx}: {e}")
                    continue
            
            logger.info(f"Scraped {len(news_items)} unique news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error scraping news items: {e}")
            return []
    
    def _extract_news_from_item(self, item_container):
        """
        Extract news data from a single news item container - SIMPLIFIED
        
        Args:
            item_container: WebElement containing one news item
            
        Returns:
            dict or None: News data dictionary
        """
        try:
            news_data = {
                'source': '',
                'time': '',
                'headline': '',
                'stock_name': '',
                'stock_change': ''
            }
            
            item_text = item_container.text
            if not item_text or len(item_text) < 20:
                return None
            
            # Split into lines
            lines = [line.strip() for line in item_text.split('\n') if line.strip()]
            
            # Extract source and time (line with "ago")
            time_pattern = re.compile(r'(\d+\s*(?:hour|minute|day)s?\s*ago)', re.IGNORECASE)
            for line in lines:
                if 'ago' in line.lower():
                    # Parse "Source - X hours ago"
                    if ' - ' in line:
                        parts = line.split(' - ', 1)
                        news_data['source'] = parts[0].strip()
                        time_match = time_pattern.search(parts[1])
                        if time_match:
                            news_data['time'] = time_match.group(1)
                    else:
                        # Try to extract time
                        time_match = time_pattern.search(line)
                        if time_match:
                            news_data['time'] = time_match.group(1)
                            # Source is everything before time
                            news_data['source'] = line[:time_match.start()].strip().replace('·', '').replace('-', '').strip()
                    break
            
            # Extract headline (longest line that's not source/time/stock)
            for line in lines:
                if 'ago' in line.lower() or '%' in line or len(line) < 30:
                    continue
                if any(skip in line.lower() for skip in ['see more', 'view more', 'login']):
                    continue
                if len(line) > len(news_data.get('headline', '')):
                    news_data['headline'] = line
            
            # Extract stock info (line with %)
            stock_pattern = re.compile(r'([A-Za-z][A-Za-z\s&.,()]+?)\s+([-+]?\d+\.\d+%)', re.IGNORECASE)
            for line in lines:
                if '%' in line and len(line) < 80 and 'ago' not in line.lower():
                    match = stock_pattern.search(line)
                    if match:
                        news_data['stock_name'] = match.group(1).strip()
                        news_data['stock_change'] = match.group(2).strip()
                        break
            
            # Validate
            if news_data['headline'] and len(news_data['headline']) > 20:
                return news_data
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting news from item: {e}")
            return None
    
    def scrape_all_news(self):
        """Main method to scrape all stock news"""
        try:
            logger.info("Starting news scraping...")
            
            container = self.find_news_section()
            news_items = self.scrape_news_items(container)
            
            result = {
                'scrape_timestamp': datetime.now().isoformat(),
                'url': self.url,
                'total_news_items': len(news_items),
                'news_items': news_items
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in scrape_all_news: {e}")
            return None
    
    def save_data(self, data, filename="groww_stock_news"):
        """Save data to JSON file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"{filename}_{timestamp}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return None
    
    def cleanup(self):
        """Close browser and clean up"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except:
                pass
        
        # Clean up profile directory
        if self._profile_dir and os.path.exists(self._profile_dir):
            try:
                shutil.rmtree(self._profile_dir)
            except:
                pass


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("GROWW STOCK NEWS SCRAPER (SIMPLIFIED)")
    print("=" * 80)
    
    headless_input = input("\nRun in headless mode? (y/n, default: n): ").strip().lower()
    headless = headless_input == 'y'
    
    scraper = GrowwStockNewsScraper(headless=headless)
    
    try:
        if not scraper._init_driver():
            print("❌ Failed to initialize browser")
            return
        
        if not scraper.navigate_to_page():
            print("❌ Failed to load page")
            return
        
        print("\n✅ Page loaded successfully")
        print("Scraping stock news...")
        
        news_data = scraper.scrape_all_news()
        
        if news_data and news_data.get('news_items'):
            filepath = scraper.save_data(news_data)
            
            print(f"\n✅ Scraping completed successfully!")
            print(f"   Total news items: {news_data['total_news_items']}")
            print(f"   Data saved to: {filepath}")
            
            print("\n" + "-" * 80)
            print("SAMPLE NEWS ITEMS:")
            print("-" * 80)
            
            for i, item in enumerate(news_data['news_items'][:5], 1):
                print(f"\n{i}. {item.get('source', 'Unknown')} · {item.get('time', 'Unknown time')}")
                print(f"   Headline: {item.get('headline', 'N/A')}")
                print(f"   Stock: {item.get('stock_name', 'N/A')} ({item.get('stock_change', 'N/A')})")
            
            if len(news_data['news_items']) > 5:
                print(f"\n... and {len(news_data['news_items']) - 5} more items")
        else:
            print("\n⚠️  No news items found")
        
        if not headless:
            input("\nPress Enter to close browser...")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.cleanup()
    
    print("\n" + "=" * 80)
    print("SCRAPING COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    import os
    main()

