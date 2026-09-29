"""Sanity + invariant tests for the KPI engine."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import generate_data  # noqa: E402
import analysis  # noqa: E402


@pytest.fixture(scope="module")
def df():
    raw = generate_data.generate(n_days=120)
    raw["month"] = raw["date"].dt.to_period("M").astype(str)
    raw["margin_pct"] = 100 * raw["profit"] / raw["revenue"].where(raw["revenue"] != 0)
    return raw


def test_schema(df):
    expected = {"date", "category", "region", "units", "unit_price",
                "revenue", "cost", "profit"}
    assert expected.issubset(df.columns)


def test_no_negative_money(df):
    assert (df["revenue"] >= 0).all()
    assert (df["units"] >= 0).all()


def test_profit_identity(df):
    # profit must equal revenue - cost (within rounding)
    assert ((df["revenue"] - df["cost"] - df["profit"]).abs() < 0.011).all()


def test_kpis_consistent(df):
    k = analysis.kpis(df)
    assert k["total_revenue"] > 0
    assert 0 <= k["gross_margin_pct"] <= 100
    assert k["best_category"] in set(df["category"])
    assert k["best_region"] in set(df["region"])
    assert k["n_transactions"] == len(df)


def test_insights_render(df):
    k = analysis.kpis(df)
    lines = analysis.insights(df, k)
    assert len(lines) == 4
    assert all(isinstance(s, str) and s for s in lines)
