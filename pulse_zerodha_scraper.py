"""
Pulse by Zerodha News Scraper
==============================

Scraper for Pulse by Zerodha that extracts:
- News headlines
- Content/summary
- Source name
- Time (relative time like "X hours ago")

Usage:
    python pulse_zerodha_scraper.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
from datetime import datetime
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PulseZerodhaScraper:
    """Scraper for Pulse by Zerodha news aggregation website"""
    
    def __init__(self, headless=False):
        """Initialize the scraper"""
        self.url = "https://pulse.zerodha.com/"
        self.headless = headless
        self.driver = None
        self.wait = None
    
    def _init_driver(self):
        """Initialize web driver"""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
            
            # Anti-bot detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {e}")
            return False
    
    def navigate_to_page(self):
        """Navigate to Pulse by Zerodha page"""
        try:
            logger.info(f"Navigating to: {self.url}")
            self.driver.get(self.url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            logger.info("Initial page load complete")
            
            # Wait for JavaScript to execute and content to load
            time.sleep(3)
            
            # Scroll down to trigger any lazy loading
            logger.info("Scrolling to load content...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Scroll back up
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Try to wait for news items
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@role='listitem']"))
                )
                logger.info("News content detected on page")
            except TimeoutException:
                logger.warning("Timeout waiting for news items, but continuing...")
            
            logger.info("Page loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading page: {e}")
            return False
    
    def parse_time_and_source(self, metadata_text):
        """
        Parse metadata text to extract time and source
        Format: "X hours/minutes ago — Source Name"
        
        Args:
            metadata_text: String containing time and source info
            
        Returns:
            tuple: (time_string, source_name) or (None, None)
        """
        if not metadata_text:
            return None, None
        
        # Pattern to match: "55 minutes ago — The Hindu Business"
        # or "3.5 hours ago — Economic Times"
        pattern = r'(\d+(?:\.\d+)?\s*(?:minutes?|hours?|days?)\s*ago)\s*[—–-]\s*(.+)'
        match = re.search(pattern, metadata_text, re.IGNORECASE)
        
        if match:
            time_str = match.group(1).strip()
            source = match.group(2).strip()
            return time_str, source
        
        # Try alternative patterns
        # Pattern without separator (if format is different)
        alt_pattern = r'(\d+(?:\.\d+)?\s*(?:minutes?|hours?|days?)\s*ago)(.+)'
        alt_match = re.search(alt_pattern, metadata_text, re.IGNORECASE)
        
        if alt_match:
            time_str = alt_match.group(1).strip()
            # Source is everything after time
            source_part = alt_match.group(2).strip()
            # Remove common separators
            source = re.sub(r'^[—–-\s]+', '', source_part).strip()
            if source:
                return time_str, source
        
        return None, None
    
    def extract_article_data(self, article_element):
        """
        Extract data from a single article element
        
        Args:
            article_element: WebElement containing an article
            
        Returns:
            dict or None: Article data dictionary
        """
        try:
            article_data = {
                'headline': '',
                'content': '',
                'source': '',
                'time': '',
                'article_url': ''
            }
            
            # Get full text from the article element
            article_text = article_element.text
            
            if not article_text or len(article_text) < 20:
                return None
            
            # Extract headline - try multiple methods
            headline = None
            try:
                # Method 1: Find heading with link
                heading_elements = article_element.find_elements(By.XPATH, ".//*[@role='heading']//a")
                if heading_elements:
                    headline = heading_elements[0].text.strip()
                    # Also get the URL
                    article_data['article_url'] = heading_elements[0].get_attribute('href') or ''
            except Exception as e:
                logger.debug(f"Error extracting headline via heading: {e}")
            
            # Method 2: Try finding link directly in article
            if not headline:
                try:
                    links = article_element.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        link_text = link.text.strip()
                        # The headline is usually the longest link text that's not metadata
                        if len(link_text) > 30 and 'ago' not in link_text.lower():
                            headline = link_text
                            article_data['article_url'] = link.get_attribute('href') or ''
                            break
                except Exception as e:
                    logger.debug(f"Error extracting headline via links: {e}")
            
            if headline:
                article_data['headline'] = headline
            else:
                # If we can't find headline, skip this article
                logger.debug("Could not extract headline, skipping article")
                return None
            
            # Extract metadata (time and source)
            # Look for text containing "ago" which indicates time
            try:
                # Find all text nodes or elements containing "ago"
                all_text = article_element.get_attribute('textContent') or article_text
                
                # Look for metadata pattern
                metadata_pattern = r'(\d+(?:\.\d+)?\s*(?:minutes?|hours?|days?)\s*ago\s*[—–-].+)'
                metadata_match = re.search(metadata_pattern, all_text, re.IGNORECASE)
                
                if metadata_match:
                    metadata_text = metadata_match.group(1)
                    time_str, source = self.parse_time_and_source(metadata_text)
                    
                    if time_str:
                        article_data['time'] = time_str
                    if source:
                        article_data['source'] = source
                
                # Alternative: look for elements containing "ago"
                if not article_data['time']:
                    ago_elements = article_element.find_elements(By.XPATH, ".//*[contains(text(), 'ago')]")
                    for elem in ago_elements:
                        elem_text = elem.text
                        time_str, source = self.parse_time_and_source(elem_text)
                        if time_str:
                            article_data['time'] = time_str
                            article_data['source'] = source
                            break
                
            except Exception as e:
                logger.debug(f"Error extracting metadata: {e}")
            
            # Extract content/summary
            # Content should be the excerpt/summary text only
            try:
                # Get all text elements in the article
                # Look for paragraph-like elements that aren't headlines or metadata
                content_parts = []
                
                # Method 1: Try to find specific content elements (p, div, span)
                try:
                    all_elements = article_element.find_elements(By.XPATH, ".//*")
                    
                    for elem in all_elements:
                        try:
                            elem_text = elem.text.strip()
                            
                            # Skip empty elements
                            if not elem_text or len(elem_text) < 20:
                                continue
                            
                            # Skip if it's the headline
                            if headline and (elem_text == headline or headline in elem_text):
                                continue
                            
                            # Skip if it contains metadata pattern
                            if 'ago' in elem_text.lower() and re.search(r'\d+\s*(?:minutes?|hours?|days?)\s*ago', elem_text, re.IGNORECASE):
                                continue
                            
                            # Skip if it's too long (likely contains multiple articles)
                            if len(elem_text) > 500:
                                continue
                            
                            # Skip if element has nested headline links
                            nested_links = elem.find_elements(By.TAG_NAME, "a")
                            has_headline_link = False
                            for link in nested_links:
                                if len(link.text.strip()) > 40:
                                    has_headline_link = True
                                    break
                            
                            if has_headline_link:
                                continue
                            
                            # This might be content
                            # Check if it's not already in our list
                            is_duplicate = False
                            for existing in content_parts:
                                if elem_text in existing or existing in elem_text:
                                    is_duplicate = True
                                    break
                            
                            if not is_duplicate and 30 <= len(elem_text) <= 400:
                                content_parts.append(elem_text)
                        except:
                            continue
                except Exception as e:
                    logger.debug(f"Error finding content elements: {e}")
                
                # Method 2: If no content found, parse from article_text
                if not content_parts:
                    content = article_text
                    
                    # Remove headline
                    if headline:
                        content = content.replace(headline, '', 1).strip()
                    
                    # Remove metadata (find first line with "ago" and remove it)
                    lines = content.split('\n')
                    cleaned_lines = []
                    metadata_found = False
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Skip metadata line
                        if not metadata_found and 'ago' in line.lower() and re.search(r'\d+\s*(?:minutes?|hours?|days?)\s*ago', line, re.IGNORECASE):
                            metadata_found = True
                            continue
                        
                        # Stop if we hit another article's headline pattern
                        # (headlines are typically title case and longer)
                        if metadata_found and len(line) > 40 and line[0].isupper() and 'ago' not in line.lower():
                            # Check if this might be another article
                            break
                        
                        cleaned_lines.append(line)
                    
                    content = ' '.join(cleaned_lines).strip()
                    
                    # Truncate if too long
                    if len(content) > 500:
                        # Take first sentence or two
                        sentences = re.split(r'[.!?]\s+', content)
                        content = '. '.join(sentences[:2]) + '.'
                    
                    if len(content) > 20 and len(content) < 1000:
                        content_parts.append(content)
                
                # Join content parts
                if content_parts:
                    # Take the longest piece as the main content
                    content = max(content_parts, key=len)
                    content = re.sub(r'\s+', ' ', content).strip()
                    article_data['content'] = content
                else:
                    article_data['content'] = ''
                    
            except Exception as e:
                logger.debug(f"Error extracting content: {e}")
                article_data['content'] = ''
            
            # Validate: must have at least headline
            if article_data['headline'] and len(article_data['headline']) > 10:
                return article_data
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting article data: {e}")
            return None
    
    def scrape_news_articles(self):
        """
        Scrape all news articles from the page
        
        Returns:
            list: List of article dictionaries
        """
        try:
            logger.info("Scraping news articles...")
            
            articles = []
            
            # IMPROVED APPROACH: Find all headline links, then find their closest parent containers
            # Headlines are in <h2> or <h3> or elements with role='heading'
            
            # Method 1: Find all heading elements that contain links
            headline_elements = []
            try:
                # Try finding by heading tag with links
                h2_links = self.driver.find_elements(By.XPATH, "//h2//a[@href]")
                h3_links = self.driver.find_elements(By.XPATH, "//h3//a[@href]")
                headline_elements.extend(h2_links)
                headline_elements.extend(h3_links)
                logger.info(f"Found {len(headline_elements)} headline links using heading tags")
            except Exception as e:
                logger.debug(f"Error finding headlines by tags: {e}")
            
            # Method 2: If no headlines found, try finding by text characteristics
            if len(headline_elements) == 0:
                try:
                    # Find all links and filter by text length
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            text = link.text.strip()
                            # Headlines are typically 40-200 characters, no "ago" pattern
                            if 40 <= len(text) <= 200 and 'ago' not in text.lower():
                                # Check if link has an href attribute
                                href = link.get_attribute('href')
                                if href and ('http' in href):
                                    headline_elements.append(link)
                        except:
                            continue
                    logger.info(f"Found {len(headline_elements)} potential headline links by text analysis")
                except Exception as e:
                    logger.warning(f"Alternative headline detection failed: {e}")
            
            if not headline_elements:
                logger.warning("No headline links found on the page")
                return articles
            
            logger.info(f"Processing {len(headline_elements)} headline elements...")
            
            # For each headline, find its article container
            processed_containers = set()
            
            for idx, headline_link in enumerate(headline_elements, 1):
                try:
                    if idx % 5 == 0:
                        logger.info(f"Processing headline {idx}/{len(headline_elements)}...")
                    
                    # Find the article container for this headline
                    # Try different ancestor levels to find the right container
                    article_container = None
                    
                    for level in range(2, 8):
                        try:
                            potential_container = headline_link.find_element(By.XPATH, f"./ancestor::*[{level}]")
                            
                            # Get a unique ID for this container
                            container_html = potential_container.get_attribute('outerHTML')
                            if container_html:
                                container_signature = container_html[:100]
                            else:
                                container_signature = str(id(potential_container))
                            
                            # Skip if we've already processed this container
                            if container_signature in processed_containers:
                                continue
                            
                            # Check if this container has ONLY ONE headline and metadata
                            # Count headlines in this container
                            headlines_in_container = potential_container.find_elements(By.TAG_NAME, "a")
                            headline_texts = [h.text.strip() for h in headlines_in_container if len(h.text.strip()) > 40]
                            
                            # Check for metadata (time "ago") in container
                            container_text = potential_container.text
                            has_metadata = 'ago' in container_text.lower()
                            
                            # Good container should have:
                            # - 1-2 headline-like links (main headline + maybe source link)
                            # - Contains "ago" (metadata)
                            # - Not too much text (< 1000 chars typically)
                            if 1 <= len(headline_texts) <= 3 and has_metadata and len(container_text) < 1500:
                                article_container = potential_container
                                processed_containers.add(container_signature)
                                break
                        except:
                            continue
                    
                    if article_container:
                        # Extract data from this container
                        article_data = self.extract_article_data(article_container)
                        
                        if article_data and article_data.get('headline'):
                            # Check for duplicates by headline
                            headline = article_data['headline'].lower().strip()
                            if not any(a.get('headline', '').lower().strip() == headline for a in articles):
                                articles.append(article_data)
                                logger.info(f"✓ Extracted {len(articles)}: {article_data['headline'][:60]}...")
                    else:
                        logger.debug(f"Could not find container for headline: {headline_link.text[:40]}...")
                    
                except Exception as e:
                    logger.debug(f"Error processing headline {idx}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} unique articles")
            
            # Log summary
            if articles:
                logger.info("=" * 60)
                logger.info("EXTRACTION SUMMARY:")
                logger.info("=" * 60)
                for i, article in enumerate(articles[:5], 1):
                    logger.info(f"{i}. {article.get('source', 'N/A')} | {article.get('time', 'N/A')}")
                    logger.info(f"   Headline: {article.get('headline', 'N/A')[:70]}...")
                if len(articles) > 5:
                    logger.info(f"... and {len(articles) - 5} more articles")
                logger.info("=" * 60)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping news articles: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def scrape_all_news(self):
        """
        Main method to scrape all news
        
        Returns:
            dict: Dictionary containing all scraped news items
        """
        try:
            logger.info("Starting news scraping...")
            
            # Scrape news articles
            articles = self.scrape_news_articles()
            
            result = {
                'scrape_timestamp': datetime.now().isoformat(),
                'url': self.url,
                'total_articles': len(articles),
                'articles': articles
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in scrape_all_news: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def save_data(self, data, filename="pulse_zerodha_news"):
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
    
    def take_screenshot(self, filename="pulse_zerodha_debug"):
        """Take screenshot of current page"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"{filename}_{timestamp}.png"
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    def cleanup(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except:
                pass


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("PULSE BY ZERODHA NEWS SCRAPER")
    print("=" * 80)
    
    # Ask for headless mode
    headless_input = input("\nRun in headless mode? (y/n, default: n): ").strip().lower()
    headless = headless_input == 'y'
    
    # Initialize scraper
    scraper = PulseZerodhaScraper(headless=headless)
    
    try:
        # Initialize driver
        if not scraper._init_driver():
            print("❌ Failed to initialize browser")
            return
        
        # Navigate to page
        if not scraper.navigate_to_page():
            print("❌ Failed to load page")
            return
        
        print("\n✅ Page loaded successfully")
        print("Scraping news articles...")
        
        # Scrape all news
        news_data = scraper.scrape_all_news()
        
        if news_data and news_data.get('articles'):
            # Save data
            filepath = scraper.save_data(news_data)
            
            print(f"\n✅ Scraping completed successfully!")
            print(f"   Total articles: {news_data['total_articles']}")
            print(f"   Data saved to: {filepath}")
            
            # Display first few items
            print("\n" + "-" * 80)
            print("SAMPLE NEWS ARTICLES:")
            print("-" * 80)
            
            for i, article in enumerate(news_data['articles'][:5], 1):
                print(f"\n{i}. {article.get('source', 'Unknown')} · {article.get('time', 'Unknown time')}")
                print(f"   Headline: {article.get('headline', 'N/A')}")
                print(f"   Content: {article.get('content', 'N/A')[:100]}..." if article.get('content') else "   Content: N/A")
                if article.get('article_url'):
                    print(f"   URL: {article.get('article_url')}")
            
            if len(news_data['articles']) > 5:
                print(f"\n... and {len(news_data['articles']) - 5} more articles")
        else:
            print("\n⚠️  No articles found")
            print("Taking screenshot for debugging...")
            scraper.take_screenshot()
        
        # Wait before closing
        if not headless:
            input("\nPress Enter to close browser...")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        scraper.take_screenshot("pulse_zerodha_error")
    
    finally:
        scraper.cleanup()
    
    print("\n" + "=" * 80)
    print("SCRAPING COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()

