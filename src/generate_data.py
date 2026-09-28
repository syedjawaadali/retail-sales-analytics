"""Generate a synthetic retail sales dataset."""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
DATA = Path(__file__).resolve().parents[1] / "data"


def generate(n_days: int = 730) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n_days, freq="D")
    categories = ["Electronics", "Apparel", "Grocery", "Home", "Beauty"]
    regions = ["North", "South", "East", "West"]
    rows = []
    for d in dates:
        season = 1.0 + 0.25 * np.sin(2 * np.pi * d.dayofyear / 365)
        weekend = 1.2 if d.weekday() >= 5 else 1.0
        for cat in categories:
            for reg in regions:
                base = RNG.gamma(shape=3.0, scale=30.0)
                units = max(0, int(base * season * weekend))
                price = {"Electronics": 220, "Apparel": 45, "Grocery": 12,
                         "Home": 80, "Beauty": 25}[cat] * RNG.uniform(0.8, 1.2)
                revenue = round(units * price, 2)
                cost = round(revenue * RNG.uniform(0.55, 0.78), 2)
                rows.append((d, cat, reg, units, round(price, 2), revenue, cost))
    df = pd.DataFrame(rows, columns=[
        "date", "category", "region", "units", "unit_price", "revenue", "cost"])
    df["profit"] = (df["revenue"] - df["cost"]).round(2)
    return df


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    df = generate()
    out = DATA / "retail_sales.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} rows -> {out}")
