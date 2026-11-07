# Superstore — KPI Report (Excel / Power BI-style write-up)

Source: Tableau "Sample – Superstore" (9,994 order lines, 5,009 orders, 793 customers, US, 2015-01-03 → 2018-12-30).
All figures produced by `src/kpis.py`; the same tables are in `outputs/superstore_kpi_report.xlsx` (8 sheets: KPIs, Yearly, Monthly Sales Pivot, Region, Sub-Category, Segment, State, Discount Bands).

## 1. Headline KPIs (2015–2018)
| KPI | Value |
|---|---:|
| Total sales | $2,297,201 |
| Total profit | $286,397 |
| Profit margin | 12.5% |
| Orders | 5,009 |
| Average order value | $459 |
| Units sold | 37,873 |
| Return rate (orders) | 5.9% |
| Average days to ship | 3.96 |

## 2. Year over year
| Year | Sales | YoY | Profit | Margin | Orders | AOV |
|---|---:|---:|---:|---:|---:|---:|
| 2015 | $484,248 | – | $49,544 | 10.2% | 969 | $500 |
| 2016 | $470,533 | −2.8% | $61,619 | 13.1% | 1,038 | $453 |
| 2017 | $609,206 | +29.5% | $81,795 | 13.4% | 1,315 | $463 |
| 2018 | $733,215 | +20.4% | $93,439 | 12.7% | 1,687 | $435 |

**Read-out:** sales grew ~51% from 2015 to 2018, driven by more orders (+74%) while AOV fell. In 2018 profit grew more slowly than sales (+14.2% vs +20.4%) and margin slipped 0.7 pts — growth is partly "bought" with discounts.

## 3. Category & sub-category
| Category | Sales | Profit | Margin |
|---|---:|---:|---:|
| Technology | $836,154 | $145,455 | 17.4% |
| Furniture | $742,000 | $18,451 | **2.5%** |
| Office Supplies | $719,047 | $122,491 | 17.0% |

- Furniture brings in 32% of sales but only 6% of profit.
- **Loss-making sub-categories:** Tables (−$17,726, −8.6% margin), Bookcases (−$3,473), Supplies (−$1,189).
- **Most profitable:** Copiers ($55,618 at 37.2% margin), Phones ($44,516), Accessories ($41,937). Paper, Labels and Envelopes earn 42–44% margins.

## 4. Region, state, segment
| Region | Sales | Profit | Margin |
|---|---:|---:|---:|
| West | $725,458 | $108,418 | 14.9% |
| East | $678,781 | $91,523 | 13.5% |
| Central | $501,240 | $39,706 | **7.9%** |
| South | $391,722 | $46,749 | 11.9% |

- **Loss-making states:** Texas (−$25,729), Ohio (−$16,971), Pennsylvania (−$15,560), Illinois (−$12,608), North Carolina (−$7,491).
- **Top profit states:** California ($76,381), New York ($74,039), Washington ($33,403).
- Segments: Consumer is 51% of sales (11.5% margin); Home Office has the best margin (14.0%).

## 5. Discount impact (the key driver)
| Discount band | Order lines | Sales | Profit | Margin |
|---|---:|---:|---:|---:|
| 0% | 4,798 | $1,087,909 | $320,988 | 29.5% |
| 1–20% | 3,803 | $846,522 | $100,786 | 11.9% |
| 21–40% | 460 | $234,138 | −$35,818 | **−15.3%** |
| >40% | 933 | $128,632 | −$99,559 | **−77.4%** |

Lines with discounts above 20% lose **$135K** in total — more than the profit of the whole Central and South regions combined ($86K).

## 6. Seasonality
Monthly sales are strongly seasonal: September, November and December run at **1.6–1.8×** the average month, while January–February are the weakest (February ≈ 0.3×).

## 7. Recommendations
1. **Cap discounts at 20%** (or require approval above it) — the 21%+ bands destroy $135K of profit.
2. **Fix Furniture pricing**, starting with Tables and Bookcases: review discounting and shipping cost, or reduce the range.
3. **Turnaround plan for Central/Texas/Ohio/Pennsylvania/Illinois** — check whether losses come from discount-heavy deals (likely, given the discount results).
4. **Lean into high-margin lines** — Copiers, Phones, Accessories and paper products; cross-sell them with Furniture orders.
5. **Plan inventory and marketing for Sep–Dec**, when sales are highest.

> Note: Superstore is a fictional sample dataset published by Tableau for training. The analysis shows a repeatable KPI workflow; the numbers describe the sample only. Returns come from the dataset's "Returns" sheet (302 orders) and are concentrated in the West region (11.7% vs ~3% elsewhere), which is probably a quirk of how the sample was built.
