"""Data loading and KPI logic shared by the Streamlit app, the static preview and the Excel report."""
from pathlib import Path
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "superstore_raw.csv"
RAW_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (orders, returns).

    The source CSV stacks two Tableau sheets: 9,994 order lines, then 806 rows from the 'Returns'
    sheet (Row ID = 'Yes', only Order ID filled). They are split here and returns are joined back
    as an `is_returned` flag at order level.
    """
    if not RAW.exists():
        RAW.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(RAW_URL, RAW)
    raw = pd.read_csv(RAW, dtype={"Postal Code": str})
    is_return_row = raw["Order Date"].isna()
    returns = raw.loc[is_return_row, ["Order ID"]].drop_duplicates()
    orders = raw.loc[~is_return_row].copy()
    orders["Order Date"] = pd.to_datetime(orders["Order Date"], format="%m/%d/%Y")
    orders["Ship Date"] = pd.to_datetime(orders["Ship Date"], format="%m/%d/%Y")
    orders["Row ID"] = orders["Row ID"].astype(int)
    orders["Quantity"] = orders["Quantity"].astype(int)
    orders["Year"] = orders["Order Date"].dt.year
    orders["Month"] = orders["Order Date"].dt.to_period("M").dt.to_timestamp()
    orders["Days to Ship"] = (orders["Ship Date"] - orders["Order Date"]).dt.days
    orders["is_returned"] = orders["Order ID"].isin(returns["Order ID"])
    return orders, returns


def kpis(df: pd.DataFrame) -> dict:
    sales, profit = df["Sales"].sum(), df["Profit"].sum()
    n_orders = df["Order ID"].nunique()
    return {
        "Sales": sales,
        "Profit": profit,
        "Profit Margin %": 100 * profit / sales if sales else 0.0,
        "Orders": n_orders,
        "Customers": df["Customer ID"].nunique(),
        "Avg Order Value": sales / n_orders if n_orders else 0.0,
        "Units": int(df["Quantity"].sum()),
        "Return Rate %": 100 * df.loc[df["is_returned"], "Order ID"].nunique() / n_orders if n_orders else 0.0,
        "Avg Days to Ship": df["Days to Ship"].mean(),
    }


def yearly(df: pd.DataFrame) -> pd.DataFrame:
    y = df.groupby("Year").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
                               Orders=("Order ID", "nunique"), Customers=("Customer ID", "nunique"))
    y["Profit Margin %"] = 100 * y["Profit"] / y["Sales"]
    y["Sales YoY %"] = 100 * y["Sales"].pct_change()
    y["AOV"] = y["Sales"] / y["Orders"]
    return y


def by(df: pd.DataFrame, col) -> pd.DataFrame:
    g = df.groupby(col).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
    g["Profit Margin %"] = 100 * g["Profit"] / g["Sales"]
    return g.sort_values("Sales", ascending=False)


def discount_bands(df: pd.DataFrame) -> pd.DataFrame:
    bands = pd.cut(df["Discount"], [-0.01, 0, 0.2, 0.4, 1.0], labels=["0%", "1–20%", "21–40%", ">40%"])
    g = df.groupby(bands, observed=True).agg(Lines=("Sales", "size"), Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    g["Profit Margin %"] = 100 * g["Profit"] / g["Sales"]
    g.index.name = "Discount band"
    return g
