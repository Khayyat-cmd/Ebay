# scraper.py
import os
import csv
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://www.ebay.com/globaldeals/tech"
CSV_FILE = "ebay_tech_deals.csv"


def get_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=opts)
    return driver


def scroll_to_bottom(driver, pause=1.2, max_tries=30):
    last_height = driver.execute_script("return document.body.scrollHeight")
    tries = 0
    while tries < max_tries:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            tries += 1
        else:
            tries = 0
            last_height = new_height


def find_product_cards(driver):
    cards = driver.find_elements(By.CSS_SELECTOR, ".dne-itemtile")
    if not cards:
        cards = driver.find_elements(By.CSS_SELECTOR, "li.s-item")
    return cards


def extract_from_card(card):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # title
    title = ""
    try:
        title_el = card.find_element(By.CSS_SELECTOR, ".dne-itemtile-title, .s-item__title")
        title = title_el.text.strip()
    except:
        pass

    # current/discounted price
    price = ""
    for sel in [
        ".first",
        ".itemtile-price-bold",
        ".dne-itemtile-price",
        ".s-item__price",
    ]:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            txt = el.text.strip()
            if txt:
                price = txt
                break
        except:
            continue

    # original/striked price
    original_price = ""
    for sel in [
        ".itemtile-price-strikethrough",
        ".dne-itemtile-original-price",
        ".s-item__original-price",
        ".s-item__price--strikethrough",
    ]:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            txt = el.text.strip()
            if txt:
                original_price = txt
                break
        except:
            continue

    # product url
    item_url = ""
    try:
        link_el = card.find_element(By.CSS_SELECTOR, "a")
        href = link_el.get_attribute("href")
        if href:
            item_url = href.split("?")[0]
    except:
        pass

    return {
        "timestamp": timestamp,
        "title": title,
        "price": price,
        "original_price": original_price,
        "item_url": item_url,
    }


def append_to_csv(rows, csv_file=CSV_FILE):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "title", "price", "original_price", "item_url"],
        )
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    driver = get_driver(headless=False)
    try:
        driver.get(URL)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dne-itemtile, li.s-item"))
            )
        except:
            print("No product cards found (initial load).")

        scroll_to_bottom(driver)

        cards = find_product_cards(driver)
        print(f"Found {len(cards)} product cards.")

        scraped_rows = []
        for card in cards:
            data = extract_from_card(card)
            if data["title"] or data["price"] or data["item_url"]:
                scraped_rows.append(data)

        if scraped_rows:
            append_to_csv(scraped_rows)
            print(f"Saved {len(scraped_rows)} rows to {CSV_FILE}")
        else:
            print("No valid rows to save.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
