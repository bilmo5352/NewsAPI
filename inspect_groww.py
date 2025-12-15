"""Inspect actual Groww page structure"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1280,720')

driver = webdriver.Chrome(service=Service(), options=opts)
driver.get('https://groww.in/share-market-today')
time.sleep(8)

# Scroll
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(2)

print("=" * 80)
print("INSPECTING ACTUAL PAGE STRUCTURE")
print("=" * 80)

# 1. Check for "Stocks in news" text
print("\n1. Searching for 'Stocks in news' text...")
try:
    headings = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'stocks')]")
    print(f"   Found {len(headings)} elements with 'stocks'")
    for i, h in enumerate(headings[:5], 1):
        print(f"   {i}. Tag: {h.tag_name}, Text: {h.text[:80]}")
except Exception as e:
    print(f"   Error: {e}")

# 2. Check for "ago" text
print("\n2. Searching for 'ago' text...")
try:
    ago_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'ago')]")
    print(f"   Found {len(ago_elements)} elements with 'ago'")
    for i, elem in enumerate(ago_elements[:5], 1):
        print(f"   {i}. Tag: {elem.tag_name}, Text: {elem.text[:80]}")
        print(f"      Class: {elem.get_attribute('class')}")
        print(f"      Parent tag: {elem.find_element(By.XPATH, './..').tag_name}")
except Exception as e:
    print(f"   Error: {e}")

# 3. Check page source for news-related classes
print("\n3. Checking page source for news-related content...")
page_source = driver.page_source
if 'stocks in news' in page_source.lower():
    print("   ✓ Found 'stocks in news' in page source")
else:
    print("   ✗ 'stocks in news' NOT in page source")

if 'ago' in page_source.lower():
    print("   ✓ Found 'ago' in page source")
    # Count occurrences
    count = page_source.lower().count('ago')
    print(f"   Found {count} occurrences of 'ago'")
else:
    print("   ✗ 'ago' NOT in page source")

# 4. Try to find by common news source names
print("\n4. Searching for news sources...")
sources = ['CNBC', 'Business Standard', 'Financial Express', 'Economic Times']
for source in sources:
    try:
        elems = driver.find_elements(By.XPATH, f"//*[contains(text(), '{source}')]")
        if elems:
            print(f"   ✓ Found {len(elems)} elements with '{source}'")
            print(f"      First: {elems[0].text[:80]}")
    except:
        pass

# 5. Get all text on page
print("\n5. Sample page text (first 1000 chars)...")
body_text = driver.find_element(By.TAG_NAME, "body").text
print(body_text[:1000])

# 6. Check if content is in iframe or shadow DOM
print("\n6. Checking for iframes...")
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print(f"   Found {len(iframes)} iframes")

driver.quit()
print("\n" + "=" * 80)


