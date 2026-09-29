"""Exploratory analysis, KPI reporting and executive dashboard for retail sales.

Reproduces, in Python/pandas, the reporting pattern I build in Power BI:
a governed set of KPIs plus a one-page executive visual. Run after
``generate_data.py`` — outputs land in ``outputs/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "retail_sales.csv"
OUT = ROOT / "outputs"

# ---- House style -----------------------------------------------------------
INK = "#0f172a"
GRID = "#e2e8f0"
ACCENT = "#1E90FF"
ACCENT_2 = "#00C2A8"
PALETTE = ["#1E90FF", "#00C2A8", "#F5A524", "#7C5CFF", "#F2647C"]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": GRID,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
})

_MONEY = FuncFormatter(lambda x, _: f"${x/1e6:.1f}M" if abs(x) >= 1e6 else f"${x/1e3:.0f}K")


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["margin_pct"] = 100 * df["profit"] / df["revenue"].where(df["revenue"] != 0)
    return df


def kpis(df: pd.DataFrame) -> dict:
    """Executive KPI set — the single source of truth for headline numbers."""
    rev = float(df["revenue"].sum())
    profit = float(df["profit"].sum())
    units = int(df["units"].sum())
    monthly = df.groupby("month")["revenue"].sum()
    mom = monthly.pct_change().dropna()
    return {
        "total_revenue": round(rev, 2),
        "total_profit": round(profit, 2),
        "gross_margin_pct": round(100 * profit / rev, 2),
        "total_units": units,
        "avg_order_value": round(rev / max(1, units), 2),
        "avg_mom_growth_pct": round(100 * mom.mean(), 2),
        "best_month": monthly.idxmax(),
        "best_category": df.groupby("category")["revenue"].sum().idxmax(),
        "best_region": df.groupby("region")["revenue"].sum().idxmax(),
        "n_transactions": int(len(df)),
        "date_range": f"{df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}",
    }


def insights(df: pd.DataFrame, k: dict) -> list[str]:
    """Turn the numbers into plain-language findings — the 'so what'."""
    cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    cat_margin = (df.groupby("category")["profit"].sum()
                  / df.groupby("category")["revenue"].sum() * 100).sort_values(ascending=False)
    top_share = 100 * cat_rev.iloc[0] / cat_rev.sum()
    return [
        f"**{k['best_category']}** is the revenue leader at "
        f"${cat_rev.iloc[0]/1e6:.1f}M ({top_share:.0f}% of total).",
        f"Highest-margin category is **{cat_margin.index[0]}** at "
        f"{cat_margin.iloc[0]:.1f}% gross margin — a candidate to scale.",
        f"Peak trading month was **{k['best_month']}**; average month-over-month "
        f"revenue growth ran at {k['avg_mom_growth_pct']:.1f}%.",
        f"**{k['best_region']}** is the strongest region; blended AOV is "
        f"${k['avg_order_value']:.2f} across {k['total_units']:,} units.",
    ]


def dashboard(df: pd.DataFrame, k: dict) -> None:
    """One-page executive dashboard (4 panels) + standalone trend/category charts."""
    OUT.mkdir(exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle("Retail Sales — Executive Dashboard", fontsize=16, fontweight="bold",
                 color=INK, x=0.5, y=0.98)

    # 1) Monthly revenue trend
    monthly = df.groupby("month")["revenue"].sum()
    ax = axes[0, 0]
    ax.plot(range(len(monthly)), monthly.values, marker="o", color=ACCENT, lw=2.2)
    ax.fill_between(range(len(monthly)), monthly.values, alpha=0.12, color=ACCENT)
    ax.set_title("Monthly Revenue Trend")
    ax.set_xticks(range(0, len(monthly), 3))
    ax.set_xticklabels(monthly.index[::3], rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(_MONEY)

    # 2) Profit by category
    ax = axes[0, 1]
    by_cat = df.groupby("category")["profit"].sum().sort_values()
    ax.barh(by_cat.index, by_cat.values, color=PALETTE)
    ax.set_title("Profit by Category")
    ax.xaxis.set_major_formatter(_MONEY)

    # 3) Revenue by region
    ax = axes[1, 0]
    by_reg = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    ax.bar(by_reg.index, by_reg.values, color=ACCENT_2)
    ax.set_title("Revenue by Region")
    ax.yaxis.set_major_formatter(_MONEY)

    # 4) Margin distribution by category (box)
    ax = axes[1, 1]
    cats = list(df["category"].unique())
    ax.boxplot([df.loc[df["category"] == c, "margin_pct"].dropna() for c in cats],
               patch_artist=True,
               boxprops=dict(facecolor="#dbeafe", color=ACCENT),
               medianprops=dict(color=ACCENT_2, lw=2))
    ax.set_xticks(range(1, len(cats) + 1))
    ax.set_xticklabels(cats, rotation=20)
    ax.set_title("Gross Margin % Distribution")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT / "dashboard.png", dpi=130)
    plt.close(fig)

    # Standalone charts (kept for embedding elsewhere)
    ax = monthly.plot(kind="line", marker="o", figsize=(10, 4), color=ACCENT,
                      title="Monthly Revenue Trend")
    ax.yaxis.set_major_formatter(_MONEY)
    plt.tight_layout(); plt.savefig(OUT / "monthly_revenue.png", dpi=120); plt.close()

    ax = by_cat.plot(kind="barh", figsize=(8, 4), color=PALETTE, title="Profit by Category")
    ax.xaxis.set_major_formatter(_MONEY)
    plt.tight_layout(); plt.savefig(OUT / "profit_by_category.png", dpi=120); plt.close()


def main() -> None:
    if not DATA.exists():
        raise SystemExit("Run: python src/generate_data.py first")
    df = load()
    k = kpis(df)
    findings = insights(df, k)
    dashboard(df, k)

    (OUT / "kpis.json").write_text(json.dumps(k, indent=2))

    print("=== Retail Sales KPIs ===")
    for key, val in k.items():
        print(f"{key:>18}: {val}")
    print("\n=== Insights ===")
    for line in findings:
        print(" •", line.replace("**", ""))
    print(f"\nDashboard + charts + kpis.json written to {OUT}/")


if __name__ == "__main__":
    main()
