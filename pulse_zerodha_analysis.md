# Pulse by Zerodha - Website Structure Analysis

**URL:** https://pulse.zerodha.com/  
**Analysis Date:** 2025-12-14  
**Purpose:** Structure analysis for future scraper design

## Overview

Pulse by Zerodha is a news aggregation website that displays the latest business, finance, and market news from all major Indian news sources from the last 24 hours.

## Page Structure

### 1. Header Section
- **Logo:** "pulse" text with "BY ZERODHA" subtitle (top left)
- **Description:** "The latest business, finance, and market news from the last 24 hours from all major Indian news sources aggregated in one place."
- **Search Bar:** Magnifying glass icon (top right)
- **App Store Links:** 
  - Google Play Store icon
  - Apple App Store icon
  - Chrome Extension icon

### 2. Trending Topics Bar
- Label: "Trending" (orange text)
- Clickable keywords/tags: indian, nifty, ipo, icici, investors, india, upside, hits, record, rally, files, papers, fresh, media

### 3. Main Content Area
- **Layout:** 3-column grid layout
- **Container:** News articles in a `<list>` element
- **Each article is a `<listitem>`**

## News Article Structure

Each news article follows this consistent structure:

```
<listitem>
  ├── <heading>
  │   └── <link> [Headline text - clickable]
  └── <generic> [Metadata container]
      ├── <link> [Source link]
      └── <link> [Time link]
```

### Data Points Available per Article:

1. **Headline**
   - Location: Inside `<heading>` > `<link>`
   - Format: Bold, prominent text
   - Example: "Enforcement Directorate aims to end legacy FERA cases by early 2026"
   - **Note:** Headline is clickable and links to the original article

2. **Summary/Excerpt**
   - Location: Text within the `<listitem>` container
   - Format: Regular paragraph text
   - Example: "The criminal sections-loaded FERA of 1973 was replaced in June 2000 by the Foreign Exchange Management Act (FEMA) of 1999, a civil law"

3. **Metadata (Time & Source)**
   - Location: Inside `<generic>` container with 2 `<link>` elements
   - Format: "X hours/minutes ago — Source Name"
   - Examples:
     - "55 minutes ago — The Hindu Business"
     - "3.5 hours ago — Economic Times"
     - "6 hours ago — Economic Times"
     - "6.5 hours ago — Economic Times"
     - "12.5 hours ago — Finshots"
     - "17.5 hours ago — The Hindu Business"
     - "22.5 hours ago — The Hindu Business"
   
   **Time Format Patterns:**
   - "X minutes ago"
   - "X hours ago"
   - "X.5 hours ago" (half hours)
   - "X days ago" (for older articles)

   **Source Examples:**
   - The Hindu Business
   - Economic Times
   - Finshots
   - The Hindu Business

## Technical Details

### Page Loading
- **Rendering:** Server-side rendered (SSR)
- **JavaScript:** Uses jQuery (version 1.8.2)
- **CSS:** Custom stylesheet (`style.css`)
- **No API Calls:** Content is loaded directly in the HTML
- **Lazy Loading:** Appears to load all content at once (no infinite scroll detected in initial view)

### HTML Structure (Accessibility Tree)
- Uses semantic HTML with accessibility roles
- News container: `role: list`
- Each article: `role: listitem`
- Headlines: `role: heading` > `role: link`
- Metadata: `role: generic` containing `role: link` elements

### CSS Classes (To investigate with DOM inspector)
- Elements appear to use semantic structure
- Classes would need to be inspected via browser DevTools for precise selectors

## Data Extraction Strategy

### Recommended Scraping Approach

**Option 1: Selenium WebDriver (Recommended)**
- Best for: JavaScript-heavy sites, dynamic content
- Advantages:
  - Can handle complex DOM navigation
  - Can extract from accessibility tree structure
  - Can click and interact if needed
