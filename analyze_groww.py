"""Quick script to analyze Groww page structure"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1280,720')

driver = webdriver.Chrome(options=opts)
driver.get('https://groww.in/share-market-today')
time.sleep(8)

print("=" * 80)
print("ANALYZING GROWW PAGE STRUCTURE")
print("=" * 80)

# Find "Stocks in news" heading
print("\n1. Looking for 'Stocks in news' heading...")
headings = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'stocks in news')]")
print(f"   Found {len(headings)} headings with 'stocks in news'")

if headings:
    heading = headings[0]
    print(f"   Heading text: {heading.text[:100]}")
    print(f"   Tag: {heading.tag_name}")
    print(f"   Class: {heading.get_attribute('class')}")
    
    # Find parent container
    parent = heading.find_element(By.XPATH, "./ancestor::*[position()=3]")
    print(f"\n2. Parent container:")
    print(f"   Tag: {parent.tag_name}")
    print(f"   Class: {parent.get_attribute('class')}")
    
    # Find all news items in this container
    print(f"\n3. Looking for news items...")
    
    # Try finding by links with percentages (stock links)
    stock_links = parent.find_elements(By.XPATH, ".//a[contains(text(), '%')]")
    print(f"   Found {len(stock_links)} links with '%'")
    
    if stock_links:
        print(f"\n4. Sample stock link:")
        link = stock_links[0]
        print(f"   Text: {link.text}")
        print(f"   Tag: {link.tag_name}")
        print(f"   Class: {link.get_attribute('class')}")
        
        # Get parent of this link (should be news item)
        news_item = link.find_element(By.XPATH, "./ancestor::*[position()<=5]")
        print(f"\n5. News item container:")
        print(f"   Tag: {news_item.tag_name}")
        print(f"   Class: {news_item.get_attribute('class')}")
        print(f"   Full text preview: {news_item.text[:200]}")
        
        # Find all similar containers
        similar_items = parent.find_elements(By.XPATH, f".//{news_item.tag_name}[@class='{news_item.get_attribute('class')}']")
        print(f"\n6. Found {len(similar_items)} items with same class")
        
        # Show structure of first item
        print(f"\n7. Structure of first news item:")
        lines = news_item.text.split('\n')
        for i, line in enumerate(lines[:10], 1):
            if line.strip():
                print(f"   {i}. {line.strip()[:80]}")

# Find time elements
print(f"\n8. Looking for time elements ('ago')...")
time_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'ago')]")
print(f"   Found {len(time_elements)} elements with 'ago'")

if time_elements:
    print(f"\n9. Sample time elements:")
    for i, elem in enumerate(time_elements[:3], 1):
        print(f"   {i}. Text: {elem.text[:80]}")
        print(f"      Tag: {elem.tag_name}, Class: {elem.get_attribute('class')}")

# Find by data attributes or IDs
print(f"\n10. Looking for data attributes...")
data_items = driver.find_elements(By.XPATH, "//*[@data-testid or @id or @class[contains(., 'news')]]")
print(f"   Found {len(data_items)} elements with data attributes")

driver.quit()
print("\n" + "=" * 80)


