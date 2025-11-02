# clean_data.py
import pandas as pd

RAW_FILE = "ebay_tech_deals.csv"
CLEAN_FILE = "cleaned_ebay_deals.csv"


def clean_money(x: str) -> str:
    if pd.isna(x):
        return ""
    x = str(x).strip()
    x = x.replace("US $", "").replace("US$", "").replace("$", "")
    x = x.replace(",", "")
    return x.strip()


def main():
    # load everything as string
    df = pd.read_csv(RAW_FILE, dtype=str)

    # ensure columns exist
    for col in ["price", "original_price"]:
        if col not in df.columns:
            df[col] = ""

    # clean text
    df["price"] = df["price"].apply(clean_money)
    df["original_price"] = df["original_price"].apply(clean_money)

    # if original_price missing -> use price
    def fill_original(row):
        orig = row["original_price"]
        if orig is None or orig == "" or orig.upper() == "N/A":
            return row["price"]
        return orig

    df["original_price"] = df.apply(fill_original, axis=1)

    # convert to numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")

    # discount %
    def calc_discount(row):
        p = row["price"]
        op = row["original_price"]
        if pd.isna(p) or pd.isna(op) or op == 0:
            return None
        return round((op - p) / op * 100, 2)

    df["discount_percentage"] = df.apply(calc_discount, axis=1)

    # save
    df.to_csv(CLEAN_FILE, index=False)
    print(f"Saved cleaned file to {CLEAN_FILE}")


if __name__ == "__main__":
    main()
