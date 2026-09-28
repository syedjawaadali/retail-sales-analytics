"""Exploratory analysis and KPI reporting for retail sales."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "retail_sales.csv"
OUT = ROOT / "outputs"


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def kpis(df: pd.DataFrame) -> dict:
    rev = df["revenue"].sum()
    profit = df["profit"].sum()
    return {
        "total_revenue": round(rev, 2),
        "total_profit": round(profit, 2),
        "gross_margin_pct": round(100 * profit / rev, 2),
        "total_units": int(df["units"].sum()),
        "avg_order_value": round(rev / max(1, df["units"].sum()), 2),
        "best_category": df.groupby("category")["revenue"].sum().idxmax(),
        "best_region": df.groupby("region")["revenue"].sum().idxmax(),
    }


def charts(df: pd.DataFrame) -> None:
    OUT.mkdir(exist_ok=True)
    monthly = df.groupby("month")["revenue"].sum()
    ax = monthly.plot(kind="line", marker="o", figsize=(10, 4),
                      title="Monthly Revenue Trend")
    ax.set_ylabel("Revenue")
    plt.tight_layout(); plt.savefig(OUT / "monthly_revenue.png", dpi=120); plt.close()

    by_cat = df.groupby("category")["profit"].sum().sort_values()
    ax = by_cat.plot(kind="barh", figsize=(8, 4), title="Profit by Category")
    plt.tight_layout(); plt.savefig(OUT / "profit_by_category.png", dpi=120); plt.close()


def main() -> None:
    if not DATA.exists():
        raise SystemExit("Run: python src/generate_data.py first")
    df = load()
    k = kpis(df)
    charts(df)
    print("=== Retail Sales KPIs ===")
    for key, val in k.items():
        print(f"{key:>18}: {val}")
    print(f"\nCharts written to {OUT}/")


if __name__ == "__main__":
    main()
