# Groww Scraper

Simple scraper for https://groww.in/share-market-today

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python scrape_groww.py
```

## Output
Creates `groww_data_TIMESTAMP.json` with:
- Market indices (NIFTY, SENSEX, etc.)
- News items
- Stock prices

## Notes
- Requires Chrome browser
- Set `headless=True` in code for background scraping
- Add delays between runs to avoid overloading the server
