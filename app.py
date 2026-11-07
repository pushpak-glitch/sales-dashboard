"""Superstore Sales Dashboard — run with:  streamlit run app.py"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from kpis import by, discount_bands, kpis, load_data, yearly  # noqa: E402

st.set_page_config(page_title="Superstore Sales Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def get_data():
    return load_data()


orders, _ = get_data()

# ---------------------------------------------------------------- sidebar filters
st.sidebar.header("Filters")
years = sorted(orders["Year"].unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)
sel_regions = st.sidebar.multiselect("Region", sorted(orders["Region"].unique()), default=sorted(orders["Region"].unique()))
sel_segments = st.sidebar.multiselect("Segment", sorted(orders["Segment"].unique()), default=sorted(orders["Segment"].unique()))
sel_cats = st.sidebar.multiselect("Category", sorted(orders["Category"].unique()), default=sorted(orders["Category"].unique()))

df = orders[orders["Year"].isin(sel_years) & orders["Region"].isin(sel_regions)
            & orders["Segment"].isin(sel_segments) & orders["Category"].isin(sel_cats)]

st.title("📊 Superstore Sales Dashboard")
st.caption("Tableau 'Sample – Superstore' dataset · US office-supplies retailer · orders 2015–2018")

if df.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------------------------------------------------------------- KPI cards (with YoY delta for the latest selected year)
k = kpis(df)
latest = max(sel_years)
prev = latest - 1
k_latest = kpis(df[df["Year"] == latest])
k_prev = kpis(df[df["Year"] == prev]) if prev in sel_years else None


def delta(key, pct=True):
    if not k_prev or not k_prev[key]:
        return None
    if pct and not key.endswith("%"):
        return f"{100 * (k_latest[key] / k_prev[key] - 1):+.1f}% YoY ({latest})"
    return f"{k_latest[key] - k_prev[key]:+.1f} pts YoY ({latest})"


c = st.columns(6)
c[0].metric("Total Sales", f"${k['Sales']:,.0f}", delta("Sales"))
c[1].metric("Total Profit", f"${k['Profit']:,.0f}", delta("Profit"))
c[2].metric("Profit Margin", f"{k['Profit Margin %']:.1f}%", delta("Profit Margin %"))
c[3].metric("Orders", f"{k['Orders']:,}", delta("Orders"))
c[4].metric("Avg Order Value", f"${k['Avg Order Value']:,.0f}", delta("Avg Order Value"))
c[5].metric("Return Rate", f"{k['Return Rate %']:.1f}%")

# ---------------------------------------------------------------- trend
m = df.groupby("Month").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
fig = px.line(m, x="Month", y=["Sales", "Profit"], markers=True, title="Monthly Sales & Profit")
fig.update_layout(legend_title_text="", yaxis_title="USD", hovermode="x unified")
st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- category / region
left, right = st.columns(2)
sub = by(df, ["Category", "Sub-Category"]).reset_index()
fig = px.bar(sub.sort_values("Profit"), x="Profit", y="Sub-Category", color="Category", orientation="h",
             title="Profit by Sub-Category", hover_data={"Sales": ":,.0f", "Profit Margin %": ":.1f"})
left.plotly_chart(fig, width="stretch")

reg = by(df, "Region").reset_index()
fig = px.bar(reg, x="Region", y="Sales", color="Profit Margin %", color_continuous_scale="RdYlGn",
             title="Sales by Region (colour = profit margin %)", text_auto=".3s")
right.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- state map + discount
left, right = st.columns(2)
STATE_CODES = {"Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
               "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Idaho": "ID", "Illinois": "IL",
               "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
               "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
               "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
               "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
               "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
               "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
st_df = by(df, "State").reset_index()
st_df["code"] = st_df["State"].map(STATE_CODES)
fig = px.choropleth(st_df, locations="code", locationmode="USA-states", color="Profit", scope="usa",
                    color_continuous_scale="RdYlGn", color_continuous_midpoint=0, hover_name="State",
                    hover_data={"code": False, "Sales": ":,.0f", "Profit": ":,.0f"}, title="Profit by State")
left.plotly_chart(fig, width="stretch")

disc = discount_bands(df).reset_index()
fig = px.bar(disc, x="Discount band", y="Profit Margin %", text_auto=".1f", title="Profit Margin by Discount Band",
             color="Profit Margin %", color_continuous_scale="RdYlGn", color_continuous_midpoint=0)
right.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- tables
left, right = st.columns(2)
prod = df.groupby("Product Name").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).round(0)
left.subheader("Top 10 products by sales")
left.dataframe(prod.sort_values("Sales", ascending=False).head(10), width="stretch")
right.subheader("10 biggest loss-making products")
right.dataframe(prod.sort_values("Profit").head(10), width="stretch")

st.subheader("Year-over-year summary")
st.dataframe(yearly(df).round(2), width="stretch")
st.download_button("Download filtered data (CSV)", df.to_csv(index=False).encode(), "superstore_filtered.csv", "text/csv")
