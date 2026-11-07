"""Excel KPI workbook (Power BI / Excel-style pivots) — python src/build_excel_report.py"""
import pandas as pd

from kpis import ROOT, by, discount_bands, kpis, load_data, yearly

orders, _ = load_data()
out = ROOT / "outputs" / "superstore_kpi_report.xlsx"; out.parent.mkdir(exist_ok=True)
with pd.ExcelWriter(out, engine="openpyxl") as xw:
    pd.Series(kpis(orders), name="Value").round(2).to_frame().to_excel(xw, sheet_name="KPIs")
    yearly(orders).round(2).to_excel(xw, sheet_name="Yearly")
    pd.pivot_table(orders, values="Sales", index=orders["Order Date"].dt.month, columns="Year",
                   aggfunc="sum").round(0).rename_axis("Month").to_excel(xw, sheet_name="Monthly Sales Pivot")
    by(orders, ["Region"]).round(2).to_excel(xw, sheet_name="Region")
    by(orders, ["Category", "Sub-Category"]).round(2).to_excel(xw, sheet_name="Sub-Category")
    by(orders, ["Segment"]).round(2).to_excel(xw, sheet_name="Segment")
    by(orders, ["State"]).sort_values("Profit").round(2).to_excel(xw, sheet_name="State")
    discount_bands(orders).round(2).to_excel(xw, sheet_name="Discount Bands")
    for ws in xw.book.worksheets:
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = max(12, max(len(str(c.value or "")) for c in col) + 2)
print("Saved", out)