- Selectors to use:
  ```python
  # Find all news items
  news_items = driver.find_elements(By.XPATH, "//*[@role='listitem']")
  
  # For each item:
  # 1. Headline
  headline = item.find_element(By.XPATH, ".//*[@role='heading']//a").text
  
  # 2. Summary (extract text excluding headline and metadata)
  # This might require more complex logic to separate from headline
  
  # 3. Metadata (time and source)
  metadata_links = item.find_elements(By.XPATH, ".//*[@role='generic']//a")
  # Parse time and source from link texts
  ```

**Option 2: BeautifulSoup with requests**
- Best for: If content is static
- May work if content is fully server-rendered
- Simpler and faster than Selenium
- Use `requests.get()` to fetch HTML
- Parse with BeautifulSoup

### Key Selectors (XPath-based on accessibility roles)

```python
# Main container
news_list = "//*[@role='list']"

# Individual news items
news_items = "//*[@role='listitem']"

# Headline (inside heading > link)
headline = ".//*[@role='heading']//a"

# Metadata container
metadata = ".//*[@role='generic']"

# Time and source links
metadata_links = ".//*[@role='generic']//a"
```

### Data Parsing Logic

**For Time & Source:**
```python
import re

def parse_metadata(metadata_text):
    """
    Parse "X hours/minutes ago — Source Name"
    Returns: (time, source)
    """
    # Pattern: "55 minutes ago — The Hindu Business"
    pattern = r'(\d+(?:\.\d+)?\s*(?:minutes?|hours?|days?)\s*ago)\s*—\s*(.+)'
    match = re.search(pattern, metadata_text)
    if match:
        return match.group(1), match.group(2)
    return None, None
```

## Example Data Structure

```json
{
  "scrape_timestamp": "2025-12-14T14:19:00Z",
  "url": "https://pulse.zerodha.com/",
  "total_articles": 26,
  "articles": [
    {
      "headline": "Enforcement Directorate aims to end legacy FERA cases by early 2026",
      "summary": "The criminal sections-loaded FERA of 1973 was replaced in June 2000 by the Foreign Exchange Management Act (FEMA) of 1999, a civil law",
      "time": "55 minutes ago",
      "source": "The Hindu Business",
      "article_url": "<link href from headline>"
    },
    {
      "headline": "Ahead of Market: 10 things that will decide stock market action on Monday",
      "summary": "Indian equity benchmarks ended the week marginally lower amid sustained FII outflows and US-India trade uncertainty, though sentiment improved after a US Fed rate cut...",
      "time": "3.5 hours ago",
      "source": "Economic Times",
      "article_url": "<link href from headline>"
    }
  ]
}
```

## Challenges & Considerations

1. **Dynamic Content:** 
   - Check if content loads via JavaScript after initial page load
   - May need wait times for Selenium

2. **Pagination/Scroll:**
   - Initial view shows ~26 articles
   - Check if there's pagination or infinite scroll for more articles
   - May need to scroll down to load more content

3. **Rate Limiting:**
   - Respect robots.txt
   - Add delays between requests
   - Consider using proxies if scraping frequently

4. **Data Quality:**
   - Summary text may need cleaning (truncation, special characters)
   - Time parsing needs to handle various formats
   - Source names may have variations

5. **URL Extraction:**
   - Headline links point to original articles
   - May need to extract `href` attribute for full article URLs

## Recommendations for Scraper Design

1. **Use Selenium** for reliable extraction given the DOM structure
2. **Extract all available data:**
   - Headline (with URL)
   - Summary/excerpt
   - Time (relative)
   - Source
3. **Parse time relative strings** and optionally convert to absolute timestamps
4. **Handle edge cases:**
   - Missing summaries
   - Various time formats
   - Different source name formats
5. **Implement error handling** for missing elements
6. **Add retry logic** for network issues
7. **Save data in structured format** (JSON recommended)

## Next Steps

1. **Inspect actual HTML** using browser DevTools to get precise CSS selectors
2. **Test with a simple scraper** to verify selectors work
3. **Check if there's pagination** or if all content loads at once
4. **Verify rate limits** and robots.txt compliance
5. **Implement the scraper** based on this analysis

