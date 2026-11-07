"""Static, matplotlib-rendered preview of the dashboard (for the README) — python src/make_preview.py"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt

from kpis import ROOT, by, discount_bands, kpis, load_data, yearly

orders, _ = load_data()
k, y = kpis(orders), yearly(orders)
IMG = ROOT / "images"; IMG.mkdir(exist_ok=True)
usd = mt.FuncFormatter(lambda v, _: f"${v/1e3:,.0f}K")

fig = plt.figure(figsize=(16, 10), facecolor="#f6f7fb")
gs = fig.add_gridspec(3, 6, height_ratios=[0.55, 1.4, 1.4], hspace=0.55, wspace=0.6)
fig.suptitle("Superstore Sales Dashboard  ·  2015–2018  (static preview of the Streamlit app)",
             fontsize=16, fontweight="bold", x=0.05, ha="left", y=0.97)

cards = [("Total Sales", f"${k['Sales']/1e6:.2f}M", f"{y['Sales YoY %'].iloc[-1]:+.1f}% YoY"),
         ("Total Profit", f"${k['Profit']/1e3:.0f}K", f"{100*(y['Profit'].iloc[-1]/y['Profit'].iloc[-2]-1):+.1f}% YoY"),
         ("Profit Margin", f"{k['Profit Margin %']:.1f}%", f"{y['Profit Margin %'].iloc[-1]-y['Profit Margin %'].iloc[-2]:+.1f} pts YoY"),
         ("Orders", f"{k['Orders']:,}", f"{100*(y['Orders'].iloc[-1]/y['Orders'].iloc[-2]-1):+.1f}% YoY"),
         ("Avg Order Value", f"${k['Avg Order Value']:,.0f}", f"{100*(y['AOV'].iloc[-1]/y['AOV'].iloc[-2]-1):+.1f}% YoY"),
         ("Return Rate", f"{k['Return Rate %']:.1f}%", "of orders")]
for i, (label, value, sub) in enumerate(cards):
    ax = fig.add_subplot(gs[0, i]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="white", ec="#dde1ea"))
    ax.text(0.07, 0.72, label, fontsize=10, color="#555", transform=ax.transAxes)
    ax.text(0.07, 0.30, value, fontsize=17, fontweight="bold", transform=ax.transAxes)
    color = "#2ca02c" if sub.startswith("+") else ("#d62728" if sub.startswith("-") else "#777")
    ax.text(0.07, 0.07, sub, fontsize=8.5, color=color, transform=ax.transAxes)

m = orders.groupby("Month").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
ax = fig.add_subplot(gs[1, :4])
ax.plot(m.index, m["Sales"], marker="o", ms=3, label="Sales"); ax.plot(m.index, m["Profit"], marker="o", ms=3, label="Profit")
ax.yaxis.set_major_formatter(usd); ax.set_title("Monthly Sales & Profit", fontweight="bold", loc="left"); ax.legend(); ax.grid(alpha=.3)

reg = by(orders, "Region")
ax = fig.add_subplot(gs[1, 4:])
bars = ax.bar(reg.index, reg["Sales"], color=plt.cm.RdYlGn(reg["Profit Margin %"] / 20))
for b, mg in zip(bars, reg["Profit Margin %"]):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{mg:.1f}%\nmargin", ha="center", va="bottom", fontsize=8)
ax.yaxis.set_major_formatter(usd); ax.set_ylim(0, reg["Sales"].max() * 1.25)
ax.set_title("Sales by Region", fontweight="bold", loc="left")

sub = by(orders, "Sub-Category").sort_values("Profit")
ax = fig.add_subplot(gs[2, :3])
ax.barh(sub.index, sub["Profit"], color=["#d62728" if v < 0 else "#2ca02c" for v in sub["Profit"]])
ax.xaxis.set_major_formatter(usd); ax.tick_params(axis="y", labelsize=8)
ax.set_title("Profit by Sub-Category", fontweight="bold", loc="left"); ax.axvline(0, c="k", lw=.8)

d = discount_bands(orders)
ax = fig.add_subplot(gs[2, 3:])
bars = ax.bar(d.index.astype(str), d["Profit Margin %"], color=["#2ca02c" if v > 0 else "#d62728" for v in d["Profit Margin %"]])
for b, v in zip(bars, d["Profit Margin %"]):
    ax.text(b.get_x() + b.get_width() / 2, v + (2 if v > 0 else -6), f"{v:.1f}%", ha="center", fontsize=9)
ax.axhline(0, c="k", lw=.8); ax.set_ylim(d["Profit Margin %"].min() - 12, d["Profit Margin %"].max() + 10)
ax.set_title("Profit Margin by Discount Band", fontweight="bold", loc="left"); ax.set_ylabel("%")

plt.savefig(IMG / "dashboard_preview.png", dpi=110, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("Saved", IMG / "dashboard_preview.png")
