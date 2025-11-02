# eBay Tech Deals Data Pipeline

## Overview
This repo automates the collection, cleaning, and exploration of tech deals from eBay’s Global Deals page. The goal is to build a small time-series dataset (every 3 hours) and analyze how prices, discounts, and product types change over time.

---

## Methodology

1. **Data Collection (Selenium)**
   - `scraper.py` opens `https://www.ebay.com/globaldeals/tech`.
   - Scrolls to the bottom to trigger lazy loading (no per-item navigation).
   - Extracts from each product card:
     - `timestamp`
     - `title`
     - `price`
     - `original_price`
     - `item_url`
   - Appends to `ebay_tech_deals.csv` (does **not** overwrite).
   - GitHub Actions runs the scraper every **3 hours** using:
     ```yaml
     cron: '0 */3 * * *'
     ```
     so the dataset grows over ~2 days.

2. **Automation (GitHub Actions)**
   - Workflow checks out the repo.
   - Installs Chrome + Chromedriver on the runner.
   - Runs `scraper.py`.
   - If `ebay_tech_deals.csv` changed → commits and pushes back to the repo using the built-in GitHub token.

3. **Data Cleaning (`clean_data.py`)**
   - Loads `ebay_tech_deals.csv` as **strings**.
   - Cleans `price` and `original_price`:
     - removes `US $`, `$`, and commas
     - strips spaces
   - If `original_price` is missing → replaces it with `price`.
   - Converts `price` and `original_price` to numeric.
   - Computes `discount_percentage = (original_price - price) / original_price * 100` (rounded to 2 decimals).
   - Saves to `cleaned_ebay_deals.csv`.

4. **Exploratory Data Analysis (`EDA.ipynb`)**
   - Uses **cleaned** data.
   - Analyzes time, price, discounts, titles, and price differences.

---

## Key Findings from EDA (template / typical results)

> Your exact numbers will depend on when the workflow ran and what eBay showed at that time.

1. **Time Series**
   - Deals get scraped in batches (every run), so counts per hour often reflect **when the workflow ran** more than when the deal was created.
   - After ~2 days, you can see if some hours consistently have more items (e.g. around eBay refresh times).

2. **Price & Discount**
   - Prices are usually **right-skewed** (many low/medium items, few expensive ones).
   - Some items have `original_price == price` → effectively no discount.
   - Scatter plot shows most points near the 45° line (price ≈ original_price), with a few true discounts.

3. **Text / Keywords**
   - Titles often include brand words (“Apple”, “Samsung”), but generic terms (“Laptop”, “Tablet”) might appear less.
   - This can be used to filter only target brands later.

4. **Discounts**
   - Real discounts (e.g. >20–30%) are fewer.
   - Some “discounts” are just formatting or missing original price.

---

## Challenges Faced

1. **Dynamic / Lazy-Loaded Page**
   - eBay loads items on scroll → needed a scroll-to-bottom loop.
   - Class names on eBay can change → used multiple CSS fallbacks.

2. **Headless Browser in GitHub Actions**
   - GitHub runners don’t have Chrome by default.
   - We had to **install Chrome + Chromedriver** and run Selenium with `xvfb-run`.
   - Push-back to the repo needed the built-in `github.token`.

3. **Inconsistent Price Formats**
   - Some items show `US $`, some `$`, some with commas → required a cleaning function before converting to numeric.

4. **Missing Original Price**
   - Many cards don’t show the “striked” price → we filled it with current price to keep the column usable.

---

## Potential Improvements

1. **De-duplication**
   - Same item may appear in multiple runs.
   - Add a unique key (e.g. item URL + title + date) and drop duplicates before analysis.

2. **Richer Parsing**
   - Parse quantity/sold info if present.
   - Detect currency explicitly (not assume USD).

3. **Brand/Category Tagging**
   - From titles, auto-tag `apple`, `samsung`, `laptop`, etc. and store in separate columns.

4. **Store to Database**
   - Instead of appending to CSV, write to SQLite / Postgres to avoid huge CSVs and to query by time.

5. **Alerting**
   - Add a step that posts to Discord/Slack when a discount exceeds a threshold (e.g. >40%).

---

## Files in This Repo

- `scraper.py` — Selenium scraper (appends to CSV).
- `clean_data.py` — cleans and normalizes prices, creates `discount_percentage`.
- `EDA.ipynb` — plots + quick insights.
- `.github/workflows/scrape-ebay.yml` — runs every 3 hours and commits the updated CSV.
- `ebay_tech_deals.csv` — raw growing dataset.
- `cleaned_ebay_deals.csv` — cleaned dataset for analysis.

---

## How to Run Locally

```bash
# 1. run the scraper
python scraper.py

# 2. clean the data
python clean_data.py

# 3. open the EDA
jupyter notebook EDA.ipynb
