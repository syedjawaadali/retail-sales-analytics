# Retail Sales Analytics

End-to-end exploratory analysis of a synthetic multi-category, multi-region
retail sales dataset (2 years, daily granularity). Computes executive KPIs and
produces trend and profitability visuals — the same reporting pattern I build
in Power BI, expressed in Python/pandas.

## What it does
- **Synthetic data generator** with seasonality, weekend uplift and realistic
  cost/margin structure (`src/generate_data.py`).
- **KPI engine** — revenue, gross margin %, AOV, best category/region.
- **Visuals** — monthly revenue trend and profit-by-category charts.

## Run it
```bash
pip install -r requirements.txt
python src/generate_data.py
python src/analysis.py
```
Charts land in `outputs/`.

## Stack
`pandas` · `numpy` · `matplotlib`

---
Part of my data analytics portfolio — [github.com/syedjawaadali](https://github.com/syedjawaadali)
